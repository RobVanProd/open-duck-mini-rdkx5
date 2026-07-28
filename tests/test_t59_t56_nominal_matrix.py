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


def test_t59_result_records_the_frozen_persistence_hold() -> None:
    if not RESULT.exists():
        pytest.skip("T59 nominal matrix has not run")
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["status"] == "HOLD_T59_T56_NOMINAL_MATRIX"
    assert value["decision"] == "CLOSE_T56_DYNAMIC_SINGLE_SUPPORT_CURRICULUM"
    assert value["condition"]["green_cells"] == 10
    assert value["execution"]["formal_behavior_cells"] == 16
    blocks = {
        (block["checkpoint_id"], block["fit_id"]): block["result"][
            "block_green"
        ]
        for block in value["blocks"]
    }
    assert blocks == {
        ("T56_TRANSFER_HALF", "p30"): False,
        ("T56_TRANSFER_HALF", "p31_34"): False,
        ("T56_TRANSFER_FINAL", "p30"): True,
        ("T56_TRANSFER_FINAL", "p31_34"): True,
    }
    assert not value["authority"]["robustness_preregistration"]
    assert not value["authority"]["gate5"]
