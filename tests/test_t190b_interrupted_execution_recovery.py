from __future__ import annotations

import json
from pathlib import Path


ANALYSIS = Path(__file__).resolve().parents[1] / "outputs" / "analysis"


def test_t190b_preregistration_when_present() -> None:
    path = (
        ANALYSIS / "t190b_interrupted_execution_recovery_preregistration.json"
    )
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PREREGISTERED_T190B_INTERRUPTED_EXECUTION_RECOVERY"
    )
    assert value["failed_checks"] == []
    assert value["interruption"]["completed_behavior_cells"] == 8
    assert value["interruption"]["missing_behavior_cells"] == 8
    assert len(value["completed_blocks"]) == 2
    assert len(value["missing_blocks"]) == 2
    assert value["decision_rule"]["no_completed_cell_retry"] is True
    assert value["authority"]["gate5"] is False


def test_t190b_result_when_present() -> None:
    path = ANALYSIS / "t190b_interrupted_execution_recovery_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    passed = value["status"] == (
        "PASS_T190B_INTERRUPTED_EXECUTION_RECOVERY"
    )
    assert value["status"] in {
        "PASS_T190B_INTERRUPTED_EXECUTION_RECOVERY",
        "HOLD_T190B_INTERRUPTED_EXECUTION_RECOVERY",
    }
    assert value["decision"] == (
        "EARN_T191_T186_FULL_R2_PREREGISTRATION_ONLY"
        if passed
        else "CLOSE_T186_SINGLE_SUPPORT_CONTINUATION"
    )
    assert value["condition"]["condition_green"] is passed
    assert (value["condition"]["green_cells"] == 16) is passed
    assert value["execution"]["behavior_cells_total"] == 16
    assert value["execution"]["behavior_cells_reused"] == 8
    assert value["execution"]["behavior_cells_executed_now"] == 8
    assert value["authority"]["full_r2_preregistration"] is passed
    assert value["authority"]["gate5"] is False
