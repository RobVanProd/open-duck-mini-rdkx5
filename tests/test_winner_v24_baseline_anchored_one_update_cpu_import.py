from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
IMPORTER = ROOT / "tools/import_winner_v24_baseline_anchored_one_update_result.py"
RESULT = ROOT / "outputs/analysis/winner_v24_baseline_anchored_one_update_cpu_result.json"


def load():
    spec = importlib.util.spec_from_file_location("winner_v24_one_update_import", IMPORTER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_artifact_names_and_trainable_inventory_are_exact() -> None:
    module = load()
    assert module.RAW_RESULT_NAME == "winner-v24-baseline-anchored-one-update-result.json"
    assert module.SNAPSHOT_NAME == "winner_v24_baseline_anchored_update_101.npz"
    assert module.GRAPH_NAME == "winner_v24_baseline_anchored_update_101.onnx"
    assert len(module.GRADIENT_KEYS) == 12
    assert "previous_action_weight" in module.GRADIENT_KEYS


def test_repository_attribution_rejects_rerun() -> None:
    module = load()
    digest = "a" * 64
    value = module.repository_attribution(
        run_id=123, run_attempt=1, run_head_sha="b" * 40, artifact_id=456,
        artifact_name="winner-v24-baseline-anchored-one-update-123",
        artifact_digest=f"sha256:{digest}", artifact_zip_sha256=digest,
    )
    assert value["repository"] == "RobVanProd/open-duck-mini-rdkx5"
    with pytest.raises(ValueError, match="attribution changed"):
        module.repository_attribution(
            run_id=123, run_attempt=2, run_head_sha="b" * 40, artifact_id=456,
            artifact_name="winner-v24-baseline-anchored-one-update-123",
            artifact_digest=f"sha256:{digest}", artifact_zip_sha256=digest,
        )


def test_imported_result_is_strict_when_present() -> None:
    if not RESULT.exists():
        return
    module = load()
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    module.validate_result(value)
    assert value["repository_attribution"]["github_run_attempt"] == 1
