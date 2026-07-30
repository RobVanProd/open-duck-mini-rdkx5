from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t220_contract_source() -> None:
    builder = (
        ROOT
        / "tools/build_t220_t216_targeted_y_negative_preregistration.py"
    ).read_text(encoding="utf-8")
    runner = (
        ROOT / "tools/run_t220_t216_targeted_y_negative.py"
    ).read_text(encoding="utf-8")
    assert "PASS_T219_T216_NOMINAL_MATRIX" in builder
    assert "TORSO_COM_Y_NEG" in builder
    assert "-0.05" in builder
    assert '"cells": 16' in builder
    assert "both_checkpoints_required" in builder
    assert "run_or_load_block" in runner
    assert "condition_summary" in runner
    assert "behavior_cells" in runner


def test_t220_result_when_present() -> None:
    path = ANALYSIS / "t220_t216_targeted_y_negative_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    if value["status"] == "HOLD_T220_T216_TARGETED_Y_NEGATIVE":
        assert 0 <= value["condition"]["green_cells"] < 16
        assert value["execution"]["behavior_cells"] == 16
        assert value["decision"] == "CLOSE_T216_AXIS_COMPLETE_TILT_CONTINUATION"
        assert value["authority"]["full_r2_preregistration"] is False
        assert value["authority"]["gate5"] is False
        return
    assert value["status"] == "PASS_T220_T216_TARGETED_Y_NEGATIVE"
    assert value["condition"]["green_cells"] == 16
    assert value["execution"]["behavior_cells"] == 16
    assert (
        value["decision"]
        == "EARN_T221_T216_FULL_R2_PREREGISTRATION_ONLY"
    )
    assert value["authority"]["gate5"] is False
