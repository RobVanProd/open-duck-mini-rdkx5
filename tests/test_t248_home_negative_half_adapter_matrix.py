from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t248_contract_source() -> None:
    builder = (
        ROOT
        / "tools/build_t248_home_negative_half_adapter_matrix_preregistration.py"
    ).read_text(encoding="utf-8")
    runner = (
        ROOT / "tools/run_t248_home_negative_half_adapter_matrix.py"
    ).read_text(encoding="utf-8")
    assert "eight_half_cells_green_and_reusable" in builder
    assert '"cells_reused": 8' in builder
    assert '"cells_new_maximum": 8' in builder
    assert "run_only_two_final_blocks_fresh_no_retry" in builder
    assert "reused half blocks changed" in runner
    assert "final block was unexpectedly cached" in runner
    assert '"optimizer_steps": 0' in runner


def test_t248_result_when_present() -> None:
    path = ANALYSIS / "t248_home_negative_half_adapter_matrix_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["recovery"]["half_blocks_reused"] == 2
    assert value["recovery"]["half_cells_reused"] == 8
    assert value["recovery"]["reused_cells_rerun"] == 0
    assert value["execution"]["optimizer_steps"] == 0
    assert value["authority"]["gate5"] is False
    if value["status"] == "PASS_T248_HOME_NEGATIVE_HALF_ADAPTER_MATRIX":
        assert value["condition"]["condition_green"]
        assert value["condition"]["green_cells"] == 16
        assert value["recovery"]["new_final_blocks_executed"] == 2
        assert value["recovery"]["new_final_cells_executed"] == 8
        assert value["recovery"]["remaining_cells_not_run"] == 0
        assert (
            value["decision"]
            == "EARN_T249_HOME_NEGATIVE_REPAIR_FULL_R2_"
            "PRESERVATION_PREREGISTRATION_ONLY"
        )
        assert value["authority"]["full_r2_preservation_preregistration"]
