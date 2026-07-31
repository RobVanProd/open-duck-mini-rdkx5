from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IMPORTER = ROOT / "tools/import_winner_v32_prefix_right_pitch_anchor_training.py"
RESULT = ROOT / "outputs/analysis/winner_v32_prefix_right_pitch_anchor_training_result.json"


def load():
    spec = importlib.util.spec_from_file_location("winner_v32_training_import", IMPORTER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_training_artifact_inventory_is_exact() -> None:
    module = load()
    members = module.artifact_members()
    assert len(members) == 104
    assert f"{module.WORK}/snapshots/snapshot_prefix_anchor_update_202.npz" in members
    assert f"{module.WORK}/snapshots/snapshot_prefix_anchor_update_301.npz" in members
    assert f"{module.WORK}/graphs/winner_v32_half.onnx" in members
    assert len(module.GRADIENT_KEYS) == 12
    assert len(module.ANCHOR_GRADIENT_KEYS) == 6
    assert len(module.NON_ANCHOR_GRADIENT_KEYS) == 6


def test_imported_result_is_strict_when_present() -> None:
    if not RESULT.exists():
        return
    module = load()
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    module.validate_result(value)
    assert value["repository_attribution"]["github_run_attempt"] == 1
