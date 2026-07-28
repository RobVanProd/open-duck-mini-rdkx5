from __future__ import annotations

import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = (
    ANALYSIS / "t65_t62_midpoint_endpoint_screen_preregistration.json"
)
RESULT = ANALYSIS / "t65_t62_midpoint_endpoint_screen_result.json"


def test_t65_preregistration_is_diagnostic_only() -> None:
    if not PREREG.exists():
        pytest.skip("T65 has not been preregistered")
    value = json.loads(PREREG.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PREREGISTERED_T65_T62_MIDPOINT_ENDPOINT_SCREEN"
    )
    assert value["failed_checks"] == []
    assert value["matrix"]["maximum_cells"] == 8
    assert value["matrix"]["diagnostic_only"]
    assert value["decision_rule"]["no_checkpoint_selection"]
    assert value["decision_rule"]["no_policy_promotion"]
    assert value["decision_rule"]["no_hosted_training_authorization"]
    assert not value["authority"]["policy_promotion"]
    assert not value["authority"]["gate5"]


def test_t65_result_obeys_frozen_decision_rule() -> None:
    if not RESULT.exists():
        pytest.skip("T65 endpoint screen has not run")
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["execution"]["formal_behavior_cells"] == 8
    passed = value["condition"]["green_cells"] == 8
    if passed:
        assert value["status"] == (
            "PASS_T65_T62_MIDPOINT_ENDPOINT_SCREEN"
        )
        assert value["decision"] == (
            "EARN_T66_FIXED_MIDPOINT_PERSISTENCE_CPU_CONTRACT_"
            "PREREGISTRATION_ONLY"
        )
        assert value["authority"]["t66_cpu_contract_preregistration"]
    else:
        assert value["status"] == (
            "HOLD_T65_T62_MIDPOINT_ENDPOINT_SCREEN"
        )
        assert value["decision"] == (
            "CLOSE_BALANCE_FIRST_REWARD_HOMOTOPY_FAMILY"
        )
        assert not value["authority"]["t66_cpu_contract_preregistration"]
    assert not value["authority"]["training"]
    assert not value["authority"]["policy_promotion"]
    assert not value["authority"]["gate5"]
