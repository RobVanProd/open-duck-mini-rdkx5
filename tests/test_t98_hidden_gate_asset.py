from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from tools import build_t98_hidden_gate_asset as t98


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t97_passing_result_is_the_only_asset_authority() -> None:
    value = t98.validate_t97_result()
    assert value["status"] == "PASS_T97_HIDDEN_GATE_FALSIFIER"
    assert value["authority"]["training"] is False
    assert value["authority"]["t98_cpu_contract_preregistration"] is True


def test_full_population_gate_is_strictly_separated() -> None:
    prereg, rows = t98.source_population()
    model = t98.t97.fit_ridge(rows)
    predicted = t98.t97.predict(model, rows)
    assert len(rows) == prereg["population"]["sample_count"] == 72
    assert t98.t97.metrics(predicted)["balanced_accuracy"] == 1.0
    assert min(row["score"] for row in predicted if row["label"] == 1) > 0.0
    assert max(row["score"] for row in predicted if row["label"] == -1) < 0.0
    assert model["mean"].shape == (64,)
    assert model["scale"].shape == (64,)
    assert model["weights"].shape == (65,)
    assert all(np.all(np.isfinite(value)) for value in model.values())


def test_frozen_asset_contract_when_present() -> None:
    path = ANALYSIS / "t98_hidden_gate_asset.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    basis = {key: item for key, item in value.items() if key != "asset_sha256"}
    assert value["asset_sha256"] == t98.canonical_sha256(basis)
    assert value["status"] == "FROZEN_T98_HIDDEN_GATE_ASSET"
    assert value["failed_checks"] == []
    assert value["constraints"] == {
        "fixed_not_trainable": True,
        "manual_measurement": False,
        "new_policy_input": False,
        "new_runtime_sensor": False,
        "policy_abi_change": False,
        "scalar_sweep": False,
    }
