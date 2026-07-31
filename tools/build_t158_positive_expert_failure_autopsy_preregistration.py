#!/usr/bin/env python3
"""Freeze the paired T151/T157 positive-COM failure autopsy."""

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


T151 = ANALYSIS / "t151_command_plateau_full_r2_result.json"
T157 = ANALYSIS / "t157_positive_com_endpoint_result.json"
OUTPUT = (
    ANALYSIS
    / "t158_positive_expert_failure_autopsy_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "T158_POSITIVE_EXPERT_FAILURE_AUTOPSY_PREREGISTRATION_20260729.md"
)
BUILDER = Path(__file__).resolve()
RUNNER = ROOT / "tools" / "run_t158_positive_expert_failure_autopsy.py"
TEST = ROOT / "tests" / "test_t158_positive_expert_failure_autopsy.py"


def trace_receipts(result: dict[str, Any]) -> list[dict[str, Any]]:
    values = []
    for block in result["blocks"]:
        if block["condition_id"] != "TORSO_COM_X_POS":
            continue
        for cell in block["result"]["cells"]:
            item = cell["protection"]
            values.append(
                {
                    "path": item["path"],
                    "bytes": Path(item["path"]).stat().st_size,
                    "sha256": item["sha256"],
                }
            )
    return values


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T158: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T158 preregistration requires clean worktree")
    t151 = json.loads(T151.read_text(encoding="utf-8"))
    t157 = json.loads(T157.read_text(encoding="utf-8"))
    old_traces = trace_receipts(t151)
    new_traces = trace_receipts(t157)
    frozen = {
        "builder": BUILDER,
        "runner": RUNNER,
        "test": TEST,
        "t151_result": T151,
        "t157_result": T157,
    }
    checks = {
        "t151_positive_endpoint_is_original_failure": (
            t151["status"] == "HOLD_T151_COMMAND_PLATEAU_FULL_R2"
            and t151["summary"]["first_failed_condition"]
            == "TORSO_COM_X_POS"
        ),
        "t157_positive_expert_closed": (
            t157["status"] == "HOLD_T157_POSITIVE_COM_ENDPOINT"
            and t157["decision"]
            == "CLOSE_POSITIVE_ONLY_EXPERT_FORMULATION"
            and t157["condition"]["green_cells"] == 4
        ),
        "sixteen_old_and_new_traces": (
            len(old_traces) == 16
            and len(new_traces) == 16
            and all(
                Path(item["path"]).is_file()
                for item in (*old_traces, *new_traces)
            )
        ),
        "frozen_inputs_present": all(
            path.is_file() for path in frozen.values()
        ),
        "no_behavior_training_colab_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T158 preregistration checks failed: {failed}")
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t158_positive_expert_failure_autopsy_"
            "preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T158_POSITIVE_EXPERT_FAILURE_AUTOPSY"
        ),
        "question": (
            "Did the positive expert improve survival while leaving a "
            "leading forward-pitch instability, and did continued "
            "training regress that improvement?"
        ),
        "populations": {
            "old": "T151 T149B positive-COM condition",
            "new": "T157 T156B positive-COM condition",
            "paired_dimensions": [
                "checkpoint step",
                "actuator fit",
                "command",
            ],
            "moving_pairs": 12,
            "x0_pairs": 4,
        },
        "thresholds": {
            "forward_pitch_rad": 0.25,
            "absolute_roll_rad": 0.25,
            "minimum_base_height_m": 0.12,
            "near_full_horizon_ticks": 570,
            "full_horizon_ticks": 600,
        },
        "measurements": [
            "paired termination tick gain",
            "first pitch/roll/height crossing order",
            "pitch sign at first pitch crossing",
            "pre-pitch mean body-forward velocity",
            "per-joint action delta over paired common prefix",
            "half-versus-final survival direction",
            "saturation/rate/track-quality invariants",
        ],
        "old_traces": old_traces,
        "new_traces": new_traces,
        "joint_order": [
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
        ],
        "decision_rule": {
            "mechanics_screen_if": [
                "all 12 moving T157 cells fail but all four x0 pass",
                "median moving survival improves over paired T151",
                "at least one T157 moving cell reaches 570 ticks",
                "positive pitch crosses 0.25 rad before roll/height in "
                "all T157 moving failures",
                "all T157 moving cells retain zero saturation/rate "
                "excess and tracking p95 <= 0.20 rad",
                "final-checkpoint median survival is below half",
            ],
            "pass_decision": (
                "EARN_T159_MECHANICS_DERIVED_SAGITTAL_"
                "COMPENSATION_PREREGISTRATION_ONLY"
            ),
            "fail_decision": (
                "HOLD_FOR_DIFFERENT_POSITIVE_COM_MECHANISM"
            ),
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
            "mechanics_screen_preregistration": False,
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
        "# T158 positive-expert failure autopsy preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Read-only pairing: T151 old path versus T157 specialist\n"
        "- Frozen thresholds: pitch/roll `0.25 rad`, height `0.12 m`\n"
        "- No new behavior, optimizer, Colab, or robot\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
