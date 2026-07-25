from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"


def load(name: str) -> dict:
    return json.loads((ANALYSIS / name).read_text(encoding="utf-8"))


def sha256(name: str) -> str:
    return hashlib.sha256((ANALYSIS / name).read_bytes()).hexdigest()


def test_v128_persistence_failure_closes_ppo_lagrangian() -> None:
    nominal = load("winner_v128_nominal_behavior_result.json")
    attribution = load("winner_v128_nominal_failure_attribution.json")
    assert sha256("winner_v128_nominal_behavior_result.json") == (
        "c703a5024dee3bcd32fb549e3c561c09d164d1f766c91ebc882fab7173c0e35a"
    )
    assert nominal["summary"]["passing_cells"] == 10
    per_checkpoint = {
        row["checkpoint_id"]: row for row in nominal["per_checkpoint"]
    }
    assert per_checkpoint["V128_CONSTRAINED_HALF"]["passing_cells"] == 2
    assert per_checkpoint["V128_CONSTRAINED_FINAL"]["passing_cells"] == 8
    assert attribution["failed_checks"] == []
    assert (
        attribution["mechanism_verdict"]["ppo_lagrangian_v121_recipe"]
        == "CLOSED_NO_RETRY"
    )
    assert attribution["authority"]["additional_ppo_lagrangian"] is False


def test_v129_teacher_is_final_because_half_is_identity() -> None:
    audit = load("winner_v129_oracle_teacher_dataset_audit.json")
    assert sha256("winner_v129_oracle_teacher_dataset_audit.json") == (
        "9fa2e685c5df292f8f817bb81e5fb5b08e2e924963cbd310f8ac08d334dfc224"
    )
    assert audit["failed_checks"] == []
    assert audit["dataset"]["source"] == (
        "V121_TRAIN_MATCHED_FINAL plus exact oracle"
    )
    assert len(audit["teacher_correction"]["projected_events"]) == 14
    assert (
        audit["decision"]
        == "AUTHORIZE_ONE_V129_CPU_DISTILLATION_CONTRACT"
    )


def test_v129_cpu_contract_corrections_are_auditable() -> None:
    v2 = load("winner_v129_oracle_teacher_cpu_preregistration_v2.json")
    v3 = load("winner_v129_oracle_teacher_cpu_preregistration_v3.json")
    result = load("winner_v129_oracle_teacher_cpu_result.json")
    assert v2["supersedes"]["artifact"] == (
        "winner_v129_oracle_teacher_cpu_preregistration.json"
    )
    assert "projected rows" in v2["supersedes"]["reason"]
    assert v3["supersedes"]["artifact"] == (
        "winner_v129_oracle_teacher_cpu_preregistration_v2.json"
    )
    assert "RunningStatisticsState" in v3["supersedes"]["reason"]
    assert result["failed_checks"] == []
    assert result["status"] == (
        "PASS_WINNER_V129_ORACLE_TEACHER_CPU_CONTRACT"
    )
    assert result["checks"]["only_adapter_location_head_changed"] is True
    assert result["checks"]["two_updates_reduce_action_loss"] is True
    assert result["dataset"]["corrected_rows"] == 14


def test_v129_formal_head_only_distillation_closes_without_behavior() -> None:
    prereg = load(
        "winner_v129_oracle_teacher_formal_cpu_preregistration.json"
    )
    result = load("winner_v129_oracle_teacher_formal_cpu_result.json")
    assert sha256("winner_v129_oracle_teacher_formal_cpu_result.json") == (
        "2b083d958ee29b3fd0cee90c73de610ed73a1b9ccd23a2a6b360242d95a5e909"
    )
    assert prereg["training"]["exports"] == [0, 19, 38]
    assert prereg["training"]["retry_or_resume"] is False
    assert result["status"] == (
        "HOLD_WINNER_V129_ORACLE_TEACHER_FORMAL_CPU_DISTILLATION"
    )
    assert set(result["failed_checks"]) == {
        "final_corrected_loss_below_step_zero",
        "final_objective_below_step_zero",
        "half_objective_below_step_zero",
    }
    assert result["decision"] == (
        "CLOSE_V129_DISTILLATION_WITHOUT_BEHAVIOR"
    )
    assert result["checks"]["formal_behavior_cells_zero"] is True
    assert result["authority"]["nominal_behavior_evaluation"] is False
