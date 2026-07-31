from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_v161_preregistration_when_present() -> None:
    path = (
        ANALYSIS
        / "winner_v161_uniform_trust_projection_preregistration.json"
    )
    if not path.exists():
        return
    result = json.loads(path.read_text(encoding="utf-8"))
    assert sha256(path) == (
        "716c5d9e4f713a19e0608be4b290c797483d9e5035fdef64b70be7a003bd841f"
    )
    assert result["status"] == (
        "PREREGISTERED_WINNER_V161_UNIFORM_TRUST_PROJECTION"
    )
    assert result["failed_checks"] == []
    assert result["source_dataset"]["rows"] == 4_800
    assert result["projection"]["behavior_or_torque_used_for_alpha"] is False
    assert result["authority"]["training"] is False


def test_v161_result_when_present() -> None:
    path = ANALYSIS / "winner_v161_uniform_trust_projection_result.json"
    if not path.exists():
        return
    result = json.loads(path.read_text(encoding="utf-8"))
    assert sha256(path) == (
        "9392b27929c4e391d2b3a6ea1b8a8b965fef6550ab56beb28c15911f370b5d12"
    )
    assert result["status"] == (
        "PASS_WINNER_V161_UNIFORM_TRUST_PROJECTION"
    )
    assert result["failed_checks"] == []
    assert 0.0 < result["summary"]["selected_alpha"] < 1.0
    assert (
        result["summary"]["maximum_selected_action_mse_to_limit"] >= 0.99
    )
    assert result["decision"] == (
        "EARN_V162_UNIFORM_TRUST_PROJECTED_DUAL_CHECKPOINT_NOMINAL"
    )
    assert result["authority"]["training"] is False
