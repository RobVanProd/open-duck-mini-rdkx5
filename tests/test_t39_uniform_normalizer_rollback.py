from __future__ import annotations

import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def load(name: str) -> dict:
    return json.loads((ANALYSIS / name).read_text(encoding="utf-8"))


def test_t39_preregisters_one_uniform_zero_credit_transform() -> None:
    value = load(
        "t39_uniform_normalizer_rollback_nominal_preregistration.json"
    )
    assert value["status"] == (
        "PREREGISTERED_T39_UNIFORM_NORMALIZER_ROLLBACK_NOMINAL_MATRIX"
    )
    assert value["failed_checks"] == []
    assert value["mechanism"]["uniform_across_checkpoints"]
    assert value["mechanism"]["changed_initializer_names"] == [
        "obs_mean",
        "obs_std",
    ]
    assert value["mechanism"]["half_effect"] == "bit_exact_identity"
    assert value["mechanism"]["training_steps"] == 0
    assert value["mechanism"]["hosted_compute_units"] == 0
    assert not value["mechanism"]["checkpoint_selection"]
    assert value["matrix"]["maximum_cells"] == 16
    assert value["decision_rule"]["both_checkpoints_required"]
    assert value["decision_rule"]["no_result_dependent_transform"]
    assert value["decision_rule"]["no_retry"]
    assert value["authority"]["execute_one_cpu_nominal_matrix"]
    assert not value["authority"]["gate5"]
    assert not value["authority"]["rdkx5_or_robot"]


def test_t39_asset_contract_changes_only_final_normalizer_values() -> None:
    value = load(
        "t39_uniform_normalizer_rollback_nominal_preregistration.json"
    )
    contract = value["asset_contract"]
    assert contract["final_pre_margin_changed_initializers"] == [
        "obs_mean",
        "obs_std",
    ]
    assert contract["final_policy_changed_initializers"] == [
        "obs_mean",
        "obs_std",
    ]
    assert value["checks"]["half_target_is_source_bit_exact"]
    assert value["checks"]["final_pre_margin_topology_exact"]
    assert value["checks"]["final_policy_topology_exact"]
    assert value["checks"]["half_policy_normalizer_is_half_exact"]
    assert value["checks"]["final_policy_normalizer_is_half_exact"]


def test_t39_result_requires_all_sixteen_cells_if_present() -> None:
    path = ANALYSIS / "t39_uniform_normalizer_rollback_nominal_result.json"
    if not path.is_file():
        pytest.skip("formal T39 result has not run")
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["execution"]["formal_behavior_cells"] == 16
    assert value["execution"]["training_steps"] == 0
    assert value["execution"]["hosted_compute_units"] == 0
    if value["status"].startswith("PASS_"):
        assert value["condition"]["green_cells"] == 16
        assert value["condition"]["condition_green"]
        assert value["authority"]["robustness_preregistration"]
    else:
        assert value["condition"]["green_cells"] < 16
        assert not value["authority"]["robustness_preregistration"]
    assert not value["authority"]["robustness_execution"]
    assert not value["authority"]["gate5"]
    assert not value["authority"]["rdkx5_or_robot"]
