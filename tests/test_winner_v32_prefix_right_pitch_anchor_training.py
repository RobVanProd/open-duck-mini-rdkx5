from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tools/run_winner_v32_prefix_right_pitch_anchor_training.py"


def test_runner_is_one_fixed_100_update_continuation() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "UPDATES = 100" in source
    assert "SOURCE_COMPLETED_UPDATES = 201" in source
    assert "HALF_COMPLETED_UPDATES = 251" in source
    assert "FINAL_COMPLETED_UPDATES = 301" in source
    assert "for local_index in range(UPDATES)" in source
    assert "training.adam_step(" in source
    assert "anchor_scale_sweep" not in source
    assert "predictor_scale_sweep" not in source


def test_runner_uses_the_frozen_anchor_without_action_replacement() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "FROZEN_ANCHOR_SCALE = np.float32(197.3112030029297)" in source
    assert "v29.build_anchor_mask" in source
    assert "v29.prefix_anchor_loss" in source
    assert "v29.compose_gradients(" in source
    assert "teacher_trainable" in source
    assert "teacher_trainable_leaves_unchanged" in source
    assert "action_replacement" not in source


def test_runner_validates_new_source_without_relaxing_v22_teacher() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "def validate_source_snapshot(" in source
    assert "validate_source_snapshot(restored, v21)" in source
    assert 'teacher, expected_stage="normalized_predictor_joint_stage2"' in source
    assert 'update not in {50, 100}' not in source


def test_runner_keeps_selection_and_hardware_outside_training() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert '"formal_support_cells": 0' in source
    assert '"locomotion_steps": 0' in source
    assert '"robot_or_rdk_access": 0' in source
    assert "AUTHORIZE_SEPARATE_PREFIX_RIGHT_PITCH_ANCHOR_SUPPORT_GATE_PREREGISTRATION_ONLY" in source
    assert 'f"winner_v32_{label}.onnx"' in source
    assert '[("half", 251), ("final", 301)]' in source
    assert "--hardware-authorized" not in source
    assert "robot_clearance\": True" not in source
