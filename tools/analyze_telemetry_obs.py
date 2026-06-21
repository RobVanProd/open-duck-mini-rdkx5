#!/usr/bin/env python3
import argparse
import json
import math
import statistics
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_PKG = ROOT / "Open_Duck_Mini_Runtime" / "mini_bdx_runtime"
if RUNTIME_PKG.exists():
    sys.path.insert(0, str(RUNTIME_PKG))

from mini_bdx_runtime.telemetry import extract_onnx_obs_normalization


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


def finite(v):
    return v is not None and not (isinstance(v, float) and (math.isnan(v) or math.isinf(v)))


def percentile(values, pct):
    values = sorted(v for v in values if finite(v))
    if not values:
        return None
    if len(values) == 1:
        return values[0]
    k = (len(values) - 1) * pct / 100.0
    lo = math.floor(k)
    hi = math.ceil(k)
    if lo == hi:
        return values[int(k)]
    return values[lo] * (hi - k) + values[hi] * (k - lo)


def stats(values):
    values = [float(v) for v in values if finite(v)]
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


def fmt(v, digits=4):
    if v is None:
        return "NA"
    return f"{v:.{digits}f}"


def load_records(path):
    records = []
    with open(path) as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                print(f"Skipping invalid JSON line {line_no}: {exc}", file=sys.stderr)
    return records


def get_obs(record):
    return record.get("observation", {}).get("raw_vector")


def get_norm(records, onnx_model_path=None):
    for record in records:
        obs = record.get("observation", {})
        mean = obs.get("normalization_mean")
        std_recip = obs.get("normalization_std_recip")
        if mean and std_recip:
            return mean, std_recip, "telemetry"
    if onnx_model_path:
        norm = extract_onnx_obs_normalization(onnx_model_path)
        if norm.get("mean") and norm.get("std_recip"):
            return norm["mean"], norm["std_recip"], onnx_model_path
    return None, None, None


def vector_column(records, start, end):
    columns = {i: [] for i in range(start, end)}
    for record in records:
        obs = get_obs(record)
        if obs is None or len(obs) < end:
            continue
        for i in range(start, end):
            columns[i].append(obs[i])
    return columns


def action_saturation(records, threshold=0.98):
    counts = [0] * 14
    totals = [0] * 14
    for record in records:
        action = record.get("action", {}).get("onnx_action")
        if action is None or len(action) < 14:
            continue
        for i, value in enumerate(action[:14]):
            totals[i] += 1
            if abs(float(value)) >= threshold:
                counts[i] += 1
    return [
        None if totals[i] == 0 else counts[i] / totals[i] * 100.0 for i in range(14)
    ]


def tracking_error_stats(records):
    per_joint = [[] for _ in range(14)]
    for record in records:
        error = record.get("joints", {}).get("tracking_error_rad")
        if error is None or len(error) < 14:
            continue
        for i, value in enumerate(error[:14]):
            per_joint[i].append(abs(float(value)))
    return [stats(values) for values in per_joint]


def contact_events(records):
    last = None
    events = 0
    counts = {"left_true": 0, "right_true": 0, "samples": 0}
    for record in records:
        contacts = record.get("control", {}).get("feet_contacts")
        if contacts is None:
            continue
        contacts = tuple(bool(v) for v in contacts[:2])
        counts["samples"] += 1
        counts["left_true"] += int(contacts[0])
        counts["right_true"] += int(contacts[1])
        if last is not None and contacts != last:
            events += 1
        last = contacts
    counts["events"] = events
    return counts


def warnings(records, mean, std_recip):
    out = []
    obs_cols = vector_column(records, 0, 6)
    obs_stats = {i: stats(v) for i, v in obs_cols.items()}
    if mean and std_recip:
        for i in range(6):
            s = obs_stats.get(i)
            if not s:
                continue
            z = (s["mean"] - mean[i]) * std_recip[i]
            if abs(z) > 3.0:
                out.append(
                    f"obs[{i}] mean is {z:.2f} sigma from ONNX normalization mean"
                )
    accel = [obs_stats.get(i) for i in range(3, 6)]
    if all(accel):
        means = [s["mean"] for s in accel]
        abs_means = [abs(v) for v in means]
        max_axis = abs_means.index(max(abs_means))
        if max_axis != 2:
            out.append(
                "upright acceleration magnitude is not largest on obs[5]/accel_z; axes may be swapped"
            )
        if means[2] < 0:
            out.append("upright accel_z mean is negative; accel sign may be flipped")
        if mean and std_recip:
            z_accel = [
                (means[i] - mean[i + 3]) * std_recip[i + 3] for i in range(3)
            ]
            if max(abs(v) for v in z_accel) > 3:
                out.append(
                    "upright accel[0:3] is outside the ONNX training neighborhood"
                )
    bus_last = records[-1].get("bus", {}) if records else {}
    if bus_last.get("read_error_count", 0):
        out.append(f"bus read errors recorded: {bus_last.get('read_error_count')}")
    if bus_last.get("write_error_count", 0):
        out.append(f"bus write errors recorded: {bus_last.get('write_error_count')}")
    return out


