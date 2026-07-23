from __future__ import annotations

import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
PREREGISTRATION = (
    ROOT / "outputs/analysis/winner_v95_precision_truncated_readout_preregistration.json"
)
RUNNER = ROOT / "tools/run_winner_v95_precision_truncated_readout.py"


def test_preregistration_derives_cutoff_only_from_precision_bound() -> None:
    value = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    assert value["status"] == "PREREGISTERED_WINNER_V95_PRECISION_TRUNCATED_READOUT"
    readout = value["readout"]
    epsilon = float(np.finfo(np.float32).eps)
    assert readout["float32_epsilon"] == epsilon
    assert readout["condition_limit"] == 1.0e-3 / epsilon
    assert readout["relative_singular_value_cutoff"] == epsilon / 1.0e-3
    assert readout["hyperparameter_rank_or_feature_search"] is False
    assert readout["regularization"] is None
    assert readout["flat_transport_feature_enabled"] is False


def test_preregistration_keeps_source_split_and_mapping_frozen() -> None:
    value = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    assert value["source"]["universal_target_candidate"] == 536
    assert value["split"] == {
        "actuator_plants": 2,
        "fit_configurations": 40,
        "fit_transitions": 19920,
        "heldout_configurations": 16,
        "heldout_data_used_during_fit_or_rank_selection": False,
        "heldout_transitions": 7968,
        "ticks_per_cell": 250,
    }
    assert value["readout"]["mapping"]["auxiliary_action_weight"] == (
        "exact zeros [14,50]"
    )


def test_runner_uses_one_explicit_svd_without_optimizer_or_hardware() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "np.linalg.svd(design, full_matrices=False)" in source
    assert "builder.RELATIVE_SINGULAR_VALUE_CUTOFF" in source
    assert '"svd_fits": 1' in source
    assert '"optimizer_updates": 0' in source
    assert '"snapshot_or_onnx_writes": 0' in source
    assert '"robot_or_rdk_access": 0' in source
