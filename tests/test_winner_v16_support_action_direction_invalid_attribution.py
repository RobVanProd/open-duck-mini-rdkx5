from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ATTRIBUTION = (
    ROOT
    / "outputs/analysis/winner_v16_support_action_direction_invalid_attribution.json"
)


def test_invalid_direction_result_is_attributed_without_interpretation() -> None:
    value = json.loads(ATTRIBUTION.read_text(encoding="utf-8"))
    assert value["status"] == (
        "INVALID_WINNER_V16_SUPPORT_ACTION_DIRECTION_DIAGNOSTIC_ATTRIBUTED"
    )
    assert value["decision"] == (
        "CORRECT_ONLY_BASELINE_DERIVED_FLOAT_COMPARATOR_AND_FRESHLY_PREREGISTER"
    )
    assert value["repository_attribution"]["github_run_id"] == 29845904251
    assert value["repository_attribution"]["github_run_attempt"] == 1
    attribution = value["attribution"]
    assert attribution["baseline_cells"] == 24
    assert attribution["old_exact_comparator_failure_cells"] == 24
    assert attribution["exact_decision_and_scalar_cells"] == 24
    assert attribution["exact_observation_action_prediction_hidden_hash_cells"] == 24
    assert attribution["exact_source_previous_action_output_cells"] == 24
    assert attribution["global_maximum_absolute_difference"] < 1.0e-12
    assert set(attribution["mismatch_paths"]) == {
        "episode.maximum_abs_tilt_rad",
        "episode.maximum_current_a",
        "episode.maximum_final_window_gyro_xy_norm_rad_s",
        "episode.maximum_torque_nm",
        "terminal.base_z_m",
        "terminal.gyro_xy_norm_rad_s",
        "terminal.maximum_current_a",
        "terminal.maximum_torque_nm",
        "terminal.pitch_rad",
        "terminal.roll_rad",
    }
    assert value["execution"] == {
        "completed_diagnostic_cells": 168,
        "valid_interpreted_cells": 0,
        "optimizer_updates": 0,
        "robot_or_rdk_access": 0,
    }
    assert value["authority"]["robot_clearance"] is False


def test_correction_changes_only_derived_float_equivalence() -> None:
    value = json.loads(ATTRIBUTION.read_text(encoding="utf-8"))
    correction = value["correction"]
    assert correction["derived_float_fields"] == ["terminal", "episode"]
    assert correction["finite_absolute_tolerance"] == 1.0e-12
    assert correction["all_other_compared_fields"] == "exact"
    assert correction["observation_action_prediction_hidden_trace_hashes"] == "exact"
    assert (
        correction[
            "population_interventions_offset_seeds_thresholds_and_selection_rule"
        ]
        == "unchanged"
    )
