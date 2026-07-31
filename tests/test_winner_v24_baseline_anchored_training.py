from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tools/run_winner_v24_baseline_anchored_training.py"


def test_runner_is_one_fixed_100_update_continuation() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "UPDATES = 100" in source
    assert "SOURCE_COMPLETED_UPDATES = 100" in source
    assert "FINAL_COMPLETED_UPDATES = 200" in source
    assert "for local_index in range(UPDATES)" in source
    assert "apply_training_objective" in source
    assert "training.adam_step(" in source
    assert "predictor_scale_sweep" not in source
    assert "--hardware-authorized" not in source


def test_runner_keeps_selection_outside_training() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert '"formal_support_cells": 0' in source
    assert '"locomotion_steps": 0' in source
    assert '"robot_or_rdk_access": 0' in source
    assert "AUTHORIZE_SEPARATE_BASELINE_ANCHORED_SUPPORT_GATE_PREREGISTRATION_ONLY" in source
    assert 'f"winner_v24_{label}.onnx"' in source
    assert '[("half", 150), ("final", 200)]' in source