def build_report(records, mean, std_recip, norm_source):
    lines = []
    lines.append(f"# Telemetry Observation Analysis")
    lines.append("")
    lines.append(f"samples: {len(records)}")
    lines.append(f"normalization_source: {norm_source or 'UNKNOWN'}")
    lines.append("")

    lines.append("## Observation 0:6")
    lines.append("")
    lines.append("| index | channel | mean | std | min | max | z_mean |")
    lines.append("|---:|---|---:|---:|---:|---:|---:|")
    names = ["gyro_x", "gyro_y", "gyro_z", "accel_x", "accel_y", "accel_z"]
    for i, values in vector_column(records, 0, 6).items():
        s = stats(values)
        z = None if not s or not mean or not std_recip else (s["mean"] - mean[i]) * std_recip[i]
        lines.append(
            f"| {i} | {names[i]} | {fmt(None if not s else s['mean'])} | "
            f"{fmt(None if not s else s['std'])} | {fmt(None if not s else s['min'])} | "
            f"{fmt(None if not s else s['max'])} | {fmt(z, 2)} |"
        )

    lines.append("")
    lines.append("## Joint Position Error obs[13:27]")
    lines.append("")
    lines.append("| obs | joint | mean | std | min | max | z_mean |")
    lines.append("|---:|---|---:|---:|---:|---:|---:|")
    for offset, (i, values) in enumerate(vector_column(records, 13, 27).items()):
        s = stats(values)
        z = None if not s or not mean or not std_recip else (s["mean"] - mean[i]) * std_recip[i]
        lines.append(
            f"| {i} | {JOINT_NAMES[offset]} | {fmt(None if not s else s['mean'])} | "
            f"{fmt(None if not s else s['std'])} | {fmt(None if not s else s['min'])} | "
            f"{fmt(None if not s else s['max'])} | {fmt(z, 2)} |"
        )

    lines.append("")
    lines.append("## Joint Velocity obs[27:41]")
    lines.append("")
    lines.append("| obs | joint | mean | std | min | max | z_mean |")
    lines.append("|---:|---|---:|---:|---:|---:|---:|")
    for offset, (i, values) in enumerate(vector_column(records, 27, 41).items()):
        s = stats(values)
        z = None if not s or not mean or not std_recip else (s["mean"] - mean[i]) * std_recip[i]
        lines.append(
            f"| {i} | {JOINT_NAMES[offset]} | {fmt(None if not s else s['mean'])} | "
            f"{fmt(None if not s else s['std'])} | {fmt(None if not s else s['min'])} | "
            f"{fmt(None if not s else s['max'])} | {fmt(z, 2)} |"
        )

    lines.append("")
    lines.append("## Action Saturation")
    lines.append("")
    lines.append("| action | joint | pct_abs_ge_0.98 |")
    lines.append("|---:|---|---:|")
    for i, pct in enumerate(action_saturation(records)):
        lines.append(f"| {i} | {JOINT_NAMES[i]} | {fmt(pct, 2)} |")

    lines.append("")
    lines.append("## Tracking Error")
    lines.append("")
    lines.append("| joint | p50_abs_rad | p95_abs_rad | p99_abs_rad | max_abs_rad |")
    lines.append("|---|---:|---:|---:|---:|")
    for i, s in enumerate(tracking_error_stats(records)):
        lines.append(
            f"| {JOINT_NAMES[i]} | {fmt(None if not s else s['p50'])} | "
            f"{fmt(None if not s else s['p95'])} | {fmt(None if not s else s['p99'])} | "
            f"{fmt(None if not s else s['max'])} |"
        )

    dt_values = [record.get("dt_s") for record in records if finite(record.get("dt_s"))]
    dt = stats(dt_values)
    lines.append("")
    lines.append("## Timing And Contacts")
    lines.append("")
    lines.append(f"dt_mean_s: {fmt(None if not dt else dt['mean'], 5)}")
    lines.append(f"dt_p95_s: {fmt(None if not dt else dt['p95'], 5)}")
    lines.append(f"dt_max_s: {fmt(None if not dt else dt['max'], 5)}")
    lines.append(f"contacts: {json.dumps(contact_events(records), sort_keys=True)}")
    bus_last = records[-1].get("bus", {}) if records else {}
    lines.append(f"bus: {json.dumps(bus_last, sort_keys=True)}")

    warn = warnings(records, mean, std_recip)
    lines.append("")
    lines.append("## Warnings")
    lines.append("")
    if warn:
        for item in warn:
            lines.append(f"- {item}")
    else:
        lines.append("- none")
    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Analyze Open Duck telemetry JSONL.")
    parser.add_argument("telemetry_jsonl")
    parser.add_argument("--onnx-model", default=None)
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    records = load_records(args.telemetry_jsonl)
    mean, std_recip, norm_source = get_norm(records, args.onnx_model)
    report = build_report(records, mean, std_recip, norm_source)
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, "w") as f:
            f.write(report)
            f.write("\n")
    print(report)


if __name__ == "__main__":
    main()
