#!/usr/bin/env python3
"""Test whether teacher disagreement precedes saved closed-loop failures.

Offline saved-trace analysis only. No training, simulation, deployment, robot
access, or GPU use is performed.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from compare_policy_to_behavior_prior import predict_mlp_npz


def roc_auc(scores: list[float], labels: list[bool]) -> float:
    positive = [score for score, label in zip(scores, labels, strict=True) if label]
    negative = [score for score, label in zip(scores, labels, strict=True) if not label]
    if not positive or not negative:
        raise ValueError("ROC AUC requires positive and negative examples")
    wins = sum(
        float(pos > neg) + 0.5 * float(pos == neg)
        for pos in positive
        for neg in negative
    )
    return wins / (len(positive) * len(negative))


def main() -> int:
    args = parse_args()
    sweep = json.loads(Path(args.sweep).read_text())
    teacher = Path(args.teacher_npz)
    traces = []
    for result in sweep.get("results", []):
        path = Path(result["output_dir"]) / "trace.jsonl"
        rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
        observations = np.asarray([row["obs_state"] for row in rows], dtype=np.float64)
        actions = np.asarray([row["action"] for row in rows], dtype=np.float64)
        disagreement = np.abs(predict_mlp_npz(teacher, observations) - actions)
        traces.append(
            {
                "seed": int(result["seed"]),
                "failure": result["summary"].get("termination_reason")
                != "duration_complete",
                "samples": len(rows),
                "disagreement": disagreement,
            }
        )
    labels = [item["failure"] for item in traces]
    windows = []
    for ticks in args.window_ticks:
        row = {"ticks": ticks, "seconds": ticks * args.dt_s, "statistics": {}}
        for name in ("mean", "p95", "max"):
            scores = []
            for item in traces:
                values = item["disagreement"][:ticks]
                score = {
                    "mean": float(np.mean(values)),
                    "p95": float(np.percentile(values, 95)),
                    "max": float(np.max(values)),
                }[name]
                scores.append(score)
            positive = [score for score, label in zip(scores, labels, strict=True) if label]
            negative = [score for score, label in zip(scores, labels, strict=True) if not label]
            row["statistics"][name] = {
                "roc_auc": roc_auc(scores, labels),
                "failure_mean": float(np.mean(positive)),
                "complete_mean": float(np.mean(negative)),
            }
        windows.append(row)
    per_seed = []
    report_ticks = args.report_window_ticks
    for item in traces:
        values = item["disagreement"][:report_ticks]
        per_seed.append(
            {
                "seed": item["seed"],
                "failure": item["failure"],
                "samples": item["samples"],
                "window_ticks": report_ticks,
                "mean": float(np.mean(values)),
                "p95": float(np.percentile(values, 95)),
                "max": float(np.max(values)),
            }
        )
    report = {
        "status": "PASS_TEACHER_CORRECTION_EARLY_WARNING_ANALYSIS_READY",
        "sweep": args.sweep,
        "teacher_npz": args.teacher_npz,
        "traces": len(traces),
        "failures": sum(labels),
        "duration_complete": len(labels) - sum(labels),
        "dt_s": args.dt_s,
        "windows": windows,
        "per_seed": per_seed,
        "interpretation": (
            "Teacher disagreement contains early failure information but is not a recovery target. "
            "No operating threshold is selected by this exploratory analysis."
        ),
        "evaluation_role": "heldout" if args.heldout else "discovery",
        "limitations": [
            (
                "This is a held-out seed block relative to the frozen discovery metrics, but it contains few failure positives."
                if args.heldout
                else "The same traces are used to identify and estimate the discovery AUC; no held-out claim is made by this artifact."
            ),
            "AUC measures ranking, not calibrated probability or a safe threshold.",
            "Teacher disagreement can identify out-of-distribution states while still proposing unsafe actions.",
        ],
        "offline_only": True,
    }
    Path(args.output_json).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output_json).write_text(json.dumps(report, indent=2) + "\n")
    write_markdown(Path(args.output_md), report)
    print(report["status"])
    return 0


def write_markdown(path: Path, report: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Teacher-Correction Early-Warning Analysis",
        "",
        f"status: `{report['status']}`",
        "",
        "Offline saved-trace analysis only. No simulation, training, robot access,",
        "deployment, GPU, or Colab allocation was performed.",
        "",
        f"- traces: `{report['traces']}`",
        f"- failures/completed: `{report['failures']}` / `{report['duration_complete']}`",
        "",
        "## Window Ranking",
        "",
        "| window | statistic | ROC AUC | failure mean | completed mean |",
        "|---:|---|---:|---:|---:|",
    ]
    for window in report["windows"]:
        for name, item in window["statistics"].items():
            lines.append(
                f"| {window['ticks']} ticks ({window['seconds']:.2f}s) | `{name}` | "
                f"{item['roc_auc']:.3f} | {item['failure_mean']:.5f} | "
                f"{item['complete_mean']:.5f} |"
            )
    lines += [
        "",
        "## Per-Seed First Window",
        "",
        f"Window: `{report['per_seed'][0]['window_ticks']}` ticks",
        "",
        "| seed | failure | mean | p95 | max |",
        "|---:|---:|---:|---:|---:|",
    ]
    for item in report["per_seed"]:
        lines.append(
            f"| {item['seed']} | `{item['failure']}` | {item['mean']:.5f} | "
            f"{item['p95']:.5f} | {item['max']:.5f} |"
        )
    lines += [
        "",
        "## Interpretation",
        "",
        report["interpretation"],
        "",
        "## Limitations",
        "",
    ]
    lines.extend(f"- {item}" for item in report["limitations"])
    path.write_text("\n".join(lines) + "\n")


def parse_int_list(value: str) -> list[int]:
    return [int(item.strip()) for item in value.split(",") if item.strip()]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sweep", required=True)
    parser.add_argument("--teacher-npz", required=True)
    parser.add_argument("--window-ticks", type=parse_int_list, default=parse_int_list("1,3,5,10,20"))
    parser.add_argument("--report-window-ticks", type=int, default=10)
    parser.add_argument("--dt-s", type=float, default=0.02)
    parser.add_argument("--heldout", action="store_true")
    parser.add_argument("--output-md", required=True)
    parser.add_argument("--output-json", required=True)
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(main())
