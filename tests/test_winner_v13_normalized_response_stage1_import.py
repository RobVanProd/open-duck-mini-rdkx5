from __future__ import annotations

import importlib.util
from pathlib import Path
import zipfile

import pytest


ROOT = Path(__file__).resolve().parents[1]
IMPORTER = ROOT / "tools/import_winner_v13_normalized_response_stage1.py"


def load():
    spec = importlib.util.spec_from_file_location("winner_v13_stage1_importer", IMPORTER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_expected_artifact_inventory_is_complete() -> None:
    module = load()
    members = module.expected_artifact_members()
    assert len(members) == 105
    assert module.RAW_RESULT_NAME in members
    assert module.RAW_RECEIPT_NAME in members
    assert module.RAW_LOG_NAME in members
    assert (
        f"{module.WORK_PREFIX}/snapshots/snapshot_stage1_update_001.npz"
        in members
    )
    assert (
        f"{module.WORK_PREFIX}/snapshots/snapshot_stage1_update_100.npz"
        in members
    )


def test_repository_attribution_is_single_attempt_and_digest_exact() -> None:
    module = load()
    digest = "a" * 64
    value = module.repository_attribution(
        run_id=123,
        run_attempt=1,
        run_head_sha="b" * 40,
        artifact_id=456,
        artifact_name="winner-v13-normalized-response-stage1-123",
        artifact_digest=f"sha256:{digest}",
        artifact_zip_sha256=digest,
    )
    assert value["github_run_attempt"] == 1
    with pytest.raises(ValueError):
        module.repository_attribution(
            run_id=123,
            run_attempt=2,
            run_head_sha="b" * 40,
            artifact_id=456,
            artifact_name="winner-v13-normalized-response-stage1-123",
            artifact_digest=f"sha256:{digest}",
            artifact_zip_sha256=digest,
        )


def test_importer_rejects_incomplete_artifact(tmp_path: Path) -> None:
    module = load()
    artifact = tmp_path / "incomplete.zip"
    with zipfile.ZipFile(artifact, "w") as archive:
        archive.writestr(module.RAW_RESULT_NAME, "{}")
    with pytest.raises(ValueError, match="inventory changed"):
        module.read_result_artifact(artifact)


def test_boolean_failure_list_must_be_exact() -> None:
    module = load()
    checks = {name: True for name in module.RUN_CHECKS}
    assert module.validate_boolean_checks(checks, module.RUN_CHECKS, [], "run") == []
    one = sorted(module.RUN_CHECKS)[0]
    checks[one] = False
    with pytest.raises(ValueError, match="failed-check list changed"):
        module.validate_boolean_checks(checks, module.RUN_CHECKS, [], "run")
