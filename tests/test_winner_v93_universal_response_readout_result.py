from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "outputs/analysis/winner_v93_universal_response_readout_result.json"


def test_result_passes_heldout_response_signal_gate() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_WINNER_V93_UNIVERSAL_RESPONSE_READOUT"
    assert (
        value["classification"]
        == "FROZEN_RECURRENT_STATE_HAS_HELDOUT_LINEAR_RESPONSE_SIGNAL"
    )
    assert value["decision"] == "PREREGISTER_UNIVERSAL_ACTION_OBSERVER_CPU_CONTRACT"
    assert value["failed_checks"] == []
    assert all(value["checks"].values())


def test_fitted_readout_beats_both_comparators_per_plant() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    expected = {
        "P30_ALL_JOINT": (0.38359192399422576, 0.9308577122034833, 0.8668286194721997),
        "P31_34_PITCH_WITH_P30_NONPITCH": (
            0.37373251908611277,
            0.9339749383552354,
            0.8691100097005369,
        ),
    }
    for plant, (fitted, frozen, constant) in expected.items():
        row = value["heldout_by_plant"][plant]
        assert row["fitted_normalized_prediction_mse"] == fitted
        assert row["frozen_predictor_normalized_prediction_mse"] == frozen
        assert row["constant_normalized_prediction_mse"] == constant
        assert fitted < frozen and fitted < constant


def test_result_exposes_rank_and_coefficient_stability_risk() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["fit"]["rank"] == 70
    assert value["fit"]["feature_dimension"] == 79
    assert value["fit"]["coefficient_maximum_abs"] == 290354176.0
    assert (
        value["fit"]["coefficient_sha256"]
        == "2a9ba80bdba96714d2c3a1106ec3c1a07b240af794b6bf0e7aeea191ce128888"
    )
    assert value["execution"] == {
        "least_squares_fits": 1,
        "optimizer_updates": 0,
        "robot_or_rdk_access": 0,
        "snapshot_or_onnx_writes": 0,
        "source_trace_cells": 112,
    }
    assert value["authority"]["robot_clearance"] is False
