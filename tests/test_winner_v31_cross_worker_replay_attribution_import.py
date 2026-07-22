from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IMPORTER = ROOT / "tools/import_winner_v31_cross_worker_replay_attribution.py"
RESULT = ROOT / "outputs/analysis/winner_v31_cross_worker_replay_attribution_result.json"


def load():
    spec = importlib.util.spec_from_file_location("winner_v31_import", IMPORTER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_artifact_names_are_exact() -> None:
    module = load()
    assert module.RAW_RESULT_NAME == "winner-v31-cross-worker-replay-attribution-result.json"
    assert module.RAW_RECEIPT_NAME == "winner-v31-cross-worker-replay-attribution-result.sha256"


def test_imported_result_is_strict_when_present() -> None:
    if not RESULT.exists():
        return
    module = load()
    module.validate_result(json.loads(RESULT.read_text(encoding="utf-8")))
