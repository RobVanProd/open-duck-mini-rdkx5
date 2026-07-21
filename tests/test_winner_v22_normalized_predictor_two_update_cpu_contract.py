from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "tools/build_winner_v22_normalized_predictor_two_update_cpu_contract.py"
CONTRACT = ROOT / "outputs/analysis/winner_v22_normalized_predictor_two_update_cpu_contract.json"


def load():
    spec = importlib.util.spec_from_file_location("winner_v22_two_update_contract", BUILDER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_contract_is_rederived_from_zero_update_pass() -> None:
    module = load()
    actual = json.loads(CONTRACT.read_text(encoding="utf-8"))
    assert actual == module.build_payload()


def test_contract_freezes_two_updates_and_no_broader_authority() -> None:
    value = json.loads(CONTRACT.read_text(encoding="utf-8"))
    assert value["proof"]["optimizer_updates"] == 2
    assert value["proof"]["frozen_predictor_scale"] == 380.9135437011719
    assert value["execution_now"]["optimizer_updates"] == 0
    assert not value["single_change"]["flat_transport_equation_used"]
    assert not value["authority"]["winner_v22_training_authorized"]
    assert not value["authority"]["robot_clearance"]
