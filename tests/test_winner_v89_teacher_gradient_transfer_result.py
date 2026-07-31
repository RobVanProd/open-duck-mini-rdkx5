from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "outputs/analysis/winner_v89_teacher_gradient_transfer_result.json"


def test_result_rejects_static_teacher_gradient_transfer() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_WINNER_V89_TEACHER_GRADIENT_TRANSFER_DIAGNOSTIC"
    assert value["classification"] == "STATIC_TEACHER_GRADIENT_NONTRANSFERABLE"
    assert value["decision"] == "PREREGISTER_OUTCOME_ALIGNED_MECHANISM_DIAGNOSTIC"
    assert value["selected_source_checkpoint_for_step_proof"] is None
    assert value["selected_gradient_group_for_step_proof"] is None
    assert value["failed_checks"] == []
    assert all(value["checks"].values())


def test_recurrent_action_and_combined_gradients_are_noncoherent() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    expected = {
        "half": {"recurrent_core": 4, "action_head": 5, "combined_policy": 5},
        "final": {"recurrent_core": 5, "action_head": 6, "combined_policy": 5},
    }
    for endpoint in value["endpoints"]:
        assert endpoint["selected_endpoint_mechanism"] is None
        for group, count in expected[endpoint["label"]].items():
            summary = endpoint["group_summaries"][group]
            assert summary["strictly_positive_folds"] == count
            assert summary["nonpositive_folds"] == 12 - count
            assert summary["all_12_strictly_positive"] is False
            assert summary["dot_sum"] < 0.0


def test_result_commits_no_update_or_artifact() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["execution"] == {
        "formal_support_cells": 0,
        "gradient_evaluations": 48,
        "optimizer_updates": 0,
        "robot_or_rdk_access": 0,
        "snapshot_or_onnx_writes": 0,
        "stage2_rollout_episodes": 160,
    }
    assert value["authority"]["training_authorized_now"] is False
    assert value["authority"]["checkpoint_selection_authorized"] is False
    assert value["authority"]["robot_clearance"] is False
