import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = (
    ROOT / "outputs/analysis/winner_v115_nominal_failure_attribution.json"
)


def test_v115_single_joint_repair_hypothesis_is_held() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["status"] == "HOLD_WINNER_V115_NOMINAL_FAILURE_ATTRIBUTION"
    assert value["decision"] == "STOP_AND_REASSESS"
    assert value["failed_checks"] == [
        "all_torque_failures_left_ankle_only",
        "at_most_one_joint_exceeds_per_tick",
    ]
    assert value["selected_repair"]["authorized"] is False
    assert value["authority"][
        "one_variable_rate_repair_preregistration_authorized"
    ] is False


def test_v115_failures_are_rate_lag_linked_but_multi_joint() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    summary = value["summary"]
    assert summary["active_exceeding_joint_ticks"] == 24
    assert summary["lag_window_boundary_hits"] == 24
    assert summary["lag_window_boundary_fraction"] == 1.0
    assert {
        name
        for name, count in summary["failure_joint_cell_counts"].items()
        if count
    } == {"left_hip_pitch", "left_knee", "left_ankle", "right_ankle"}
    assert summary["final_passing_cells"] == 7
    assert summary["half_passing_cells"] == 2
