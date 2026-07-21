from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PREREG = ROOT / "outputs/analysis/winner_v16_support_action_direction_diagnostic_preregistration.json"


def test_preregistration_is_exact_when_present() -> None:
    if not PREREG.exists():
        return
    value = json.loads(PREREG.read_text(encoding="utf-8"))
    assert value["status"] == "PREREGISTERED_WINNER_V16_SUPPORT_ACTION_DIRECTION_DIAGNOSTIC"
    assert value["decision"] == "AUTHORIZE_ONE_CPU_ONLY_BILATERAL_PITCH_CHAIN_DIRECTION_DIAGNOSTIC"
    screen = value["frozen_screen"]
    assert screen["checkpoint_labels"] == ["half", "final"]
    assert len(screen["failure_configuration_ids"]) == 6
    assert len(screen["interventions"]) == 7
    assert screen["target_offset_rad"] == 0.03
    assert screen["normalized_offset"] == 0.12
    assert screen["total_cells"] == 168
    assert screen["optimizer_updates"] == 0
    assert value["execution_now"] == {
        "optimizer_updates": 0,
        "diagnostic_cells": 0,
        "locomotion_steps": 0,
        "robot_or_rdk_access": 0,
    }


def test_workflow_is_dormant_until_preregistration_exists() -> None:
    workflow = ROOT / ".github/workflows/winner-v16-support-action-direction-diagnostic.yml"
    source = workflow.read_text(encoding="utf-8")
    trigger = source.split("permissions:", 1)[0]
    assert "winner_v16_support_action_direction_diagnostic_preregistration.json" in trigger
    assert "run_winner_v16_support_action_direction_diagnostic.py" in source
    assert "--direction-diagnostic-authorized" in source
    assert "--hardware-authorized" not in source
