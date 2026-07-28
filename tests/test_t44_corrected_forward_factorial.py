from __future__ import annotations

import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def load(name: str) -> dict:
    return json.loads((ANALYSIS / name).read_text(encoding="utf-8"))


def test_t44_preregistration_corrects_only_worker_command() -> None:
    value = load("t44_corrected_forward_factorial_preregistration.json")
    assert value["status"] == (
        "PREREGISTERED_T44_CORRECTED_FORWARD_ACTOR_FACTORIAL"
    )
    assert value["failed_checks"] == []
    assert value["correction"]["only_change"] == (
        "formal_worker_command_x0p077_to_x0p080"
    )
    assert value["correction"]["t43_policy_assets_reused_exact"]
    assert not value["correction"]["t43_policy_outcomes_reused"]
    assert value["cell"]["command_x_m_s"] == 0.08
    assert len(value["variants"]) == 3
    assert value["decision_rule"]["run_all_three"]
    assert value["decision_rule"]["no_early_stop"]
    assert value["decision_rule"]["no_retry"]
    assert value["authority"]["execute_three_cpu_cells"]
    assert not value["authority"]["gate5"]
    assert not value["authority"]["rdkx5_or_robot"]


def test_t44_result_has_three_valid_cells_if_present() -> None:
    path = ANALYSIS / "t44_corrected_forward_factorial_result.json"
    if not path.is_file():
        pytest.skip("formal T44 factorial has not run")
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["summary"]["formal_behavior_cells"] == 3
    assert value["summary"]["valid_cells"] == 3
    assert len(value["cells"]) == 3
    if value["summary"]["one_group_passing_variants"]:
        assert value["status"] == (
            "PASS_T44_CORRECTED_FORWARD_ONE_BLOCK_CAUSE"
        )
        assert value["authority"]["uniform_transform_preregistration"]
    else:
        assert not value["authority"]["uniform_transform_preregistration"]
    assert not value["authority"]["policy_promotion"]
    assert not value["authority"]["gate5"]
    assert not value["authority"]["rdkx5_or_robot"]
