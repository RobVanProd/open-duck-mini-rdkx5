from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_v162_preregistration_when_present() -> None:
    path = (
        ANALYSIS / "winner_v162_uniform_trust_nominal_preregistration.json"
    )
    if not path.exists():
        return
    result = json.loads(path.read_text(encoding="utf-8"))
    assert sha256(path) == (
        "084ec5ee5dabba05e36b9117c8db6f1c4806fcc3cf8ddcce8ca3e79935887cce"
    )
    assert result["status"] == (
        "PREREGISTERED_WINNER_V162_UNIFORM_TRUST_NOMINAL"
    )
    assert result["failed_checks"] == []
    assert result["matrix"]["cells"] == 16
    assert result["authority"]["training"] is False


def test_v162_result_when_present() -> None:
    path = ANALYSIS / "winner_v162_uniform_trust_nominal_result.json"
    if not path.exists():
        return
    result = json.loads(path.read_text(encoding="utf-8"))
    assert result["status"] == "PASS_WINNER_V162_UNIFORM_TRUST_NOMINAL"
    assert result["failed_checks"] == []
    assert result["summary"]["completed_cells"] == 16
    assert result["summary"]["passing_cells"] == 16
    assert all(row["all_eight_pass"] for row in result["per_checkpoint"])
    assert result["decision"] == (
        "EARN_V163_COMPLETE_FROZEN_ROBUSTNESS_PREREGISTRATION"
    )
    assert result["authority"]["training"] is False
