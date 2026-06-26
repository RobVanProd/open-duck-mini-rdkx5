#!/usr/bin/env python3
"""Compare closed-loop stance timing across published-policy command cells.

This offline analyzer reads existing BEST_WALK full-observation traces with
foot-site positions. It summarizes how often the policy enters single support,
where the base sits relative to the stance foot, and whether single-support
ticks are followed by forward velocity gain.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import glob
import json
import math
from pathlib import Path
from statistics import mean, pstdev
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def finite(value: Any) -> bool:
    return isinstance(value, (int, float)) and math.isfinite(float(value))


def fmt(value: Any, digits: int = 4) -> str:
    if value is None:
        return "NA"
    if isinstance(value, str):
        return value
    if finite(value):
        return f"{float(value):.{digits}f}"
    return "NA"


def percentile(values: list[float], q: float) -> float | None:
    xs = sorted(float(value) for value in values if finite(value))
    if not xs:
        return None
    if len(xs) == 1:
        return xs[0]
    pos = (len(xs) - 1) * q
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return xs[lo]
    frac = pos - lo
    return xs[lo] * (1.0 - frac) + xs[hi] * frac


def stats(values: list[float]) -> dict[str, float | None]:
    xs = [float(value) for value in values if finite(value)]
    if not xs:
        return {"mean": None, "std": None, "min": None, "p50": None, "p95": None, "max": None}
    return {
        "mean": mean(xs),
        "std": pstdev(xs) if len(xs) > 1 else 0.0,
        "min": min(xs),
        "p50": percentile(xs, 0.50),
        "p95": percentile(xs, 0.95),
        "max": max(xs),
    }


def pct(count: int, total: int) -> float | None:
    if total <= 0:
        return None
    return 100.0 * count / total


def read_trace(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def command_label(path: Path) -> str:
    name = path.parent.name
    marker = "published_policy_command_"
    if marker in name:
        rest = name.split(marker, 1)[1]
        if "_seed" in rest:
            return rest.rsplit("_seed", 1)[0]
        return rest
    return name


def contact_code(row: dict[str, Any]) -> str:
    contacts = row.get("foot_contacts")
    if not isinstance(contacts, list) or len(contacts) < 2:
        return "??"
    left = 1 if int(contacts[0]) else 0
    right = 1 if int(contacts[1]) else 0
    return f"{left}{right}"


def contact_bucket(code: str) -> str:
    if code == "11":
        return "double"
    if code in {"10", "01"}:
        return "single"
    if code == "00":
        return "flight"
    return "unknown"


def local_vx(row: dict[str, Any]) -> float | None:
    value = row.get("local_linvel_m_s")
    if isinstance(value, list) and value and finite(value[0]):
        return float(value[0])
    return None


def stance_foot_index(code: str) -> int | None:
    if code == "10":
        return 0
    if code == "01":
        return 1
    return None


def stance_relative_base(row: dict[str, Any]) -> tuple[float, float] | None:
    code = contact_code(row)
    index = stance_foot_index(code)
    feet = row.get("foot_site_pos_m")
    base_x = row.get("base_x_m")
    base_y = row.get("base_y_m")
    if index is None or not isinstance(feet, list) or len(feet) <= index:
        return None
    foot = feet[index]
    if not isinstance(foot, list) or len(foot) < 2:
        return None
    if not (finite(base_x) and finite(base_y) and finite(foot[0]) and finite(foot[1])):
        return None
    return float(base_x) - float(foot[0]), float(base_y) - float(foot[1])


def target_velocity_p95(rows: list[dict[str, Any]], dt_s: float) -> float | None:
    previous: list[float] | None = None
    values: list[float] = []
    pitch_indices = [2, 3, 4, 11, 12, 13]
    for row in rows:
        target = row.get("sent_target_rad") or row.get("applied_target_rad")
        if not isinstance(target, list) or len(target) < 14:
            previous = None
            continue
        current = [float(value) for value in target[:14] if finite(value)]
        if len(current) < 14:
            previous = None
            continue
        if previous is not None:
            for index in pitch_indices:
                values.append(abs(current[index] - previous[index]) / dt_s)
        previous = current
    return percentile(values, 0.95)


def alternations(codes: list[str]) -> int:
    singles = [code for code in codes if code in {"10", "01"}]
    return sum(1 for prev, cur in zip(singles, singles[1:]) if prev != cur)


def analyze_trace(path: Path, args: argparse.Namespace) -> dict[str, Any]:
    rows = read_trace(path)
    contacts = [contact_code(row) for row in rows]
    counts = Counter(contacts)
    future_dvx_single: list[float] = []
    future_dvx_double: list[float] = []
    future_dvx_all: list[float] = []
    stance_dx: list[float] = []
    stance_dy: list[float] = []
    stance_abs_dy: list[float] = []
    single_positive_push = 0
    single_push_samples = 0
    for index, row in enumerate(rows):
        future_index = index + args.future_ticks
        now = local_vx(row)
        later = local_vx(rows[future_index]) if future_index < len(rows) else None
        if now is not None and later is not None:
            delta = later - now
            future_dvx_all.append(delta)
            if contact_bucket(contact_code(row)) == "single":
                future_dvx_single.append(delta)
                single_push_samples += 1
                if delta > 0.0:
                    single_positive_push += 1
            elif contact_bucket(contact_code(row)) == "double":
                future_dvx_double.append(delta)
        rel = stance_relative_base(row)
        if rel is not None:
            dx, dy = rel
            stance_dx.append(dx)
            stance_dy.append(dy)
            stance_abs_dy.append(abs(dy))
    vx_values = [value for row in rows if (value := local_vx(row)) is not None]
    command = rows[0].get("command") if rows else None
    command_x = command[0] if isinstance(command, list) and command and finite(command[0]) else None
    return {
        "source_path": str(path),
        "source_name": path.parent.name,
        "command_cell": command_label(path),
        "seed": rows[0].get("seed") if rows else None,
        "samples": len(rows),
        "duration_complete": not any(bool(row.get("done")) for row in rows),
        "command": command,
        "mean_vx_m_s": mean(vx_values) if vx_values else None,
        "command_tracking_ratio": mean(vx_values) / command_x if vx_values and command_x not in (None, 0.0) else None,
        "contact_counts": dict(sorted(counts.items())),
        "single_support_pct": pct(counts["10"] + counts["01"], len(rows)),
        "double_support_pct": pct(counts["11"], len(rows)),
        "flight_pct": pct(counts["00"], len(rows)),
        "single_alternations": alternations(contacts),
        "single_future_dvx_0p1s_m_s": stats(future_dvx_single),
        "double_future_dvx_0p1s_m_s": stats(future_dvx_double),
        "all_future_dvx_0p1s_m_s": stats(future_dvx_all),
        "single_positive_push_pct": pct(single_positive_push, single_push_samples),
        "stance_base_dx_m": stats(stance_dx),
        "stance_base_dy_m": stats(stance_dy),
        "stance_base_abs_dy_m": stats(stance_abs_dy),
        "pitch_target_velocity_p95_rad_s": target_velocity_p95(rows, args.dt_s),
    }


def collect(values: list[dict[str, Any]], path: list[str]) -> list[float]:
    out: list[float] = []
    for item in values:
        value: Any = item
        for key in path:
            value = value.get(key) if isinstance(value, dict) else None
        if finite(value):
            out.append(float(value))
    return out


def aggregate(traces: list[dict[str, Any]]) -> dict[str, Any]:
    by_cell: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for trace in traces:
        by_cell[trace["command_cell"]].append(trace)
    payload: dict[str, Any] = {}
    for label, items in sorted(by_cell.items()):
        payload[label] = {
            "trace_count": len(items),
            "duration_complete_count": sum(1 for item in items if item.get("duration_complete")),
            "mean_vx_m_s": stats(collect(items, ["mean_vx_m_s"])),
            "command_tracking_ratio": stats(collect(items, ["command_tracking_ratio"])),
            "single_support_pct": stats(collect(items, ["single_support_pct"])),
            "double_support_pct": stats(collect(items, ["double_support_pct"])),
            "single_alternations": stats(collect(items, ["single_alternations"])),
            "single_future_dvx_0p1s_m_s": stats(collect(items, ["single_future_dvx_0p1s_m_s", "mean"])),
            "single_positive_push_pct": stats(collect(items, ["single_positive_push_pct"])),
            "stance_base_dx_mean_m": stats(collect(items, ["stance_base_dx_m", "mean"])),
            "stance_base_abs_dy_mean_m": stats(collect(items, ["stance_base_abs_dy_m", "mean"])),
            "pitch_target_velocity_p95_rad_s": stats(collect(items, ["pitch_target_velocity_p95_rad_s"])),
        }
    return payload


def status(aggregate_payload: dict[str, Any]) -> str:
    moving_cells = [
        item
        for item in aggregate_payload.values()
        if (item["mean_vx_m_s"]["mean"] or 0.0) >= 0.04 and (item["single_support_pct"]["mean"] or 0.0) >= 20.0
    ]
    if not moving_cells:
        return "HOLD_NO_MOVING_SINGLE_SUPPORT_CELL"
    return "PASS_STANCE_TIMING_COMPARISON_READY"


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    lines = [
        "# Published Policy Stance Timing Comparison",
        "",
        f"status: `{payload['status']}`",
        "",
        "This is an offline analysis of existing BEST_WALK traces. It does not train, deploy, SSH, run robot tests, or change runtime behavior.",
        "",
        "## Command Summary",
        "",
        "| command_cell | traces | complete | mean_vx | track_ratio | single_% | double_% | alt | single_dvx_0p1s | single_push_% | stance_dx | stance_abs_dy | pitch_p95 |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for label, item in payload["aggregate"].items():
        lines.append(
            f"| {label} | {item['trace_count']} | {item['duration_complete_count']} | "
            f"{fmt(item['mean_vx_m_s']['mean'])} | "
            f"{fmt(item['command_tracking_ratio']['mean'])} | "
            f"{fmt(item['single_support_pct']['mean'])} | "
            f"{fmt(item['double_support_pct']['mean'])} | "
            f"{fmt(item['single_alternations']['mean'])} | "
            f"{fmt(item['single_future_dvx_0p1s_m_s']['mean'])} | "
            f"{fmt(item['single_positive_push_pct']['mean'])} | "
            f"{fmt(item['stance_base_dx_mean_m']['mean'])} | "
            f"{fmt(item['stance_base_abs_dy_mean_m']['mean'])} | "
            f"{fmt(item['pitch_target_velocity_p95_rad_s']['mean'])} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- `single_dvx_0p1s` is the average local-forward velocity change 5 ticks after a single-support tick.",
            "- `stance_dx` and `stance_abs_dy` use base x/y minus the active stance foot site x/y during single support.",
            "- Compare straight `x=0.04` with the moving command cells before treating x=0.04 as a walking existence gate.",
            "- Positive single-support propulsion with high pitch p95 means the mechanism exists, but may still exceed the measured actuator envelope.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--trace-glob",
        action="append",
        default=[],
        help="Trace glob. May be passed multiple times.",
    )
    parser.add_argument("--output-md", default="outputs/analysis/PUBLISHED_POLICY_STANCE_TIMING_COMPARISON.md")
    parser.add_argument("--output-json", default="outputs/analysis/published_policy_stance_timing_comparison.json")
    parser.add_argument("--dt-s", type=float, default=0.02)
    parser.add_argument("--future-ticks", type=int, default=5, help="Future tick horizon for velocity delta.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    patterns = args.trace_glob or ["outputs/analysis/published_policy_command_*_seed*/trace_full_obs_footpos.jsonl"]
    paths: list[Path] = []
    for pattern in patterns:
        paths.extend(Path(path) for path in glob.glob(str(ROOT / pattern)))
    paths = sorted(set(paths))
    traces = [analyze_trace(path, args) for path in paths]
    aggregate_payload = aggregate(traces)
    payload = {
        "status": status(aggregate_payload),
        "criteria": {"dt_s": args.dt_s, "future_ticks": args.future_ticks},
        "trace_globs": patterns,
        "aggregate": aggregate_payload,
        "traces": traces,
    }
    output_json = ROOT / args.output_json
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    write_markdown(payload, ROOT / args.output_md)
    print(f"status={payload['status']}")
    print(f"traces={len(traces)}")
    print(f"wrote {args.output_md}")
    print(f"wrote {args.output_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
