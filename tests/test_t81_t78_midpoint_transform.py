from __future__ import annotations

import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "t81_t78_midpoint_preregistration.json"
RESULT = ANALYSIS / "t81_t78_midpoint_result.json"


def test_t81_preregistration_is_exact_and_diagnostic_only() -> None:
    if not PREREG.exists():
        pytest.skip("T81 has not been preregistered")
    value = json.loads(PREREG.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PREREGISTERED_T81_T78_EXACT_ADAPTER_MIDPOINT"
    )
    assert value["failed_checks"] == []
    assert value["transform"]["coefficient"] == 0.5
    assert value["transform"]["coefficient_sweep"] is False
    assert len(value["transform"]["initializers"]) == 5
    assert value["decision_rule"]["candidate_promotion"] is False
    assert not value["authority"]["behavior_execution"]
    assert not value["authority"]["gate5"]


def test_t81_result_obeys_frozen_decision_rule() -> None:
    if not RESULT.exists():
        pytest.skip("T81 has not run")
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    passed = not value["failed_checks"]
    if passed:
        assert value["status"] == (
            "PASS_T81_T78_EXACT_ADAPTER_MIDPOINT"
        )
        assert value["decision"] == (
            "EARN_T82_TWO_CELL_MIDPOINT_CROSSOVER_PREREGISTRATION_ONLY"
        )
        assert value["authority"]["two_cell_behavior_preregistration"]
    else:
        assert value["status"] == (
            "HOLD_T81_T78_EXACT_ADAPTER_MIDPOINT"
        )
        assert value["decision"] == "CLOSE_EXACT_T78_ADAPTER_MIDPOINT"
    assert value["execution"]["formal_behavior_cells"] == 0
    assert not value["authority"]["candidate_promotion"]
    assert not value["authority"]["gate5"]
