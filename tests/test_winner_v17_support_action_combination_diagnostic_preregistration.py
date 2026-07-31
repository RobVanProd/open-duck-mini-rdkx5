from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PREREG = (
    ROOT
    / "outputs/analysis/winner_v17_support_action_combination_diagnostic_preregistration.json"
)


def test_preregistration_is_frozen_when_present() -> None:
    if not PREREG.exists():
        return
    value = json.loads(PREREG.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PREREGISTERED_WINNER_V17_SUPPORT_ACTION_COMBINATION_DIAGNOSTIC"
    )
    assert value["decision"] == (
        "AUTHORIZE_ONE_CPU_ONLY_SIGN_CONSISTENT_COMBINATION_DIAGNOSTIC"
    )
    assert set(value["causal_basis"]) == {
        "HIP_MAG_NEG",
        "KNEE_POS",
        "ANKLE_POS",
    }
    assert all(
        row["desired_outlives_opposite_cells"] == 24
        for row in value["causal_basis"].values()
    )
    screen = value["frozen_screen"]
    assert len(screen["interventions"]) == 8
    assert screen["total_cells"] == 192
    assert screen["target_offset_per_active_axis_rad"] == 0.03
    assert screen["optimizer_updates"] == 0
    assert value["execution_now"] == {
        "optimizer_updates": 0,
        "diagnostic_cells": 0,
        "locomotion_steps": 0,
        "robot_or_rdk_access": 0,
    }
    assert value["authority"]["robot_clearance"] is False
    assert value["authority"]["training_authorized"] is False


def test_workflow_is_dormant_until_preregistration_exists() -> None:
    workflow = (
        ROOT
        / ".github/workflows/winner-v17-support-action-combination-diagnostic.yml"
    )
    source = workflow.read_text(encoding="utf-8")
    trigger = source.split("permissions:", 1)[0]
    assert (
        "winner_v17_support_action_combination_diagnostic_preregistration.json"
        in trigger
    )
    assert "run_winner_v17_support_action_combination_diagnostic.py" in source
    assert "--hardware-authorized" not in source
