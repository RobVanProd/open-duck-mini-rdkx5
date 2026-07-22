from __future__ import annotations

import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "outputs/analysis/winner_v60_integrated_numeric_guard_training_result.json"


def test_result_is_complete_hash_bound_training_evidence() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert (
        value["status"]
        == "PASS_WINNER_V60_INTEGRATED_FIRST_TICK_TEACHER_TRAINING_ARTIFACT"
    )
    assert (
        value["decision"]
        == "AUTHORIZE_INTEGRATED_FIRST_TICK_TEACHER_SUPPORT_GATE_PREREGISTRATION_ONLY"
    )
    assert value["failed_checks"] == []
    assert len(value["checks"]) == 23
    assert all(value["checks"].values())
    assert len(value["metrics"]) == 100
    assert [row["completed_updates"] for row in value["metrics"]] == list(
        range(455, 555)
    )
    assert len(value["snapshot_manifest"]) == 100
    assert value["execution"] == {
        "formal_support_cells": 0,
        "locomotion_steps": 0,
        "optimizer_updates": 100,
        "robot_or_rdk_access": 0,
        "scheduled_episode_slots": 2_000_000,
    }
    assert max(
        row["sampled_hidden_replay_max_abs_error"] for row in value["metrics"]
    ) == pytest.approx(1.6093254089355469e-6, rel=0.0, abs=0.0)
    checkpoints = {row["label"]: row for row in value["persistent_checkpoints"]}
    assert checkpoints["half"]["completed_updates"] == 504
    assert (
        checkpoints["half"]["snapshot"]["sha256"]
        == "efbf2ecf5ffa892c3c51251ccd9d87a6f9c70adbbd15c0d913ed9d04e14c06de"
    )
    assert (
        checkpoints["half"]["graph"]["sha256"]
        == "37e483f533e606e38257a16efdde341cd8725b798a44d21b8eacc21c57af0a02"
    )
    assert checkpoints["final"]["completed_updates"] == 554
    assert (
        checkpoints["final"]["snapshot"]["sha256"]
        == "c8eb7032dea20c2c197ab03f7544ea9be92d2694a3a3414656941978117d8802"
    )
    assert (
        checkpoints["final"]["graph"]["sha256"]
        == "4a6386d8dddfcc441f90bce4f64d7307144446bb3032c171c22cb2e299ac3939"
    )
    for checkpoint in checkpoints.values():
        contract = checkpoint["graph"]["contract"]
        assert contract["abi_exact"] is True
        assert contract["training_only_tensors_absent"] is True
        assert contract["previous_action_out_equals_action_bit_exact"] is True
        assert contract["jax_onnx_at_most_1e_7"] is True
    assert value["authority"]["formal_support_gate_executed"] is False
    assert value["authority"]["robot_clearance"] is False
