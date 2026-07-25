from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
CORRECTION_SHA256 = (
    "5387506c639498fc315b3d2366acc236644ac051ad1de2f698e35466e125baad"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_v166b_transport_reporting_correction_when_present() -> None:
    path = ANALYSIS / "winner_v166b_transport_reporting_correction.json"
    if not path.exists():
        return
    assert sha256(path) == CORRECTION_SHA256
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PASS_WINNER_V166B_TRANSPORT_REPORTING_CORRECTION"
    )
    assert value["failed_checks"] == []
    assert value["observed_failure"]["classified_cell_written"] is False
    assert value["observed_failure"]["result_written"] is False
    assert value["observed_failure"][
        "orphan_trace_not_inspected_for_behavior"
    ]
    assert value["correction"]["mechanism_change"] is False
    assert value["correction"]["factor_change"] is False
    assert value["correction"]["interpolation_change"] is False
    assert value["correction"]["policy_or_matrix_change"] is False
    assert value["correction"]["gate_or_stop_rule_change"] is False
    assert value["authority"]["training"] is False
