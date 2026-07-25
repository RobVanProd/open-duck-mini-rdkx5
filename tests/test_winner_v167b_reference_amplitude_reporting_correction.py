from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
CORRECTION_SHA256 = (
    "6fef12181f939491498184ca4b052e1eee99ebc3ddc1e2435aa6e5bef391e4f8"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_v167b_reporting_correction_when_present() -> None:
    path = (
        ANALYSIS
        / "winner_v167b_reference_amplitude_reporting_correction.json"
    )
    if not path.exists():
        return
    assert sha256(path) == CORRECTION_SHA256
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PASS_WINNER_V167B_REFERENCE_AMPLITUDE_REPORTING_CORRECTION"
    )
    assert value["failed_checks"] == []
    assert value["observed_issue"]["mechanism_alignment_counts_affected"] is False
    assert value["correction"]["shadow_scale_changed"] is False
    assert value["correction"]["event_population_changed"] is False
    assert value["correction"]["pass_rule_changed"] is False
    assert value["authority"]["simulation"] is False
    assert value["authority"]["training"] is False
