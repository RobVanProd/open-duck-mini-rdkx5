from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IMPORTER = ROOT / "tools/import_winner_v13_support_controller_cpu_result.py"
RESULT = ROOT / "outputs/analysis/winner_v13_support_controller_cpu_result.json"


def load():
    spec = importlib.util.spec_from_file_location("winner_v13_support_cpu_import", IMPORTER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_expected_artifact_inventory_is_exact() -> None:
    module = load()
    assert module.artifact_members() == {
        module.RAW_RESULT,
        module.RAW_RECEIPT,
        module.RAW_GRAPH,
        module.RAW_SNAPSHOT,
    }


def test_imported_result_is_exactly_valid() -> None:
    module = load()
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    module.validate_result(value)
    assert value["status"] == "PASS_WINNER_V13_SUPPORT_CONTROLLER_CPU_CONTRACT"
    assert value["failed_checks"] == []
    assert value["execution"] == {
        "stage2_optimizer_updates": 1,
        "formal_support_cells": 0,
        "locomotion_steps": 0,
        "robot_or_rdk_access": 0,
    }
