from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IMPORTER = ROOT / "tools/import_winner_v13_support_controller_training.py"


def load():
    spec = importlib.util.spec_from_file_location("winner_v13_support_training_import", IMPORTER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_expected_artifact_inventory_is_complete_and_exact() -> None:
    module = load()
    members = module.artifact_members()
    assert len(members) == 105
    assert module.RAW_RESULT in members
    assert module.RAW_RECEIPT in members
    assert module.RAW_LOG in members
    assert f"{module.WORK_PREFIX}/snapshots/snapshot_stage2_update_001.npz" in members
    assert f"{module.WORK_PREFIX}/snapshots/snapshot_stage2_update_100.npz" in members
    assert f"{module.WORK_PREFIX}/graphs/winner_v13_support_controller_half.onnx" in members
    assert f"{module.WORK_PREFIX}/graphs/winner_v13_support_controller_final.onnx" in members
