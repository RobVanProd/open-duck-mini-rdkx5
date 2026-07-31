#!/usr/bin/env python3
"""Attribute the valid Winner-v109 peak failures from immutable CPU traces."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
RESULT = ANALYSIS / "winner_v109_recurrent_source_result.json"
CURRENT = ANALYSIS / "winner_v3_current_gate_application_contract.json"
GUARD_PREREG = (
    ANALYSIS / "ground_up_actual_centered_guard_screen_preregistration.json"
)
GUARD_RESULT = ANALYSIS / "ground_up_actual_centered_guard_screen_result.json"
OUTPUT = ANALYSIS / "winner_v109_peak_failure_attribution.json"
MARKDOWN = ANALYSIS / "WINNER_V109_PEAK_FAILURE_ATTRIBUTION_20260724.md"
EXPECTED = {
    "result": "dd79fc3976e1e8aae37aba7a0838c20c2e10f34ab1337526c9eaea3d4860cf5b",
    "current": "17e841450a2dde66182c3d41a06abf8d14366011f811bcde20adb1f1c8f68ddb",
    "guard_prereg": "9bf9b3ec4e4423a5e44a582d29a69927382468e24d7aa3a478712b6c87988dae",
    "guard_result": "b90b5d4032b50b34470bead489394a91d9c2520830876f58d05caf3e9683a5f9",
}
JOINT_NAMES = (
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
)
CURRENT_NM_PER_A = 0.784532


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def longest_true_run(values: np.ndarray) -> int:
    longest = 0
    current = 0
    for value in values:
        if bool(value):
            current += 1
            longest = max(longest, current)
        else:
            current = 0
    return longest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite: {path}")

    result = json.loads(RESULT.read_text(encoding="utf-8"))
    current_contract = json.loads(CURRENT.read_text(encoding="utf-8"))
    guard_prereg = json.loads(GUARD_PREREG.read_text(encoding="utf-8"))
    guard_result = json.loads(GUARD_RESULT.read_text(encoding="utf-8"))
    traces = sorted((args.run_root.resolve() / "traces").glob("*.jsonl"))
    gate = current_contract["prospective_offline_candidate_gate"]
    rows: list[dict[str, Any]] = []
    failure_joint_counts = {name: 0 for name in JOINT_NAMES}
    for path in traces:
        records = [
            json.loads(line)
            for line in path.read_text(encoding="utf-8").splitlines()
            if line
        ]
        force = np.abs(
            np.asarray(
                [record["actuator_force_nm"] for record in records],
                dtype=np.float64,
            )
        )
        current = force / CURRENT_NM_PER_A
        peak_by_joint = np.max(current, axis=0)
        torque_by_joint = np.max(force, axis=0)
        current_fail = [
            JOINT_NAMES[index]
            for index, value in enumerate(peak_by_joint)
            if value > float(gate["per_joint_peak_current_a_max"])
        ]
        torque_fail = [
            JOINT_NAMES[index]
            for index, value in enumerate(torque_by_joint)
            if value > float(gate["per_joint_peak_torque_nm_max"])
        ]
        for name in set(current_fail) | set(torque_fail):
            failure_joint_counts[name] += 1
        tick, joint = (
            int(value)
            for value in np.unravel_index(np.argmax(force), force.shape)
        )
        longest = max(
            longest_true_run(
                current[:, index]
                > float(gate["strict_overcurrent_threshold_a"])
            )
            for index in range(14)
        )
        rows.append(
            {
                "trace": {
                    "path": str(path),
                    "sha256": sha256(path),
                    "rows": len(records),
                },
                "identity_from_stem": path.stem,
                "zero_command": "x0.000" in path.stem,
                "current_fail_joints": current_fail,
                "torque_fail_joints": torque_fail,
                "peak": {
                    "tick": tick,
                    "joint": JOINT_NAMES[joint],
                    "current_a": float(current[tick, joint]),
                    "torque_nm": float(force[tick, joint]),
                    "tracking_error_rad": float(
                        records[tick]["tracking_error_rad"][joint]
                    ),
                    "action": float(records[tick]["action"][joint]),
                    "sent_target_rad": float(
                        records[tick]["sent_target_rad"][joint]
                    ),
                    "applied_target_rad": float(
                        records[tick]["applied_target_rad"][joint]
                    ),
                    "actual_position_rad": float(
                        records[tick]["actual_position_rad"][joint]
                    ),
                },
                "maximum_consecutive_ticks_strictly_above_2a": longest,
                "gates": {
                    "current_peak_pass": not current_fail,
                    "torque_peak_pass": not torque_fail,
                    "overcurrent_duration_pass": longest
                    <= int(
                        gate[
                            "strict_overcurrent_max_consecutive_ticks"
                        ]
                    ),
                },
            }
        )

    moving = [row for row in rows if not row["zero_command"]]
    zero = [row for row in rows if row["zero_command"]]
    failed_joint_set = sorted(
        name for name, count in failure_joint_counts.items() if count
    )
    checks = {
        "frozen_inputs_exact": all(
            sha256(path) == EXPECTED[name]
            for name, path in (
                ("result", RESULT),
                ("current", CURRENT),
                ("guard_prereg", GUARD_PREREG),
                ("guard_result", GUARD_RESULT),
            )
        ),
        "v109_valid_rejection_exact": result.get("status")
        == "PASS_WINNER_V109_RECURRENT_SOURCE_SCREEN"
        and result.get("decision", {}).get("status")
        == "REJECT_RECURRENT_SOURCE",
        "all_16_traces_present": len(rows) == 16
        and all(row["trace"]["rows"] == 600 for row in rows),
        "four_zero_traces_pass_current_torque": len(zero) == 4
        and all(
            row["gates"]["current_peak_pass"]
            and row["gates"]["torque_peak_pass"]
            for row in zero
        ),
        "all_12_moving_traces_fail_current_and_torque": len(moving) == 12
        and all(
            not row["gates"]["current_peak_pass"]
            and not row["gates"]["torque_peak_pass"]
            for row in moving
        ),
        "failure_joints_exactly_bilateral_knees_and_left_ankle": (
            failed_joint_set == ["left_ankle", "left_knee", "right_knee"]
        ),
        "no_overcurrent_duration_failure": all(
            row["gates"]["overcurrent_duration_pass"] for row in rows
        ),
        "g3_was_frozen_before_v109": {
            (row["name"], float(row["margin_rad"]))
            for row in guard_prereg["arms"]
        }
        >= {("G3_FULL_TICK_BUFFER", 0.165)},
        "g3_prior_persistent_behavior_pass": any(
            row["guard"] == "G3_FULL_TICK_BUFFER"
            and row["tail"] == "T2_EQUAL"
            for row in guard_result["passing_combinations"]
        ),
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    value = {
        "schema_version": "winner_v109.peak_failure_attribution.v1",
        "status": (
            "PASS_WINNER_V109_PEAK_FAILURE_ATTRIBUTION"
            if not failed
            else "HOLD_WINNER_V109_PEAK_FAILURE_ATTRIBUTION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "population": {
            "traces": len(rows),
            "zero_command": len(zero),
            "moving": len(moving),
            "failure_joint_counts": {
                name: count
                for name, count in failure_joint_counts.items()
                if count
            },
            "worst_peak_current_a": max(
                row["peak"]["current_a"] for row in rows
            ),
            "worst_peak_torque_nm": max(
                row["peak"]["torque_nm"] for row in rows
            ),
            "maximum_overcurrent_streak_ticks": max(
                row[
                    "maximum_consecutive_ticks_strictly_above_2a"
                ]
                for row in rows
            ),
        },
        "trace_audits": rows,
        "decision": {
            "status": "SELECT_FROZEN_G3_GUARD_FEASIBILITY_SCREEN"
            if not failed
            else "NO_REPAIR_SCREEN_SELECTED",
            "repair": (
                "change the already-present symmetric pitch guard from the "
                "selected G1 0.20-rad boundary to the already-preregistered "
                "G3 0.165-rad full-tick buffer; do not tune a new value"
            ),
            "reason": (
                "the failure is isolated to instantaneous bilateral-knee and "
                "left-ankle peaks, the overcurrent duration rule passes, and every "
                "noncurrent behavior metric passed"
            ),
        },
        "v109_gate_completeness_note": (
            "Winner-v109 explicitly enforced current peak and duration but "
            "did not separately report the manufacturer peak-torque check. "
            "Replaying the immutable traces shows all 12 moving cells also "
            "fail the stricter 1.91229675 N.m torque gate, so the V109 "
            "rejection is unchanged. Winner-v110 must enforce both."
        ),
        "input_hashes": EXPECTED,
        "authority": {
            "one_frozen_cpu_feasibility_screen_next": not failed,
            "hosted_training": False,
            "checkpoint_selection": False,
            "gate5": False,
            "robot_clearance": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    args.output.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown.write_text(
        "# Winner-v109 peak-failure attribution\n\n"
        f"Status: `{value['status']}`\n\n"
        f"Decision: `{value['decision']['status']}`\n\n"
        "All 12 moving cells fail both the 2.5-A peak-current limit and the "
        "stricter 1.91229675-N.m peak-torque limit. The only failing joints "
        "are the bilateral knees and left ankle; no overcurrent streak reaches the "
        "duration trip. This authorizes one CPU-only feasibility screen of "
        "the already-frozen G3 guard, not training, policy selection, Gate 5, "
        "robot use, torque, or motion.\n",
        encoding="utf-8",
    )
    print(value["status"])
    print(f"output_sha256={sha256(args.output)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
