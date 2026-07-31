from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "outputs/analysis/winner_v94_stable_response_readout_result.json"


def test_result_holds_only_on_numeric_stability_bounds() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["status"] == "HOLD_WINNER_V94_STABLE_RESPONSE_READOUT"
    assert value["decision"] == "DO_NOT_SELECT_STABLE_RESPONSE_READOUT"
    assert value["failed_checks"] == [
        "condition_amplification_at_most_1e_minus_3",
        "heldout_float64_float32_delta_at_most_1e_minus_4",
    ]
    failed = set(value["failed_checks"])
    assert all(passed for name, passed in value["checks"].items() if name not in failed)


def test_readout_is_predictive_but_not_numerically_selected() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["fit"]["rank"] == 65
    assert value["fit"]["feature_dimension"] == 65
    assert value["fit"]["condition_number"] == 194311.27277166364
    assert value["fit"]["condition_number_times_float32_epsilon"] == 0.023163708778818088
    assert value["fit"]["heldout_float64_float32_maximum_abs"] == 0.000707581060225948
    assert value["fit"]["coefficient_maximum_abs"] == 770.3970336914062
    expected = {
        "P30_ALL_JOINT": 0.0070873889394893995,
        "P31_34_PITCH_WITH_P30_NONPITCH": 0.006904531331492193,
    }
    for plant, mse in expected.items():
        row = value["heldout_by_plant"][plant]
        assert row["fitted_float32_normalized_prediction_mse"] == mse
        assert mse < row["frozen_predictor_normalized_prediction_mse"]
        assert mse < row["constant_normalized_prediction_mse"]


def test_result_has_no_policy_artifact_or_hardware_authority() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["execution"] == {
        "least_squares_fits": 1,
        "optimizer_updates": 0,
        "robot_or_rdk_access": 0,
        "snapshot_or_onnx_writes": 0,
        "source_trace_cells": 112,
    }
    assert value["authority"]["checkpoint_selection_authorized"] is False
    assert value["authority"]["deployment_authorized"] is False
    assert value["authority"]["robot_clearance"] is False
