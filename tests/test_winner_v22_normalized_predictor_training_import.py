from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IMPORTER = ROOT / "tools/import_winner_v22_normalized_predictor_training.py"


def load():
    spec = importlib.util.spec_from_file_location("winner_v22_training_import", IMPORTER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_artifact_inventory_contains_100_snapshots_and_two_graphs() -> None:
    module = load()
    members = module.artifact_members()
    assert len(members) == 104
    assert sum(name.endswith(".npz") for name in members) == 100
    assert sum(name.endswith(".onnx") for name in members) == 2


def test_importer_has_no_training_or_hardware_surface() -> None:
    source = IMPORTER.read_text(encoding="utf-8")
    assert "import jax" not in source
    assert "onnxruntime" not in source
    assert "--hardware-authorized" not in source
