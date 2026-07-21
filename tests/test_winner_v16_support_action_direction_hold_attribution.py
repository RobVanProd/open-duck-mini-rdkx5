from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ATTRIBUTION = (
    ROOT / "outputs/analysis/winner_v16_support_action_direction_hold_attribution.json"
)


def test_single_axis_class_is_closed_and_sign_evidence_is_unanimous() -> None:
    value = json.loads(ATTRIBUTION.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PASS_WINNER_V16_SUPPORT_ACTION_DIRECTION_HOLD_ATTRIBUTION"
    )
    assert value["decision"] == (
        "CLOSE_SINGLE_AXIS_CONSTANT_OFFSET_PREREGISTER_SIGN_CONSISTENT_COMBINATION_DIAGNOSTIC"
    )
    assert not any(
        row["passes_both_checkpoints"]
        for row in value["single_axis_result"].values()
    )
    assert set(value["direction_evidence"]) == {
        "HIP_MAG_NEG",
        "KNEE_POS",
        "ANKLE_POS",
    }
    for row in value["direction_evidence"].values():
        assert row["compared_cells"] == 24
        assert row["desired_outlives_baseline_cells"] == 24
        assert row["desired_outlives_opposite_cells"] == 24
        assert row["opposite_shortens_baseline_cells"] == 24
        assert row["desired_minus_baseline_tick_range"][0] > 0
        assert row["desired_minus_opposite_tick_range"][0] > 0
        assert row["opposite_minus_baseline_tick_range"][1] < 0


def test_next_screen_is_complete_subset_diagnostic_without_training_authority() -> None:
    value = json.loads(ATTRIBUTION.read_text(encoding="utf-8"))
    screen = value["next_screen"]
    assert screen["interventions"] == [
        "BASELINE",
        "HIP_MAG_NEG",
        "KNEE_POS",
        "ANKLE_POS",
        "HIP_NEG_KNEE_POS",
        "HIP_NEG_ANKLE_POS",
        "KNEE_POS_ANKLE_POS",
        "HIP_NEG_KNEE_POS_ANKLE_POS",
    ]
    assert screen["total_cells"] == 192
    assert screen["offset_per_active_axis_rad"] == 0.03
    assert screen["optimizer_updates"] == 0
    assert value["execution"] == {
        "new_diagnostic_cells": 0,
        "optimizer_updates": 0,
        "robot_or_rdk_access": 0,
    }
    assert value["authority"]["robot_clearance"] is False
