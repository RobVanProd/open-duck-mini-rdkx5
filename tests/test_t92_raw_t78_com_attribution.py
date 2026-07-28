from __future__ import annotations

import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "t92_raw_t78_com_attribution_preregistration.json"
RESULT = ANALYSIS / "t92_raw_t78_com_attribution_result.json"


def test_t92_preregistration_is_exact_and_diagnostic_only() -> None:
    if not PREREG.exists():
        pytest.skip("T92 preregistration has not been built")
    value = json.loads(PREREG.read_text(encoding="utf-8"))
    assert value["status"] == "PREREGISTERED_T92_RAW_T78_COM_ATTRIBUTION"
    assert value["failed_checks"] == []
    assert value["condition"] == {
        "condition_index": 7,
        "id": "TORSO_COM_X_NEG",
        "override": {"torso_com_offset_m": [-0.05, 0.0, 0.0]},
    }
    assert value["matrix"]["cells"] == 16
    assert value["matrix"]["diagnostic_only"]
    assert not value["matrix"]["checkpoint_selection"]
    assert value["baselines"] == {
        "raw_t78_nominal_green_cells": 14,
        "t67_core_endpoint_green_cells": 6,
        "t84_rolling_endpoint_green_cells": 4,
    }
    assert value["execution_now"] == {
        "formal_behavior_cells": 0,
        "hosted_compute_units": 0,
        "optimizer_steps": 0,
        "robot_or_rdk_access": 0,
    }


def test_t92_result_follows_frozen_three_way_classification() -> None:
    if not RESULT.exists():
        pytest.skip("formal T92 attribution has not run")
    value = json.loads(RESULT.read_text(encoding="utf-8"))
    assert value["status"] == "PASS_T92_RAW_T78_COM_ATTRIBUTION"
    assert value["summary"]["completed_cells"] == 16
    green = value["summary"]["green_cells"]
    if green == 16:
        expected = (
            "RAW_ENDPOINT_LEARNED_ROLLING_TRANSFORM_DESTROYED_IT",
            "EARN_COTRAINING_CONFLICT_CPU_FALSIFIER_"
            "PREREGISTRATION_ONLY",
        )
    elif green > 6:
        expected = (
            "RAW_ENDPOINT_PARTIALLY_LEARNED_BUT_NOT_PERSISTENT",
            "EARN_SPECIALIST_CAPACITY_CPU_FALSIFIER_"
            "PREREGISTRATION_ONLY",
        )
    else:
        expected = (
            "NO_GAIN_OVER_T67_CORE_ENDPOINT_BASELINE",
            "CLOSE_T78_ADAPTER_ENDPOINT_CONTINUATION",
        )
    assert (value["classification"], value["decision"]) == expected
    assert sum(item["cells"] for item in value["per_checkpoint"]) == 16
    assert not value["interpretation"]["hosted_run_earned"]
