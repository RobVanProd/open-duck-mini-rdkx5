#!/usr/bin/env python3
"""Summarize reference-vs-actual contact compatibility from rollout traces."""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TRACE_DIRS = [
    ROOT / "outputs" / "analysis" / "reference_motion_rollout_v20_traces",
    ROOT / "outputs" / "analysis" / "reference_motion_rollout_v20_projected_traces",
    ROOT / "outputs" / "analysis" / "reference_motion_rollout_v20_projected_phase5_traces",
    ROOT / "outputs" / "analysis" / "reference_motion_rollout_v20_projected_phase19_traces",
]
DEFAULT_OUTPUT_MD = ROOT / "outputs" / "analysis" / "REFERENCE_CONTACT_COMPATIBILITY_V20.md"
DEFAULT_OUTPUT_JSON = ROOT / "outputs" / "analysis" / "reference_contact_compatibility_v20.json"


def pattern(values: list[int] | tuple[int, ...]) -> str:
    return "".join(str(int(value)) for value in values)


def percent(count: int, total: int) -> float:
    return float(count / total * 100.0) if total else 0.0


def read_trace_dir(path: Path) -> dict[str, Any]:
    records = []
    for trace in sorted(path.glob("*.jsonl")):
        for line in trace.read_text().splitlines():
            if line.strip():
                records.append(json.loads(line))
    actual = Counter()
    expected = Counter()
    pair = Counter()
    seed_samples = Counter()
    seed_mismatch = Counter()
    first_mismatch: dict[str, dict[str, Any]] = {}
    terminations: dict[str, dict[str, Any]] = {}
    for record in records:
        seed = str(record.get("seed"))
        actual_pattern = pattern(record.get("foot_contacts", []))
        expected_pattern = pattern(record.get("reference_foot_contacts", []))
        actual[actual_pattern] += 1
        expected[expected_pattern] += 1
        pair[f"{expected_pattern}->{actual_pattern}"] += 1
        seed_samples[seed] += 1
        mismatch = actual_pattern != expected_pattern
        if mismatch:
            seed_mismatch[seed] += 1
            first_mismatch.setdefault(
                seed,
                {
                    "tick": record.get("tick"),
                    "time_s": record.get("time_s"),
                    "expected": expected_pattern,
                    "actual": actual_pattern,
                },
            )
        if record.get("done"):
            terminations[seed] = {
                "tick": record.get("tick"),
                "time_s": record.get("time_s"),
                "expected": expected_pattern,
                "actual": actual_pattern,
                "base_height_m": record.get("base_height_m"),
                "local_linvel_m_s": record.get("local_linvel_m_s"),
            }
    total = len(records)
    seed_rows = []
    for seed in sorted(seed_samples, key=lambda value: int(value)):
        seed_rows.append(
            {
                "seed": int(seed),
                "samples": int(seed_samples[seed]),
                "mismatch_pct": percent(seed_mismatch[seed], seed_samples[seed]),
                "first_mismatch": first_mismatch.get(seed),
                "termination": terminations.get(seed),
            }
        )
    return {
        "trace_dir": str(path),
        "label": path.name,
        "samples": total,
        "mismatch_pct": percent(
            sum(count for key, count in pair.items() if key.split("->")[0] != key.split("->")[1]),
            total,
        ),
        "actual_contact_pct": {
            key: percent(value, total) for key, value in sorted(actual.items())
        },
        "reference_contact_pct": {
            key: percent(value, total) for key, value in sorted(expected.items())
        },
        "pair_pct": {
            key: percent(value, total) for key, value in sorted(pair.items())
        },
        "seed_rows": seed_rows,
    }


def fmt(value: Any, digits: int = 2) -> str:
    if value is None:
        return "NA"
    return f"{float(value):.{digits}f}"


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    lines = [
        "# Reference Contact Compatibility",
        "",
        "This summarizes actual foot contacts from reference-target rollouts against",
        "the foot-contact pattern encoded in the polynomial reference.",
        "",
        "## Runs",
        "",
        "| label | samples | mismatch_pct | actual 11 pct | ref 11 pct | actual 10 pct | ref 10 pct | actual 01 pct | ref 01 pct |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for run in payload["runs"]:
        actual = run["actual_contact_pct"]
        ref = run["reference_contact_pct"]
        lines.append(
            "| {label} | {samples} | {mismatch} | {a11} | {r11} | {a10} | {r10} | {a01} | {r01} |".format(
                label=run["label"],
                samples=run["samples"],
                mismatch=fmt(run["mismatch_pct"]),
                a11=fmt(actual.get("11", 0.0)),
                r11=fmt(ref.get("11", 0.0)),
                a10=fmt(actual.get("10", 0.0)),
                r10=fmt(ref.get("10", 0.0)),
                a01=fmt(actual.get("01", 0.0)),
                r01=fmt(ref.get("01", 0.0)),
            )
        )
    lines.extend(
        [
            "",
            "## Dominant Mismatch Pairs",
            "",
            "| label | pair | pct |",
            "|---|---|---:|",
        ]
    )
    for run in payload["runs"]:
        mismatches = [
            (pair, pct)
            for pair, pct in run["pair_pct"].items()
            if pair.split("->")[0] != pair.split("->")[1]
        ]
        for pair, pct in sorted(mismatches, key=lambda item: item[1], reverse=True)[:4]:
            lines.append(f"| {run['label']} | `{pair}` | {fmt(pct)} |")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- `11` means both feet in contact, `10` left-only, `01` right-only, `00` no contact.",
            "- High mismatch means the reference contact schedule is not realized by the simulated body under the tested target path.",
            "- Persistent double-support actual contacts while the reference expects single support points to contact/lateral/reference incompatibility.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--trace-dir",
        action="append",
        default=None,
        help="Trace directory containing reference_seed_*.jsonl. May be repeated.",
    )
    parser.add_argument("--output-md", default=str(DEFAULT_OUTPUT_MD))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    args = parser.parse_args()
    trace_dirs = [Path(item) for item in args.trace_dir] if args.trace_dir else DEFAULT_TRACE_DIRS
    runs = []
    for trace_dir in trace_dirs:
        path = trace_dir if trace_dir.is_absolute() else ROOT / trace_dir
        if not path.exists():
            raise SystemExit(f"Missing trace dir: {path}")
        runs.append(read_trace_dir(path))
    payload = {"runs": runs}
    output_json = Path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2) + "\n")
    write_markdown(payload, Path(args.output_md))
    print(f"wrote {args.output_md}")
    print(f"wrote {args.output_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
