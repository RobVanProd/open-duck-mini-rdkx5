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
