from __future__ import annotations

import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "outputs/analysis/winner_v62_residual_teacher_causal_result.json"


def test_result_selects_persistent_pitch_mismatch_diagnosis() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_WINNER_V62_RESIDUAL_TEACHER_CAUSAL_DIAGNOSTIC"
    assert (
        value["decision"]
        == "SELECT_NEXT_MECHANISM_FROM_FROZEN_RESIDUAL_CLASSIFICATION_ONLY"
    )
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert value["findings"]["support_pass_counts"] == {
        "full_teacher": 13,
        "graph": 0,
        "nonpitch_zero": 0,
        "pitch_teacher": 12,
    }
    assert value["findings"]["classification_counts"] == {
        "either_single_intervention_rescues": 0,
        "nonpitch_output_causal": 0,
        "pitch_nonpitch_interaction": 1,
        "pitch_output_causal": 12,
        "teacher_insufficient": 0,
    }
    assert value["findings"]["first_tick_pitch_rms_mean"] == pytest.approx(
        0.07728285739495369, rel=0.0, abs=0.0
    )
    assert value["findings"]["post_first_tick_pitch_rms_mean"] == pytest.approx(
        0.0817888110754449, rel=0.0, abs=0.0
    )
    assert value["execution"] == {
        "diagnostic_cells": 52,
        "locomotion_steps": 0,
        "optimizer_updates": 0,
        "robot_or_rdk_access": 0,
    }
    assert value["authority"]["robot_clearance"] is False
