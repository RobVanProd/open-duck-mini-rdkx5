from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ATTRIBUTION = (
    ROOT / "outputs/analysis/winner_v17_support_action_combination_hold_attribution.json"
)


def test_fixed_offset_subsets_are_closed() -> None:
    value = json.loads(ATTRIBUTION.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PASS_WINNER_V17_SUPPORT_ACTION_COMBINATION_HOLD_ATTRIBUTION"
    )
    assert value["decision"] == (
        "CLOSE_FIXED_003_RAD_OFFSET_SUBSET_PREREGISTER_ONE_SIDED_IMU_ANKLE_FEEDBACK_DIAGNOSTIC"
    )
    failures = value["failure_counts_half_final"]
    assert failures["ANKLE_POS"] == [8, 6]
    assert failures["KNEE_POS_ANKLE_POS"] == [8, 7]
    assert failures["HIP_NEG_ANKLE_POS"] == [12, 12]
    assert failures["HIP_NEG_KNEE_POS_ANKLE_POS"] == [12, 12]


def test_next_screen_is_deployable_input_feedback_only() -> None:
    value = json.loads(ATTRIBUTION.read_text(encoding="utf-8"))
    screen = value["next_screen"]
    assert screen["observation_inputs"] == {
        "gyro_pitch_rate": {"index": 1, "source": "gyro y"},
        "accelerometer_pitch_proxy": {"index": 3, "source": "accelerometer x"},
    }
    assert screen["maximum_target_offset_rad"] == 0.03
    assert screen["tilt_boundary_rad"] == 0.35
    assert screen["rate_reference_rad_s"] == 1.75
    assert screen["total_cells"] == 168
    assert screen["optimizer_updates"] == 0
    assert value["execution"] == {
        "new_diagnostic_cells": 0,
        "optimizer_updates": 0,
        "robot_or_rdk_access": 0,
    }
    assert value["authority"]["robot_clearance"] is False
