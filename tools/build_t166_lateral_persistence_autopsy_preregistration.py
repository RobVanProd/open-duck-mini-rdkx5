#!/usr/bin/env python3
"""Freeze the T165 negative-lateral-COM persistence autopsy."""

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


T165 = ANALYSIS / "t165_composed_full_r2_result.json"
OUTPUT = ANALYSIS / "t166_lateral_persistence_autopsy_preregistration.json"
MARKDOWN = (
    ANALYSIS
    / "T166_LATERAL_PERSISTENCE_AUTOPSY_PREREGISTRATION_20260729.md"
)
BUILDER = Path(__file__).resolve()
RUNNER = ROOT / "tools" / "run_t166_lateral_persistence_autopsy.py"
TEST = ROOT / "tests" / "test_t166_lateral_persistence_autopsy.py"
CONDITIONS = ("ARMATURE_LO", "TORSO_COM_Y_NEG")
JOINT_ORDER = [
    "left_hip_yaw",
    "left_hip_roll",
    "left_hip_pitch",
    "left_knee",
    "left_ankle",
    "neck_pitch",
    "head_pitch",
    "head_yaw",
    "head_roll",
    "right_hip_yaw",
    "right_hip_roll",
    "right_hip_pitch",
    "right_knee",
    "right_ankle",
]


def trace_receipts(result: dict[str, Any]) -> list[dict[str, Any]]:
    values: list[dict[str, Any]] = []
    for block in result["blocks"]:
        if block["condition_id"] not in CONDITIONS:
            continue
        for cell in block["result"]["cells"]:
            protection = cell["protection"]
            path = Path(protection["path"])
            values.append(
                {
                    "condition_id": block["condition_id"],
                    "checkpoint_id": block["checkpoint_id"],
                    "step": int(block["step"]),
                    "fit_id": block["fit_id"],
                    "command_x_m_s": float(cell["command_x_m_s"]),
                    "cell_green": bool(cell["cell_green"]),
                    "context_sha256": cell["handoff"]["context_sha256"],
                    "path": str(path),
                    "bytes": path.stat().st_size,
                    "rows": int(protection["rows"]),
                    "sha256": protection["sha256"],
                }
            )
    values.sort(
        key=lambda item: (
            item["condition_id"],
            item["step"],
            item["fit_id"],
            item["command_x_m_s"],
        )
    )
    return values


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T166: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T166 preregistration requires clean worktree")
    t165 = json.loads(T165.read_text(encoding="utf-8"))
    traces = trace_receipts(t165)
    condition_summary = {
        item["condition_id"]: item
        for item in t165["conditions"]
        if item["condition_id"] in CONDITIONS
    }
    frozen = {
        "builder": BUILDER,
        "runner": RUNNER,
        "test": TEST,
        "t165_result": T165,
    }
    checks = {
        "t165_stopped_at_negative_lateral_com": (
            t165["status"] == "HOLD_T165_COMPOSED_FULL_R2"
            and t165["summary"]["first_failed_condition"]
            == "TORSO_COM_Y_NEG"
        ),
        "default_equivalent_control_green": (
            condition_summary["ARMATURE_LO"]["condition_green"]
            and condition_summary["ARMATURE_LO"]["green_cells"] == 16
        ),
        "negative_lateral_result_is_eleven_of_sixteen": (
            not condition_summary["TORSO_COM_Y_NEG"]["condition_green"]
            and condition_summary["TORSO_COM_Y_NEG"]["green_cells"] == 11
        ),
        "thirty_two_protected_traces": (
            len(traces) == 32
            and all(Path(item["path"]).is_file() for item in traces)
        ),
        "matrix_coordinates_exact": (
            len(
                {
                    (
                        item["condition_id"],
                        item["checkpoint_id"],
                        item["fit_id"],
                        item["command_x_m_s"],
                    )
                    for item in traces
                }
            )
            == 32
        ),
        "frozen_inputs_present": all(path.is_file() for path in frozen.values()),
        "no_behavior_training_colab_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T166 preregistration checks failed: {failed}")
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t166_lateral_persistence_autopsy_"
            "preregistration.v1"
        ),
        "status": "PREREGISTERED_T166_LATERAL_PERSISTENCE_AUTOPSY",
        "question": (
            "Why does T164 final pass all negative-lateral-COM cells while "
            "T164 half fails five, despite both passing the default-equivalent "
            "control condition?"
        ),
        "populations": {
            "control_condition": "ARMATURE_LO",
            "failure_condition": "TORSO_COM_Y_NEG",
            "checkpoints": ["T164_COMPOSED_HALF", "T164_COMPOSED_FINAL"],
            "fits": ["p30", "p31_34"],
            "commands_x_m_s": [0.0, 0.074, 0.077, 0.08],
            "protected_traces": 32,
            "half_final_failure_pairs": 8,
            "condition_control_pairs": 16,
        },
        "thresholds": {
            "absolute_roll_rad": 0.25,
            "absolute_pitch_rad": 0.25,
            "minimum_base_height_m": 0.12,
            "early_action_window_ticks": 64,
            "full_horizon_ticks": 600,
            "minimum_roll_leading_failures_for_lateral_class": 4,
            "minimum_final_green_cells": 8,
        },
        "measurements": [
            "first absolute roll, absolute pitch, and low-height crossings",
            "failure-leading axis and signed roll direction",
            "half-versus-final action, base-action, phase-correction, applied-target, actual-position, and force deltas",
            "negative-lateral-versus-control deltas within each checkpoint",
            "per-joint tick-0, first-64-tick RMS, and common-prefix RMS",
            "hip-roll share of early half-versus-final action divergence",
            "calibration-context equality across checkpoints",
            "saturation, rate, tracking, and handoff invariants",
        ],
        "joint_order": JOINT_ORDER,
        "lateral_joint_names": [
            "left_hip_yaw",
            "left_hip_roll",
            "right_hip_yaw",
            "right_hip_roll",
        ],
        "traces": traces,
        "decision_rule": {
            "lateral_response_screen_if": [
                "T164 final is 8/8 green and T164 half is below 8/8",
                "all five half failures are valid protected traces",
                "at least four of five half failures cross absolute roll before absolute pitch and low height",
                "paired calibration contexts are identical between checkpoints",
                "all final cells retain zero saturation/rate excess and tracking p95 <= 0.20 rad",
            ],
            "pass_decision": (
                "EARN_T167_ZERO_TRAINING_LATERAL_RESPONSE_"
                "CAUSAL_SCREEN_PREREGISTRATION_ONLY"
            ),
            "fail_decision": "HOLD_FOR_DIFFERENT_PERSISTENCE_MECHANISM",
        },
        "frozen_inputs": {
            name: receipt(path) for name, path in frozen.items()
        },
        "checks": checks,
        "failed_checks": failed,
        "execution_now": {
            "trace_rows_read": 0,
            "behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "one_read_only_trace_autopsy": True,
            "causal_behavior_screen_preregistration": False,
            "behavior_evaluation": False,
            "training": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    value["preregistered_contract_sha256"] = canonical_sha256(value)
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T166 lateral-persistence autopsy preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Frozen population: 32 protected T165 traces\n"
        "- Pairing: condition 9 versus default-equivalent condition 5, "
        "plus half versus final\n"
        "- No new behavior, optimizer, Colab, RDK, or robot\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
