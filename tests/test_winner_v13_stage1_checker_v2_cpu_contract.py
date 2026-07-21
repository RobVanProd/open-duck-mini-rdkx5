from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tools/run_winner_v13_stage1_checker_v2_cpu_contract.py"
CONTRACT = ROOT / "outputs/analysis/winner_v13_stage1_checker_v2_cpu_contract.json"


def load():
    spec = importlib.util.spec_from_file_location("winner_v13_checker_v2", RUNNER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_contract_is_zero_cell_and_source_bound() -> None:
    module = load()
    value = json.loads(CONTRACT.read_text(encoding="utf-8"))
    assert value["schema_version"] == "winner_v13.stage1_checker_v2_cpu_contract.v2"
    assert value["status"] == "FROZEN_WINNER_V13_STAGE1_CHECKER_V2_CPU_CONTRACT"
    assert value["decision"] == "AUTHORIZE_ONE_ZERO_CELL_CHECKER_PROOF_ONLY"
    assert value["execution_now"] == {
        "optimizer_updates": 0,
        "simulation_cells": 0,
        "formal_support_cells": 0,
        "locomotion_steps": 0,
        "robot_or_rdk_access": 0,
    }
    module.validate_source_manifest(value)


def test_runner_uses_same_input_reference_and_no_training() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "networks.calibrator_step" in source
    assert "previous_action" in source
    assert "hidden_inputs" in source
    assert "maximum_errors[2] <= 1.0e-7" in source
    assert "bool(maximum_errors[1] <= 1.0e-7)" in source
    assert "v13.STAGE1_LEARNING_RATE == 0.0001" in source
    assert '"optimizer_updates": 0' in source
    assert "adam_step" not in source
    assert "--hardware-authorized" not in source


def test_workflow_is_dormant_until_contract_commit() -> None:
    workflow = ROOT / ".github/workflows/winner-v13-stage1-checker-v2-cpu-contract.yml"
    source = workflow.read_text(encoding="utf-8")
    trigger = source.split("permissions:", 1)[0]
    assert "winner_v13_stage1_checker_v2_cpu_contract.json" in trigger
    assert "--zero-cell-checker-contract-authorized" in source
    assert "--offline-cpu-only" in source
    assert "--hardware-authorized" not in source
