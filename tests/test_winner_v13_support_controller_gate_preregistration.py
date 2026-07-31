from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PREREG = ROOT / "outputs/analysis/winner_v13_support_controller_gate_preregistration.json"


def test_gate_preregistration_is_exact_when_present() -> None:
    if not PREREG.exists():
        return
    value = json.loads(PREREG.read_text(encoding="utf-8"))
    assert value["status"] == "PREREGISTERED_WINNER_V13_SUPPORT_CONTROLLER_GATE"
    assert value["decision"] == "AUTHORIZE_ONE_FROZEN_248_CELL_GATE_ONLY"
    gate = value["future_frozen_support_gate"]
    assert gate["cells_per_checkpoint"] == 124
    assert gate["checkpoint_labels"] == ["half", "final"]
    assert gate["all_cells_at_both_checkpoints_must_pass"] is True
    assert gate["selection_by_closest_result"] is False
    assert value["execution_now"] == {
        "formal_support_cells": 0,
        "heldout_repeat_cells": 0,
        "locomotion_steps": 0,
        "robot_or_rdk_access": 0,
    }


def test_workflow_is_dormant_until_preregistration_exists() -> None:
    workflow = ROOT / ".github/workflows/winner-v13-support-controller-gate.yml"
    source = workflow.read_text(encoding="utf-8")
    trigger = source.split("permissions:", 1)[0]
    assert "winner_v13_support_controller_gate_preregistration.json" in trigger
    assert "run_winner_v13_support_controller_gate.py" in source
    assert "--formal-gate-authorized" in source
    assert "--hardware-authorized" not in source
