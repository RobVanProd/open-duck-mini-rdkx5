from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "outputs/analysis/winner_v86_residual_pitch_causal_result.json"


def test_result_selects_only_a_new_mechanism_preregistration() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_WINNER_V86_RESIDUAL_PITCH_CAUSAL_DIAGNOSTIC"
    assert (
        value["decision"]
        == "SELECT_NEXT_MECHANISM_FROM_FROZEN_RESIDUAL_CLASSIFICATION_ONLY"
    )
    assert value["failed_checks"] == []
    assert value["checks"] == {
        "all_12_graph_cells_bit_exact_to_v85": True,
        "all_12_source_graph_cells_fail": True,
        "all_jax_onnx_hidden_errors_at_most_1e_7": True,
        "all_previous_action_chains_exact": True,
        "all_values_finite": True,
        "exact_48_cells": True,
    }
    assert value["execution"] == {
        "diagnostic_cells": 48,
        "locomotion_training_steps": 0,
        "optimizer_updates": 0,
        "robot_or_rdk_access": 0,
    }
    assert value["authority"]["robot_clearance"] is False
    assert value["authority"]["checkpoint_selection_authorized"] is False
    assert value["authority"]["training_authorized_now"] is False
    assert value["authority"]["rdkx5_robot_serial_gpio_i2c_torque_motion"] is False


def test_all_twelve_residual_failures_are_pitch_output_causal() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    findings = value["findings"]
    assert findings["classification_counts"] == {
        "either_single_intervention_rescues": 0,
        "nonpitch_output_causal": 0,
        "pitch_nonpitch_interaction": 0,
        "pitch_output_causal": 12,
        "teacher_insufficient": 0,
    }
    assert findings["support_pass_counts"] == {
        "full_teacher": 12,
        "graph": 0,
        "nonpitch_zero": 0,
        "pitch_teacher": 12,
    }
    assert len(findings["classification_rows"]) == 12
    assert {
        row["classification"] for row in findings["classification_rows"]
    } == {"pitch_output_causal"}
    assert findings["first_tick_pitch_rms_mean"] == 0.11153305383971929
    assert findings["post_first_tick_pitch_rms_mean"] == 0.10304415580358957


def test_predictor_failure_remains_separate_from_locomotion_cause() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    rows = value["findings"]["predictor_failure_by_checkpoint"]
    assert set(rows) == {"half", "final"}
    for checkpoint in rows.values():
        assert set(checkpoint) == {
            "P30_ALL_JOINT",
            "P31_34_PITCH_WITH_P30_NONPITCH",
        }
        for plant in checkpoint.values():
            assert plant["learned_strictly_below_constant"] is False
            assert (
                plant["learned_normalized_prediction_mse"]
                > plant["constant_normalized_prediction_mse"]
            )
