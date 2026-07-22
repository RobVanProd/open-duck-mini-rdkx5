from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "outputs/analysis/winner_v81_pitch_action_head_continuation_result.json"


def test_result_stops_before_persistence_gate_at_count_675() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["status"] == "HOLD_WINNER_V81_PITCH_ACTION_HEAD_CONTINUATION"
    assert value["decision"] == "DO_NOT_RUN_PERSISTENCE_GATE"
    assert value["execution"] == {
        "optimizer_updates": 18,
        "formal_support_cells": 0,
        "locomotion_steps": 0,
        "robot_or_rdk_access": 0,
    }
    assert value["persistent_checkpoints"] == []
    snapshots = value["snapshot_manifest"]
    assert [row["completed_updates"] for row in snapshots] == list(range(657, 675))
    assert snapshots[0]["sha256"] == (
        "dfeb3f2eeea428645dc6901839828125ea53768544d9cfd9ef3678316b417f2b"
    )
    assert snapshots[-1]["sha256"] == (
        "bfcc8f4c3cc22e3259decafb2f5a557a55e94534a2464933d061b6facbe80057"
    )


def test_stop_is_negative_dot_grid_exhaustion_not_stale_moment_reset() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    stop = value["stop"]
    assert stop["attempted_completed_count"] == 675
    assert stop["moment_reset_attempted"] is False
    assert stop["gradient_dot_proposed_delta"] < 0.0
    assert stop["loss_before"] == 0.007218536455184221
    assert [row["fraction"] for row in stop["backtracking_rows"]] == [
        1.0,
        0.5,
        0.25,
        0.125,
        0.0625,
        0.03125,
        0.015625,
        0.0078125,
        0.00390625,
        0.001953125,
        0.0009765625,
    ]
    assert all(row["loss"] >= stop["loss_before"] for row in stop["backtracking_rows"])
    assert stop["backtracking_rows"][-1]["loss_delta"] == 1.3969838619232178e-09
    assert value["authority"]["robot_clearance"] is False
