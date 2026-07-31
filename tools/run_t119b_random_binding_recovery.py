#!/usr/bin/env python3
"""Run T119B's read-only attribution of the random-input binding hold."""

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
import run_t98_hidden_expert_cpu_contract as t98  # noqa: E402


PREREG = ANALYSIS / "t119b_random_binding_recovery_preregistration.json"
RESULT = ANALYSIS / "t119b_random_binding_recovery_result.json"
MARKDOWN = ANALYSIS / "T119B_RANDOM_BINDING_RECOVERY_RESULT_20260729.md"
WORK = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t119b_random_binding_recovery_v1"
)


def validate_prereg(value: dict[str, Any]) -> None:
    basis = {
        key: item
        for key, item in value.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        value.get("status")
        != "PREREGISTERED_T119B_READ_ONLY_BINDING_RECOVERY"
        or value.get("failed_checks")
        or t20.canonical_sha256(basis)
        != value.get("preregistered_contract_sha256")
    ):
        raise RuntimeError("T119B preregistration identity changed")
    for group in ("sources", "assets"):
        for name, item in value[group].items():
            t20.verify_receipt(item, name)


def trace_envelope(prereg: dict[str, Any]) -> dict[str, np.ndarray]:
    cases = t98.trace_cases(
        {
            "assets": {
                "t97_preregistration": prereg["assets"][
                    "t97_preregistration"
                ]
            }
        }
    )
    obs = np.concatenate([case["feed"]["obs"] for case in cases], axis=0)
    hidden = np.concatenate(
        [case["feed"]["h_in"] for case in cases], axis=0
    )
    return {
        "obs_min": obs.min(axis=0),
        "obs_max": obs.max(axis=0),
        "hidden_min": hidden.min(axis=0),
        "hidden_max": hidden.max(axis=0),
    }


