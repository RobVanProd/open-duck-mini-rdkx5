from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t250_source_contract() -> None:
    builder = (
        ROOT / "tools/build_t250_offline_deployment_contract_audit_preregistration.py"
    ).read_text(encoding="utf-8")
    runner = (
        ROOT / "tools/run_t250_offline_deployment_contract_audit.py"
    ).read_text(encoding="utf-8")
    assert "maximum preregistered continuation step" in builder
    assert "behavior_metric_ranking_or_cherry_pick" in builder
    assert "verify_all_20_conditions_and_320_cells_green" in builder
    assert '"calibration_ticks": 250' in runner
    assert '"home_return_ticks": 0' in runner
    assert '"fixed_p30_observer_state": "preserved"' in runner
    assert '"action_history": "preserve final three calibrator actions"' in runner
    assert '"locomotion_previous_action": "final calibrator previous_action_out"' in runner
    assert '"frozen_101d_v1_contract_changed": False' in runner
    assert '"gate5": False' in runner
    assert '"robot_or_rdk_access": 0' in runner


def test_t250_preregistration_when_present() -> None:
    path = ANALYSIS / "t250_offline_deployment_contract_audit_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert not value["failed_checks"]
    assert value["selection_rule"]["selected_step"] == 2_007_040
    assert value["selection_rule"]["persistence_witness_step"] == 1_003_520
    assert not value["selection_rule"]["behavior_metric_ranking_or_cherry_pick"]
    assert not value["authority"]["gate5"]
    assert not value["authority"]["rdkx5_or_robot"]


def test_t250_result_when_present() -> None:
    path = ANALYSIS / "t250_offline_deployment_contract_audit_result.json"
    handoff_path = ANALYSIS / "t250_gate5_policy_handoff_manifest.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    handoff = json.loads(handoff_path.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_T250_OFFLINE_DEPLOYMENT_CONTRACT_AUDIT"
    assert not value["failed_checks"]
    assert value["full_r2"]["green_cells"] == 320
    assert value["handoff_population"]["total_cells"] == 320
    assert all(value["golden_first_locomotion_tick"]["checks"].values())
    assert value["authority"]["versioned_runtime_integration_preregistration"]
    assert not value["authority"]["gate5"]
    assert not value["authority"]["rdkx5_or_robot"]
    assert handoff["deployment_selection"]["step"] == 2_007_040
    assert handoff["two_stage_handoff"]["calibration_ticks"] == 250
    assert handoff["two_stage_handoff"]["home_return_ticks"] == 0
    assert not handoff["runtime_integration_boundary"]["frozen_101d_v1_contract_changed"]
    assert not handoff["authority"]["gate5"]
