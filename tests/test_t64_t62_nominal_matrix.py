from __future__ import annotations

import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "t64_t62_nominal_matrix_preregistration.json"
RESULT = ANALYSIS / "t64_t62_nominal_matrix_result.json"


def test_t64_preregistration_requires_both_transfer_checkpoints() -> None:
    if not PREREG.exists():
        pytest.skip("T64 has not been preregistered")
    value = json.loads(PREREG.read_text(encoding="utf-8"))
    assert value["status"] == "PREREGISTERED_T64_T62_NOMINAL_MATRIX"
    assert value["failed_checks"] == []
    assert value["matrix"]["maximum_cells"] == 16
    assert value["decision_rule"]["both_checkpoints_required"]
    assert value["decision_rule"]["no_checkpoint_selection"]
    assert value["authority"]["execute_one_cpu_nominal_matrix"]
    assert not value["authority"]["gate5"]


def test_t64_result_obeys_the_frozen_decision_rule() -> None:
    if not RESULT.exists():
        pytest.skip("T64 nominal matrix has not run")
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["execution"]["formal_behavior_cells"] == 16
    passed = value["condition"]["green_cells"] == 16
    if passed:
        assert value["status"] == "PASS_T64_T62_NOMINAL_MATRIX"
        assert value["decision"] == (
            "EARN_T65_T62_R2_ROBUSTNESS_MATRIX_PREREGISTRATION"
        )
        assert value["authority"]["robustness_preregistration"]
    else:
        assert value["status"] == "HOLD_T64_T62_NOMINAL_MATRIX"
        assert value["decision"] == (
            "CLOSE_T62_MIDPOINT_GAIT_TRANSFER_CURRICULUM"
        )
        assert not value["authority"]["robustness_preregistration"]
    assert not value["authority"]["gate5"]
