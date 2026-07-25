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


def test_v141_preregistration_reuses_half_and_tests_final() -> None:
    prereg = load("winner_v141_projected_final_behavior_preregistration.json")
    assert sha256(
        "winner_v141_projected_final_behavior_preregistration.json"
    ) == "40ac2e58d9a8058697e81011f66051840bcc3f81fe278f44e0356e2f532709a0"
    assert prereg["status"] == (
        "PREREGISTERED_WINNER_V141_PROJECTED_FINAL_BEHAVIOR"
    )
    assert prereg["failed_checks"] == []
    assert prereg["matrix"]["reused_half_cells"] == 8
    assert len(prereg["matrix"]["new_final_rows"]) == 8
    assert prereg["candidate_pair"]["half"]["new_cells"] == 0
    assert prereg["candidate_pair"]["half"]["evidence"][
        "all_eight_cells_pass"
    ]
    assert prereg["authority"]["new_final_behavior_cells"] == 8
    assert prereg["authority"]["training"] is False
    assert prereg["authority"]["policy_deployment"] is False


def test_v141_closes_on_transferred_right_ankle_load() -> None:
    result = load("winner_v141_projected_final_behavior_result.json")
    assert sha256("winner_v141_projected_final_behavior_result.json") == (
        "08ecfbeb87a09781228d0657e795e106a1f4fae0e60b844f7055dacead21929b"
    )
    assert result["status"] == "HOLD_WINNER_V141_PROJECTED_FINAL_BEHAVIOR"
    assert result["decision"] == "CLOSE_PRESERVATION_PROJECTED_ACTOR"
    assert result["summary"]["new_final_cells_completed"] == 2
    assert result["summary"]["combined_cells_passing"] == 9
    moving = result["new_final_cells"][1]
    assert moving["failure_reasons"] == [
        "torque_peak_at_most_1p91229675_nm"
    ]
    assert 1.920 < moving["torque_gate"]["worst_peak_torque_nm"] < 1.921
    assert moving["prospective_current_gate"]["pass"] is True
    assert moving["metrics"]["candidate_gate_status"] == (
        "PASS_CANDIDATE_SIM_GATE"
    )
    assert moving["metrics"]["worst_tracking_p95_rad"] < 0.15
    assert result["authority"]["policy_deployment"] is False
