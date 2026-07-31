from __future__ import annotations

import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "t66_endpoint_core_cpu_preregistration.json"
RESULT = ANALYSIS / "t66_endpoint_core_cpu_result.json"


def test_t66_preregistration_freezes_noncore_contract() -> None:
    if not PREREG.exists():
        pytest.skip("T66 has not been preregistered")
    value = json.loads(PREREG.read_text(encoding="utf-8"))
    assert value["status"] == "PREREGISTERED_T66_ENDPOINT_CORE_CPU_CONTRACT"
    assert value["failed_checks"] == []
    assert value["mechanism"]["hosted_per_category"] == 32
    assert len(value["mechanism"]["endpoint_categories"]) == 8
    assert value["mechanism"]["normalizer_frozen"]
    assert not value["mechanism"]["reward_change"]
    assert not value["mechanism"]["policy_abi_change"]
    assert not value["authority"]["hosted_training"]
    assert not value["authority"]["gate5"]


def test_t66_result_obeys_frozen_decision_rule() -> None:
    if not RESULT.exists():
        pytest.skip("T66 CPU contract has not run")
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    passed = not value["failed_checks"]
    if passed:
        assert value["status"] == "PASS_T66_ENDPOINT_CORE_CPU_CONTRACT"
        assert value["decision"] == (
            "EARN_T67_ENDPOINT_CORE_HOSTED_PREREGISTRATION_ONLY"
        )
        assert value["authority"]["hosted_preregistration"]
    else:
        assert value["status"] == "HOLD_T66_ENDPOINT_CORE_CPU_CONTRACT"
        assert value["decision"] == "CLOSE_T66_ENDPOINT_CORE_CONTINUATION"
        assert not value["authority"]["hosted_preregistration"]
    assert value["execution"]["formal_behavior_cells"] == 0
    assert value["execution"]["hosted_compute_units"] == 0
    assert not value["authority"]["hosted_training"]
    assert not value["authority"]["gate5"]
