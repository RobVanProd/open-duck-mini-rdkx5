#!/usr/bin/env python3
import argparse
import json
import math
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

PITCH_CHAIN_JOINTS = [
    "left_hip_pitch",
    "left_knee",
    "left_ankle",
    "right_hip_pitch",
    "right_knee",
    "right_ankle",
]


def finite(value):
    return value is not None and not (
        isinstance(value, float) and (math.isnan(value) or math.isinf(value))
    )


def percentile(values, pct):
    values = sorted(float(value) for value in values if finite(value))
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
    values = [float(value) for value in values if finite(value)]
    if not values:
        return None
    return {
        "p50": percentile(values, 50),
        "p95": percentile(values, 95),
        "p99": percentile(values, 99),
        "max": max(values),
    }


def fmt(value, digits=4):
    if value is None:
        return "NA"
    return f"{value:.{digits}f}"


def load_records(path, startup_ticks):
    records = []
    with open(path) as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                print(f"Skipping invalid JSON line {line_no}: {exc}")
                continue
            tick = record.get("tick")
            if tick is not None and int(tick) <= startup_ticks:
                continue
            records.append(record)
    return records


def vector(record, group, field):
    values = record.get(group, {}).get(field)
    if not values:
        return None
    return values


def record_dt(prev, cur):
    dt_s = cur.get("dt_s")
    if finite(dt_s) and float(dt_s) > 0:
        return float(dt_s)
    prev_t = prev.get("timestamp_monotonic_s")
    cur_t = cur.get("timestamp_monotonic_s")
    if finite(prev_t) and finite(cur_t) and float(cur_t) > float(prev_t):
        return float(cur_t) - float(prev_t)
    return None


def consecutive_abs_steps(records, group, field, joint_index):
    values = []
    velocities = []
    previous = None
    for record in records:
        current = vector(record, group, field)
        if current is None or len(current) <= joint_index:
            previous = None
            continue
        if previous is not None:
            before_record, before_value = previous
            dt_s = record_dt(before_record, record)
            step = abs(float(current[joint_index]) - float(before_value))
            values.append(step)
            if dt_s:
                velocities.append(step / dt_s)
        previous = (record, current[joint_index])
    return values, velocities


def within_tick_abs_delta(records, group, before_field, after_field, joint_index):
    values = []
    for record in records:
        before = vector(record, group, before_field)
        after = vector(record, group, after_field)
        if before is None or after is None:
            continue
        if len(before) <= joint_index or len(after) <= joint_index:
            continue
        values.append(abs(float(before[joint_index]) - float(after[joint_index])))
    return values


def per_joint_series(records, group, field, joint_index):
    output = []
    times = []
    for record in records:
        values = vector(record, group, field)
        if values is None or len(values) <= joint_index:
            continue
        value = values[joint_index]
        if not finite(value):
            continue
        output.append(float(value))
        times.append(record.get("timestamp_monotonic_s"))
    return output, times


def best_lag(target, actual, times, max_lag_ticks):
    best = None
    for lag in range(-max_lag_ticks, max_lag_ticks + 1):
        pairs = []
        for index, target_value in enumerate(target):
            actual_index = index + lag
            if 0 <= actual_index < len(actual):
                pairs.append((target_value, actual[actual_index]))
        if len(pairs) < 20:
            continue
        rmse = math.sqrt(sum((left - right) ** 2 for left, right in pairs) / len(pairs))
        if best is None or rmse < best["rmse"]:
            best = {"ticks": lag, "rmse": rmse, "samples": len(pairs)}
    dt_values = [
        float(right) - float(left)
        for left, right in zip(times, times[1:])
        if finite(left) and finite(right) and float(right) > float(left)
    ]
    dt_median = statistics.median(dt_values) if dt_values else None
    if best is not None and dt_median is not None:
        best["ms"] = best["ticks"] * dt_median * 1000.0
    elif best is not None:
        best["ms"] = None
    return best


def action_saturation(records, joint_index, threshold=0.98):
    values, _ = per_joint_series(records, "action", "onnx_action", joint_index)
    if not values:
        return None
    return sum(abs(value) >= threshold for value in values) / len(values) * 100.0


