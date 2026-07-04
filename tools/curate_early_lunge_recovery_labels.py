#!/usr/bin/env python3
"""Curate early-lunge recovery labels from aligned pass/fail traces.

This offline helper keeps observations from a failing rollout and replaces the
selected early-lunge actions with actions from an aligned pass-control rollout.
It emits a compact BC manifest entry that can be merged into existing Phase 2
student manifests. It does not train, deploy, SSH, or touch the robot.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fail-trace", required=True)
    parser.add_argument("--pass-trace", required=True)
    parser.add_argument("--output-trace", required=True)
    parser.add_argument("--output-md", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--indices", required=True, help="comma-separated obs indices")
    parser.add_argument("--centers", required=True, help="comma-separated centers")
    parser.add_argument("--weights", required=True, help="comma-separated weights")
    parser.add_argument("--threshold", type=float, default=5.0)
    parser.add_argument("--tick-start", type=int, default=0)
    parser.add_argument("--tick-end", type=int, default=140)
    parser.add_argument("--sample-weight", type=float, default=8.0)
    parser.add_argument("--mode", default="iter21_early_lunge_gain095_relabel")
    parser.add_argument("--source-name", default=None)
    parser.add_argument("--dt-s", type=float, default=0.02)
    return parser.parse_args()


def parse_int_vector(text: str) -> np.ndarray:
    values = [int(part.strip()) for part in text.split(",") if part.strip()]
    if not values:
        raise SystemExit("empty integer vector")
    return np.asarray(values, dtype=np.int64)


def parse_float_vector(text: str) -> np.ndarray:
    values = [float(part.strip()) for part in text.split(",") if part.strip()]
    if not values:
        raise SystemExit("empty float vector")
    return np.asarray(values, dtype=np.float64)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")


def score_obs(obs: list[float], indices: np.ndarray, centers: np.ndarray, weights: np.ndarray) -> float:
    values = np.asarray([obs[int(index)] for index in indices], dtype=np.float64)
    return float(np.sum((values - centers) * weights))


def trace_by_tick(rows: list[dict[str, Any]]) -> dict[int, dict[str, Any]]:
    return {int(row["tick"]): row for row in rows}


def pct(values: list[float], percentile: float) -> float | None:
    if not values:
        return None
    return float(np.percentile(np.asarray(values, dtype=float), percentile))


def target_velocity_p95(rows: list[dict[str, Any]], *, dt_s: float) -> float | None:
    targets = []
    for row in rows:
        value = row.get("sent_target_rad")
        if isinstance(value, list) and len(value) == 14:
            targets.append(np.asarray(value, dtype=np.float64))
    if len(targets) < 2:
        return None
    stacked = np.stack(targets, axis=0)
    velocity = np.abs(np.diff(stacked, axis=0)) / max(float(dt_s), 1.0e-9)
    return float(np.percentile(velocity.reshape(-1), 95))


def tracking_p95(rows: list[dict[str, Any]]) -> float | None:
    errors: list[float] = []
    for row in rows:
        sent = row.get("sent_target_rad")
        actual = row.get("actual_position_rad")
        if isinstance(sent, list) and isinstance(actual, list) and len(sent) == len(actual) == 14:
            errors.extend(np.abs(np.asarray(sent, dtype=float) - np.asarray(actual, dtype=float)).tolist())
    return pct(errors, 95)


def digest_rows(rows: list[dict[str, Any]]) -> str:
    payload = [
        {
            "tick": row.get("tick"),
            "action": row.get("action"),
            "mode": row.get("mode"),
            "sample_weight": row.get("sample_weight"),
        }
        for row in rows
    ]
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()[:16]


def summarize_entry(
    rows: list[dict[str, Any]],
    *,
    source_path: Path,
    mode: str,
    source_name: str,
    dt_s: float,
) -> dict[str, Any]:
    vx = [float(row["local_linvel_m_s"][0]) for row in rows if row.get("local_linvel_m_s")]
    vy = [abs(float(row["local_linvel_m_s"][1])) for row in rows if row.get("local_linvel_m_s")]
    pitch = [abs(float(row["body_pitch_rad"])) for row in rows if row.get("body_pitch_rad") is not None]
    height = [float(row["base_height_m"]) for row in rows if row.get("base_height_m") is not None]
    contacts: dict[str, int] = {}
    for row in rows:
        value = row.get("foot_contacts")
        if isinstance(value, list) and len(value) == 2:
            key = f"{int(value[0])}{int(value[1])}"
            contacts[key] = contacts.get(key, 0) + 1
    total_contacts = max(sum(contacts.values()), 1)
    contact_pct = {key: 100.0 * count / total_contacts for key, count in sorted(contacts.items())}
    return {
        "entry_id": hashlib.sha256(
            json.dumps(
                {
                    "source_path": str(source_path),
                    "mode": mode,
                    "start_tick": int(rows[0]["tick"]),
                    "end_tick": int(rows[-1]["tick"]),
                },
                sort_keys=True,
            ).encode()
        ).hexdigest()[:16],
        "source_path": str(source_path),
        "source_name": source_name,
        "mode": mode,
        "start_tick": int(rows[0]["tick"]),
        "end_tick": int(rows[-1]["tick"]),
        "raw_trace_exists": True,
        "bc_ready": True,
        "obs_state_dim_ok": True,
        "action_dim_ok": True,
        "done_inside_window": any(bool(row.get("done")) for row in rows[:-1]),
        "samples": len(rows),
        "mean_vx_m_s": float(np.mean(vx)) if vx else None,
        "vy_abs_p95_m_s": pct(vy, 95),
        "body_pitch_abs_p95_rad": pct(pitch, 95),
        "base_height_min_m": min(height) if height else None,
        "sent_target_velocity_p95_rad_s": target_velocity_p95(rows, dt_s=dt_s),
        "joint_tracking_p95_rad": tracking_p95(rows),
        "contact_pct": contact_pct,
    }


def render_md(payload: dict[str, Any]) -> str:
    lines = [
        "# Phase 2 Early-Lunge Recovery Labels",
        "",
        f"status: `{payload['status']}`",
        "",
        "Offline-only curation. Failing rollout observations are preserved and",
        "selected actions are replaced with aligned pass-control actions. No",
        "training, deployment, SSH, robot test, or runtime change was performed.",
        "",
        "## Inputs",
        "",
        f"- fail_trace: `{payload['fail_trace']}`",
        f"- pass_trace: `{payload['pass_trace']}`",
        f"- output_trace: `{payload['output_trace']}`",
        "",
        "## Gate",
        "",
        f"- indices: `{payload['score']['indices']}`",
        f"- threshold: `{payload['score']['threshold']}`",
        f"- tick_window: `{payload['selection']['tick_start']}-{payload['selection']['tick_end']}`",
        "",
        "## Summary",
        "",
        f"- selected_samples: `{payload['summary']['selected_samples']}`",
        f"- dataset_id: `{payload['dataset_id']}`",
        f"- score_p50: `{payload['summary']['score_p50']}`",
        f"- score_p95: `{payload['summary']['score_p95']}`",
        f"- action_delta_p95: `{payload['summary']['action_delta_p95']}`",
        "",
        "## Manifest Entry",
        "",
        "| source | ticks | samples | mode | mean_vx | pitch_p95 | base_min |",
        "|---|---:|---:|---|---:|---:|---:|",
    ]
    entry = payload["manifest"]["entries"][0] if payload["manifest"]["entries"] else None
    if entry:
        lines.append(
            "| {source} | {start}-{end} | {samples} | `{mode}` | {vx:.4f} | {pitch:.4f} | {height:.4f} |".format(
                source=entry["source_name"],
                start=entry["start_tick"],
                end=entry["end_tick"],
                samples=entry["samples"],
                mode=entry["mode"],
                vx=float(entry["mean_vx_m_s"] or 0.0),
                pitch=float(entry["body_pitch_abs_p95_rad"] or 0.0),
                height=float(entry["base_height_min_m"] or 0.0),
            )
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- This artifact is a data input for the next BC student only.",
            "- It is not a candidate policy and is not promotable by itself.",
            "- Gate seeds 0, 2, and 6 before any full promotion test.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    fail_trace = Path(args.fail_trace)
    pass_trace = Path(args.pass_trace)
    output_trace = Path(args.output_trace)
    indices = parse_int_vector(args.indices)
    centers = parse_float_vector(args.centers)
    weights = parse_float_vector(args.weights)
    if not (len(indices) == len(centers) == len(weights)):
        raise SystemExit("--indices, --centers, and --weights must have equal length")

    fail_rows = read_jsonl(fail_trace)
    pass_by_tick = trace_by_tick(read_jsonl(pass_trace))
    selected_rows: list[dict[str, Any]] = []
    scores: list[float] = []
    deltas: list[float] = []
    missing_pass_ticks = 0
    for row in fail_rows:
        tick = int(row["tick"])
        if tick < int(args.tick_start) or tick > int(args.tick_end):
            continue
        obs = row.get("obs_state")
        action = row.get("action")
        pass_row = pass_by_tick.get(tick)
        if obs is None or len(obs) != 101 or action is None or len(action) != 14:
            continue
        if pass_row is None or not isinstance(pass_row.get("action"), list) or len(pass_row["action"]) != 14:
            missing_pass_ticks += 1
            continue
        score = score_obs(obs, indices, centers, weights)
        if score < float(args.threshold):
            continue
        pass_action = np.asarray(pass_row["action"], dtype=np.float64)
        original = np.asarray(action, dtype=np.float64)
        copied = dict(row)
        copied["original_action"] = row.get("original_action", row.get("action"))
        copied["pre_recovery_action"] = row.get("action")
        copied["action"] = pass_action.astype(float).tolist()
        copied["recovery_teacher_trace"] = str(pass_trace)
        copied["recovery_teacher_tick"] = tick
        copied["early_lunge_score"] = score
        copied["sample_weight"] = float(args.sample_weight)
        copied["sample_weight_reasons"] = sorted(
            set([*copied.get("sample_weight_reasons", []), "early_lunge_gain095_recovery"])
        )
        copied["mode"] = str(args.mode)
        selected_rows.append(copied)
        scores.append(score)
        deltas.extend(np.abs(pass_action - original).reshape(-1).tolist())

    if not selected_rows:
        status = "HOLD_EARLY_LUNGE_RECOVERY_LABELS_EMPTY"
        manifest = {"status": status, "dataset_id": None, "entries": []}
        dataset_id = None
    else:
        write_jsonl(output_trace, selected_rows)
        dataset_id = digest_rows(selected_rows)
        source_name = args.source_name or str(output_trace)
        entry = summarize_entry(
            selected_rows,
            source_path=output_trace,
            mode=str(args.mode),
            source_name=source_name,
            dt_s=float(args.dt_s),
        )
        manifest = {
            "status": "PASS_EARLY_LUNGE_RECOVERY_LABELS_READY",
            "dataset_id": dataset_id,
            "input_traces": {
                "fail_trace": str(fail_trace),
                "pass_trace": str(pass_trace),
            },
            "summary": {
                "entries": 1,
                "samples": len(selected_rows),
            },
            "entries": [entry],
        }
        status = manifest["status"]

    payload = {
        "status": status,
        "dataset_id": dataset_id,
        "fail_trace": str(fail_trace),
        "pass_trace": str(pass_trace),
        "output_trace": str(output_trace),
        "score": {
            "indices": [int(value) for value in indices.tolist()],
            "centers": [float(value) for value in centers.tolist()],
            "weights": [float(value) for value in weights.tolist()],
            "threshold": float(args.threshold),
        },
        "selection": {
            "tick_start": int(args.tick_start),
            "tick_end": int(args.tick_end),
            "sample_weight": float(args.sample_weight),
            "missing_pass_ticks": int(missing_pass_ticks),
        },
        "summary": {
            "selected_samples": len(selected_rows),
            "score_p50": pct(scores, 50),
            "score_p95": pct(scores, 95),
            "action_delta_p50": pct(deltas, 50),
            "action_delta_p95": pct(deltas, 95),
            "action_delta_max": max(deltas) if deltas else None,
        },
        "manifest": manifest,
    }
    output_json = Path(args.output_json)
    output_md = Path(args.output_md)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    output_md.write_text(render_md(payload), encoding="utf-8")
    print(f"status={status}")
    print(f"selected_samples={len(selected_rows)}")
    print(f"wrote {output_md}")
    print(f"wrote {output_json}")
    return 0 if selected_rows else 1


if __name__ == "__main__":
    raise SystemExit(main())
