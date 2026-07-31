#!/usr/bin/env python3
"""Attribute V115 nominal physical-load failures from all frozen traces."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
RESULT = ANALYSIS / "winner_v115_nominal_behavior_result.json"
PREREG = ANALYSIS / "winner_v115_nominal_behavior_preregistration.json"
V113_RESULT = ANALYSIS / "winner_v113_nominal_behavior_result.json"
OUTPUT = ANALYSIS / "winner_v115_nominal_failure_attribution.json"
MARKDOWN = ANALYSIS / "WINNER_V115_NOMINAL_FAILURE_ATTRIBUTION_20260724.md"
RESULT_SHA256 = (
    "370e444785692d3c64070f5b9f694e82859d295d4433f22d15f351f87f90a25c"
)
PREREG_SHA256 = (
    "b185c5bda376a6bedd6b8bba272ea26cd48b1bdbddf4aaad56e52afae2d68a37"
)
V113_RESULT_SHA256 = (
    "20802e3f4b094bbe1d6019982182e7eee90f1d13c143f6bac7aa8b10cd7820bc"
)
TORQUE_LIMIT_NM = 1.91229675
CONTROL_DT_S = 0.02
ACTION_SCALE_RAD = 0.25
JOINTS = (
    "left_hip_yaw",
    "left_hip_roll",
    "left_hip_pitch",
    "left_knee",
    "left_ankle",
    "head_1",
    "head_2",
    "head_3",
    "head_4",
    "right_hip_yaw",
    "right_hip_roll",
    "right_hip_pitch",
    "right_knee",
    "right_ankle",
)
RATE_LIMITS_RAD_S = np.asarray(
    [
        1.0,
        0.75,
        1.5,
        1.5,
        1.5,
        0.5,
        0.5,
        0.5,
        0.5,
        0.5,
        0.75,
        1.25,
        1.0,
        1.25,
    ],
    dtype=np.float64,
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value, allow_nan=False, separators=(",", ":"), sort_keys=True
        ).encode()
    ).hexdigest()


def load_trace(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line
    ]


def checkpoint_stage(checkpoint_id: str) -> str:
    return "half" if "HALF" in checkpoint_id.upper() else "final"


def trace_metrics(path: Path) -> dict[str, Any]:
    samples = load_trace(path)
    force = np.abs(
        np.asarray(
            [sample["actuator_force_nm"] for sample in samples],
            dtype=np.float64,
        )
    )
    velocity = np.abs(
        np.asarray(
            [sample["sent_target_velocity_rad_s"] for sample in samples],
            dtype=np.float64,
        )
    )
    if force.shape != (600, 14) or velocity.shape != (600, 14):
        raise ValueError(f"unexpected trace shape: {path}")
    excess = np.maximum(force - TORQUE_LIMIT_NM, 0.0)
    active = excess > 0.0
    boundary = velocity >= RATE_LIMITS_RAD_S[None] - 2.0e-5
    active_indices = np.argwhere(active)
    lag_window_hits = 0
    for tick, joint in active_indices:
        start = max(0, int(tick) - 3)
        lag_window_hits += int(np.any(boundary[start : int(tick) + 1, joint]))
    peak_tick, peak_joint = np.unravel_index(np.argmax(force), force.shape)
    return {
        "trace_sha256": sha256(path),
        "peak_torque_nm": float(force[peak_tick, peak_joint]),
        "peak_tick": int(peak_tick),
        "peak_joint": JOINTS[int(peak_joint)],
        "peak_joint_index": int(peak_joint),
        "peak_joint_velocity_rad_s": float(
            velocity[peak_tick, peak_joint]
        ),
        "exceeding_joint_ticks": int(active_indices.shape[0]),
        "exceeding_ticks": int(np.sum(np.any(active, axis=1))),
        "exceeding_joints": [
            JOINTS[int(index)]
            for index in np.flatnonzero(np.any(active, axis=0))
        ],
        "maximum_simultaneous_exceeding_joints": int(
            np.max(np.sum(active, axis=1))
        ),
        "lag_window_boundary_hits": lag_window_hits,
        "lag_window_boundary_fraction": (
            float(lag_window_hits / active_indices.shape[0])
            if active_indices.shape[0]
            else 1.0
        ),
    }


def cell_rows(run_root: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    values = [
        (path, json.loads(path.read_text(encoding="utf-8")))
        for path in sorted((run_root / "cells").glob("*.json"))
    ]
    manifest = []
    traces = []
    for path, value in values:
        identity = value["identity"]
        trace_path = Path(value["trace"]["path"])
        if not trace_path.is_absolute():
            trace_path = run_root / "traces" / trace_path.name
        metrics = trace_metrics(trace_path)
        manifest.append(
            {
                "identity": identity,
                "pass": value["pass"],
                "failure_reasons": value["failure_reasons"],
                "cell_sha256": sha256(path),
                "trace_sha256": value["trace"].get("sha256"),
            }
        )
        traces.append(
            {
                "checkpoint_stage": checkpoint_stage(
                    identity["checkpoint_id"]
                ),
                "plant": identity["plant"],
                "command_x_m_s": float(identity["command_x_m_s"]),
                "pass": bool(value["pass"]),
                "failure_reasons": value["failure_reasons"],
                **metrics,
            }
        )
    return manifest, traces


def keyed(rows: list[dict[str, Any]]) -> dict[tuple[str, str, float], dict[str, Any]]:
    return {
        (
            row["checkpoint_stage"],
            row["plant"],
            row["command_x_m_s"],
        ): row
        for row in rows
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--v113-run-root", type=Path, required=True)
    args = parser.parse_args()
    if OUTPUT.exists() or MARKDOWN.exists():
        raise FileExistsError("refusing to overwrite V115 attribution")
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    v113_result = json.loads(V113_RESULT.read_text(encoding="utf-8"))
    if (
        sha256(RESULT) != RESULT_SHA256
        or sha256(PREREG) != PREREG_SHA256
        or sha256(V113_RESULT) != V113_RESULT_SHA256
        or result.get("decision", {}).get("status")
        != "REJECT_V115_NOMINAL_POLICY"
    ):
        raise ValueError("V115 attribution evidence identity changed")
    manifest_unordered, traces = cell_rows(args.run_root.resolve())
    _, v113_traces = cell_rows(args.v113_run_root.resolve())
    manifest_map = {
        (
            row["identity"]["checkpoint_id"],
            row["identity"]["plant"],
            float(row["identity"]["command_x_m_s"]),
        ): row
        for row in manifest_unordered
    }
    manifest = [
        manifest_map[
            (
                row["checkpoint_id"],
                row["plant"],
                float(row["command_x_m_s"]),
            )
        ]
        for row in prereg["matrix"]["rows"]
    ]
    torque_failing = [
        row for row in traces if row["exceeding_joint_ticks"] > 0
    ]
    failure_joint_cell_counts = {name: 0 for name in JOINTS}
    for row in torque_failing:
        for name in row["exceeding_joints"]:
            failure_joint_cell_counts[name] += 1
    active_joint_ticks = sum(
        row["exceeding_joint_ticks"] for row in torque_failing
    )
    lag_hits = sum(
        row["lag_window_boundary_hits"] for row in torque_failing
    )
    lag_fraction = lag_hits / active_joint_ticks if active_joint_ticks else 1.0
    matched = []
    v115_map = keyed(traces)
    v113_map = keyed(v113_traces)
    for key in sorted(v115_map):
        current = v115_map[key]
        previous = v113_map[key]
        matched.append(
            {
                "checkpoint_stage": key[0],
                "plant": key[1],
                "command_x_m_s": key[2],
                "v113_peak_torque_nm": previous["peak_torque_nm"],
                "v115_peak_torque_nm": current["peak_torque_nm"],
                "peak_delta_nm": (
                    current["peak_torque_nm"]
                    - previous["peak_torque_nm"]
                ),
                "v113_pass": previous["pass"],
                "v115_pass": current["pass"],
            }
        )
    moving = [row for row in matched if row["command_x_m_s"] > 0.0]
    half = [row for row in moving if row["checkpoint_stage"] == "half"]
    final = [row for row in moving if row["checkpoint_stage"] == "final"]
    final_failures = [
        row
        for row in traces
        if row["checkpoint_stage"] == "final" and not row["pass"]
    ]
    failure_joints = {
        name for name, count in failure_joint_cell_counts.items() if count
    }
    mirror_rate = float(RATE_LIMITS_RAD_S[13])
    current_left_ankle_rate = float(RATE_LIMITS_RAD_S[4])
    selected = (
        failure_joints == {"left_ankle"}
        and lag_fraction >= 0.95
        and len(final_failures) == 1
        and max(
            row["peak_torque_nm"] - TORQUE_LIMIT_NM
            for row in final_failures
        )
        <= 1.0e-4
    )
    checks = {
        "result_prereg_and_v113_hashes_exact": True,
        "valid_complete_16_cell_result": (
            result.get("failed_validity_checks") == []
            and result.get("summary", {}).get("cells") == 16
        ),
        "cell_manifest_hash_exact": (
            canonical_sha256(manifest) == result["cell_manifest_sha256"]
        ),
        "all_trace_hashes_exact": len(traces) == 16
        and all(
            row["trace_sha256"]
            == manifest_row["trace_sha256"]
            for row, manifest_row in zip(
                traces, manifest_unordered, strict=True
            )
        ),
        "all_failures_current_or_torque_only": set(
            result["summary"]["failures_by_reason"]
        )
        == {
            "current_peak_at_most_2p5",
            "torque_peak_at_most_1p91229675_nm",
        },
        "behavior_tracking_and_motion_pass": (
            float(result["summary"]["worst_tracking_p95_rad"]) < 0.20
            and float(result["summary"]["minimum_moving_mean_vx_m_s"]) > 0.0
        ),
        "v113_comparator_complete": len(v113_traces) == 16
        and v113_result.get("summary", {}).get("cells") == 16,
        "all_torque_failures_left_ankle_only": (
            failure_joints == {"left_ankle"}
        ),
        "at_most_one_joint_exceeds_per_tick": all(
            row["maximum_simultaneous_exceeding_joints"] <= 1
            for row in torque_failing
        ),
        "at_least_95pct_exceedance_in_rate_lag_window": lag_fraction >= 0.95,
        "final_has_one_sub_0p1mnm_failure": (
            len(final_failures) == 1
            and max(
                row["peak_torque_nm"] - TORQUE_LIMIT_NM
                for row in final_failures
            )
            <= 1.0e-4
        ),
        "mirror_rate_is_strictly_more_conservative": (
            mirror_rate < current_left_ankle_rate
        ),
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": "winner_v115.nominal_failure_attribution.v1",
        "status": (
            "PASS_WINNER_V115_NOMINAL_FAILURE_ATTRIBUTION"
            if not failed
            else "HOLD_WINNER_V115_NOMINAL_FAILURE_ATTRIBUTION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "summary": {
            "failing_cells": sum(not row["pass"] for row in traces),
            "torque_failing_cells": len(torque_failing),
            "failure_joint_cell_counts": failure_joint_cell_counts,
            "active_exceeding_joint_ticks": active_joint_ticks,
            "lag_window_boundary_hits": lag_hits,
            "lag_window_boundary_fraction": lag_fraction,
            "half_passing_cells": result["per_checkpoint"][0][
                "passing_cells"
            ],
            "final_passing_cells": result["per_checkpoint"][1][
                "passing_cells"
            ],
            "half_mean_peak_delta_vs_v113_nm": float(
                np.mean([row["peak_delta_nm"] for row in half])
            ),
            "final_mean_peak_delta_vs_v113_nm": float(
                np.mean([row["peak_delta_nm"] for row in final])
            ),
        },
        "trace_rows": traces,
        "matched_v113_v115": matched,
        "selected_repair": {
            "authorized": not failed and selected,
            "mechanism": (
                "replace only the left-ankle max_action_delta initializer"
            ),
            "current_left_ankle_rate_limit_rad_s": current_left_ankle_rate,
            "selected_left_ankle_rate_limit_rad_s": mirror_rate,
            "selection_basis": (
                "mirror the already-frozen right-ankle 1.25 rad/s limit; "
                "not a scalar sweep"
            ),
            "current_normalized_action_delta": (
                current_left_ankle_rate * CONTROL_DT_S / ACTION_SCALE_RAD
            ),
            "selected_normalized_action_delta": (
                mirror_rate * CONTROL_DT_S / ACTION_SCALE_RAD
            ),
            "apply_identically_to_both_checkpoints": True,
            "screen_cells": 16,
            "training_steps": 0,
        },
        "decision": (
            "PREREGISTER_ONE_VARIABLE_LEFT_ANKLE_RATE_REPAIR"
            if not failed and selected
            else "STOP_AND_REASSESS"
        ),
        "input_hashes": {
            "v115_result": sha256(RESULT),
            "v115_preregistration": sha256(PREREG),
            "v113_result": sha256(V113_RESULT),
        },
        "authority": {
            "one_variable_rate_repair_preregistration_authorized": (
                not failed and selected
            ),
            "training_authorized": False,
            "behavior_evaluation_authorized": False,
            "full_matrix_authorized": False,
            "checkpoint_selection_authorized": False,
            "gate5_authorized": False,
            "rdkx5_or_robot": False,
            "robot_clearance": False,
            "torque_or_motion": False,
        },
    }
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner-v115 nominal failure attribution\n\n"
        f"Status: `{payload['status']}`\n\n"
        f"Decision: `{payload['decision']}`\n\n"
        f"Failure joints: `{failure_joint_cell_counts}`\n\n"
        f"Rate-lag coincidence: `{lag_fraction}`\n\n"
        "This read-only attribution compares every V115 trace to the matched "
        "V113 trace. A pass authorizes only a separately preregistered "
        "one-variable post-export screen applied to both checkpoints. It "
        "authorizes no training, full matrix, Gate 5, robot, torque, or "
        "motion.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(payload["decision"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
