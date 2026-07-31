from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IMPORTER = ROOT / "tools/import_winner_v22_normalized_predictor_two_update_result.py"


def load():
    spec = importlib.util.spec_from_file_location("winner_v22_two_update_import", IMPORTER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_artifact_inventory_binds_result_snapshot_and_graph() -> None:
    module = load()
    assert module.RAW_RESULT.endswith("result.json")
    assert module.RAW_RECEIPT.endswith("result.sha256")
    assert module.SNAPSHOT.endswith("update_002.npz")
    assert module.GRAPH.endswith("update_002.onnx")


def test_importer_has_no_execution_or_hardware_surface() -> None:
    source = IMPORTER.read_text(encoding="utf-8")
    assert "import jax" not in source
    assert "onnxruntime" not in source
    assert "--hardware-authorized" not in source
