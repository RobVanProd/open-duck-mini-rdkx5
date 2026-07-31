#!/usr/bin/env python3
"""Analyze push-window contrast traces for Phase 2 recovery design.

This is an offline analysis helper. It reads closed-loop trace JSONL files and
compares observation channels around disturbance windows. It does not train,
deploy, SSH, or touch the robot.
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np


@dataclass(frozen=True)
class TraceSpec:
    label: str
    role: str
    path: Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--trace",
        action="append",
        default=[],
        metavar="LABEL:ROLE:PATH",
        help="Trace spec. ROLE is pass, lunge_fail, or collapse_fail.",
    )
    parser.add_argument("--output-md", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--first-push-pre", type=int, default=20)
    parser.add_argument("--first-push-post", type=int, default=60)
    parser.add_argument("--late-window", type=int, default=80)
    parser.add_argument("--top-k", type=int, default=16)
    return parser.parse_args()


def parse_trace_spec(raw: str) -> TraceSpec:
    parts = raw.split(":", 2)
    if len(parts) != 3:
        raise SystemExit(f"bad --trace spec: {raw!r}")
    label, role, path = parts
    if role not in {"pass", "lunge_fail", "collapse_fail"}:
        raise SystemExit(f"bad trace role {role!r} in {raw!r}")
    trace_path = Path(path)
    if not trace_path.exists():
        raise SystemExit(f"trace does not exist: {trace_path}")
    return TraceSpec(label=label, role=role, path=trace_path)


def load_trace(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    if not rows:
        raise SystemExit(f"empty trace: {path}")
    return rows


def first_push_tick(rows: list[dict[str, Any]]) -> int | None:
    for row in rows:
        if float(row.get("push_magnitude") or 0.0) > 0.0:
            return int(row["tick"])
    return None


def window_rows(
    rows: list[dict[str, Any]], start_tick: int, end_tick: int
) -> list[dict[str, Any]]:
    return [
        row
        for row in rows
        if start_tick <= int(row["tick"]) <= end_tick
    ]


def obs_matrix(rows: list[dict[str, Any]]) -> np.ndarray:
    return np.asarray([row["obs_state"] for row in rows], dtype=np.float64)


def summarize_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {"samples": 0}
    vx = np.asarray([row["local_linvel_m_s"][0] for row in rows], dtype=np.float64)
    pitch = np.asarray([row["body_pitch_rad"] for row in rows], dtype=np.float64)
    height = np.asarray([row["base_height_m"] for row in rows], dtype=np.float64)
    push = np.asarray([row.get("push_magnitude") or 0.0 for row in rows], dtype=np.float64)
    return {
        "samples": len(rows),
        "tick_start": int(rows[0]["tick"]),
        "tick_end": int(rows[-1]["tick"]),
        "mean_vx": float(np.mean(vx)),
        "max_abs_pitch": float(np.max(np.abs(pitch))),
        "min_base_height": float(np.min(height)),
        "push_events": int(np.count_nonzero(push > 0.0)),
    }


def channel_contrast(
    a: np.ndarray, b: np.ndarray, *, top_k: int
) -> list[dict[str, Any]]:
    if a.size == 0 or b.size == 0:
        return []
    mean_a = np.mean(a, axis=0)
    mean_b = np.mean(b, axis=0)
    std_a = np.std(a, axis=0)
    std_b = np.std(b, axis=0)
    pooled = np.sqrt(0.5 * (std_a * std_a + std_b * std_b)) + 1.0e-9
    score = np.abs(mean_a - mean_b) / pooled
    rows = []
    for index in np.argsort(score)[::-1][:top_k]:
        rows.append(
            {
                "obs_index": int(index),
                "score": float(score[index]),
                "mean_a": float(mean_a[index]),
                "mean_b": float(mean_b[index]),
                "diff_a_minus_b": float(mean_a[index] - mean_b[index]),
                "std_a": float(std_a[index]),
                "std_b": float(std_b[index]),
            }
        )
    return rows


def trace_summary(spec: TraceSpec, rows: list[dict[str, Any]]) -> dict[str, Any]:
    push_tick = first_push_tick(rows)
    end = rows[-1]
    return {
        "label": spec.label,
        "role": spec.role,
        "path": str(spec.path),
        "samples": len(rows),
        "first_push_tick": push_tick,
        "last_tick": int(end["tick"]),
        "done": bool(end.get("done")),
        "end_base_height": float(end["base_height_m"]),
        "end_body_pitch": float(end["body_pitch_rad"]),
        "end_local_vx": float(end["local_linvel_m_s"][0]),
    }


def md_table(rows: list[dict[str, Any]], columns: list[str]) -> list[str]:
    out = ["| " + " | ".join(columns) + " |"]
    out.append("|" + "|".join(["---"] * len(columns)) + "|")
    for row in rows:
        values = []
        for col in columns:
            value = row.get(col)
            if isinstance(value, float):
                values.append(f"{value:.4f}")
            else:
                values.append(str(value))
        out.append("| " + " | ".join(values) + " |")
    return out


def main() -> int:
    args = parse_args()
    specs = [parse_trace_spec(raw) for raw in args.trace]
    if len(specs) < 2:
        raise SystemExit("at least two --trace specs are required")

    traces: dict[str, list[dict[str, Any]]] = {}
    summaries = []
    windows: dict[str, dict[str, list[dict[str, Any]]]] = {}
    for spec in specs:
        rows = load_trace(spec.path)
        traces[spec.label] = rows
        summaries.append(trace_summary(spec, rows))
        push_tick = first_push_tick(rows)
        if push_tick is None:
            first = []
        else:
            first = window_rows(
                rows,
                push_tick - args.first_push_pre,
                push_tick + args.first_push_post,
            )
        late = rows[-args.late_window :]
        windows[spec.label] = {
            "first_push": first,
            "late": late,
        }

    pass_specs = [spec for spec in specs if spec.role == "pass"]
    if not pass_specs:
        raise SystemExit("one trace must have role pass")
    pass_label = pass_specs[0].label

    contrast_rows = []
    for spec in specs:
        if spec.label == pass_label:
            continue
        for window_name in ["first_push", "late"]:
            a_rows = windows[spec.label][window_name]
            b_rows = windows[pass_label][window_name]
            contrast_rows.append(
                {
                    "label_a": spec.label,
                    "role_a": spec.role,
                    "label_b": pass_label,
                    "role_b": "pass",
                    "window": window_name,
                    "summary_a": summarize_rows(a_rows),
                    "summary_b": summarize_rows(b_rows),
                    "top_channels": channel_contrast(
                        obs_matrix(a_rows),
                        obs_matrix(b_rows),
                        top_k=int(args.top_k),
                    ),
                }
            )

    obs1_note = []
    for label, label_windows in windows.items():
        for window_name, rows in label_windows.items():
            if not rows:
                continue
            obs = obs_matrix(rows)
            obs1_note.append(
                {
                    "label": label,
                    "window": window_name,
                    "obs1_mean": float(np.mean(obs[:, 1])),
                    "obs1_p95": float(np.percentile(obs[:, 1], 95)),
                    "obs1_max": float(np.max(obs[:, 1])),
                }
            )

    report = {
        "status": "PASS_PUSH_WINDOW_CONTRAST_AUDIT",
        "trace_summaries": summaries,
        "window_config": {
            "first_push_pre": int(args.first_push_pre),
            "first_push_post": int(args.first_push_post),
            "late_window": int(args.late_window),
            "top_k": int(args.top_k),
        },
        "obs1_window_stats": obs1_note,
        "contrasts": contrast_rows,
        "interpretation": (
            "Use this audit to design a multivariate or history-aware recovery "
            "gate. A single obs[1] threshold already failed Iter18."
        ),
    }

    output_json = Path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")

    lines = [
        "# Phase 2 z=0.0075 Push-Window Contrast Audit",
        "",
        "status: `PASS_PUSH_WINDOW_CONTRAST_AUDIT`",
        "",
        "This is offline analysis only. It did not train, deploy, SSH, run robot",
        "tests, grounded replay, or change runtime behavior.",
        "",
        "## Trace Summaries",
        "",
    ]
    lines.extend(
        md_table(
            summaries,
            [
                "label",
                "role",
                "samples",
                "first_push_tick",
                "last_tick",
                "done",
                "end_base_height",
                "end_body_pitch",
                "end_local_vx",
            ],
        )
    )
    lines.extend(["", "## Obs[1] Window Stats", ""])
    lines.extend(
        md_table(
            obs1_note,
            ["label", "window", "obs1_mean", "obs1_p95", "obs1_max"],
        )
    )
    for contrast in contrast_rows:
        lines.extend(
            [
                "",
                f"## Contrast: `{contrast['label_a']}` vs `{contrast['label_b']}`",
                "",
                f"window: `{contrast['window']}`",
                "",
                "summary_a:",
                "",
            ]
        )
        lines.extend(md_table([contrast["summary_a"]], list(contrast["summary_a"].keys())))
        lines.extend(["", "summary_b:", ""])
        lines.extend(md_table([contrast["summary_b"]], list(contrast["summary_b"].keys())))
        lines.extend(["", "top observation channels:", ""])
        lines.extend(
            md_table(
                contrast["top_channels"],
                [
                    "obs_index",
                    "score",
                    "mean_a",
                    "mean_b",
                    "diff_a_minus_b",
                    "std_a",
                    "std_b",
                ],
            )
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- Iter18 showed that a single `obs[1]` threshold is not a sufficient",
            "  deployable recovery gate.",
            "- Use the highest-separation channels here to build a contrastive",
            "  push-window gate that distinguishes seed0 lunge, seed0 pass, and",
            "  seed6 late collapse states before any further candidate promotion.",
        ]
    )
    output_md = Path(args.output_md)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text("\n".join(lines) + "\n")
    print(output_md)
    print(output_json)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
