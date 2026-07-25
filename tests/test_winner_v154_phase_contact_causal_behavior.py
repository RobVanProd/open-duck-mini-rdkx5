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


def test_v154_preregisters_only_the_original_causal_cell() -> None:
    prereg = load(
        "winner_v154_phase_contact_causal_behavior_preregistration.json"
    )
    assert sha256(
        "winner_v154_phase_contact_causal_behavior_preregistration.json"
    ) == "0bf06e7821095c9167e38dff40a9ac7b134adf95a7cba0137b9947cd5d102ae2"
    assert prereg["status"] == (
        "PREREGISTERED_WINNER_V154_PHASE_CONTACT_CAUSAL_BEHAVIOR"
    )
    assert prereg["failed_checks"] == []
    assert prereg["matrix"]["rows"] == 1
    row = prereg["matrix"]["row"]
    assert row["plant"] == "P30_ALL_JOINT"
    assert row["command_x_m_s"] == 0.074
    assert row["seed"] == 167_931_544
    assert row["duration_ticks"] == 600
    assert prereg["authority"]["behavior_cells"] == 1
    assert prereg["authority"]["additional_behavior"] is False
    assert prereg["authority"]["training"] is False
    assert prereg["authority"]["policy_deployment"] is False
