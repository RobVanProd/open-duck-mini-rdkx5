import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"


def test_v117_failure_earns_one_cpu_v118_vector_not_training() -> None:
    value = json.loads(
        (
            ANALYSIS / "winner_v117_nominal_failure_attribution.json"
        ).read_text(encoding="utf-8")
    )
    assert value["status"] == (
        "PASS_WINNER_V117_NOMINAL_FAILURE_ATTRIBUTION"
    )
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert value["decision"] == (
        "PREREGISTER_ONE_V118_POSTGUARD_RATE_PROJECTION"
    )
    assert value["derivation"]["candidate_vectors"] == 1
    assert value["derivation"]["scalar_search"] is False
    assert set(value["derivation"]["affected_joints"]) == {
        "left_hip_pitch",
        "left_knee",
        "left_ankle",
        "right_ankle",
    }
    assert value["checks"]["all_exceeding_ticks_rate_lag_linked"]
    assert value["checks"]["final_checkpoint_all_eight_pass"]
    assert value["checks"]["training_not_yet_earned"]
    assert value["authority"][
        "v118_projection_preregistration_authorized"
    ]
    assert value["authority"]["training_authorized"] is False
    for joint in value["derivation"]["joints"]:
        if joint["changed"]:
            assert joint["selected_rate_limit_rad_s"] < (
                joint["current_rate_limit_rad_s"]
            )
        else:
            assert joint["selected_normalized_action_delta"] == (
                joint["current_normalized_action_delta"]
            )
