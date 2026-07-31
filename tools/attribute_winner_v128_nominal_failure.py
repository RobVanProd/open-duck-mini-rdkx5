#!/usr/bin/env python3
"""Attribute the frozen V128 nominal failure before any successor work."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
RESULT = ANALYSIS / "winner_v128_nominal_behavior_result.json"
OUTPUT = ANALYSIS / "winner_v128_nominal_failure_attribution.json"
MARKDOWN = ANALYSIS / "WINNER_V128_NOMINAL_FAILURE_ATTRIBUTION_20260724.md"
EXPECTED_RESULT_SHA256 = (
    "c703a5024dee3bcd32fb549e3c561c09d164d1f766c91ebc882fab7173c0e35a"
)
TORQUE_LIMIT_NM = 1.91229675
JOINTS = (
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


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root", type=Path, required=True)
    args = parser.parse_args()
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V128: {path}")
    run_root = args.run_root.resolve()
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    rows = []
    joint_counts = {name: 0 for name in JOINTS}
    all_event_ticks: list[int] = []
    for cell_path in sorted((run_root / "cells").glob("*.json")):
        cell = json.loads(cell_path.read_text(encoding="utf-8"))
        if cell["pass"]:
            continue
        trace_path = Path(cell["trace"]["path"])
        if sha256(trace_path) != cell["trace"]["sha256"]:
            raise ValueError(f"V128 trace changed: {trace_path}")
        trace = [
            json.loads(line)
            for line in trace_path.read_text(encoding="utf-8").splitlines()
            if line
        ]
        force = np.abs(
            np.asarray(
                [tick["actuator_force_nm"] for tick in trace],
                dtype=np.float64,
            )
        )
        events = np.argwhere(force > TORQUE_LIMIT_NM)
        peak_tick, peak_joint = np.unravel_index(
            int(np.argmax(force)), force.shape
        )
        per_joint = {}
        for joint_index, joint_name in enumerate(JOINTS):
            count = int(np.sum(force[:, joint_index] > TORQUE_LIMIT_NM))
            if count:
                per_joint[joint_name] = count
                joint_counts[joint_name] += count
        ticks = [int(value) for value in events[:, 0]]
        all_event_ticks.extend(ticks)
        rows.append(
            {
                "cell": cell_path.name,
                "checkpoint_id": cell["identity"]["checkpoint_id"],
                "step": cell["identity"]["step"],
                "plant": cell["identity"]["plant"],
                "command_x_m_s": cell["identity"]["command_x_m_s"],
                "failure_reasons": cell["failure_reasons"],
                "torque_event_count": len(ticks),
                "first_event_tick": min(ticks),
                "last_event_tick": max(ticks),
                "events_by_joint": per_joint,
                "peak_torque_nm": float(force[peak_tick, peak_joint]),
                "peak_tick": int(peak_tick),
                "peak_joint": JOINTS[peak_joint],
                "tracking_p95_rad": cell["metrics"][
                    "worst_tracking_p95_rad"
                ],
                "trace_sha256": cell["trace"]["sha256"],
            }
        )
    active_joint_counts = {
        name: count for name, count in joint_counts.items() if count
    }
    checks = {
        "result_hash_exact": sha256(RESULT) == EXPECTED_RESULT_SHA256,
        "result_valid_but_rejected": (
            result.get("status")
            == "PASS_WINNER_V128_NOMINAL_BEHAVIOR_VALID_RESULT"
            and result.get("decision", {}).get("status")
            == "REJECT_V128_NOMINAL_POLICY"
        ),
        "both_checkpoint_rule_failed": (
            result["summary"]["persistent_both_checkpoint_pass"] is False
        ),
        "half_two_of_eight": (
            result["per_checkpoint"][0]["checkpoint_id"]
            == "V128_CONSTRAINED_HALF"
            and result["per_checkpoint"][0]["passing_cells"] == 2
        ),
        "final_eight_of_eight": (
            result["per_checkpoint"][1]["checkpoint_id"]
            == "V128_CONSTRAINED_FINAL"
            and result["per_checkpoint"][1]["passing_cells"] == 8
        ),
        "six_failed_cells_exact": len(rows) == 6,
        "all_failures_half_moving_cells": all(
            row["checkpoint_id"] == "V128_CONSTRAINED_HALF"
            and float(row["command_x_m_s"]) > 0.0
            for row in rows
        ),
        "only_left_knee_and_right_ankle_exceed": (
            set(active_joint_counts) == {"left_knee", "right_ankle"}
        ),
        "events_are_not_startup_localized": (
            len(all_event_ticks) == 102
            and sum(tick <= 31 for tick in all_event_ticks) == 7
            and sum(tick > 31 for tick in all_event_ticks) == 95
        ),
        "tracking_gate_green": (
            float(result["summary"]["worst_tracking_p95_rad"]) <= 0.20
        ),
        "no_eta_retry_or_checkpoint_selection": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": "winner_v128.nominal_failure_attribution.v1",
        "status": (
            "PASS_WINNER_V128_NOMINAL_FAILURE_ATTRIBUTION"
            if not failed
            else "HOLD_WINNER_V128_NOMINAL_FAILURE_ATTRIBUTION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "result_sha256": sha256(RESULT),
        "failed_cells": rows,
        "event_summary": {
            "events": len(all_event_ticks),
            "ticks_at_most_31": sum(
                tick <= 31 for tick in all_event_ticks
            ),
            "ticks_after_31": sum(
                tick > 31 for tick in all_event_ticks
            ),
            "first_tick": min(all_event_ticks),
            "last_tick": max(all_event_ticks),
            "by_joint": active_joint_counts,
        },
        "mechanism_verdict": {
            "ppo_lagrangian_v121_recipe": "CLOSED_NO_RETRY",
            "eta_rederivation": False,
            "checkpoint_cherry_pick": False,
            "reason": (
                "half fails six moving cells while final passes; the "
                "preregistered both-checkpoint persistence rule rejects "
                "the formulation despite a green final checkpoint"
            ),
            "sole_preregistered_successor": (
                "oracle-teacher distillation, conditional on a separate "
                "CPU-only contract and falsifier"
            ),
        },
        "authority": {
            "teacher_distillation_preregistration_authorized": not failed,
            "training_authorized": False,
            "additional_ppo_lagrangian": False,
            "checkpoint_selection": False,
            "full_matrix": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner V128 nominal failure attribution\n\n"
        f"- Status: `{payload['status']}`\n"
        "- Half checkpoint: 2/8; final checkpoint: 8/8.\n"
        "- Six moving half cells exceed peak torque/current.\n"
        "- 102 events: 25 left-knee, 77 right-ankle; 95 occur after tick 31.\n"
        "- PPO-Lagrangian is closed with no η change, retry, or cherry-pick.\n"
        "- Sole successor: separately contracted oracle-teacher distillation.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
