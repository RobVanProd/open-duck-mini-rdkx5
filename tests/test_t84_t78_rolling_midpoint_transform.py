from __future__ import annotations

import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "t84_t78_rolling_midpoint_preregistration.json"
RESULT = ANALYSIS / "t84_t78_rolling_midpoint_result.json"


def test_t84_preregistration_freezes_uniform_persistent_rule() -> None:
    if not PREREG.exists():
        pytest.skip("T84 has not been preregistered")
    value = json.loads(PREREG.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PREREGISTERED_T84_T78_ROLLING_ADAPTER_MIDPOINTS"
    )
    assert value["failed_checks"] == []
    assert value["transform"]["coefficient"] == 0.5
    assert value["transform"]["coefficient_sweep"] is False
    assert value["transform"]["uniform_rule_at_both_exports"] is True
    assert value["persistence_contract"]["both_required"] is True
    assert value["persistence_contract"]["no_checkpoint_selection"] is True


def test_t84_result_obeys_frozen_decision_rule() -> None:
    if not RESULT.exists():
        pytest.skip("T84 has not run")
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    passed = not value["failed_checks"]
    if passed:
        assert value["status"] == (
            "PASS_T84_T78_ROLLING_ADAPTER_MIDPOINTS"
        )
        assert value["decision"] == (
            "EARN_T85_ROLLING_MIDPOINT_NOMINAL_PREREGISTRATION_ONLY"
        )
        assert value["authority"]["nominal_matrix_preregistration"]
    else:
        assert value["status"] == (
            "HOLD_T84_T78_ROLLING_ADAPTER_MIDPOINTS"
        )
    assert value["execution"]["formal_behavior_cells"] == 0
    assert not value["authority"]["candidate_promotion"]
    assert not value["authority"]["gate5"]
