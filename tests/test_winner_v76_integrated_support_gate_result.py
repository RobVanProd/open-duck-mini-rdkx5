from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "outputs/analysis/winner_v76_integrated_support_gate_result.json"


def failed_pairs(row: dict) -> list[tuple[str, str]]:
    cells = row["core_model_plant_cells"] + row["sensor_transport_plant_cells"]
    return [
        (cell["configuration_id"], cell["plant"])
        for cell in cells
        if not cell["support_pass"]
    ]


def test_result_holds_both_endpoints_without_selection() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["status"] == "HOLD_WINNER_V76_INTEGRATED_SUPPORT_GATE"
    assert value["decision"] == "DO_NOT_SELECT_WINNER_V75_DEPLOYMENT_POLICY"
    assert value["failed_checks"] == ["all_248_main_cells_pass"]
    assert value["selected_checkpoint"] is None
    assert value["execution"] == {
        "formal_support_cells": 248,
        "heldout_repeat_cells": 64,
        "locomotion_training_steps": 0,
        "robot_or_rdk_access": 0,
    }
    rows = value["checkpoint_results"]
    assert [(row["label"], row["update"]) for row in rows] == [
        ("half", 605),
        ("final", 655),
    ]
    assert [len(failed_pairs(row)) for row in rows] == [10, 9]
    assert rows[0]["checks"]["learned_prediction_beats_constant_per_plant"] is True
    assert rows[1]["checks"]["learned_prediction_beats_constant_per_plant"] is False
    for row in rows:
        cells = row["core_model_plant_cells"] + row["sensor_transport_plant_cells"]
        failures = [cell for cell in cells if not cell["support_pass"]]
        assert all(cell["terminal"]["checks"]["roll_pitch"] is False for cell in failures)
        assert all(
            all(
                passed
                for name, passed in cell["terminal"]["checks"].items()
                if name != "roll_pitch"
            )
            for cell in failures
        )
        assert row["checks"]["all_previous_action_chains_exact"] is True
        assert row["checks"]["all_jax_onnx_hidden_errors_at_most_1e_7"] is True
        assert row["checks"]["all_32_heldout_repeats_bit_exact"] is True
        assert row["checks"]["all_16_heldout_contexts_separate"] is True
    assert rows[1]["heldout_prediction"] == {
        "P30_ALL_JOINT": {
            "constant_normalized_prediction_mse": 0.22133911194408576,
            "learned_normalized_prediction_mse": 0.48976497452680934,
            "learned_strictly_below_constant": False,
        },
        "P31_34_PITCH_WITH_P30_NONPITCH": {
            "constant_normalized_prediction_mse": 0.22115866100783338,
            "learned_normalized_prediction_mse": 0.4907547941652682,
            "learned_strictly_below_constant": False,
        },
    }
    assert value["authority"]["robot_clearance"] is False
    assert value["authority"]["execution_authorized_by_this_result"] is False
