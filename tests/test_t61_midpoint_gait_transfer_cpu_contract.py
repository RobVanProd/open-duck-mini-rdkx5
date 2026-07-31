from __future__ import annotations

import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = (
    ANALYSIS / "t61_midpoint_gait_transfer_cpu_preregistration.json"
)
RESULT = ANALYSIS / "t61_midpoint_gait_transfer_cpu_result.json"


def test_t61_cpu_preregistration_is_fixed_and_cpu_only() -> None:
    if not PREREG.exists():
        pytest.skip("T61 CPU preregistration has not been built")
    value = json.loads(PREREG.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PREREGISTERED_T61_MIDPOINT_GAIT_TRANSFER_CPU_CONTRACT"
    )
    assert value["failed_checks"] == []
    mechanism = value["mechanism"]
    assert mechanism["midpoint_stage"] == (
        "support_reward + 0.5 * complete_frozen_locomotion_reward"
    )
    assert not mechanism["scalar_sweep"]
    assert not mechanism["policy_abi_change"]
    assert value["cpu_contract"]["midpoint_simulator_steps"] == 1024
    assert value["cpu_contract"]["full_transfer_simulator_steps"] == 1024
    assert value["authority"]["execute_one_2048_step_cpu_contract"]
    assert not value["authority"]["hosted_training"]


def test_t61_cpu_result_earns_only_hosted_preregistration() -> None:
    if not RESULT.exists():
        pytest.skip("formal T61 CPU contract has not run")
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PASS_T61_MIDPOINT_GAIT_TRANSFER_CPU_CONTRACT"
    )
    assert value["decision"] == (
        "EARN_T62_MIDPOINT_GAIT_TRANSFER_HOSTED_PREREGISTRATION"
    )
    assert value["failed_checks"] == []
    assert value["checks"]["midpoint_source_restore_exact"]
    assert value["checks"]["midpoint_step_zero_onnx_byte_exact_source"]
    assert value["checks"]["default_off_trajectory_bit_exact"]
    assert value["checks"]["midpoint_exercises_both_support_sides"]
    assert value["checks"]["transfer_exercises_both_support_sides"]
    assert value["execution"] == {
        "cpu_simulator_steps": 2048,
        "formal_behavior_cells": 0,
        "hosted_or_colab_compute": 0,
        "robot_or_rdk_access": 0,
    }
    assert value["authority"]["hosted_preregistration"]
    assert not value["authority"]["hosted_training"]
    assert not value["authority"]["gate5"]
