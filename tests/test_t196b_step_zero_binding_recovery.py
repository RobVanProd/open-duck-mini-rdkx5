from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t196b_preregistration_when_present() -> None:
    path = (
        ANALYSIS / "t196b_step_zero_binding_recovery_preregistration.json"
    )
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert (
        value["status"]
        == "PREREGISTERED_T196B_STEP_ZERO_BINDING_RECOVERY"
    )
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert value["execution_now"]["inference_samples"] == 0
    assert value["execution_now"]["behavior_cells"] == 0


def test_t196b_result_when_present() -> None:
    path = ANALYSIS / "t196b_step_zero_binding_recovery_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_T196B_STEP_ZERO_BINDING_RECOVERY"
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert (
        value["decision"]
        == "EARN_T197_T194_NOMINAL_BEHAVIOR_MATRIX_"
        "PREREGISTRATION_ONLY"
    )
    assert value["execution_now"]["inference_samples"] == 0
    assert value["execution_now"]["behavior_cells"] == 0
    assert value["authority"]["behavior_matrix"] is False
    assert value["authority"]["gate5"] is False
