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


def test_v131_cpu_contract_proves_a_common_two_fit_action() -> None:
    result = load("winner_v131_two_fit_oracle_cpu_contract.json")
    assert sha256("winner_v131_two_fit_oracle_cpu_contract.json") == (
        "73aea66c4d79beef8d78829ff909eac94d39b2289f822a3de8d1a89476ed56a8"
    )
    assert result["failed_checks"] == []
    assert result["checks"]["all_128_rows_use_two_fit_oracle"] is True
    assert result["checks"]["all_two_fit_rows_robust_safe"] is True
    assert result["checks"]["zero_common_intersection_failures"] is True
    assert result["checks"]["at_least_one_shared_projection"] is True
    assert result["decision"] == (
        "EARN_ONE_V131_FINAL_TEACHER_8_CELL_PREREGISTRATION"
    )


def test_v131_behavior_preregistration_freezes_only_eight_cpu_cells() -> None:
    prereg = load("winner_v131_two_fit_oracle_behavior_preregistration.json")
    assert sha256(
        "winner_v131_two_fit_oracle_behavior_preregistration.json"
    ) == "7dbaa7dcc1a00aba522c491a4b67870c12dc06cf1aa4a8190ba0b2b794068783"
    assert prereg["failed_checks"] == []
    assert prereg["matrix"]["cells"] == 8
    assert prereg["matrix"]["ticks_per_cell"] == 600
    assert prereg["authority"]["formal_behavior_cells"] == 8
    assert prereg["authority"]["training"] is False
    assert prereg["authority"]["rdkx5_or_robot"] is False


def test_v131_two_fit_teacher_passes_every_frozen_cell() -> None:
    result = load("winner_v131_two_fit_oracle_behavior_result.json")
    assert sha256("winner_v131_two_fit_oracle_behavior_result.json") == (
        "ab1535e11287f191e8ee6b4be5c020c44726c6263465c7cb760892387b07c9ea"
    )
    assert result["status"] == (
        "PASS_WINNER_V131_TWO_FIT_ORACLE_BEHAVIOR_VALID_RESULT"
    )
    assert result["failed_validity_checks"] == []
    assert result["summary"]["passing_cells"] == 8
    assert result["summary"]["robust_safe_rows"] == 3_600
    assert result["summary"]["x0_bypass_rows"] == 1_200
    assert result["summary"]["empty_intersection_events"] == 0
    assert result["summary"]["projected_joint_events"] == 45
    assert result["decision"] == (
        "EARN_ONE_V132_ROBUST_TEACHER_DATASET_AUDIT"
    )
