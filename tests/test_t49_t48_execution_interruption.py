from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t49_closes_incomplete_t48_without_retry() -> None:
    path = ANALYSIS / "t49_t48_execution_interruption_attribution.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PASS_T49_T48_TWO_CELL_EXECUTION_INTERRUPTION_ATTRIBUTION"
    )
    assert value["decision"] == (
        "CLOSE_T48_ZERO_DECISION_WEIGHT_NO_RETRY_"
        "EARN_T49_MISSING_COMBINED_CONTROL_PREREGISTRATION"
    )
    assert value["failed_checks"] == []
    assert value["classification"]["formal_behavior_cells_completed"] == 2
    assert value["classification"]["formal_behavior_cells_required"] == 3
    assert value["classification"]["t48_policy_decision_weight"] == 0
    assert value["classification"]["missing_variant_id"] == (
        "FINAL_WITH_HALF_CORE_HEAD"
    )
    assert all(
        item["cell_green"] for item in value["completed_cells"]
    )
    assert value["authority"]["missing_combined_control_preregistration"]
    assert not value["authority"]["completed_cell_retry"]
    assert not value["authority"]["factorial_decision"]
    assert not value["authority"]["gate5"]
