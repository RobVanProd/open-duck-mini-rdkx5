from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IMPORTER = ROOT / "tools/import_winner_v22_normalized_predictor_cpu_result.py"


def load():
    spec = importlib.util.spec_from_file_location("winner_v22_cpu_import", IMPORTER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def valid_result(module):
    return {
        "schema_version": "winner_v22.normalized_predictor_cpu_result.v1",
        "status": "PASS_WINNER_V22_NORMALIZED_PREDICTOR_CPU_CONTRACT",
        "decision": "AUTHORIZE_SEPARATE_TWO_UPDATE_NORMALIZED_PREDICTOR_PROOF_PREREGISTRATION_ONLY",
        "source_snapshot": {
            "sha256": "8c1392c738eddfb098e61c1a6ae2f863eda883e1eba6ac546aef695da6f163af",
            "bytes": 189027,
        },
        "checks": {"formula": True},
        "failed_checks": [],
        "execution": {
            "optimizer_updates": 0,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "sources": {
            "contract_lf_sha256": module.lf_sha256(module.CONTRACT),
            "attribution_lf_sha256": module.lf_sha256(module.ATTRIBUTION),
            "runner_lf_sha256": module.lf_sha256(module.RUNNER),
        },
        "authority": {"robot_clearance": False, "training_executed": False},
    }


def test_importer_accepts_complete_pass_schema() -> None:
    module = load()
    module.validate_result(valid_result(module))


def test_importer_rejects_classification_check_mismatch() -> None:
    module = load()
    value = valid_result(module)
    value["checks"]["formula"] = False
    try:
        module.validate_result(value)
    except ValueError as exc:
        assert "classification" in str(exc)
    else:
        raise AssertionError("invalid Winner-v22 classification was accepted")
