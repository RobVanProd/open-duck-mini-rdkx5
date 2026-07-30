from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t213b_contract_source() -> None:
    builder = (
        ROOT
        / "tools/build_t213b_support_continuity_autopsy_preregistration.py"
    ).read_text(encoding="utf-8")
    runner = (
        ROOT / "tools/run_t213b_support_continuity_autopsy.py"
    ).read_text(encoding="utf-8")
    assert "HOLD_T213_T210_NOMINAL_MATRIX" in builder
    assert "foot_contacts == [0, 0]" in builder
    assert "late_roll_lead_maximum_ticks" in builder
    assert "threshold_tuning" in builder
    assert "maximum_true_run" in runner
    assert "height_strictly_collapses_after_anomalous_support_loss" in runner
    assert "current_pass_envelope_is_terminal_late" in runner
    assert '"simulator_transitions": 0' in runner
    assert '"optimizer_steps": 0' in runner
    assert '"behavior_cells": 0' in runner


def test_t213b_result_when_present() -> None:
    path = ANALYSIS / "t213b_support_continuity_autopsy_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_T213B_SUPPORT_CONTINUITY_AUTOPSY"
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert (
        value["decision"]
        == "EARN_T214B_SUPPORT_CONTINUITY_CURRICULUM_"
        "CPU_FALSIFIER_PREREGISTRATION_ONLY"
    )
    assert (
        value["classification"]
        == "SUPPORT_CONTINUITY_BREAK_PRECEDES_HEIGHT_AND_ROLL_COLLAPSE"
    )
    assert value["execution"]["simulator_transitions"] == 0
    assert value["execution"]["optimizer_steps"] == 0
    assert value["execution"]["behavior_cells"] == 0
    assert value["authority"]["training"] is False
    assert value["authority"]["gate5"] is False
