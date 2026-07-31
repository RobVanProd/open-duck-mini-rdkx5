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


def test_v142_attributes_closed_loop_transfer_without_new_behavior() -> None:
    result = load("winner_v142_transferred_load_attribution.json")
    assert sha256("winner_v142_transferred_load_attribution.json") == (
        "38049a224d0d6190b6415a5691ecbabd9e5915ac8a6b788245abdc08b2234181"
    )
    assert result["status"] == (
        "PASS_WINNER_V142_TRANSFERRED_LOAD_ATTRIBUTION"
    )
    assert result["failed_checks"] == []
    assert result["source"]["left_knee_peak_nm"] > 1.91229675
    assert result["projected"]["left_knee_peak_nm"] < 1.91229675
    assert result["source"]["right_ankle_peak_nm"] < 1.91229675
    assert result["projected"]["right_ankle_peak_nm"] > 1.91229675
    teacher = result["teacher_at_new_peak"]
    assert teacher["right_ankle_action_delta"] == 0
    assert teacher["candidate_on_teacher_minus_base"] == 0
    assert result["decision"] == (
        "PREREGISTER_TORQUE_ONLY_PRESERVATION_CONSTRAINED_ACTOR_CPU"
    )
    assert result["authority"]["training"] is False
    assert result["authority"]["behavior"] is False
