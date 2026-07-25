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
    assert result["status"] == "PASS_WINNER_V158_X077_SHADOW_CENSUS"
    assert result["failed_checks"] == []
    assert result["checks"]["shadow_action_never_applied"] is True
    assert result["checks"][
        "every_violation_has_safe_nonempty_precursor_label"
    ] is True
    assert result["oracle"]["rows"] == 600
    assert result["torque"]["events"] > 0
    assert result["authority"]["candidate_behavior"] is False
