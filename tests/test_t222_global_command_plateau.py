from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t222_contract_source() -> None:
    builder = (
        ROOT / "tools/build_t222_global_command_plateau_preregistration.py"
    ).read_text(encoding="utf-8")
    runner = (
        ROOT / "tools/run_t222_global_command_plateau_transform.py"
    ).read_text(encoding="utf-8")
    assert '"cap_m_s": 0.077' in builder
    assert "existing_t149_cap_order" in builder
    assert "no_alternative_cap" in builder
    assert "REWIRED_NODES" in runner
    assert "t222_rebuild_policy_obs" in runner
    assert "all_random_lower_commands_bit_exact" in runner
    assert "transformed_trace_x008_exact_source_x0077" in runner
    assert '"optimizer_steps": 0' in runner
    assert '"behavior_cells": 0' in runner


def test_t222_result_when_present() -> None:
    path = ANALYSIS / "t222_global_command_plateau_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_T222_GLOBAL_COMMAND_PLATEAU"
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert (
        value["decision"]
        == "EARN_T223_GLOBAL_PLATEAU_NOMINAL_MATRIX_"
        "PREREGISTRATION_ONLY"
    )
    assert value["execution"]["simulator_transitions"] == 0
    assert value["execution"]["optimizer_steps"] == 0
    assert value["execution"]["behavior_cells"] == 0
    assert value["authority"]["training"] is False
    assert value["authority"]["gate5"] is False
