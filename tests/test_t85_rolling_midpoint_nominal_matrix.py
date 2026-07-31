from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t85_preregistration_requires_both_rolling_exports() -> None:
    path = ANALYSIS / "t85_rolling_midpoint_nominal_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PREREGISTERED_T85_ROLLING_MIDPOINT_NOMINAL_MATRIX"
    )
    assert value["failed_checks"] == []
    assert value["matrix"]["maximum_cells"] == 16
    assert value["persistence_contract"]["both_rolling_exports_required"]
    assert value["persistence_contract"]["same_transform_rule_at_both_exports"]
    assert value["persistence_contract"]["no_checkpoint_selection"]
    assert value["persistence_contract"]["no_coefficient_search"]


def test_t85_result_obeys_persistent_decision() -> None:
    path = ANALYSIS / "t85_rolling_midpoint_nominal_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    if value["condition"]["green_cells"] == 16:
        assert value["status"] == (
            "PASS_T85_ROLLING_MIDPOINT_NOMINAL_MATRIX"
        )
        assert value["decision"] == (
            "EARN_T86_ROLLING_MIDPOINT_R2_REVALIDATION_PREREGISTRATION"
        )
        assert value["authority"]["robustness_preregistration"]
    else:
        assert value["status"] == (
            "HOLD_T85_ROLLING_MIDPOINT_NOMINAL_MATRIX"
        )
        assert value["decision"] == "CLOSE_T78_ROLLING_ADAPTER_MIDPOINT"
    assert not value["authority"]["gate5"]
