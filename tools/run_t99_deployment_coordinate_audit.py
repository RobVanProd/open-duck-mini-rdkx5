#!/usr/bin/env python3
"""Run T99's frozen deployment-coordinate audit without retraining."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

import numpy as np
import onnxruntime as ort


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
ANALYSIS = ROOT / "outputs" / "analysis"
sys.path.insert(0, str(TOOLS))

import run_t20_support_trainthrough_one_update as t20  # noqa: E402
import run_t31_action_margin_trainthrough_cpu_smoke as t31  # noqa: E402
import run_t98_hidden_expert_cpu_contract as t98  # noqa: E402


PREREG = ANALYSIS / "t99_deployment_coordinate_audit_preregistration.json"
RESULT = ANALYSIS / "t99_deployment_coordinate_audit_result.json"
MARKDOWN = ANALYSIS / "T99_DEPLOYMENT_COORDINATE_AUDIT_RESULT_20260728.md"
WORK = Path(
    "D:/CodexArtifacts/open-duck-policy/t99_deployment_coordinate_audit_v1"
)


def validate_prereg(value: dict[str, Any]) -> None:
    basis = {
        key: item
        for key, item in value.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        value.get("status")
        != "PREREGISTERED_T99_DEPLOYMENT_COORDINATE_AUDIT"
        or value.get("failed_checks")
        or t20.canonical_sha256(basis)
        != value.get("preregistered_contract_sha256")
    ):
        raise RuntimeError("T99 preregistration identity changed")
    for name, item in value["sources"].items():
        t20.verify_receipt(item, name)
    for name, item in value["graphs"].items():
        t20.verify_receipt(item, name)


def final_trace_cases(prereg: dict[str, Any]) -> list[dict[str, Any]]:
    t97_prereg = json.loads(
        Path(prereg["sources"]["t97_preregistration"]["path"]).read_text(
            encoding="utf-8"
        )
    )
    ticks = set(prereg["population"]["ticks"])
    labels = t97_prereg["population"]["labels"]
    cases: list[dict[str, Any]] = []
    for item in t97_prereg["traces"]:
        if item["checkpoint_id"] != prereg["population"]["checkpoint"]:
            continue
        found: set[int] = set()
        with Path(item["trace"]["path"]).open(encoding="utf-8") as stream:
            for line in stream:
                row = json.loads(line)
                tick = int(row["tick"])
                if tick not in ticks:
                    continue
                found.add(tick)
                cases.append(
                    {
                        "population": item["population"],
                        "label": int(labels[item["population"]]),
                        "tick": tick,
                        "stored_h_out": np.asarray(
                            row["policy_state_output"]["h_out"],
                            dtype=np.float32,
                        ),
                        "feed": {
                            "obs": np.asarray(
                                row["obs_state"], dtype=np.float32
                            )[None, :],
                            "previous_action": np.asarray(
                                row["policy_state_input"][
                                    "previous_action"
                                ],
                                dtype=np.float32,
                            ),
                            "h_in": np.asarray(
                                row["policy_state_input"]["h_in"],
                                dtype=np.float32,
                            ),
                            "calibration_context": np.zeros(
                                (1, 64), dtype=np.float32
                            ),
                        },
                    }
                )
        if found != ticks:
            raise RuntimeError("T99 final trace population is incomplete")
    return cases


def raw_coordinate_diagnosis(
    raw_source: Path,
    deployed_source: Path,
    cases: list[dict[str, Any]],
) -> dict[str, Any]:
    raw = ort.InferenceSession(
        str(raw_source), providers=["CPUExecutionProvider"]
    )
    deployed = ort.InferenceSession(
        str(deployed_source), providers=["CPUExecutionProvider"]
    )
    raw_errors: list[float] = []
    deployed_errors: list[float] = []
    for case in cases:
        raw_feed = {
            key: value
            for key, value in case["feed"].items()
            if key != "calibration_context"
        }
        raw_hidden = raw.run(["h_out"], raw_feed)[0]
        deployed_hidden = deployed.run(["h_out"], case["feed"])[0]
        raw_errors.append(t98.max_abs(raw_hidden, case["stored_h_out"]))
        deployed_errors.append(
            t98.max_abs(deployed_hidden, case["stored_h_out"])
        )
    return {
        "rows": len(cases),
        "raw_maximum_stored_hidden_error": max(raw_errors),
        "raw_minimum_stored_hidden_error": min(raw_errors),
        "deployed_maximum_stored_hidden_error": max(deployed_errors),
        "deployed_bit_exact_rows": sum(
            value == 0.0 for value in deployed_errors
        ),
    }


def random_chain_exact(
    source: Path,
    candidate: Path,
    steps: int = 256,
) -> dict[str, Any]:
    source_session = ort.InferenceSession(
        str(source), providers=["CPUExecutionProvider"]
    )
    candidate_session = ort.InferenceSession(
        str(candidate), providers=["CPUExecutionProvider"]
    )
    rng = np.random.default_rng(990001)
    previous = np.zeros((1, 14), dtype=np.float32)
    hidden = np.zeros((1, 64), dtype=np.float32)
    exact = 0
    maximum_error = 0.0
    for _ in range(steps):
        feed = {
            "obs": rng.normal(size=(1, 115)).astype(np.float32),
            "previous_action": previous,
            "h_in": hidden,
            "calibration_context": rng.normal(
                size=(1, 64)
            ).astype(np.float32),
        }
        expected = source_session.run(None, feed)
        actual = candidate_session.run(None, feed)
        errors = [
            t98.max_abs(left, right)
            for left, right in zip(expected, actual, strict=True)
        ]
        maximum_error = max(maximum_error, *errors)
        exact += int(
            all(
                np.array_equal(left, right)
                for left, right in zip(expected, actual, strict=True)
            )
        )
        previous = expected[1]
        hidden = expected[2]
    return {
        "steps": steps,
        "bit_exact_steps": exact,
        "maximum_abs_error": maximum_error,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--read-only-authorized", action="store_true")
    args = parser.parse_args()
    if not args.read_only_authorized:
        raise PermissionError("T99 requires --read-only-authorized")
    for path in (RESULT, MARKDOWN, WORK):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T99 output: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("formal T99 execution requires a clean worktree")

    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    validate_prereg(prereg)
    WORK.mkdir(parents=True)
    raw_zero = Path(prereg["graphs"]["t98_raw_zero"]["path"])
    raw_final = Path(prereg["graphs"]["t98_raw_final"]["path"])
    deployments = {
        "0": t31.deployment_graph(raw_zero, WORK / "0"),
        "1024": t31.deployment_graph(raw_final, WORK / "1024"),
    }
    deployed_zero = Path(deployments["0"]["wrapped"]["path"])
    deployed_final = Path(deployments["1024"]["wrapped"]["path"])
    source_raw = Path(prereg["graphs"]["source_raw"]["path"])
    source_deployed = Path(prereg["graphs"]["source_deployed"]["path"])
    cases = final_trace_cases(prereg)

    # Reuse T98's exact intermediate-output audit on deployment graphs.
    t98.INSPECTION = WORK / "inspection"
    step_zero = t98.compare_step_zero(
        source_deployed, deployed_zero, cases
    )
    final_binding = t98.compare_final(
        source_deployed, deployed_final, cases
    )
    random_chain = random_chain_exact(
        source_deployed, deployed_zero
    )
    diagnosis = raw_coordinate_diagnosis(
        source_raw, source_deployed, cases
    )
    thresholds = prereg["thresholds"]
    transform_pass = all(
        item["source_deployment"]["inference"]["pass"]
        and item["context_parity"]["all_outputs_bit_exact"]
        and item["context_parity"]["context_is_diagnostic_only"]
        and item["verification"]["outputs_exact"]
        and item["verification"][
            "previous_action_out_equals_action_bit_exact"
        ]
        and item["margin_contract"]["pass"]
        for item in deployments.values()
    )
    checks = {
        "population_exact": (
            len(cases) == 36
            and sum(case["label"] == -1 for case in cases) == 18
            and sum(case["label"] == 1 for case in cases) == 18
        ),
        "coordinate_mismatch_proven": (
            diagnosis["raw_minimum_stored_hidden_error"] > 0.0
            and diagnosis["deployed_maximum_stored_hidden_error"] == 0.0
            and diagnosis["deployed_bit_exact_rows"] == 36
        ),
        "frozen_deployment_transform_passes": transform_pass,
        "step_zero_trace_outputs_bit_exact": (
            step_zero["rows"]
            == thresholds["step_zero_trace_bit_exact_rows"]
            and step_zero["bit_exact_rows"] == 36
            and step_zero["maximum_abs_error"] == 0.0
            and step_zero["gate_correct_rows"] == 36
            and step_zero["zero_head_rows"] == 36
        ),
        "step_zero_random_chain_bit_exact": (
            random_chain["steps"]
            == thresholds["step_zero_random_chain_bit_exact_steps"]
            and random_chain["bit_exact_steps"] == 256
            and random_chain["maximum_abs_error"] == 0.0
        ),
        "final_gate_and_hidden_exact": (
            final_binding["gate_correct_rows"] == 36
            and final_binding["hidden_maximum_abs_delta"] == 0.0
        ),
        "final_nominal_branch_bit_exact": (
            final_binding["nominal_rows"]
            == thresholds["final_nominal_bit_exact_rows"]
            and final_binding["nominal_raw_bit_exact_rows"] == 18
            and final_binding["nominal_final_bit_exact_rows"] == 18
        ),
        "final_negative_raw_action_binding": (
            final_binding["negative_raw_changed_fraction"]
            >= thresholds["minimum_negative_raw_action_changed_fraction"]
            and final_binding["maximum_negative_raw_action_delta"]
            >= thresholds["minimum_maximum_negative_raw_action_delta"]
        ),
        "final_negative_deployed_action_binding": (
            final_binding["negative_final_changed_fraction"]
            >= thresholds["minimum_negative_final_action_changed_fraction"]
        ),
        "optimizer_simulator_behavior_hosted_robot_zero": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    passed = not failed
    result: dict[str, Any] = {
        "schema_version": "open_duck.t99_deployment_coordinate_audit_result.v1",
        "status": (
            "PASS_T99_DEPLOYMENT_COORDINATE_AUDIT"
            if passed
            else "HOLD_T99_DEPLOYMENT_COORDINATE_AUDIT"
        ),
        "decision": (
            prereg["decision_rule"]["pass_decision"]
            if passed
            else prereg["decision_rule"]["fail_decision"]
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "repository_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "diagnosis": diagnosis,
        "deployment_graphs": {
            step: {
                "wrapped": item["wrapped"],
                "wrapped_io": item["wrapped_io"],
                "context_parity": item["context_parity"],
                "verification": item["verification"],
                "margin_contract": item["margin_contract"],
            }
            for step, item in deployments.items()
        },
        "causal_contract": {
            "step_zero_trace": step_zero,
            "step_zero_random_chain": random_chain,
            "postupdate_trace": final_binding,
        },
        "checks": checks,
        "failed_checks": failed,
        "execution": {
            "optimizer_steps": 0,
            "simulator_steps": 0,
            "formal_behavior_cells": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "hosted_preregistration": passed,
            "hosted_training": False,
            "behavior_evaluation": False,
            "policy_promotion": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    result["result_sha256"] = t20.canonical_sha256(result)
    RESULT.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T99 deployment-coordinate audit result",
                "",
                f"- Status: `{result['status']}`",
                f"- Decision: `{result['decision']}`",
                f"- Failed checks: `{failed}`",
                (
                    "- Raw/deployed maximum stored-hidden error: "
                    f"`{diagnosis['raw_maximum_stored_hidden_error']:.9f} / "
                    f"{diagnosis['deployed_maximum_stored_hidden_error']:.9f}`"
                ),
                (
                    "- Step-zero trace / chain exact: "
                    f"`{step_zero['bit_exact_rows']}/36 / "
                    f"{random_chain['bit_exact_steps']}/256`"
                ),
                (
                    "- Negative raw/final changed fraction: "
                    f"`{final_binding['negative_raw_changed_fraction']:.6f} / "
                    f"{final_binding['negative_final_changed_fraction']:.6f}`"
                ),
                (
                    "- Nominal raw/final exact rows: "
                    f"`{final_binding['nominal_raw_bit_exact_rows']}/18 / "
                    f"{final_binding['nominal_final_bit_exact_rows']}/18`"
                ),
                "- Optimizer / behavior / hosted / robot: `0 / 0 / 0 / 0`",
                f"- Result SHA-256: `{result['result_sha256']}`",
                "",
            ]
        ),
        encoding="utf-8",
        newline="\n",
    )
    print(result["status"])
    print(f"decision={result['decision']}")
    print(f"failed_checks={failed}")
    print(f"result_sha256={result['result_sha256']}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
