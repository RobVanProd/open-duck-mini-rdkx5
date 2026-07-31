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


def test_t34_result_records_the_frozen_15_of_16_hold() -> None:
    path = ANALYSIS / "t34_t32_nominal_matrix_result.json"
    if not path.is_file():
        pytest.skip("formal T34 result has not run")
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == "HOLD_T34_T32_NOMINAL_MATRIX"
    assert value["condition"]["green_cells"] == 15
    assert not value["condition"]["condition_green"]
    assert value["execution"]["formal_behavior_cells"] == 16
    assert value["decision"] == "CLOSE_T32_ACTION_MARGIN_TRAINTHROUGH"
    failed = [
        (block, cell)
        for block in value["blocks"]
        for cell in block["result"]["cells"]
        if not cell["cell_green"]
    ]
    assert len(failed) == 1
    block, cell = failed[0]
    assert block["checkpoint_id"] == "T32_MARGIN_FINAL"
    assert block["fit_id"] == "p31_34"
    assert cell["command_x_m_s"] == 0.077
    assert cell["behavior"]["termination_reason"] == "fall_or_nan"
    assert cell["behavior"]["samples"] == 494
    assert cell["behavior"]["replacement_quality_pass"]
    assert not cell["behavior"]["emergence_pass"]
    assert cell["protection"]["duration_protection_pass"]
    assert not value["authority"]["robustness_preregistration"]
    assert not value["authority"]["robustness_execution"]
    assert not value["authority"]["gate5"]
    assert not value["authority"]["rdkx5_or_robot"]
