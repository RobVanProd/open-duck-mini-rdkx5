from __future__ import annotations

import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "outputs/analysis/winner_v64b_isolated_persistent_teacher_step_result.json"


def test_v64b_result_is_one_valid_nonselected_step() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_WINNER_V64B_ISOLATED_PERSISTENT_TEACHER_STEP"
    assert value["decision"] == (
        "PREREGISTER_BOUNDED_ISOLATED_PERSISTENT_TEACHER_CONTINUATION_ONLY"
    )
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    optimization = value["optimization"]
    assert optimization["optimizer_count_before"] == 554
    assert optimization["optimizer_count_after"] == 555
    assert optimization["loss_before"] == pytest.approx(
        0.003402196103706956, abs=1.0e-15
    )
    assert optimization["loss_after"] == pytest.approx(
        0.003393699647858739, abs=1.0e-15
    )
    assert optimization["loss_delta"] < 0.0
    assert len(optimization["leaf_max_abs_delta"]) == 12
    assert all(value > 0.0 for value in optimization["leaf_max_abs_delta"].values())
    assert value["snapshot"]["completed_updates"] == 555
    assert value["snapshot"]["sha256"] == (
        "4ed0d4587bf21b448849d46b897f449182c27d5bb5ed830be2738f1fdad1f0e9"
    )
    assert value["graph"]["sha256"] == (
        "f6e341e24972c434780fc803d9bf30113d71fd24561ead380c12a14b4ae45b80"
    )
    assert value["graph"]["abi_exact"] is True
    assert value["graph"]["training_only_tensors_absent"] is True
    assert value["graph"]["previous_action_out_equals_action_bit_exact"] is True
    assert value["graph"]["jax_onnx_max_abs_error"] <= 1.0e-7
    assert value["execution"] == {
        "rollout_episode_slots": 80,
        "scheduled_rollout_ticks": 20000,
        "optimizer_updates": 1,
        "continuation_updates": 0,
        "formal_support_cells": 0,
        "candidate_graph_exports": 1,
        "robot_or_rdk_access": 0,
    }
    assert value["authority"]["robot_clearance"] is False
    assert value["authority"]["continuation_training_executed"] is False

