from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
sys.path.insert(0, str(ROOT / "tools"))

from run_t5_actuator_protection_reanalysis import (  # noqa: E402
    corrected_failure_reasons,
    duration_metrics,
)


def load(name: str) -> dict:
    return json.loads((ANALYSIS / name).read_text(encoding="utf-8"))


def test_t5_rule_removes_only_obsolete_peak_failures() -> None:
    force = np.zeros((600, 14), dtype=np.float64)
    force[10:20, 3] = 2.1
    duration = duration_metrics(
        force,
        motor_constant_nm_per_a=0.784532,
        overcurrent_threshold_a=2.0,
        overload_threshold_nm=1.5298374,
        trip_ticks=100,
    )
    assert duration["worst_strict_overcurrent_run_ticks"] == 10
    assert duration["worst_strict_overload_run_ticks"] == 10
    assert corrected_failure_reasons(
        [
            "current_peak_at_most_2p5",
            "torque_peak_at_most_1p91229675_nm",
        ],
        duration,
    ) == []
    assert corrected_failure_reasons(
        ["tracking_p95_at_most_0p20"],
        duration,
    ) == ["tracking_p95_at_most_0p20"]


def test_t26_preregistration_is_read_only_and_frozen() -> None:
    value = load("t26_t23_corrected_nominal_preregistration.json")
    assert value["status"] == (
        "PREREGISTERED_T26_T23_CORRECTED_NOMINAL_RECLASSIFICATION"
    )
    assert value["failed_checks"] == []
    assert all(value["checks"].values())
    assert value["external_run_manifest"]["cell_files"] == 16
    assert value["external_run_manifest"]["trace_files"] == 16
    frozen = value["frozen_reclassification"]
    assert frozen["expected_cells"] == 16
    assert frozen["cells_per_checkpoint"] == 8
    assert frozen["simulation_ticks"] == 0
    assert frozen["optimizer_steps"] == 0
    assert value["authority"]["robustness_execution_authorized"] is False
    assert value["authority"]["gate5_authorized"] is False


def test_t26_result_requires_both_checkpoint_pairs() -> None:
    value = load("t26_t23_corrected_nominal_result.json")
    assert value["status"] == (
        "PASS_T26_T23_CORRECTED_NOMINAL_PERSISTENCE"
    )
    assert value["decision"] == (
        "EARN_T23_FULL_ROBUSTNESS_MATRIX_PREREGISTRATION"
    )
    assert value["summary"]["cells"] == 16
    assert value["summary"]["original_passing_cells"] == 6
    assert value["summary"]["corrected_passing_cells"] == 16
    assert value["summary"]["persistent_both_checkpoint_pass"] is True
    assert value["summary"]["all_nonprotection_failures_absent"] is True
    assert all(
        row["corrected_all_eight_pass"]
        for row in value["per_checkpoint"]
    )
    assert value["authority"]["robustness_preregistration_authorized"] is True
    assert value["authority"]["robustness_execution_authorized"] is False
    assert value["authority"]["gate5_authorized"] is False
