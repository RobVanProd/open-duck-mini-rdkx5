from __future__ import annotations

import json
from pathlib import Path


ANALYSIS = Path(__file__).resolve().parents[1] / "outputs" / "analysis"


def test_t127_preregistration_when_present() -> None:
    path = ANALYSIS / "t127_negative_expert_interference_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert (
        value["status"]
        == "PREREGISTERED_T127_NEGATIVE_EXPERT_INTERFERENCE_AUDIT"
    )
    assert value["authority"]["training"] is False


def test_t127_result_when_present() -> None:
    path = ANALYSIS / "t127_negative_expert_interference_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_T127_NEGATIVE_EXPERT_INTERFERENCE_AUDIT"
    assert value["decision"] == (
        "EARN_T128_NEGATIVE_ONLY_LINEAR_EXPERT_CPU_PREREGISTRATION_ONLY"
    )
    assert value["execution"]["optimizer_steps"] == 0
