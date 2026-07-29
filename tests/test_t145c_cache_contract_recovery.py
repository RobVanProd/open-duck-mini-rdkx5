from __future__ import annotations

import json
from pathlib import Path


ANALYSIS = Path(__file__).resolve().parents[1] / "outputs" / "analysis"


def test_t145c_preregistration_when_present() -> None:
    path = ANALYSIS / "t145c_cache_contract_recovery_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["recovery_kind"] == (
        "T145B_ORIGINAL_CACHE_CONTRACT_REJECTION"
    )
    assert value["execution_now"]["t145b_new_behavior_cells"] == 0
    assert value["execution_now"]["recovery_remaining_behavior_cells"] == 8


def test_t145c_result_when_present() -> None:
    path = ANALYSIS / "t145c_cache_contract_recovery_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["execution"]["behavior_cells"] == 16
    assert value["execution"]["t145b_new_behavior_cells"] == 0
    assert value["execution"]["recovery_new_behavior_cells"] == 8
    assert value["status"] in {
        "PASS_T145C_CONDITIONAL_PATH_NEGATIVE_ENDPOINT_MATRIX",
        "HOLD_T145C_CONDITIONAL_PATH_NEGATIVE_ENDPOINT_MATRIX",
    }