def analyze_joint(records, joint_name, servo_no_load_rad_s, max_lag_ticks):
    joint_index = JOINT_NAMES.index(joint_name)
    sent_steps, sent_velocities = consecutive_abs_steps(
        records, "action", "motor_targets_sent_rad", joint_index
    )
    pre_steps, pre_velocities = consecutive_abs_steps(
        records, "action", "motor_targets_pre_rate_limit_rad", joint_index
    )
    action_steps, _ = consecutive_abs_steps(records, "action", "onnx_action", joint_index)
    rate_limit_delta = within_tick_abs_delta(
        records,
        "action",
        "motor_targets_pre_rate_limit_rad",
        "motor_targets_post_rate_limit_rad",
        joint_index,
    )
    target, times = per_joint_series(records, "action", "motor_targets_sent_rad", joint_index)
    actual, _ = per_joint_series(records, "joints", "actual_position_rad", joint_index)
    lag = best_lag(target, actual, times, max_lag_ticks) if target and actual else None
    tracking_error, _ = per_joint_series(records, "joints", "tracking_error_rad", joint_index)
    tracking_abs = [abs(value) for value in tracking_error]
    sent_velocity_stats = stats(sent_velocities)
    pre_velocity_stats = stats(pre_velocities)
    max_sent_velocity = None if sent_velocity_stats is None else sent_velocity_stats["max"]
    p95_sent_velocity = None if sent_velocity_stats is None else sent_velocity_stats["p95"]
    return {
        "joint": joint_name,
        "sent_step": stats(sent_steps),
        "pre_step": stats(pre_steps),
        "sent_velocity": sent_velocity_stats,
        "pre_velocity": pre_velocity_stats,
        "action_delta": stats(action_steps),
        "tracking": stats(tracking_abs),
        "rate_limit_active_pct": (
            None
            if not rate_limit_delta
            else sum(value > 1e-6 for value in rate_limit_delta) / len(rate_limit_delta) * 100.0
        ),
        "rate_limit_delta_max": max(rate_limit_delta) if rate_limit_delta else None,
        "lag": lag,
        "action_saturation_pct": action_saturation(records, joint_index),
        "p95_vs_no_load_pct": (
            None
            if p95_sent_velocity is None
            else p95_sent_velocity / servo_no_load_rad_s * 100.0
        ),
        "max_vs_no_load_pct": (
            None
            if max_sent_velocity is None
            else max_sent_velocity / servo_no_load_rad_s * 100.0
        ),
    }


def collect_bus(records):
    read_values = []
    write_values = []
    last_error = None
    for record in records:
        bus = record.get("bus", {})
        read = bus.get("read_error_count")
        write = bus.get("write_error_count")
        if finite(read):
            read_values.append(int(read))
        if finite(write):
            write_values.append(int(write))
        if bus.get("last_error"):
            last_error = bus.get("last_error")
    return {
        "read_error_count": max(read_values) if read_values else None,
        "write_error_count": max(write_values) if write_values else None,
        "last_error": last_error,
    }


