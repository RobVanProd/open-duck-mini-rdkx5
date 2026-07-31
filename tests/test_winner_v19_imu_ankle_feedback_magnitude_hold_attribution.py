from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ATTRIBUTION = (
    ROOT
    / "outputs/analysis/winner_v19_imu_ankle_feedback_magnitude_hold_attribution.json"
)


def test_feedback_authority_and_wrapper_class_are_closed() -> None:
    value = json.loads(ATTRIBUTION.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PASS_WINNER_V19_IMU_ANKLE_FEEDBACK_MAGNITUDE_HOLD_ATTRIBUTION"
    )
    assert value["decision"] == (
        "CLOSE_POST_POLICY_ACTION_WRAPPERS_PREREGISTER_TRAINING_SIDE_CAUSAL_REPAIR"
    )
    assert value["failure_counts_half_final"]["CONSTANT_003"] == [8, 6]
    assert value["failure_counts_half_final"]["CONSTANT_006"] == [12, 12]
    assert value["failure_counts_half_final"]["TILT_RATE_006"] == [10, 8]
    assert value["failure_counts_half_final"]["TILT_RATE_009"] == [10, 8]
    assert len(value["closed_mechanisms"]) == 4


def test_attribution_grants_neither_training_nor_robot_authority() -> None:
    value = json.loads(ATTRIBUTION.read_text(encoding="utf-8"))
    assert value["next_work"]["optimizer_updates_authorized_now"] == 0
    assert value["next_work"]["diagnostic_cells_authorized_now"] == 0
    assert value["execution"] == {
        "new_diagnostic_cells": 0,
        "optimizer_updates": 0,
        "robot_or_rdk_access": 0,
    }
    assert value["authority"]["robot_clearance"] is False
    assert value["authority"]["rdkx5_robot_serial_gpio_i2c_torque_motion"] is False
