from __future__ import annotations

import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def load(name: str) -> dict:
    return json.loads((ANALYSIS / name).read_text(encoding="utf-8"))


def test_t43_preregisters_exact_three_cell_factorial() -> None:
    value = load("t43_forward_actor_block_factorial_preregistration.json")
    assert value["status"] == (
        "PREREGISTERED_T43_FORWARD_ACTOR_BLOCK_FACTORIAL"
    )
    assert value["failed_checks"] == []
    assert value["execution_order"] == [
        "HALF_WITH_FINAL_BASE",
        "HALF_WITH_FINAL_ADAPTER",
        "HALF_WITH_FINAL_BASE_ADAPTER",
    ]
    assert value["cell"]["condition"]["id"] == "JOINT_FRICTIONLOSS_LO"
    assert value["cell"]["fit_id"] == "p30"
    assert value["cell"]["command_x_m_s"] == 0.08
    assert value["decision_rule"]["run_all_three"]
    assert value["decision_rule"]["no_early_stop"]
    assert value["decision_rule"]["no_policy_promotion"]
    assert value["decision_rule"]["no_checkpoint_selection"]
    assert value["execution_now"]["formal_behavior_cells"] == 0
    assert value["authority"]["execute_three_cpu_cells"]
    assert not value["authority"]["uniform_transform_preregistration"]
    assert not value["authority"]["gate5"]
    assert not value["authority"]["rdkx5_or_robot"]


def test_t43_combined_variant_is_endpoint_duplicate() -> None:
    value = load("t43_forward_actor_block_factorial_preregistration.json")
    variants = {item["variant_id"]: item for item in value["variants"]}
    assert not variants["HALF_WITH_FINAL_BASE"][
        "semantically_equals_final_endpoint"
    ]
    assert not variants["HALF_WITH_FINAL_ADAPTER"][
        "semantically_equals_final_endpoint"
    ]
    assert variants["HALF_WITH_FINAL_BASE_ADAPTER"][
        "semantically_equals_final_endpoint"
    ]
    assert all(item["pass"] for item in variants.values())


def test_t43_result_has_three_valid_cells_if_present() -> None:
    path = ANALYSIS / "t43_forward_actor_block_factorial_result.json"
    if not path.is_file():
        pytest.skip("formal T43 factorial has not run")
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["summary"]["formal_behavior_cells"] == 3
    assert value["summary"]["valid_cells"] == 3
    assert len(value["cells"]) == 3
    if value["summary"]["one_group_passing_variants"]:
        assert value["status"] == (
            "PASS_T43_FORWARD_ACTOR_BLOCK_ONE_BLOCK_CAUSE"
        )
        assert value["authority"]["uniform_transform_preregistration"]
    else:
        assert not value["authority"]["uniform_transform_preregistration"]
    assert not value["authority"]["policy_promotion"]
    assert not value["authority"]["gate5"]
    assert not value["authority"]["rdkx5_or_robot"]
