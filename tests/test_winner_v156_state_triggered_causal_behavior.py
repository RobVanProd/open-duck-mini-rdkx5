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
    assert result["status"] == (
        "PASS_WINNER_V156_STATE_TRIGGERED_CAUSAL_BEHAVIOR"
    )
    assert result["failed_checks"] == []
    assert result["cell"]["pass"] is True
    assert result["causal_contract"]["gate"]["active_ticks"] == [394, 583]
    assert result["decision"] == (
        "EARN_V157_DUAL_CHECKPOINT_FULL_MATRIX_PREREGISTRATION"
    )
    assert result["authority"]["additional_behavior"] is False
