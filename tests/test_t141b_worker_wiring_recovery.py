from __future__ import annotations

import json
from pathlib import Path


ANALYSIS = Path(__file__).resolve().parents[1] / "outputs" / "analysis"


def test_t141b_preregistration_when_present() -> None:
    path = ANALYSIS / "t141b_worker_wiring_recovery_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["recovery_kind"] == (
        "T141_PRE_BEHAVIOR_REPOSITORY_INPUT_WIRING"
    )
    assert value["execution_now"]["source_attempt_behavior_cells"] == 0
    assert "worker" in value["repository_inputs"]


def test_t141b_result_when_present() -> None:
    path = ANALYSIS / "t141b_worker_wiring_recovery_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] in {
        "PASS_T141B_EXPERT_BANK_NEGATIVE_ENDPOINT_MATRIX",
        "HOLD_T141B_EXPERT_BANK_NEGATIVE_ENDPOINT_MATRIX",
    }
    assert value["execution"]["behavior_cells"] == 16
    assert value["execution"]["optimizer_steps"] == 0
