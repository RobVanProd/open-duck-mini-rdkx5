from __future__ import annotations

from collections import Counter
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "outputs/analysis/winner_v75_functional_numeric_guard_continuation_result.json"


def test_result_reaches_both_endpoints_with_functional_guard() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_WINNER_V75_FUNCTIONAL_NUMERIC_GUARD_CONTINUATION"
    assert value["decision"] == "AUTHORIZE_UNCHANGED_PERSISTENCE_GATE_FOR_COUNTS_605_AND_655_ONLY"
    assert value["failed_checks"] == []
    assert value["execution"] == {
        "optimizer_updates": 53,
        "rollout_episode_slots": 4240,
        "scheduled_rollout_ticks": 1060000,
        "formal_support_cells": 0,
        "locomotion_steps": 0,
        "robot_or_rdk_access": 0,
    }
    checkpoints = value["persistent_checkpoints"]
    assert [(row["label"], row["completed_updates"]) for row in checkpoints] == [
        ("half", 605),
        ("final", 655),
    ]
    assert checkpoints[0]["snapshot"]["sha256"] == (
        "0b2c804686dff8b01ecdf2a431d4caf43f7a5a234ee6055e3d9835a75db000d0"
    )
    assert checkpoints[0]["graph"]["sha256"] == (
        "e2b97fe6b18c09c69fd9a9d8a1fe9e39cfa6b2a806f20bd05a215253830d5eab"
    )
    assert checkpoints[1]["snapshot"]["sha256"] == (
        "00a68b8c0f08996afa770cd84218574872851e613cbb8441caa66af84ece73c6"
    )
    assert checkpoints[1]["graph"]["sha256"] == (
        "abd438a70904d9fc117bd04520a7ea7555f310a2f0c5259027af0ee6752f9add"
    )
    metrics = value["metrics"]
    assert [row["completed_updates"] for row in metrics] == list(range(603, 656))
    audits = [
        row for row in metrics if row["hidden_replay_functional_evidence"]["functional_audit_performed"]
    ]
    assert [row["completed_updates"] for row in audits] == [638]
    assert audits[0]["hidden_replay_functional_evidence"]["pass"] is True
    assert audits[0]["hidden_replay_functional_evidence"]["eager_hidden_max_abs_error"] == 0.0
    assert sum(row["moment_reset_applied"] for row in metrics) == 4
    assert Counter(row["accepted_backtracking_fraction"] for row in metrics) == {
        1.0: 9,
        0.5: 17,
        0.25: 13,
        0.125: 8,
        0.0625: 2,
        0.03125: 1,
        0.015625: 1,
        0.0078125: 1,
        0.00390625: 1,
    }
    assert all(value["checks"].values())
    assert value["authority"]["robot_clearance"] is False
