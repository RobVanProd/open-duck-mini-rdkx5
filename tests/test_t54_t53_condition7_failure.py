from __future__ import annotations

import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
RESULT = (
    ROOT
    / "outputs"
    / "analysis"
    / "t54_t53_condition7_failure_attribution.json"
)


def test_t54_attributes_dynamic_support_failure_without_training() -> None:
    if not RESULT.exists():
        pytest.skip("formal T54 attribution has not run")
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PASS_T54_T53_CONDITION7_FAILURE_ATTRIBUTION"
    )
    assert value["decision"] == (
        "EARN_T55_DYNAMIC_SINGLE_SUPPORT_CURRICULUM_"
        "CPU_CONTRACT_PREREGISTRATION_ONLY"
    )
    assert value["classification"] == (
        "NEGATIVE_COM_DYNAMIC_SUPPORT_CONTROL_INADEQUATE"
    )
    assert value["failed_checks"] == []
    summary = value["summary"]
    assert summary["green_cells"] == 8
    assert summary["x0_green_cells"] == 4
    assert summary["moving_green_cells"] == 4
    assert summary["moving_failed_cells"] == 8
    assert summary["failure_onset_tick_min"] == 139
    assert summary["failure_onset_tick_max"] == 382
    assert summary["failure_onset_support_counts"] == {
        "double": 2,
        "left_only": 6,
        "right_only": 0,
    }
    assert summary["capture_point_support_margin_p05_m"][
        "ranges_overlap"
    ]
    assert summary[
        "capture_minus_pressure_rolling32_minimum_mean_m"
    ]["ranges_overlap"]
    assert value["successor_constraints"]["automatic_sim_measurement_only"]
    assert not value["successor_constraints"]["policy_abi_change"]
    assert value["authority"]["t55_cpu_contract_preregistration"]
    assert not value["authority"]["hosted_training"]
    assert value["execution"] == {
        "hosted_compute_units": 0,
        "new_behavior_cells": 0,
        "optimizer_steps": 0,
        "robot_or_rdk_access": 0,
    }
