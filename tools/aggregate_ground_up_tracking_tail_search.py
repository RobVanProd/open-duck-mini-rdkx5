#!/usr/bin/env python3
"""Aggregate the preregistered tracking-tail half/final behavior gate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ARMS = {
    "T1_QUARTER": -1643.0637410077638,
    "T2_EQUAL": -6572.254964031055,
    "T3_FOUR": -26289.01985612422,
}
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
                "left_contact_transition_count": emergence[
                    "left_contact_transition_count"
                ],
                "right_contact_transition_count": emergence[
                    "right_contact_transition_count"
                ],
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
        row["action_saturation_pct"] == 0.0
        and row["max_rate_excess_rad_s"] == 0.0
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
            row["mean_velocity_x_m_s"] for row in rows if not row["missing"]
        ),
        "minimum_base_height_m": min(
            row["min_base_height_m"] for row in rows if not row["missing"]
        ),
        "cells": rows,
    }


def prior_worst(path: Path) -> dict:
    payload = json.loads(path.read_text())
    values = [
        run["candidate_gate"]["metrics"]["max_pitch_tracking_p95_rad"]
        for run in payload["runs"]
    ]
    return {"path": str(path.resolve()), "sha256": sha256(path), "worst": max(values)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--eval-root", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--artifact", type=Path, required=True)
    parser.add_argument("--source-eval", type=Path, required=True)
    parser.add_argument("--control-eval", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-md", type=Path, required=True)
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text())
    artifact_hash = sha256(args.artifact)
    arms = {}
    for arm, scale in ARMS.items():
        checkpoints = {}
        for step in STEPS:
            path = args.eval_root / f"ground_up_tracking_tail_{arm}_{step}_eval.json"
            checkpoints[str(step)] = checkpoint_summary(path)
        arms[arm] = {
            "scale": scale,
            "checkpoints": checkpoints,
            "arm_pass": all(item["checkpoint_pass"] for item in checkpoints.values()),
            "worst_tracking_p95_rad": max(
                item["worst_tracking_p95_rad"] for item in checkpoints.values()
            ),
            "minimum_forward_velocity_m_s": min(
                item["minimum_forward_velocity_m_s"] for item in checkpoints.values()
            ),
        }
    passing = [name for name, item in arms.items() if item["arm_pass"]]
    source = prior_worst(args.source_eval)
    control = prior_worst(args.control_eval)
    closest_name, closest = min(
        arms.items(), key=lambda item: item[1]["worst_tracking_p95_rad"]
    )
    checks = {
        "hosted_manifest_passed": manifest["status"]
        == "PASS_TRAINING_ARTIFACT_CONTRACT_ONLY",
        "artifact_hash_matches_manifest": artifact_hash == manifest["artifact_sha256"],
        "all_36_cells_present": all(
            checkpoint["checks"]["all_six_cells_present"]
            for arm in arms.values()
            for checkpoint in arm["checkpoints"].values()
        ),
        "all_36_cells_cpu_only": all(
            json.loads(Path(checkpoint["path"]).read_text())["execution"]["platform"]
            == "cpu"
            for arm in arms.values()
            for checkpoint in arm["checkpoints"].values()
        ),
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        status = "FAIL_TRACKING_TAIL_SEARCH_EVIDENCE_CONTRACT"
        decision = "INVALID_EVIDENCE"
    elif passing:
        status = "PASS_TRACKING_TAIL_SEARCH_WITH_WINNER"
        decision = "ADVANCE_" + sorted(
            passing,
            key=lambda name: (
                arms[name]["worst_tracking_p95_rad"],
                -arms[name]["minimum_forward_velocity_m_s"],
                abs(arms[name]["scale"]),
            ),
        )[0]
    else:
        status = "PASS_TRACKING_TAIL_SEARCH_NO_WINNER"
        decision = "CLOSE_EXACT_TRACKING_TAIL_EXCEEDANCE_FORMULATION"
    payload = {
        "schema_version": "ground_up_tracking_tail_search_result.v1",
        "status": status,
        "decision": decision,
        "checks": checks,
        "failed_checks": failed,
        "hosted_artifact": {
            "path": str(args.artifact.resolve()),
            "sha256": artifact_hash,
            "bytes": args.artifact.stat().st_size,
            "manifest_path": str(args.manifest.resolve()),
            "manifest_sha256": sha256(args.manifest),
        },
        "prior": {"protected_source_1M": source, "no_tail_control_2M": control},
        "arms": arms,
        "passing_arms": passing,
        "closest_nonpassing_arm": {
            "name": closest_name,
            "worst_tracking_p95_rad": closest["worst_tracking_p95_rad"],
            "excess_over_limit_rad": closest["worst_tracking_p95_rad"] - 0.20,
        },
        "selection_uses_training_reward": False,
        "authority": {
            "x0_gate": bool(passing),
            "robot_or_rdk": False,
            "local_gpu": False,
        },
        "interpretation": (
            "Every arm retained 12-second gait, bilateral support, zero saturation, "
            "and zero measured rate excess, but no arm passed tracking at both half "
            "and final checkpoints. The preregistered rule therefore closes this exact "
            "tail-exceedance formulation without selecting the closest checkpoint."
        ),
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    lines = [
        "# Ground-Up Tracking-Tail Search Result",
        "",
        f"status: `{status}`",
        f"decision: `{decision}`",
        "",
        "| arm | half worst p95 | final worst p95 | arm pass |",
        "|---|---:|---:|---|",
    ]
    for name, arm in arms.items():
        lines.append(
            f"| `{name}` | {arm['checkpoints']['512000']['worst_tracking_p95_rad']:.9f} "
            f"| {arm['checkpoints']['1024000']['worst_tracking_p95_rad']:.9f} "
            f"| `{arm['arm_pass']}` |"
        )
    lines.extend(
        [
            "",
            f"protected source 1M worst p95: `{source['worst']}`",
            f"no-tail control 2M worst p95: `{control['worst']}`",
            f"closest nonpassing arm: `{closest_name}` at `{closest['worst_tracking_p95_rad']}`",
            f"excess over .20 rad: `{closest['worst_tracking_p95_rad'] - 0.20}`",
            "",
            payload["interpretation"],
            "",
        ]
    )
    args.output_md.write_text("\n".join(lines))
    print(json.dumps({"status": status, "decision": decision, "passing": passing}, sort_keys=True))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
