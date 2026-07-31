from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import jax
import jax.numpy as jnp
import numpy as np
import pytest


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "tools/build_winner_v50_full_action_teacher_source_gradient_contract.py"
RUNNER = ROOT / "tools/run_winner_v50_full_action_teacher_source_gradient_contract.py"
CONTRACT = ROOT / "outputs/analysis/winner_v50_full_action_teacher_source_gradient_contract.json"
RESULT = ROOT / "outputs/analysis/winner_v50_full_action_teacher_source_gradient_result.json"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_full_training_mask_preserves_pitch_and_adds_nonpitch() -> None:
    runner = load(RUNNER, "winner_v50_mask")
    identifiers = [name for name in runner.TRAINING_TEACHER_IDS for _ in range(2)]
    previous = np.zeros((22, 3, 14), dtype=np.float32)
    valid = np.ones((22, 3), dtype=np.float32)
    table = {
        name: np.zeros((14,), dtype=np.float32)
        for name in runner.v43.CONFIGURATION_IDS
    }
    raw, bounded, mask = runner.build_full_training_teacher_batch(
        identifiers, previous, valid, table, jax, jnp
    )
    assert np.asarray(raw).shape == np.asarray(bounded).shape == (22, 3, 14)
    assert np.array_equal(np.asarray(mask), np.ones((22, 3, 14), dtype=np.float32))


def test_builder_selects_terminal_v46_optimizer_state_not_deployment() -> None:
    builder = load(BUILDER, "winner_v50_builder")
    v46 = json.loads(builder.V46_RESULT.read_text(encoding="utf-8"))
    final = next(row for row in v46["persistent_checkpoints"] if row["label"] == "final")
    assert final["completed_updates"] == 352
    assert final["snapshot"]["sha256"] == (
        "e32a7d5ee7fa272639fb58a2b500e394d983d4a984fb1ace1f7d87058c86e0df"
    )


def test_generated_contract_is_exact_and_source_bound_when_present() -> None:
    if not CONTRACT.exists():
        return
    runner = load(RUNNER, "winner_v50_generated")
    value = json.loads(CONTRACT.read_text(encoding="utf-8"))
    runner.validate_contract(value)
    assert value["source_selection"]["selected_update"] == 352
    assert value["source_selection"]["deployment_checkpoint_selected"] is False
    assert value["objective"]["new_supervised_indices"] == list(range(14))
    assert value["authority"]["one_update_authorized"] is False


def test_result_remains_zero_update_when_present() -> None:
    if not RESULT.exists():
        return
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["status"] in {
        "PASS_WINNER_V50_FULL_ACTION_TEACHER_SOURCE_GRADIENT_CPU_PROOF",
        "HOLD_WINNER_V50_FULL_ACTION_TEACHER_SOURCE_GRADIENT_CPU_PROOF",
    }
    assert value["execution"]["optimizer_updates"] == 0
    assert value["execution"]["formal_support_cells"] == 0
    assert value["authority"]["one_update_authorized"] is False


def test_runner_requires_explicit_cpu_authority(monkeypatch, tmp_path: Path) -> None:
    runner = load(RUNNER, "winner_v50_authority")
    monkeypatch.setattr(
        "sys.argv",
        [
            str(RUNNER),
            "--playground-root", str(tmp_path),
            "--canonical-fit", str(tmp_path / "fit.json"),
            "--v46-training-work-root", str(tmp_path),
            "--v22-training-work-root", str(tmp_path),
            "--output", str(tmp_path / "out.json"),
        ],
    )
    with pytest.raises(PermissionError, match="requires --offline-cpu-only"):
        runner.main()


def test_runner_has_no_optimizer_export_or_hardware_operation() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "adam_step(" not in source
    assert "export_" not in source
    assert "--hardware-authorized" not in source
    assert '"optimizer_updates": 0' in source
    assert '"formal_support_cells": 0' in source
    assert '"robot_or_rdk_access": 0' in source
