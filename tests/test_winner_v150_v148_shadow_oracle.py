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


def test_v150_preregisters_one_shadow_only_displaced_event_trace() -> None:
    prereg = load("winner_v150_v148_shadow_oracle_preregistration.json")
    assert sha256(
        "winner_v150_v148_shadow_oracle_preregistration.json"
    ) == "3d4421a5e7041faa48cc2ac1603e53a970b49aaad1eebc475c701e1e6492f270"
    assert prereg["status"] == (
        "PREREGISTERED_WINNER_V150_V148_SHADOW_ORACLE"
    )
    assert prereg["failed_checks"] == []
    assert prereg["matrix"]["cells"] == 1
    assert prereg["matrix"]["row"]["plant"] == "P30_ALL_JOINT"
    assert prereg["matrix"]["row"]["command_x_m_s"] == 0.074
    assert prereg["matrix"]["row"]["seed"] == 167_931_544
    assert prereg["checks"]["source_has_exact_single_displaced_event"]
    assert prereg["authority"]["one_cpu_shadow_cell"] is True
    assert prereg["authority"]["policy_change"] is False
    assert prereg["authority"]["training"] is False


def test_v150_reporting_correction_preserves_the_causal_result() -> None:
    raw = load("winner_v150_v148_shadow_oracle_result.json")
    assert sha256("winner_v150_v148_shadow_oracle_result.json") == (
        "5232d59b0334a2e83d5d62ae06b5c89886e4cdac78a14425edf6557c54869e98"
    )
    assert raw["failed_checks"] == [
        "behavior_failure_remains_torque_only"
    ]
    assert raw["trajectory_reproduction_linf"] == {
        "action": 0,
        "actuator_force_nm": 0,
        "obs_state": 0,
        "qpos": 0,
        "qvel": 0,
    }
    assert raw["torque"]["events"] == 1
    event = raw["torque"]["event_rows"][0]
    assert event["tick"] == 586
    assert event["joint"] == 13
    assert event["source_tick"] == 583
    assert event["source_empty_joint_indices"] == []
    assert event["source_action_delta"] > 0
    assert abs(event["projected_force_nm"]) <= 1.91229675 + 5.0e-6

    correction = load(
        "winner_v150_v148_shadow_oracle_reporting_correction.json"
    )
    assert sha256(
        "winner_v150_v148_shadow_oracle_reporting_correction.json"
    ) == "032641cb262a8138d8cf1b395d61d2b71cca560590652ae0b92090c945531e00"
    assert correction["status"] == (
        "PASS_WINNER_V150_V148_SHADOW_ORACLE_REPORTING_CORRECTION"
    )
    assert correction["failed_checks"] == []
    assert correction["reporting_correction"]["rerun"] is False
    assert (
        correction["reporting_correction"]["data_or_threshold_change"]
        is False
    )
    assert correction["decision"] == (
        "EARN_V151_BOUNDED_TWO_CENTER_CONTRACT_PREREGISTRATION"
    )
    assert correction["authority"]["policy_change"] is False
