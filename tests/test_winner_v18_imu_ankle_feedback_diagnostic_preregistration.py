from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PREREG = (
    ROOT / "outputs/analysis/winner_v18_imu_ankle_feedback_diagnostic_preregistration.json"
)


def test_preregistration_is_frozen_when_present() -> None:
    if not PREREG.exists():
        return
    value = json.loads(PREREG.read_text(encoding="utf-8"))
    assert value["status"] == "PREREGISTERED_WINNER_V18_IMU_ANKLE_FEEDBACK_DIAGNOSTIC"
    assert value["decision"] == (
        "AUTHORIZE_ONE_CPU_ONLY_ONE_SIDED_IMU_ANKLE_FEEDBACK_DIAGNOSTIC"
    )
    screen = value["frozen_screen"]
    assert len(screen["interventions"]) == 7
    assert screen["total_cells"] == 168
    assert screen["maximum_target_offset_rad"] == 0.03
    assert screen["gyro_pitch_rate_observation_index"] == 1
    assert screen["accelerometer_observation_slice"] == [3, 6]
    assert screen["optimizer_updates"] == 0
    assert value["execution_now"] == {
        "optimizer_updates": 0,
        "diagnostic_cells": 0,
        "locomotion_steps": 0,
        "robot_or_rdk_access": 0,
    }
    assert value["authority"]["robot_clearance"] is False


def test_workflow_is_dormant_until_preregistration_exists() -> None:
    workflow = ROOT / ".github/workflows/winner-v18-imu-ankle-feedback-diagnostic.yml"
    source = workflow.read_text(encoding="utf-8")
    trigger = source.split("permissions:", 1)[0]
    assert "winner_v18_imu_ankle_feedback_diagnostic_preregistration.json" in trigger
    assert "run_winner_v18_imu_ankle_feedback_diagnostic.py" in source
    assert "--hardware-authorized" not in source
