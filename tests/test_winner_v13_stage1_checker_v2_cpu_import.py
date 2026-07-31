from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IMPORTER = ROOT / "tools/import_winner_v13_stage1_checker_v2_cpu_contract.py"
RESULT = ROOT / "outputs/analysis/winner_v13_stage1_checker_v2_cpu_result.json"


def load():
    spec = importlib.util.spec_from_file_location("winner_v13_checker_v2_import", IMPORTER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_imported_result_passes_exact_validation() -> None:
    module = load()
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    module.validate_result(value)
    assert value["status"] == "PASS_WINNER_V13_STAGE1_CHECKER_V2_CPU_CONTRACT"
    assert value["failed_checks"] == []


def test_imported_result_has_exact_zero_execution_boundary() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["execution"] == {
        "optimizer_updates": 0,
        "simulation_cells": 0,
        "formal_support_cells": 0,
        "locomotion_steps": 0,
        "robot_or_rdk_access": 0,
    }
    assert value["authority"]["robot_clearance"] is False
    assert value["decision"] == "AUTHORIZE_FRESH_STAGE1_V2_PREREGISTRATION_ONLY"
