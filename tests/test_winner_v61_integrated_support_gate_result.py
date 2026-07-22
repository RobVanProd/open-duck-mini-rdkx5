from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "outputs/analysis/winner_v61_integrated_support_gate_result.json"


def test_result_holds_both_checkpoints_without_selection() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["status"] == "HOLD_WINNER_V61_INTEGRATED_SUPPORT_GATE"
    assert value["decision"] == "DO_NOT_SELECT_WINNER_V60_DEPLOYMENT_POLICY"
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
        ("half", 504),
        ("final", 554),
    ]
    assert [
        sum(not cell["support_pass"] for cell in row["core_model_plant_cells"])
        for row in rows
    ] == [11, 13]
    for row in rows:
        assert row["checks"]["exact_124_main_cells"] is True
        assert row["checks"]["all_support_cells_pass"] is False
        assert row["checks"]["all_previous_action_chains_exact"] is True
        assert row["checks"]["all_jax_onnx_hidden_errors_at_most_1e_7"] is True
        assert row["checks"]["all_32_heldout_repeats_bit_exact"] is True
        assert row["checks"]["all_16_heldout_contexts_separate"] is True
        assert row["checks"]["learned_prediction_beats_constant_per_plant"] is True
        failures = [
            cell for cell in row["core_model_plant_cells"] if not cell["support_pass"]
        ]
        assert all(cell["terminal"]["checks"]["roll_pitch"] is False for cell in failures)
        assert all(
            all(
                passed
                for name, passed in cell["terminal"]["checks"].items()
                if name != "roll_pitch"
            )
            for cell in failures
        )
    assert value["authority"]["robot_clearance"] is False
    assert value["authority"]["execution_authorized_by_this_result"] is False
