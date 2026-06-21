#!/usr/bin/env python3
import argparse
import json
import math
import re
import statistics
from pathlib import Path


JOINT_NAMES = [
    "left_hip_yaw",
    "left_hip_roll",
    "left_hip_pitch",
    "left_knee",
    "left_ankle",
    "neck_pitch",
    "head_pitch",
    "head_yaw",
    "head_roll",
    "right_hip_yaw",
    "right_hip_roll",
    "right_hip_pitch",
    "right_knee",
    "right_ankle",
]

WARNING_PATTERNS = {
    "crc_mismatch": re.compile(r"\bcrc\b", re.IGNORECASE),
    "read_crc": re.compile(r"read\s+crc", re.IGNORECASE),
    "write_crc": re.compile(r"write\s+crc", re.IGNORECASE),
    "read_error": re.compile(r"read\s+(?:error|failed|exception)", re.IGNORECASE),
    "write_error": re.compile(r"write\s+(?:error|failed|exception)", re.IGNORECASE),
    "timeout": re.compile(r"\btimeout\b|\btimed out\b", re.IGNORECASE),
    "control_budget_exceeded": re.compile(
        r"policy control budget exceeded", re.IGNORECASE
    ),
    "exception_or_traceback": re.compile(r"\bexception\b|\btraceback\b", re.IGNORECASE),
    "motor_off_cleanup": re.compile(
        r"\bturning off\b|\bturn_off\b|\bmotor off\b|\bcleanup\b", re.IGNORECASE
    ),
}

TIMESTAMP_RE = re.compile(
    r"(?P<iso>\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}(?:[.,]\d+)?)|"
    r"(?P<bracket>\[(?:t=)?(?P<float>\d+(?:\.\d+)?)\])"
)


def is_finite(value):
    return value is not None and not (
        isinstance(value, float) and (math.isnan(value) or math.isinf(value))
    )


def percentile(values, pct):
    values = sorted(float(v) for v in values if is_finite(v))
    if not values:
        return None
    if len(values) == 1:
        return values[0]
    k = (len(values) - 1) * pct / 100.0
    lo = math.floor(k)
    hi = math.ceil(k)
    if lo == hi:
        return values[lo]
    return values[lo] * (hi - k) + values[hi] * (k - lo)


def stats(values):
    values = [float(v) for v in values if is_finite(v)]
    if not values:
        return None
    return {
        "mean": statistics.fmean(values),
        "std": statistics.pstdev(values) if len(values) > 1 else 0.0,
        "min": min(values),
        "max": max(values),
        "p50": percentile(values, 50),
        "p95": percentile(values, 95),
        "p99": percentile(values, 99),
    }


def fmt(value, digits=4):
    if value is None:
        return "NA"
    return f"{value:.{digits}f}"


def load_records(path):
    records = []
    if not path:
        return records
    with open(path) as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                print(f"Skipping invalid JSON line {line_no}: {exc}")
    return records


def extract_timestamp(line):
    match = TIMESTAMP_RE.search(line)
    if not match:
        return None
    if match.group("float") is not None:
        return float(match.group("float"))
    return match.group(0)


def parse_terminal_log(path):
    counts = {name: 0 for name in WARNING_PATTERNS}
    matches = []
    if not path:
        return {
            "path": None,
            "counts": counts,
            "matches": matches,
            "has_timestamps": False,
            "missing": True,
        }
    path = Path(path)
    if not path.exists():
        return {
            "path": str(path),
            "counts": counts,
            "matches": matches,
            "has_timestamps": False,
            "missing": True,
        }
    with path.open(errors="replace") as f:
        for line_no, line in enumerate(f, 1):
            line = line.rstrip("\n")
            kinds = [
                name for name, pattern in WARNING_PATTERNS.items() if pattern.search(line)
            ]
            if not kinds:
                continue
            for kind in kinds:
                counts[kind] += 1
            matches.append(
                {
                    "line_no": line_no,
                    "timestamp": extract_timestamp(line),
                    "kinds": kinds,
                    "line": line,
                }
            )
    return {
        "path": str(path),
        "counts": counts,
        "matches": matches,
        "has_timestamps": any(match["timestamp"] is not None for match in matches),
        "missing": False,
    }


def telemetry_dt_summary(records, threshold=0.04):
    values = []
    spikes = []
    for record in records:
        dt_s = record.get("dt_s")
        if not is_finite(dt_s):
            continue
        values.append(float(dt_s))
        if float(dt_s) > threshold:
            spikes.append(
                {
                    "tick": record.get("tick"),
                    "timestamp_monotonic_s": record.get("timestamp_monotonic_s"),
                    "dt_s": float(dt_s),
                }
            )
    return stats(values), spikes


