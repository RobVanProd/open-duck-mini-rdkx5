from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IMPORTER = ROOT / "tools/import_winner_v46_static_target_teacher_training.py"
RESULT = ROOT / "outputs/analysis/winner_v46_static_target_teacher_training_result.json"


def load():
    spec = importlib.util.spec_from_file_location("winner_v46_import", IMPORTER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_artifact_inventory_is_exact() -> None:
    module = load()
    names = module.artifact_members()
    assert len(names) == 104
    assert f"{module.WORK}/snapshots/snapshot_static_target_teacher_update_253.npz" in names
    assert f"{module.WORK}/snapshots/snapshot_static_target_teacher_update_352.npz" in names


def test_imported_result_is_strict_when_present() -> None:
    if not RESULT.exists():
        return
    module = load()
    module.validate_result(json.loads(RESULT.read_text(encoding="utf-8")))
