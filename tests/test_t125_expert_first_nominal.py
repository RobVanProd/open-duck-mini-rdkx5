from __future__ import annotations

import json
from pathlib import Path


ANALYSIS = Path(__file__).resolve().parents[1] / "outputs" / "analysis"


def test_t125_preregistration_when_present() -> None:
    path = ANALYSIS / "t125_expert_first_nominal_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert (
        value["status"]
        == "PREREGISTERED_T125_EXPERT_FIRST_NOMINAL_SCREEN"
    )
    assert value["matrix"]["cells"] == 16
    assert value["authority"]["training"] is False


def test_t125_result_when_present() -> None:
    path = ANALYSIS / "t125_expert_first_nominal_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    if value["condition"]["green_cells"] == 16:
        assert value["status"] == "PASS_T125_EXPERT_FIRST_NOMINAL_SCREEN"
        assert value["decision"] == (
            "EARN_T126_EXPERT_FIRST_NEGATIVE_ENDPOINT_SCREEN_ONLY"
        )
    else:
        assert value["status"] == "HOLD_T125_EXPERT_FIRST_NOMINAL_SCREEN"
        assert value["decision"] == "CLOSE_EXPERT_FIRST_STAGE_HYPOTHESIS"
