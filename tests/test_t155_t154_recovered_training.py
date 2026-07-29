from __future__ import annotations

import json
from pathlib import Path


ANALYSIS = Path(__file__).resolve().parents[1] / "outputs" / "analysis"


def test_t155_result_when_present() -> None:
    path = ANALYSIS / "t155_t154_recovered_training_validation.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PASS_T155_T154_RECOVERED_TRAINING_VALIDATION"
    )
    assert value["classification"]["actor_update_scope"] == (
        "negative_adapter_location_only"
    )
    assert value["classification"]["deployment_role"] == (
        "positive_adapter_location"
    )
    assert value["classification"]["exact_torso_com_offset_m"] == [
        0.05,
        0.0,
        0.0,
    ]
    assert value["decision"] == (
        "EARN_T156_POSITIVE_EXPERT_THREE_WAY_ROUTER_"
        "PREREGISTRATION_ONLY"
    )
    assert value["classification"]["body_configuration_strata"] == 1
    assert value["authority"]["behavior_evaluation_authorized"] is False
