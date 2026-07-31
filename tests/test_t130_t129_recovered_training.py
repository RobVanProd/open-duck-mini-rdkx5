from __future__ import annotations

import json
from pathlib import Path


ANALYSIS = Path(__file__).resolve().parents[1] / "outputs" / "analysis"


def test_t130_result_when_present() -> None:
    path = ANALYSIS / "t130_t129_recovered_training_validation.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PASS_T130_T129_RECOVERED_TRAINING_VALIDATION"
    )
    assert value["classification"]["actor_update_scope"] == (
        "negative_adapter_location_only"
    )
    assert value["classification"]["body_configuration_strata"] == 1
    assert value["authority"]["behavior_evaluation_authorized"] is False
