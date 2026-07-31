from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t97_preregistration_contract() -> None:
    path = ANALYSIS / "t97_hidden_gate_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == "PREREGISTERED_T97_HIDDEN_GATE_FALSIFIER"
    assert value["failed_checks"] == []
    assert value["population"]["sample_count"] == 72
    assert value["population"]["ticks"] == [8, 16, 32]
    assert value["execution_now"] == {
        "optimizer_steps": 0,
        "simulator_steps": 0,
        "hosted_compute_units": 0,
        "robot_or_rdk_access": 0,
    }


def test_t97_result_is_read_only_and_decisive() -> None:
    path = ANALYSIS / "t97_hidden_gate_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] in {
        "PASS_T97_HIDDEN_GATE_FALSIFIER",
        "HOLD_T97_HIDDEN_GATE_FALSIFIER",
    }
    assert value["execution"]["trace_rows_read"] == 72
    assert value["execution"]["optimizer_steps"] == 0
    assert value["execution"]["simulator_steps"] == 0
    assert value["execution"]["hosted_compute_units"] == 0
    assert value["execution"]["robot_or_rdk_access"] == 0
    assert set(value["families"]) == {
        "checkpoint",
        "fit",
        "command",
        "exact_group",
    }
