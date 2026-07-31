from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"


def load(name: str) -> dict:
    return json.loads((ANALYSIS / name).read_text(encoding="utf-8"))


def test_v130_is_valid_but_rejects_the_linear_residual() -> None:
    result_path = (
        ANALYSIS / "winner_v130_oracle_correction_feature_audit.json"
    )
    result = json.loads(result_path.read_text(encoding="utf-8"))
    assert hashlib.sha256(result_path.read_bytes()).hexdigest() == (
        "7b4078c3ea18c3a3e1d129de3329cca8e71d178d93b836ba37f552544bed33d7"
    )
    assert result["status"] == (
        "PASS_WINNER_V130_ORACLE_CORRECTION_FEATURE_AUDIT"
    )
    assert result["failed_validity_checks"] == []
    assert result["decision"] == "NO_OBSERVATION_RESIDUAL_TRAINING"
    assert result["authority"]["formal_training"] is False
    assert result["authority"]["behavior_evaluation"] is False


def test_v130_cross_plant_failure_is_the_blocking_evidence() -> None:
    result = load("winner_v130_oracle_correction_feature_audit.json")
    transfer = result["cross_plant_fit"]
    assert (
        transfer["p30_to_p31_34"]["corrected_ratio_to_zero_predictor"]
        < 1.0
    )
    assert (
        transfer["p31_34_to_p30"]["corrected_ratio_to_zero_predictor"]
        > 6.0
    )
    assert "p31_to_p30_improves_corrected_rows" in (
        result["failed_mechanism_checks"]
    )
    assert (
        result["combined_fit"]["normalized_obs_plus_h_in"][
            "preservation_ratio_to_corrected_baseline"
        ]
        > 0.01
    )
