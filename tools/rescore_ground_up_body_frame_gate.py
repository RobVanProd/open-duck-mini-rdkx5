#!/usr/bin/env python3
"""Rescore saved ground-up evaluations with a body-frame progress gate."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def finite(value) -> bool:
    return isinstance(value, (int, float)) and value == value and abs(value) != float("inf")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("outputs/analysis/ground_up_recipe_search"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    evaluations = []
    changed_positive_runs = []
    corrected_full_positive_checkpoints = []
    for path in sorted(args.root.glob("*/eval_*.json")):
        try:
            payload = json.loads(path.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        corrected = []
        for run in payload.get("runs", []):
            emergence = run.get("emergence") or {}
            old_pass = bool(emergence.get("pass"))
            command_x = float(run.get("command_x") or 0.0)
            reasons = list(emergence.get("reasons") or [])
            local_velocity = emergence.get("mean_velocity_x_m_s")
            duration = emergence.get("requested_duration_s")
            local_progress = (
                float(local_velocity) * float(duration)
                if finite(local_velocity) and finite(duration)
                else None
            )
            corrected_reasons = reasons.copy()
            if command_x > 0.0:
                corrected_reasons = [
                    reason for reason in corrected_reasons
                    if reason != "no_positive_forward_displacement"
                ]
                if not finite(local_progress) or float(local_progress) <= 0.0:
                    corrected_reasons.append("no_positive_body_forward_progress")
            new_pass = not corrected_reasons
            row = {
                "command_x": command_x,
                "seed": run.get("seed"),
                "old_pass": old_pass,
                "corrected_pass": new_pass,
                "world_progress_x_m": emergence.get("progress_x_m"),
                "body_forward_progress_m": local_progress,
                "mean_body_forward_velocity_m_s": local_velocity,
                "old_reasons": reasons,
                "corrected_reasons": corrected_reasons,
            }
            corrected.append(row)
            if command_x > 0.0 and old_pass != new_pass:
                changed_positive_runs.append({"path": str(path), **row})
        positive = [row for row in corrected if row["command_x"] > 0.0]
        full_positive = bool(positive) and all(row["corrected_pass"] for row in positive)
        if full_positive:
            corrected_full_positive_checkpoints.append(str(path))
        evaluations.append({
            "path": str(path),
            "positive_runs": len(positive),
            "corrected_positive_passes": sum(row["corrected_pass"] for row in positive),
            "corrected_full_positive_checkpoint": full_positive,
        })

    result = {
        "schema_version": "ground_up_body_frame_gate_rescore.v1",
        "status": (
            "NO_HISTORICAL_FULL_POSITIVE_CHECKPOINT_AFTER_FRAME_REPAIR"
            if not corrected_full_positive_checkpoints
            else "HISTORICAL_FULL_POSITIVE_CHECKPOINT_FOUND"
        ),
        "evaluations": len(evaluations),
        "changed_positive_runs": changed_positive_runs,
        "changed_positive_run_count": len(changed_positive_runs),
        "corrected_full_positive_checkpoints": corrected_full_positive_checkpoints,
        "corrected_full_positive_checkpoint_count": len(corrected_full_positive_checkpoints),
        "historical_files_modified": False,
        "robot_access": False,
        "local_gpu_access": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "status": result["status"],
        "evaluations": len(evaluations),
        "changed_positive_run_count": len(changed_positive_runs),
        "corrected_full_positive_checkpoint_count": len(corrected_full_positive_checkpoints),
    }, indent=2))


if __name__ == "__main__":
    main()
