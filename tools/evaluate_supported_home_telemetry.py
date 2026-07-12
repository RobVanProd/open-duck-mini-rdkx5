#!/usr/bin/env python3
"""Evaluate telemetry for supported home; physical geometry remains operator-only."""

import argparse, json, math
from pathlib import Path
from analyze_runtime_warnings import parse_terminal_log
JOINT_NAMES = ["left_hip_yaw", "left_hip_roll", "left_hip_pitch", "left_knee",
               "left_ankle", "neck_pitch", "head_pitch", "head_yaw", "head_roll",
               "right_hip_yaw", "right_hip_roll", "right_hip_pitch", "right_knee",
               "right_ankle"]


def load_records(path):
    with open(path) as stream:
        return [json.loads(line) for line in stream if line.strip()]


def percentile(values, pct):
    values = sorted(values)
    if not values:
        return None
    position = (len(values) - 1) * pct / 100
    low, high = math.floor(position), math.ceil(position)
    if low == high:
        return values[low]
    return values[low] * (high - position) + values[high] * (position - low)

PITCH = {2, 3, 4, 11, 12, 13}


def columns(records, group, field, width):
    out = [[] for _ in range(width)]
    for record in records:
        values = record.get(group, {}).get(field)
        if values and len(values) >= width:
            for i, value in enumerate(values[:width]):
                if value is not None and math.isfinite(float(value)):
                    out[i].append(float(value))
    return out


def longest_over(values, limit):
    best = run = 0
    for value in values:
        run = run + 1 if abs(value) > limit else 0
        best = max(best, run)
    return best


def evaluate(records, terminal, startup, p95_limit, sustained_limit, sustained_samples):
    post = records[startup:]
    holds, warnings, rows = [], [], []
    if len(post) < 50:
        holds.append(f"only {len(post)} post-startup samples; require at least 50")
    tracking = columns(post, "joints", "tracking_error_rad", 14)
    for i, values in enumerate(tracking):
        p95 = percentile([abs(v) for v in values], 95) if values else None
        run = longest_over(values, sustained_limit)
        rows.append({"joint": JOINT_NAMES[i], "pitch_chain": i in PITCH,
                     "p95_abs_rad": p95, "max_consecutive_over_limit": run})
        if not values:
            holds.append(f"missing tracking telemetry for {JOINT_NAMES[i]}")
        elif i in PITCH and p95 >= p95_limit:
            holds.append(f"{JOINT_NAMES[i]} p95 {p95:.4f} rad is not below {p95_limit:.4f}")
        if i in PITCH and run >= sustained_samples:
            holds.append(f"{JOINT_NAMES[i]} has {run} consecutive samples above {sustained_limit:.3f} rad")
    obs = columns(post, "observation", "raw_vector", 6)
    gyro = [percentile([abs(v) for v in axis], 95) if axis else None for axis in obs[:3]]
    accel = [sum(axis) / len(axis) if axis else None for axis in obs[3:6]]
    if any(v is None for v in gyro + accel):
        holds.append("missing upright IMU telemetry")
    else:
        if max(gyro) >= 0.20:
            holds.append(f"gyro p95 {max(gyro):.4f} rad/s is not below 0.20")
        if accel[2] <= 0 or abs(accel[2]) <= max(abs(accel[0]), abs(accel[1])):
            holds.append("upright acceleration is not positive-Z dominant")
    bus = records[-1].get("bus", {}) if records else {}
    first_bus = records[0].get("bus", {}) if records else {}
    read_delta = None
    if bus.get("read_error_count") is None or first_bus.get("read_error_count") is None:
        warnings.append("read_error_count unavailable")
    else:
        read_delta = max(0, int(bus["read_error_count"]) - int(first_bus["read_error_count"]))
        read_rate = read_delta / len(records) if records else None
        if read_rate is not None and read_rate > 0.02:
            holds.append(f"read retry rate {read_rate * 100:.2f}% exceeds 2.00%")
        elif read_delta:
            warnings.append(f"{read_delta} recovered read retries ({read_rate * 100:.2f}%) without a write failure")
    if bus.get("write_error_count") is None:
        warnings.append("write_error_count unavailable")
    elif int(bus["write_error_count"]):
        holds.append(f"write_error_count={bus['write_error_count']}")
    if terminal["missing"]:
        holds.append("terminal log missing")
    for key in ("write_error", "control_budget_exceeded", "exception_or_traceback"):
        if terminal["counts"].get(key, 0):
            holds.append(f"terminal {key} count={terminal['counts'][key]}")
    status = ("HOLD_TELEMETRY_COMPONENT" if holds else
              "PASS_TELEMETRY_COMPONENT_WITH_WARNINGS" if warnings else
              "PASS_TELEMETRY_COMPONENT")
    return {"schema_version": "open_duck_supported_home_telemetry_gate_v1",
            "status": status,
            "physical_pose_status": "REQUIRES_OPERATOR_VISUAL_CONFIRMATION",
            "samples": len(records), "post_startup_samples": len(post),
            "thresholds": {"startup_ticks": startup, "pitch_p95_rad_exclusive": p95_limit,
                           "sustained_error_rad_exclusive": sustained_limit,
                           "sustained_samples": sustained_samples,
                           "gyro_p95_rad_s_exclusive": 0.20},
            "gyro_p95_abs_rad_s": gyro, "accel_mean_m_s2": accel, "tracking": rows,
            "bus": bus, "bus_read_error_delta": read_delta,
            "terminal": terminal, "holds": holds, "warnings": warnings}


def markdown(r):
    lines = ["# Supported Home Telemetry Gate", "", f"status: `{r['status']}`",
             f"physical_pose_status: `{r['physical_pose_status']}`", "",
             "Telemetry cannot approve physical geometry.", "", "## Holds", ""]
    lines += [f"- {x}" for x in r["holds"]] or ["- none"]
    lines += ["", "## Tracking", "", "| joint | pitch | p95 abs rad | max consecutive over limit |",
              "|---|---|---:|---:|"]
    for row in r["tracking"]:
        p95 = "NA" if row["p95_abs_rad"] is None else f"{row['p95_abs_rad']:.4f}"
        lines.append(f"| `{row['joint']}` | `{row['pitch_chain']}` | {p95} | {row['max_consecutive_over_limit']} |")
    lines += ["", f"gyro_p95_abs_rad_s: `{r['gyro_p95_abs_rad_s']}`",
              f"accel_mean_m_s2: `{r['accel_mean_m_s2']}`", ""]
    return "\n".join(lines)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("telemetry_jsonl"); p.add_argument("--terminal-log", required=True)
    p.add_argument("--startup-ticks", type=int, default=25)
    p.add_argument("--pitch-p95-limit", type=float, default=0.08)
    p.add_argument("--sustained-limit", type=float, default=0.10)
    p.add_argument("--sustained-samples", type=int, default=3)
    p.add_argument("--output-md", required=True); p.add_argument("--output-json", required=True)
    a = p.parse_args()
    r = evaluate(load_records(a.telemetry_jsonl), parse_terminal_log(a.terminal_log),
                 a.startup_ticks, a.pitch_p95_limit, a.sustained_limit, a.sustained_samples)
    Path(a.output_md).write_text(markdown(r).rstrip() + "\n")
    Path(a.output_json).write_text(json.dumps(r, indent=2, sort_keys=True) + "\n")
    print(r["status"])


if __name__ == "__main__": main()
