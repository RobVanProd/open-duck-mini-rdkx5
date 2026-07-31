from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"


def sha256(name: str) -> str:
    return hashlib.sha256((ANALYSIS / name).read_bytes()).hexdigest()


def test_v158_preregistration_when_present() -> None:
    path = ANALYSIS / "winner_v158_x077_shadow_census_preregistration.json"
    if not path.exists():
        return
    result = json.loads(path.read_text(encoding="utf-8"))
    assert sha256(
        "winner_v158_x077_shadow_census_preregistration.json"
    ) == "87e7dcb899422553628aab28d91d5922cf14c3ac51060411c3b2c7ad03c744ea"
    assert result["status"] == "PREREGISTERED_WINNER_V158_X077_SHADOW_CENSUS"
    assert result["failed_checks"] == []
    assert result["matrix"]["cells"] == 1
    assert result["matrix"]["row"]["plant"] == "P30_ALL_JOINT"
    assert result["matrix"]["row"]["command_x_m_s"] == 0.077
    assert result["method"]["application"] is False
    assert result["authority"]["training"] is False


def test_v158_result_when_present() -> None:
    path = ANALYSIS / "winner_v158_x077_shadow_census_result.json"
    if not path.exists():
        return
    result = json.loads(path.read_text(encoding="utf-8"))
    assert sha256(
        "winner_v158_x077_shadow_census_result.json"
    ) == "f43f4c2f7c21efd58e231ea00c88dc233852f7af54600f5cb220be2c09bfe8bb"
    assert result["status"] == "HOLD_WINNER_V158_X077_SHADOW_CENSUS"
    assert result["failed_checks"] == ["torque_failure_reproduced"]
    assert result["checks"]["shadow_action_never_applied"] is True
    assert result["checks"][
        "every_violation_has_safe_nonempty_precursor_label"
    ] is True
    assert result["oracle"]["rows"] == 600
    assert result["torque"]["events"] > 0
    assert result["authority"]["candidate_behavior"] is False


def test_v158_reporting_correction_when_present() -> None:
    path = (
        ANALYSIS
        / "winner_v158_x077_shadow_census_reporting_correction.json"
    )
    if not path.exists():
        return
    result = json.loads(path.read_text(encoding="utf-8"))
    assert sha256(
        "winner_v158_x077_shadow_census_reporting_correction.json"
    ) == "96feb1995018d2b8614406d9e922794d14beb03b2407330e25b71a46aab4b08b"
    assert result["status"] == (
        "PASS_WINNER_V158_X077_SHADOW_CENSUS_REPORTING_CORRECTION"
    )
    assert result["failed_checks"] == []
    assert result["census"]["violating_joints"] == [3, 13]
    assert [
        (event["tick"], event["joint"])
        for event in result["census"]["events"]
    ] == [(30, 3), (208, 13)]
    assert result["checks"]["policy_action_unchanged"] is True
    assert result["decision"] == "EARN_V159_POLICY_SPACE_REDESIGN_AUDIT"
    assert result["authority"]["training"] is False
