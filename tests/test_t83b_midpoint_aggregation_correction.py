from __future__ import annotations

import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = (
    ANALYSIS / "t83b_midpoint_aggregation_correction_preregistration.json"
)
RESULT = ANALYSIS / "t83b_midpoint_aggregation_correction_result.json"


def test_t83b_preregistration_is_reporting_only() -> None:
    if not PREREG.exists():
        pytest.skip("T83b has not been preregistered")
    value = json.loads(PREREG.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PREREGISTERED_T83B_REPORTING_ONLY_AGGREGATION_CORRECTION"
    )
    assert value["failed_checks"] == []
    assert value["frozen_correction"]["expected_blocks"] == 2
    assert value["frozen_correction"]["expected_cells"] == 8
    assert value["frozen_correction"]["simulator_rerun"] is False
    assert value["execution_now"]["correction_formal_behavior_cells"] == 0


def test_t83b_result_obeys_read_only_decision() -> None:
    if not RESULT.exists():
        pytest.skip("T83b has not run")
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    passed = not value["failed_checks"]
    if passed:
        assert value["status"] == (
            "PASS_T83B_MIDPOINT_AGGREGATION_CORRECTION"
        )
        assert value["decision"] == (
            "EARN_T84_PERSISTENT_INTERPOLATION_MECHANISM_PREREGISTRATION_ONLY"
        )
        assert value["condition"]["condition_green"]
        assert value["condition"]["green_cells"] == 8
    else:
        assert value["status"] == (
            "HOLD_T83B_MIDPOINT_AGGREGATION_CORRECTION"
        )
    assert value["execution"]["correction_formal_behavior_cells"] == 0
    assert not value["authority"]["candidate_promotion"]
    assert not value["authority"]["gate5"]
