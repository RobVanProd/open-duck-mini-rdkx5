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


def test_v156_preregistration_when_present() -> None:
    path = (
        ANALYSIS
        / "winner_v156_state_triggered_causal_behavior_preregistration.json"
    )
    if not path.exists():
        return
    result = json.loads(path.read_text(encoding="utf-8"))
    assert sha256(
        "winner_v156_state_triggered_causal_behavior_preregistration.json"
    ) == "ce29caf023782bedb6fa2363e38871a478cfe758950fe2e391dae79cb70d7e0a"
    assert result["status"] == (
        "PREREGISTERED_WINNER_V156_STATE_TRIGGERED_CAUSAL_BEHAVIOR"
    )
    assert result["failed_checks"] == []
    assert result["matrix"]["rows"] == 1
    assert result["causal_contract"]["active_ticks"] == [394, 583]
    assert result["authority"]["behavior_cells"] == 1
    assert result["authority"]["additional_behavior"] is False


def test_v156_result_when_present() -> None:
    path = ANALYSIS / "winner_v156_state_triggered_causal_behavior_result.json"
    if not path.exists():
        return
    result = json.loads(path.read_text(encoding="utf-8"))
    assert sha256(
        "winner_v156_state_triggered_causal_behavior_result.json"
    ) == "72b4f83a377c7ef0f4a8520cafb212437683a6ef67b2c3b7cd6429e7a4c01abd"
    assert result["status"] == (
        "HOLD_WINNER_V156_STATE_TRIGGERED_CAUSAL_BEHAVIOR"
    )
    assert result["cell"]["failure_reasons"] == ["trace_contract"]
    assert result["cell"]["torque_gate"]["check"] is True


def test_v156_reporting_correction_when_present() -> None:
    path = (
        ANALYSIS
        / "winner_v156_state_triggered_causal_behavior_reporting_"
        "correction.json"
    )
    if not path.exists():
        return
    result = json.loads(path.read_text(encoding="utf-8"))
    assert sha256(
        "winner_v156_state_triggered_causal_behavior_reporting_"
        "correction.json"
    ) == "afa8879e460df0b1b7d3ead25ef55f82e37a1ce1612320925d709bfb48187038"
    assert result["status"] == (
        "PASS_WINNER_V156_STATE_TRIGGERED_CAUSAL_BEHAVIOR_"
        "REPORTING_CORRECTION"
    )
    assert result["failed_checks"] == []
    assert result["incident"]["blocks_byte_identical"] is True
    assert result["incident"]["scientific_rerun"] is False
    assert result["corrected_causal_contract"]["rows"] == 600
    assert result["corrected_causal_contract"]["active_ticks"] == [394, 583]
    assert result["cell_metrics"]["worst_peak_torque_nm"] <= 1.91229675
    assert result["decision"] == (
        "EARN_V157_DUAL_CHECKPOINT_FULL_MATRIX_PREREGISTRATION"
    )
    assert result["authority"]["additional_behavior"] is False
