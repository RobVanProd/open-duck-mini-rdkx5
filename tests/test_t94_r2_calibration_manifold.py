from __future__ import annotations

import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
PREREG = (
    ROOT
    / "outputs"
    / "analysis"
    / "t94_r2_calibration_manifold_preregistration_v2.json"
)
RESULT = (
    ROOT / "outputs" / "analysis" / "t94_r2_calibration_manifold_result.json"
)


def test_t94_preregistration_is_calibration_only() -> None:
    if not PREREG.exists():
        pytest.skip("T94 preregistration has not run")
    value = json.loads(PREREG.read_text(encoding="utf-8"))
    assert value["status"] == "PREREGISTERED_T94_R2_CALIBRATION_MANIFOLD_V2"
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
