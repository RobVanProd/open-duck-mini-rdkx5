from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tools/run_winner_v13_support_controller_cpu_contract.py"
CONTRACT = ROOT / "outputs/analysis/winner_v13_support_controller_cpu_contract.json"


def load():
    spec = importlib.util.spec_from_file_location("winner_v13_support_cpu", RUNNER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_contract_restores_exact_passing_stage1_snapshot() -> None:
    module = load()
    value = json.loads(CONTRACT.read_text(encoding="utf-8"))
    assert value["status"] == "FROZEN_WINNER_V13_SUPPORT_CONTROLLER_CPU_CONTRACT"
    assert value["decision"] == "AUTHORIZE_ONE_RESTORED_STAGE2_UPDATE_ONLY"
    assert value["source_artifact"]["snapshot_sha256"] == module.SNAPSHOT_SHA256
    assert value["source_artifact"]["snapshot_bytes"] == module.SNAPSHOT_BYTES
    module.validate_source_manifest(value)


def test_runner_is_exactly_one_stage2_update_and_no_hardware() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "full.stage2_rollout" in source
    assert "jax.value_and_grad" in source
    assert "training.adam_step" in source
    assert '"stage2_optimizer_updates": 1' in source
    assert '"formal_support_cells": 0' in source
    assert '"locomotion_steps": 0' in source
    assert '"robot_or_rdk_access": 0' in source
    assert "for update_index in range" not in source
    assert "--hardware-authorized" not in source


def test_workflow_is_dormant_until_contract_commit() -> None:
    workflow = ROOT / ".github/workflows/winner-v13-support-controller-cpu-contract.yml"
    source = workflow.read_text(encoding="utf-8")
    trigger = source.split("permissions:", 1)[0]
    assert "winner_v13_support_controller_cpu_contract.json" in trigger
    assert "8492593761" in source
    assert "8c1392c738eddfb098e61c1a6ae2f863eda883e1eba6ac546aef695da6f163af" in source
    assert "--one-update-support-contract-authorized" in source
    assert "--hardware-authorized" not in source
