from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t213_contract_source() -> None:
    builder = (
        ROOT / "tools/build_t213_t210_nominal_matrix_preregistration.py"
    ).read_text(encoding="utf-8")
    runner = (
        ROOT / "tools/run_t213_t210_nominal_matrix.py"
    ).read_text(encoding="utf-8")
    assert "PASS_T212_T210_POSTEXPORT_COMPOSITION" in builder
    assert "FLOOR_FRICTION_HI" in builder
    assert '"cells": 16' in builder
    assert "both_checkpoints_required" in builder
    assert "run_or_load_block" in runner
    assert "condition_summary" in runner
    assert "behavior_cells" in runner


def test_t213_result_when_present() -> None:
    path = ANALYSIS / "t213_t210_nominal_matrix_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_T213_T210_NOMINAL_MATRIX"
    assert value["condition"]["green_cells"] == 16
    assert value["execution"]["behavior_cells"] == 16
    assert (
        value["decision"]
        == "EARN_T214_T210_TARGETED_Y_NEGATIVE_MATRIX_"
        "PREREGISTRATION_ONLY"
    )
    assert value["authority"]["gate5"] is False
