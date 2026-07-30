from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t221b_contract_source() -> None:
    builder = (
        ROOT
        / "tools/build_t221b_command_route_verifier_recovery_preregistration.py"
    ).read_text(encoding="utf-8")
    runner = (
        ROOT / "tools/run_t221b_command_route_verifier_recovery.py"
    ).read_text(encoding="utf-8")
    assert "strict float64 JSON versus float32 endpoint equality" in builder
    assert "random states saturated or rate-clipped" in builder
    assert "first_64_contiguous_rows" in builder
    assert "math.isclose" in runner
    assert "same_state_command_sensitivity_exercised_every_pair" in runner
    assert "all_t221_route_and_existing_cap_checks_retained" in runner
    assert '"simulator_transitions": 0' in runner
    assert '"behavior_cells": 0' in runner


def test_t221b_result_when_present() -> None:
    path = ANALYSIS / "t221b_command_route_verifier_recovery_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_T221B_COMMAND_ROUTE_VERIFIER_RECOVERY"
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert (
        value["decision"]
        == "RECOVER_T221_AND_EARN_T222_GLOBAL_X008_TO_X0077_"
        "PLATEAU_CPU_CONTRACT_PREREGISTRATION_ONLY"
    )
    assert (
        value["classification"]
        == "T221_VERIFIER_ONLY_HOLD_RECOVERED_ON_FROZEN_TRACE_STATES"
    )
    assert value["execution"]["simulator_transitions"] == 0
    assert value["execution"]["behavior_cells"] == 0
    assert value["authority"]["training"] is False
    assert value["authority"]["gate5"] is False
