from __future__ import annotations

import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def load(name: str) -> dict:
    return json.loads((ANALYSIS / name).read_text(encoding="utf-8"))


def test_t36_freezes_the_complete_six_variant_factorial() -> None:
    payload = load("t36_t32_actor_block_factorial_preregistration.json")
    assert (
        payload["status"]
        == "PREREGISTERED_T36_T32_ACTOR_BLOCK_FACTORIAL"
    )
    assert payload["failed_checks"] == []
    assert payload["execution_order"] == [
        "NORMALIZER_HALF",
        "BASE_HALF",
        "ADAPTER_HALF",
        "NORMALIZER_BASE_HALF",
        "NORMALIZER_ADAPTER_HALF",
        "BASE_ADAPTER_HALF",
    ]
    assert len(payload["variants"]) == 6
    assert all(item["pass"] for item in payload["variants"])
    assert payload["cell"]["fit_id"] == "p31_34"
    assert payload["cell"]["command_x_m_s"] == 0.077
    assert payload["cell"]["seed"] == 167931544
    assert payload["decision_rule"]["run_all_six"]
    assert payload["decision_rule"]["no_early_stop"]
    assert payload["decision_rule"][
        "no_policy_promotion_or_checkpoint_selection"
    ]
    assert payload["authority"]["execute_six_cpu_cells"]
    assert not payload["authority"]["training"]
    assert not payload["authority"]["colab"]
    assert not payload["authority"]["gate5"]
    assert not payload["authority"]["rdkx5_or_robot"]


def test_t36_result_never_promotes_a_hybrid_policy() -> None:
    path = ANALYSIS / "t36_t32_actor_block_factorial_result.json"
    if not path.is_file():
        pytest.skip("formal T36 result has not run")
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["status"] in {
        "PASS_T36_T32_ACTOR_BLOCK_FACTORIAL_NO_REPAIR",
        "PASS_T36_T32_ACTOR_BLOCK_FACTORIAL_WITH_REPAIR",
    }
    assert payload["summary"]["formal_behavior_cells"] == 6
    assert payload["summary"]["valid_cells"] == 6
    assert not payload["authority"]["policy_promotion"]
    assert not payload["authority"]["checkpoint_selection"]
    assert not payload["authority"]["training"]
    assert not payload["authority"]["colab"]
    assert not payload["authority"]["gate5"]
    assert not payload["authority"]["rdkx5_or_robot"]
    assert not payload["authority"]["torque_or_motion"]
