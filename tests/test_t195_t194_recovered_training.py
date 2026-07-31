from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t195_validator_contract_source() -> None:
    text = (
        ROOT / "tools/validate_t194_recovered_training.py"
    ).read_text(encoding="utf-8")
    assert "EXPECTED_STEPS = [0, 1_003_520, 2_007_040]" in text
    assert "negative_adapter_location" in text
    assert "t193_reference_support_balance" in text
    assert "t193/reference_left_requested" in text
    assert "t193/reference_right_requested" in text
    assert "behavior_evaluation_authorized" in text


def test_t195_result_when_present() -> None:
    path = ANALYSIS / "t195_t194_recovered_training_validation.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert (
        value["status"]
        == "PASS_T195_T194_RECOVERED_TRAINING_VALIDATION"
    )
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert (
        value["decision"]
        == "EARN_T196_T194_POSTEXPORT_COMPOSITION_"
        "PREREGISTRATION_ONLY"
    )
    assert (
        value["classification"]["actor_update_scope"]
        == "negative_adapter_location_only"
    )
    assert value["classification"]["training_retry"] is False
    assert value["classification"]["same_run_resume"] is False
    assert value["authority"]["behavior_evaluation_authorized"] is False
    assert value["authority"]["gate5_authorized"] is False
