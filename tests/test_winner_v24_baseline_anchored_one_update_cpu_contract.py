from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tools/run_winner_v24_baseline_anchored_one_update_cpu_proof.py"


def test_runner_executes_exactly_one_offline_update() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "ROLLOUT_UPDATE_INDEX = 100" in source
    assert "apply_baseline_anchored_objective" in source
    assert "training.adam_step(" in source
    assert '"optimizer_updates": 1' in source
    assert "range(2)" not in source
    assert "range(100)" not in source
    assert '"formal_support_cells": 0' in source
    assert '"robot_or_rdk_access": 0' in source
    assert "--hardware-authorized" not in source


def test_runner_proves_snapshot_and_onnx_contracts() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "save_snapshot(" in source
    assert "snapshot_readback_exact" in source
    assert "onnx_abi_exact" in source
    assert "onnx_previous_action_chain_exact" in source
    assert "all_12_trainable_leaves_changed" in source
