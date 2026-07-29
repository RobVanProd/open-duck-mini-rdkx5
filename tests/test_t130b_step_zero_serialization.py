from __future__ import annotations

import json
from pathlib import Path


ANALYSIS = Path(__file__).resolve().parents[1] / "outputs" / "analysis"


def test_t130b_preregistration_when_present() -> None:
    path = ANALYSIS / "t130b_step_zero_serialization_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PREREGISTERED_T130B_STEP_ZERO_SERIALIZATION_RECOVERY"
    )
    assert value["expected_difference"]["expected_only_initializers"] == [
        "zero_adapter_location"
    ]


def test_t130b_result_when_present() -> None:
    path = ANALYSIS / "t130b_step_zero_serialization_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PASS_T130B_STEP_ZERO_SERIALIZATION_RECOVERY"
    )
    assert value["classification"] == (
        "EXPECTED_UNUSED_INITIALIZER_SERIALIZATION_DIFFERENCE"
    )
    assert value["execution"]["formal_behavior_cells"] == 0
