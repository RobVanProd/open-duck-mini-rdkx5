from __future__ import annotations

import json
from pathlib import Path


ANALYSIS = Path(__file__).resolve().parents[1] / "outputs" / "analysis"


def test_t146c_preregistration_when_present() -> None:
    path = ANALYSIS / "t146c_test_receipt_recovery_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["recovery_kind"] == "T146B_OBSOLETE_BASE_TEST_RECEIPT"
    assert value["execution_now"]["t146b_trace_rows_read"] == 0


def test_t146c_result_when_present() -> None:
    path = ANALYSIS / "t146c_test_receipt_recovery_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_T146C_UPPER_COMMAND_ATTRIBUTION"
    assert value["classification"] == (
        "SUSTAINED_UPPER_COMMAND_POLICY_COLLAPSE_NOT_HANDOFF"
    )
    assert value["failed_checks"] == []
    assert value["execution"]["new_behavior_cells"] == 0
