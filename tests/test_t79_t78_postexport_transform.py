from __future__ import annotations

import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "t79_t78_postexport_preregistration.json"
RESULT = ANALYSIS / "t79_t78_postexport_result.json"


def test_t79_preregistration_freezes_three_identical_transforms() -> None:
    if not PREREG.exists():
        pytest.skip("T79 has not been preregistered")
    value = json.loads(PREREG.read_text(encoding="utf-8"))
    assert value["status"] == "PREREGISTERED_T79_T78_POSTEXPORT_TRANSFORM"
    assert value["failed_checks"] == []
    assert sorted(map(int, value["raw_graphs"])) == [
        0,
        1_003_520,
        2_007_040,
    ]
    assert value["postupdate_steps"] == [1_003_520, 2_007_040]
    assert not value["authority"]["behavior_evaluation"]
    assert not value["authority"]["gate5"]


def test_t79_result_obeys_transform_decision_rule() -> None:
    if not RESULT.exists():
        pytest.skip("T79 transform has not run")
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    passed = not value["failed_checks"]
    if passed:
        assert value["status"] == "PASS_T79_T78_POSTEXPORT_TRANSFORM"
        assert value["decision"] == "EARN_T80_NOMINAL_MATRIX_PREREGISTRATION"
        assert value["authority"]["nominal_matrix_preregistration_authorized"]
    else:
        assert value["status"] == "HOLD_T79_T78_POSTEXPORT_TRANSFORM"
        assert value["decision"] == "HOLD_WITHOUT_BEHAVIOR"
    assert value["execution"]["formal_behavior_cells"] == 0
    assert value["execution"]["robot_or_rdk_access"] == 0
    assert not value["authority"]["gate5_authorized"]
