from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t114_recovered_training_when_present() -> None:
    path = ANALYSIS / "t114_t113_recovered_training_validation.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    if value["failed_checks"]:
        assert value["status"] == (
            "HOLD_T114_T113_RECOVERED_TRAINING_VALIDATION"
        )
        assert value["decision"] == "NO_BEHAVIOR_EVALUATION"
    else:
        assert value["status"] == (
            "PASS_T114_T113_RECOVERED_TRAINING_VALIDATION"
        )
        assert value["decision"] == (
            "EARN_T115_ALWAYS_ON_TRAINTHROUGH_NOMINAL_PREREGISTRATION_ONLY"
        )
        assert value["classification"]["behavior_cells"] == 0
        assert value["classification"]["actor_update_scope"] == (
            "negative_adapter_location_only"
        )
        assert all(value["checks"].values())
