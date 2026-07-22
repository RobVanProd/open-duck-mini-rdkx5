from __future__ import annotations

import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "outputs/analysis/winner_v58b_guard_failure_attribution_result.json"


def test_result_records_the_exact_zero_update_failure() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_WINNER_V58B_GUARD_FAILURE_ATTRIBUTION"
    assert value["decision"] == "DO_NOT_RETRY_WINNER_V58"
    assert value["classification"] == "OTHER_OR_INCOMPLETE_PREUPDATE_GUARD_FAILURE"
    assert value["failed_checks"] == []
    assert value["failed_original_guard_predicates"] == [
        "hidden_replay_at_most_1e_6"
    ]
    assert value["metrics"]["sampled_hidden_replay_max_abs_error"] == pytest.approx(
        1.125037670135498e-6, rel=0.0, abs=0.0
    )
    assert value["metrics"]["observed_nonzero_reset_gradient_leaves"] == [
        "action_bias",
        "action_weight",
        "hidden_bias",
        "obs_weight",
    ]
    assert value["execution"]["optimizer_updates"] == 0
    assert value["checks"]["optimizer_count_unchanged_at_476"] is True
