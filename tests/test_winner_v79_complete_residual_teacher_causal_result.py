from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "outputs/analysis/winner_v79_complete_residual_teacher_causal_result.json"


def test_result_localizes_all_nine_failures_to_pitch_outputs() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_WINNER_V79_RESIDUAL_TEACHER_CAUSAL_DIAGNOSTIC"
    assert value["decision"] == "SELECT_NEXT_MECHANISM_FROM_FROZEN_RESIDUAL_CLASSIFICATION_ONLY"
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert value["findings"]["support_pass_counts"] == {
        "graph": 0,
        "full_teacher": 9,
        "pitch_teacher": 9,
        "nonpitch_zero": 0,
    }
    assert value["findings"]["classification_counts"] == {
        "teacher_insufficient": 0,
        "pitch_output_causal": 9,
        "nonpitch_output_causal": 0,
        "either_single_intervention_rescues": 0,
        "pitch_nonpitch_interaction": 0,
    }
    assert value["findings"]["full_teacher_all_9_pass"] is True
    assert all(
        row["classification"] == "pitch_output_causal"
        for row in value["findings"]["classification_rows"]
    )
    assert value["execution"] == {
        "diagnostic_cells": 36,
        "optimizer_updates": 0,
        "locomotion_steps": 0,
        "robot_or_rdk_access": 0,
    }
    assert value["checkpoint"]["update"] == 655
    assert len(value["checkpoint"]["cells"]) == 9
    assert value["authority"]["robot_clearance"] is False
