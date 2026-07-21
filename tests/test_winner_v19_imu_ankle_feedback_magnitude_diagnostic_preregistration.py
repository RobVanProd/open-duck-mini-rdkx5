from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PREREG = (
    ROOT
    / "outputs/analysis/winner_v19_imu_ankle_feedback_magnitude_diagnostic_preregistration.json"
)


def test_preregistration_is_frozen_when_present() -> None:
    if not PREREG.exists():
        return
    value = json.loads(PREREG.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PREREGISTERED_WINNER_V19_IMU_ANKLE_FEEDBACK_MAGNITUDE_DIAGNOSTIC"
    )
    assert value["decision"] == (
        "AUTHORIZE_ONE_CPU_ONLY_FEEDBACK_MAGNITUDE_FEASIBILITY_SCREEN"
    )
    screen = value["frozen_screen"]
    assert len(screen["interventions"]) == 7
    assert screen["maximum_target_offsets_rad"] == [0.03, 0.06, 0.09]
    assert screen["total_cells"] == 168
    assert screen["optimizer_updates"] == 0
    assert value["feedback_semantics"]["only_variable"] == (
        "maximum target offset 0.03, 0.06, or 0.09 rad"
    )
    assert value["authority"]["robot_clearance"] is False


def test_workflow_is_dormant_until_preregistration_exists() -> None:
    workflow = (
        ROOT / ".github/workflows/winner-v19-imu-ankle-feedback-magnitude-diagnostic.yml"
    )
    source = workflow.read_text(encoding="utf-8")
    trigger = source.split("permissions:", 1)[0]
    assert (
        "winner_v19_imu_ankle_feedback_magnitude_diagnostic_preregistration.json"
        in trigger
    )
    assert "run_winner_v19_imu_ankle_feedback_magnitude_diagnostic.py" in source
    assert "--hardware-authorized" not in source
