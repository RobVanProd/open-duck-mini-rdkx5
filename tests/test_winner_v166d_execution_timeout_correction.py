from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
CORRECTION_SHA256 = (
    "d6a08881a7eec4831f27369d6d5020f20bfa28caab608dac3ba418d0f9a01f08"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_v166d_execution_timeout_correction_when_present() -> None:
    path = ANALYSIS / "winner_v166d_execution_timeout_correction.json"
    if not path.exists():
        return
    assert sha256(path) == CORRECTION_SHA256
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PASS_WINNER_V166D_EXECUTION_TIMEOUT_CORRECTION"
    )
    assert value["failed_checks"] == []
    assert value["observed_failure"]["failed_files"] == []
    assert value["observed_failure"]["trace_written"] is False
    assert value["observed_failure"]["result_written"] is False
    assert value["correction"]["code_change"] is False
    assert value["correction"]["mechanism_change"] is False
    assert value["correction"]["policy_or_matrix_change"] is False
    assert value["authority"]["training"] is False
