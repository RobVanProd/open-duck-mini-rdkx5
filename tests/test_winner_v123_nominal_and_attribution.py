import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"


def load(name: str) -> dict:
    return json.loads((ANALYSIS / name).read_text(encoding="utf-8"))


def test_v123_nominal_result_is_valid_and_rejected() -> None:
    value = load("winner_v123_nominal_behavior_result.json")
    assert value["status"] == ("PASS_WINNER_V123_NOMINAL_BEHAVIOR_VALID_RESULT")
    assert value["failed_validity_checks"] == []
    assert all(value["validity_checks"].values())
    assert value["summary"]["cells"] == 16
    assert value["summary"]["passing_cells"] == 4
    assert value["summary"]["persistent_both_checkpoint_pass"] is False
    assert value["summary"]["failures_by_reason"] == {
        "current_peak_at_most_2p5": 11,
        "torque_peak_at_most_1p91229675_nm": 12,
    }
    assert value["summary"]["worst_tracking_p95_rad"] < 0.15
    assert value["summary"]["minimum_moving_mean_vx_m_s"] > 0.1
    assert value["decision"]["status"] == "REJECT_V123_NOMINAL_POLICY"
    assert value["authority"]["full_frozen_matrix_preregistration_authorized"] is False
    assert value["authority"]["gate5_authorized"] is False


def test_v123_attribution_closes_episode_peak_without_successor() -> None:
    value = load("winner_v123_episode_peak_failure_attribution.json")
    assert value["status"] == ("PASS_WINNER_V123_EPISODE_PEAK_FAILURE_ATTRIBUTION")
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert value["comparison"]["v121"]["trace"]["torque_exceed_events"] == 15
    assert value["comparison"]["v123"]["trace"]["torque_exceed_events"] == 184
    assert value["comparison"]["v123"]["trace"]["joint_event_counts"] == {
        "left_ankle": 13,
        "left_knee": 148,
        "right_ankle": 18,
        "right_knee": 5,
    }
    assert value["decision"]["status"] == ("CLOSE_V122_EPISODE_PEAK_OBJECTIVE")
    assert value["decision"]["repeat_or_scalar_search_authorized"] is False
    assert value["decision"]["successor_training_authorized"] is False
    assert value["decision"]["successor_behavior_screen_authorized"] is False
    assert value["execution"] == {
        "colab_compute_units": 0,
        "new_behavior_cells": 0,
        "new_training_steps": 0,
        "robot_or_rdk_access": 0,
    }
    assert not any(value["authority"].values())
