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


def test_v132_audit_was_preregistered_read_only() -> None:
    prereg = load("winner_v132_robust_teacher_dataset_preregistration.json")
    assert sha256(
        "winner_v132_robust_teacher_dataset_preregistration.json"
    ) == "583c03daf7516d54e2804079a3f3a04c24b5574080efb7fc5fd2fa10c1311353"
    assert prereg["status"] == (
        "PREREGISTERED_WINNER_V132_ROBUST_TEACHER_DATASET_AUDIT"
    )
    assert prereg["failed_checks"] == []
    assert prereg["authority"]["read_only_cpu_audit"] is True
    assert prereg["authority"]["training"] is False
    assert prereg["authority"]["behavior_evaluation"] is False


def test_v132_validly_closes_static_linear_distillation() -> None:
    result = load("winner_v132_robust_teacher_dataset_audit.json")
    assert sha256("winner_v132_robust_teacher_dataset_audit.json") == (
        "1292b12ff996cf99fc5fdd718048517256bb86d656512fad3586a6d62a8963ca"
    )
    assert result["status"] == (
        "PASS_WINNER_V132_ROBUST_TEACHER_DATASET_AUDIT"
    )
    assert result["failed_validity_checks"] == []
    assert result["dataset"]["rows"] == 4_800
    assert result["dataset"]["corrected_rows"] == 17
    assert result["dataset"]["projected_joint_events"] == 45
    assert result["advancement"]["hidden_qualifies"] is False
    assert result["advancement"]["state_qualifies"] is False
    assert result["decision"] == (
        "NO_STATIC_LINEAR_ROBUST_TEACHER_DISTILLATION"
    )
    assert result["authority"]["formal_training"] is False
    assert result["authority"]["behavior_evaluation"] is False


def test_v132_failure_is_preservation_and_cross_fit_not_teacher_safety() -> None:
    result = load("winner_v132_robust_teacher_dataset_audit.json")
    assert result["checks"]["all_moving_rows_robust_safe"] is True
    hidden = result["combined_fit"]["current_hidden"]
    assert hidden["corrected_ratio_to_zero_predictor"] <= 0.25
    assert hidden["preservation_ratio_to_corrected_baseline"] > 0.01
    state = result["cross_plant_fit"]["normalized_obs_plus_h_in"]
    assert (
        state["p31_34_to_p30"]["corrected_ratio_to_zero_predictor"]
        > 1.0
    )
    assert (
        state["p31_34_to_p30"]["preservation_ratio_to_corrected_baseline"]
        > 0.01
    )
