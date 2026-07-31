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


def test_v152_selects_a_distinct_phase_contact_mechanism() -> None:
    result = load("winner_v152_phase_contact_alignment.json")
    assert sha256("winner_v152_phase_contact_alignment.json") == (
        "15d2a253d638dac796e0021cdb46daf70aee08ad3dd56ed1c265031548cfaaf7"
    )
    assert result["status"] == "PASS_WINNER_V152_PHASE_CONTACT_ALIGNMENT"
    assert result["failed_checks"] == []
    assert result["events"]["source_tick_separation"] == 189
    assert result["events"]["gait_periods_apart"] == 7
    phase_contact = result["phase_contact"]
    assert phase_contact["period_ticks"] == 27
    assert phase_contact["contacts"] == [0, 1]
    assert len(phase_contact["phase_contact_ticks_first"]) == 21
    assert len(phase_contact["phase_contact_ticks_second"]) == 21
    mechanism = result["selected_mechanism"]
    assert mechanism["source"] == (
        "V140 raw actor; no V148/V151 state-local centers"
    )
    assert mechanism["correction"] > 0
    assert result["decision"] == (
        "EARN_V153_PHASE_CONTACT_RESIDUAL_PREREGISTRATION"
    )
    assert result["authority"]["policy_change"] is False
