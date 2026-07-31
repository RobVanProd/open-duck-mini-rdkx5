from __future__ import annotations

import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "t58_t56_postexport_preregistration.json"
RESULT = ANALYSIS / "t58_t56_postexport_result.json"


def test_t58_preregistration_has_no_behavior_authority() -> None:
    if not PREREG.exists():
        pytest.skip("T58 has not been preregistered")
    value = json.loads(PREREG.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PREREGISTERED_T58_T56_POSTEXPORT_TRANSFORM"
    )
    assert value["failed_checks"] == []
    assert value["postupdate_steps"] == [1_003_520, 2_007_040]
    assert value["authority"]["one_cpu_only_postexport_transform"]
    assert not value["authority"]["behavior_evaluation"]
    assert not value["authority"]["gate5"]


def test_t58_all_transfer_exports_pass_frozen_chain() -> None:
    if not RESULT.exists():
        pytest.skip("T58 transform has not run")
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_T58_T56_POSTEXPORT_TRANSFORM"
    assert value["decision"] == "EARN_T59_NOMINAL_MATRIX_PREREGISTRATION"
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert sorted(value["deployments"]) == [
        "0",
        "1003520",
        "2007040",
    ]
    assert value["execution"]["formal_behavior_cells"] == 0
    assert value["authority"]["nominal_matrix_preregistration_authorized"]
    assert not value["authority"]["behavior_evaluation_authorized"]
    assert not value["authority"]["gate5_authorized"]
