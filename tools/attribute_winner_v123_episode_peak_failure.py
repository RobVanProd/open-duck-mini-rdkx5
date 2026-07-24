#!/usr/bin/env python3
"""Attribute V123 nominal failure without selecting another training run."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v123_episode_peak_failure_attribution.json"
MARKDOWN = ANALYSIS / "WINNER_V123_EPISODE_PEAK_FAILURE_ATTRIBUTION_20260724.md"
INPUTS = {
    "v121_result": ANALYSIS / "winner_v121_nominal_behavior_result.json",
    "v123_result": ANALYSIS / "winner_v123_nominal_behavior_result.json",
    "v122_cpu_result": ANALYSIS / "winner_v122_episode_peak_cpu_result.json",
    "v122_recovery": (ANALYSIS / "winner_v122_recovered_training_validation.json"),
    "v123_transform": (ANALYSIS / "winner_v123_deployment_transform_contract.json"),
    "v123_preregistration": (
        ANALYSIS / "winner_v123_nominal_behavior_preregistration.json"
    ),
}
EXPECTED_HASHES = {
    "v121_result": ("8bdefb90032facb4a3f3f7c833e608d2b35dac958ac0fcc2bbbd393ddcbb6047"),
    "v123_result": ("015fc6b85c5b3e3742f97c1e082987bc82c65da774e74d22b9a9e3c32907baa0"),
    "v122_cpu_result": (
        "56006d763f9a92ef2a40ea6e0501ef7181d5411569f411b43b85f6614f88689a"
    ),
    "v122_recovery": (
        "95e8240fa3aae8226a3f2bf2f9658b43ec61ecfd7356713fc3cd4a46146c1256"
    ),
    "v123_transform": (
        "b179214f576d3e8ba26d7aca04d9a2760ff26ff0bf518922e528b9fcfd3dce84"
    ),
    "v123_preregistration": (
        "b470600091b03cd93a67dc28cdbd3b298dd03679bd1716acb541fed9d1b15754"
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
NOMINAL_KP = 13.37
HIGH_LOAD_NM = 1.5


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line
    ]


def trace_summary(run_root: Path) -> dict:
    joint_counts = np.zeros(len(JOINTS), dtype=np.int64)
    event_count = 0
    event_ticks = 0
    early_events = 0
    simultaneous_ticks = 0
    moving_cells = 0
    moving_torque_failures = 0
    event_sent_error_above_static = 0
    high_load_bridge_lag: list[float] = []
    rows: list[dict] = []
    static_margin = TORQUE_LIMIT_NM / NOMINAL_KP
    for cell_path in sorted((run_root / "cells").glob("*.json")):
        cell = load_json(cell_path)
        identity = cell["identity"]
        if float(identity["command_x_m_s"]) == 0.0:
            continue
        moving_cells += 1
        if "torque_peak_at_most_1p91229675_nm" in cell["failure_reasons"]:
            moving_torque_failures += 1
        trace = load_jsonl(Path(cell["trace"]["path"]))
        force = np.abs(
            np.asarray(
                [sample["actuator_force_nm"] for sample in trace],
                dtype=np.float64,
            )
        )
        sent = np.asarray(
            [sample["sent_target_rad"] for sample in trace],
            dtype=np.float64,
        )
        applied = np.asarray(
            [sample["applied_target_rad"] for sample in trace],
            dtype=np.float64,
        )
        actual_pre = np.asarray(
            [sample["actual_position_pre_rad"] for sample in trace],
            dtype=np.float64,
        )
        exceed = force > TORQUE_LIMIT_NM
        counts = exceed.sum(axis=0)
        joint_counts += counts
        event_count += int(exceed.sum())
        event_ticks += int(exceed.any(axis=1).sum())
        early_events += int(exceed[:32].sum())
        simultaneous_ticks += int(np.sum(exceed.sum(axis=1) > 1))
        sent_error = np.abs(sent - actual_pre)
        event_sent_error_above_static += int(
            np.sum(exceed & (sent_error > static_margin))
        )
        high_load = force > HIGH_LOAD_NM
        high_load_bridge_lag.extend(np.abs(applied - sent)[high_load].tolist())
        rows.append(
            {
                "checkpoint_id": identity["checkpoint_id"],
                "plant": identity["plant"],
                "command_x_m_s": identity["command_x_m_s"],
                "cell_pass": cell["pass"],
                "failure_reasons": cell["failure_reasons"],
                "torque_exceed_events": int(exceed.sum()),
                "torque_exceed_ticks": int(exceed.any(axis=1).sum()),
                "early_tick_0_31_events": int(exceed[:32].sum()),
                "peak_torque_nm": float(np.max(force)),
            }
        )
    bridge = np.asarray(high_load_bridge_lag, dtype=np.float64)
    return {
        "moving_cells": moving_cells,
        "moving_torque_failures": moving_torque_failures,
        "torque_exceed_events": event_count,
        "torque_exceed_ticks": event_ticks,
        "early_tick_0_31_events": early_events,
        "simultaneous_exceed_ticks": simultaneous_ticks,
        "joint_event_counts": {
            JOINTS[index]: int(count)
            for index, count in enumerate(joint_counts)
            if count
        },
        "static_torque_margin_rad": static_margin,
        "event_sent_error_above_static_margin": (event_sent_error_above_static),
        "event_sent_error_not_above_static_margin": (
            event_count - event_sent_error_above_static
        ),
        "high_load_bridge_lag_population": int(bridge.size),
        "high_load_bridge_lag_p95_rad": float(np.percentile(bridge, 95.0)),
        "high_load_bridge_lag_max_rad": float(np.max(bridge)),
        "rows": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--v121-run-root", type=Path, required=True)
    parser.add_argument("--v123-run-root", type=Path, required=True)
    args = parser.parse_args()
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V123: {path}")
    hashes = {name: sha256(path) for name, path in INPUTS.items()}
    values = {name: load_json(path) for name, path in INPUTS.items()}
    v121_trace = trace_summary(args.v121_run_root.resolve())
    v123_trace = trace_summary(args.v123_run_root.resolve())
    v121_result = values["v121_result"]
    v123_result = values["v123_result"]
    checks = {
        "all_input_hashes_exact": hashes == EXPECTED_HASHES,
        "v122_cpu_mechanics_passed": (
            values["v122_cpu_result"]["status"]
            == "PASS_WINNER_V122_EPISODE_PEAK_CPU_SMOKE"
            and values["v122_cpu_result"]["failed_checks"] == []
        ),
        "v122_recovery_validation_passed": (
            values["v122_recovery"]["status"]
            == "PASS_WINNER_V122_RECOVERED_TRAINING_VALIDATION"
            and values["v122_recovery"]["failed_checks"] == []
        ),
        "v123_transform_contract_passed": (
            values["v123_transform"]["status"]
            == "PASS_WINNER_V123_DEPLOYMENT_TRANSFORM_CONTRACT"
            and values["v123_transform"]["failed_checks"] == []
        ),
        "v123_result_valid_but_rejected": (
            v123_result["status"] == "PASS_WINNER_V123_NOMINAL_BEHAVIOR_VALID_RESULT"
            and v123_result["failed_validity_checks"] == []
            and v123_result["decision"]["status"] == "REJECT_V123_NOMINAL_POLICY"
        ),
        "v121_comparison_exact": (
            v121_result["summary"]["passing_cells"] == 11
            and v121_result["summary"]["persistent_both_checkpoint_pass"] is False
            and v121_trace["torque_exceed_events"] == 15
        ),
        "v123_only_zero_command_cells_pass": (
            v123_result["summary"]["passing_cells"] == 4
            and all(not row["cell_pass"] for row in v123_trace["rows"])
        ),
        "all_v123_moving_cells_fail_torque": (
            v123_trace["moving_cells"] == 12
            and v123_trace["moving_torque_failures"] == 12
        ),
        "episode_peak_objective_expands_events": (
            v121_trace["torque_exceed_events"] == 15
            and v123_trace["torque_exceed_events"] == 184
        ),
        "v123_events_distributed_beyond_startup": (
            v123_trace["early_tick_0_31_events"] == 5
            and v123_trace["torque_exceed_events"] > 5
        ),
        "v123_joint_event_counts_exact": (
            v123_trace["joint_event_counts"]
            == {
                "left_knee": 148,
                "left_ankle": 13,
                "right_knee": 5,
                "right_ankle": 18,
            }
        ),
        "walking_and_tracking_preserved": (
            v123_result["summary"]["minimum_moving_mean_vx_m_s"] > 0.1
            and v123_result["summary"]["worst_tracking_p95_rad"] < 0.15
        ),
        "static_sent_target_margin_not_sufficient_explanation": (
            v123_trace["event_sent_error_above_static_margin"] == 149
            and v123_trace["event_sent_error_not_above_static_margin"] == 35
        ),
        "no_new_training_or_behavior_executed": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    value = {
        "schema_version": ("winner_v123.episode_peak_failure_attribution.v1"),
        "status": (
            "PASS_WINNER_V123_EPISODE_PEAK_FAILURE_ATTRIBUTION"
            if not failed
            else "HOLD_WINNER_V123_EPISODE_PEAK_FAILURE_ATTRIBUTION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": hashes,
        "comparison": {
            "v121": {
                "passing_cells": v121_result["summary"]["passing_cells"],
                "worst_peak_current_a": v121_result["summary"]["worst_peak_current_a"],
                "worst_peak_torque_nm": v121_result["summary"]["worst_peak_torque_nm"],
                "worst_tracking_p95_rad": v121_result["summary"][
                    "worst_tracking_p95_rad"
                ],
                "trace": v121_trace,
            },
            "v123": {
                "passing_cells": v123_result["summary"]["passing_cells"],
                "worst_peak_current_a": v123_result["summary"]["worst_peak_current_a"],
                "worst_peak_torque_nm": v123_result["summary"]["worst_peak_torque_nm"],
                "worst_tracking_p95_rad": v123_result["summary"][
                    "worst_tracking_p95_rad"
                ],
                "minimum_moving_mean_vx_m_s": v123_result["summary"][
                    "minimum_moving_mean_vx_m_s"
                ],
                "trace": v123_trace,
            },
        },
        "causal_readout": {
            "supported": [
                (
                    "The exact episode-global peak formulation preserved gait "
                    "and tracking but expanded the torque-exceedance population "
                    "from 15 to 184 events."
                ),
                (
                    "The new failures are repeated gait-cycle loads rather "
                    "than the V121 startup-localized signature."
                ),
                (
                    "A static sent-target guard at torque_limit/kp cannot "
                    "explain or guarantee away every event because 35 V123 "
                    "events occur without exceeding that sent-target error."
                ),
            ],
            "not_proven": [
                (
                    "Reward clipping and sparse running-maximum credit are a "
                    "plausible cause, but the nominal traces do not isolate "
                    "them as the sole cause."
                ),
                (
                    "A tighter static G3 margin has not been behavior-tested "
                    "and is not selected by this attribution."
                ),
            ],
        },
        "decision": {
            "status": "CLOSE_V122_EPISODE_PEAK_OBJECTIVE",
            "repeat_or_scalar_search_authorized": False,
            "checkpoint_selection_authorized": False,
            "successor_training_authorized": False,
            "successor_behavior_screen_authorized": False,
            "next_action": (
                "external causal review of a hard bridge-aware physical "
                "constraint before any successor preregistration"
            ),
        },
        "execution": {
            "new_training_steps": 0,
            "new_behavior_cells": 0,
            "colab_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
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
        "# Winner-v123 episode-peak failure attribution\n\n"
        f"Status: `{value['status']}`\n\n"
        "Decision: `CLOSE_V122_EPISODE_PEAK_OBJECTIVE`\n\n"
        "V123 preserved walking and tracking but expanded the nominal "
        "torque-exceedance population from 15 events in V121 to 184 events. "
        "All 12 moving cells fail torque; only the four x=0 holds pass. The "
        "events are distributed through the gait cycle and across both knees "
        "and ankles, so the exact episode-global peak objective is closed "
        "without retry, scalar search, or checkpoint selection.\n\n"
        "A static `torque_limit/kp = 0.14302893 rad` sent-target margin is not "
        "selected: 35/184 events occur without crossing that sent-target "
        "error, while the measured bridge leaves applied and sent targets "
        "separated under load. No successor training or behavior screen is "
        "authorized by this attribution.\n",
        encoding="utf-8",
    )
    print(value["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
