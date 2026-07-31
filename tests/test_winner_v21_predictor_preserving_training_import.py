from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IMPORTER = ROOT / "tools/import_winner_v21_predictor_preserving_training.py"
RESULT = ROOT / "outputs/analysis/winner_v21_predictor_preserving_training_result.json"


def load():
    spec = importlib.util.spec_from_file_location("winner_v21_training_import", IMPORTER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_artifact_inventory_is_exact() -> None:
    module = load()
    members = module.artifact_members()
    assert len(members) == 104
    assert module.RAW_RESULT in members
    assert module.RAW_RECEIPT in members
    assert f"{module.WORK_PREFIX}/graphs/winner_v21_half.onnx" in members
    assert f"{module.WORK_PREFIX}/graphs/winner_v21_final.onnx" in members


def test_imported_result_is_strict_when_present() -> None:
    if not RESULT.exists():
        return
    module = load()
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    module.validate_result(value)
    assert value["repository_attribution"]["github_run_attempt"] == 1


def test_importer_has_no_execution_or_hardware_authority() -> None:
    source = IMPORTER.read_text(encoding="utf-8")
    assert "import jax" not in source
    assert "onnxruntime" not in source
    assert "--hardware-authorized" not in source
