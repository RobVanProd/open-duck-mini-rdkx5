from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t226_contract_source() -> None:
    builder = (
        ROOT
        / "tools/build_t226_r2_boundary_corner_autopsy_preregistration.py"
    ).read_text(encoding="utf-8")
    runner = (
        ROOT / "tools/run_t226_r2_boundary_corner_autopsy.py"
    ).read_text(encoding="utf-8")
    assert "CLOSE_GLOBAL_COMMAND_PLATEAU_AT_FIRST_FAILED_R2_CONDITION" in builder
    assert "deterministic_endpoint_atoms_in_t216" in builder
    assert "minimum_dynamic_failure_tick" in builder
    assert "forbidden_successor" in builder
    assert "obs_tick_zero_difference_indices" in runner
    assert "only_tick_zero_observation_difference_is_command_x" in runner
    assert "all_eight_final_checkpoint_cells_pass" in runner
    assert '"simulator_transitions": 0' in runner
    assert '"optimizer_steps": 0' in runner
    assert '"behavior_cells": 0' in runner
    assert '"hosted_compute_units": 0' in runner


def test_t226_result_when_present() -> None:
    path = ANALYSIS / "t226_r2_boundary_corner_autopsy_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_T226_R2_BOUNDARY_CORNER_AUTOPSY"
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert (
        value["decision"]
        == "EARN_T227_BOUNDARY_ATOM_TRAINING_CPU_CONTRACT_"
        "PREREGISTRATION_ONLY"
    )
    assert (
        value["classification"]
        == "LOW_COMMAND_UPPER_Z_UNSAMPLED_BOUNDARY_CORNER_WITH_LATE_ABI_FEASIBILITY"
    )
    assert value["training_support"]["deterministic_endpoint_atoms"] == 0
    assert value["training_support"]["policy_abi_change"] is False
    assert value["execution"]["simulator_transitions"] == 0
    assert value["execution"]["optimizer_steps"] == 0
    assert value["execution"]["behavior_cells"] == 0
    assert value["authority"]["training"] is False
    assert value["authority"]["gate5"] is False
