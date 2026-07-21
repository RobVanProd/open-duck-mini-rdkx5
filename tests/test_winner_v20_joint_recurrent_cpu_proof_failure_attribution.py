from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ATTRIBUTION = (
    ROOT
    / "outputs/analysis/winner_v20_joint_recurrent_cpu_proof_failure_attribution.json"
)


def test_first_proof_is_invalid_and_attributed_exactly() -> None:
    value = json.loads(ATTRIBUTION.read_text(encoding="utf-8"))
    assert value["status"] == (
        "INVALID_WINNER_V20_JOINT_RECURRENT_SUPPORT_CPU_CONTRACT_PROOF"
    )
    assert value["decision"] == (
        "CORRECT_ONLY_JOINT_SNAPSHOT_READER_AND_FRESHLY_PREREGISTER"
    )
    assert value["failed_run"]["github_run_id"] == 29851858965
    assert value["failed_run"]["github_artifact_id"] == 8503746957
    assert value["failed_run"]["formal_result_present"] is False
    assert value["failure"]["proof_valid"] is False
    assert value["failure"]["behavior_or_objective_semantics_change"] is False


def test_correction_does_not_grant_training_or_robot_authority() -> None:
    value = json.loads(ATTRIBUTION.read_text(encoding="utf-8"))
    assert value["correction_boundary"]["fresh_run_required"] is True
    assert value["correction_boundary"]["workflow_rerun_permitted"] is False
    assert value["execution"]["authorized_training_arm_updates"] == 0
    assert value["execution"]["formal_support_cells"] == 0
    assert value["execution"]["robot_or_rdk_access"] == 0
    assert value["authority"]["joint_recurrent_training_authorized"] is False
    assert value["authority"]["robot_clearance"] is False
