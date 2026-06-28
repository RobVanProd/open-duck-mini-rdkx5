#!/usr/bin/env python3
"""Apply per-row sample weights to BC JSONL traces.

This is an offline curation helper. It does not train, deploy, SSH, run robot
tests, or change robot runtime behavior. The output traces are intended to stay
ignored and be referenced by compact BC manifests.
"""

from __future__ import annotations

import argparse
from collections import Counter
import glob
import json
from pathlib import Path
from typing import Any


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    for line in path.read_text().splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")


def contact_code(row: dict[str, Any]) -> str:
    contacts = row.get("foot_contacts")
    if isinstance(contacts, list | tuple) and len(contacts) == 2:
        return f"{int(contacts[0])}{int(contacts[1])}"
    return "NA"


def row_matches(row: dict[str, Any], args: argparse.Namespace) -> bool:
    if args.contact_code and contact_code(row) != args.contact_code:
        return False
    if args.min_command_x is not None:
        command = row.get("command")
        if not isinstance(command, list | tuple) or not command:
            return False
        try:
            if float(command[0]) < float(args.min_command_x):
                return False
        except (TypeError, ValueError):
            return False
    return True


def rel_output_path(source: Path, output_dir: Path, parent_depth: int) -> Path:
    parent_parts = list(source.parent.parts[-max(1, parent_depth):])
    return output_dir.joinpath(*parent_parts, source.name)


def process_trace(path: Path, output_dir: Path, args: argparse.Namespace) -> dict[str, Any]:
    rows = read_jsonl(path)
    out_rows: list[dict[str, Any]] = []
    contact_counts: Counter[str] = Counter()
    weight_counts: Counter[str] = Counter()
    matched = 0
    for row in rows:
        code = contact_code(row)
        contact_counts[code] += 1
        copied = dict(row)
        if row_matches(row, args):
            base = float(copied.get("sample_weight", 1.0))
            copied["sample_weight"] = max(base * float(args.match_weight), 0.0)
            copied["sample_weight_reasons"] = sorted(
                set([*copied.get("sample_weight_reasons", []), args.reason])
            )
            matched += 1
            weight_counts[args.reason] += 1
        else:
            copied["sample_weight"] = float(copied.get("sample_weight", 1.0))
            weight_counts["base"] += 1
        out_rows.append(copied)
    output_path = rel_output_path(path, output_dir, int(args.output_parent_depth))
    write_jsonl(output_path, out_rows)
    return {
        "source_trace": str(path),
        "output_trace": str(output_path),
        "samples": len(rows),
        "matched_samples": matched,
        "match_weight": float(args.match_weight),
        "contact_counts": dict(sorted(contact_counts.items())),
        "weight_reasons": dict(sorted(weight_counts.items())),
    }


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Weighted BC Trace Samples",
        "",
        f"status: `{payload['status']}`",
        "",
        "This offline artifact applies per-row sample weights to BC JSONL traces.",
        "It does not copy traces into git by itself, train, deploy, SSH, run robot",
        "tests, or change runtime behavior.",
        "",
        "## Rule",
        "",
        f"- contact_code: `{payload['rule']['contact_code']}`",
        f"- min_command_x: `{payload['rule']['min_command_x']}`",
        f"- match_weight: `{payload['rule']['match_weight']}`",
        f"- reason: `{payload['rule']['reason']}`",
        "",
        "## Traces",
        "",
        "| source | samples | matched | contacts | weight reasons |",
        "|---|---:|---:|---|---|",
    ]
    for item in payload["traces"]:
        lines.append(
            "| {source} | {samples} | {matched} | `{contacts}` | `{reasons}` |".format(
                source=Path(item["source_trace"]).name,
                samples=item["samples"],
                matched=item["matched_samples"],
                contacts=item["contact_counts"],
                reasons=item["weight_reasons"],
            )
        )
    lines.extend(
        [
            "",
            "## Gate",
            "",
            "- Output JSONL traces are generated artifacts and should remain ignored",
            "  unless explicitly approved.",
            "- A weighted trace is not a candidate policy.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trace-glob", action="append", required=True)
    parser.add_argument("--output-trace-dir", required=True)
    parser.add_argument("--output-parent-depth", type=int, default=1)
    parser.add_argument("--contact-code", default=None)
    parser.add_argument("--min-command-x", type=float, default=None)
    parser.add_argument("--match-weight", type=float, required=True)
    parser.add_argument("--reason", default="sample_weight_rule")
    parser.add_argument("--output-md", required=True)
    parser.add_argument("--output-json", required=True)
    args = parser.parse_args()

    paths: list[Path] = []
    for item in args.trace_glob:
        paths.extend(Path(path) for path in sorted(glob.glob(item)))
    paths = sorted(dict.fromkeys(paths))
    output_dir = Path(args.output_trace_dir)
    traces = [process_trace(path, output_dir, args) for path in paths]
    payload = {
        "status": "PASS_WEIGHTED_BC_TRACE_SAMPLES_READY" if traces else "HOLD_NO_TRACES",
        "trace_globs": args.trace_glob,
        "output_trace_dir": str(output_dir),
        "rule": {
            "contact_code": args.contact_code,
            "min_command_x": args.min_command_x,
            "match_weight": float(args.match_weight),
            "reason": args.reason,
        },
        "summary": {
            "traces": len(traces),
            "samples": int(sum(item["samples"] for item in traces)),
            "matched_samples": int(sum(item["matched_samples"] for item in traces)),
        },
        "traces": traces,
    }
    output_json = Path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    output_md = Path(args.output_md)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text(render_markdown(payload))
    print(payload["status"])
    print(f"matched_samples={payload['summary']['matched_samples']}")
    print(f"wrote {output_md}")
    print(f"wrote {output_json}")
    return 0 if payload["status"].startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
