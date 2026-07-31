from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t225_preregistration_scope() -> None:
    source = (
        ROOT / "tools/build_t225_global_plateau_full_r2_preregistration.py"
    ).read_text(encoding="utf-8")
    runner = (
        ROOT / "tools/run_t225_global_plateau_full_r2.py"
    ).read_text(encoding="utf-8")
    assert "PASS_T224_GLOBAL_PLATEAU_TARGETED_Y_NEGATIVE" in source
    assert "plan_exact_320_cells" in source
    assert "fresh_cache_no_prior_behavior_reuse" in source
    assert "maximum_new_conditions_per_invocation" in source
    assert "stop_after_first_failed_condition" in source
    assert "IN_PROGRESS_T225_GLOBAL_PLATEAU_FULL_R2" in runner
    assert "maximum-new-conditions" in runner
    assert '"optimizer_steps": 0' in runner


def test_t225_preregistration_when_present() -> None:
    path = ANALYSIS / "t225_global_plateau_full_r2_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == "PREREGISTERED_T225_GLOBAL_PLATEAU_FULL_R2"
    assert not value["failed_checks"]
    assert len(value["conditions"]) == 20
    assert value["matrix"]["maximum_cells"] == 320
    assert value["matrix"]["strictly_sequential_conditions"]
    assert value["matrix"]["stop_after_first_failed_condition"]
    assert value["matrix"]["maximum_new_conditions_per_invocation"] == 1
    assert value["execution_now"]["behavior_cells"] == 0
    assert not value["authority"]["deployment_contract_audit_preregistration"]
    assert not value["authority"]["gate5"]


def test_t225_result_scope() -> None:
    path = ANALYSIS / "t225_global_plateau_full_r2_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] in {
        "PASS_T225_GLOBAL_PLATEAU_FULL_R2",
        "HOLD_T225_GLOBAL_PLATEAU_FULL_R2",
    }
    assert value["execution"]["optimizer_steps"] == 0
    assert value["execution"]["hosted_compute_units"] == 0
    assert value["execution"]["robot_or_rdk_access"] == 0
    assert not value["authority"]["gate5_hardware_authorized"]
    if value["status"].startswith("PASS_"):
        assert value["summary"]["completed_conditions"] == 20
        assert value["summary"]["completed_cells"] == 320
        assert value["summary"]["green_cells"] == 320
