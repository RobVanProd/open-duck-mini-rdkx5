from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "outputs/analysis/winner_v12_calibrator_artifact_recovery_result.json"
IMPORTER = ROOT / "tools/import_winner_v12_calibrator_artifact_recovery.py"


def load_importer():
    spec = importlib.util.spec_from_file_location(
        "winner_v12_recovery_importer", IMPORTER
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_imported_recovery_pass_is_exact_and_zero_authority() -> None:
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    assert result["status"] == "PASS_WINNER_V12_CALIBRATOR_ARTIFACT_RECOVERY"
    assert (
        result["decision"] == "AUTHORIZE_FULL_CALIBRATOR_TRAINING_PREREGISTRATION_ONLY"
    )
    assert result["failed_checks"] == []
    assert result["checks"] and all(result["checks"].values())
    assert result["execution"] == {
        "formal_support_cells": 0,
        "locomotion_behavior_cells": 0,
        "locomotion_training_steps": 0,
        "new_checkpoints_written": 0,
        "new_onnx_graphs_written": 0,
        "optimizer_updates": {"stage1": 0, "stage2": 0},
        "protected_policy_inference_calls": 0,
        "retry_of_failed_smoke": False,
        "robot_or_rdk_access": 0,
    }
    assert result["repository_attribution"] == {
        "github_artifact_digest": "sha256:4d6be6c54f0c44cc2279aa37b7bf462b8a6912a40b8e71ed46ebb195bbbfd070",
        "github_artifact_id": 8484550478,
        "github_run_commit": "0d7b0309431e5401259f0528d8cc0ee009bc9d4a",
        "github_run_id": 29803319695,
        "raw_result_sha256": "940f8a94cf5710b120892f1d7207f96ce6835e79cf970647e3bb65f646ac19e8",
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
    broadened["execution"]["optimizer_updates"]["stage2"] = 1
    with pytest.raises(ValueError):
        importer.validate(broadened)
