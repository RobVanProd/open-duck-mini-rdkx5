#!/usr/bin/env python3
"""Recover T152 using the frozen realistic +COM trace population."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
from typing import Any

import numpy as np
import onnxruntime as ort

from run_t136_static_calibration_router_transform import (
    ANALYSIS,
    ROOT,
    canonical_sha256,
    verify,
)


PREREG = (
    ANALYSIS
    / "t152b_reflected_positive_expert_recovery_preregistration.json"
)
RESULT = (
    ANALYSIS / "t152b_reflected_positive_expert_recovery_result.json"
)
MARKDOWN = (
    ANALYSIS / "T152B_REFLECTED_POSITIVE_EXPERT_RECOVERY_RESULT_20260729.md"
)
STEPS = (1_003_520, 2_007_040)


def validate_prereg(value: dict[str, Any]) -> None:
    basis = {
        key: item
        for key, item in value.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        value.get("status")
        != "PREREGISTERED_T152B_REFLECTED_POSITIVE_EXPERT_RECOVERY"
        or value.get("failed_checks")
        or canonical_sha256(basis)
        != value.get("preregistered_contract_sha256")
    ):
        raise RuntimeError("T152B preregistration identity changed")
    for name, item in value["frozen_inputs"].items():
        verify(item, name)
    for index, item in enumerate(value["trace_population"]):
        verify(
            {
                "path": item["path"],
                "bytes": item["bytes"],
                "sha256": item["sha256"],
            },
            f"trace_{index}",
        )


def session(path: Path) -> ort.InferenceSession:
    return ort.InferenceSession(
        str(path), providers=["CPUExecutionProvider"]
    )


def run(
    active: ort.InferenceSession,
    obs: np.ndarray,
    previous: np.ndarray,
    hidden: np.ndarray,
    context: np.ndarray,
) -> dict[str, np.ndarray]:
    values = active.run(
        None,
        {
            "obs": obs.astype(np.float32),
            "previous_action": previous.astype(np.float32),
            "h_in": hidden.astype(np.float32),
            "calibration_context": context.astype(np.float32),
        },
    )
    return {
        item.name: np.asarray(value, dtype=np.float32)
        for item, value in zip(
            active.get_outputs(), values, strict=True
        )
    }


def trace_contract(
    source_path: Path,
    reflected_path: Path,
    cases: list[dict[str, Any]],
) -> dict[str, Any]:
    source = session(source_path)
    reflected = session(reflected_path)
    zero_context = np.zeros((1, 64), dtype=np.float32)
    one_context = np.ones((1, 64), dtype=np.float32)
    rows = 0
    moving_rows = 0
    x0_rows = 0
    moving_changed = 0
    x0_changed = 0
    maximum_action_delta = 0.0
    maximum_x0_action_delta = 0.0
    maximum_source_x0_action_abs = 0.0
    maximum_reflected_x0_action_abs = 0.0
    maximum_hidden_error = 0.0
    maximum_context_error = 0.0
    finite = True
    feedback_exact = True
    case_rows = []
    for case in cases:
        count = 0
        changed = 0
        with Path(case["path"]).open("r", encoding="utf-8") as stream:
            for line in stream:
                if not line.strip():
                    continue
                row = json.loads(line)
                obs = np.asarray(row["obs_state"], dtype=np.float32).reshape(
                    1, 115
                )
                state = row["policy_state_input"]
                previous = np.asarray(
                    state["previous_action"], dtype=np.float32
                ).reshape(1, 14)
                hidden = np.asarray(
                    state["h_in"], dtype=np.float32
                ).reshape(1, 64)
                left = run(
                    source, obs, previous, hidden, zero_context
                )
                right_zero = run(
                    reflected, obs, previous, hidden, zero_context
                )
                right_one = run(
                    reflected, obs, previous, hidden, one_context
                )
                action_delta = float(
                    np.max(
                        np.abs(
                            left["continuous_actions"]
                            - right_zero["continuous_actions"]
                        )
                    )
                )
                action_changed = action_delta > 0.0
                maximum_action_delta = max(
                    maximum_action_delta, action_delta
                )
                maximum_hidden_error = max(
                    maximum_hidden_error,
                    float(
                        np.max(
                            np.abs(
                                left["h_out"] - right_zero["h_out"]
                            )
                        )
                    ),
                )
                maximum_context_error = max(
                    maximum_context_error,
                    max(
                        float(np.max(np.abs(right_zero[name] - right_one[name])))
                        for name in right_zero
                    ),
                )
                finite &= all(
                    np.all(np.isfinite(value))
                    for value in right_zero.values()
                )
                feedback_exact &= np.array_equal(
                    right_zero["continuous_actions"],
                    right_zero["previous_action_out"],
                )
                command = float(case["command_x_m_s"])
                if command == 0.0:
                    x0_rows += 1
                    x0_changed += int(action_changed)
                    maximum_x0_action_delta = max(
                        maximum_x0_action_delta, action_delta
                    )
                    maximum_source_x0_action_abs = max(
                        maximum_source_x0_action_abs,
                        float(
                            np.max(np.abs(left["continuous_actions"]))
                        ),
                    )
                    maximum_reflected_x0_action_abs = max(
                        maximum_reflected_x0_action_abs,
                        float(
                            np.max(
                                np.abs(
                                    right_zero["continuous_actions"]
                                )
                            )
                        ),
                    )
                else:
                    moving_rows += 1
                    moving_changed += int(action_changed)
                rows += 1
                count += 1
                changed += int(action_changed)
        if count != int(case["rows"]):
            raise RuntimeError(f"T152B trace row count changed: {case}")
        case_rows.append(
            {
                "fit_id": case["fit_id"],
                "command_x_m_s": case["command_x_m_s"],
                "rows": count,
                "action_changed_rows": changed,
            }
        )
    return {
        "providers": reflected.get_providers(),
        "rows": rows,
        "moving_rows": moving_rows,
        "x0_rows": x0_rows,
        "moving_action_changed_rows": moving_changed,
        "moving_action_changed_fraction": (
            moving_changed / moving_rows if moving_rows else 0.0
        ),
        "x0_action_changed_rows": x0_changed,
        "maximum_action_delta": maximum_action_delta,
        "maximum_x0_action_delta": maximum_x0_action_delta,
        "maximum_source_x0_action_abs": maximum_source_x0_action_abs,
        "maximum_reflected_x0_action_abs": (
            maximum_reflected_x0_action_abs
        ),
        "maximum_hidden_state_error": maximum_hidden_error,
        "maximum_context_dependence_error": maximum_context_error,
        "finite": bool(finite),
        "action_feedback_exact": bool(feedback_exact),
        "cases": case_rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    args = parser.parse_args()
    del args
    for path in (RESULT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T152B: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("formal T152B execution requires clean tree")

    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    validate_prereg(prereg)
    contracts: dict[str, Any] = {}
    for step in STEPS:
        cases = [
            item
            for item in prereg["trace_population"]
            if int(item["step"]) == step
        ]
        contracts[str(step)] = trace_contract(
            Path(
                prereg["frozen_inputs"][f"source_graph_{step}"]["path"]
            ),
            Path(
                prereg["frozen_inputs"][
                    f"reflected_graph_{step}"
                ]["path"]
            ),
            cases,
        )

    thresholds = prereg["thresholds"]
    checks = {
        "both_cached_graphs_evaluated": sorted(contracts)
        == [str(step) for step in STEPS],
        "realistic_moving_action_binding": all(
            row["moving_rows"]
            >= thresholds["minimum_realistic_moving_rows"]
            and row["moving_action_changed_rows"]
            >= thresholds["minimum_moving_action_changed_rows"]
            and row["moving_action_changed_fraction"]
            > thresholds["minimum_moving_action_changed_fraction"]
            and row["maximum_action_delta"] > 0.0
            for row in contracts.values()
        ),
        "hidden_state_path_exact": all(
            row["maximum_hidden_state_error"]
            == thresholds["maximum_hidden_state_error"]
            for row in contracts.values()
        ),
        "forced_branch_context_invariant": all(
            row["maximum_context_dependence_error"]
            == thresholds["maximum_context_dependence_error"]
            for row in contracts.values()
        ),
        "all_outputs_finite_and_feedback_exact": all(
            row["providers"][0] == "CPUExecutionProvider"
            and row["finite"]
            and row["action_feedback_exact"]
            for row in contracts.values()
        ),
        "x0_source_contradicts_arbitrary_zero_invariant": all(
            row["x0_rows"] > 0
            and row["maximum_source_x0_action_abs"] > 0.0
            for row in contracts.values()
        ),
        "x0_behavior_deferred_with_full_population": all(
            row["x0_rows"] == 1200 for row in contracts.values()
        ),
        "no_new_behavior_optimizer_hosted_or_hardware": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    passed = not failed
    result: dict[str, Any] = {
        "schema_version": (
            "open_duck.t152b_reflected_positive_expert_"
            "recovery_result.v1"
        ),
        "status": (
            "PASS_T152B_REFLECTED_POSITIVE_EXPERT_RECOVERY"
            if passed
            else "HOLD_T152B_REFLECTED_POSITIVE_EXPERT_RECOVERY"
        ),
        "decision": (
            prereg["decision_rule"]["pass_decision"]
            if passed
            else prereg["decision_rule"]["fail_decision"]
        ),
        "recovery_kind": prereg["recovery_kind"],
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "failed_t152_contract_sha256": prereg[
            "failed_t152_contract_sha256"
        ],
        "failed_t152_result_sha256": prereg[
            "failed_t152_result_sha256"
        ],
        "repository_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "contracts": contracts,
        "checks": checks,
        "failed_checks": failed,
        "execution": {
            "trace_rows_read": sum(
                row["rows"] for row in contracts.values()
            ),
            "new_behavior_cells": 0,
            "environment_steps": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "positive_endpoint_preregistration": passed,
            "positive_endpoint_execution": False,
            "positive_only_training_contract": False,
            "hosted_training": False,
            "policy_promotion": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    result["result_sha256"] = canonical_sha256(result)
    RESULT.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T152B reflected positive expert recovery result\n\n"
        f"- Status: `{result['status']}`\n"
        f"- Decision: `{result['decision']}`\n"
        f"- Failed checks: `{failed}`\n"
        "- New behavior / optimizer / Colab / robot: `0/0/0/0`\n"
        f"- Result SHA-256: `{result['result_sha256']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(result["status"])
    print(f"decision={result['decision']}")
    print(f"result_sha256={result['result_sha256']}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
