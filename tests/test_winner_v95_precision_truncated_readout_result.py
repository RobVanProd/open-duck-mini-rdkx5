from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "outputs/analysis/winner_v95_precision_truncated_readout_result.json"


def test_result_passes_complete_precision_contract() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_WINNER_V95_PRECISION_TRUNCATED_READOUT"
    assert value["decision"] == "PREREGISTER_RESPONSE_CONDITIONED_LOCOMOTION_CPU_CONTRACT"
    assert value["failed_checks"] == []
    assert all(value["checks"].values())


def test_precision_selected_rank_and_float32_bounds_are_exact() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    fit = value["fit"]
    assert fit["original_rank"] == 65
    assert fit["retained_rank"] == 28
    assert fit["retained_condition_number"] == 7294.13939627666
    assert fit["condition_number_times_float32_epsilon"] == 0.0008695291753145051
    assert fit["heldout_float64_float32_maximum_abs"] == 9.331073880680663e-05
    assert fit["coefficient_maximum_abs"] == 128.03909301757812
    assert (
        fit["combined_coefficient_sha256"]
        == "ccab7d2ad3b2a29591f6696eba5c08a4b6446ebab3d246a46bbc6f2043419e76"
    )


def test_stable_readout_beats_both_comparators_per_plant() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    expected = {
        "P30_ALL_JOINT": 0.009943151995521256,
        "P31_34_PITCH_WITH_P30_NONPITCH": 0.009648919196881605,
    }
    for plant, mse in expected.items():
        row = value["heldout_by_plant"][plant]
        assert row["fitted_float32_normalized_prediction_mse"] == mse
        assert mse < row["frozen_predictor_normalized_prediction_mse"]
        assert mse < row["constant_normalized_prediction_mse"]
    assert value["execution"] == {
        "optimizer_updates": 0,
        "robot_or_rdk_access": 0,
        "snapshot_or_onnx_writes": 0,
        "source_trace_cells": 112,
        "svd_fits": 1,
    }
    assert value["authority"]["robot_clearance"] is False
