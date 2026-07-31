from __future__ import annotations

import json
from pathlib import Path


ANALYSIS = Path(__file__).resolve().parents[1] / "outputs" / "analysis"


def test_t141_preregistration_when_present() -> None:
    path = (
        ANALYSIS / "t141_expert_bank_negative_endpoint_preregistration.json"
    )
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PREREGISTERED_T141_EXPERT_BANK_NEGATIVE_ENDPOINT_MATRIX"
    )
    assert value["matrix"]["cells"] == 16
    assert value["matrix"]["both_checkpoints_required"]


def test_t141_result_when_present() -> None:
    path = ANALYSIS / "t141_expert_bank_negative_endpoint_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] in {
        "PASS_T141_EXPERT_BANK_NEGATIVE_ENDPOINT_MATRIX",
        "HOLD_T141_EXPERT_BANK_NEGATIVE_ENDPOINT_MATRIX",
    }
    assert value["execution"]["behavior_cells"] == 16
    assert value["execution"]["optimizer_steps"] == 0
