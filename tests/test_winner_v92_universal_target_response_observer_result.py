from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = (
    ROOT / "outputs/analysis/winner_v92_universal_target_response_observer_result.json"
)


def test_result_holds_only_on_predictor_transfer() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["status"] == "HOLD_WINNER_V92_UNIVERSAL_TARGET_RESPONSE_OBSERVER"
    assert value["decision"] == "DO_NOT_USE_UNIVERSAL_TARGET_RESPONSE_OBSERVER"
    assert value["failed_checks"] == ["learned_prediction_beats_constant_per_plant"]
    assert value["failed_cells"] == []
    assert value["checks"]["all_124_support_cells_pass"] is True
    assert value["checks"]["all_16_heldout_contexts_separate"] is True
    assert value["checks"]["all_32_heldout_repeats_bit_exact"] is True
    assert value["checks"]["learned_prediction_beats_constant_per_plant"] is False


def test_action_state_and_prediction_evidence_is_exact() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["maximum_bounded_target_action_error"] == 0.0
    assert value["checks"]["all_previous_action_chains_exact"] is True
    assert value["checks"]["all_jax_onnx_hidden_errors_at_most_1e_7"] is True
    assert min(
        row["final_h_out_linf_separation"]
        for row in value["heldout_context_separation"]
    ) == 0.0010801255702972412
    assert value["heldout_prediction"] == {
        "P30_ALL_JOINT": {
            "constant_normalized_prediction_mse": 0.8660024273035073,
            "learned_normalized_prediction_mse": 0.9300278051707194,
            "learned_strictly_below_constant": False,
        },
        "P31_34_PITCH_WITH_P30_NONPITCH": {
            "constant_normalized_prediction_mse": 0.8682778689395438,
            "learned_normalized_prediction_mse": 0.9331387929700476,
            "learned_strictly_below_constant": False,
        },
    }


def test_result_has_no_training_artifact_or_hardware_authority() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["execution"] == {
        "formal_support_cells": 124,
        "heldout_repeat_cells": 32,
        "optimizer_updates": 0,
        "robot_or_rdk_access": 0,
        "snapshot_or_onnx_writes": 0,
    }
    assert value["authority"]["training_authorized_now"] is False
    assert value["authority"]["checkpoint_selection_authorized"] is False
    assert value["authority"]["deployment_authorized"] is False
    assert value["authority"]["robot_clearance"] is False
