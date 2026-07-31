from __future__ import annotations

import json
from pathlib import Path


ANALYSIS = Path(__file__).resolve().parents[1] / "outputs" / "analysis"


def test_t134_preregistration_when_present() -> None:
    path = ANALYSIS / "t134_t129_nominal_gate_attribution_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PREREGISTERED_T134_T129_NOMINAL_GATE_ATTRIBUTION"
    )
    assert value["execution_now"]["simulator_steps"] == 0
    assert value["authority"]["training"] is False


def test_t134_result_when_present() -> None:
    path = ANALYSIS / "t134_t129_nominal_gate_attribution_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PASS_T134_T129_NOMINAL_GATE_ATTRIBUTION"
    )
    assert value["classification"] == (
        "DYNAMIC_GATE_FALSE_POSITIVE_EXPOSES_NEGATIVE_EXPERT"
    )
    assert value["failed_checks"] == []
    assert value["execution"]["simulator_steps"] == 0
