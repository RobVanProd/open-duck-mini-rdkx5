from __future__ import annotations

import json
from pathlib import Path


ANALYSIS = Path(__file__).resolve().parents[1] / "outputs" / "analysis"


def test_t138_preregistration_when_present() -> None:
    path = ANALYSIS / "t138_expert_bank_causality_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PREREGISTERED_T138_EXPERT_BANK_CAUSALITY_AUDIT"
    )
    assert value["execution_now"]["formal_behavior_cells"] == 0


def test_t138_result_when_present() -> None:
    path = ANALYSIS / "t138_expert_bank_causality_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_T138_EXPERT_BANK_CAUSALITY_AUDIT"
    assert value["failed_checks"] == []
    assert value["checks"][
        "both_checkpoint_pairs_differ_only_in_expert_parameters"
    ]
    assert value["execution"]["formal_behavior_cells"] == 0
