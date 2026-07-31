from __future__ import annotations

import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
PREREG = (
    ROOT
    / "outputs"
    / "analysis"
    / "t94_r2_calibration_manifold_preregistration_v3.json"
)
RESULT = (
    ROOT / "outputs" / "analysis" / "t94_r2_calibration_manifold_result.json"
)
CORRECTION = (
    ROOT
    / "outputs"
    / "analysis"
    / "t94_home_offset_reporting_correction.json"
)


def test_t94_preregistration_is_calibration_only() -> None:
    if not PREREG.exists():
        pytest.skip("T94 preregistration has not run")
    value = json.loads(PREREG.read_text(encoding="utf-8"))
    assert value["status"] == "PREREGISTERED_T94_R2_CALIBRATION_MANIFOLD_V3"
    assert value["failed_checks"] == []
    assert value["matrix"]["cells"] == 40
    assert value["matrix"]["duration_ticks"] == 250
    assert not value["authority"]["locomotion_behavior"]
    assert not value["authority"]["hosted_training"]
    assert not value["authority"]["rdkx5_or_robot"]


def test_t94_result_has_no_training_or_deployment_authority() -> None:
    if not RESULT.exists():
        pytest.skip("T94 formal calibration screen has not run")
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["execution"]["optimizer_steps"] == 0
    assert value["execution"]["hosted_compute_units"] == 0
    assert value["execution"]["robot_or_rdk_access"] == 0
    assert not value["authority"]["hosted_training"]
    assert not value["authority"]["deployment"]
    assert not value["authority"]["gate5"]


def test_t94_home_offset_reporting_correction_preserves_hold() -> None:
    if not CORRECTION.exists():
        pytest.skip("T94 reporting correction has not run")
    value = json.loads(CORRECTION.read_text(encoding="utf-8"))
    assert value["status"] == "CORRECTED_T94_HOME_OFFSET_REPORTING"
    assert len(value["corrections"]) == 4
    assert all(cell["corrected_cell_pass"] for cell in value["corrections"])
    assert value["corrected_summary"]["passing_calibration_cells"] == 40
    assert value["unchanged_routing_failures"]["fit_correct_cells"] == 23
    assert value["unchanged_routing_failures"][
        "negative_com_false_positives"
    ] == 2
    assert value["decision"] == "CLOSE_CALIBRATION_ROUTED_EXPERT_MECHANISM"
    assert not value["authority"]["hosted_training"]
    assert not value["authority"]["deployment"]
