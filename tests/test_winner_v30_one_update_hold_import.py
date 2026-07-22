from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IMPORTER = ROOT / "tools/import_winner_v30_one_update_hold_artifact.py"


def load():
    spec = importlib.util.spec_from_file_location("winner_v30_hold_import", IMPORTER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_expected_hold_failures_are_exact() -> None:
    module = load()
    assert module.EXPECTED_FAILED_CHECKS == [
        "exact_v29_anchor_loss_gradient_and_scale_reproduced",
        "exact_v29_update_200_batch_reproduced",
    ]


def test_hold_importer_preserves_all_four_members() -> None:
    module = load()
    assert module.RAW_RESULT_NAME.endswith("result.json")
    assert module.RAW_RECEIPT_NAME.endswith("result.sha256")
    assert module.SNAPSHOT_MEMBER.endswith("update_201.npz")
    assert module.GRAPH_MEMBER.endswith("update_201.onnx")


def test_hold_importer_authorizes_no_rerun() -> None:
    source = IMPORTER.read_text(encoding="utf-8")
    assert "HOLD result is already imported" in source
    assert "optimizer_updates\": 1" in source
    assert "authorizes no rerun" in source
