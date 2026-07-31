from __future__ import annotations

import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "t77_endpoint_joint_adapter_cpu_preregistration.json"
RESULT = ANALYSIS / "t77_endpoint_joint_adapter_cpu_result.json"


def test_t77_preregistration_freezes_base_contract() -> None:
    if not PREREG.exists():
        pytest.skip("T77 has not been preregistered")
    value = json.loads(PREREG.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PREREGISTERED_T77_ENDPOINT_JOINT_ADAPTER_CPU_CONTRACT"
    )
    assert value["failed_checks"] == []
    assert value["mechanism"]["hosted_per_category"] == 32
    assert len(value["mechanism"]["endpoint_categories"]) == 8
    assert value["mechanism"]["trainable_actor_groups"] == [
        "adapter_obs_projection",
        "adapter_hidden_projection",
        "adapter_hidden_bias",
        "adapter_location",
    ]
    assert value["mechanism"]["frozen_actor_groups"] == [
        "residual_trunk",
        "residual_location",
        "scale_logits",
    ]
    assert value["mechanism"]["normalizer_frozen"]
    assert not value["mechanism"]["reward_change"]
    assert not value["mechanism"]["policy_abi_change"]
    assert not value["mechanism"]["runtime_change"]
    assert not value["authority"]["hosted_training"]
    assert not value["authority"]["gate5"]


def test_t77_result_obeys_frozen_decision_rule() -> None:
    if not RESULT.exists():
        pytest.skip("T77 CPU contract has not run")
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    passed = not value["failed_checks"]
    if passed:
        assert value["status"] == (
            "PASS_T77_ENDPOINT_JOINT_ADAPTER_CPU_CONTRACT"
        )
        assert value["decision"] == (
            "EARN_T78_ENDPOINT_JOINT_ADAPTER_HOSTED_PREREGISTRATION_ONLY"
        )
        assert value["authority"]["hosted_preregistration"]
    else:
        assert value["status"] == (
            "HOLD_T77_ENDPOINT_JOINT_ADAPTER_CPU_CONTRACT"
        )
        assert value["decision"] == (
            "CLOSE_T77_ENDPOINT_JOINT_ADAPTER_CONTINUATION"
        )
        assert not value["authority"]["hosted_preregistration"]
    assert value["execution"]["formal_behavior_cells"] == 0
    assert value["execution"]["hosted_compute_units"] == 0
    assert not value["authority"]["hosted_training"]
    assert not value["authority"]["gate5"]
