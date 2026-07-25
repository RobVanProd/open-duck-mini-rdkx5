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


def test_v133_corrections_preserve_the_two_protocol_repairs() -> None:
    v2 = load("winner_v133_compact_local_residual_preregistration_v2.json")
    v3 = load("winner_v133_compact_local_residual_preregistration_v3.json")
    assert v2["supersedes"]["artifact"] == (
        "winner_v133_compact_local_residual_preregistration.json"
    )
    assert "x=0 folds" in v2["supersedes"]["reason"]
    assert v3["supersedes"]["artifact"] == (
        "winner_v133_compact_local_residual_preregistration_v2.json"
    )
    assert "45 projected joint flags" in v3["supersedes"]["reason"]
    assert v3["thresholds"] == v2["thresholds"]
    assert sha256(
        "winner_v133_compact_local_residual_preregistration_v3.json"
    ) == "1e36d2879ed2021e0e687bd49a803e00569accbb308c3f02ce074272799e1b0e"


def test_v133_invalid_population_result_is_not_used_as_evidence() -> None:
    invalid = load("winner_v133_compact_local_residual_audit.json")
    assert invalid["status"] == (
        "INVALID_WINNER_V133_COMPACT_LOCAL_RESIDUAL_AUDIT"
    )
    assert invalid["failed_validity_checks"] == [
        "corrected_joint_events_exact_45"
    ]
    assert invalid["decision"] == "INVALID_NO_COMPACT_LOCAL_RESIDUAL"


def test_v133_valid_audit_closes_compact_local_interpolation() -> None:
    result = load("winner_v133_compact_local_residual_audit_v3.json")
    assert sha256("winner_v133_compact_local_residual_audit_v3.json") == (
        "c57f894724e0f350658945990f19b76caae9f3e7da219d32f97b9cb5df8f4229"
    )
    assert result["status"] == (
        "PASS_WINNER_V133_COMPACT_LOCAL_RESIDUAL_AUDIT"
    )
    assert result["failed_validity_checks"] == []
    assert result["selected_representation"] is None
    assert result["decision"] == (
        "NO_COMPACT_LOCAL_RESIDUAL_FROM_NOMINAL_DATASET"
    )
    for representation in result["representations"].values():
        assert representation["qualifies"] is False
        assert representation["combined"]["event_recall"] < 0.12
        assert (
            representation["combined"][
                "corrected_ratio_to_zero_predictor"
            ]
            > 0.95
        )
    assert result["authority"]["v134_cpu_contract"] is False
    assert result["authority"]["formal_training"] is False
    assert result["authority"]["behavior_evaluation"] is False
