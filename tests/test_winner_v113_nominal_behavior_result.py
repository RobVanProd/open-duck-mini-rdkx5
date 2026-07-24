import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "outputs/analysis/winner_v113_nominal_behavior_result.json"


def test_v113_nominal_result_is_valid_but_rejected() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_WINNER_V113_NOMINAL_BEHAVIOR_VALID_RESULT"
    assert value["failed_validity_checks"] == []
    assert all(value["validity_checks"].values())
    assert value["decision"]["status"] == "REJECT_V113_NOMINAL_POLICY"
    assert value["summary"]["passing_cells"] == 5
    assert value["summary"]["persistent_both_checkpoint_pass"] is False
    assert value["summary"]["worst_tracking_p95_rad"] < 0.20
    assert value["summary"]["minimum_moving_mean_vx_m_s"] > 0.0
    assert value["summary"]["failures_by_reason"] == {
        "current_peak_at_most_2p5": 9,
        "torque_peak_at_most_1p91229675_nm": 11,
    }
    authority = value["authority"]
    assert authority["full_frozen_matrix_preregistration_authorized"] is False
    assert authority["gate5_authorized"] is False
    assert authority["rdkx5_or_robot"] is False
