from __future__ import annotations

import json
from pathlib import Path

from tools.run_t161_command_endpoint_replay_autopsy import canonical_sha256


ROOT = Path(__file__).resolve().parents[1]
RESULT = (
    ROOT
    / "outputs"
    / "analysis"
    / "t161_command_endpoint_replay_autopsy.json"
)


def test_t161_result_is_canonical_and_zero_execution() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    digest = value.pop("result_sha256")
    assert canonical_sha256(value) == digest
    assert value["status"] == "PASS_T161_COMMAND_ENDPOINT_REPLAY_AUTOPSY"
    assert not value["failed_checks"]
    assert value["checks"]["zero_behavior_executions"]
    assert value["checks"]["zero_training_or_hosted_compute"]
    assert value["authority"]["graph_contract"]
    assert not value["authority"]["behavior_rerun"]
    assert not value["authority"]["gate5"]


def test_t161_replay_uses_only_frozen_green_support_endpoints() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    rows = value["projected_replay_cells"]
    assert len(rows) == 16
    assert all(row["projected_cell_green_under_behavior_replay"] for row in rows)
    assert {
        row["policy_command_x_m_s"]
        for row in rows
        if row["checkpoint_id"] == "T159_MECHANICS_HALF"
        and row["external_command_x_m_s"] > 0
    } == {0.08}
    assert {
        row["policy_command_x_m_s"]
        for row in rows
        if row["checkpoint_id"] == "T159_MECHANICS_FINAL"
        and row["external_command_x_m_s"] > 0
    } == {0.074}
    assert min(
        row["projected_forward_tracking_ratio"]
        for row in rows
        if row["projected_forward_tracking_ratio"] is not None
    ) >= 0.25
