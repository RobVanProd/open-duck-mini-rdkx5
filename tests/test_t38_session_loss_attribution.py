from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def load(name: str) -> dict:
    return json.loads((ANALYSIS / name).read_text(encoding="utf-8"))


def test_t38_session_loss_has_zero_policy_weight_and_no_retry() -> None:
    payload = load("t38_unrecoverable_session_loss_attribution.json")
    assert (
        payload["status"]
        == "PASS_T38_UNRECOVERABLE_SESSION_LOSS_ATTRIBUTION"
    )
    assert payload["decision"] == (
        "CLOSE_T38_ZERO_WEIGHT_NO_RETRY_"
        "EARN_T39_UNIFORM_NORMALIZER_ROLLBACK_PREREGISTRATION"
    )
    assert payload["failed_checks"] == []
    assert payload["checks"]["executor_returned_system_exit_zero"]
    assert payload["checks"]["session_terminated_pruned"]
    assert payload["checks"]["expected_outputs_absent_locally"]
    assert payload["classification"]["training_completion"] == (
        "indicated_but_unverifiable"
    )
    assert payload["classification"]["optimizer_steps"] is None
    assert payload["classification"]["policy_decision_weight"] == 0
    assert not payload["classification"]["policy_pass"]
    assert not payload["classification"]["policy_failure"]
    assert not payload["classification"]["hosted_retry"]
    assert payload["authority"][
        "t39_uniform_normalizer_rollback_preregistration"
    ]
    assert not payload["authority"]["t39_behavior_evaluation"]
    assert not payload["authority"]["additional_hosted_training"]
    assert not payload["authority"]["gate5"]
    assert not payload["authority"]["rdkx5_or_robot"]
