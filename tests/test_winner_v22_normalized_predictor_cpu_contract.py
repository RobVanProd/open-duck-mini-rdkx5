from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "tools/build_winner_v22_normalized_predictor_cpu_contract.py"
CONTRACT = ROOT / "outputs/analysis/winner_v22_normalized_predictor_cpu_contract.json"


def load():
    spec = importlib.util.spec_from_file_location("winner_v22_cpu_contract", BUILDER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_contract_is_rederived_from_attribution_and_sources() -> None:
    module = load()
    actual = json.loads(CONTRACT.read_text(encoding="utf-8"))
    assert actual == module.build_payload()
    assert actual["status"] == "FROZEN_WINNER_V22_NORMALIZED_PREDICTOR_CPU_CONTRACT"


def test_contract_freezes_only_one_zero_update_proof() -> None:
    value = json.loads(CONTRACT.read_text(encoding="utf-8"))
    assert value["execution_now"]["optimizer_updates"] == 0
    assert value["frozen_cpu_proof"]["predictor_scale_evaluations"] == 1
    assert not value["frozen_cpu_proof"]["scale_sweep"]
    assert not value["single_correction"]["flat_transport_equation_used"]
    assert not value["authority"]["winner_v22_training_authorized"]
    assert not value["authority"]["robot_clearance"]
