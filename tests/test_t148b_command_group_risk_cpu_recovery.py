from __future__ import annotations

import json
from pathlib import Path


ANALYSIS = Path(__file__).resolve().parents[1] / "outputs" / "analysis"


def test_t148b_preregistration_when_present() -> None:
    path = (
        ANALYSIS
        / "t148b_command_group_risk_cpu_recovery_preregistration.json"
    )
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PREREGISTERED_T148B_COMMAND_GROUP_RISK_CPU_RECOVERY"
    )
    assert value["failed_checks"] == []
    assert value["training"]["num_envs"] == 32
    assert value["training"]["batch_size"] == 32
    assert value["decision_rule"]["no_further_cpu_recovery"] is True


def test_t148b_result_when_present() -> None:
    path = (
        ANALYSIS / "t148b_command_group_risk_cpu_recovery_result.json"
    )
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PASS_T148B_COMMAND_GROUP_RISK_CPU_RECOVERY"
    )
    assert value["failed_checks"] == []
    assert value["execution"]["hosted_compute_units"] == 0
