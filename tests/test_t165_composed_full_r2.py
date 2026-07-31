from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t165_preregistration_scope() -> None:
    path = ANALYSIS / "t165_composed_full_r2_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == "PREREGISTERED_T165_COMPOSED_FULL_R2"
    assert not value["failed_checks"]
    assert len(value["conditions"]) == 20
    assert value["matrix"]["maximum_cells"] == 320
    assert value["matrix"]["strictly_sequential_conditions"]
    assert value["matrix"]["stop_after_first_failed_condition"]
    assert value["matrix"]["maximum_new_conditions_per_invocation"] == 1
    assert value["execution_now"]["behavior_cells"] == 0
    assert not value["authority"]["deployment_contract_audit_preregistration"]
    assert not value["authority"]["gate5"]


def test_t165_result_scope() -> None:
    path = ANALYSIS / "t165_composed_full_r2_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] in {
        "PASS_T165_COMPOSED_FULL_R2",
        "HOLD_T165_COMPOSED_FULL_R2",
    }
    assert value["execution"]["optimizer_steps"] == 0
    assert value["execution"]["hosted_compute_units"] == 0
    assert value["execution"]["robot_or_rdk_access"] == 0
    assert not value["authority"]["gate5_hardware_authorized"]
    if value["status"].startswith("PASS_"):
        assert value["summary"]["completed_conditions"] == 20
        assert value["summary"]["completed_cells"] == 320
        assert value["summary"]["green_cells"] == 320
