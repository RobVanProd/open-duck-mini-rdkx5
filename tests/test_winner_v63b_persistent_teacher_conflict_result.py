from __future__ import annotations

import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "outputs/analysis/winner_v63b_persistent_teacher_conflict_result.json"


def test_v63b_result_selects_isolated_persistent_teacher_step() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PASS_WINNER_V63B_PERSISTENT_TEACHER_CONFLICT_ATTRIBUTION"
    )
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert value["classification"] == (
        "INTEGRATED_STEP_BLOCKS_PERSISTENT_TEACHER_DESCENT"
    )
    assert value["decision"] == (
        "PREREGISTER_ISOLATED_PERSISTENT_TEACHER_STEP_CONTRACT"
    )
    integrated = value["counterfactual_same_batch_steps"]["integrated"]
    isolated = value["counterfactual_same_batch_steps"][
        "teacher_only_with_inherited_adam_state"
    ]
    assert integrated["teacher_loss_before"] == pytest.approx(
        0.003402196103706956, abs=1.0e-15
    )
    assert integrated["teacher_loss_after"] == pytest.approx(
        0.003406578442081809, abs=1.0e-15
    )
    assert integrated["teacher_loss_delta"] > 0.0
    assert isolated["teacher_loss_after"] == pytest.approx(
        0.003393699647858739, abs=1.0e-15
    )
    assert isolated["teacher_loss_delta"] < 0.0
    policy = value["gradient_alignment_to_persistent_teacher"]["policy"]
    assert policy["all_other_terms"]["dot_product"] == pytest.approx(
        -85.6093058525753, abs=1.0e-12
    )
    assert policy["integrated_total"]["dot_product"] == pytest.approx(
        -19.18844086774707, abs=1.0e-12
    )
    assert policy["all_other_terms"][
        "gradient_descent_first_order_hurts_reference"
    ] is True
    assert policy["integrated_total"][
        "gradient_descent_first_order_hurts_reference"
    ] is True
    assert value["execution"] == {
        "rollout_episode_slots": 80,
        "scheduled_rollout_ticks": 20000,
        "counterfactual_in_memory_adam_steps": 2,
        "committed_optimizer_updates": 0,
        "formal_support_cells": 0,
        "locomotion_training_steps": 0,
        "deployable_graph_exports": 0,
        "robot_or_rdk_access": 0,
    }
    assert value["authority"]["robot_clearance"] is False

