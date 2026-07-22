from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IMPORTER = ROOT / "tools/import_winner_v45_static_target_teacher_one_update_cpu_result_v2.py"
CONTRACT = ROOT / "outputs/analysis/winner_v45_importer_v2_correction_preregistration.json"
RESULT = ROOT / "outputs/analysis/winner_v45_static_target_teacher_one_update_cpu_result.json"


def load():
    spec = importlib.util.spec_from_file_location("winner_v45_import_v2", IMPORTER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_correction_is_minimal_and_exact_when_present() -> None:
    if not CONTRACT.exists():
        return
    module = load()
    value = json.loads(CONTRACT.read_text(encoding="utf-8"))
    module.validate_correction(value)
    assert value["failure"]["artifact_or_proof_invalidated"] is False
    assert value["artifact"]["run_id"] == 29907921832
    assert value["artifact"]["artifact_id"] == 8524663581


def test_v1_validation_is_preserved_and_only_reporting_binding_is_added() -> None:
    source = IMPORTER.read_text(encoding="utf-8")
    assert source.count("v1.validate_result(") == 2
    assert 'before = float(result["optimization"]["teacher_loss_before"])' in source
    assert 'after = float(result["optimization"]["teacher_loss_after"])' in source
    assert "adam_step" not in source
    assert "workflow_dispatch" not in source


def test_imported_result_is_strict_when_present() -> None:
    if not RESULT.exists():
        return
    module = load()
    module.validate_result(json.loads(RESULT.read_text(encoding="utf-8")))
