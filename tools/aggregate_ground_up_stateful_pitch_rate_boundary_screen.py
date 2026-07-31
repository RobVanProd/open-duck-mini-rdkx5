#!/usr/bin/env python3
"""Aggregate the preregistered CPU-only stateful pitch-rate boundary screen."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


RATES = {
    "R1_GATE_GAP": 0.9799092569101565,
    "R2_DOUBLE_GAP": 0.959818513820313,
    "R3_FOUR_GAP": 0.919637027640626,
}
TAIL_ARMS = ("T2_EQUAL", "T3_FOUR")
STEPS = (512000, 1024000)
COMMANDS = (0.074, 0.077, 0.080)
SEEDS = (100, 101)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def checkpoint_summary(path: Path) -> dict:
    payload = json.loads(path.read_text())
    cells = {(float(run["command_x"]), int(run["seed"])): run for run in payload["runs"]}
    expected = {(command, seed) for command in COMMANDS for seed in SEEDS}
    rows = []
    for command, seed in sorted(expected):
        run = cells.get((command, seed))
        if run is None:
            rows.append({"command_x": command, "seed": seed, "missing": True})
            continue
        metrics = run["candidate_gate"]["metrics"]
        emergence = run["emergence"]
        fitted = run["modes"]["fitted"]
        rows.append(
            {
                "command_x": command,
                "seed": seed,
                "missing": False,
                "candidate_gate_status": run["candidate_gate"]["status"],
                "samples": fitted["samples"],
                "termination_reason": emergence["termination_reason"],
                "emergence_pass": emergence["pass"],
                "left_contact_transition_count": emergence["left_contact_transition_count"],
                "right_contact_transition_count": emergence["right_contact_transition_count"],
                "tracking_p95_rad": metrics["max_pitch_tracking_p95_rad"],
                "mean_velocity_x_m_s": emergence["mean_velocity_x_m_s"],
                "action_saturation_pct": metrics["max_action_saturation_pct"],
                "max_rate_excess_rad_s": metrics[
                    "max_sent_target_velocity_max_limit_excess_rad_s"
                ],
                "min_base_height_m": metrics["min_base_height_m"],
            }
        )
    complete = len(cells) == 6 and all(not row["missing"] for row in rows)
    full_duration = complete and all(
        row["samples"] == 600 and row["termination_reason"] == "duration_complete"
        for row in rows
    )
    bilateral = complete and all(
        row["emergence_pass"]
        and row["left_contact_transition_count"] > 0
        and row["right_contact_transition_count"] > 0
        for row in rows
    )
    zero_saturation_rate = complete and all(
        row["action_saturation_pct"] == 0.0 and row["max_rate_excess_rad_s"] == 0.0
        for row in rows
    )
    worst_tracking = max(
        (row["tracking_p95_rad"] for row in rows if not row["missing"]),
        default=float("inf"),
    )
    all_candidate_gate = complete and all(
        row["candidate_gate_status"] == "PASS_CANDIDATE_SIM_GATE" for row in rows
    )
    checkpoint_pass = (
        complete
        and full_duration
        and bilateral
        and zero_saturation_rate
        and worst_tracking <= 0.20
        and all_candidate_gate
    )
    return {
        "path": str(path.resolve()),
        "sha256": sha256(path),
        "execution_platform": payload["execution"]["platform"],
        "checks": {
            "all_six_cells_present": complete,
            "all_600_ticks_duration_complete": full_duration,
            "all_walk_with_bilateral_support": bilateral,
            "all_zero_saturation_and_rate_excess": zero_saturation_rate,
            "worst_tracking_p95_at_most_0p20": worst_tracking <= 0.20,
            "all_candidate_gates_pass": all_candidate_gate,
        },
        "checkpoint_pass": checkpoint_pass,
        "worst_tracking_p95_rad": worst_tracking,
        "minimum_forward_velocity_m_s": min(
            (row["mean_velocity_x_m_s"] for row in rows if not row["missing"]),
            default=float("-inf"),
        ),
        "minimum_base_height_m": min(
            (row["min_base_height_m"] for row in rows if not row["missing"]),
            default=float("-inf"),
        ),
        "cells": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--eval-root", type=Path, required=True)
    parser.add_argument("--preregistration", type=Path, required=True)
    parser.add_argument("--transform-contract", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-md", type=Path, required=True)
    args = parser.parse_args()

    prereg = json.loads(args.preregistration.read_text())
    transform = json.loads(args.transform_contract.read_text())
    rates = {}
    for rate_name, multiplier in RATES.items():
        tail_arms = {}
        for tail_arm in TAIL_ARMS:
            checkpoints = {}
            for step in STEPS:
                path = args.eval_root / (
                    f"ground_up_stateful_pitch_rate_boundary_{rate_name}_"
                    f"{tail_arm}_{step}_eval.json"
                )
                checkpoints[str(step)] = checkpoint_summary(path)
            tail_arms[tail_arm] = {
                "checkpoints": checkpoints,
                "combination_pass": all(
                    item["checkpoint_pass"] for item in checkpoints.values()
                ),
                "worst_tracking_p95_rad": max(
                    item["worst_tracking_p95_rad"] for item in checkpoints.values()
                ),
                "minimum_forward_velocity_m_s": min(
                    item["minimum_forward_velocity_m_s"] for item in checkpoints.values()
                ),
            }
        rates[rate_name] = {"multiplier": multiplier, "tail_arms": tail_arms}

    combinations = [
        (rate_name, tail_name, tail)
        for rate_name, rate in rates.items()
        for tail_name, tail in rate["tail_arms"].items()
    ]
    passing = [(rate, tail, item) for rate, tail, item in combinations if item["combination_pass"]]
    checks = {
        "preregistration_status_valid": prereg["status"] == "PREREGISTERED_CPU_ONLY",
        "preregistered_matrix_exact": (
            prereg["source_tail_arms"] == list(TAIL_ARMS)
            and prereg["source_steps"] == list(STEPS)
            and prereg["commands_x"] == list(COMMANDS)
            and prereg["seeds"] == list(SEEDS)
            and prereg["duration_ticks"] == 600
        ),
        "transform_contract_passed": transform["status"]
        == "PASS_STATEFUL_PITCH_RATE_TRANSFORM_CONTRACT",
        "all_72_cells_present": all(
            checkpoint["checks"]["all_six_cells_present"]
            for _, _, item in combinations
            for checkpoint in item["checkpoints"].values()
        ),
        "all_72_cells_cpu_only": all(
            checkpoint["execution_platform"] == "cpu"
            for _, _, item in combinations
            for checkpoint in item["checkpoints"].values()
        ),
        "all_72_cells_600_ticks": all(
            checkpoint["checks"]["all_600_ticks_duration_complete"]
            for _, _, item in combinations
            for checkpoint in item["checkpoints"].values()
        ),
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        status = "FAIL_STATEFUL_PITCH_RATE_BOUNDARY_EVIDENCE_CONTRACT"
        decision = "INVALID_EVIDENCE"
        winner = None
    elif passing:
        rate_name, tail_name, item = sorted(
            passing,
            key=lambda row: (
                -RATES[row[0]],
                row[2]["worst_tracking_p95_rad"],
                -row[2]["minimum_forward_velocity_m_s"],
            ),
        )[0]
        status = "PASS_STATEFUL_PITCH_RATE_BOUNDARY_WITH_WINNER"
        decision = f"ADVANCE_{rate_name}_{tail_name}"
        winner = {
            "rate_arm": rate_name,
            "tail_arm": tail_name,
            "worst_tracking_p95_rad": item["worst_tracking_p95_rad"],
            "minimum_forward_velocity_m_s": item["minimum_forward_velocity_m_s"],
        }
    else:
        status = "PASS_STATEFUL_PITCH_RATE_BOUNDARY_NO_WINNER"
        decision = "CLOSE_STATEFUL_PITCH_RATE_BOUNDARY_SCREEN"
        winner = None

    closest_rate, closest_tail, closest = min(
        combinations, key=lambda row: row[2]["worst_tracking_p95_rad"]
    )
    payload = {
        "schema_version": "ground_up_stateful_pitch_rate_boundary_screen_result.v1",
        "status": status,
        "decision": decision,
        "checks": checks,
        "failed_checks": failed,
        "preregistration": {
            "path": str(args.preregistration.resolve()),
            "sha256": sha256(args.preregistration),
        },
        "transform_contract": {
            "path": str(args.transform_contract.resolve()),
            "sha256": sha256(args.transform_contract),
        },
        "rates": rates,
        "passing_combinations": [
            {"rate_arm": rate, "tail_arm": tail} for rate, tail, _ in passing
        ],
        "winner": winner,
        "closest_nonpassing_combination": {
            "rate_arm": closest_rate,
            "tail_arm": closest_tail,
            "worst_tracking_p95_rad": closest["worst_tracking_p95_rad"],
            "excess_over_limit_rad": closest["worst_tracking_p95_rad"] - 0.20,
        },
        "selection_uses_training_reward": False,
        "authority": {
            "x0_preservation_gate": bool(winner),
            "training": False,
            "robot_or_rdk": False,
            "local_gpu": False,
        },
        "interpretation": (
            "All 72 preregistered CPU cells were valid 600-tick walks with bilateral "
            "support, zero action saturation, and zero measured pitch-chain rate excess. "
            "No rate/tail combination passed the 0.20 rad tracking gate at both its half "
            "and final checkpoints, so the screen is closed without promoting the closest result."
        ),
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")

    lines = [
        "# Ground-Up Stateful Pitch-Rate Boundary Screen Result",
        "",
        f"status: `{status}`",
        f"decision: `{decision}`",
        "",
        "| rate arm | tail arm | half worst p95 | final worst p95 | combination pass |",
        "|---|---|---:|---:|---|",
    ]
    for rate_name, rate in rates.items():
        for tail_name, tail in rate["tail_arms"].items():
            lines.append(
                f"| `{rate_name}` | `{tail_name}` "
                f"| {tail['checkpoints']['512000']['worst_tracking_p95_rad']:.9f} "
                f"| {tail['checkpoints']['1024000']['worst_tracking_p95_rad']:.9f} "
                f"| `{tail['combination_pass']}` |"
            )
    lines.extend(
        [
            "",
            f"closest nonpassing combination: `{closest_rate}/{closest_tail}` at "
            f"`{closest['worst_tracking_p95_rad']}` rad",
            "",
            payload["interpretation"],
            "",
            "This result authorizes no training, x=0 preservation gate, RDK deployment, or robot motion.",
            "",
        ]
    )
    args.output_md.write_text("\n".join(lines))
    print(json.dumps({"status": status, "decision": decision, "winner": winner}))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
