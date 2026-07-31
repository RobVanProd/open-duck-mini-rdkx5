from __future__ import annotations

import json
from pathlib import Path


ANALYSIS = Path(__file__).resolve().parents[1] / "outputs" / "analysis"


def test_t130d_preregistration_when_present() -> None:
    path = ANALYSIS / "t130d_step_zero_node_name_preregistration.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PREREGISTERED_T130D_STEP_ZERO_NODE_NAME_RECOVERY"
    )
    assert value["expected_difference"] == {
        "node_index": 27,
        "expected_name": "t109_always_on_negative_adapter",
        "hosted_name": "",
        "op_type": "Identity",
        "inputs": ["negative_adapter_location"],
        "outputs": ["conditional_adapter_location"],
        "trace_rows_bit_exact": 72,
        "random_chain_steps_bit_exact": 256,
    }


def test_t130d_result_when_present() -> None:
    path = ANALYSIS / "t130d_step_zero_node_name_result.json"
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PASS_T130D_STEP_ZERO_NODE_NAME_RECOVERY"
    )
    assert value["classification"] == (
        "OPTIONAL_ONNX_NODE_NAME_METADATA_ONLY"
    )
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert value["execution"] == {
        "optimizer_steps": 0,
        "simulator_steps": 0,
        "formal_behavior_cells": 0,
        "hosted_compute_units": 0,
        "robot_or_rdk_access": 0,
    }
