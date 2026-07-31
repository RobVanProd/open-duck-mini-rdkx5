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


def test_v151_preregisters_a_hard_two_center_family_bound() -> None:
    prereg = load("winner_v151_bounded_two_center_preregistration.json")
    assert sha256(
        "winner_v151_bounded_two_center_preregistration.json"
    ) == "ca77bc58546ec6283ea87e9b7475d581622765f1000da086ba3d959f24c57b94"
    assert prereg["status"] == (
        "PREREGISTERED_WINNER_V151_BOUNDED_TWO_CENTER"
    )
    assert prereg["failed_checks"] == []
    assert prereg["family_bound"]["maximum_centers"] == 2
    assert prereg["family_bound"]["centers_after_contract"] == 2
    assert prereg["family_bound"]["third_center_permitted"] is False
    assert prereg["checks"]["second_center_is_exact_displaced_event_precursor"]
    assert prereg["mechanism"]["optimizer_or_training"] is False
    assert prereg["authority"]["behavior"] is False
    assert prereg["authority"]["hosted_training"] is False


def test_v151_closes_before_behavior_on_frozen_target_tolerance() -> None:
    result = load("winner_v151_bounded_two_center_result.json")
    assert sha256("winner_v151_bounded_two_center_result.json") == (
        "fbc794b6d12bbe8f60087f8d417a201ccf5b259f5f2514c730ba4af2ef4a90f2"
    )
    assert result["status"] == "HOLD_WINNER_V151_BOUNDED_TWO_CENTER"
    assert result["failed_checks"] == ["center_matches_oracle_target"]
    assert result["aggregate"]["rows"] == 6_000
    assert result["aggregate"]["second_gate_rows"] == [5_983]
    assert result["aggregate"]["changed_elements"] == [[5_983, 13]]
    assert result["aggregate"]["preservation_linf"] == 0
    assert result["checks"]["first_center_parameters_bit_exact"] is True
    assert result["checks"]["deployment_contract_green"] is True
    assert 1.7e-7 < result["second_center"]["center_error"] < 1.9e-7
    assert result["decision"] == "CLOSE_FINITE_LOCAL_RESIDUAL_FAMILY"
    assert result["family_bound"]["third_center_permitted"] is False
    assert result["authority"]["behavior"] is False
