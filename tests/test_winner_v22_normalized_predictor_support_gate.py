from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tools/run_winner_v22_normalized_predictor_support_gate.py"


def load():
    spec = importlib.util.spec_from_file_location("winner_v22_support_gate", RUNNER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_checkpoint_paths_are_normalized_predictor_outputs() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "snapshot_normalized_predictor_update_{update:03d}.npz" in source
    assert "winner_v22_{label}.onnx" in source
    assert "snapshot_manifest" in source
    assert "persistent_checkpoints" in source


def test_adapter_preserves_reviewed_gate_with_only_coordinate_projection() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    base = (ROOT / "tools/run_winner_v12_calibrator_support_gate.py").read_text(
        encoding="utf-8"
    )
    assert "run_winner_v12_calibrator_support_gate" in source
    assert "AUTHORIZE_ONE_FROZEN_CORRECTED_COORDINATE_248_CELL_GATE_ONLY" in source
    assert "raw_coordinate_predictor_parameters" in source
    assert "learned_prediction_beats_constant_per_plant" in base
    assert "selection_by_closest_result" in source
    assert "--formal-gate-authorized" in source
    assert "--hardware-authorized" not in source


def test_stage_and_coordinate_aliases_are_in_memory_and_artifacts_read_only() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert 'expected_stage="normalized_predictor_joint_stage2"' in source
    assert 'adapted["metadata"]["stage"] = "stage2"' in source
    assert 'adapted["parameters"] = normalized_support.raw_coordinate_predictor_parameters' in source
    assert ".write_bytes(" not in source


def test_adapter_module_is_dormant_without_gate_files() -> None:
    module = load()
    assert module._TRAINING is None
    assert module.PREREGISTRATION.name == (
        "winner_v22_normalized_predictor_support_gate_preregistration.json"
    )
