from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t217_validator_contract_source() -> None:
    text = (
        ROOT / "tools/validate_t216_recovered_training.py"
    ).read_text(encoding="utf-8")
    assert "EXPECTED_STEPS = [0, 1_003_520, 2_007_040]" in text
    assert "negative_adapter_location" in text
    assert "step_zero_cost_tree_reproducible_bit_exact" in text
    assert "dual_initialized_from_derived_cost_and_monotone" in text
    assert "1.0 / (" in text
    assert "eval/episode_cost/t215b_predicted_tilt_box" in text
    assert "eval/episode_t215b/predicted_pitch_risk_rad" in text
    assert "eval/episode_t215b/predicted_roll_risk_rad" in text
    assert "behavior_evaluation_authorized" in text


def test_t217_result_when_present() -> None:
    path = ANALYSIS / "t217_t216_recovered_training_validation.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    if (
        value["status"]
        == "HOLD_T217_T216_RECOVERED_TRAINING_VALIDATION"
    ):
        assert value["failed_checks"] == [
            "step_zero_cost_tree_reproducible_bit_exact"
        ]
        assert all(
            passed
            for name, passed in value["checks"].items()
            if name != "step_zero_cost_tree_reproducible_bit_exact"
        )
        assert value["decision"] == "NO_BEHAVIOR_EVALUATION"
        assert value["authority"]["behavior_evaluation_authorized"] is False
        assert value["authority"]["gate5_authorized"] is False
        return
    assert (
        value["status"]
        == "PASS_T217_T216_RECOVERED_TRAINING_VALIDATION"
    )
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert (
        value["decision"]
        == "EARN_T218_T216_POSTEXPORT_COMPOSITION_PREREGISTRATION_ONLY"
    )
    assert (
        value["classification"]["actor_update_scope"]
        == "negative_adapter_location_only"
    )
    assert value["classification"]["training_retry"] is False
    assert value["classification"]["same_run_resume"] is False
    assert value["classification"]["cost_critic"] == "separate_updated"
    assert value["classification"]["deployment_graph_change"] is False
    assert value["authority"]["behavior_evaluation_authorized"] is False
    assert value["authority"]["gate5_authorized"] is False
