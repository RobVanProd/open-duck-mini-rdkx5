#!/usr/bin/env python3
"""Replay a saved MLP router gate on a closed-loop trace.

This is an offline trace diagnostic. It does not train, deploy, SSH, run robot
tests, change runtime behavior, or run grounded replay.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]


def now_utc() -> str:
    return dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def rel(path: Path | str | None) -> str | None:
    if path is None:
        return None
    p = Path(path)
    try:
        return str(p.resolve().relative_to(ROOT))
    except ValueError:
        return str(p)


def percentile(values: np.ndarray, q: float) -> float | None:
    arr = np.asarray(values, dtype=np.float64).reshape(-1)
    arr = arr[np.isfinite(arr)]
    if arr.size == 0:
        return None
    return float(np.percentile(arr, q))


def load_gate_npz(path: Path) -> dict[str, Any]:
    data = np.load(path, allow_pickle=False)
    norm = np.asarray(data["obs_norm"], dtype=np.float64)
    layers = []
    index = 0
    while f"w_{index}" in data and f"b_{index}" in data:
        layers.append((np.asarray(data[f"w_{index}"], dtype=np.float64), np.asarray(data[f"b_{index}"], dtype=np.float64)))
        index += 1
    if norm.shape != (2, 101) or not layers:
        raise ValueError(f"invalid gate NPZ: {path}")
    return {"norm": norm, "layers": layers}


def forward_gate(obs: np.ndarray, gate: dict[str, Any]) -> np.ndarray:
    mean, std = gate["norm"]
    z = (obs - mean) / std
    for index, (weights, bias) in enumerate(gate["layers"]):
        z = z @ weights + bias
        if index < len(gate["layers"]) - 1:
            z = z / (1.0 + np.exp(-z))
    return z.reshape(-1)


def read_trace(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open() as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    if not rows:
        raise ValueError(f"empty trace: {path}")
    return rows


def bool_summary(
    mask: np.ndarray, values: np.ndarray, threshold: float, direction: str
) -> dict[str, Any]:
    if mask.size == 0:
        return {"samples": 0, "branch_b_pct": None, "logit_p50": None, "logit_p05": None, "logit_p95": None}
    selected = values[mask] if mask.dtype == bool else values[np.asarray(mask, dtype=bool)]
    if selected.size == 0:
        return {"samples": 0, "branch_b_pct": None, "logit_p50": None, "logit_p05": None, "logit_p95": None}
    branch = selected >= threshold if direction == "ge" else selected <= threshold
    return {
        "samples": int(selected.size),
        "branch_b_pct": float(np.mean(branch) * 100.0),
        "logit_p05": percentile(selected, 5),
        "logit_p50": percentile(selected, 50),
        "logit_p95": percentile(selected, 95),
    }


def summarize_windows(
    rows: list[dict[str, Any]],
    logits: np.ndarray,
    tail_ticks: int,
    threshold: float,
    direction: str,
) -> dict[str, Any]:
    n = len(rows)
    all_mask = np.ones((n,), dtype=bool)
    first_mask = np.zeros((n,), dtype=bool)
    first_mask[: min(tail_ticks, n)] = True
    tail_mask = np.zeros((n,), dtype=bool)
    tail_mask[max(0, n - tail_ticks) :] = True
    push_mask = np.asarray([float(row.get("push_magnitude") or 0.0) > 0.0 for row in rows], dtype=bool)
    single_support = np.asarray([
        sum(int(v) for v in (row.get("foot_contacts") or [0, 0])[:2]) == 1 for row in rows
    ], dtype=bool)
    double_support = np.asarray([
        sum(int(v) for v in (row.get("foot_contacts") or [0, 0])[:2]) == 2 for row in rows
    ], dtype=bool)
    reverse = np.asarray([
        float((row.get("local_linvel_m_s") or [0.0])[0]) < 0.0 for row in rows
    ], dtype=bool)
    return {
        "all": bool_summary(all_mask, logits, threshold, direction),
        "first_ticks": bool_summary(first_mask, logits, threshold, direction),
        "tail_ticks": bool_summary(tail_mask, logits, threshold, direction),
        "push_ticks": bool_summary(push_mask, logits, threshold, direction),
        "single_support": bool_summary(single_support, logits, threshold, direction),
        "double_support": bool_summary(double_support, logits, threshold, direction),
        "reverse_vx": bool_summary(reverse, logits, threshold, direction),
    }


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    lines = [
        "# MLP Router Branch Trace",
        "",
        f"status: `{report['status']}`",
        "",
        "Offline trace diagnostic only. It did not train, deploy, SSH, run robot tests, change runtime behavior, or run grounded replay.",
        "",
        "## Inputs",
        "",
        f"- trace: `{report['trace']}`",
        f"- gate_npz: `{report['gate_npz']}`",
        f"- threshold: `{report['threshold']}`",
        f"- direction: `{report['direction']}`",
        f"- samples: `{report['samples']}`",
        f"- termination: `{report['termination_reason']}`",
        "",
        "## Branch Selection",
        "",
        "| window | samples | branch_b_pct | logit_p05 | logit_p50 | logit_p95 |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for name, item in report["windows"].items():
        lines.append(
            f"| {name} | {item['samples']} | "
            f"{item['branch_b_pct'] if item['branch_b_pct'] is not None else 'NA'} | "
            f"{item['logit_p05'] if item['logit_p05'] is not None else 'NA'} | "
            f"{item['logit_p50'] if item['logit_p50'] is not None else 'NA'} | "
            f"{item['logit_p95'] if item['logit_p95'] is not None else 'NA'} |"
        )
    lines.extend(
        [
            "",
            "## Outcome",
            "",
            f"- mean_vx_m_s: `{report['mean_vx_m_s']:.4f}`",
            f"- base_height_min_m: `{report['base_height_min_m']:.4f}`",
            f"- body_pitch_abs_p95_rad: `{report['body_pitch_abs_p95_rad']:.4f}`",
            "",
            "## Decision",
            "",
            report["decision"],
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trace", required=True)
    parser.add_argument("--gate-npz", required=True)
    parser.add_argument("--threshold", type=float, default=0.0)
    parser.add_argument("--direction", choices=["ge", "le"], default="ge")
    parser.add_argument("--tail-ticks", type=int, default=80)
    parser.add_argument("--output-md", required=True)
    parser.add_argument("--output-json", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    trace_path = Path(args.trace)
    gate_path = Path(args.gate_npz)
    rows = read_trace(trace_path)
    obs = np.asarray([row["obs_state"] for row in rows], dtype=np.float64)
    gate = load_gate_npz(gate_path)
    logits = forward_gate(obs, gate)
    vx = np.asarray([float((row.get("local_linvel_m_s") or [0.0])[0]) for row in rows], dtype=np.float64)
    base_height = np.asarray([float(row.get("base_height_m", np.nan)) for row in rows], dtype=np.float64)
    pitch_abs = np.asarray([abs(float(row.get("body_pitch_rad", 0.0))) for row in rows], dtype=np.float64)
    termination = "duration_complete"
    if rows and bool(rows[-1].get("done", False)):
        termination = "fall_or_nan"
    windows = summarize_windows(rows, logits, int(args.tail_ticks), float(args.threshold), args.direction)
    selected_b = logits >= float(args.threshold) if args.direction == "ge" else logits <= float(args.threshold)
    branch_b_pct = float(np.mean(selected_b) * 100.0)
    first_branch_b_pct = windows["first_ticks"]["branch_b_pct"]
    if first_branch_b_pct is not None and first_branch_b_pct >= 80.0:
        status = "HOLD_ROUTER_STARTUP_BRANCH_B_ON_FAILED_TRACE"
        decision = (
            "The failed trace starts on branch B for most of the startup window, then flips away late. "
            "Train the gate with a seed-0 startup cost or prefix validation pressure before composing another router."
        )
    elif branch_b_pct >= 50.0:
        status = "HOLD_ROUTER_BRANCH_B_DOMINATES_FAILED_TRACE"
        decision = (
            "The failed trace spends most ticks on branch B. Tighten or cost-train the MLP gate so the seed-5 branch is not selected on this seed-0-like trajectory."
        )
    else:
        status = "PASS_ROUTER_BRANCH_B_NOT_DOMINANT"
        decision = "The failed trace is not dominated by branch B selection; debug the branch-A policy dynamics or mixed transition instead."
    report = {
        "created_utc": now_utc(),
        "status": status,
        "trace": rel(trace_path),
        "gate_npz": rel(gate_path),
        "threshold": float(args.threshold),
        "direction": args.direction,
        "samples": int(len(rows)),
        "termination_reason": termination,
        "branch_b_pct": branch_b_pct,
        "windows": windows,
        "mean_vx_m_s": float(np.mean(vx)),
        "base_height_min_m": float(np.min(base_height)),
        "body_pitch_abs_p95_rad": percentile(pitch_abs, 95),
        "decision": decision,
        "no_robot_tests": True,
        "no_ssh": True,
        "no_deploy": True,
        "no_grounded_replay": True,
        "runtime_behavior_changed": False,
    }
    output_json = Path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    write_markdown(Path(args.output_md), report)
    print(status)
    print(f"wrote {args.output_md}")
    print(f"wrote {args.output_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
