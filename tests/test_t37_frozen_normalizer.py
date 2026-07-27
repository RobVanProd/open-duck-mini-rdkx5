from __future__ import annotations

import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def load(name: str) -> dict:
    return json.loads((ANALYSIS / name).read_text(encoding="utf-8"))


def test_t37_preregisters_exact_default_off_normalizer_freeze() -> None:
    payload = load("t37_frozen_normalizer_cpu_preregistration.json")
    assert (
        payload["status"]
        == "PREREGISTERED_T37_FROZEN_NORMALIZER_CPU_SMOKE"
    )
    assert payload["failed_checks"] == []
    assert payload["normalizer_contract"]["source_count"] == 16056320
    assert payload["normalizer_contract"]["mode"] == "welford"
    assert payload["normalizer_contract"]["normalization_enabled"]
    assert payload["normalizer_contract"]["freeze_mechanism"] == (
        "temporary_identity_update_context"
    )
    assert payload["normalizer_contract"]["policy_and_critic_trainable"]
    assert payload["transition"]["default_off"]
    assert payload["transition"]["environment_changes"] == 0
    assert payload["transition"]["reward_changes"] == 0
    assert payload["transition"]["deployment_graph_changes"] == 0
    assert payload["authority"]["execute_1024_cpu_steps"]
    assert not payload["authority"]["hosted_training"]
    assert not payload["authority"]["behavior_evaluation"]
    assert not payload["authority"]["gate5"]
    assert not payload["authority"]["rdkx5_or_robot"]


def test_t37_result_requires_exact_frozen_normalizer_tree() -> None:
    path = ANALYSIS / "t37_frozen_normalizer_cpu_result.json"
    if not path.is_file():
        pytest.skip("formal T37 CPU result has not run")
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["status"] == "PASS_T37_FROZEN_NORMALIZER_CPU_SMOKE"
    assert payload["decision"] == (
        "EARN_T38_FROZEN_NORMALIZER_HOSTED_PREREGISTRATION"
    )
    assert payload["failed_checks"] == []
    contract = payload["normalizer_contract"]
    assert contract["expected_count"] == 16056320
    assert contract["initial_count"] == contract["expected_count"]
    assert contract["final_count"] == contract["expected_count"]
    assert contract["all_leaves_bit_exact_after_update"]
    assert contract["expected_source"] == contract["initial"]
    assert contract["initial"] == contract["final"]
    assert payload["checks"]["every_policy_leaf_updated"]
    assert payload["checks"]["every_critic_leaf_updated"]
    assert payload["checks"]["both_margin_export_contracts_pass"]
    assert not payload["authority"]["hosted_training"]
    assert not payload["authority"]["behavior_evaluation"]
    assert not payload["authority"]["gate5"]
    assert not payload["authority"]["rdkx5_or_robot"]
