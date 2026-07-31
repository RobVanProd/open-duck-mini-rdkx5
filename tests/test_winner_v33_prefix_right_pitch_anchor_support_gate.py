from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tools/run_winner_v33_prefix_right_pitch_anchor_support_gate.py"


def test_gate_is_the_unchanged_two_checkpoint_reviewed_gate() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert 'reviewed_gate.CHECKPOINTS = (("half", 251), ("final", 301))' in source
    assert "run_winner_v12_calibrator_support_gate" in source
    assert "normalized_support.raw_coordinate_predictor_parameters" in source
    assert "checkpoint_paths" in source
    assert "formal-gate-authorized" in source


def test_gate_has_no_training_or_hardware_path() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "training.adam_step" not in source
    assert "optimizer_updates" not in source
    assert "--hardware-authorized" not in source
    assert '"robot_clearance": False' in source
    assert '"closest_checkpoint_selection": False' in source
