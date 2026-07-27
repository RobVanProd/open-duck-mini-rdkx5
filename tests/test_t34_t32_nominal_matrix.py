from __future__ import annotations

import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def load(name: str) -> dict:
    return json.loads((ANALYSIS / name).read_text(encoding="utf-8"))


def test_t34_preregistration_freezes_exactly_16_cpu_cells() -> None:
    value = load("t34_t32_nominal_matrix_preregistration.json")
    assert value["status"] == "PREREGISTERED_T34_T32_NOMINAL_MATRIX"
    assert value["failed_checks"] == []
    assert value["matrix"]["maximum_cells"] == 16
    assert value["matrix"]["checkpoints"] == 2
    assert value["matrix"]["fits"] == 2
    assert value["matrix"]["commands"] == 4
    assert value["decision_rule"]["both_checkpoints_required"]
    assert value["decision_rule"]["no_checkpoint_selection"]
    assert value["authority"]["execute_one_cpu_nominal_matrix"]
    assert not value["authority"]["gate5"]
    assert not value["authority"]["rdkx5_or_robot"]


def test_t34_result_requires_all_16_cells() -> None:
    path = ANALYSIS / "t34_t32_nominal_matrix_result.json"
    if not path.is_file():
        pytest.skip("formal T34 result has not run")
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_T34_T32_NOMINAL_MATRIX"
    assert value["condition"]["green_cells"] == 16
    assert value["condition"]["condition_green"]
    assert value["execution"]["formal_behavior_cells"] == 16
    assert value["decision"] == (
        "EARN_T32_R2_ROBUSTNESS_MATRIX_PREREGISTRATION"
    )
    assert value["authority"]["robustness_preregistration"]
    assert not value["authority"]["robustness_execution"]
    assert not value["authority"]["gate5"]
    assert not value["authority"]["rdkx5_or_robot"]
