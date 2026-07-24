#!/usr/bin/env python3
"""Attribute the V113 nominal current/torque failures."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
RESULT = ANALYSIS / "winner_v113_nominal_behavior_result.json"
V110 = ANALYSIS / "winner_v110_pitch_guard_behavior_result.json"
PREREG = ANALYSIS / "winner_v113_nominal_behavior_preregistration.json"
OUTPUT = ANALYSIS / "winner_v113_nominal_failure_attribution.json"
MARKDOWN = ANALYSIS / "WINNER_V113_NOMINAL_FAILURE_ATTRIBUTION_20260724.md"
RESULT_SHA256 = (
    "20802e3f4b094bbe1d6019982182e7eee90f1d13c143f6bac7aa8b10cd7820bc"
)
V110_SHA256 = (
    "0386bc3834fb451d9f6470187ed8447e971ad90021748379977b59fd19174404"
)
TORQUE_LIMIT_NM = 1.91229675
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


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_sha256(value: object) -> str:
    return hashlib.sha256(
        json.dumps(
            value, allow_nan=False, separators=(",", ":"), sort_keys=True
        ).encode()
    ).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root", type=Path, required=True)
    args = parser.parse_args()
    if OUTPUT.exists() or MARKDOWN.exists():
        raise FileExistsError("refusing to overwrite V113 attribution")
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    v110 = json.loads(V110.read_text(encoding="utf-8"))
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    if (
        sha256(RESULT) != RESULT_SHA256
        or result.get("decision", {}).get("status")
        != "REJECT_V113_NOMINAL_POLICY"
        or sha256(V110) != V110_SHA256
    ):
        raise ValueError("V113/V110 evidence identity changed")
    trace_root = args.run_root.resolve() / "traces"
    cell_root = args.run_root.resolve() / "cells"
    rows = []
    joint_failure_cells = {name: 0 for name in JOINTS}
    all_one_joint = True
    trace_hashes_exact = True
    cell_values = [
        (path, json.loads(path.read_text(encoding="utf-8")))
        for path in sorted(cell_root.glob("*.json"))
    ]
    unordered_manifest = [
        {
            "identity": value["identity"],
            "pass": value["pass"],
            "failure_reasons": value["failure_reasons"],
            "cell_sha256": sha256(path),
            "trace_sha256": value["trace"].get("sha256"),
        }
        for path, value in cell_values
    ]
    manifest_map = {
        (
            row["identity"]["checkpoint_id"],
            row["identity"]["plant"],
            float(row["identity"]["command_x_m_s"]),
        ): row
        for row in unordered_manifest
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
    manifest_by_trace = {
        row["trace_sha256"]: row for row in manifest
    }
    for path in sorted(trace_root.glob("*.jsonl")):
        trace_hash = sha256(path)
        trace_hashes_exact &= trace_hash in manifest_by_trace
        samples = [
            json.loads(line)
            for line in path.read_text(encoding="utf-8").splitlines()
            if line
        ]
        force = np.abs(
            np.asarray(
                [sample["actuator_force_nm"] for sample in samples],
                dtype=float,
            )
        )
        excess = np.maximum(force - TORQUE_LIMIT_NM, 0.0)
        active = excess > 0.0
        simultaneous = np.sum(active, axis=1)
        all_one_joint &= bool(np.max(simultaneous) <= 1)
        for index in np.flatnonzero(np.any(active, axis=0)):
            joint_failure_cells[JOINTS[int(index)]] += 1
        tick, joint = np.unravel_index(np.argmax(force), force.shape)
        rows.append(
            {
                "trace": path.name,
                "trace_sha256": trace_hash,
                "peak_torque_nm": float(force[tick, joint]),
                "peak_tick": int(tick),
                "peak_joint": JOINTS[int(joint)],
                "exceeding_joint_ticks": int(np.sum(active)),
                "exceeding_ticks": int(np.sum(np.any(active, axis=1))),
                "squared_mean_sum": float(
                    np.sum(np.mean(excess**2, axis=1))
                ),
                "squared_max_sum": float(
                    np.sum(np.max(excess**2, axis=1))
                ),
                "linear_mean_sum": float(
                    np.sum(np.mean(excess, axis=1))
                ),
            }
        )
    failing = [row for row in rows if row["exceeding_ticks"] > 0]
    squared_ratio_exact = all(
        abs(row["squared_max_sum"] - 14.0 * row["squared_mean_sum"])
        <= 1.0e-12
        for row in rows
    )
    v110_excess = (
        float(v110["summary"]["worst_peak_torque_nm"]) - TORQUE_LIMIT_NM
    )
    prior_worst_weighted = 1000.0 * v110_excess**2 / 14.0
    linear_scale = -prior_worst_weighted / (v110_excess / 14.0)
    checks = {
        "result_and_v110_hashes_exact": True,
        "all_16_trace_hashes_exact": trace_hashes_exact and len(rows) == 16,
        "cell_manifest_hash_exact": (
            canonical_sha256(manifest) == result["cell_manifest_sha256"]
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
        "at_most_one_joint_exceeds_per_tick": all_one_joint,
        "squared_max_is_exactly_14x_squared_mean": squared_ratio_exact,
        "failure_joints_only_left_knee_and_ankle": {
            name for name, count in joint_failure_cells.items() if count
        }
        == {"left_knee", "left_ankle"},
        "failures_are_sparse": max(
            row["exceeding_ticks"] for row in failing
        )
        <= 12,
        "linear_scale_finite_and_negative": (
            np.isfinite(linear_scale) and linear_scale < 0.0
        ),
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": "winner_v113.nominal_failure_attribution.v1",
        "status": (
            "PASS_WINNER_V113_NOMINAL_FAILURE_ATTRIBUTION"
            if not failed
            else "HOLD_WINNER_V113_NOMINAL_FAILURE_ATTRIBUTION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "summary": {
            "failing_cells": len(failing),
            "failure_joint_cell_counts": joint_failure_cells,
            "maximum_exceeding_ticks_per_cell": max(
                row["exceeding_ticks"] for row in failing
            ),
            "worst_peak_torque_nm": max(
                row["peak_torque_nm"] for row in rows
            ),
        },
        "objective_diagnosis": {
            "closed_option": (
                "per-tick max squared hinge; it is exactly a 14x scalar "
                "multiple of the existing mean squared hinge on every trace"
            ),
            "selected_option": (
                "all-joint mean linear torque exceedance; it preserves "
                "nonzero boundary gradient on the sparse peak-setting ticks"
            ),
            "formula": (
                "mean_j(max(abs(actuator_force_nm[j]) - 1.91229675, 0))"
            ),
            "default_off_scale": 0.0,
            "training_scale": linear_scale,
            "scale_derivation": {
                "v110_worst_excess_nm": v110_excess,
                "prior_squared_weighted_cost": -prior_worst_weighted,
                "linear_weighted_cost_at_same_v110_tick": (
                    linear_scale * v110_excess / 14.0
                ),
            },
        },
        "cells": rows,
        "input_hashes": {
            "v113_result": sha256(RESULT),
            "v110_result": sha256(V110),
        },
        "decision": (
            "PREREGISTER_LINEAR_TORQUE_EXCEEDANCE_CPU_CONTRACT"
            if not failed
            else "STOP"
        ),
        "authority": {
            "linear_objective_cpu_preregistration_authorized": not failed,
            "training_authorized": False,
            "behavior_evaluation_authorized": False,
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
        "# Winner-v113 nominal failure attribution\n\n"
        f"Status: `{payload['status']}`\n\n"
        f"Failing cells: `{len(failing)}/16`\n\n"
        f"Failure joints: `{joint_failure_cells}`\n\n"
        "Every failure remains a sparse left-knee/left-ankle torque event. "
        "Only one joint exceeds the boundary per tick, so a max-squared loss "
        "would be exactly a scalar rewrite of the existing mean-squared loss. "
        "The evidence instead selects a linear hinge with a non-vanishing "
        "boundary gradient. This authorizes only its CPU mechanics contract.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"linear_scale={linear_scale}")
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
