from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t223_contract_source() -> None:
    builder = (
        ROOT
        / "tools/build_t223_global_plateau_nominal_matrix_preregistration.py"
    ).read_text(encoding="utf-8")
    runner = (
        ROOT / "tools/run_t223_global_plateau_nominal_matrix.py"
    ).read_text(encoding="utf-8")
    assert "PASS_T222B_ABI_HELPER_RECOVERY" in builder
    assert "FLOOR_FRICTION_HI" in builder
    assert '"cells": 16' in builder
    assert "both_checkpoints_required" in builder
    assert "run_or_load_block" in runner
    assert "condition_summary" in runner
    assert "behavior_cells" in runner


def test_t223_result_when_present() -> None:
    path = ANALYSIS / "t223_global_plateau_nominal_matrix_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    if value["status"] == "HOLD_T223_GLOBAL_PLATEAU_NOMINAL_MATRIX":
        assert 0 <= value["condition"]["green_cells"] < 16
        assert value["execution"]["behavior_cells"] == 16
        assert value["decision"] == "CLOSE_GLOBAL_COMMAND_PLATEAU"
        assert value["authority"]["targeted_y_negative_preregistration"] is False
        assert value["authority"]["gate5"] is False
        return
    assert value["status"] == "PASS_T223_GLOBAL_PLATEAU_NOMINAL_MATRIX"
    assert value["condition"]["green_cells"] == 16
    assert value["execution"]["behavior_cells"] == 16
    assert (
        value["decision"]
        == "EARN_T224_GLOBAL_PLATEAU_TARGETED_Y_NEGATIVE_"
        "MATRIX_PREREGISTRATION_ONLY"
    )
    assert value["authority"]["gate5"] is False
