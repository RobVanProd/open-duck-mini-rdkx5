from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
IMPORTER = ROOT / "tools/import_winner_v27_early_prefix_recovery_scan.py"
RESULT = ROOT / "outputs/analysis/winner_v27_early_prefix_recovery_scan_result.json"


def load():
    spec = importlib.util.spec_from_file_location("winner_v27_import", IMPORTER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_artifact_names_are_exact() -> None:
    module = load()
    assert module.RAW_RESULT_NAME == "winner-v27-early-prefix-recovery-scan-result.json"
    assert module.RAW_RECEIPT_NAME == "winner-v27-early-prefix-recovery-scan-result.sha256"


def test_repository_attribution_is_strict() -> None:
    module = load()
    digest = "a" * 64
    value = module.repository_attribution(
        run_id=123,
        run_attempt=1,
        run_head_sha="b" * 40,
        artifact_id=456,
        artifact_name="winner-v27-early-prefix-recovery-scan-123",
        artifact_digest=f"sha256:{digest}",
        artifact_zip_sha256=digest,
    )
    assert value["repository"] == "RobVanProd/open-duck-mini-rdkx5"
    with pytest.raises(ValueError, match="attribution changed"):
        module.repository_attribution(
            run_id=123,
            run_attempt=2,
            run_head_sha="b" * 40,
            artifact_id=456,
            artifact_name="winner-v27-early-prefix-recovery-scan-123",
            artifact_digest=f"sha256:{digest}",
            artifact_zip_sha256=digest,
        )


def test_imported_result_is_strict_when_present() -> None:
    if not RESULT.exists():
        return
    module = load()
    module.validate_result(json.loads(RESULT.read_text(encoding="utf-8")))


def test_importer_rederives_all_forks() -> None:
    source = IMPORTER.read_text(encoding="utf-8")
    assert "len(rows) != 240" in source
    assert "runner.compare_recovery" in source
    assert "runner.aggregate_scan" in source
    assert "candidate continuation no longer replays support" in source
