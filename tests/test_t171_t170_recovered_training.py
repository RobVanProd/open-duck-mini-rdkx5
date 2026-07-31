from __future__ import annotations

import json
from pathlib import Path


ANALYSIS = Path(__file__).resolve().parents[1] / "outputs" / "analysis"


def test_t171_result_when_present() -> None:
    path = ANALYSIS / "t171_t170_recovered_training_validation.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PASS_T171_T170_RECOVERED_TRAINING_VALIDATION"
    )
    assert value["classification"]["actor_update_scope"] == (
        "negative_adapter_location_only"
    )
    assert value["classification"]["body_configuration_strata"] == 8
    assert value["authority"]["behavior_evaluation_authorized"] is False
