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


def test_v146_preregisters_preservation_selected_direction_audit() -> None:
    prereg = load("winner_v146_dagger_direction_preregistration.json")
    assert sha256(
        "winner_v146_dagger_direction_preregistration.json"
    ) == "3495ba8476482d1ea556f84d93055afdf4a841cc90ae4362dd62d88e9c839e91"
    assert prereg["status"] == (
        "PREREGISTERED_WINNER_V146_DAGGER_DIRECTION_FEASIBILITY"
    )
    assert prereg["failed_checks"] == []
    assert prereg["method"]["bisection_steps"] == 20
    assert prereg["method"]["correction_selection_weight"] == 0
    assert prereg["method"]["optimizer_or_training"] is False
    assert prereg["authority"]["behavior"] is False
    assert prereg["authority"]["training"] is False


def test_v146_closes_global_direction_without_behavior() -> None:
    result = load("winner_v146_dagger_direction_result.json")
    assert sha256("winner_v146_dagger_direction_result.json") == (
        "8f9e2d69d34ee36066c54e6bc7f99eb009f395ae565ee8bc485bef626c9db90c"
    )
    assert result["status"] == (
        "HOLD_WINNER_V146_DAGGER_DIRECTION_FEASIBILITY"
    )
    assert result["failed_checks"] == [
        "selected_correction_all_subsets_green"
    ]
    assert 0.38010 < result["selected"]["alpha"] < 0.38011
    assert result["selected"]["maximum_preservation_ratio"] <= 0.01
    assert result["selected"]["maximum_correction_ratio"] > 0.974
    assert result["decision"] == "CLOSE_GLOBAL_DAGGER_DIRECTION"
    assert result["authority"]["behavior"] is False
    assert result["authority"]["training"] is False
