#!/usr/bin/env python3
"""Preregister the saved-trace bilateral single-support failure audit."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
from typing import Any

from run_t136_static_calibration_router_transform import (
    ANALYSIS,
    ROOT,
    canonical_sha256,
    receipt,
)


T180B_PREREG = (
    ANALYSIS / "t180b_transform_route_attribution_preregistration.json"
)
T180B_RESULT = ANALYSIS / "t180b_transform_route_attribution_result.json"
T182B_RESULT = ANALYSIS / "t182b_shared_failure_single_cell_result.json"
T183B_RESULT = ANALYSIS / "t183b_hidden_gate_confidence_result.json"
T183_RECOVERY = ANALYSIS / "t183_receipt_schema_recovery_20260730.json"
OUTPUT = (
    ANALYSIS / "t184_bilateral_single_support_anatomy_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "T184_BILATERAL_SINGLE_SUPPORT_ANATOMY_PREREGISTRATION_20260730.md"
)
BUILDER = Path(__file__).resolve()
RUNNER = ROOT / "tools" / "run_t184_bilateral_single_support_anatomy.py"
TEST = ROOT / "tests" / "test_t184_bilateral_single_support_anatomy.py"


def _load(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(path)
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"JSON root is not an object: {path}")
    return value


def _canonical_without(value: dict[str, Any], field: str) -> str:
    basis = dict(value)
    basis.pop(field, None)
    return canonical_sha256(basis)


def _normalized_trace(old: dict[str, Any]) -> dict[str, Any]:
    path = Path(old["path"])
    value = receipt(path)
    if value["sha256"] != old["sha256"]:
        raise RuntimeError(f"trace SHA differs: {path}")
    return value


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T184: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T184 preregistration requires clean worktree")

    t180b_prereg = _load(T180B_PREREG)
    t180b_result = _load(T180B_RESULT)
    t182b_result = _load(T182B_RESULT)
    t183b_result = _load(T183B_RESULT)
    t183_recovery = _load(T183_RECOVERY)
    for value, field, label in (
        (t180b_prereg, "preregistered_contract_sha256", "T180B prereg"),
        (t180b_result, "result_sha256", "T180B result"),
        (t182b_result, "result_sha256", "T182B result"),
        (t183b_result, "result_sha256", "T183B result"),
        (t183_recovery, "result_sha256", "T183 recovery"),
    ):
        if _canonical_without(value, field) != value[field]:
            raise RuntimeError(f"{label} hash differs")
    if (
        t183b_result["decision"]
        != "CLOSE_EXISTING_HIDDEN_SCORE_CONTEXT_GATE_AND_RETURN_TO_"
        "MECHANISM_SELECTION"
    ):
        raise RuntimeError("T183B has not returned to mechanism selection")

    traces = []
    for case in t180b_prereg["cases"]:
        for role in ("source", "transformed"):
            traces.append(
                {
                    "trace_id": f"{case['case_id']}:{role}",
                    "case_id": case["case_id"],
                    "family": case["family"],
                    "condition_id": case["condition_id"],
                    "checkpoint_pair": case["checkpoint_pair"],
                    "fit_id": case["fit_id"],
                    "command_x_m_s": case["command_x_m_s"],
                    "policy_role": role,
                    "expected_green": bool(
                        case[f"{role}_cell_green"]
                    ),
                    "trace": _normalized_trace(case[f"{role}_trace"]),
                }
            )
    alpha_trace = t182b_result["cell"]["protection"]
    traces.append(
        {
            "trace_id": "Z_POS_SHARED_ALPHA_0P2_HALF_P31_X077:alpha_0p2",
            "case_id": "Z_POS_SHARED_ALPHA_0P2_HALF_P31_X077",
            "family": "positive_z_shared_failure",
            "condition_id": "TORSO_COM_Z_POS",
            "checkpoint_pair": "half",
            "fit_id": "p31_34",
            "command_x_m_s": 0.077,
            "policy_role": "alpha_0p2",
            "expected_green": False,
            "trace": _normalized_trace(alpha_trace),
        }
    )
    green = sum(row["expected_green"] for row in traces)
    failed = len(traces) - green
    if len(traces) != 13 or green != 5 or failed != 8:
        raise RuntimeError(
            f"unexpected T184 trace population: {len(traces)}/{green}/{failed}"
        )

    basis: dict[str, Any] = {
        "schema_version": (
            "open_duck.t184_bilateral_single_support_anatomy_"
            "preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T184_BILATERAL_SINGLE_SUPPORT_ANATOMY"
        ),
        "question": (
            "Do the eight current policy falls remain mechanically linked "
            "to recent single-foot support on both sides, strongly enough "
            "to earn a default-off bilateral single-support curriculum "
            "software contract before any training?"
        ),
        "frozen_inputs": {
            "builder": receipt(BUILDER),
            "runner": receipt(RUNNER),
            "test": receipt(TEST),
            "t180b_preregistration": receipt(T180B_PREREG),
            "t180b_result": receipt(T180B_RESULT),
            "t182b_result": receipt(T182B_RESULT),
            "t183b_result": receipt(T183B_RESULT),
            "t183_receipt_recovery": receipt(T183_RECOVERY),
        },
        "traces": traces,
        "population": {
            "trace_count": 13,
            "passing_traces": 5,
            "failing_traces": 8,
            "source_transformed_pairs": 6,
            "alpha_traces": 1,
            "new_behavior_cells": 0,
        },
        "analysis_contract": {
            "gait_period_ticks": 20,
            "terminal_window_ticks": 40,
            "maximum_ticks_from_last_supported_to_done": 20,
            "contact_modes": {
                "none": [0, 0],
                "left_only": [1, 0],
                "right_only": [0, 1],
                "both": [1, 1],
            },
            "last_supported_tick": (
                "last trace row whose contact mode is not none"
            ),
            "terminal_single_support_link": (
                "last supported mode is left_only or right_only and done "
                "occurs no more than one frozen gait period later"
            ),
            "bilateral_requirement": (
                "the last-supported modes across failures include both "
                "left_only and right_only"
            ),
            "passing_requirement": (
                "every expected-green trace has exactly 600 contiguous rows "
                "and no done row"
            ),
            "failing_requirement": (
                "every expected-failure trace is shorter than 600 rows and "
                "ends with done=true"
            ),
            "threshold_search": False,
            "feature_search": False,
        },
        "decision_rule": {
            "pass": (
                "EARN_T185_BILATERAL_SINGLE_SUPPORT_CURRICULUM_CPU_"
                "CONTRACT_PREREGISTRATION_ONLY"
            ),
            "fail": (
                "NO_SINGLE_SUPPORT_CURRICULUM_RUN_EARNED_RETURN_TO_"
                "MECHANISM_SELECTION"
            ),
            "no_training_from_this_result": True,
        },
        "execution_now": {
            "saved_trace_rows": 0,
            "new_behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority_after_result": {
            "curriculum_cpu_contract_preregistration_if_pass": True,
            "curriculum_implementation": False,
            "new_behavior": False,
            "optimizer": False,
            "hosted_compute": False,
            "deployment_contract_audit": False,
            "gate5": False,
            "robot_or_rdk": False,
        },
    }
    value = {
        **basis,
        "preregistered_contract_sha256": canonical_sha256(basis),
    }
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T184 bilateral single-support anatomy preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Population: 8 failures, 5 matched passes, 13 saved traces\n"
        "- Terminal window: two gait periods; support-loss allowance: one "
        "gait period\n"
        "- Pass requires every failure to link to recent single support and "
        "both support sides to occur.\n"
        "- New behavior / optimizer / hosted compute / robot: `0/0/0/0`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
