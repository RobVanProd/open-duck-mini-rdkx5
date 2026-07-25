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


def test_v139_preregistration_freezes_per_event_upper_bound() -> None:
    prereg = load(
        "winner_v139_reference_input_controllability_preregistration.json"
    )
    assert sha256(
        "winner_v139_reference_input_controllability_preregistration.json"
    ) == "64f46d5d4b6565a006449c253dedb6f2b5d4f0d1fe39ea9ebcaa74bdd45eab33"
    assert prereg["status"] == (
        "PREREGISTERED_WINNER_V139_REFERENCE_INPUT_CONTROLLABILITY"
    )
    assert prereg["failed_checks"] == []
    assert prereg["population"]["rows"] == 17
    assert prereg["method"]["variable"] == (
        "reference input obs[101:115] only"
    )
    assert prereg["method"]["parameter_or_threshold_search"] is False
    assert prereg["authority"]["reference_artifact_change"] is False
    assert prereg["authority"]["behavior_evaluation"] is False
    assert prereg["authority"]["training"] is False
