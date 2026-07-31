from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t221_contract_source() -> None:
    builder = (
        ROOT
        / "tools/build_t221_t220_command_route_audit_preregistration.py"
    ).read_text(encoding="utf-8")
    runner = (
        ROOT / "tools/run_t221_t220_command_route_audit.py"
    ).read_text(encoding="utf-8")
    assert "candidate_global_cap_m_s" in builder
    assert "all_three_failures_are_x008_only" in builder
    assert "no_alternative_cap" in builder
    assert "route_scores" in runner
    assert "preserved_t149_gate_false_for_y_negative" in runner
    assert "targeted_x0077_retains_external_x008_minimum_ratio" in runner
    assert '"simulator_transitions": 0' in runner
    assert '"behavior_cells": 0' in runner
    assert '"hosted_compute_units": 0' in runner


def test_t221_result_when_present() -> None:
    path = ANALYSIS / "t221_t220_command_route_audit_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_T221_T220_COMMAND_ROUTE_AUDIT"
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert (
        value["decision"]
        == "EARN_T222_GLOBAL_X008_TO_X0077_PLATEAU_"
        "CPU_CONTRACT_PREREGISTRATION_ONLY"
    )
    assert (
        value["classification"]
        == "Y_NEGATIVE_NOMINAL_ROUTE_BYPASSES_T149_CAP_AT_X008"
    )
    assert value["execution"]["simulator_transitions"] == 0
    assert value["execution"]["behavior_cells"] == 0
    assert value["authority"]["training"] is False
    assert value["authority"]["gate5"] is False
