from __future__ import annotations

import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "t59_t56_nominal_matrix_preregistration.json"
RESULT = ANALYSIS / "t59_t56_nominal_matrix_result.json"


def test_t59_preregistration_requires_both_transfer_checkpoints() -> None:
    if not PREREG.exists():
        pytest.skip("T59 has not been preregistered")
    value = json.loads(PREREG.read_text(encoding="utf-8"))
    assert value["status"] == "PREREGISTERED_T59_T56_NOMINAL_MATRIX"
    assert value["failed_checks"] == []
    assert value["matrix"]["maximum_cells"] == 16
    assert value["decision_rule"]["both_checkpoints_required"]
    assert value["decision_rule"]["no_checkpoint_selection"]
    assert value["authority"]["execute_one_cpu_nominal_matrix"]
    assert not value["authority"]["gate5"]


def test_t59_result_is_full_persistence_pass() -> None:
    if not RESULT.exists():
        pytest.skip("T59 nominal matrix has not run")
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_T59_T56_NOMINAL_MATRIX"
    assert value["decision"] == (
        "EARN_T60_T56_R2_ROBUSTNESS_MATRIX_PREREGISTRATION"
    )
    assert value["condition"]["green_cells"] == 16
    assert value["execution"]["formal_behavior_cells"] == 16
    assert value["authority"]["robustness_preregistration"]
    assert not value["authority"]["gate5"]
