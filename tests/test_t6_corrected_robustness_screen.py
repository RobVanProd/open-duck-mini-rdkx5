from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from run_t6_corrected_robustness_screen import (  # noqa: E402
    classify_behavior,
    load_abi_amendment,
    longest_true_run,
    selection_key,
    trace_summary,
)


def behavior_contract() -> dict:
    return {
        "x0_core": {
            "samples": 600,
            "maximum_body_pitch_p95_rad": 0.25,
            "minimum_base_height_m": 0.12,
            "maximum_action_saturation_pct": 1.0,
            "maximum_absolute_mean_local_vx_m_s": 0.02,
        },
        "moving_core": {
            "samples": 600,
            "maximum_body_pitch_p95_rad": 0.25,
            "minimum_base_height_m": 0.12,
            "maximum_action_saturation_pct": 1.0,
            "minimum_track_ratio": 0.25,
        },
        "x0_replacement_quality": {
            "maximum_pitch_tracking_p95_rad": 0.20,
            "maximum_rate_excess_rad_s": 0.0,
            "maximum_action_saturation_pct": 0.0,
        },
        "moving_replacement_quality": {
            "maximum_pitch_tracking_p95_rad": 0.20,
            "maximum_rate_excess_rad_s": 0.0,
            "maximum_action_saturation_pct": 0.0,
        },
    }


def behavior_row(command: float = 0.08) -> dict:
    return {
        "command_x_m_s": command,
        "samples": 600,
        "termination_reason": "duration_complete",
        "emergence_pass": True,
        "left_contact_transitions": 4,
        "right_contact_transitions": 4,
        "mean_local_vx_m_s": 0.06 if command else 0.0,
        "track_ratio": 0.75 if command else None,
        "body_pitch_p95_rad": 0.10,
        "minimum_base_height_m": 0.14,
        "pitch_tracking_p95_rad": 0.18,
        "action_saturation_pct": 0.0,
        "p95_rate_excess_rad_s": 0.0,
        "instant_rate_excess_rad_s": 0.0,
    }


def protection_contract() -> dict:
    return {
        "motor_constant_nm_per_a": 0.784532,
        "overcurrent_threshold_a": 2.0,
        "overload_threshold_nm": 1.5298374,
        "pass_max_consecutive_ticks": 99,
        "simulator_force_limit_abs_nm": 3.23,
        "force_limit_tolerance_nm": 5.0e-6,
    }


def write_trace(path: Path, overload_ticks: int) -> None:
    rows = []
    for tick in range(120):
        force = [0.0] * 14
        if tick < overload_ticks:
            force[0] = 1.6
        rows.append(
            {
                "mode": "fitted",
                "tick": tick,
                "actuator_force_nm": force,
                "conservative_rate_excess_rad_s": [0.0] * 14,
            }
        )
    path.write_text(
        "".join(json.dumps(row) + "\n" for row in rows),
        encoding="utf-8",
    )


def test_longest_true_run_is_consecutive() -> None:
    assert longest_true_run(
        np.asarray([True, True, False, True, True, True])
    ) == 3


def test_trace_duration_rule_accepts_99_and_rejects_100(
    tmp_path: Path,
) -> None:
    passing = tmp_path / "passing.jsonl"
    write_trace(passing, 99)
    result = trace_summary(passing, protection_contract())
    assert result["worst_strict_overload_run_ticks"] == 99
    assert result["duration_protection_pass"] is True

    failing = tmp_path / "failing.jsonl"
    write_trace(failing, 100)
    result = trace_summary(failing, protection_contract())
    assert result["worst_strict_overload_run_ticks"] == 100
    assert result["duration_protection_pass"] is False


def test_core_and_replacement_quality_are_separate() -> None:
    row = behavior_row()
    row["pitch_tracking_p95_rad"] = 0.21
    result = classify_behavior(row, behavior_contract())
    assert result["core_pass"] is True
    assert result["replacement_quality_pass"] is False


def test_x0_core_preserves_stationary_semantics() -> None:
    result = classify_behavior(behavior_row(0.0), behavior_contract())
    assert result["core_pass"] is True
    assert result["replacement_quality_pass"] is True


def test_selection_prefers_duration_margin_before_tracking() -> None:
    order = ["V121", "V177"]
    lower_duration = {
        "candidate_id": "V121",
        "worst_strict_overload_run_ticks": 10,
        "worst_strict_overcurrent_run_ticks": 9,
        "worst_tracking_p95_rad": 0.19,
        "minimum_moving_vx_m_s": 0.05,
    }
    lower_tracking = {
        "candidate_id": "V177",
        "worst_strict_overload_run_ticks": 11,
        "worst_strict_overcurrent_run_ticks": 8,
        "worst_tracking_p95_rad": 0.15,
        "minimum_moving_vx_m_s": 0.08,
    }
    assert selection_key(lower_duration, order) < selection_key(
        lower_tracking,
        order,
    )


def test_preoutcome_abi_amendment_is_canonical_and_narrow() -> None:
    prereg = json.loads(
        (
            ROOT
            / "outputs/analysis/t6_corrected_robustness_screen_preregistration.json"
        ).read_text(encoding="utf-8")
    )
    amendment = load_abi_amendment(prereg)
    basis = {
        key: amendment[key]
        for key in (
            "original_preregistration",
            "preoutcome_evidence",
            "onnx_abi",
            "authorized_change",
            "corrected_runner_sha256",
            "unchanged_contract",
        )
    }
    canonical = json.dumps(
        basis,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode()
    assert (
        hashlib.sha256(canonical).hexdigest()
        == amendment["amendment_contract_sha256"]
    )
    assert amendment["preoutcome_evidence"][
        "behavior_cells_with_decision_weight"
    ] == 0
    assert amendment["authorized_change"]["new_state_inputs"] == [
        "previous_action",
        "h_in",
    ]
    assert amendment["authorized_change"]["new_state_outputs"] == [
        "previous_action_out",
        "h_out",
    ]
    assert all(
        value is True
        for key, value in amendment["unchanged_contract"].items()
        if key != "training_steps"
    )
    assert amendment["unchanged_contract"]["training_steps"] == 0
