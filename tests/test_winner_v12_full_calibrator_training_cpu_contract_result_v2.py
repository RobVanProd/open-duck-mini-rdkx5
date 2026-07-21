from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
RESULT = (
    ROOT
    / "outputs/analysis/winner_v12_full_calibrator_training_cpu_contract_result_v2.json"
)
IMPORTER = (
    ROOT / "tools/import_winner_v12_full_calibrator_training_cpu_contract_result_v2.py"
)


def load_importer():
    spec = importlib.util.spec_from_file_location(
        "winner_v12_full_importer_v2", IMPORTER
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_imported_corrected_result_passes_with_zero_update_authority() -> None:
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    assert result["status"] == "PASS_WINNER_V12_FULL_CALIBRATOR_TRAINING_CPU_CONTRACT"
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
        "github_artifact_digest": "sha256:f02a902412abf23ef08832c3d73e3faee13f5af53cfe977bb3832c4b13fe853c",
        "github_artifact_id": 8486408542,
        "github_run_attempt": 1,
        "github_run_commit": "35069ead37433e1b8d98c3082d4b163e06ec5fef",
        "github_run_id": 29808349887,
        "raw_result_sha256": "d0d035123122bc37462c2a6e83cb6a8bc82081f34cfdd3317fd79db3fbbc010e",
    }


def test_corrected_importer_rejects_missing_or_false_check() -> None:
    importer = load_importer()
    raw = json.loads(RESULT.read_text(encoding="utf-8"))
    raw.pop("repository_attribution")
    missing = copy.deepcopy(raw)
    missing["checks"].pop(next(iter(missing["checks"])))
    with pytest.raises(ValueError):
        importer.validate(missing)
    false_check = copy.deepcopy(raw)
    false_check["checks"][next(iter(false_check["checks"]))] = False
    with pytest.raises(ValueError):
        importer.validate(false_check)


def test_corrected_importer_rejects_changed_calibrator_abi() -> None:
    importer = load_importer()
    raw = json.loads(RESULT.read_text(encoding="utf-8"))
    raw.pop("repository_attribution")
    raw["persistence_contract"]["half"]["graph"]["inputs"][0]["shape"] = [
        1,
        101,
    ]
    with pytest.raises(ValueError):
        importer.validate(raw)
