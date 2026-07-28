from __future__ import annotations

import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def load(name: str) -> dict:
    return json.loads((ANALYSIS / name).read_text(encoding="utf-8"))


def test_t52_preregisters_distinct_uniform_half_head_endpoints() -> None:
    value = load(
        "t52_uniform_half_head_qualification_preregistration.json"
    )
    assert value["status"] == (
        "PREREGISTERED_T52_UNIFORM_HALF_HEAD_QUALIFICATION"
    )
    assert value["failed_checks"] == []
    mechanism = value["mechanism"]
    assert mechanism["half_changed_initializers"] == []
    assert mechanism["final_changed_initializers"] == [
        "adapter_bias",
        "adapter_weight",
    ]
    assert mechanism["endpoint_differing_initializers"] == [
        "adapter_hidden_bias",
        "adapter_hidden_weight",
        "adapter_obs_weight",
    ]
    assert mechanism["checkpoint_endpoints_distinct"]
    assert mechanism["training_steps"] == 0
    assert value["matrix"]["maximum_cells"] == 64
    assert value["matrix"]["condition_two_is_nominal_matrix"]
    assert value["matrix"]["both_checkpoints_required"]
    assert not value["matrix"]["checkpoint_cherry_pick"]
    assert value["decision_rule"]["no_additional_adapter_variant"]
    assert value["authority"]["execute_one_64_cell_cpu_qualification"]
    assert not value["authority"]["gate5"]


def test_t52_result_requires_all_64_cells_if_present() -> None:
    path = ANALYSIS / "t52_uniform_half_head_qualification_result.json"
    if not path.is_file():
        pytest.skip("formal T52 qualification has not run")
    value = json.loads(path.read_text(encoding="utf-8"))
    summary = value["summary"]
    assert summary["completed_cells"] == (
        16 * summary["completed_conditions"]
    )
    if value["status"].startswith("PASS_"):
        assert summary["completed_conditions"] == 4
        assert summary["completed_cells"] == 64
        assert summary["green_cells"] == 64
        assert value["authority"]["later_robustness_preregistration"]
    else:
        assert summary["green_cells"] < summary["completed_cells"]
        assert not value["authority"]["later_robustness_preregistration"]
    assert not value["authority"]["policy_promotion"]
    assert not value["authority"]["gate5"]