def inspect(source: Path, destination: Path) -> ort.InferenceSession:
    graph = t98.inspection_graph(
        source,
        destination,
        {
            "anchored_location": [1, 14],
            "raw_continuous_actions": [1, 14],
            "soft_negative_com_weight": [1, 1],
        },
    )
    return ort.InferenceSession(
        str(graph), providers=["CPUExecutionProvider"]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--recover-read-only", action="store_true")
    args = parser.parse_args()
    if not args.recover_read_only:
        raise PermissionError("T119B requires --recover-read-only")
    for path in (RESULT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T119B result: {path}")
    if WORK.exists():
        raise FileExistsError(f"refusing to reuse T119B work root: {WORK}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("formal T119B recovery requires clean worktree")

    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    validate_prereg(prereg)
    WORK.mkdir(parents=True)
    initial = inspect(
        Path(prereg["assets"]["initial_graph"]["path"]),
        WORK / "initial_inspection.onnx",
    )
    final = inspect(
        Path(prereg["assets"]["final_graph"]["path"]),
        WORK / "final_inspection.onnx",
    )
    envelope = trace_envelope(prereg)
    thresholds = prereg["thresholds"]
    rng = np.random.default_rng(1190001)
    rows: list[dict[str, Any]] = []
    saturated_elements = 0
    total_elements = 0
    for _ in range(256):
        obs = rng.normal(size=(1, 115)).astype(np.float32)
        hidden = rng.normal(size=(1, 64)).astype(np.float32)
        feed = {
            "obs": obs,
            "previous_action": rng.uniform(
                -0.5, 0.5, size=(1, 14)
            ).astype(np.float32),
            "h_in": hidden,
        }
        names = [
            "anchored_location",
            "raw_continuous_actions",
            "soft_negative_com_weight",
        ]
        before = initial.run(names, feed)
        after = final.run(names, feed)
        obs_outside = bool(
            np.any(obs[0] < envelope["obs_min"])
            or np.any(obs[0] > envelope["obs_max"])
        )
        hidden_outside = bool(
            np.any(hidden[0] < envelope["hidden_min"])
            or np.any(hidden[0] > envelope["hidden_max"])
        )
        saturated_elements += int(
            np.count_nonzero(
                np.abs(before[1])
                >= thresholds["raw_saturation_abs"]
            )
        )
        total_elements += int(before[1].size)
        rows.append(
            {
                "outside_trace_envelope": obs_outside or hidden_outside,
                "anchored_delta": t98.max_abs(before[0], after[0]),
                "raw_delta": t98.max_abs(before[1], after[1]),
                "weight_delta": t98.max_abs(before[2], after[2]),
            }
        )

    out_fraction = sum(
        row["outside_trace_envelope"] for row in rows
    ) / len(rows)
    saturation_fraction = saturated_elements / total_elements
    jointly_changed = sum(
        row["anchored_delta"]
        >= thresholds["minimum_anchored_location_delta"]
        and row["weight_delta"]
        >= thresholds["minimum_router_weight_delta"]
        for row in rows
    )
    audit = {
        "rows": len(rows),
        "out_of_trace_support_rows": sum(
            row["outside_trace_envelope"] for row in rows
        ),
        "out_of_trace_support_fraction": out_fraction,
        "initial_raw_saturated_elements": saturated_elements,
        "initial_raw_elements": total_elements,
        "initial_raw_saturated_element_fraction": saturation_fraction,
        "jointly_changed_rows": jointly_changed,
        "maximum_anchored_location_delta": max(
            row["anchored_delta"] for row in rows
        ),
        "maximum_raw_action_delta": max(
            row["raw_delta"] for row in rows
        ),
        "maximum_router_weight_delta": max(
            row["weight_delta"] for row in rows
        ),
    }
    original = json.loads(
        Path(
            prereg["sources"]["t119_result"]["path"]
        ).read_text(encoding="utf-8")
    )
    checks = {
        "same_256_random_feeds": len(rows) == 256,
        "synthetic_rows_outside_trace_support": (
            out_fraction
            >= thresholds[
                "minimum_out_of_trace_support_random_row_fraction"
            ]
        ),
        "initial_raw_actions_are_saturated": (
            saturation_fraction
            >= thresholds[
                "minimum_initial_raw_saturated_element_fraction"
            ]
        ),
        "router_and_pre_tanh_path_are_bound": (
            jointly_changed
            >= thresholds["minimum_jointly_changed_random_rows"]
            and audit["maximum_anchored_location_delta"]
            >= thresholds["minimum_anchored_location_delta"]
            and audit["maximum_router_weight_delta"]
            >= thresholds["minimum_router_weight_delta"]
        ),
        "frozen_real_trace_binding_remains_green": (
            original["checks"][
                "nominal_population_action_and_router_binding"
            ]
            and original["checks"][
                "negative_population_action_and_router_binding"
            ]
        ),
        "no_optimizer_simulator_behavior_hosted_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    passed = not failed
    result: dict[str, Any] = {
        "schema_version": (
            "open_duck.t119b_random_binding_recovery_result.v1"
        ),
        "status": (
            "PASS_T119B_READ_ONLY_BINDING_RECOVERY"
            if passed
            else "HOLD_T119B_READ_ONLY_BINDING_RECOVERY"
        ),
        "decision": (
            prereg["decision_rule"]["pass_decision"]
            if passed
            else prereg["decision_rule"]["fail_decision"]
        ),
        "classification": (
            "AUXILIARY_RANDOM_INPUTS_OUT_OF_SUPPORT_AND_TANH_SATURATED"
            if passed
            else "AUXILIARY_RANDOM_BINDING_FAILURE_CONFIRMED"
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "repository_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "audit": audit,
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
            "torque_or_motion": False,
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
                "# T119B read-only random-binding recovery result",
                "",
                f"- Status: `{result['status']}`",
                f"- Decision: `{result['decision']}`",
                f"- Failed checks: `{failed}`",
                (
                    "- Out-of-support random rows: "
                    f"`{audit['out_of_trace_support_rows']}/256`"
                ),
                (
                    "- Initial raw saturation fraction: "
                    f"`{saturation_fraction:.6f}`"
                ),
                (
                    "- Router + pre-tanh jointly changed rows: "
                    f"`{jointly_changed}/256`"
                ),
                "- Optimizer / simulator / behavior / hosted / robot: "
                "`0/0/0/0/0`",
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
