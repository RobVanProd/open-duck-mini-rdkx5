from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t202b_preregistration_when_present() -> None:
    path = ANALYSIS / "t202b_metric_namespace_recovery_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == "PREREGISTERED_T202B_METRIC_NAMESPACE_RECOVERY"
    assert value["failed_checks"] == []
    assert value["execution_now"]["simulator_transitions"] == 0
    assert value["execution_now"]["optimizer_steps"] == 0
    assert value["authority"]["hosted_training"] is False


def test_t202b_result_when_present() -> None:
    path = ANALYSIS / "t202b_metric_namespace_recovery_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_T202B_METRIC_NAMESPACE_RECOVERY"
    assert (
        value["classification"]
        == "T202_CPU_HOLD_WAS_REPORTING_NAMESPACE_ONLY"
    )
    assert (
        value["decision"]
        == "EARN_T203_PREDICTED_ROLL_RISK_HOSTED_PREREGISTRATION_ONLY"
    )
    assert value["failed_checks"] == []
    assert value["execution"]["simulator_transitions"] == 0
    assert value["execution"]["optimizer_steps"] == 0
    assert value["execution"]["hosted_compute_units"] == 0
    assert value["execution"]["robot_or_rdk_access"] == 0
