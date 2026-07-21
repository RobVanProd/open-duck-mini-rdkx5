from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ATTRIBUTION = ROOT / "outputs/analysis/winner_v18_imu_ankle_feedback_hold_attribution.json"


def test_same_ceiling_feedback_is_closed() -> None:
    value = json.loads(ATTRIBUTION.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_WINNER_V18_IMU_ANKLE_FEEDBACK_HOLD_ATTRIBUTION"
    assert value["decision"] == (
        "CLOSE_003_RAD_FEEDBACK_PREREGISTER_ONE_VARIABLE_MAGNITUDE_FEASIBILITY_SCREEN"
    )
    assert value["failure_counts_half_final"]["CONSTANT_ANKLE_POS"] == [8, 6]
    assert value["failure_counts_half_final"]["TILT_RATE_BACKWARD"] == [10, 10]
    assert 0.30 < value["magnitude_basis"]["combined_mean_activation"] < 0.32


def test_next_screen_has_one_frozen_variable_and_no_training_authority() -> None:
    value = json.loads(ATTRIBUTION.read_text(encoding="utf-8"))
    assert value["magnitude_basis"]["selected_multipliers"] == [1, 2, 3]
    assert value["magnitude_basis"]["maximum_target_offsets_rad"] == [0.03, 0.06, 0.09]
    assert value["next_screen"]["total_cells"] == 168
    assert value["next_screen"]["optimizer_updates"] == 0
    assert value["execution"] == {
        "new_diagnostic_cells": 0,
        "optimizer_updates": 0,
        "robot_or_rdk_access": 0,
    }
    assert value["authority"]["robot_clearance"] is False
