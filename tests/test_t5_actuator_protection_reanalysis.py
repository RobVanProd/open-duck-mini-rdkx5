from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from run_t5_actuator_protection_reanalysis import (  # noqa: E402
    clipping_metrics,
    corrected_failure_reasons,
    duration_metrics,
    longest_true_run,
)


def model() -> dict:
    return {
        "qpos_indices": list(range(14)),
        "qvel_indices": list(range(14)),
        "kp_nm_per_rad": [17.11] * 14,
        "kv_nm_s_per_rad": [0.0] * 14,
        "forcerange_nm": [[-3.23, 3.23] for _ in range(14)],
        "sim_dt_s": 0.002,
        "reconstruction_tolerance_nm": 5.0e-6,
    }


def test_longest_true_run_is_consecutive_not_occupancy() -> None:
    assert longest_true_run([True, True, False, True, True, True]) == 3
    assert longest_true_run([False, False]) == 0


def test_duration_rule_accepts_99_and_rejects_100_ticks() -> None:
    threshold_nm = 0.8 * 19.5 * 0.0980665
    force = np.zeros((120, 14), dtype=float)
    force[:99, 0] = threshold_nm + 0.01
    passing = duration_metrics(
        force,
        motor_constant_nm_per_a=0.784532,
        overcurrent_threshold_a=2.0,
        overload_threshold_nm=threshold_nm,
        trip_ticks=100,
    )
    assert passing["worst_strict_overload_run_ticks"] == 99
    assert passing["pass"] is True

    force[99, 0] = threshold_nm + 0.01
    failing = duration_metrics(
        force,
        motor_constant_nm_per_a=0.784532,
        overcurrent_threshold_a=2.0,
        overload_threshold_nm=threshold_nm,
        trip_ticks=100,
    )
    assert failing["worst_strict_overload_run_ticks"] == 100
    assert failing["pass"] is False


def test_instantaneous_stall_failures_are_removed_but_other_gates_remain() -> None:
    duration = {
        "overcurrent_duration_pass": True,
        "overload_duration_pass": True,
    }
    assert corrected_failure_reasons(
        [
            "current_peak_at_most_2p5",
            "torque_peak_at_most_1p91229675_nm",
        ],
        duration,
    ) == []
    assert corrected_failure_reasons(
        [
            "torque_peak_at_most_1p91229675_nm",
            "tracking_p95_at_most_0p20",
        ],
        duration,
    ) == ["tracking_p95_at_most_0p20"]


def test_duration_failures_are_added_deterministically() -> None:
    failures = corrected_failure_reasons(
        [],
        {
            "overcurrent_duration_pass": False,
            "overload_duration_pass": False,
        },
    )
    assert failures == [
        "overcurrent_gt_2a_reaches_100_consecutive_ticks",
        "overload_gt_80pct_stall_reaches_100_consecutive_ticks",
    ]


def test_force_clipping_reconstruction_distinguishes_demand_from_output() -> None:
    applied = np.zeros(14)
    applied[0] = 4.0 / 17.11
    unclipped_force = 17.11 * applied
    actual_force = np.clip(unclipped_force, -3.23, 3.23)
    row = {
        "qpos": [0.0] * 14,
        "qvel": [0.0] * 14,
        "applied_target_rad": applied.tolist(),
        "actuator_force_nm": actual_force.tolist(),
    }
    result = clipping_metrics([row], model())
    assert result["reconstruction_within_tolerance"] is True
    assert result["clipped_joint_ticks"] == 1
    assert result["clipped_joints"] == ["left_hip_yaw"]
    assert result["unclipped_peak_torque_nm"] == pytest.approx(4.0)
    assert result["actual_peak_torque_nm"] == pytest.approx(3.23)


def test_old_decimal_gate_has_no_float32_value_above_baseline_below_gate() -> None:
    baseline = np.float32(1.9122966527938843)
    old_gate = 1.91229675
    next_value = np.nextafter(baseline, np.float32(np.inf))
    assert float(baseline) < old_gate
    assert float(next_value) > old_gate
    assert not (float(baseline) < float(next_value) < old_gate)


def test_preregistration_freezes_duration_protection_and_decision_population() -> None:
    payload = json.loads(
        (
            ROOT
            / "outputs/analysis/t5_actuator_protection_reanalysis_preregistration.json"
        ).read_text(encoding="utf-8")
    )
    assert (
        payload["status"]
        == "PREREGISTERED_T5_ACTUATOR_PROTECTION_REANALYSIS"
    )
    protection = payload["corrected_protection_contract"]
    assert protection["trip_ticks"] == 100
    assert protection["pass_max_consecutive_ticks"] == 99
    assert protection["overcurrent_threshold_a"] == 2.0
    assert protection["overload_fraction_of_stall"] == 0.8
    assert protection["overload_threshold_nm"] == pytest.approx(1.5298374)
    assert payload["decision_rule"][
        "previously_rejected_complete_candidates"
    ] == ["V121", "V123", "V128"]
    assert (
        payload["decision_rule"]["minimum_corrected_passes_to_reopen"] == 3
    )


def test_result_meets_frozen_reopen_trigger_and_preserves_authority() -> None:
    result = json.loads(
        (
            ROOT
            / "outputs/analysis/t5_actuator_protection_reanalysis_result.json"
        ).read_text(encoding="utf-8")
    )
    assert result["status"] == "PASS_T5_MIS_SPECIFIED_INSTANTANEOUS_CONSTRAINT"
    assert result["decision"] == "REOPEN_V121_V175_CAMPAIGN_CLOSURES"
    summary = result["decision_summary"]
    assert summary["corrected_complete_passes"] == ["V121", "V123", "V128"]
    assert summary["corrected_complete_pass_count"] == 3
    assert summary["frozen_reopen_trigger_met"] is True
    assert summary["post_handoff_v177_corrected_complete_pass"] is True
    assert summary["strict_between_old_baseline_and_gate_samples"] == 0
    assert summary["all_force_reconstructions_close"] is True
    assert result["baseline_clamp_audit"][
        "all_moving_peaks_equal_model_force_limit"
    ] is True
    assert all(
        row["simulator_clipped_joint_ticks"] == 0
        for row in result["candidate_reanalysis"]
    )
    assert result["authority"]["policy_selected"] is False
    assert result["authority"]["hosted_compute_authorized"] is False
    assert result["authority"]["robot_rdkx5_gate5_torque_motion"] is False
