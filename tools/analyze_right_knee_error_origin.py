#!/usr/bin/env python3
"""Distinguish reset-initialized from control-grown right-knee error."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

FEATURES = ("tick0_abs_error_rad", "max_error_growth_rad", "tick9_to_tick0_error_ratio")


def auc(scores: np.ndarray, labels: np.ndarray) -> float:
    pos, neg = scores[labels], scores[~labels]
    return float(np.mean((pos[:, None] > neg[None, :]) + 0.5 * (pos[:, None] == neg[None, :])))


def block(name: str, path: str, ticks: int, joint: int) -> dict:
    sweep = json.loads(Path(path).read_text())
    rows = []
    for result in sweep["results"]:
        trace = Path(result["output_dir"]) / "trace.jsonl"
        records = [json.loads(line) for line in trace.read_text().splitlines()[:ticks]]
        error = np.abs(np.asarray([row["applied_target_rad"][joint] - row["actual_position_rad"][joint] for row in records]))
        rows.append({
            "seed": int(result["seed"]),
            "failure": result["summary"].get("termination_reason") != "duration_complete",
            "tick0_abs_error_rad": float(error[0]),
            "max_error_growth_rad": float(np.max(error) - error[0]),
            "tick9_to_tick0_error_ratio": float(error[-1] / max(error[0], 1e-6)),
        })
    labels = np.asarray([row["failure"] for row in rows], dtype=bool)
    metrics = {}
    for feature in FEATURES:
        values = np.asarray([row[feature] for row in rows])
        metrics[feature] = {"roc_auc": auc(values, labels), "failure_mean": float(np.mean(values[labels])), "complete_mean": float(np.mean(values[~labels]))}
    return {"name": name, "sweep": path, "samples": len(rows), "failures": int(np.sum(labels)), "metrics": metrics, "per_seed": rows}


def main() -> int:
    args = parse_args()
    blocks = [block(name, path, args.window_ticks, args.joint_index) for name, path in args.block]
    reset = all(b["metrics"]["tick0_abs_error_rad"]["roc_auc"] >= args.minimum_auc for b in blocks)
    growth = all(b["metrics"]["max_error_growth_rad"]["roc_auc"] >= args.minimum_auc for b in blocks)
    status = "RESET_ORIGIN_SUPPORTED" if reset and not growth else "CONTROL_GROWTH_SUPPORTED" if growth and not reset else "BOTH_ERROR_ORIGINS_SUPPORTED" if reset and growth else "NO_SIMPLE_ERROR_ORIGIN_REPLICATED"
    report = {
        "status": status, "preregistration": args.preregistration,
        "joint_index": args.joint_index, "joint_name": "right_knee",
        "window_ticks": args.window_ticks, "minimum_auc_each_block": args.minimum_auc,
        "blocks": blocks, "reset_origin_supported": reset, "control_growth_supported": growth,
        "decision": "Mechanism is associative; a matched causal screen must be separately preregistered.",
        "intervention_authorized": False, "offline_only": True,
    }
    Path(args.output_json).write_text(json.dumps(report, indent=2) + "\n")
    lines = ["# Right-Knee Error-Origin Result", "", f"Status: **{status}**", "",
             "| feature | " + " | ".join(f"{b['name']} AUC" for b in blocks) + " | minimum |",
             "|---|" + "---:|" * (len(blocks) + 1)]
    for feature in FEATURES:
        values = [b["metrics"][feature]["roc_auc"] for b in blocks]
        lines.append(f"| `{feature}` | " + " | ".join(f"{value:.3f}" for value in values) + f" | {min(values):.3f} |")
    lines += ["", f"- reset origin supported: `{reset}`", f"- control growth supported: `{growth}`", "", "No intervention is authorized."]
    Path(args.output_md).write_text("\n".join(lines) + "\n")
    print(status)
    return 0


def parse_block(value: str) -> tuple[str, str]:
    if "=" not in value: raise argparse.ArgumentTypeError("block must be NAME=SWEEP_JSON")
    return tuple(value.split("=", 1))  # type: ignore[return-value]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--block", action="append", type=parse_block, required=True)
    parser.add_argument("--joint-index", type=int, default=12)
    parser.add_argument("--window-ticks", type=int, default=10)
    parser.add_argument("--minimum-auc", type=float, default=0.70)
    parser.add_argument("--preregistration", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-md", required=True)
    return parser.parse_args()


if __name__ == "__main__": raise SystemExit(main())
