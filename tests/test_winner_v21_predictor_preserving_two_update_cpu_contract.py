from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "outputs/analysis/winner_v21_predictor_preserving_two_update_cpu_contract.json"


def test_two_update_contract_is_frozen_and_has_no_training_authority() -> None:
    value = json.loads(CONTRACT.read_text(encoding="utf-8"))
    assert value["status"] == (
        "FROZEN_WINNER_V21_PREDICTOR_PRESERVING_TWO_UPDATE_CPU_CONTRACT"
    )
    assert value["decision"] == "AUTHORIZE_EXACT_TWO_UPDATE_EXPLICIT_GRADIENT_PROOF_ONLY"
    assert value["execution_now"] == {
        "optimizer_updates": 0,
        "formal_support_cells": 0,
        "locomotion_steps": 0,
        "robot_or_rdk_access": 0,
    }
    assert value["proof"]["optimizer_updates"] == 2
    assert value["proof"]["predictor_scale_evaluations"] == 0
    assert value["single_change"]["flat_transport_equation_used"] is False
    assert value["authority"]["winner_v21_training_authorized"] is False
    assert value["authority"]["robot_clearance"] is False


def test_contract_freezes_all_sources_by_lf_hash() -> None:
    value = json.loads(CONTRACT.read_text(encoding="utf-8"))
    assert len(value["sources"]) >= 15
    assert all(item["hash_mode"] == "lf" for item in value["sources"].values())
    assert len(value["source_manifest_sha256"]) == 64
