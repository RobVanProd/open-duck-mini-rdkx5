from __future__ import annotations

import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "outputs/analysis/winner_v74_update638_hidden_replay_numeric_audit_result.json"


def test_numeric_audit_proves_bounded_execution_order_drift() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_WINNER_V74_UPDATE638_HIDDEN_REPLAY_NUMERIC_AUDIT"
    assert value["classification"] == (
        "EAGER_SCAN_FLOAT32_DRIFT_WITH_BOUNDED_POLICY_EFFECT_AND_STALE_ABSOLUTE_SCAN_GUARD"
    )
    assert value["decision"] == "PREREGISTER_FUNCTIONAL_NUMERIC_GUARD_CONTINUATION_ONLY"
    assert value["failed_checks"] == []
    metrics = value["metrics"]
    assert metrics["scan_hidden_max_abs_error"] == pytest.approx(
        3.7550926208496094e-6, rel=0.0, abs=0.0
    )
    assert metrics["eager_hidden_max_abs_error"] == 0.0
    assert metrics["mean_action_max_abs_delta"] == pytest.approx(
        1.6391277313232422e-7, rel=0.0, abs=0.0
    )
    assert metrics["value_max_abs_delta"] == pytest.approx(
        4.76837158203125e-6, rel=0.0, abs=0.0
    )
    assert metrics["log_probability_max_abs_delta"] == pytest.approx(
        7.62939453125e-6, rel=0.0, abs=0.0
    )
    assert metrics["probability_ratio_max_abs_delta"] == pytest.approx(
        7.62939453125e-6, rel=0.0, abs=0.0
    )
    assert metrics["ppo_loss_abs_delta"] == 0.0
    assert value["execution"]["optimizer_updates"] == 0
    assert value["execution"]["formal_support_cells"] == 0
    assert value["execution"]["robot_or_rdk_access"] == 0
    assert value["authority"]["robot_clearance"] is False
