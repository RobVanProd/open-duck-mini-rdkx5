from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tools/run_winner_v13_support_controller_gate.py"


def load():
    spec = importlib.util.spec_from_file_location("winner_v13_support_gate", RUNNER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_checkpoint_paths_are_v13_training_outputs() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "snapshot_stage2_update_{update:03d}.npz" in source
    assert "winner_v13_support_controller_{label}.onnx" in source
    assert "snapshot_manifest" in source
    assert "persistent_checkpoints" in source


def test_adapter_preserves_reviewed_gate_and_has_no_hardware_authority() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "run_winner_v12_calibrator_support_gate" in source
    assert "AUTHORIZE_ONE_FROZEN_248_CELL_GATE_ONLY" in source
    assert "selection_by_closest_result" in source
    assert "--formal-gate-authorized" in source
    assert "--hardware-authorized" not in source


def test_adapter_module_is_dormant_without_result_and_preregistration() -> None:
    module = load()
    assert module._TRAINING is None
    assert module.PREREGISTRATION.name == "winner_v13_support_controller_gate_preregistration.json"
    assert module.TRAINING_RESULT.name == "winner_v13_support_controller_training_result.json"
