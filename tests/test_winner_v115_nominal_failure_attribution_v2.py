import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = (
    ROOT / "outputs/analysis/winner_v115_nominal_failure_attribution_v2.json"
)


def test_v115_v2_hold_is_numerical_check_only() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["status"] == (
        "HOLD_WINNER_V115_NOMINAL_FAILURE_ATTRIBUTION_V2"
    )
    assert value["failed_checks"] == [
        "formula_exact",
        "no_rate_limit_increased",
    ]
    assert value["decision"] == "STOP"
    assert value["authority"]["rate_projection_preregistration_authorized"] is False


def test_v115_v2_derivation_identifies_complete_affected_set() -> None:
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    derivation = value["derivation"]
    assert derivation["candidate_vectors"] == 1
    assert derivation["scalar_search"] is False
    assert set(derivation["affected_joints"]) == {
        "left_hip_pitch",
        "left_knee",
        "left_ankle",
        "right_ankle",
    }
    assert all(
        row["rate_lag_fraction"] == 1.0
        for row in derivation["joints"]
        if row["active_exceeding_joint_ticks"]
    )
