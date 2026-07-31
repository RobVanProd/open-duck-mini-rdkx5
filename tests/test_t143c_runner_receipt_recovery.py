from __future__ import annotations

import json
from pathlib import Path


ANALYSIS = Path(__file__).resolve().parents[1] / "outputs" / "analysis"


def test_t143c_preregistration_when_present() -> None:
    path = ANALYSIS / "t143c_runner_receipt_recovery_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["recovery_kind"] == (
        "T143B_OBSOLETE_PRIMARY_RUNNER_RECEIPT"
    )
    assert value["execution_now"]["prior_attempt_transforms"] == 0


def test_t143c_result_when_present() -> None:
    path = ANALYSIS / "t143c_runner_receipt_recovery_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PASS_T143C_CONDITIONAL_FORWARD_PATH_TRANSFORM"
    )
    assert value["failed_checks"] == []
    assert value["execution"]["formal_behavior_cells"] == 0
