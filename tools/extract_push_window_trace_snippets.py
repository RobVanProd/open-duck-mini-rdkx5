#!/usr/bin/env python3
"""Extract compact push-window snippets from traced candidate failures.

This is an offline data-curation helper. It reads a seed-sweep JSON plus the
per-seed trace directories written by ``run_candidate_seed_sweep.py`` and emits
short JSONL snippets around unrecovered push events. It does not train, deploy,
SSH, touch the robot, or modify Playground.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def fmt(value: Any, digits: int = 4) -> str:
    if value is None:
        return "NA"
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def event_end(event: dict[str, Any]) -> int:
    tick = int(event.get("tick") or 0)
    samples = int(event.get("window_samples") or 1)
    return tick + max(0, samples - 1)


def event_selected(event: dict[str, Any], *, include_recovered: bool) -> bool:
    if include_recovered:
        return True
    return (not bool(event.get("recovered"))) or bool(event.get("terminated_in_window"))


def snippet_id(seed: int, event_index: int, start_tick: int, end_tick: int) -> str:
    payload = {
        "seed": int(seed),
        "event_index": int(event_index),
        "start_tick": int(start_tick),
        "end_tick": int(end_tick),
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()[:16]


def extract_for_seed(
    result: dict[str, Any],
    args: argparse.Namespace,
) -> list[dict[str, Any]]:
    seed = int(result["seed"])
    if args.failed_only and result.get("status") == "PASS_CANDIDATE_SIM_GATE":
        return []
    output_dir = Path(result["output_dir"])
    if not output_dir.is_absolute():
        output_dir = ROOT / output_dir
    trace_path = output_dir / "trace.jsonl"
    eval_path = output_dir / "closed_loop_actuator_bridge_eval.json"
    if not trace_path.exists() or not eval_path.exists():
        return []
    rows = read_jsonl(trace_path)
    eval_payload = load_json(eval_path)
    mode = eval_payload.get("closed_loop_sim", {}).get("modes", {}).get("fitted", {})
    events = mode.get("push_recovery", {}).get("events", []) or []
    selected: list[dict[str, Any]] = []
    for event_index, event in enumerate(events):
        if not event_selected(event, include_recovered=args.include_recovered):
            continue
        push_tick = int(event.get("tick") or 0)
        start_tick = max(0, push_tick - int(args.pre_ticks))
        end_tick = min(len(rows) - 1, event_end(event) + int(args.post_ticks))
        snippet_rows = []
        for row in rows[start_tick : end_tick + 1]:
            if args.truncate_done and bool(row.get("done")):
                break
            copied = dict(row)
            copied["mode"] = str(args.output_mode)
            copied["source_failure_seed"] = seed
            copied["source_push_event_index"] = event_index
            copied["source_push_tick"] = push_tick
            copied["source_push_recovered"] = bool(event.get("recovered"))
            copied["source_push_terminated_in_window"] = bool(event.get("terminated_in_window"))
            copied["sample_weight"] = float(args.sample_weight)
            reasons = list(copied.get("sample_weight_reasons") or [])
            reasons.append("push_window_recovery")
            if not bool(event.get("recovered")):
                reasons.append("unrecovered_push")
            copied["sample_weight_reasons"] = sorted(set(reasons))
            snippet_rows.append(copied)
        if not snippet_rows:
            continue
        sid = snippet_id(seed, event_index, start_tick, end_tick)
        output_path = Path(args.output_trace_dir) / f"seed_{seed:03d}" / f"push_{event_index:03d}_{sid}.jsonl"
        write_jsonl(output_path, snippet_rows)
        selected.append(
            {
                "seed": seed,
                "event_index": event_index,
                "source_trace": rel(trace_path),
                "output_trace": rel(output_path),
                "samples": len(snippet_rows),
                "push_tick": push_tick,
                "start_tick": int(snippet_rows[0].get("tick", start_tick)),
                "end_tick": int(snippet_rows[-1].get("tick", end_tick)),
                "push": event.get("push"),
                "push_magnitude": event.get("push_magnitude"),
                "window_samples": event.get("window_samples"),
                "recovered": bool(event.get("recovered")),
                "terminated_in_window": bool(event.get("terminated_in_window")),
                "max_abs_pitch_rad": event.get("max_abs_pitch_rad"),
                "min_base_height_m": event.get("min_base_height_m"),
            }
        )
    return selected


def render_md(payload: dict[str, Any]) -> str:
    lines = [
        "# Push-Window Trace Snippets",
        "",
        f"status: `{payload['status']}`",
        "",
        "This is an offline trace-curation artifact. It does not train, deploy, SSH, run robot tests, or change runtime behavior.",
        "",
        "## Inputs",
        "",
        f"- sweep_json: `{payload['sweep_json']}`",
        f"- output_trace_dir: `{payload['output_trace_dir']}`",
        f"- failed_only: `{payload['failed_only']}`",
        f"- include_recovered: `{payload['include_recovered']}`",
        f"- pre_ticks: `{payload['pre_ticks']}`",
        f"- post_ticks: `{payload['post_ticks']}`",
        f"- truncate_done: `{payload['truncate_done']}`",
        f"- sample_weight: `{payload['sample_weight']}`",
        "",
        "## Summary",
        "",
        f"- snippets: `{payload['summary']['snippets']}`",
        f"- samples: `{payload['summary']['samples']}`",
        "",
        "| seed | event | ticks | samples | recovered | terminated | push | pitch max | height min | output |",
        "|---:|---:|---:|---:|---|---|---:|---:|---:|---|",
    ]
    for item in payload["snippets"]:
        lines.append(
            "| {seed} | {event} | {ticks} | {samples} | `{recovered}` | `{terminated}` | {push} | {pitch} | {height} | `{output}` |".format(
                seed=item["seed"],
                event=item["event_index"],
                ticks=f"{item['start_tick']}-{item['end_tick']}",
                samples=item["samples"],
                recovered=item["recovered"],
                terminated=item["terminated_in_window"],
                push=fmt(item.get("push_magnitude")),
                pitch=fmt(item.get("max_abs_pitch_rad")),
                height=fmt(item.get("min_base_height_m")),
                output=item["output_trace"],
            )
        )
    lines.extend(
        [
            "",
            "## Gate",
            "",
            "- These snippets are local data for offline relabeling or supervised recovery checks.",
            "- They are not a candidate policy and do not prove deployability.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sweep-json", required=True)
    parser.add_argument("--output-trace-dir", required=True)
    parser.add_argument("--output-md", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--pre-ticks", type=int, default=8)
    parser.add_argument("--post-ticks", type=int, default=8)
    parser.add_argument("--sample-weight", type=float, default=4.0)
    parser.add_argument("--output-mode", default="phase2_push_window_recovery")
    parser.add_argument("--failed-only", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--include-recovered", action="store_true")
    parser.add_argument("--truncate-done", action=argparse.BooleanOptionalAction, default=True)
    args = parser.parse_args()

    sweep_json = Path(args.sweep_json)
    sweep = load_json(sweep_json)
    snippets: list[dict[str, Any]] = []
    for result in sweep.get("results", []):
        snippets.extend(extract_for_seed(result, args))
    status = "PASS_PUSH_WINDOW_SNIPPETS_READY" if snippets else "HOLD_PUSH_WINDOW_SNIPPETS_EMPTY"
    payload = {
        "status": status,
        "sweep_json": rel(sweep_json),
        "output_trace_dir": rel(Path(args.output_trace_dir)),
        "failed_only": bool(args.failed_only),
        "include_recovered": bool(args.include_recovered),
        "pre_ticks": int(args.pre_ticks),
        "post_ticks": int(args.post_ticks),
        "truncate_done": bool(args.truncate_done),
        "sample_weight": float(args.sample_weight),
        "output_mode": args.output_mode,
        "summary": {
            "snippets": len(snippets),
            "samples": int(sum(item["samples"] for item in snippets)),
        },
        "snippets": snippets,
        "scope": {
            "robot_tests": False,
            "ssh": False,
            "deploy": False,
            "training": False,
            "runtime_behavior_changes": False,
        },
    }
    out_json = Path(args.output_json)
    out_md = Path(args.output_md)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(render_md(payload))
    print(status)
    print(f"snippets={len(snippets)}")
    print(f"samples={payload['summary']['samples']}")
    print(f"wrote {out_md}")
    print(f"wrote {out_json}")
    return 0 if status.startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
