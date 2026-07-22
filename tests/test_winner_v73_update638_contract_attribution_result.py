from __future__ import annotations

import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "outputs/analysis/winner_v73_update638_contract_attribution_result.json"


def test_result_is_single_invariant_zero_update_attribution() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_WINNER_V73_UPDATE638_CONTRACT_ATTRIBUTION"
    assert value["classification"] == "SAMPLED_HIDDEN_REPLAY_TOLERANCE_CROSSED"
    assert value["decision"] == "PREREGISTER_HIDDEN_REPLAY_TOLERANCE_CAUSAL_AUDIT_ONLY"
    assert value["failed_checks"] == ["sampled_hidden_replay_at_most_2e_6"]
    metrics = value["contract_values"]
    assert metrics["sampled_hidden_replay_limit"] == 2.0e-6
    assert metrics["sampled_hidden_replay_max_abs_error"] == pytest.approx(
        3.7550926208496094e-6, rel=0.0, abs=0.0
    )
    assert metrics["stored_successor_transition_count"] == 18490
    assert metrics["expected_stored_successor_transition_count"] == 18490
    assert metrics["anchor_selected_elements"] == 384
    assert metrics["expected_anchor_selected_elements"] == 384
    assert metrics["teacher_selected_elements"] == 59626
    assert metrics["reconstructed_teacher_selected_elements"] == 59626
    assert metrics["teacher_selected_rows"] == 22
    assert value["execution"]["committed_optimizer_updates"] == 0
    assert value["execution"]["snapshots_written"] == 0
    assert value["execution"]["onnx_graphs_written"] == 0
    assert value["execution"]["formal_support_cells"] == 0
    assert value["execution"]["robot_or_rdk_access"] == 0
    assert value["authority"]["robot_clearance"] is False