def build_report(args, records):
    joints = args.joints or PITCH_CHAIN_JOINTS
    results = [
        analyze_joint(records, joint, args.servo_no_load_rad_s, args.max_lag_ticks)
        for joint in joints
    ]
    bus = collect_bus(records)
    command_vectors = [
        tuple(record.get("control", {}).get("commands") or [])
        for record in records
        if record.get("control", {}).get("commands")
    ]
    command_first = command_vectors[0] if command_vectors else None
    command_last = command_vectors[-1] if command_vectors else None

    lines = ["# Policy Target Velocity Analysis", ""]
    lines.append(f"telemetry_jsonl: `{args.telemetry_jsonl}`")
    lines.append(f"samples_after_startup_filter: `{len(records)}`")
    lines.append(f"startup_ticks_excluded: `{args.startup_ticks}`")
    lines.append(f"servo_no_load_rad_s_reference: `{fmt(args.servo_no_load_rad_s, 3)}`")
    lines.append(f"command_first: `{command_first}`")
    lines.append(f"command_last: `{command_last}`")
    lines.append(
        f"bus: read_error_count=`{bus['read_error_count']}`, "
        f"write_error_count=`{bus['write_error_count']}`, last_error=`{bus['last_error']}`"
    )
    lines.append("")

    lines.append("## Pitch-Chain Summary")
    lines.append("")
    lines.append(
        "| joint | sent_vel_p95 | sent_vel_p99 | sent_vel_max | "
        "p95_vs_no_load | rate_limit_active | action_delta_p95 | "
        "tracking_p95 | lag_ticks | lag_ms | action_sat_pct |"
    )
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for item in results:
        velocity = item["sent_velocity"] or {}
        action_delta = item["action_delta"] or {}
        tracking = item["tracking"] or {}
        lag = item["lag"] or {}
        lines.append(
            f"| {item['joint']} | "
            f"{fmt(velocity.get('p95'))} | "
            f"{fmt(velocity.get('p99'))} | "
            f"{fmt(velocity.get('max'))} | "
            f"{fmt(item['p95_vs_no_load_pct'], 1)}% | "
            f"{fmt(item['rate_limit_active_pct'], 1)}% | "
            f"{fmt(action_delta.get('p95'))} | "
            f"{fmt(tracking.get('p95'))} | "
            f"{fmt(lag.get('ticks'), 0)} | "
            f"{fmt(lag.get('ms'), 1)} | "
            f"{fmt(item['action_saturation_pct'], 2)} |"
        )
    lines.append("")

    lines.append("## Detailed Joint Metrics")
    lines.append("")
    for item in results:
        lines.append(f"### {item['joint']}")
        lines.append("")
        lines.append(
            "| metric | p50 | p95 | p99 | max |"
        )
        lines.append("|---|---:|---:|---:|---:|")
        for label, key in [
            ("target step sent rad/tick", "sent_step"),
            ("target velocity sent rad/s", "sent_velocity"),
            ("pre-rate-limit target velocity rad/s", "pre_velocity"),
            ("action delta per tick", "action_delta"),
            ("tracking error abs rad", "tracking"),
        ]:
            summary = item[key] or {}
            lines.append(
                f"| {label} | {fmt(summary.get('p50'))} | {fmt(summary.get('p95'))} | "
                f"{fmt(summary.get('p99'))} | {fmt(summary.get('max'))} |"
            )
        lines.append("")
        lines.append(f"- rate_limit_active_pct: `{fmt(item['rate_limit_active_pct'], 2)}`")
        lines.append(f"- rate_limit_delta_max_rad: `{fmt(item['rate_limit_delta_max'])}`")
        if item["lag"]:
            lines.append(
                f"- best_lag: `{item['lag']['ticks']} ticks`, "
                f"`{fmt(item['lag'].get('ms'), 1)} ms`, rmse `{fmt(item['lag']['rmse'])}`"
            )
        else:
            lines.append("- best_lag: `NA`")
        lines.append("")

    lines.append("## Interpretation")
    lines.append("")
    high_velocity = [
        item
        for item in results
        if item["p95_vs_no_load_pct"] is not None and item["p95_vs_no_load_pct"] > 75
    ]
    if high_velocity:
        lines.append(
            "- At least one joint has p95 sent target velocity above 75% of the "
            "ST3215 no-load speed reference."
        )
    if any((item["rate_limit_active_pct"] or 0) > 0 for item in results):
        lines.append("- Runtime rate limiting is active on at least one analyzed joint.")
    if any((item["action_saturation_pct"] or 0) > 0 for item in results):
        lines.append("- ONNX action saturation appears on at least one analyzed joint.")
    lines.append(
        "- Compare these target velocities against actuator sine sweep velocities "
        "before attributing tracking error to ground contact."
    )
    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze policy target velocity and target-vs-actual lag from telemetry JSONL."
    )
    parser.add_argument("telemetry_jsonl")
    parser.add_argument("--output", default=None)
    parser.add_argument("--startup-ticks", type=int, default=25)
    parser.add_argument("--max-lag-ticks", type=int, default=12)
    parser.add_argument("--servo-no-load-rad-s", type=float, default=4.72)
    parser.add_argument("--joints", nargs="+", default=PITCH_CHAIN_JOINTS)
    args = parser.parse_args()

    records = load_records(args.telemetry_jsonl, args.startup_ticks)
    report = build_report(args, records)
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, "w") as f:
            f.write(report)
            f.write("\n")
    print(report)


if __name__ == "__main__":
    main()
