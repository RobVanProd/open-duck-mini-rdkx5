from __future__ import annotations

import json
from pathlib import Path


ANALYSIS = Path(__file__).resolve().parents[1] / "outputs" / "analysis"


def test_t131_preregistration_when_present() -> None:
    path = ANALYSIS / "t131_t129_postexport_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PREREGISTERED_T131_T129_HARD_GATE_POSTEXPORT_TRANSFORM"
    )
    assert value["frozen_chain"][0] == "restore_t98_hard_hidden_gate"


def test_t131_result_when_present() -> None:
    path = ANALYSIS / "t131_t129_postexport_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PASS_T131_T129_HARD_GATE_POSTEXPORT_TRANSFORM"
    )
    assert value["checks"]["step_zero_hard_gate_byte_exact"]
    assert value["execution"]["formal_behavior_cells"] == 0
