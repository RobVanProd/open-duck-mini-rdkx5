from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t237_scope() -> None:
    source = (
        ROOT
        / "tools"
        / "build_t237_exact_low_command_full_r2_preregistration.py"
    ).read_text(encoding="utf-8")
    runner = (
        ROOT / "tools" / "run_t237_exact_low_command_full_r2.py"
    ).read_text(encoding="utf-8")
    assert "PASS_T236_EXACT_LOW_COMMAND_UPPER_Z" in source
    assert "plan_exact_320_cells" in source
    assert "fresh_cache_no_prior_behavior_reuse" in source
    assert "maximum_new_conditions_per_invocation" in source
    assert "stop_after_first_failed_condition" in source
    assert "IN_PROGRESS_T237_EXACT_LOW_COMMAND_FULL_R2" in runner
    assert '"optimizer_steps": 0' in source


def test_t237_preregistration_when_present() -> None:
    path = ANALYSIS / "t237_exact_low_command_full_r2_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == "PREREGISTERED_T237_EXACT_LOW_COMMAND_FULL_R2"
    assert not value["failed_checks"]
    assert len(value["conditions"]) == 20
    assert value["matrix"]["maximum_cells"] == 320
    assert value["matrix"]["strictly_sequential_conditions"]
    assert value["matrix"]["stop_after_first_failed_condition"]
    assert value["matrix"]["maximum_new_conditions_per_invocation"] == 1
    assert value["execution_now"]["behavior_cells"] == 0
    assert not value["authority"]["deployment_contract_audit_preregistration"]
    assert not value["authority"]["gate5"]


def test_t237_terminal_result_when_present() -> None:
    path = ANALYSIS / "t237_exact_low_command_full_r2_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    summary = value["summary"]
    authority = value["authority"]
    execution = value["execution"]

    assert value["status"] == "HOLD_T237_EXACT_LOW_COMMAND_FULL_R2"
    assert value["decision"] == (
        "CLOSE_EXACT_LOW_COMMAND_HEAD_ROUTE_AT_FIRST_FAILED_R2_CONDITION"
    )
    assert summary["completed_conditions"] == 17
    assert summary["expected_conditions"] == 20
    assert summary["completed_cells"] == 272
    assert summary["green_cells"] == 256
    assert summary["first_failed_condition"] == "HOME_JOINT_OFFSET_NEG"
    assert not summary["matrix_complete"]
    assert not summary["all_twenty_conditions_green"]
    assert execution["hosted_compute_units"] == 0
    assert execution["optimizer_steps"] == 0
    assert execution["robot_or_rdk_access"] == 0
    assert not authority["deployment_contract_audit_preregistration"]
    assert not authority["gate5_hardware_authorized"]
    assert not authority["rdkx5_or_robot"]
