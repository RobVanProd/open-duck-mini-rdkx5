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


def test_v139_reference_input_route_closes_on_rank_and_error() -> None:
    result = load("winner_v139_reference_input_controllability_result.json")
    assert sha256(
        "winner_v139_reference_input_controllability_result.json"
    ) == "1407587ad6ee15d44220a17860411f55d4f4988118d2f7cb191b4b91225dee0b"
    assert result["status"] == (
        "HOLD_WINNER_V139_REFERENCE_INPUT_CONTROLLABILITY"
    )
    assert result["failed_checks"] == [
        "every_event_nonlinearly_improves",
        "linear_minimum_norm_fit_ratio_at_most_point25",
        "nonlinear_fit_ratio_at_most_point25",
    ]
    assert result["summary"]["minimum_jacobian_rank"] == 1
    assert result["summary"]["nonlinear_ratio_to_source"] > 0.86
    assert result["summary"]["worst_event_nonlinear_ratio"] == 1.0
    assert result["decision"] == "CLOSE_REFERENCE_INPUT_REDIRECTION"
    assert result["authority"]["reference_artifact_change"] is False
    assert result["authority"]["behavior_evaluation"] is False
