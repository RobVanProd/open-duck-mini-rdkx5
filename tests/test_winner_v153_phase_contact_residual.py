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


def test_v153_preregisters_one_fixed_phase_contact_residual() -> None:
    prereg = load("winner_v153_phase_contact_residual_preregistration.json")
    assert sha256(
        "winner_v153_phase_contact_residual_preregistration.json"
    ) == "7970123f7ad206b8dc1b10f657107f3c1d266f1247daf41bc60d6bc905b1734a"
    assert prereg["status"] == (
        "PREREGISTERED_WINNER_V153_PHASE_CONTACT_RESIDUAL"
    )
    assert prereg["failed_checks"] == []
    mechanism = prereg["mechanism"]
    assert mechanism["source"] == "V140 selected raw actor"
    assert mechanism["trigger"]["contacts"] == [0, 1]
    assert mechanism["correction"]["joint"] == (
        "right ankle / action index 13"
    )
    assert mechanism["correction"]["value"] > 0
    assert mechanism["state_local_initializers"] is False
    assert mechanism["optimizer_or_training"] is False
    assert prereg["authority"]["behavior"] is False
    assert prereg["authority"]["hosted_training"] is False


def test_v153_v2_changes_only_the_oracle_vector_source() -> None:
    prereg = load(
        "winner_v153_phase_contact_residual_preregistration_v2.json"
    )
    assert sha256(
        "winner_v153_phase_contact_residual_preregistration_v2.json"
    ) == "106464cb98dce8391ace0d52b7fb0f3ec9a5040dcb7942fd9e450ab9fd79654f"
    assert prereg["status"] == (
        "PREREGISTERED_WINNER_V153_PHASE_CONTACT_RESIDUAL"
    )
    assert prereg["failed_checks"] == []
    assert prereg["input_hashes"]["v1_preregistration"] == (
        "7970123f7ad206b8dc1b10f657107f3c1d266f1247daf41bc60d6bc905b1734a"
    )
    assert "stopped before producing a result" in prereg["supersedes"][
        "reason"
    ]
    assert prereg["mechanism"]["correction"]["value"] > 0
    assert prereg["authority"]["behavior"] is False


def test_v153_graph_contract_is_phase_periodic_and_deployable() -> None:
    result = load("winner_v153_phase_contact_residual_result.json")
    assert sha256("winner_v153_phase_contact_residual_result.json") == (
        "4548d098902dd260561fb10e3c0a437c68980e9c775cb9c08423336afbf2ee1f"
    )
    assert result["status"] == "PASS_WINNER_V153_PHASE_CONTACT_RESIDUAL"
    assert result["failed_checks"] == []
    assert result["gate"]["aggregate_gate_count"] == 168
    assert result["gate"]["contact"] == [0, 1]
    assert result["correction"]["joint"] == 13
    assert result["correction"]["value"] > 0
    assert result["correction"]["first_target_error"] <= 5.0e-7
    assert result["checks"]["changes_only_right_ankle"] is True
    assert result["checks"]["x0_deadband_remains_exact"] is True
    assert result["artifact"]["deployed"]["inference"]["pass"] is True
    assert result["decision"] == (
        "EARN_ONE_V154_PHASE_CONTACT_CAUSAL_BEHAVIOR_PREREGISTRATION"
    )
    assert result["authority"]["behavior"] is False
