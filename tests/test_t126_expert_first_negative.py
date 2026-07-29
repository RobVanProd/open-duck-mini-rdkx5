from __future__ import annotations

import json
from pathlib import Path


ANALYSIS = Path(__file__).resolve().parents[1] / "outputs" / "analysis"


def test_t126_preregistration_when_present() -> None:
    path = ANALYSIS / "t126_expert_first_negative_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert (
        value["status"]
        == "PREREGISTERED_T126_EXPERT_FIRST_NEGATIVE_SCREEN"
    )
    assert value["condition"]["id"] == "TORSO_COM_X_NEG"
    assert value["matrix"]["cells"] == 16
    assert value["authority"]["training"] is False


def test_t126_result_when_present() -> None:
    path = ANALYSIS / "t126_expert_first_negative_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    if value["condition"]["green_cells"] == 16:
        assert value["status"] == "PASS_T126_EXPERT_FIRST_NEGATIVE_SCREEN"
        assert value["decision"] == (
            "EARN_T127_EXPERT_FIRST_STAGED_TRAINING_CPU_CONTRACT_ONLY"
        )
    else:
        assert value["status"] == "HOLD_T126_EXPERT_FIRST_NEGATIVE_SCREEN"
        assert value["decision"] == "CLOSE_EXPERT_FIRST_STAGE_HYPOTHESIS"
