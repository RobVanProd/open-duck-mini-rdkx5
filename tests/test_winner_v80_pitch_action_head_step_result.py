from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "outputs/analysis/winner_v80_pitch_action_head_step_result.json"


def test_result_proves_localized_pitch_head_step() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_WINNER_V80_PITCH_ACTION_HEAD_STEP"
    assert value["decision"] == "PREREGISTER_BOUNDED_PITCH_ACTION_HEAD_CONTINUATION_ONLY"
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    optimization = value["optimization"]
    assert optimization["optimizer_count_before"] == 655
    assert optimization["optimizer_count_after"] == 656
    assert optimization["accepted_fraction"] == 1.0
    assert optimization["accepted_loss"] < optimization["loss_before"]
    assert optimization["predictor_loss_after"] == optimization["predictor_loss_before"]
    assert optimization["projected_gradient_nonzero_counts"]["action_weight"] == 384
    assert optimization["projected_gradient_nonzero_counts"]["action_bias"] == 6
    assert all(
        count == 0
        for name, count in optimization["projected_gradient_nonzero_counts"].items()
        if name not in {"action_weight", "action_bias"}
    )
    assert value["snapshot"]["sha256"] == (
        "6d0cbb20c0985ba2926471a6d5902d6f969ce2e82bb04471a3ddc308f183ce71"
    )
    assert value["graph"]["sha256"] == (
        "38e9dd4886593c4e3a996ec74493748138295e9740098a9594020ed152249210"
    )
    assert value["execution"] == {
        "optimizer_updates": 1,
        "continuation_optimizer_updates": 0,
        "formal_support_cells": 0,
        "locomotion_steps": 0,
        "robot_or_rdk_access": 0,
    }
    assert value["authority"]["robot_clearance"] is False
