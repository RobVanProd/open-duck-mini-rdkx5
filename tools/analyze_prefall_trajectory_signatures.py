#!/usr/bin/env python3
"""Test preregistered physical pre-fall signatures in saved traces."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


FEATURES = (
    "base_height_drop_m",
    "abs_pitch_growth_rad",
    "adverse_forward_velocity_m_s",
    "actuator_tracking_error_p95_rad",
    "joint_speed_p95_rad_s",
    "contact_transition_count",
)


def auc(scores: np.ndarray, labels: np.ndarray) -> float:
    positive, negative = scores[labels], scores[~labels]
    return float(np.mean(
        (positive[:, None] > negative[None, :])
        + 0.5 * (positive[:, None] == negative[None, :])
    ))


def features(rows: list[dict], ticks: int) -> dict[str, float]:
    rows = rows[:ticks]
    if len(rows) < ticks:
        raise ValueError(f"trace has only {len(rows)} rows, needs {ticks}")
    height = np.asarray([row["base_height_m"] for row in rows], dtype=float)
    pitch = np.abs(np.asarray([row["body_pitch_rad"] for row in rows], dtype=float))
    velocity = np.asarray([row["local_linvel_m_s"][0] for row in rows], dtype=float)
    tracking = np.asarray([
        np.max(np.abs(np.asarray(row["applied_target_rad"]) - np.asarray(row["actual_position_rad"])))
        for row in rows
    ])
    joint_speed = np.asarray([
        np.max(np.abs(np.asarray(row["qvel"], dtype=float)[-14:])) for row in rows
    ])
    contacts = [tuple(int(value) for value in row["foot_contacts"]) for row in rows]
    return {
        "base_height_drop_m": float(height[0] - np.min(height)),
        "abs_pitch_growth_rad": float(np.max(pitch) - pitch[0]),
        "adverse_forward_velocity_m_s": float(-np.mean(velocity)),
        "actuator_tracking_error_p95_rad": float(np.percentile(tracking, 95)),
        "joint_speed_p95_rad_s": float(np.percentile(joint_speed, 95)),
        "contact_transition_count": float(sum(a != b for a, b in zip(contacts, contacts[1:]))),
    }


def load_block(name: str, path: str, ticks: int) -> dict:
    sweep = json.loads(Path(path).read_text())
    rows = []
    for result in sweep["results"]:
        trace = Path(result["output_dir"]) / "trace.jsonl"
        records = [json.loads(line) for line in trace.read_text().splitlines() if line.strip()]
        rows.append({
            "seed": int(result["seed"]),
            "failure": result["summary"].get("termination_reason") != "duration_complete",
            "features": features(records, ticks),
        })
    labels = np.asarray([row["failure"] for row in rows], dtype=bool)
    if not np.any(labels) or np.all(labels):
        raise ValueError(f"block {name} needs both outcome classes")
    metrics = {}
    for feature in FEATURES:
        values = np.asarray([row["features"][feature] for row in rows])
        metrics[feature] = {
            "roc_auc": auc(values, labels),
            "failure_mean": float(np.mean(values[labels])),
            "complete_mean": float(np.mean(values[~labels])),
        }
    return {
        "name": name, "sweep": path, "samples": len(rows),
        "failures": int(np.sum(labels)), "duration_complete": int(np.sum(~labels)),
        "metrics": metrics, "per_seed": rows,
    }


def main() -> int:
    args = parse_args()
    blocks = [load_block(name, path, args.window_ticks) for name, path in args.block]
    passing = [
        feature for feature in FEATURES
        if all(block["metrics"][feature]["roc_auc"] >= args.minimum_auc for block in blocks)
    ]
    report = {
        "status": "CANDIDATE_RECOVERY_VARIABLES_IDENTIFIED" if passing else "NO_REPLICATED_SIMPLE_RECOVERY_VARIABLE_ROUTE_CLOSED",
        "preregistration": args.preregistration,
        "window_ticks": args.window_ticks,
        "window_seconds": args.window_ticks * args.dt_s,
        "minimum_auc_each_block": args.minimum_auc,
        "features": list(FEATURES),
        "blocks": blocks,
        "passing_features": passing,
        "decision": (
            "Treat passing features only as candidate recovery variables requiring causal intervention tests."
            if passing else
            "Close this simple physical-signature route without post-hoc feature or window tuning."
        ),
        "intervention_authorized": False,
        "offline_only": True,
    }
    Path(args.output_json).write_text(json.dumps(report, indent=2) + "\n")
    write_markdown(Path(args.output_md), report)
    print(report["status"])
    return 0


def write_markdown(path: Path, report: dict) -> None:
    blocks = report["blocks"]
    lines = [
        "# Pre-Fall Trajectory Signature Result", "",
        f"Status: **{report['status']}**", "",
        "Offline analysis of existing traces only. No intervention, training, robot, GPU, or Colab use.", "",
        f"Window: first `{report['window_ticks']}` ticks (`{report['window_seconds']:.2f}` seconds)", "",
        "| feature | " + " | ".join(f"{block['name']} AUC" for block in blocks) + " | minimum | passes |",
        "|---|" + "---:|" * (len(blocks) + 2),
    ]
    for feature in report["features"]:
        values = [block["metrics"][feature]["roc_auc"] for block in blocks]
        lines.append(
            f"| `{feature}` | " + " | ".join(f"{value:.3f}" for value in values)
            + f" | {min(values):.3f} | `{feature in report['passing_features']}` |"
        )
    lines += ["", "## Decision", "", report["decision"], "",
              "Passing is association evidence only; no intervention is authorized."]
    path.write_text("\n".join(lines) + "\n")


def parse_block(value: str) -> tuple[str, str]:
    if "=" not in value:
        raise argparse.ArgumentTypeError("block must be NAME=SWEEP_JSON")
    return tuple(value.split("=", 1))  # type: ignore[return-value]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--block", action="append", type=parse_block, required=True)
    parser.add_argument("--window-ticks", type=int, default=10)
    parser.add_argument("--dt-s", type=float, default=0.02)
    parser.add_argument("--minimum-auc", type=float, default=0.70)
    parser.add_argument("--preregistration", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-md", required=True)
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(main())
