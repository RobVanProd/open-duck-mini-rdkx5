from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tools/run_winner_v20_joint_recurrent_support_cpu_contract.py"
CONTRACT = ROOT / "outputs/analysis/winner_v20_joint_recurrent_support_cpu_contract.json"
WORKFLOW = ROOT / ".github/workflows/winner-v20-joint-recurrent-support-cpu-contract.yml"


def load_runner():
    spec = importlib.util.spec_from_file_location("winner_v20_cpu", RUNNER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_contract_freezes_one_existing_abi_causal_change() -> None:
    module = load_runner()
    value = json.loads(CONTRACT.read_text(encoding="utf-8"))
    assert value["status"] == (
        "FROZEN_WINNER_V20_JOINT_RECURRENT_SUPPORT_CPU_CONTRACT"
    )
    assert value["decision"] == (
        "AUTHORIZE_ONE_JOINT_RECURRENT_PPO_PROOF_UPDATE_ONLY"
    )
    assert value["source_artifact"]["snapshot_sha256"] == module.SNAPSHOT_SHA256
    assert value["source_artifact"]["snapshot_bytes"] == module.SNAPSHOT_BYTES
    assert value["single_change"]["new_parameters"] == 0
    assert value["single_change"]["onnx_abi_change"] is False
    assert value["single_change"]["reward_change_from_winner_v15"] is False
    module.validate_source_manifest(value)


def test_runner_is_one_cpu_update_with_no_behavior_or_hardware_gate() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "jax.value_and_grad" in source
    assert "v20.joint_recurrent_ppo_loss" in source
    assert "v15.stage2_rollout" in source
    assert "v20.stage2_rollout" in source
    assert '"optimizer_updates": 1' in source
    assert '"formal_support_cells": 0' in source
    assert '"locomotion_steps": 0' in source
    assert '"robot_or_rdk_access": 0' in source
    assert "for update_index in range" not in source
    assert "--hardware-authorized" not in source


def test_workflow_is_dormant_and_recovers_the_exact_source() -> None:
    source = WORKFLOW.read_text(encoding="utf-8")
    trigger = source.split("permissions:", 1)[0]
    assert "winner_v20_joint_recurrent_support_cpu_contract.json" in trigger
    assert "8492593761" in source
    assert "8c1392c738eddfb098e61c1a6ae2f863eda883e1eba6ac546aef695da6f163af" in source
    assert "--one-update-joint-recurrent-contract-authorized" in source
    assert "--hardware-authorized" not in source
