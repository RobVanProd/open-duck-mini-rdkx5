from __future__ import annotations

import json
from pathlib import Path


ANALYSIS = Path(__file__).resolve().parents[1] / "outputs" / "analysis"


def test_t135b_preregistration_when_present() -> None:
    path = (
        ANALYSIS
        / "t135b_interrupted_calibration_context_router_recovery_"
        "preregistration.json"
    )
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PREREGISTERED_T135B_INTERRUPTED_CALIBRATION_CONTEXT_"
        "ROUTER_RECOVERY"
    )
    assert len(value["remaining_prefixes"]) == 3
    assert value["execution_now"]["formal_behavior_cells"] == 0


def test_t135b_result_when_present() -> None:
    path = (
        ANALYSIS
        / "t135b_interrupted_calibration_context_router_recovery_result.json"
    )
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PASS_T135B_INTERRUPTED_CALIBRATION_CONTEXT_ROUTER_RECOVERY"
    )
    assert value["failed_checks"] == []
    assert value["execution"]["cached_calibration_prefixes"] == 1
    assert value["execution"]["new_calibration_prefixes"] == 3
    assert value["execution"]["formal_behavior_cells"] == 0
