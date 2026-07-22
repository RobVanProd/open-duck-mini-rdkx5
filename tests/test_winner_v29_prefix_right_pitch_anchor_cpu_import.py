from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IMPORTER = ROOT / "tools/import_winner_v29_prefix_right_pitch_anchor_cpu_result.py"
RESULT = ROOT / "outputs/analysis/winner_v29_prefix_right_pitch_anchor_cpu_result.json"


def load():
    spec = importlib.util.spec_from_file_location("winner_v29_import", IMPORTER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_artifact_names_are_exact() -> None:
    module = load()
    assert module.RAW_RESULT_NAME == "winner-v29-prefix-right-pitch-anchor-cpu-result.json"
    assert module.RAW_RECEIPT_NAME == "winner-v29-prefix-right-pitch-anchor-cpu-result.sha256"


def test_imported_result_is_strict_when_present() -> None:
    if not RESULT.exists():
        return
    module = load()
    module.validate_result(json.loads(RESULT.read_text(encoding="utf-8")))


def test_importer_checks_anchor_scale_graph_replay_and_zero_update() -> None:
    source = IMPORTER.read_text(encoding="utf-8")
    assert "anchor_scale" in source
    assert 'graph.get("rows") != 128' in source
    assert '"optimizer_updates": 0' in source
    assert "one separately preregistered CPU-only one-update proof" in source
