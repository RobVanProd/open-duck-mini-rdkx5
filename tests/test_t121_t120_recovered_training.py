from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t121_recovered_training_when_present() -> None:
    path = ANALYSIS / "t121_t120_recovered_training_validation.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] in {
        "PASS_T121_T120_RECOVERED_TRAINING_VALIDATION",
        "HOLD_T121_T120_RECOVERED_TRAINING_VALIDATION",
    }
    assert value["classification"]["behavior_cells"] == 0
    assert value["classification"]["training_retry"] is False
    assert value["classification"]["same_run_resume"] is False
    assert value["authority"]["behavior_evaluation_authorized"] is False
