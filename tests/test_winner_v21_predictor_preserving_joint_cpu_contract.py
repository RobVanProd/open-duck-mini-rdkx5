from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tools/run_winner_v21_predictor_preserving_joint_cpu_contract.py"
CONTRACT = ROOT / "outputs/analysis/winner_v21_predictor_preserving_joint_cpu_contract.json"
WORKFLOW = ROOT / ".github/workflows/winner-v21-predictor-preserving-joint-cpu-contract.yml"


def load_runner():
    spec = importlib.util.spec_from_file_location("winner_v21_cpu", RUNNER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_contract_freezes_zero_update_one_scale_proof() -> None:
    module = load_runner()
    value = json.loads(CONTRACT.read_text(encoding="utf-8"))
    assert value["status"] == (
        "FROZEN_WINNER_V21_PREDICTOR_PRESERVING_JOINT_CPU_CONTRACT"
    )
    assert value["decision"] == (
        "AUTHORIZE_EXACT_ZERO_UPDATE_GRADIENT_BALANCE_PROOF_ONLY"
    )
    assert value["source_artifact"]["snapshot_sha256"] == module.SNAPSHOT_SHA256
    assert value["source_artifact"]["snapshot_bytes"] == module.SNAPSHOT_BYTES
    assert value["single_change"]["new_parameters"] == 0
    assert value["single_change"]["onnx_abi_change"] is False
    assert value["objective"]["scale_evaluations"] == 1
    assert value["objective"]["scale_sweep"] is False
    assert value["frozen_cpu_proof"]["optimizer_updates"] == 0
    module.validate_source_manifest(value)


def test_runner_has_no_optimizer_behavior_or_hardware_surface() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "jax.value_and_grad" in source
    assert "v21.gradient_balance_scale" in source
    assert "v21.combined_loss" in source
    assert "adam_step" not in source
    assert '"optimizer_updates": 0' in source
    assert '"formal_support_cells": 0' in source
    assert '"locomotion_steps": 0' in source
    assert '"robot_or_rdk_access": 0' in source
    assert "--hardware-authorized" not in source


def test_workflow_is_dormant_and_recovers_exact_stage1_source() -> None:
    source = WORKFLOW.read_text(encoding="utf-8")
    trigger = source.split("permissions:", 1)[0]
    assert "winner_v21_predictor_preserving_joint_cpu_contract.json" in trigger
    assert "8492593761" in source
    assert "8c1392c738eddfb098e61c1a6ae2f863eda883e1eba6ac546aef695da6f163af" in source
    assert "--zero-update-predictor-preserving-contract-authorized" in source
    assert "--hardware-authorized" not in source
