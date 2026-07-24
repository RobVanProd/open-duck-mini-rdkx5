#!/usr/bin/env python3
"""Diagnose V121 sparse peaks and select an exact episode-peak objective."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
RESULT = ANALYSIS / "winner_v121_nominal_behavior_result.json"
PREREG = ANALYSIS / "winner_v121_nominal_behavior_preregistration.json"
TRANSFORM = ANALYSIS / "winner_v121_deployment_transform_contract.json"
OUTPUT = ANALYSIS / "winner_v121_peak_objective_diagnosis.json"
MARKDOWN = ANALYSIS / "WINNER_V121_PEAK_OBJECTIVE_DIAGNOSIS_20260724.md"
EXPECTED = {
    "result": "8bdefb90032facb4a3f3f7c833e608d2b35dac958ac0fcc2bbbd393ddcbb6047",
    "preregistration": (
        "9c10dc3de6ea4b5f0f5fe00b287a53e7dc17f1e77b34da84916f90ba285770f5"
    ),
    "transform": (
        "4bd5eab5343cd8401db1789773fa3cc345727d903cb31222e0ea9870f0e9e640"
    ),
}
JOINTS = [
    "left_hip_yaw",
    "left_hip_roll",
    "left_hip_pitch",
    "left_knee",
    "left_ankle",
    "neck_pitch",
    "head_pitch",
    "head_yaw",
    "head_roll",
    "right_hip_yaw",
    "right_hip_roll",
    "right_hip_pitch",
    "right_knee",
    "right_ankle",
]
TORQUE_LIMIT_NM = 1.91229675
DT_S = 0.02


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root", type=Path, required=True)
    args = parser.parse_args()
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V121: {path}")
    run_root = args.run_root.resolve()
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    _prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    transform = json.loads(TRANSFORM.read_text(encoding="utf-8"))
    hashes = {
        "result": sha256(RESULT),
        "preregistration": sha256(PREREG),
        "transform": sha256(TRANSFORM),
    }
    rate_limits = np.asarray(
        transform["transform"]["exact_train_effective_rate_rad_s"],
        dtype=np.float64,
    )
    rows = []
    joint_event_counts = np.zeros(14, dtype=np.int64)
    total_events = 0
    early_events = 0
    lag_events = 0
    simultaneous_ticks = 0
    max_integral_error = 0.0
    for cell_path in sorted((run_root / "cells").glob("*.json")):
        cell = json.loads(cell_path.read_text(encoding="utf-8"))
        trace_path = Path(cell["trace"]["path"])
        trace = load_jsonl(trace_path)
        force = np.abs(
            np.asarray(
                [row["actuator_force_nm"] for row in trace],
                dtype=np.float64,
            )
        )
        velocity = np.abs(
            np.asarray(
                [row["sent_target_velocity_rad_s"] for row in trace],
                dtype=np.float64,
            )
        )
        exceed = force > TORQUE_LIMIT_NM
        events = np.argwhere(exceed)
        joint_counts = exceed.sum(axis=0)
        joint_event_counts += joint_counts
        total_events += int(exceed.sum())
        early_events += int(exceed[:32].sum())
        simultaneous_ticks += int(np.sum(exceed.sum(axis=1) > 1))
        boundary = np.isclose(
            velocity, rate_limits[None, :], atol=3.0e-6, rtol=0.0
        )
        within_lag = np.zeros_like(boundary)
        for lag in range(3):
            within_lag[lag:] |= boundary[: len(trace) - lag]
        lag_events += int(np.sum(exceed & within_lag))
        instantaneous_peak_excess = np.maximum(
            np.max(force, axis=1) - TORQUE_LIMIT_NM,
            0.0,
        )
        running = np.maximum.accumulate(instantaneous_peak_excess)
        previous = np.concatenate(([0.0], running[:-1]))
        increment_rate = (running - previous) / DT_S
        integrated = float(np.sum(increment_rate) * DT_S)
        direct = float(np.max(instantaneous_peak_excess))
        max_integral_error = max(
            max_integral_error, abs(integrated - direct)
        )
        rows.append(
            {
                "checkpoint_id": cell["identity"]["checkpoint_id"],
                "step": cell["identity"]["step"],
                "plant": cell["identity"]["plant"],
                "command_x_m_s": cell["identity"]["command_x_m_s"],
                "cell_pass": cell["pass"],
                "failure_reasons": cell["failure_reasons"],
                "torque_exceed_events": int(exceed.sum()),
                "torque_exceed_ticks": int(exceed.any(axis=1).sum()),
                "simultaneous_exceed_ticks": int(
                    np.sum(exceed.sum(axis=1) > 1)
                ),
                "early_tick_0_31_events": int(exceed[:32].sum()),
                "within_two_tick_rate_boundary_events": int(
                    np.sum(exceed & within_lag)
                ),
                "peak_excess_nm": direct,
                "integrated_increment_cost_nm": integrated,
                "event_ticks_and_joints": [
                    {
                        "tick": int(tick),
                        "joint": JOINTS[int(joint)],
                        "torque_nm": float(force[tick, joint]),
                    }
                    for tick, joint in events
                ],
            }
        )
    half_rows = [row for row in rows if row["step"] == 1_003_520]
    final_rows = [row for row in rows if row["step"] == 2_007_040]
    failed_rows = [row for row in rows if not row["cell_pass"]]
    failure_reasons = sorted(
        {
            reason
            for row in failed_rows
            for reason in row["failure_reasons"]
        }
    )
    checks = {
        "all_input_hashes_exact": hashes == EXPECTED,
        "nominal_result_valid_rejected_persistence": (
            result.get("status")
            == "PASS_WINNER_V121_NOMINAL_BEHAVIOR_VALID_RESULT"
            and result.get("failed_validity_checks") == []
            and result.get("decision", {}).get("status")
            == "REJECT_V121_NOMINAL_POLICY"
            and result.get("summary", {}).get("passing_cells") == 11
        ),
        "half_exactly_eight_of_eight": (
            len(half_rows) == 8 and all(row["cell_pass"] for row in half_rows)
        ),
        "final_exactly_three_of_eight": (
            len(final_rows) == 8
            and sum(row["cell_pass"] for row in final_rows) == 3
        ),
        "failures_only_current_or_torque": failure_reasons
        == [
            "current_peak_at_most_2p5",
            "torque_peak_at_most_1p91229675_nm",
        ],
        "sparse_single_joint_events_exact": (
            total_events == 15 and simultaneous_ticks == 0
        ),
        "events_localized_left_knee_and_right_ankle": (
            {
                JOINTS[index]: int(count)
                for index, count in enumerate(joint_event_counts)
                if count
            }
            == {"left_knee": 13, "right_ankle": 2}
        ),
        "startup_dominates_but_not_all_events": early_events == 13,
        "rate_boundary_route_not_selected": lag_events == 3,
        "increment_integral_equals_exact_episode_peak": (
            max_integral_error <= 1.0e-12
        ),
        "formal_behavior_not_rerun": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    value = {
        "schema_version": "winner_v121.peak_objective_diagnosis.v1",
        "status": (
            "PASS_WINNER_V121_PEAK_OBJECTIVE_DIAGNOSIS"
            if not failed
            else "HOLD_WINNER_V121_PEAK_OBJECTIVE_DIAGNOSIS"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": hashes,
        "summary": {
            "cells": len(rows),
            "failed_cells": len(failed_rows),
            "torque_exceed_events": total_events,
            "simultaneous_exceed_ticks": simultaneous_ticks,
            "early_tick_0_31_events": early_events,
            "within_two_tick_rate_boundary_events": lag_events,
            "joint_event_counts": {
                JOINTS[index]: int(count)
                for index, count in enumerate(joint_event_counts)
                if count
            },
            "max_peak_integral_identity_error_nm": max_integral_error,
        },
        "rows": rows,
        "selected_mechanism": {
            "name": "episode_global_peak_torque_increment_integral",
            "instantaneous_excess": (
                "e_t=max(0,max_j(abs(tau_tj))-1.91229675)"
            ),
            "state": "m_t=max(m_(t-1),e_t), m_reset=0",
            "per_step_cost": "(m_t-m_(t-1))/0.02",
            "episode_integral_identity": (
                "sum_t cost_t*0.02=max_t,j max(0,abs(tau_tj)-limit)"
            ),
            "replace_linear_mean_hinge": True,
            "reuse_scale": -307.48131091308585,
            "scale_search": False,
            "source_checkpoint": "exact V119 half checkpoint",
            "both_new_postupdate_checkpoints_required": True,
        },
        "decision": (
            "PREREGISTER_V122_DEFAULT_OFF_EPISODE_PEAK_CPU_CONTRACT"
            if not failed
            else "HOLD_WITHOUT_TRAINING"
        ),
        "execution": {
            "new_training_steps": 0,
            "new_behavior_cells": 0,
            "colab_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "v122_cpu_preregistration_authorized": not failed,
            "training_authorized": False,
            "behavior_evaluation_authorized": False,
            "full_matrix_authorized": False,
            "gate5_authorized": False,
            "rdkx5_or_robot": False,
            "robot_clearance": False,
            "torque_or_motion": False,
        },
    }
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner-v121 peak-objective diagnosis\n\n"
        f"Status: `{value['status']}`\n\n"
        f"Decision: `{value['decision']}`\n\n"
        "The final checkpoint has 15 single-joint torque exceedance events: "
        "13 left-knee events in ticks 0-31 and two later right-ankle events. "
        "Only three are near a rate boundary, so another rate clamp is not "
        "selected. The proposed running-peak increment integrates exactly to "
        "the episode-global peak gate, without a scalar search.\n",
        encoding="utf-8",
    )
    print(value["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
