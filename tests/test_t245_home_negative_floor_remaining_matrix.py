from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t245_contract_source() -> None:
    builder = (
        ROOT
        / "tools/build_t245_home_negative_floor_remaining_matrix_preregistration.py"
    ).read_text(encoding="utf-8")
    runner = (
        ROOT / "tools/run_t245_home_negative_floor_remaining_matrix.py"
    ).read_text(encoding="utf-8")
    assert "three_non_target_half_p30_cells_are_inheritable" in builder
    assert '"cells_reused": 4' in builder
    assert '"cells_new_maximum": 12' in builder
    assert "stop_at_first_failed_new_block" in builder
    assert "reused half/P30 cells changed" in runner
    assert "new block was unexpectedly cached" in runner
    assert "remaining_cells_not_run" in runner
    assert '"optimizer_steps": 0' in runner


def test_t245_result_when_present() -> None:
    path = (
        ANALYSIS / "t245_home_negative_floor_remaining_matrix_result.json"
    )
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["recovery"]["blocks_reused"] == 1
    assert value["recovery"]["cells_reused"] == 4
    assert value["recovery"]["reused_cells_rerun"] == 0
    assert value["execution"]["optimizer_steps"] == 0
    assert value["authority"]["gate5"] is False
    if (
        value["status"]
        == "PASS_T245_HOME_NEGATIVE_FLOOR_REMAINING_MATRIX"
    ):
        assert value["condition"]["condition_green"]
        assert value["condition"]["green_cells"] == 16
        assert value["recovery"]["new_blocks_executed"] == 3
        assert value["recovery"]["new_cells_executed"] == 12
        assert value["recovery"]["remaining_cells_not_run"] == 0
        assert (
            value["decision"]
            == "EARN_T246_HOME_NEGATIVE_FLOOR_FULL_R2_"
            "PRESERVATION_PREREGISTRATION_ONLY"
        )
        assert value["authority"]["full_r2_preservation_preregistration"]
