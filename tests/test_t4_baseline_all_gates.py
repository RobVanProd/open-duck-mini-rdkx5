from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from run_t4_baseline_all_gates import (  # noqa: E402
    aggregate_condition,
    gate_rows,
)


def cell(seed: int, vx: float = 0.08, track: float = 1.0) -> dict:
    return {
        "termination_reason": "duration_complete",
        "mean_local_vx_m_s": vx,
        "track_ratio": track,
        "max_pitch_tracking_p95_rad": 0.19,
        "max_p95_velocity_limit_excess_rad_s": 0.0,
        "max_instant_velocity_limit_excess_rad_s": 0.0,
        "max_action_saturation_pct": 0.0,
        "max_abs_body_pitch_p95_rad": 0.10,
        "min_base_height_m": 0.15,
        "min_reward_mean": 0.50,
        "candidate_gate_status": "PASS_CANDIDATE_SIM_GATE",
        "per_joint_sent_target_velocity_p95_rad_s": {
            "left_knee": 2.0 + seed * 0.01
        },
        "pitch_chain_velocity_limits_rad_s": {"left_knee": 3.25},
    }


def prereg() -> dict:
    return {
        "gate_contract": {
            "coded_candidate_gate": [
                {
                    "metric": "max_action_saturation_pct",
                    "operator": "lte",
                    "threshold": 1.0,
                },
                {
                    "metric": "min_seed_track_ratio",
                    "operator": "gte",
                    "threshold": 0.25,
                    "applies_if_abs_command_gte": 0.02,
                },
            ],
            "documented_promotion_x008": [
                {
                    "metric": "mean_track_ratio",
                    "operator": "gte",
                    "threshold": 0.50,
                }
            ],
            "documented_semantic_x000": [
                {
                    "metric": "mean_abs_vx_m_s",
                    "operator": "lte",
                    "threshold": 0.005,
                }
            ],
        }
    }


def test_condition_aggregate_uses_worst_gate_values() -> None:
    rows = [cell(seed) for seed in range(8)]
    rows[7]["max_pitch_tracking_p95_rad"] = 0.21
    rows[3]["termination_reason"] = "fall_or_nan"
    result = aggregate_condition(rows)
    assert result["duration_complete_count"] == 7
    assert result["fall_count"] == 1
    assert result["max_pitch_tracking_p95_rad"] == 0.21
    assert (
        result["per_joint_sent_target_velocity_p95_rad_s"]["left_knee"]
        == 2.07
    )


def test_x008_reports_documented_and_coded_forward_gates() -> None:
    rows = [cell(seed, vx=0.04, track=0.49) for seed in range(8)]
    aggregate = aggregate_condition(rows)
    result = gate_rows(
        prereg(),
        {"condition": "x0.080_vanilla", "command_x_m_s": 0.08},
        aggregate,
    )
    by_metric = {row["metric"]: row for row in result}
    assert by_metric["mean_track_ratio"]["passed"] is False
    assert by_metric["min_seed_track_ratio"]["passed"] is True


def test_x000_skips_coded_forward_ratio_and_checks_mean_abs_vx() -> None:
    rows = [cell(seed, vx=(-1) ** seed * 0.004, track=0.0) for seed in range(8)]
    aggregate = aggregate_condition(rows)
    result = gate_rows(
        prereg(),
        {"condition": "x0.000_fitted", "command_x_m_s": 0.0},
        aggregate,
    )
    metrics = {row["metric"] for row in result}
    assert "min_seed_track_ratio" not in metrics
    assert next(
        row for row in result if row["metric"] == "mean_abs_vx_m_s"
    )["passed"]
