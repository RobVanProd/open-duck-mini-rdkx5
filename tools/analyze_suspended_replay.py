#!/usr/bin/env python3
import argparse
import json
import math
import statistics
from pathlib import Path

from analyze_runtime_warnings import parse_terminal_log


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

PITCH_JOINTS = [
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
    values = sorted(float(v) for v in values if finite(v))
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


def fmt(value, digits=4):
    if value is None:
        return "NA"
    return f"{value:.{digits}f}"


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
                print(f"Skipping invalid JSON line {line_no}: {exc}")
    return records


def vector_values(records, group, field):
    per_joint = [[] for _ in JOINT_NAMES]
    for record in records:
        vector = record.get(group, {}).get(field)
        if not vector:
            continue
        for index, value in enumerate(vector[: len(JOINT_NAMES)]):
            if finite(value):
                per_joint[index].append(float(value))
    return per_joint


def vector_stats(records, group, field, absolute=False):
    output = []
    for values in vector_values(records, group, field):
        if absolute:
            values = [abs(value) for value in values]
        output.append(stats(values))
    return output


def action_saturation(records, threshold=0.98):
    per_joint = vector_values(records, "action", "onnx_action")
    result = []
    for values in per_joint:
        if not values:
            result.append(None)
            continue
        result.append(sum(abs(value) >= threshold for value in values) / len(values) * 100)
    return result


def observation_stats(records, start, end):
    columns = [[] for _ in range(end - start)]
    for record in records:
        obs = record.get("observation", {}).get("raw_vector")
        if not obs or len(obs) < end:
            continue
        for offset, index in enumerate(range(start, end)):
            if finite(obs[index]):
                columns[offset].append(float(obs[index]))
    return [stats(values) for values in columns]


def dt_stats(records, threshold):
    values = []
    spikes = []
    for record in records:
        dt_s = record.get("dt_s")
        if not finite(dt_s):
            continue
        dt_s = float(dt_s)
        values.append(dt_s)
        if dt_s > threshold:
            spikes.append(record)
    return stats(values), spikes


def tracking_stats_and_spikes(records, threshold):
    per_joint = [[] for _ in JOINT_NAMES]
    largest = None
    spikes = []
    for record in records:
        errors = record.get("joints", {}).get("tracking_error_rad")
        if not errors:
            continue
        for index, value in enumerate(errors[: len(JOINT_NAMES)]):
            if not finite(value):
                continue
            abs_value = abs(float(value))
            per_joint[index].append(abs_value)
            item = {
                "tick": record.get("tick"),
                "timestamp_monotonic_s": record.get("timestamp_monotonic_s"),
                "joint": JOINT_NAMES[index],
                "abs_error_rad": abs_value,
            }
            if largest is None or abs_value > largest["abs_error_rad"]:
                largest = item
            if abs_value > threshold:
                spikes.append(item)
    return [stats(values) for values in per_joint], largest, spikes


def consecutive_step_stats(records, group, field):
    per_joint = [[] for _ in JOINT_NAMES]
    previous = None
    for record in records:
        vector = record.get(group, {}).get(field)
        if not vector:
            continue
        if previous is not None:
            for index, (before, after) in enumerate(
                zip(previous[: len(JOINT_NAMES)], vector[: len(JOINT_NAMES)])
            ):
                if finite(before) and finite(after):
                    per_joint[index].append(abs(float(after) - float(before)))
        previous = vector
    return [stats(values) for values in per_joint]


def within_tick_delta_stats(records, group, before_field, after_field):
    per_joint = [[] for _ in JOINT_NAMES]
    for record in records:
        before = record.get(group, {}).get(before_field)
        after = record.get(group, {}).get(after_field)
        if not before or not after:
            continue
        for index, (left, right) in enumerate(
            zip(before[: len(JOINT_NAMES)], after[: len(JOINT_NAMES)])
        ):
            if finite(left) and finite(right):
                per_joint[index].append(abs(float(right) - float(left)))
    return [stats(values) for values in per_joint]


def command_summary(records):
    vectors = []
    for record in records:
        commands = record.get("control", {}).get("commands")
        if commands:
            vectors.append([float(value) for value in commands])
    if not vectors:
        return None
    max_abs = max(max(abs(value) for value in vector) for vector in vectors)
    return {
        "first": vectors[0],
        "last": vectors[-1],
        "max_abs": max_abs,
        "unique_count": len({tuple(vector) for vector in vectors}),
    }


def bus_summary(records):
    keys = ["read_error_count", "write_error_count"]
    output = {"status": "unavailable", "last_error": None}
    for key in keys:
        values = [
            record.get("bus", {}).get(key)
            for record in records
            if finite(record.get("bus", {}).get(key))
        ]
        output[key] = None if not values else max(int(value) for value in values)
    last_errors = [
        record.get("bus", {}).get("last_error")
        for record in records
        if record.get("bus", {}).get("last_error")
    ]
    if output["read_error_count"] is not None or output["write_error_count"] is not None:
        output["status"] = "available"
    if last_errors:
        output["last_error"] = last_errors[-1]
    return output


def warning_total(terminal):
    non_cleanup = [
        name
        for name in terminal["counts"]
        if name not in {"motor_off_cleanup"}
    ]
    return sum(terminal["counts"][name] for name in non_cleanup)


def gate_recommendation(
    *,
    records,
    terminal,
    dt_spikes,
    tracking_spikes,
    tracking_stats,
    accel_stats,
    action_saturation_pct,
    bus,
):
    if not records:
        return "HOLD_TRACKING", "no telemetry samples"
    if terminal["missing"]:
        return "HOLD_CRC_OR_TIMING", "terminal log missing; CRC/control warnings unknown"
    if warning_total(terminal) > 0:
        return "HOLD_CRC_OR_TIMING", "terminal warnings detected"
    if dt_spikes:
        return "HOLD_CRC_OR_TIMING", "dt spike above threshold"
    if bus.get("read_error_count") or bus.get("write_error_count") or bus.get("last_error"):
        return "HOLD_CRC_OR_TIMING", "bus error counters reported activity"
    if any(pct is not None and pct > 0 for pct in action_saturation_pct):
        return "HOLD_ACTION_SATURATION", "at least one action reached saturation"
    if accel_stats and len(accel_stats) == 3 and all(accel_stats):
        means = [item["mean"] for item in accel_stats]
        if abs(means[2]) < abs(means[0]) or abs(means[2]) < abs(means[1]) or means[2] < 0:
            return "HOLD_IMU", "accelerometer is not +Z dominant"
    severe_tracking = [
        item for item in tracking_stats if item and item.get("p95") and item["p95"] > 0.05
    ]
    if severe_tracking:
        return "HOLD_TRACKING", "tracking p95 above threshold"
    if tracking_spikes:
        return "HOLD_TRACKING", "tracking spike above threshold without timing explanation"
    return "PASS_X0", "zero-command suspended replay gate passed"


def first_policy(records):
    return records[0].get("policy", {}) if records else {}


def build_report(args, records, terminal):
    command = command_summary(records)
    policy = first_policy(records)
    dt, dt_spikes = dt_stats(records, args.dt_spike_threshold)
    tracking, largest_tracking, tracking_spikes = tracking_stats_and_spikes(
        records, args.tracking_spike_threshold
    )
    accel = observation_stats(records, 3, 6)
    action = vector_stats(records, "action", "onnx_action")
    scaled_delta = vector_stats(records, "action", "scaled_delta_rad")
    sent_targets = vector_stats(records, "action", "motor_targets_sent_rad")
    action_sat = action_saturation(records)
    pre_steps = consecutive_step_stats(records, "action", "motor_targets_pre_rate_limit_rad")
    post_steps = consecutive_step_stats(records, "action", "motor_targets_post_rate_limit_rad")
    rate_limit_delta = within_tick_delta_stats(
        records,
        "action",
        "motor_targets_pre_rate_limit_rad",
        "motor_targets_post_rate_limit_rad",
    )
    bus = bus_summary(records)
    gate, reason = gate_recommendation(
        records=records,
        terminal=terminal,
        dt_spikes=dt_spikes,
        tracking_spikes=tracking_spikes,
        tracking_stats=tracking,
        accel_stats=accel,
        action_saturation_pct=action_sat,
        bus=bus,
    )

    lines = ["# Suspended Replay Gate Analysis", ""]
    lines.append(f"telemetry_jsonl: `{args.telemetry_jsonl}`")
    lines.append(f"terminal_log: `{terminal['path'] or 'MISSING'}`")
    lines.append(f"samples: `{len(records)}`")
    lines.append(f"gate_recommendation: `{gate}`")
    lines.append(f"gate_reason: `{reason}`")
    lines.append("")

    lines.append("## Policy And Command")
    lines.append("")
    lines.append(f"policy_hash: `{policy.get('onnx_sha256')}`")
    lines.append(f"input_name: `{policy.get('input_name')}`")
    lines.append(f"output_name: `{policy.get('output_name')}`")
    if command:
        lines.append(f"command_first: `{command['first']}`")
        lines.append(f"command_last: `{command['last']}`")
        lines.append(f"command_unique_count: `{command['unique_count']}`")
        lines.append(f"command_max_abs: `{fmt(command['max_abs'])}`")

    lines.append("")
    lines.append("## Terminal Warnings")
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
        lines.append("terminal_timestamp_status: `present`")
    else:
        lines.append("")
        lines.append("terminal_timestamp_status: `not present; correlation is limited`")

    lines.append("")
    lines.append("## Timing")
    lines.append("")
    lines.append(f"dt_mean_s: {fmt(None if not dt else dt['mean'], 5)}")
    lines.append(f"dt_p95_s: {fmt(None if not dt else dt['p95'], 5)}")
    lines.append(f"dt_p99_s: {fmt(None if not dt else dt['p99'], 5)}")
    lines.append(f"dt_max_s: {fmt(None if not dt else dt['max'], 5)}")
    lines.append(f"dt_spikes_gt_{args.dt_spike_threshold}_s: `{len(dt_spikes)}`")
    for record in dt_spikes[:10]:
        lines.append(
            f"- tick `{record.get('tick')}` t=`{fmt(record.get('timestamp_monotonic_s'), 5)}` "
            f"dt_s=`{fmt(record.get('dt_s'), 5)}`"
        )

    lines.append("")
    lines.append("## Accel Obs[3:6]")
    lines.append("")
    lines.append("| axis | mean | std | min | max |")
    lines.append("|---|---:|---:|---:|---:|")
    for axis, summary in zip(["accel_x", "accel_y", "accel_z"], accel):
        lines.append(
            f"| {axis} | {fmt(None if not summary else summary['mean'])} | "
            f"{fmt(None if not summary else summary['std'])} | "
            f"{fmt(None if not summary else summary['min'])} | "
            f"{fmt(None if not summary else summary['max'])} |"
        )

    lines.append("")
    lines.append("## Action Stats")
    lines.append("")
    lines.append("| joint | action_mean | action_min | action_max | saturation_pct |")
    lines.append("|---|---:|---:|---:|---:|")
    for index, summary in enumerate(action):
        lines.append(
            f"| {JOINT_NAMES[index]} | {fmt(None if not summary else summary['mean'])} | "
            f"{fmt(None if not summary else summary['min'])} | "
            f"{fmt(None if not summary else summary['max'])} | "
            f"{fmt(action_sat[index], 2)} |"
        )

    lines.append("")
    lines.append("## Tracking Error")
    lines.append("")
    lines.append("| joint | p50_abs_rad | p95_abs_rad | p99_abs_rad | max_abs_rad |")
    lines.append("|---|---:|---:|---:|---:|")
    for index, summary in enumerate(tracking):
        lines.append(
            f"| {JOINT_NAMES[index]} | {fmt(None if not summary else summary['p50'])} | "
            f"{fmt(None if not summary else summary['p95'])} | "
            f"{fmt(None if not summary else summary['p99'])} | "
            f"{fmt(None if not summary else summary['max'])} |"
        )
    lines.append("")
    if largest_tracking:
        lines.append(
            "largest_tracking_spike: "
            f"tick `{largest_tracking['tick']}`, "
            f"t=`{fmt(largest_tracking['timestamp_monotonic_s'], 5)}`, "
            f"joint `{largest_tracking['joint']}`, "
            f"abs_error_rad=`{fmt(largest_tracking['abs_error_rad'])}`"
        )
        if dt_spikes:
            nearest = min(
                dt_spikes,
                key=lambda record: abs(
                    int(record.get("tick", 0)) - int(largest_tracking["tick"] or 0)
                ),
            )
            delta_ticks = abs(
                int(nearest.get("tick", 0)) - int(largest_tracking["tick"] or 0)
            )
            lines.append(
                "nearest_dt_spike_to_largest_tracking: "
                f"tick `{nearest.get('tick')}`, "
                f"delta_ticks=`{delta_ticks}`, "
                f"dt_s=`{fmt(nearest.get('dt_s'), 5)}`"
            )
        else:
            lines.append("nearest_dt_spike_to_largest_tracking: `NONE`")
    else:
        lines.append("largest_tracking_spike: `NONE`")
    lines.append(
        f"tracking_spikes_gt_{args.tracking_spike_threshold}_rad: `{len(tracking_spikes)}`"
    )
    for spike in sorted(
        tracking_spikes, key=lambda item: item["abs_error_rad"], reverse=True
    )[:10]:
        lines.append(
            f"- tick `{spike['tick']}` t=`{fmt(spike['timestamp_monotonic_s'], 5)}` "
            f"joint `{spike['joint']}` abs_error_rad=`{fmt(spike['abs_error_rad'])}`"
        )

    lines.append("")
    lines.append("## Target Step And Rate Limit")
    lines.append("")
    lines.append(
        "| joint | pre_step_max_rad | post_step_max_rad | pre_to_post_delta_max_rad |"
    )
    lines.append("|---|---:|---:|---:|")
    for index in range(len(JOINT_NAMES)):
        lines.append(
            f"| {JOINT_NAMES[index]} | "
            f"{fmt(None if not pre_steps[index] else pre_steps[index]['max'])} | "
            f"{fmt(None if not post_steps[index] else post_steps[index]['max'])} | "
            f"{fmt(None if not rate_limit_delta[index] else rate_limit_delta[index]['max'])} |"
        )

    lines.append("")
    lines.append("## Pitch Posture Numeric Summary")
    lines.append("")
    lines.append(
        "Sign-to-physical-forward cannot be inferred from telemetry alone; use joint identity visual notes for direction."
    )
    lines.append("")
    lines.append("| joint | scaled_delta_mean_rad | sent_target_mean_rad | sent_min | sent_max |")
    lines.append("|---|---:|---:|---:|---:|")
    for joint in PITCH_JOINTS:
        index = JOINT_NAMES.index(joint)
        delta = scaled_delta[index]
        sent = sent_targets[index]
        lines.append(
            f"| {joint} | {fmt(None if not delta else delta['mean'])} | "
            f"{fmt(None if not sent else sent['mean'])} | "
            f"{fmt(None if not sent else sent['min'])} | "
            f"{fmt(None if not sent else sent['max'])} |"
        )

    lines.append("")
    lines.append("## Bus Counters")
    lines.append("")
    lines.append(f"bus_status: `{bus['status']}`")
    lines.append(f"read_error_count_max: `{bus['read_error_count']}`")
    lines.append(f"write_error_count_max: `{bus['write_error_count']}`")
    lines.append(f"last_error: `{bus['last_error']}`")
    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Create a suspended policy replay gate summary."
    )
    parser.add_argument("telemetry_jsonl")
    parser.add_argument("--terminal-log", default=None)
    parser.add_argument("--output", default=None)
    parser.add_argument("--dt-spike-threshold", type=float, default=0.04)
    parser.add_argument("--tracking-spike-threshold", type=float, default=0.05)
    args = parser.parse_args()

    records = load_records(args.telemetry_jsonl)
    terminal = parse_terminal_log(args.terminal_log)
    report = build_report(args, records, terminal)

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, "w") as f:
            f.write(report)
            f.write("\n")
    print(report)


if __name__ == "__main__":
    main()
