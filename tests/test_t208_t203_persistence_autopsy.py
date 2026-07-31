from __future__ import annotations

import json
from pathlib import Path


ANALYSIS = Path(__file__).resolve().parents[1] / "outputs" / "analysis"


def test_t208_preregistration_when_present() -> None:
    path = ANALYSIS / "t208_t203_persistence_autopsy_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert (
        value["status"]
        == "PREREGISTERED_T208_T203_PERSISTENCE_AUTOPSY"
    )
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert len(value["traces"]) == 16
    assert value["execution_now"]["behavior_cells"] == 0
    assert value["authority"]["training"] is False
    assert value["authority"]["gate5"] is False


def test_t208_result_when_present() -> None:
    path = ANALYSIS / "t208_t203_persistence_autopsy_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_T208_T203_PERSISTENCE_AUTOPSY"
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert value["execution"]["behavior_cells"] == 0
    assert value["execution"]["optimizer_steps"] == 0
    assert value["authority"]["behavior"] is False
    assert value["authority"]["training"] is False
    assert value["authority"]["gate5"] is False
