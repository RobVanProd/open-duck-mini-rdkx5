from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"


def load(name: str) -> dict:
    return json.loads((ANALYSIS / name).read_text(encoding="utf-8"))


def test_exact_oracle_contracts_pass_without_behavior_or_training() -> None:
    initial = load("winner_v126_exact_oracle_cpu_contract.json")
    optimized = load("winner_v126_exact_oracle_cpu_contract_v2.json")
    sparse = load("winner_v126_sparse_oracle_schedule_cpu_contract.json")
    assert initial["status"] == "PASS_WINNER_V126_EXACT_ORACLE_CPU_CONTRACT"
    assert (
        optimized["status"]
        == "PASS_WINNER_V126_EXACT_ORACLE_CPU_CONTRACT_OPTIMIZED"
    )
    assert (
        sparse["status"]
        == "PASS_WINNER_V126_SPARSE_ORACLE_SCHEDULE_CPU_CONTRACT"
    )
    assert initial["formal_behavior_cells_executed"] == 0
    assert sparse["formal_behavior_cells_executed"] == 0
    assert not initial["failed_checks"]
    assert not optimized["failed_checks"]
    assert not sparse["failed_checks"]
    assert sparse["oracle"]["projected_joint_events"] == 3
    assert sparse["oracle"]["prediction_mismatches"] == 0
    assert sparse["oracle"]["nonempty_residual_violations"] == 0
    assert sparse["oracle"]["unscheduled_residual_violations"] == 0
    assert sparse["authority"]["training"] is False


def test_v115_retro_audit_corrects_clip_hypothesis() -> None:
    audit = load("winner_v126_v115_linear_price_clipping_audit.json")
    assert (
        audit["status"]
        == "PASS_WINNER_V126_V115_LINEAR_PRICE_CLIPPING_AUDIT"
    )
    assert audit["summary"]["cells"] == 16
    assert audit["summary"]["rows"] == 9600
    assert audit["summary"]["event_ticks"] == 23
    assert abs(audit["summary"]["removed_fraction"]) <= 1.0e-12
    assert (
        audit["summary"]["maximum_base_reward_reconstruction_error"]
        <= 2.0e-6
    )
    assert audit["authority"]["selection_weight"] == 0


def test_sparse_schedule_covers_all_v124_events_and_fails_new_events() -> None:
    prereg = load("winner_v126_sparse_oracle_schedule_preregistration.json")
    assert (
        prereg["status"]
        == "PREREGISTERED_WINNER_V126_SPARSE_ORACLE_SCHEDULE"
    )
    assert prereg["causal_selection"]["unique_scheduled_decisions"] == 15
    assert len(prereg["causal_selection"]["events"]) == 15
    assert len(prereg["matrix"]["rows"]) == 16
    assert (
        "unscheduled residual"
        in prereg["causal_selection"]["not_scheduled"]
    )
    assert prereg["authority"]["training"] is False
    assert prereg["authority"]["formal_screen_cells_after_contract_pass"] == 16


def test_formal_behavior_preregistration_freezes_half_teacher_rule() -> None:
    prereg = load("winner_v126_exact_oracle_behavior_preregistration.json")
    assert (
        prereg["status"]
        == "PREREGISTERED_WINNER_V126_EXACT_ORACLE_BEHAVIOR"
    )
    assert prereg["matrix"]["cells"] == 16
    assert prereg["decision"]["required_teacher_checkpoint_id"] == (
        "V121_TRAIN_MATCHED_HALF"
    )
    assert prereg["decision"]["required_teacher_cells"] == 8
    assert prereg["authority"]["formal_screen_cells"] == 16
    assert prereg["authority"]["retry"] is False
    assert prereg["authority"]["training"] is False
    validity = prereg["screen_rule"]["oracle_validity"]
    assert "zero prediction mismatches" in validity
    assert "zero unscheduled residual violations" in validity


def test_v126_evaluator_is_isolated_without_changing_frozen_bytes() -> None:
    amendment = load("winner_v126_evaluator_isolation_amendment.json")
    assert (
        amendment["status"]
        == "PASS_WINNER_V126_EVALUATOR_ISOLATION_AMENDMENT"
    )
    assert not amendment["failed_checks"]
    assert all(amendment["checks"].values())
    assert (
        amendment["observed_sha256"]["v126_evaluator"]
        == amendment["observed_sha256"][
            "behavior_prereg_frozen_evaluator"
        ]
        == amendment["observed_sha256"][
            "sparse_contract_frozen_evaluator"
        ]
    )
    assert amendment["authority"]["formal_behavior_cells"] == 0
    assert amendment["authority"]["training"] is False
