from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from run_t1_accel_bias_dose_response import decide, encode_nonfinite  # noqa: E402


COMMANDS = [0.0, 0.04, 0.074, 0.077, 0.08]
BIASES = [-2.0, -1.6, -1.2, -0.8, -0.4, 0.0, 0.4, 0.8, 1.2, 1.6, 2.0]
METRICS = [
    "mean_local_vx_m_s",
    "command_tracking_ratio",
    "body_pitch_mean_rad",
    "body_pitch_max_rad",
    "body_pitch_abs_max_rad",
    "pitch_chain_target_velocity_p95_max_rad_s",
    "actuator_force_peak_nm",
]


def prereg() -> dict:
    return {
        "frozen_configuration": {
            "commands_x_m_s": COMMANDS,
            "biases_m_s2": BIASES,
        },
        "decision_rule": {
            "close_metrics": METRICS,
            "first_order_support_if_any": {
                "mean_local_vx_relative_degradation_gte": 0.4,
                "fall_count_increase_gte": 2,
                "mean_body_pitch_forward_shift_rad_gte": 0.05235987755982989,
            },
        },
    }


def groups() -> list[dict]:
    result = []
    for bias in BIASES:
        for command in COMMANDS:
            result.append(
                {
                    "bias_m_s2": bias,
                    "command_x_m_s": command,
                    "aggregate": {
                        "fall_count": 0,
                        "mean_local_vx_m_s": 0.08,
                        "command_tracking_ratio": 1.0,
                        "body_pitch_mean_rad": 0.05,
                        "body_pitch_max_rad": 0.10,
                        "body_pitch_abs_max_rad": 0.10,
                        "pitch_chain_target_velocity_p95_max_rad_s": 2.0,
                        "actuator_force_peak_nm": 1.0,
                    },
                }
            )
    return result


def group(rows: list[dict], bias: float, command: float) -> dict:
    return next(
        row["aggregate"]
        for row in rows
        if row["bias_m_s2"] == bias and row["command_x_m_s"] == command
    )


def test_close_when_every_aggregate_is_identical() -> None:
    result = decide(prereg(), groups())
    assert result["status"] == "CLOSE_T1_ACCEL_BIAS_CAUSE"
    assert result["close_rule"]["passed"] is True


def test_primary_vx_degradation_supports_t1() -> None:
    rows = groups()
    group(rows, 1.6, 0.08)["mean_local_vx_m_s"] = 0.048
    result = decide(prereg(), rows)
    assert result["status"] == "SUPPORT_T1_ACCEL_BIAS_FIRST_ORDER_CAUSE"
    assert (
        result["primary_x008"]["triggers"][
            "mean_local_vx_relative_degradation"
        ]["triggered"]
        is True
    )


def test_primary_falls_support_t1() -> None:
    rows = groups()
    group(rows, 1.6, 0.08)["fall_count"] = 2
    result = decide(prereg(), rows)
    assert result["status"] == "SUPPORT_T1_ACCEL_BIAS_FIRST_ORDER_CAUSE"
    assert (
        result["primary_x008"]["triggers"]["fall_count_increase"]["triggered"]
        is True
    )


def test_primary_forward_pitch_supports_t1() -> None:
    rows = groups()
    group(rows, 1.6, 0.08)["body_pitch_mean_rad"] += 0.05235987755982989
    result = decide(prereg(), rows)
    assert result["status"] == "SUPPORT_T1_ACCEL_BIAS_FIRST_ORDER_CAUSE"
    assert (
        result["primary_x008"]["triggers"][
            "mean_body_pitch_forward_shift_rad"
        ]["triggered"]
        is True
    )


def test_nonprimary_large_change_is_inconclusive() -> None:
    rows = groups()
    group(rows, -2.0, 0.074)["actuator_force_peak_nm"] = 1.11
    result = decide(prereg(), rows)
    assert result["status"] == "INCONCLUSIVE_T1_T2_RAW_TELEMETRY_REQUIRED"
    assert result["close_rule"]["passed"] is False


def test_nonfinite_diagnostic_values_are_losslessly_labeled() -> None:
    result = encode_nonfinite(
        {"values": [1.0, float("inf"), float("-inf"), float("nan")]}
    )
    assert result == {
        "values": [1.0, "Infinity", "-Infinity", "NaN"]
    }
