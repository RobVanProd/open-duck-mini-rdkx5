from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IMPORTER = ROOT / "tools/import_winner_v30_prefix_right_pitch_anchor_one_update_cpu_result.py"
RESULT = ROOT / "outputs/analysis/winner_v30_prefix_right_pitch_anchor_one_update_cpu_result.json"


def load():
    spec = importlib.util.spec_from_file_location("winner_v30_import", IMPORTER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_artifact_inventory_is_exact() -> None:
    module = load()
    assert module.RAW_RESULT_NAME == "winner-v30-prefix-right-pitch-anchor-one-update-cpu-result.json"
    assert module.SNAPSHOT_MEMBER.endswith("winner_v30_prefix_right_pitch_anchor_update_201.npz")
    assert module.GRAPH_MEMBER.endswith("winner_v30_prefix_right_pitch_anchor_update_201.onnx")


def test_imported_result_is_strict_when_present() -> None:
    if not RESULT.exists():
        return
    module = load()
    module.validate_result(json.loads(RESULT.read_text(encoding="utf-8")))


def test_importer_enforces_count_loss_and_artifact_bytes() -> None:
    source = IMPORTER.read_text(encoding="utf-8")
    assert 'optimization.get("optimizer_count_before") != 200' in source
    assert 'optimization.get("optimizer_count_after") != 201' in source
    assert "not after < before" in source
    assert "snapshot_bytes" in source
    assert "graph_bytes" in source
