from __future__ import annotations

import json
from pathlib import Path


ANALYSIS = Path(__file__).resolve().parents[1] / "outputs" / "analysis"


def test_t130c_preregistration_when_present() -> None:
    path = ANALYSIS / "t130c_step_zero_serialization_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PREREGISTERED_T130C_STEP_ZERO_SERIALIZATION_RECOVERY"
    )
    assert value["correction_from_t130b"] == {
        "cause": (
            "The T130B verifier called a receipt helper requiring a kind "
            "field, but T130B froze plain file receipts."
        ),
        "precomparison": True,
        "result_written": False,
        "work_root_created": False,
        "changed_scientific_hypothesis": False,
    }
    assert value["expected_difference"]["expected_only_initializers"] == [
        "zero_adapter_location"
    ]


def test_t130c_result_when_present() -> None:
    path = ANALYSIS / "t130c_step_zero_serialization_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == (
        "HOLD_T130C_STEP_ZERO_SERIALIZATION_RECOVERY"
    )
    assert value["classification"] == "UNRESOLVED_STEP_ZERO_MISMATCH"
    assert value["failed_checks"] == [
        "nodes_bit_exact",
        "only_expected_unused_initializer_omitted",
    ]
    assert value["facts"]["trace"]["bit_exact_rows"] == 72
    assert value["facts"]["random_chain"]["bit_exact_steps"] == 256
    assert value["execution"] == {
        "optimizer_steps": 0,
        "simulator_steps": 0,
        "formal_behavior_cells": 0,
        "hosted_compute_units": 0,
        "robot_or_rdk_access": 0,
    }
