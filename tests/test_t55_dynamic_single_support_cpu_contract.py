from __future__ import annotations

import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = (
    ANALYSIS / "t55_dynamic_single_support_cpu_preregistration.json"
)
RESULT = ANALYSIS / "t55_dynamic_single_support_cpu_result.json"


def test_t55_cpu_preregistration_is_frozen_without_hosted_authority() -> None:
    if not PREREG.exists():
        pytest.skip("T55 CPU preregistration has not been built")
    value = json.loads(PREREG.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PREREGISTERED_T55_DYNAMIC_SINGLE_SUPPORT_CPU_CONTRACT"
    )
    assert value["failed_checks"] == []
    assert value["mechanism"]["manual_mass_com_or_foot_measurement"] is False
    assert value["mechanism"]["policy_abi_change"] is False
    assert value["cpu_contract"]["balance_simulator_steps"] == 1024
    assert value["cpu_contract"]["transfer_simulator_steps"] == 1024
    assert value["authority"]["execute_one_2048_step_cpu_contract"]
    assert not value["authority"]["hosted_training"]


def test_t55_cpu_result_earns_only_hosted_preregistration() -> None:
    if not RESULT.exists():
        pytest.skip("formal T55 CPU contract has not run")
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PASS_T55_DYNAMIC_SINGLE_SUPPORT_CPU_CONTRACT"
    )
    assert value["decision"] == (
        "EARN_T56_DYNAMIC_SINGLE_SUPPORT_HOSTED_PREREGISTRATION"
    )
    assert value["failed_checks"] == []
    assert value["checks"]["materialized_deployment_byte_exact_t52_half"]
    assert value["checks"]["default_off_trajectory_bit_exact"]
    assert value["checks"]["balance_stage_exercises_both_support_sides"]
    assert value["checks"]["transfer_stage_exercises_both_support_sides"]
    assert value["execution"] == {
        "cpu_simulator_steps": 2048,
        "formal_behavior_cells": 0,
        "hosted_or_colab_compute": 0,
        "robot_or_rdk_access": 0,
    }
    assert value["authority"]["hosted_preregistration"]
    assert not value["authority"]["hosted_training"]
    assert not value["authority"]["gate5"]
