from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ATTRIBUTION = ROOT / "outputs/analysis/winner_v20_joint_recurrent_support_attribution.json"


def test_evidence_selects_joint_recurrent_existing_abi_repair() -> None:
    value = json.loads(ATTRIBUTION.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_WINNER_V20_JOINT_RECURRENT_SUPPORT_ATTRIBUTION"
    assert value["decision"] == "PREREGISTER_ONE_JOINT_RECURRENT_PPO_CPU_CONTRACT"
    assert value["causal_chain"]["v15_persistent_failures_half_final"] == [12, 12]
    assert value["causal_chain"]["v15_recurrent_encoder_bit_exact_frozen"] is True
    selected = value["selected_mechanism"]
    assert selected["new_parameters"] == 0
    assert selected["onnx_abi_change"] is False
    assert selected["post_policy_wrapper"] is False
    assert selected["reward_change_from_v15"] is False
    assert selected["population_seed_budget_change_from_v15"] is False
    assert set(selected["bit_exact_frozen_leaves"]) == {
        "auxiliary_hidden_weight",
        "auxiliary_action_weight",
        "auxiliary_bias",
    }


def test_attribution_does_not_authorize_training_or_robot() -> None:
    value = json.loads(ATTRIBUTION.read_text(encoding="utf-8"))
    assert value["flat_transport_kernel"]["selected"] is False
    assert value["required_cpu_contract"]["optimizer_updates"] == 1
    assert value["execution"] == {
        "optimizer_updates": 0,
        "formal_support_cells": 0,
        "locomotion_steps": 0,
        "robot_or_rdk_access": 0,
    }
    assert value["authority"]["joint_recurrent_training_authorized"] is False
    assert value["authority"]["robot_clearance"] is False
