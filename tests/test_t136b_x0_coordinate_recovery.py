from __future__ import annotations

import json
from pathlib import Path


ANALYSIS = Path(__file__).resolve().parents[1] / "outputs" / "analysis"


def test_t136b_preregistration_when_present() -> None:
    path = ANALYSIS / "t136b_x0_coordinate_recovery_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PREREGISTERED_T136B_X0_COORDINATE_RECOVERY"
    )
    assert value["execution_now"]["formal_behavior_cells"] == 0


def test_t136b_result_when_present() -> None:
    path = ANALYSIS / "t136b_x0_coordinate_recovery_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_T136B_X0_COORDINATE_RECOVERY"
    assert value["failed_checks"] == []
    assert value["checks"][
        "all_x0_source_transformed_outputs_bit_exact"
    ]
    assert value["execution"]["formal_behavior_cells"] == 0
