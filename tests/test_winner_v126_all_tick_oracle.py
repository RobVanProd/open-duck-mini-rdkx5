from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"


def load(name: str) -> dict:
    return json.loads((ANALYSIS / name).read_text(encoding="utf-8"))


def test_sparse_falsifier_selects_all_tick_screen_without_training() -> None:
    prereg = load("winner_v126_all_tick_oracle_preregistration.json")
    assert (
        prereg["status"]
        == "PREREGISTERED_WINNER_V126_ALL_TICK_EXACT_ORACLE"
    )
    assert prereg["causal_correction"][
        "new_unscheduled_residual_violations"
    ] == 5
    assert prereg["nonformal_contract"]["duration_ticks"] == 64
    assert prereg["matrix"]["cells"] == 16
    assert all(
        row["oracle_schedule_ticks"] is None
        for row in prereg["matrix"]["rows"]
    )
    assert prereg["authority"]["training"] is False


def test_first_all_tick_execution_is_frozen_as_invalid_recovery() -> None:
    amendment = load(
        "winner_v126_all_tick_contract_recovery_amendment.json"
    )
    assert (
        amendment["status"]
        == "PREREGISTERED_WINNER_V126_ALL_TICK_CONTRACT_RECOVERY"
    )
    assert amendment["authorized_recovery_executions"] == 1
    assert amendment["first_execution"]["trace_exists"] is False
    assert amendment["first_execution"]["result_exists"] is False
    assert amendment["first_execution"]["selection_weight"] == 0
    assert all(amendment["checks"].values())


def test_recovered_all_tick_contract_holds_at_supreme_interval() -> None:
    result = load("winner_v126_all_tick_oracle_cpu_contract.json")
    assert result["status"] == "HOLD_WINNER_V126_ALL_TICK_ORACLE_CPU_CONTRACT"
    assert result["simulator_status"] == "HOLD_EXACT_TORQUE_ORACLE_CONTRACT"
    assert result["simulator_diagnostic"]["tick"] == 38
    assert result["simulator_diagnostic"]["error"] == (
        "base action violates the supreme oracle interval"
    )
    assert result["formal_behavior_cells_executed"] == 0
    assert result["authority"]["formal_screen_cells"] == 0
    assert result["authority"]["training"] is False


def test_supreme_clip_correction_passes_all_tick_contract() -> None:
    prereg = load(
        "winner_v126_all_tick_supreme_clip_preregistration.json"
    )
    result = load("winner_v126_all_tick_supreme_clip_cpu_contract.json")
    assert (
        prereg["status"]
        == "PREREGISTERED_WINNER_V126_ALL_TICK_SUPREME_CLIP"
    )
    assert prereg["causal_correction"]["no_parameter_change"] is True
    assert prereg["causal_correction"]["no_threshold_change"] is True
    assert (
        result["status"]
        == "PASS_WINNER_V126_ALL_TICK_SUPREME_CLIP_CPU_CONTRACT"
    )
    assert not result["failed_checks"]
    assert result["oracle"]["scheduled_ticks"] == 64
    assert result["oracle"]["projected_joint_events"] > 0
    assert result["oracle"]["prediction_mismatches"] == 0
    assert result["oracle"]["nonempty_residual_violations"] == 0
    assert result["oracle"]["unscheduled_residual_violations"] == 0
    assert result["authority"]["formal_screen_cells"] == 16
    assert result["authority"]["training"] is False