def tracking_summary(records, threshold=0.05):
    per_joint = [[] for _ in JOINT_NAMES]
    spikes = []
    for record in records:
        errors = record.get("joints", {}).get("tracking_error_rad")
        if not errors:
            continue
        for index, value in enumerate(errors[: len(JOINT_NAMES)]):
            if not is_finite(value):
                continue
            abs_value = abs(float(value))
            per_joint[index].append(abs_value)
            if abs_value > threshold:
                spikes.append(
                    {
                        "tick": record.get("tick"),
                        "timestamp_monotonic_s": record.get("timestamp_monotonic_s"),
                        "joint": JOINT_NAMES[index],
                        "abs_error_rad": abs_value,
                    }
                )
    return [stats(values) for values in per_joint], spikes


def build_report(terminal, records):
    lines = ["# Runtime Warning Analysis", ""]
    lines.append(f"terminal_log: `{terminal['path'] or 'MISSING'}`")
    lines.append(f"telemetry_samples: `{len(records)}`")
    lines.append("")

    lines.append("## Warning Counts")
    lines.append("")
    lines.append("| pattern | count |")
    lines.append("|---|---:|")
    for name, count in terminal["counts"].items():
        lines.append(f"| {name} | {count} |")

    if terminal["missing"]:
        lines.append("")
        lines.append("terminal_status: `MISSING`")
    elif terminal["has_timestamps"]:
        lines.append("")
        lines.append("timestamp_status: `present`")
    else:
        lines.append("")
        lines.append("timestamp_status: `not present; warning correlation is limited`")

    if records:
        dt, dt_spikes = telemetry_dt_summary(records)
        tracking, tracking_spikes = tracking_summary(records)
        lines.append("")
        lines.append("## Telemetry Timing")
        lines.append("")
        lines.append(f"dt_mean_s: {fmt(None if not dt else dt['mean'], 5)}")
        lines.append(f"dt_p95_s: {fmt(None if not dt else dt['p95'], 5)}")
        lines.append(f"dt_p99_s: {fmt(None if not dt else dt['p99'], 5)}")
        lines.append(f"dt_max_s: {fmt(None if not dt else dt['max'], 5)}")
        lines.append(f"dt_spikes_gt_0.04_s: {len(dt_spikes)}")
        for spike in dt_spikes[:10]:
            lines.append(
                f"- tick `{spike['tick']}` t=`{fmt(spike['timestamp_monotonic_s'], 5)}` "
                f"dt_s=`{fmt(spike['dt_s'], 5)}`"
            )

        lines.append("")
        lines.append("## Tracking Error")
        lines.append("")
        lines.append("| joint | p95_abs_rad | p99_abs_rad | max_abs_rad |")
        lines.append("|---|---:|---:|---:|")
        for index, summary in enumerate(tracking):
            lines.append(
                f"| {JOINT_NAMES[index]} | {fmt(None if not summary else summary['p95'])} | "
                f"{fmt(None if not summary else summary['p99'])} | "
                f"{fmt(None if not summary else summary['max'])} |"
            )
        lines.append("")
        lines.append(f"tracking_spikes_gt_0.05_rad: {len(tracking_spikes)}")
        for spike in sorted(
            tracking_spikes, key=lambda item: item["abs_error_rad"], reverse=True
        )[:10]:
            lines.append(
                f"- tick `{spike['tick']}` t=`{fmt(spike['timestamp_monotonic_s'], 5)}` "
                f"joint `{spike['joint']}` abs_error_rad=`{fmt(spike['abs_error_rad'])}`"
            )

    lines.append("")
    lines.append("## Terminal Matches")
    lines.append("")
    if terminal["matches"]:
        for match in terminal["matches"][:50]:
            kinds = ",".join(match["kinds"])
            lines.append(
                f"- line `{match['line_no']}` kinds=`{kinds}`: `{match['line']}`"
            )
    else:
        lines.append("- none")

    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze runtime terminal warnings and optional telemetry timing."
    )
    parser.add_argument("terminal_log")
    parser.add_argument("--telemetry-jsonl", default=None)
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    terminal = parse_terminal_log(args.terminal_log)
    records = load_records(args.telemetry_jsonl)
    report = build_report(terminal, records)

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, "w") as f:
            f.write(report)
            f.write("\n")
    print(report)


if __name__ == "__main__":
    main()
