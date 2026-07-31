from __future__ import annotations

import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
PREREG = (
    ROOT
    / "outputs"
    / "analysis"
    / "t55b_dynamic_single_support_cpu_recovery_preregistration.json"
)


def test_t55b_is_exact_cpu_only_recovery() -> None:
    if not PREREG.exists():
        pytest.skip("T55B CPU recovery has not been preregistered")
    value = json.loads(PREREG.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PREREGISTERED_T55B_DYNAMIC_SINGLE_SUPPORT_CPU_RECOVERY"
    )
    assert value["failed_checks"] == []
    assert value["preexecution_hold"]["optimizer_steps"] == 0
    assert value["preexecution_hold"]["behavior_cells"] == 0
    assert value["preexecution_hold"]["policy_decision_weight"] == 0
    assert value["recovery"]["one_attempt"]
    assert not value["recovery"]["retry_or_tuning"]
    assert value["cpu_contract"]["balance_simulator_steps"] == 1024
    assert value["cpu_contract"]["transfer_simulator_steps"] == 1024
    assert value["authority"]["execute_one_2048_step_cpu_recovery"]
    assert not value["authority"]["hosted_training"]
    assert not value["authority"]["gate5"]
