from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_v160_preregistration_when_present() -> None:
    path = (
        ANALYSIS
        / "winner_v160_remaining_shadow_census_preregistration.json"
    )
    if not path.exists():
        return
    result = json.loads(path.read_text(encoding="utf-8"))
    assert sha256(path) == (
        "feab00e5943af8019333e11b380d20343a757960658e9e68a2283dd948eb4eba"
    )
    assert result["status"] == (
        "PREREGISTERED_WINNER_V160_REMAINING_SHADOW_CENSUS"
    )
    assert result["failed_checks"] == []
    assert result["matrix"]["cells"] == 4
    assert result["method"]["application"] is False
    assert result["authority"]["training"] is False


def test_v160_result_when_present() -> None:
    path = ANALYSIS / "winner_v160_remaining_shadow_census_result.json"
    if not path.exists():
        return
    result = json.loads(path.read_text(encoding="utf-8"))
    assert sha256(path) == (
        "bf50eade4c73a6f5769cb8dcda8f1d5138be085848446a83cf9bad990c74965f"
    )
    assert result["status"] == "PASS_WINNER_V160_REMAINING_SHADOW_CENSUS"
    assert result["failed_checks"] == []
    assert result["aggregate"]["cells"] == 4
    assert result["selection_weight"] == 0
    assert result["decision"] == (
        "EARN_V161_V140_ON_POLICY_ORACLE_DATASET_AUDIT"
    )
    assert result["authority"]["training"] is False
