#!/usr/bin/env python3
"""Analyze a failing warm-start trace against a BC manifest.

This offline tool helps decide whether a failing seed is out-of-distribution,
has a bad local action fit, or fails despite nearby teacher coverage.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np


def percentile(values: np.ndarray, q: float) -> float | None:
    arr = np.asarray(values, dtype=float).reshape(-1)
    arr = arr[np.isfinite(arr)]
    if arr.size == 0:
        return None
    return float(np.percentile(arr, q))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records = []
    with path.open() as handle:
        for line in handle:
            if line.strip():
                records.append(json.loads(line))
    if not records:
        raise ValueError(f"empty trace {path}")
    return records


def load_manifest_samples(manifest_path: Path) -> tuple[np.ndarray, np.ndarray, list[str]]:
    manifest = json.loads(manifest_path.read_text())
    obs_rows: list[list[float]] = []
    action_rows: list[list[float]] = []
    sources: list[str] = []
    for entry in manifest.get("entries", []):
        if not entry.get("bc_ready", False):
            continue
        source = Path(entry["source_path"])
        if not source.exists():
            continue
        with source.open() as handle:
            for line in handle:
                record = json.loads(line)
                obs = record.get("obs_state")
                action = record.get("action")
                if obs is None or action is None:
                    continue
                obs_arr = np.asarray(obs, dtype=np.float64).reshape(-1)
                action_arr = np.asarray(action, dtype=np.float64).reshape(-1)
                if obs_arr.shape != (101,) or action_arr.shape != (14,):
                    continue
                obs_rows.append(obs_arr.astype(float).tolist())
                action_rows.append(action_arr.astype(float).tolist())
                sources.append(entry.get("source_name") or str(source))
    if not obs_rows:
        raise ValueError(f"no manifest samples found in {manifest_path}")
    return np.asarray(obs_rows), np.asarray(action_rows), sources


def contact_key(values: Any) -> str:
    if not isinstance(values, list) or len(values) != 2:
        return "NA"
    return f"{int(values[0])}{int(values[1])}"


def summarize_trace(records: list[dict[str, Any]], dt_s: float) -> dict[str, Any]:
    vx = np.asarray([rec.get("local_linvel_m_s", [np.nan])[0] for rec in records], dtype=float)
    vy = np.asarray([rec.get("local_linvel_m_s", [np.nan, np.nan])[1] for rec in records], dtype=float)
    height = np.asarray([rec.get("base_height_m", np.nan) for rec in records], dtype=float)
    pitch = np.asarray([rec.get("body_pitch_rad", np.nan) for rec in records], dtype=float)
    action = np.asarray([rec.get("action", [np.nan] * 14) for rec in records], dtype=float)
    target = np.asarray([rec.get("sent_target_rad", [np.nan] * 14) for rec in records], dtype=float)
    actual = np.asarray([rec.get("actual_position_rad", [np.nan] * 14) for rec in records], dtype=float)
    target_rate = np.abs(np.diff(target, axis=0)) / max(dt_s, 1.0e-9) if len(records) > 1 else np.zeros((0, 14))
    tracking = np.abs(target - actual)
    contact_counts: dict[str, int] = {}
    for rec in records:
        key = contact_key(rec.get("foot_contacts"))
        contact_counts[key] = contact_counts.get(key, 0) + 1
    first_negative_vx = next((int(i) for i, value in enumerate(vx) if np.isfinite(value) and value < 0.0), None)
    first_height_below_10cm = next((int(i) for i, value in enumerate(height) if np.isfinite(value) and value < 0.10), None)
    done_tick = next((int(i) for i, rec in enumerate(records) if rec.get("done")), None)
    return {
        "samples": int(len(records)),
        "termination_tick": done_tick,
        "first_negative_vx_tick": first_negative_vx,
        "first_height_below_10cm_tick": first_height_below_10cm,
        "mean_vx_m_s": float(np.nanmean(vx)),
        "min_vx_m_s": float(np.nanmin(vx)),
        "p95_abs_vy_m_s": percentile(np.abs(vy), 95),
        "base_height_min_m": float(np.nanmin(height)),
        "base_height_final_m": float(height[-1]),
        "body_pitch_abs_p95_rad": percentile(np.abs(pitch), 95),
        "body_pitch_final_rad": float(pitch[-1]),
        "action_delta_p95_per_s": percentile(np.abs(np.diff(action, axis=0)) / max(dt_s, 1.0e-9), 95)
        if len(records) > 1
        else None,
        "sent_target_velocity_p95_rad_s": percentile(target_rate, 95),
        "sent_target_velocity_max_rad_s": float(np.nanmax(target_rate)) if target_rate.size else None,
        "joint_tracking_p95_rad": percentile(tracking, 95),
        "joint_tracking_max_rad": float(np.nanmax(tracking)) if tracking.size else None,
        "contact_pct": {
            key: float(count / max(len(records), 1) * 100.0)
            for key, count in sorted(contact_counts.items())
        },
        "last_10": [
            {
                "tick": int(rec.get("tick", i)),
                "vx": float(vx[i]),
                "vy": float(vy[i]),
                "height": float(height[i]),
                "pitch": float(pitch[i]),
                "contacts": contact_key(rec.get("foot_contacts")),
            }
            for i, rec in list(enumerate(records))[-10:]
        ],
    }


def nearest_coverage(
    trace_records: list[dict[str, Any]],
    manifest_obs: np.ndarray,
    manifest_actions: np.ndarray,
    sources: list[str],
    bc_norm: np.ndarray,
    top_k: int,
) -> dict[str, Any]:
    trace_obs_rows = []
    missing_obs = 0
    for rec in trace_records:
        obs = rec.get("obs_state")
        if obs is None:
            missing_obs += 1
            obs = [np.nan] * 101
        trace_obs_rows.append(obs)
    trace_obs = np.asarray(trace_obs_rows, dtype=float)
    trace_action = np.asarray([rec.get("action", [np.nan] * 14) for rec in trace_records], dtype=float)
    if missing_obs or trace_obs.shape[1:] != (101,) or not np.isfinite(trace_obs).all():
        return {
            "available": False,
            "reason": "trace is missing finite obs_state rows",
            "missing_obs_rows": int(missing_obs),
            "trace_rows": int(len(trace_records)),
            "top_k": int(top_k),
            "nearest_distance": {"mean": None, "p50": None, "p95": None, "max": None},
            "nearest_action_l1": {"mean": None, "p50": None, "p95": None, "max": None},
            "top_nearest_sources": [],
        }
    mean, std = bc_norm
    train_norm = (manifest_obs - mean) / std
    trace_norm = (trace_obs - mean) / std
    nearest_dist = []
    nearest_action_l1 = []
    nearest_sources = []
    for obs_row, action_row in zip(trace_norm, trace_action, strict=True):
        diff = train_norm - obs_row
        dist = np.sqrt(np.mean(diff * diff, axis=1))
        order = np.argsort(dist)[: max(1, top_k)]
        nearest_dist.append(float(dist[order[0]]))
        nearest_action = np.mean(manifest_actions[order], axis=0)
        nearest_action_l1.append(float(np.mean(np.abs(action_row - nearest_action))))
        nearest_sources.append(sources[int(order[0])])
    source_counts: dict[str, int] = {}
    for source in nearest_sources:
        source_counts[source] = source_counts.get(source, 0) + 1
    top_sources = sorted(source_counts.items(), key=lambda item: item[1], reverse=True)[:8]
    return {
        "available": True,
        "reason": None,
        "missing_obs_rows": 0,
        "trace_rows": int(len(trace_records)),
        "top_k": int(top_k),
        "nearest_distance": {
            "mean": float(np.mean(nearest_dist)),
            "p50": percentile(np.asarray(nearest_dist), 50),
            "p95": percentile(np.asarray(nearest_dist), 95),
            "max": float(np.max(nearest_dist)),
        },
        "nearest_action_l1": {
            "mean": float(np.mean(nearest_action_l1)),
            "p50": percentile(np.asarray(nearest_action_l1), 50),
            "p95": percentile(np.asarray(nearest_action_l1), 95),
            "max": float(np.max(nearest_action_l1)),
        },
        "top_nearest_sources": [
            {"source": source, "count": int(count), "pct": float(count / max(len(nearest_sources), 1) * 100.0)}
            for source, count in top_sources
        ],
    }


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    trace = report["trace_summary"]
    coverage = report["nearest_coverage"]
    lines = [
        "# Warm-Start Seed Failure Analysis",
        "",
        f"status: `{report['status']}`",
        "",
        "Offline trace analysis only. No PPO updates, robot tests, SSH, deploy, or",
        "runtime changes were performed.",
        "",
        "## Inputs",
        "",
        f"- trace: `{report['trace']}`",
        f"- manifest: `{report['manifest']}`",
        f"- BC NPZ: `{report['bc_npz']}`",
        "",
        "## Trace Summary",
        "",
        f"- samples: `{trace['samples']}`",
        f"- termination tick: `{trace['termination_tick']}`",
        f"- first negative vx tick: `{trace['first_negative_vx_tick']}`",
        f"- first height below 10 cm tick: `{trace['first_height_below_10cm_tick']}`",
        f"- mean vx: `{trace['mean_vx_m_s']:.4f}` m/s",
        f"- min vx: `{trace['min_vx_m_s']:.4f}` m/s",
        f"- base height min: `{trace['base_height_min_m']:.4f}` m",
        f"- target velocity p95: `{trace['sent_target_velocity_p95_rad_s']:.4f}` rad/s",
        f"- joint tracking p95: `{trace['joint_tracking_p95_rad']:.4f}` rad",
        f"- action delta p95: `{trace['action_delta_p95_per_s']:.4f}` /s",
        "",
        "Contact percentage:",
        "",
        "```text",
    ]
    for key, value in trace["contact_pct"].items():
        lines.append(f"{key}: {value:.2f}%")
    lines += [
        "```",
        "",
        "## Nearest Manifest Coverage",
        "",
    ]
    if not coverage.get("available", True):
        lines += [
            f"- status: unavailable",
            f"- reason: `{coverage.get('reason')}`",
            f"- missing obs rows: `{coverage.get('missing_obs_rows')}` / `{coverage.get('trace_rows')}`",
        ]
    else:
        lines += [
            f"- nearest distance mean/p95/max: `{coverage['nearest_distance']['mean']:.4f}` / `{coverage['nearest_distance']['p95']:.4f}` / `{coverage['nearest_distance']['max']:.4f}`",
            f"- nearest action L1 mean/p95/max: `{coverage['nearest_action_l1']['mean']:.4f}` / `{coverage['nearest_action_l1']['p95']:.4f}` / `{coverage['nearest_action_l1']['max']:.4f}`",
            "",
            "| source | count | pct |",
            "|---|---:|---:|",
        ]
        for row in coverage["top_nearest_sources"]:
            lines.append(f"| `{row['source']}` | {row['count']} | {row['pct']:.2f} |")
    lines += [
        "",
        "## Last 10 Samples",
        "",
        "| tick | vx | vy | height | pitch | contacts |",
        "|---:|---:|---:|---:|---:|---|",
    ]
    for row in trace["last_10"]:
        lines.append(
            f"| {row['tick']} | {row['vx']:.4f} | {row['vy']:.4f} | "
            f"{row['height']:.4f} | {row['pitch']:.4f} | `{row['contacts']}` |"
        )
    lines += [
        "",
        "## Decision",
        "",
        report["decision"],
        "",
    ]
    path.write_text("\n".join(lines))


def main() -> int:
    args = parse_args()
    trace_records = load_jsonl(Path(args.trace))
    manifest_obs, manifest_actions, sources = load_manifest_samples(Path(args.manifest))
    bc = np.load(args.bc_npz, allow_pickle=True)
    bc_norm = np.asarray(bc["norm"], dtype=float)
    trace_summary = summarize_trace(trace_records, args.dt_s)
    coverage = nearest_coverage(
        trace_records,
        manifest_obs,
        manifest_actions,
        sources,
        bc_norm,
        args.top_k,
    )
    if not coverage.get("available", True):
        status = "HOLD_TRACE_OBS_MISSING"
        decision = "Trace does not contain finite obs_state rows; rerun the candidate trace with full-observation logging before judging manifest coverage."
    else:
        ood = coverage["nearest_distance"]["p95"] > args.ood_distance_p95
        high_action_gap = coverage["nearest_action_l1"]["p95"] > args.action_l1_p95
        status = (
            "HOLD_SEED_FAILURE_OOD"
            if ood
            else "HOLD_SEED_FAILURE_ACTION_MISMATCH"
            if high_action_gap
            else "HOLD_SEED_FAILURE_CLOSED_LOOP_INSTABILITY"
        )
        decision = (
            "Seed failure appears out-of-distribution against the current manifest; collect or relabel nearby states."
            if ood
            else "Seed failure has nearby states but high action mismatch; improve local BC fit/relabeling."
            if high_action_gap
            else "Seed failure has nearby manifest support and modest action mismatch; investigate closed-loop stability/contact dynamics."
        )
    report = {
        "status": status,
        "trace": args.trace,
        "manifest": args.manifest,
        "bc_npz": args.bc_npz,
        "trace_summary": trace_summary,
        "nearest_coverage": coverage,
        "thresholds": {
            "ood_distance_p95": float(args.ood_distance_p95),
            "action_l1_p95": float(args.action_l1_p95),
        },
        "decision": decision,
    }
    Path(args.output_json).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output_json).write_text(json.dumps(report, indent=2))
    write_markdown(Path(args.output_md), report)
    print(status)
    print(f"wrote {args.output_md}")
    print(f"wrote {args.output_json}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trace", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--bc-npz", required=True)
    parser.add_argument("--dt-s", type=float, default=0.02)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--ood-distance-p95", type=float, default=2.0)
    parser.add_argument("--action-l1-p95", type=float, default=0.12)
    parser.add_argument(
        "--output-md",
        default="outputs/analysis/WARMSTART_SEED_FAILURE_ANALYSIS.md",
    )
    parser.add_argument(
        "--output-json",
        default="outputs/analysis/warmstart_seed_failure_analysis.json",
    )
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(main())
