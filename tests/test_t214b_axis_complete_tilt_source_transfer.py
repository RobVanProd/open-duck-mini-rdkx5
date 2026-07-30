from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t214b_contract_source() -> None:
    builder = (
        ROOT
        / "tools"
        / "build_t214b_axis_complete_tilt_source_transfer_"
        "preregistration.py"
    ).read_text(encoding="utf-8")
    runner = (
        ROOT / "tools/run_t214b_axis_complete_tilt_source_transfer.py"
    ).read_text(encoding="utf-8")
    assert "prior_single_support_curricula_are_closed" in builder
    assert '"repeat_single_support_curriculum": False' in builder
    assert "body_pitch_rad + 0.08 * body_pitch_rate_rad_s" in builder
    assert "body_roll_rad + 0.08 * body_roll_rate_rad_s" in builder
    assert "required_dominant_axes_across_failures" in builder
    assert "dominant_failure_axes == required_axes" in runner
    assert "all_passes_have_zero_box_exceedance" in runner
    assert '"simulator_transitions": 0' in runner
    assert '"optimizer_steps": 0' in runner
    assert '"behavior_cells": 0' in runner


def test_t214b_result_when_present() -> None:
    path = (
        ANALYSIS / "t214b_axis_complete_tilt_source_transfer_result.json"
    )
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert (
        value["status"]
        == "PASS_T214B_AXIS_COMPLETE_TILT_SOURCE_TRANSFER"
    )
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert value["separation_rule_passed"] is True
    assert len(value["failure_summaries"]) == 3
    assert value["dominant_failure_axes"] == ["pitch", "roll"]
    assert (
        value["decision"]
        == "EARN_T215B_AXIS_COMPLETE_TILT_DUAL_CPU_CONTRACT_"
        "PREREGISTRATION_ONLY"
    )
    assert value["execution"]["simulator_transitions"] == 0
    assert value["execution"]["optimizer_steps"] == 0
    assert value["execution"]["behavior_cells"] == 0
    assert value["authority"]["training"] is False
    assert value["authority"]["gate5"] is False
