from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
RESULT = (
    ROOT
    / "outputs/analysis/winner_v12_full_calibrator_training_cpu_contract_result.json"
)
IMPORTER = (
    ROOT / "tools/import_winner_v12_full_calibrator_training_cpu_contract_result.py"
)


def load_importer():
    spec = importlib.util.spec_from_file_location("winner_v12_full_importer", IMPORTER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_imported_result_passes_with_zero_update_authority() -> None:
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    assert result["status"] == ("PASS_WINNER_V12_FULL_CALIBRATOR_TRAINING_CPU_CONTRACT")
    assert result["decision"] == (
        "AUTHORIZE_ONE_WINNER_V12_FULL_CALIBRATOR_TRAINING_RUN_ONLY"
    )
    assert result["checks"] and all(result["checks"].values())
    assert result["failed_checks"] == []
    assert result["execution"] == {
        "formal_support_cells": 0,
        "locomotion_training_steps": 0,
        "optimizer_updates": 0,
        "robot_or_rdk_access": 0,
    }
    assert result["repository_attribution"] == {
        "github_artifact_digest": "sha256:f4f72120109d5db1a5360cf66b4589011e30ee63689924c8b66f907f34aa62c3",
        "github_artifact_id": 8485829253,
        "github_run_commit": "4c3cd478c41a18c3c06f4bac40d82837039431fd",
        "github_run_id": 29806824132,
        "raw_result_sha256": "faf520ccf7a34e2da3cd3c86acadb66656dbcf99ce61f227116d8d5dbeba15c3",
    }


def test_importer_rejects_false_check_or_broadened_authority() -> None:
    importer = load_importer()
    raw = json.loads(RESULT.read_text(encoding="utf-8"))
    raw.pop("repository_attribution")
    false_check = copy.deepcopy(raw)
    false_check["checks"][next(iter(false_check["checks"]))] = False
    with pytest.raises(ValueError):
        importer.validate(false_check)
    broadened = copy.deepcopy(raw)
    broadened["execution"]["optimizer_updates"] = 1
    with pytest.raises(ValueError):
        importer.validate(broadened)


def test_importer_rejects_changed_calibrator_abi() -> None:
    importer = load_importer()
    raw = json.loads(RESULT.read_text(encoding="utf-8"))
    raw.pop("repository_attribution")
    raw["persistence_contract"]["half"]["graph"]["inputs"][0]["shape"] = [1, 101]
    with pytest.raises(ValueError):
        importer.validate(raw)
