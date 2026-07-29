from __future__ import annotations

import json
from pathlib import Path


ANALYSIS = Path(__file__).resolve().parents[1] / "outputs" / "analysis"


def test_t146b_preregistration_when_present() -> None:
    path = ANALYSIS / "t146b_pre_action_field_recovery_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["recovery_kind"] == (
        "T146_POST_ACTION_FIELDS_USED_FOR_HANDOFF"
    )
    assert value["execution_now"]["new_behavior_cells"] == 0


def test_t146b_result_when_present() -> None:
    path = ANALYSIS / "t146b_pre_action_field_recovery_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_T146B_UPPER_COMMAND_ATTRIBUTION"
    assert value["classification"] == (
        "SUSTAINED_UPPER_COMMAND_POLICY_COLLAPSE_NOT_HANDOFF"
    )
    assert value["failed_checks"] == []
    assert value["execution"]["new_behavior_cells"] == 0
