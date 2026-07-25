from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
CORRECTION_SHA256 = (
    "6fef12181f939491498184ca4b052e1eee99ebc3ddc1e2435aa6e5bef391e4f8"
)
RESULT_SHA256 = (
    "c4cf9efc6421fd684bb5b05be78e89926273d3f168655c3b843bd726d7841ca3"
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


def test_v167b_corrected_result_when_present() -> None:
    path = (
        ANALYSIS / "winner_v167b_reference_amplitude_direction_result.json"
    )
    if not path.exists():
        return
    assert sha256(path) == RESULT_SHA256
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == (
        "HOLD_WINNER_V167_REFERENCE_AMPLITUDE_DIRECTION"
    )
    assert value["summary"]["original_graph_reproduction_linf"] == 0.0
    assert value["summary"]["same_nonzero_direction"] == 3
    assert value["summary"]["strict_error_reduction"] == 2
    assert value["decision"] == (
        "CLOSE_UNIFORM_REFERENCE_AMPLITUDE_CONTRACTION_NO_RETRY"
    )
    assert value["authority"]["behavior_preregistration"] is False
    assert value["authority"]["training"] is False
