from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "tools/build_winner_v13_normalized_response_cpu_contract.py"
RUNNER = ROOT / "tools/run_winner_v13_normalized_response_cpu_contract.py"
PRIMITIVES = ROOT / "patches/winner_v13_normalized_calibrator_training.py"
CONTRACT = ROOT / "outputs/analysis/winner_v13_normalized_response_cpu_contract.json"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_evidence_selects_normalized_response_without_advancement() -> None:
    builder = load(BUILDER, "winner_v13_cpu_builder")
    diagnostic = json.loads(builder.DIAGNOSTIC.read_text(encoding="utf-8"))
    builder.validate_selected_evidence(diagnostic)
    assert diagnostic["findings"] == {
        "all_formal_failed_pairs_pass_with_zero_action": False,
        "contact_floor_dominates_all_predictor_aggregates": True,
        "graph_fail_zero_fail_count": 20,
        "graph_fail_zero_pass_count": 10,
        "noncontact_predictor_beats_constant_all_aggregates": False,
    }


def test_training_primitive_predicts_in_normalized_coordinates() -> None:
    source = PRIMITIVES.read_text(encoding="utf-8")
    assert "normalized_prediction" in source
    assert "target = normalized_target" in source
    assert "jnp.square(prediction - target)" in source
    assert "prediction_normalized = (predictions - target_mean)" not in source
    assert "deployable_parameters = v12.deployable_parameters" in source


def test_generated_contract_is_zero_cell_and_source_bound() -> None:
    runner = load(RUNNER, "winner_v13_cpu_runner")
    value = json.loads(CONTRACT.read_text(encoding="utf-8"))
    assert value["status"] == "FROZEN_WINNER_V13_NORMALIZED_RESPONSE_CPU_CONTRACT"
    assert value["decision"] == "AUTHORIZE_ONE_ZERO_CELL_CPU_UPDATE_ONLY"
    assert value["execution_now"] == {
        "cpu_contract_optimizer_updates": 0,
        "full_training_updates": 0,
        "formal_support_cells": 0,
        "locomotion_steps": 0,
        "robot_or_rdk_access": 0,
    }
    assert value["authority"]["robot_clearance"] is False
    assert len(value["frozen_cpu_proof"]["required_checks"]) == 15
    runner.validate_source_manifest(value)


def test_runner_has_one_update_and_no_full_training_path() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "optimizer_after" in source
    assert '"cpu_contract_optimizer_updates": 1' in source
    assert '"full_training_updates": 0' in source
    assert "for update_index in range" not in source
    assert "--zero-cell-contract-authorized" in source
    assert "--hardware-authorized" not in source


def test_workflow_is_dormant_until_contract_commit() -> None:
    workflow = (
        ROOT / ".github/workflows/winner-v13-normalized-response-cpu-contract.yml"
    )
    source = workflow.read_text(encoding="utf-8")
    trigger = source.split("permissions:", 1)[0]
    assert "winner_v13_normalized_response_cpu_contract.json" in trigger
    assert "--offline-cpu-only" in source
    assert "--zero-cell-contract-authorized" in source
    assert "--hardware-authorized" not in source

