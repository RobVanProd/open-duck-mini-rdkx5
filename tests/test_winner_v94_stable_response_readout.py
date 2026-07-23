from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PREREGISTRATION = (
    ROOT / "outputs/analysis/winner_v94_stable_response_readout_preregistration.json"
)
RUNNER = ROOT / "tools/run_winner_v94_stable_response_readout.py"


def test_preregistration_selects_one_identifiable_parameterization() -> None:
    value = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    assert value["status"] == "PREREGISTERED_WINNER_V94_STABLE_RESPONSE_READOUT"
    readout = value["readout"]
    assert readout["feature_order"] == ["h_out[0:64]", "bias"]
    assert readout["feature_dimension"] == 65
    assert readout["mapping"] == {
        "auxiliary_action_weight": "exact zeros [14,50]",
        "auxiliary_bias": "fit row 64",
        "auxiliary_hidden_weight": "fit rows 0:64",
    }
    assert readout["full_rank_required"] == 65
    assert readout["regularization"] is None
    assert readout["hyperparameter_or_alternative_feature_search"] is False
    assert readout["flat_transport_feature_enabled"] is False


def test_preregistration_freezes_float32_stability_thresholds() -> None:
    value = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    readout = value["readout"]
    assert readout["condition_number_times_float32_epsilon_at_most"] == 1.0e-3
    assert readout["heldout_float64_vs_float32_max_abs_at_most"] == 1.0e-4
    assert value["split"]["heldout_data_used_during_fit_or_selection"] is False
    assert value["execution_now"] == {
        "least_squares_fits": 0,
        "optimizer_updates": 0,
        "robot_or_rdk_access": 0,
        "snapshot_or_onnx_writes": 0,
        "source_trace_cells": 0,
    }


def test_runner_maps_hidden_and_bias_with_zero_action_weight() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "coefficients32[:64]" in source
    assert "coefficients32[64]" in source
    assert "np.zeros((14, 50), dtype=np.float32)" in source
    assert "condition_number * float(np.finfo(np.float32).eps)" in source
    assert '"optimizer_updates": 0' in source
    assert '"robot_or_rdk_access": 0' in source
