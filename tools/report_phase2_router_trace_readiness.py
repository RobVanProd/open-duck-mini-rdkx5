#!/usr/bin/env python3
"""Report trace-data readiness for the Phase 2 router/mixture diagnostic.

This is offline/read-only. It does not train, SSH, deploy, run robot tests, or
change runtime behavior. It verifies that candidate rollouts needed for an
observation/history router contain JSONL traces with full `obs_state` rows.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_MD = ROOT / "outputs/analysis/PHASE2_ROUTER_TRACE_READINESS.md"
DEFAULT_OUTPUT_JSON = ROOT / "outputs/analysis/phase2_router_trace_readiness.json"

DEFAULT_TRACE_SOURCES = {
    "iter24_iter27": ROOT / "outputs/analysis/phase2_policy_route_trace_iter24_27",
    "iter25_iter26": ROOT / "outputs/analysis/phase2_policy_route_trace_iter25_26",
}


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


def sha256(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_seed(path: Path) -> int | None:
    for part in reversed(path.parts):
        if part.startswith("seed_"):
            try:
                return int(part.split("_", 1)[1])
            except ValueError:
                return None
    return None


def parse_policy_label(source_label: str, root: Path, path: Path) -> str:
    try:
        relative = path.relative_to(root)
    except ValueError:
        return source_label
    first = relative.parts[0] if relative.parts else source_label
    if first.startswith("seed_"):
        return source_label
    return first


def inspect_trace(path: Path, max_scan_rows: int | None) -> dict[str, Any]:
    rows = 0
    obs_rows = 0
    action_rows = 0
    first_tick = None
    last_tick = None
    malformed = 0
    with path.open() as handle:
        for line in handle:
            rows += 1
            if max_scan_rows is not None and rows > max_scan_rows:
                break
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                malformed += 1
                continue
            if first_tick is None:
                first_tick = record.get("tick", record.get("sample"))
            last_tick = record.get("tick", record.get("sample", rows - 1))
            obs = record.get("obs_state")
            action = record.get("action")
            if isinstance(obs, list) and len(obs) == 101:
                obs_rows += 1
            if isinstance(action, list) and len(action) == 14:
                action_rows += 1
    if max_scan_rows is not None:
        # Count exact rows cheaply after validating the prefix.
        with path.open() as handle:
            rows = sum(1 for _ in handle)
    return {
        "path": rel(path),
        "exists": path.exists(),
        "size_bytes": path.stat().st_size if path.exists() else None,
        "sha256": sha256(path),
        "seed": parse_seed(path),
        "rows": rows,
        "obs_state_rows_scanned": obs_rows,
        "action_rows_scanned": action_rows,
        "first_tick": first_tick,
        "last_tick_scanned": last_tick,
        "malformed_rows_scanned": malformed,
        "has_full_obs_state": obs_rows > 0 and malformed == 0,
    }


def inspect_source(label: str, root: Path, max_scan_rows: int | None) -> dict[str, Any]:
    traces = sorted(root.glob("**/trace.jsonl")) if root.exists() else []
    trace_rows = []
    for trace in traces:
        row = inspect_trace(trace, max_scan_rows)
        row["policy_label"] = parse_policy_label(label, root, trace)
        trace_rows.append(row)
    seeds = sorted({row["seed"] for row in trace_rows if row["seed"] is not None})
    return {
        "label": label,
        "root": rel(root),
        "exists": root.exists(),
        "trace_count": len(trace_rows),
        "seeds": seeds,
        "total_size_bytes": sum(row.get("size_bytes") or 0 for row in trace_rows),
        "all_have_full_obs_state": bool(trace_rows) and all(row["has_full_obs_state"] for row in trace_rows),
        "traces": trace_rows,
    }


def decide(sources: list[dict[str, Any]], required_seeds: list[int]) -> tuple[str, str, list[str]]:
    all_rows = [row for source in sources for row in source["traces"]]
    labels = {row["policy_label"] for row in all_rows}
    seeds_by_label = {
        label: sorted({row["seed"] for row in all_rows if row["policy_label"] == label and row["seed"] is not None})
        for label in labels
    }
    has_iter24 = "iter24" in labels
    has_iter25 = "iter25" in labels
    has_iter26 = "iter26" in labels
    has_iter27 = "iter27" in labels
    full_obs_ok = all(row["has_full_obs_state"] for row in all_rows) and bool(all_rows)
    required_present = all(set(required_seeds).issubset(set(seeds)) for seeds in seeds_by_label.values())

    if has_iter24 and has_iter25 and has_iter26 and has_iter27 and full_obs_ok and required_present:
        return (
            "PASS_ROUTER_TRACE_DATA_READY",
            "Full-observation traces are present for Iter24, Iter25, Iter26, and Iter27 across the compact z=0.0075 seed set. The observation-based router diagnostic can be built from current local data.",
            [
                "Train/test only offline router diagnostics from these traces.",
                "Do not use seed id as a deployable routing feature.",
                "Gate any router on the canonical z=0.0075 rough+push compact screen before generating trainable behavior-preservation data.",
            ],
        )

    missing = []
    if not has_iter24:
        missing.append("iter24 traces")
    if not has_iter25:
        missing.append("iter25 traces")
    if not has_iter26:
        missing.append("iter26 traces")
    if not has_iter27:
        missing.append("iter27 traces")
    if not full_obs_ok:
        missing.append("full obs_state coverage")
    if not required_present:
        missing.append("all required seeds per policy")
    return (
        "HOLD_ROUTER_TRACE_DATA_INCOMPLETE",
        "Router trace data is incomplete: " + ", ".join(missing),
        ["Collect missing full-observation traces before training or testing an observation-based router."],
    )


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    lines = [
        "# Phase 2 Router Trace Readiness",
        "",
        f"status: `{payload['status']}`",
        "",
        "## Executive Summary",
        "",
        payload["summary"],
        "",
        "This is offline/read-only. It did not train, SSH, deploy, run robot tests, "
        "change runtime behavior, or run grounded replay.",
        "",
        "## Sources",
        "",
        "| source | exists | trace count | seeds | total size | full obs |",
        "|---|---|---:|---|---:|---|",
    ]
    for source in payload["sources"]:
        lines.append(
            f"| `{source['label']}` | `{source['exists']}` | `{source['trace_count']}` | "
            f"`{source['seeds']}` | `{source['total_size_bytes']}` | "
            f"`{source['all_have_full_obs_state']}` |"
        )
    lines.extend(
        [
            "",
            "## Trace Files",
            "",
            "| policy | seed | rows | obs rows scanned | size | sha256 |",
            "|---|---:|---:|---:|---:|---|",
        ]
    )
    for source in payload["sources"]:
        for row in source["traces"]:
            lines.append(
                f"| `{row['policy_label']}` | `{row['seed']}` | `{row['rows']}` | "
                f"`{row['obs_state_rows_scanned']}` | `{row['size_bytes']}` | "
                f"`{row['sha256']}` |"
            )
    lines.extend(["", "## Next", ""])
    for item in payload["next_required"]:
        lines.append(f"- {item}")
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines))


def parse_seed_list(text: str) -> list[int]:
    return [int(part.strip()) for part in text.split(",") if part.strip()]


def parse_source_items(items: list[str] | None) -> dict[str, Path]:
    if not items:
        return DEFAULT_TRACE_SOURCES
    out: dict[str, Path] = {}
    for item in items:
        if "=" not in item:
            raise argparse.ArgumentTypeError("--source must be label=path")
        label, path = item.split("=", 1)
        out[label] = Path(path)
    return out


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", action="append", help="Trace source as label=path")
    parser.add_argument("--required-seeds", default="0,1,2,6,7")
    parser.add_argument(
        "--max-scan-rows",
        type=int,
        default=25,
        help="Rows per trace to parse for obs/action validation; exact row count is still computed.",
    )
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    sources = [
        inspect_source(label, path, args.max_scan_rows)
        for label, path in parse_source_items(args.source).items()
    ]
    status, summary, next_required = decide(sources, parse_seed_list(args.required_seeds))
    payload = {
        "generated_at": now_utc(),
        "scope": "offline_phase2_router_trace_readiness",
        "status": status,
        "summary": summary,
        "required_seeds": parse_seed_list(args.required_seeds),
        "sources": sources,
        "next_required": next_required,
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    write_markdown(payload, args.output_md)
    print(status)
    print(rel(args.output_md))
    print(rel(args.output_json))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
