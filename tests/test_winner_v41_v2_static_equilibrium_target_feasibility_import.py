from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
IMPORTER = ROOT / "tools/import_winner_v41_v2_static_equilibrium_target_feasibility.py"
RESULT = ROOT / "outputs/analysis/winner_v41_v2_static_equilibrium_target_feasibility_result.json"


def load():
    spec = importlib.util.spec_from_file_location("winner_v41_v2_import", IMPORTER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_artifact_names_and_attribution_fields_are_exact() -> None:
    module = load()
    assert module.RAW_RESULT_NAME == "winner-v41-v2-static-equilibrium-target-feasibility-result.json"
    assert module.RAW_RECEIPT_NAME.endswith(".sha256")
    assert module.ATTRIBUTION_FIELDS == {
        "repository", "github_run_id", "github_run_attempt", "github_run_head_sha",
        "github_artifact_id", "github_artifact_name", "github_artifact_digest",
        "artifact_zip_sha256", "artifact_zip_bytes", "raw_result_sha256",
        "raw_result_receipt_sha256", "base_preregistration_lf_sha256",
        "base_runner_lf_sha256", "correction_preregistration_lf_sha256",
        "correction_runner_lf_sha256", "first_attempt_failure_receipt_lf_sha256",
        "workflow_lf_sha256", "importer_lf_sha256",
    }


def test_imported_result_is_strict_when_present() -> None:
    if not RESULT.exists():
        return
    module = load()
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    module.validate_result(value)
    assert value["repository_attribution"]["github_run_attempt"] == 1


def test_repository_attribution_rejects_rerun() -> None:
    module = load()
    with pytest.raises(ValueError, match="workflow attribution changed"):
        module.repository_attribution(
            run_id=1,
            run_attempt=2,
            run_head_sha="a" * 40,
            artifact_id=1,
            artifact_name="winner-v41-v2-static-equilibrium-target-feasibility-1",
            artifact_digest=f"sha256:{'b' * 64}",
            artifact_zip_sha256="b" * 64,
        )
