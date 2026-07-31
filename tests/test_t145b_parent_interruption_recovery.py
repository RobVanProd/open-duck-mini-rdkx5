from __future__ import annotations

import json
from pathlib import Path


ANALYSIS = Path(__file__).resolve().parents[1] / "outputs" / "analysis"


def test_t145b_preregistration_when_present() -> None:
    path = ANALYSIS / "t145b_parent_interruption_recovery_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["recovery_kind"] == (
        "T145_PARENT_INTERRUPTED_AFTER_TWO_BLOCKS"
    )
    assert value["execution_now"]["source_completed_behavior_cells"] == 8
    assert value["execution_now"]["recovery_remaining_behavior_cells"] == 8


def test_t145b_result_when_present() -> None:
    path = ANALYSIS / "t145b_parent_interruption_recovery_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["execution"]["behavior_cells"] == 16
    assert value["execution"]["source_completed_behavior_cells"] == 8
    assert value["execution"]["recovery_new_behavior_cells"] == 8
    assert value["status"] in {
        "PASS_T145B_CONDITIONAL_PATH_NEGATIVE_ENDPOINT_MATRIX",
        "HOLD_T145B_CONDITIONAL_PATH_NEGATIVE_ENDPOINT_MATRIX",
    }
