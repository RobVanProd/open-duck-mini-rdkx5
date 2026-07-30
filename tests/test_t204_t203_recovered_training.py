from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t204_validator_contract_source() -> None:
    text = (
        ROOT / "tools/validate_t203_recovered_training.py"
    ).read_text(encoding="utf-8")
    assert "EXPECTED_STEPS = [0, 1_003_520, 2_007_040]" in text
    assert "negative_adapter_location" in text
    assert "t202_predicted_roll_risk" in text
    assert "t202/predicted_roll_risk_rad" in text
    assert "t202/roll_risk_excess_rad" in text
    assert "behavior_evaluation_authorized" in text


def test_t204_result_when_present() -> None:
    path = ANALYSIS / "t204_t203_recovered_training_validation.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert (
        value["status"]
        == "PASS_T204_T203_RECOVERED_TRAINING_VALIDATION"
    )
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert (
        value["decision"]
        == "EARN_T205_T203_POSTEXPORT_COMPOSITION_"
        "PREREGISTRATION_ONLY"
    )
    assert (
        value["classification"]["actor_update_scope"]
        == "negative_adapter_location_only"
    )
    assert value["classification"]["training_retry"] is False
    assert value["classification"]["same_run_resume"] is False
    assert value["classification"]["support_objective"] is False
    assert value["authority"]["behavior_evaluation_authorized"] is False
    assert value["authority"]["gate5_authorized"] is False
