from __future__ import annotations

from collections import Counter
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = (
    ROOT / "outputs/analysis/winner_v84_negative_gradient_pitch_head_continuation_result.json"
)


def test_result_reaches_both_original_persistence_endpoints() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PASS_WINNER_V84_NEGATIVE_GRADIENT_PITCH_HEAD_CONTINUATION"
    )
    assert value["decision"] == (
        "AUTHORIZE_UNCHANGED_PERSISTENCE_GATE_FOR_COUNTS_705_AND_755_ONLY"
    )
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert value["execution"] == {
        "optimizer_updates": 80,
        "rollout_episode_slots": 6400,
        "scheduled_rollout_ticks": 1600000,
        "formal_support_cells": 0,
        "locomotion_steps": 0,
        "robot_or_rdk_access": 0,
    }
    assert [row["completed_updates"] for row in value["snapshot_manifest"]] == list(
        range(676, 756)
    )
    assert [(row["label"], row["completed_updates"]) for row in value["persistent_checkpoints"]] == [
        ("half", 705),
        ("final", 755),
    ]
    assert Counter(row["accepted_fraction"] for row in value["metrics"]) == {
        1.0: 69,
        0.5: 11,
    }
    assert value["authority"]["robot_clearance"] is False


def test_endpoint_snapshot_and_graph_receipts_are_frozen() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    half, final = value["persistent_checkpoints"]
    assert half["snapshot"]["sha256"] == (
        "a39e76e0eaaeb795eb88ccd636e35fab073bcde4ebf19d6cc91a581b1849e05c"
    )
    assert half["graph"]["sha256"] == (
        "f2f6d6ac0d184245d5abee92c57eb45828356ce63dafc97ce0bf38080c644727"
    )
    assert final["snapshot"]["sha256"] == (
        "45528bb25cd993406d5c5527d0391411274f6c657dc486d622e35bcad8c2de1e"
    )
    assert final["graph"]["sha256"] == (
        "de20542d9c49849d974e063e03e8fd55d2310337ed1d8f2329453ee25b489173"
    )
    assert all(
        row["graph"]["contract"]["previous_action_out_equals_action_bit_exact"]
        for row in (half, final)
    )
