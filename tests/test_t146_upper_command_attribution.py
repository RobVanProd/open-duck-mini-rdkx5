from __future__ import annotations

import json
from pathlib import Path


ANALYSIS = Path(__file__).resolve().parents[1] / "outputs" / "analysis"


def test_t146_preregistration_when_present() -> None:
    path = ANALYSIS / "t146_upper_command_attribution_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == "PREREGISTERED_T146_UPPER_COMMAND_ATTRIBUTION"
    assert len(value["traces"]) == 16
    assert value["execution_now"]["new_behavior_cells"] == 0


def test_t146_result_when_present() -> None:
    path = ANALYSIS / "t146_upper_command_attribution_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_T146_UPPER_COMMAND_ATTRIBUTION"
    assert value["classification"] == (
        "SUSTAINED_UPPER_COMMAND_POLICY_COLLAPSE_NOT_HANDOFF"
    )
    assert value["failure_summary"]["failing_cells"] == 8
    assert value["execution"]["new_behavior_cells"] == 0
