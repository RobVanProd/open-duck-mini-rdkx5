import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "outputs/analysis/winner_v115_nominal_behavior_result.json"


def test_v115_nominal_result_is_valid_and_rejected_persistently() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PASS_WINNER_V115_NOMINAL_BEHAVIOR_VALID_RESULT"
    )
    assert value["failed_validity_checks"] == []
    assert all(value["validity_checks"].values())
    assert value["summary"]["cells"] == 16
    assert value["summary"]["passing_cells"] == 9
    assert value["summary"]["persistent_both_checkpoint_pass"] is False
    assert value["decision"]["status"] == "REJECT_V115_NOMINAL_POLICY"
    assert [row["passing_cells"] for row in value["per_checkpoint"]] == [2, 7]
    assert not any(
        row["all_eight_cells_pass"] for row in value["per_checkpoint"]
    )


def test_v115_nominal_preserves_behavior_but_fails_physical_peaks() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    summary = value["summary"]
    assert summary["failures_by_reason"] == {
        "current_peak_at_most_2p5": 5,
        "torque_peak_at_most_1p91229675_nm": 7,
    }
    assert summary["worst_tracking_p95_rad"] < 0.20
    assert summary["minimum_moving_mean_vx_m_s"] > 0.0
    assert value["per_checkpoint"][1]["passing_cells"] == 7
    assert value["per_checkpoint"][1]["worst_peak_torque_nm"] == (
        1.9123668670654297
    )
    authority = value["authority"]
    assert authority["full_frozen_matrix_preregistration_authorized"] is False
    assert authority["checkpoint_selection_authorized"] is False
    assert authority["gate5_authorized"] is False
