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


def test_v155_preregisters_one_state_trigger_without_search() -> None:
    result = load(
        "winner_v155_velocity_gated_phase_residual_preregistration.json"
    )
    assert sha256(
        "winner_v155_velocity_gated_phase_residual_preregistration.json"
    ) == "da91d9fe292c758b210f3516a7d6cd9ec941ce83dcdbdcbddd0fef3e96a2ff36"
    assert result["status"] == (
        "PREREGISTERED_WINNER_V155_VELOCITY_GATED_PHASE_RESIDUAL"
    )
    assert result["failed_checks"] == []
    mechanism = result["mechanism"]
    assert mechanism["state_feature"]["obs_index"] == 40
    assert mechanism["correction_joint"] == 13
    assert mechanism["optimizer_or_training"] is False
    assert mechanism["forward_predictor"] is False
    separation = result["separation"]
    assert len(separation["positive_values"]) == 3
    assert separation["negative_max"] < mechanism["threshold"]
    assert mechanism["threshold"] < separation["positive_min"]
    assert result["authority"]["behavior"] is False
    assert result["authority"]["hosted_training"] is False


def test_v155_graph_contract_when_present() -> None:
    path = ANALYSIS / "winner_v155_velocity_gated_phase_residual_result.json"
    if not path.exists():
        return
    result = json.loads(path.read_text(encoding="utf-8"))
    assert sha256(
        "winner_v155_velocity_gated_phase_residual_result.json"
    ) == "71276cb1abb4f3e1649b6ca4e6b4711e6fabdd552c6be2344c32c7cec3d389a6"
    assert result["status"] == (
        "PASS_WINNER_V155_VELOCITY_GATED_PHASE_RESIDUAL"
    )
    assert result["failed_checks"] == []
    assert result["checks"]["all_three_positive_rows_inside_gate"] is True
    assert (
        result["checks"]["all_39_frozen_negative_rows_outside_gate"] is True
    )
    assert result["checks"]["changes_only_right_ankle"] is True
    assert result["checks"]["x0_deadband_remains_exact"] is True
    assert result["artifact"]["deployed"]["inference"]["pass"] is True
    assert result["decision"] == (
        "EARN_ONE_V156_STATE_TRIGGERED_CAUSAL_BEHAVIOR_PREREGISTRATION"
    )
    assert result["authority"]["behavior"] is False
