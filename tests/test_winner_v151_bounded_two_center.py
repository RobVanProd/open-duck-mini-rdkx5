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
