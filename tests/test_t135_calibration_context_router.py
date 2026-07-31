from __future__ import annotations

import json
from pathlib import Path


ANALYSIS = Path(__file__).resolve().parents[1] / "outputs" / "analysis"


def test_t135_preregistration_when_present() -> None:
    path = ANALYSIS / "t135_calibration_context_router_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PREREGISTERED_T135_CALIBRATION_CONTEXT_ROUTER_SCREEN"
    )
    assert len(value["expected_context_hashes"]) == 2
    assert value["execution_now"]["formal_behavior_cells"] == 0


def test_t135_result_when_present() -> None:
    path = ANALYSIS / "t135_calibration_context_router_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PASS_T135_CALIBRATION_CONTEXT_ROUTER_SCREEN"
    )
    assert value["classification"] == (
        "STATIC_CALIBRATION_CONTEXT_SEPARATES_COM_ACROSS_FITS"
    )
    assert value["failed_checks"] == []
    assert value["execution"]["formal_behavior_cells"] == 0
