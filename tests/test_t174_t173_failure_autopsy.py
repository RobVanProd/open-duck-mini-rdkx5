from __future__ import annotations

import json
from pathlib import Path


ANALYSIS = Path(__file__).resolve().parents[1] / "outputs" / "analysis"


def test_t174_preregistration_when_present() -> None:
    path = ANALYSIS / "t174_t173_failure_autopsy_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == "PREREGISTERED_T174_T173_FAILURE_AUTOPSY"
    assert value["failed_checks"] == []
    assert len(value["traces"]) == 4
    assert value["authority"]["behavior"] is False
    assert value["authority"]["training"] is False


def test_t174_result_when_present() -> None:
    path = ANALYSIS / "t174_t173_failure_autopsy_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_T174_T173_FAILURE_AUTOPSY"
    assert value["failed_checks"] == []
    assert value["replay"]["all_recorded_outputs_bit_exact"]
    assert value["execution"]["behavior_cells"] == 0
    assert value["authority"]["training"] is False
