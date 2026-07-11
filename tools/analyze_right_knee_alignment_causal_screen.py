#!/usr/bin/env python3
"""Audit a complete or early-stopped right-knee alignment causal screen."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


def failure(result: dict) -> bool:
    return result["summary"].get("termination_reason") != "duration_complete"


def early_error(result: dict, joint: int, ticks: int) -> float:
    trace = Path(result["output_dir"]) / "trace.jsonl"
    rows = [json.loads(line) for line in trace.read_text().splitlines()[:ticks]]
    values = [abs(row["applied_target_rad"][joint] - row["actual_position_rad"][joint]) for row in rows]
    return float(np.percentile(values, 95))


def main() -> int:
    args = parse_args()
    baseline = json.loads(Path(args.baseline).read_text())["results"]
    candidate_payload = json.loads(Path(args.candidate).read_text())
    candidate = candidate_payload["results"]
    by_seed = {int(row["seed"]): row for row in baseline}
    candidate_falls = [int(row["seed"]) for row in candidate if failure(row)]
    new_falls = [int(row["seed"]) for row in candidate if failure(row) and not failure(by_seed[int(row["seed"])])]
    recovered = [int(row["seed"]) for row in candidate if not failure(row) and failure(by_seed[int(row["seed"])])]
    tested_baseline_falls = [row for row in candidate if failure(by_seed[int(row["seed"])])]
    tracking = []
    for row in tested_baseline_falls:
        seed = int(row["seed"])
        before, after = early_error(by_seed[seed], args.joint_index, args.window_ticks), early_error(row, args.joint_index, args.window_ticks)
        tracking.append({"seed": seed, "baseline_p95_rad": before, "candidate_p95_rad": after, "decreased": after < before})
    criteria = {
        "falls_at_most_5": len(candidate_falls) <= 5,
        "no_new_falls": not new_falls,
        "passes_at_least_4": None,
        "mean_vx_not_regressed_more_than_0p01": None,
        "tracking_decreased_on_at_least_9_of_11_baseline_falls": None,
    }
    full = len(candidate) == len(baseline)
    if full:
        criteria["passes_at_least_4"] = sum("PASS_CANDIDATE_SIM_GATE" in str(row.get("status")) for row in candidate) >= 4
        mean_vx = float(np.mean([row["summary"]["mean_local_vx_m_s"] for row in candidate]))
        criteria["mean_vx_not_regressed_more_than_0p01"] = mean_vx >= -0.0385
        criteria["tracking_decreased_on_at_least_9_of_11_baseline_falls"] = sum(row["decreased"] for row in tracking) >= 9
    impossible = not criteria["falls_at_most_5"] or not criteria["no_new_falls"]
    report = {
        "status": "FAIL_CAUSAL_SCREEN_EARLY_STOP_ROUTE_CLOSED" if impossible else "COMPLETE_CAUSAL_SCREEN_PASS" if full and all(criteria.values()) else "INCOMPLETE_CAUSAL_SCREEN",
        "preregistration": args.preregistration,
        "baseline": args.baseline, "candidate": args.candidate,
        "evaluated_seeds": [int(row["seed"]) for row in candidate],
        "evaluated_runs": len(candidate), "planned_runs": len(baseline),
        "candidate_falls": candidate_falls, "new_falls": new_falls,
        "recovered_baseline_falls": recovered,
        "tracking_error_on_tested_baseline_falls": tracking,
        "criteria": criteria,
        "early_stop_justified": impossible,
        "decision": "Close exact right-knee bridge reset-alignment route without tuning." if impossible else "No final decision.",
        "deployment_authorized": False, "offline_only": True,
    }
    Path(args.output_json).write_text(json.dumps(report, indent=2) + "\n")
    lines = ["# Right-Knee Bridge Reset-Alignment Causal Result", "", f"Status: **{report['status']}**", "",
             f"- evaluated: `{len(candidate)}/{len(baseline)}` seeds (early stopped)",
             f"- candidate falls: `{candidate_falls}`", f"- new falls: `{new_falls}`",
             f"- recovered baseline falls: `{recovered}`", "", "## Frozen criteria", ""]
    lines += [f"- `{name}`: `{value}`" for name, value in criteria.items()]
    lines += ["", "## Decision", "", report["decision"], "",
              "The remaining criteria were not evaluated because two already-failed requirements cannot recover with additional seeds."]
    Path(args.output_md).write_text("\n".join(lines) + "\n")
    print(report["status"])
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", required=True)
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--joint-index", type=int, default=12)
    parser.add_argument("--window-ticks", type=int, default=10)
    parser.add_argument("--preregistration", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-md", required=True)
    return parser.parse_args()


if __name__ == "__main__": raise SystemExit(main())
