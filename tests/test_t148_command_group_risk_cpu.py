from __future__ import annotations

import json
from pathlib import Path


ANALYSIS = Path(__file__).resolve().parents[1] / "outputs" / "analysis"


def test_t148_preregistration_when_present() -> None:
    path = ANALYSIS / "t148_command_group_risk_cpu_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PREREGISTERED_T148_COMMAND_GROUP_RISK_CPU_CONTRACT"
    )
    assert value["failed_checks"] == []
    assert value["mechanism"]["new_scalar_hyperparameters"] == 0
    assert value["mechanism"]["policy_abi_change"] is False


def test_t148_result_when_present() -> None:
    path = ANALYSIS / "t148_command_group_risk_cpu_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PASS_T148_COMMAND_GROUP_RISK_CPU_CONTRACT"
    )
    assert value["failed_checks"] == []
    assert value["execution"]["optimizer_steps"] == 1024
    assert value["execution"]["hosted_compute_units"] == 0
