from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"


def test_t244_contract_source() -> None:
    builder = (
        ROOT
        / "tools/build_t244_home_negative_low_command_behavior_preregistration.py"
    ).read_text(encoding="utf-8")
    runner = (
        ROOT / "tools/run_t244_home_negative_low_command_behavior.py"
    ).read_text(encoding="utf-8")
    assert "single_cell_is_exact_prior_failure" in builder
    assert '"cells": 1' in builder
    assert "stop_on_failure" in builder
    assert "corrected_joint_offset_readback" in runner
    assert "duration_protection_pass" in runner
    assert "maximum_full_measured_vector_excess_rad_s" in runner
    assert '"optimizer_steps": 0' in runner


def test_t244_result_when_present() -> None:
    path = (
        ANALYSIS / "t244_home_negative_low_command_behavior_result.json"
    )
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["execution"]["formal_t244_behavior_cells"] == 1
    assert value["execution"]["optimizer_steps"] == 0
    assert value["authority"]["gate5"] is False
    if value["status"] == "PASS_T244_HOME_NEGATIVE_LOW_COMMAND_BEHAVIOR":
        assert value["cell"]["cell_green"]
        assert value["cell"]["behavior"]["samples"] == 600
        assert value["cell"]["trace_valid"]
        assert value["cell"]["override_readback_exact"]
        assert (
            value["decision"]
            == "EARN_T245_HOME_NEGATIVE_FLOOR_REMAINING_MATRIX_"
            "PREREGISTRATION_ONLY"
        )
        assert value["authority"]["remaining_matrix_preregistration"]
