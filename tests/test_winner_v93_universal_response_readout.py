from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PREREGISTRATION = (
    ROOT / "outputs/analysis/winner_v93_universal_response_readout_preregistration.json"
)
RUNNER = ROOT / "tools/run_winner_v93_universal_response_readout.py"


def test_preregistration_freezes_fit_and_heldout_populations() -> None:
    value = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    assert value["status"] == "PREREGISTERED_WINNER_V93_UNIVERSAL_RESPONSE_READOUT"
    assert value["source"]["observer_label"] == "winner_v22_final"
    assert value["source"]["universal_target"]["candidate_index"] == 536
    assert value["split"] == {
        "actuator_plants": 2,
        "fit_configuration_groups": ["fixed_anchors", "discovery_samples"],
        "fit_configurations": 40,
        "fit_transitions": 19920,
        "heldout_configuration_group": "heldout_samples",
        "heldout_configurations": 16,
        "heldout_data_used_during_fit_or_selection": False,
        "heldout_transitions": 7968,
        "ticks_per_cell": 250,
    }


def test_readout_has_one_search_free_architecture_exact_fit() -> None:
    value = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    readout = value["readout"]
    assert readout["feature_order"] == [
        "h_out[0:64]",
        "realized_action[0:14]",
        "bias",
    ]
    assert readout["feature_dimension"] == 79
    assert readout["target_dimension"] == 50
    assert readout["solver"] == "numpy.linalg.lstsq float64 rcond=None minimum-norm"
    assert readout["stored_coefficient_dtype"] == "float32"
    assert readout["regularization"] is None
    assert readout["hyperparameter_or_feature_search"] is False
    assert readout["recurrent_parameters_changed"] is False
    assert readout["policy_action_parameters_changed"] is False
    assert readout["flat_transport_feature_enabled"] is False


def test_runner_cannot_train_or_touch_hardware() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "np.linalg.lstsq" in source
    assert '"least_squares_fits": 1' in source
    assert '"optimizer_updates": 0' in source
    assert '"snapshot_or_onnx_writes": 0' in source
    assert '"robot_or_rdk_access": 0' in source
    assert "hardware-authorized" not in source
