from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np
import pytest


ROOT = Path(__file__).resolve().parents[1]
IMPORTER = ROOT / "tools/import_winner_v42_static_target_teacher_table.py"
RESULT = ROOT / "outputs/analysis/winner_v42_static_target_teacher_table_result.json"


def load():
    spec = importlib.util.spec_from_file_location("winner_v42_import", IMPORTER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_artifact_names_and_attribution_fields_are_exact() -> None:
    module = load()
    assert module.RAW_RESULT_NAME == "winner-v42-static-target-teacher-table-result.json"
    assert module.RAW_RECEIPT_NAME.endswith(".sha256")
    assert module.ATTRIBUTION_FIELDS == {
        "repository", "github_run_id", "github_run_attempt", "github_run_head_sha",
        "github_artifact_id", "github_artifact_name", "github_artifact_digest",
        "artifact_zip_sha256", "artifact_zip_bytes", "raw_result_sha256",
        "raw_result_receipt_sha256", "preregistration_lf_sha256",
        "workflow_lf_sha256", "runner_lf_sha256", "importer_lf_sha256",
    }


def test_coordinate_identity_and_selection_tie_break_are_rederived() -> None:
    module = load()
    coordinates = module.EXPECTED_COORDINATES[0]
    assert module.array_sha256(np.asarray(coordinates, dtype=np.float32)) == (
        "7f47ac9344c8f00756f2435339560685fabdacca9d40789e858397a5e5a29e87"
    )
    plant = {
        "support_pass": True,
        "valid_ticks": 250,
        "minimum_base_z_m": 0.15,
        "maximum_abs_tilt_rad": 0.03,
        "maximum_final_window_gyro_xy_norm_rad_s": 0.001,
    }
    first = {"candidate_index": 4, "plant_results": [plant, plant]}
    second = {"candidate_index": 5, "plant_results": [plant, plant]}
    assert module.candidate_key(first, (0.0, 0.0, 0.0)) > module.candidate_key(
        second, (0.0, 0.0, 0.0)
    )


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
            artifact_name="winner-v42-static-target-teacher-table-1",
            artifact_digest=f"sha256:{'b' * 64}",
            artifact_zip_sha256="b" * 64,
        )
