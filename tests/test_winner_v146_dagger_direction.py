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
