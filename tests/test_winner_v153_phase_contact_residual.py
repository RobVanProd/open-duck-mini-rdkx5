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


def test_v153_preregisters_one_fixed_phase_contact_residual() -> None:
    prereg = load("winner_v153_phase_contact_residual_preregistration.json")
    assert sha256(
        "winner_v153_phase_contact_residual_preregistration.json"
    ) == "7970123f7ad206b8dc1b10f657107f3c1d266f1247daf41bc60d6bc905b1734a"
    assert prereg["status"] == (
        "PREREGISTERED_WINNER_V153_PHASE_CONTACT_RESIDUAL"
    )
    assert prereg["failed_checks"] == []
    mechanism = prereg["mechanism"]
    assert mechanism["source"] == "V140 selected raw actor"
    assert mechanism["trigger"]["contacts"] == [0, 1]
    assert mechanism["correction"]["joint"] == (
        "right ankle / action index 13"
    )
    assert mechanism["correction"]["value"] > 0
    assert mechanism["state_local_initializers"] is False
    assert mechanism["optimizer_or_training"] is False
    assert prereg["authority"]["behavior"] is False
    assert prereg["authority"]["hosted_training"] is False
