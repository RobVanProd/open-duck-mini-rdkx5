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


def test_v140_preregistration_projects_without_optimizer_retry() -> None:
    prereg = load(
        "winner_v140_preservation_projected_actor_preregistration.json"
    )
    assert sha256(
        "winner_v140_preservation_projected_actor_preregistration.json"
    ) == "dcae023363e5979b23e5ea6d438955445b1471d9ae81937a10eb9ed76a1f87d5"
    assert prereg["status"] == (
        "PREREGISTERED_WINNER_V140_PRESERVATION_PROJECTED_ACTOR"
    )
    assert prereg["failed_checks"] == []
    assert prereg["selection"]["preservation_limit"] == 0.01
    assert prereg["selection"]["corrected_error_selection_weight"] == 0
    assert prereg["selection"]["parameter_search"] is False
    assert "optimizer" in prereg["mechanism"]["why_distinct"]
    assert prereg["authority"]["behavior_evaluation"] is False
    assert prereg["authority"]["training"] is False


def test_v140_projection_hits_preservation_boundary_and_keeps_gain() -> None:
    result = load("winner_v140_preservation_projected_actor_result.json")
    assert sha256(
        "winner_v140_preservation_projected_actor_result.json"
    ) == "44921665d80235246737b333a5149ceacb702d477dcc2c7496395bf0c42ba637"
    assert result["status"] == (
        "PASS_WINNER_V140_PRESERVATION_PROJECTED_ACTOR"
    )
    assert result["failed_checks"] == []
    assert 0.73 < result["summary"]["selected_alpha"] < 0.74
    selected = result["summary"]["selected_metrics"]
    assert selected["preservation_ratio_to_corrected_baseline"] <= 0.01
    assert selected["preservation_ratio_to_corrected_baseline"] > 0.00999
    assert selected["corrected_ratio_to_source"] < 0.91
    assert selected["x0_nonzero_values"] == 0
    assert result["decision"] == (
        "EARN_ONE_V141_DUAL_CHECKPOINT_BEHAVIOR_PREREGISTRATION"
    )
    assert result["authority"]["behavior_evaluation"] is False
    assert result["authority"]["training"] is False
