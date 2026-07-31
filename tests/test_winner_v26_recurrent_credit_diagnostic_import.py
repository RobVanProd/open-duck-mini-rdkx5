from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
IMPORTER = ROOT / "tools/import_winner_v26_recurrent_credit_diagnostic.py"
RESULT = ROOT / "outputs/analysis/winner_v26_recurrent_credit_diagnostic_result.json"


def load():
    spec = importlib.util.spec_from_file_location("winner_v26_import", IMPORTER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_result_artifact_names_are_exact() -> None:
    module = load()
    assert module.RAW_RESULT_NAME == "winner-v26-recurrent-credit-diagnostic-result.json"
    assert module.RAW_RECEIPT_NAME == "winner-v26-recurrent-credit-diagnostic-result.sha256"


def test_repository_attribution_is_strict() -> None:
    module = load()
    digest = "a" * 64
    value = module.repository_attribution(
        run_id=123,
        run_attempt=1,
        run_head_sha="b" * 40,
        artifact_id=456,
        artifact_name="winner-v26-recurrent-credit-diagnostic-123",
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
            artifact_name="winner-v26-recurrent-credit-diagnostic-123",
            artifact_digest=f"sha256:{digest}",
            artifact_zip_sha256=digest,
        )


def test_imported_result_is_strict_when_present() -> None:
    if not RESULT.exists():
        return
    module = load()
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    module.validate_result(value)
    assert value["repository_attribution"]["github_run_attempt"] == 1


def test_importer_rederives_branches_when_present() -> None:
    source = IMPORTER.read_text(encoding="utf-8")
    assert "len(bases) != 20" in source
    assert "len(branches) != 40" in source
    assert "validate_trace" in source
    assert "runner.compare_branches" in source
    assert "runner.aggregate_candidates" in source
