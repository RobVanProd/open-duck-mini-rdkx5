from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t223b_contract_source() -> None:
    builder = (
        ROOT
        / "tools/build_t223b_interrupted_matrix_recovery_preregistration.py"
    ).read_text(encoding="utf-8")
    runner = (
        ROOT / "tools/run_t223b_interrupted_matrix_recovery.py"
    ).read_text(encoding="utf-8")
    assert "exactly_two_completed_half_blocks" in builder
    assert "rerun_completed_cells" in builder
    assert "required_missing_blocks" in builder
    assert "completed block was not reused" in runner
    assert "missing block was unexpectedly cached" in runner
    assert "behavior_cells_reused" in runner
    assert '"optimizer_steps": 0' in runner


def test_t223b_result_when_present() -> None:
    path = ANALYSIS / "t223b_interrupted_matrix_recovery_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["recovery"]["completed_blocks_reused"] == 2
    assert value["recovery"]["missing_blocks_executed"] == 2
    assert value["recovery"]["no_completed_cell_rerun"]
    assert value["execution"]["behavior_cells_reused"] == 8
    assert value["execution"]["new_behavior_cells"] == 8
    assert value["execution"]["optimizer_steps"] == 0
    assert value["authority"]["gate5"] is False
    if value["status"] == "HOLD_T223B_INTERRUPTED_MATRIX_RECOVERY":
        assert value["condition"]["green_cells"] < 16
        assert value["decision"] == "CLOSE_GLOBAL_COMMAND_PLATEAU"
        assert value["authority"]["targeted_y_negative_preregistration"] is False
        return
    assert value["status"] == "PASS_T223B_INTERRUPTED_MATRIX_RECOVERY"
    assert value["condition"]["green_cells"] == 16
    assert (
        value["decision"]
        == "EARN_T224_GLOBAL_PLATEAU_TARGETED_Y_NEGATIVE_"
        "MATRIX_PREREGISTRATION_ONLY"
    )
