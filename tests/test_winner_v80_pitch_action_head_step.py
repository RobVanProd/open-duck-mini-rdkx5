from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "tools/build_winner_v80_pitch_action_head_step_contract.py"
RUNNER = ROOT / "tools/run_winner_v80_pitch_action_head_step.py"


def load_builder():
    spec = importlib.util.spec_from_file_location("winner_v80_builder_test", BUILDER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_contract_constants_are_exact() -> None:
    builder = load_builder()
    assert builder.PITCH_INDICES == [2, 3, 4, 11, 12, 13]
    assert len(builder.TRAINING_TEACHER_IDS) == 12
    assert "COM_CORNER_07" in builder.TRAINING_TEACHER_IDS
    assert all(not name.startswith("HELDOUT_") for name in builder.TRAINING_TEACHER_IDS)
    assert builder.FRACTIONS == [
        1.0,
        0.5,
        0.25,
        0.125,
        0.0625,
        0.03125,
        0.015625,
        0.0078125,
        0.00390625,
        0.001953125,
        0.0009765625,
    ]


def test_runner_has_only_offline_one_step_authority() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "--offline-cpu-only" in source
    assert "--pitch-action-head-step-authorized" in source
    assert "--hardware-authorized" not in source
    assert "training.adam_step" in source
    assert "action_weight" in source
    assert "action_bias" in source
    assert "PITCH_INDICES" in source
    assert '"optimizer_updates": 1' in source
    assert '"formal_support_cells": 0' in source
    assert '"robot_or_rdk_access": 0' in source
