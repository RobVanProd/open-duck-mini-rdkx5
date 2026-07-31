from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "outputs/analysis/winner_v85_integrated_support_gate_result.json"


def failing_pairs(row: dict) -> set[tuple[str, str]]:
    return {
        (cell["configuration_id"], cell["plant"])
        for key in ("core_model_plant_cells", "sensor_transport_plant_cells")
        for cell in row[key]
        if not cell["support_pass"]
    }


def test_result_holds_without_selection_or_robot_clearance() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["status"] == "HOLD_WINNER_V85_INTEGRATED_SUPPORT_GATE"
    assert value["decision"] == "DO_NOT_SELECT_WINNER_V84_DEPLOYMENT_POLICY"
    assert value["selected_checkpoint"] is None
    assert value["failed_checks"] == ["all_248_main_cells_pass"]
    assert value["checks"] == {
        "both_checkpoints_evaluated": True,
        "all_248_main_cells_pass": False,
        "formal_cell_count_exact": True,
    }
    assert value["execution"] == {
        "formal_support_cells": 248,
        "heldout_repeat_cells": 64,
        "locomotion_training_steps": 0,
        "robot_or_rdk_access": 0,
    }
    assert value["authority"]["robot_clearance"] is False
    assert value["authority"]["execution_authorized_by_this_result"] is False
    assert value["authority"]["grounded_walking_authorized"] is False


def test_remaining_failures_are_roll_pitch_only_and_predictor_is_below_gate() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    half, final = value["checkpoint_results"]
    assert failing_pairs(half) == {
        ("COM_CORNER_01", "P30_ALL_JOINT"),
        ("COM_CORNER_01", "P31_34_PITCH_WITH_P30_NONPITCH"),
        ("COM_CORNER_03", "P30_ALL_JOINT"),
        ("COM_CORNER_03", "P31_34_PITCH_WITH_P30_NONPITCH"),
    }
    assert failing_pairs(final) == {
        ("COM_X_NEG", "P30_ALL_JOINT"),
        ("COM_X_NEG", "P31_34_PITCH_WITH_P30_NONPITCH"),
        ("COM_CORNER_01", "P30_ALL_JOINT"),
        ("COM_CORNER_01", "P31_34_PITCH_WITH_P30_NONPITCH"),
        ("COM_CORNER_03", "P30_ALL_JOINT"),
        ("COM_CORNER_03", "P31_34_PITCH_WITH_P30_NONPITCH"),
        ("DISCOVERY_03", "P30_ALL_JOINT"),
        ("DISCOVERY_03", "P31_34_PITCH_WITH_P30_NONPITCH"),
    }
    for row in (half, final):
        assert row["checks"]["all_support_cells_pass"] is False
        assert row["checks"]["learned_prediction_beats_constant_per_plant"] is False
        assert row["checks"]["all_32_heldout_repeats_bit_exact"] is True
        assert row["checks"]["all_16_heldout_contexts_separate"] is True
        assert row["checks"]["all_jax_onnx_hidden_errors_at_most_1e_7"] is True
        assert row["checks"]["all_previous_action_chains_exact"] is True
        for key in ("core_model_plant_cells", "sensor_transport_plant_cells"):
            for cell in row[key]:
                if not cell["support_pass"]:
                    assert cell["terminal"] is not None
                    assert [
                        name
                        for name, passed in cell["terminal"]["checks"].items()
                        if not passed
                    ] == ["roll_pitch"]
