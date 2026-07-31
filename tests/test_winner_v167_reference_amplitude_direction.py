from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
PREREGISTRATION_SHA256 = (
    "9b66bfd6f787ac85ad218e24e4908bdb4ac32f6218ae502e7893203f7e55c299"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_v167_preregistration_when_present() -> None:
    path = (
        ANALYSIS
        / "winner_v167_reference_amplitude_direction_preregistration.json"
    )
    if not path.exists():
        return
    assert sha256(path) == PREREGISTRATION_SHA256
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PREREGISTERED_WINNER_V167_REFERENCE_AMPLITUDE_DIRECTION"
    )
    assert value["failed_checks"] == []
    assert value["screen"]["event_count"] == 12
    assert value["mechanism"]["scale"] == (
        value["mechanism"]["torque_limit_nm"]
        / value["mechanism"]["observed_worst_v140_peak_nm"]
    )
    assert value["authority"]["simulation"] is False
    assert value["authority"]["training"] is False
    assert value["authority"]["production_contract_change"] is False


def test_v167_result_when_present() -> None:
    path = ANALYSIS / "winner_v167_reference_amplitude_direction_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] in {
        "PASS_WINNER_V167_REFERENCE_AMPLITUDE_DIRECTION",
        "HOLD_WINNER_V167_REFERENCE_AMPLITUDE_DIRECTION",
    }
    assert value["summary"]["events"] == 12
    assert value["authority"]["simulation"] is False
    assert value["authority"]["training"] is False
    assert value["authority"]["production_contract_change"] is False
