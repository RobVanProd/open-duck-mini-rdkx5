from __future__ import annotations

import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "outputs/analysis/winner_v59_hidden_replay_numeric_attribution_result.json"


def test_result_proves_bounded_eager_scan_float32_drift() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_WINNER_V59_HIDDEN_REPLAY_NUMERIC_ATTRIBUTION"
    assert (
        value["decision"]
        == "AUTHORIZE_REVISED_NUMERIC_GUARD_CONTINUATION_PREREGISTRATION_ONLY"
    )
    assert (
        value["classification"]
        == "EAGER_SCAN_FLOAT32_NUMERIC_DRIFT_WITH_BOUNDED_POLICY_EFFECT"
    )
    assert value["failed_checks"] == []
    assert value["failed_original_guard_predicates"] == [
        "hidden_replay_at_most_1e_6"
    ]
    assert all(value["checks"].values())
    metrics = value["metrics"]
    assert metrics["eager_hidden_max_abs_error"] == 0.0
    assert metrics["scan_hidden_max_abs_error"] == pytest.approx(
        1.125037670135498e-6, rel=0.0, abs=0.0
    )
    assert metrics["mean_action_max_abs_delta"] == pytest.approx(
        1.4901161193847656e-7, rel=0.0, abs=0.0
    )
    assert metrics["value_max_abs_delta"] == pytest.approx(
        1.1920928955078125e-6, rel=0.0, abs=0.0
    )
    assert metrics["log_probability_max_abs_delta"] == pytest.approx(
        1.1444091796875e-5, rel=0.0, abs=0.0
    )
    assert metrics["probability_ratio_max_abs_delta"] == pytest.approx(
        1.1444091796875e-5, rel=0.0, abs=0.0
    )
    assert metrics["ppo_loss_abs_delta"] == 0.0
    assert value["execution"]["optimizer_updates"] == 0
    assert value["execution"]["formal_support_cells"] == 0
    assert value["authority"]["continuation_executed"] is False
    assert value["authority"]["robot_clearance"] is False
