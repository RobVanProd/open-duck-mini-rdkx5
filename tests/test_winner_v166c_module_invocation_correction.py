from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
CORRECTION_SHA256 = (
    "84565bdf42e7e2c3b8b4b19f4095e7d7626eaac4d3c2eafb07cab005aa3a5bc8"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_v166c_module_invocation_correction_when_present() -> None:
    path = ANALYSIS / "winner_v166c_module_invocation_correction.json"
    if not path.exists():
        return
    assert sha256(path) == CORRECTION_SHA256
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PASS_WINNER_V166C_MODULE_INVOCATION_CORRECTION"
    )
    assert value["failed_checks"] == []
    assert value["observed_failure"]["run_root_created"] is False
    assert value["observed_failure"]["trace_written"] is False
    assert value["observed_failure"]["result_written"] is False
    assert value["correction"]["code_change"] is False
    assert value["correction"]["mechanism_change"] is False
    assert value["correction"]["policy_or_matrix_change"] is False
    assert value["authority"]["training"] is False
