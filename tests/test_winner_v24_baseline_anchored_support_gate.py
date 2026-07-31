from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tools/run_winner_v24_baseline_anchored_support_gate.py"


def test_gate_binds_only_half_and_final_without_training() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert 'mapping = {"half": 150, "final": 200}' in source
    assert "snapshot_baseline_anchored_update_" in source
    assert "winner_v24_{label}.onnx" in source
    assert 'reviewed_gate.CHECKPOINTS = (("half", 150), ("final", 200))' in source
    assert "training.adam_step(" not in source
    assert "--formal-gate-authorized" in source
    assert "--hardware-authorized" not in source


def test_gate_reuses_reviewed_physical_evaluator() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "run_winner_v12_calibrator_support_gate" in source
    assert "reviewed_gate.main()" in source
    assert "load_snapshot_for_reviewed_gate" in source
    assert "raw_coordinate_predictor_parameters" in source
    assert "selection_by_closest_result" in source
