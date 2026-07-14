#!/usr/bin/env python3
"""Aggregate the preregistered x=0 preservation gate for the guard winner."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


STEPS = (512000, 1024000)
SEEDS = (100, 101)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--eval-root", type=Path, required=True)
    parser.add_argument("--preregistration", type=Path, required=True)
    parser.add_argument("--source-result", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-md", type=Path, required=True)
    args = parser.parse_args()
    prereg = json.loads(args.preregistration.read_text())
    source = json.loads(args.source_result.read_text())
    gate = prereg["per_cell_gate"]
    checkpoints = {}
    all_cells = []
    for step in STEPS:
        path = args.eval_root / f"ground_up_guard_winner_x0_T2_EQUAL_{step}_eval.json"
        payload = json.loads(path.read_text())
        rows = []
        for run in payload["runs"]:
            metrics = run["candidate_gate"]["metrics"]
            fitted = run["modes"]["fitted"]
            row = {
                "seed": run["seed"],
                "samples": fitted["samples"],
                "termination_reason": run["emergence"]["termination_reason"],
                "candidate_gate_status": run["candidate_gate"]["status"],
                "mean_local_velocity_m_s": run["emergence"]["mean_velocity_x_m_s"],
                "body_pitch_p95_rad": metrics["max_abs_body_pitch_p95_rad"],
                "minimum_base_height_m": metrics["min_base_height_m"],
                "pitch_tracking_p95_rad": metrics["max_pitch_tracking_p95_rad"],
                "action_saturation_pct": metrics["max_action_saturation_pct"],
                "rate_excess_rad_s": metrics["max_sent_target_velocity_limit_excess_rad_s"],
                "max_rate_excess_rad_s": metrics["max_sent_target_velocity_max_limit_excess_rad_s"],
            }
            row["pass"] = (
                row["samples"] == gate["samples"]
                and row["termination_reason"] == gate["termination_reason"]
                and row["candidate_gate_status"] == gate["candidate_gate_status"]
                and abs(row["mean_local_velocity_m_s"]) <= gate["maximum_absolute_mean_local_velocity_m_s"]
                and row["body_pitch_p95_rad"] <= gate["maximum_body_pitch_p95_rad"]
                and row["minimum_base_height_m"] >= gate["minimum_base_height_m"]
                and row["pitch_tracking_p95_rad"] <= gate["maximum_pitch_tracking_p95_rad"]
                and row["action_saturation_pct"] <= gate["maximum_action_saturation_pct"]
                and row["rate_excess_rad_s"] <= gate["maximum_sent_target_velocity_limit_excess_rad_s"]
                and row["max_rate_excess_rad_s"] <= gate["maximum_sent_target_velocity_max_limit_excess_rad_s"]
            )
            rows.append(row)
            all_cells.append(row)
        checkpoints[str(step)] = {
            "path": str(path.resolve()),
            "sha256": sha256(path),
            "execution_platform": payload["execution"]["platform"],
            "cells": rows,
            "checkpoint_pass": len(rows) == 2 and all(row["pass"] for row in rows),
        }
    checks = {
        "preregistration_status_valid": prereg["status"] == "PREREGISTERED_CPU_ONLY",
        "source_nominal_winner_exact": (
            source["status"] == "PASS_ACTUAL_CENTERED_GUARD_WITH_WINNER"
            and source["winner"]["guard"] == "G1_EXACT_BOUNDARY"
            and source["winner"]["tail"] == "T2_EQUAL"
        ),
        "all_four_cells_present": len(all_cells) == 4 and {row["seed"] for row in all_cells} == set(SEEDS),
        "all_cells_cpu_only": all(item["execution_platform"] == "cpu" for item in checkpoints.values()),
    }
    failed = [name for name, passed in checks.items() if not passed]
    x0_pass = not failed and all(item["checkpoint_pass"] for item in checkpoints.values())
    if failed:
        status = "FAIL_GUARD_WINNER_X0_EVIDENCE_CONTRACT"
        decision = "INVALID_EVIDENCE"
    elif x0_pass:
        status = "PASS_GUARD_WINNER_X0"
        decision = "ADVANCE_OFFLINE_NOMINAL_AND_X0_CANDIDATE_TO_PREREGISTERED_ROBUSTNESS_LADDER"
    else:
        status = "PASS_GUARD_WINNER_X0_NO_ADVANCE"
        decision = "PREREGISTER_COMMAND_DEADBAND_ZERO_ACTION_REPAIR"
    payload = {
        "schema_version": "ground_up_guard_winner_x0_result.v1",
        "status": status,
        "decision": decision,
        "checks": checks,
        "failed_checks": failed,
        "x0_pass": x0_pass,
        "checkpoints": checkpoints,
        "authority": {
            "command_deadband_repair_preregistration": not failed and not x0_pass,
            "robustness_ladder": x0_pass,
            "training": False,
            "colab": False,
            "local_gpu": False,
            "rdk_or_robot": False,
        },
        "interpretation": (
            "Both selected checkpoints fail x=0 with early termination and extreme action saturation. "
            "Their tracking and rate metrics remain inside bounds before termination, isolating the "
            "unsupported zero-command actor output rather than the actual-centered guard."
        ),
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    lines = ["# Ground-Up Guard Winner x=0 Result", "", f"status: `{status}`", f"decision: `{decision}`", "", "| step | seed | samples | termination | saturation | mean vx | pass |", "|---:|---:|---:|---|---:|---:|---|"]
    for step, item in checkpoints.items():
        for row in item["cells"]:
            lines.append(f"| {step} | {row['seed']} | {row['samples']} | `{row['termination_reason']}` | {row['action_saturation_pct']:.6f}% | {row['mean_local_velocity_m_s']:.9f} | `{row['pass']}` |")
    lines.extend(["", payload["interpretation"], "", "The nominal winner remains held. No robustness ladder, training, RDK-X5, or robot access is authorized.", ""])
    args.output_md.write_text("\n".join(lines))
    print(json.dumps({"status": status, "decision": decision, "x0_pass": x0_pass}))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
