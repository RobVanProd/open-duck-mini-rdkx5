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

STARTUP_TICKS = 25
CORRELATION_WINDOW_TICKS = 2
BUS_BURST_MIN_EVENTS = 3
BUS_BURST_WINDOW_TICKS = 3
READ_ERROR_GREEN_RATE = 0.002
READ_ERROR_RED_RATE = 0.02
DT_YELLOW_S = 0.03
DT_RED_S = 0.05
P95_TRACKING_YELLOW_RAD = 0.02
P95_TRACKING_RED_RAD = 0.05
MAX_TRACKING_RED_RAD = 0.15
ACTION_SATURATION_YELLOW_PCT = 0.0
ACTION_SATURATION_RED_PCT = 1.0


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


def as_tick(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def bus_counter_events(records):
    events = []
    previous = {"read_error_count": None, "write_error_count": None}
    names = {
        "read_error_count": "read",
        "write_error_count": "write",
    }
    for record in records:
        bus = record.get("bus", {})
        for key, op in names.items():
            value = bus.get(key)
            if not finite(value):
                continue
            value = int(value)
            prior = previous[key]
            if prior is not None and value > prior:
                delta = value - prior
                for _ in range(delta):
                    events.append(
                        {
                            "tick": as_tick(record.get("tick")),
                            "timestamp_monotonic_s": record.get("timestamp_monotonic_s"),
                            "op": op,
                            "last_error": bus.get("last_error"),
                        }
                    )
            previous[key] = value
    return events


def bus_bursts(events, *, op="read"):
    ticks = sorted(
        event["tick"] for event in events if event["op"] == op and event["tick"] is not None
    )
    bursts = []
    for index in range(0, len(ticks) - BUS_BURST_MIN_EVENTS + 1):
        window = ticks[index : index + BUS_BURST_MIN_EVENTS]
        if window[-1] - window[0] <= BUS_BURST_WINDOW_TICKS:
            bursts.append(window)
    return bursts


def items_after_startup(items):
    return [
        item
        for item in items
        if item.get("tick") is not None and int(item["tick"]) > STARTUP_TICKS
    ]


def items_within_ticks(left_items, right_items, window):
    pairs = []
    for left in left_items:
        left_tick = left.get("tick")
        if left_tick is None:
            continue
        for right in right_items:
            right_tick = right.get("tick")
            if right_tick is None:
                continue
            if abs(int(left_tick) - int(right_tick)) <= window:
                pairs.append((left, right))
    return pairs


def count_terminal_patterns(terminal, names):
    return sum(terminal["counts"].get(name, 0) for name in names)


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
    dt_summary,
    dt_spikes,
    tracking_spikes,
    tracking_stats,
    accel_stats,
    action_saturation_pct,
    bus,
):
    holds = []
    warnings = []
    metrics = {
        "read_error_rate": None,
        "bus_event_count": 0,
        "bus_read_burst_count": 0,
        "bus_write_burst_count": 0,
        "post_startup_tracking_spikes": 0,
        "startup_tracking_spikes": 0,
        "dt_gt_0_03_count": 0,
        "dt_gt_0_05_count": 0,
    }

    if not records:
        return {
            "gate": "HOLD_TRACKING",
            "reason": "no telemetry samples",
            "holds": ["no telemetry samples"],
            "warnings": [],
            "metrics": metrics,
        }

    if terminal["missing"]:
        warnings.append("terminal log missing; CRC/control warnings cannot be reviewed")

    bus_events = bus_counter_events(records)
    metrics["bus_event_count"] = len(bus_events)
    read_bursts = bus_bursts(bus_events, op="read")
    write_bursts = bus_bursts(bus_events, op="write")
    metrics["bus_read_burst_count"] = len(read_bursts)
    metrics["bus_write_burst_count"] = len(write_bursts)

    terminal_crc_count = max(
        terminal["counts"].get("crc_mismatch", 0),
        terminal["counts"].get("read_crc", 0) + terminal["counts"].get("write_crc", 0),
    )
    terminal_read_write_errors = count_terminal_patterns(
        terminal, ["read_error", "write_error", "timeout"]
    )
    terminal_control_budget = terminal["counts"].get("control_budget_exceeded", 0)
    terminal_exceptions = terminal["counts"].get("exception_or_traceback", 0)

    read_count = bus.get("read_error_count")
    write_count = bus.get("write_error_count")
    observed_read_count = read_count if read_count is not None else terminal_crc_count
    if observed_read_count is not None:
        read_rate = observed_read_count / len(records)
        metrics["read_error_rate"] = read_rate
        if read_rate > READ_ERROR_RED_RATE:
            holds.append(
                f"read retry/error rate {read_rate * 100:.2f}% exceeds red threshold"
            )
        elif read_rate > READ_ERROR_GREEN_RATE:
            warnings.append(
                f"read retry/error rate {read_rate * 100:.2f}% is yellow; continue only if uncorrelated"
            )

    if write_count is not None and write_count > 1:
        holds.append(f"repeated write errors reported by bus counter: {write_count}")
    elif write_count:
        warnings.append(f"single write error reported by bus counter: {write_count}")

    if read_bursts:
        holds.append(
            f"read retry/error burst detected: {read_bursts[0]} within {BUS_BURST_WINDOW_TICKS} ticks"
        )
    if write_bursts:
        holds.append(
            f"write retry/error burst detected: {write_bursts[0]} within {BUS_BURST_WINDOW_TICKS} ticks"
        )

    if terminal_crc_count:
        warnings.append(f"terminal CRC/read checksum warnings observed: {terminal_crc_count}")
        if bus["status"] == "unavailable":
            warnings.append("bus counters unavailable; warning-to-tick correlation is limited")
    if terminal_read_write_errors:
        warnings.append(f"terminal read/write/timeout warnings observed: {terminal_read_write_errors}")
    if terminal_control_budget > 1:
        holds.append(f"repeated control budget warnings: {terminal_control_budget}")
    elif terminal_control_budget == 1:
        warnings.append("one isolated control budget warning")
    if terminal_exceptions:
        holds.append(f"terminal exception/traceback lines observed: {terminal_exceptions}")

    dt_gt_0_03 = [
        record
        for record in records
        if finite(record.get("dt_s")) and float(record["dt_s"]) > DT_YELLOW_S
    ]
    dt_gt_0_05 = [
        record
        for record in records
        if finite(record.get("dt_s")) and float(record["dt_s"]) > DT_RED_S
    ]
    metrics["dt_gt_0_03_count"] = len(dt_gt_0_03)
    metrics["dt_gt_0_05_count"] = len(dt_gt_0_05)
    if dt_gt_0_05:
        holds.append(f"dt exceeded {DT_RED_S:.3f}s")
    elif len(dt_gt_0_03) > 1:
        holds.append(f"repeated dt above {DT_YELLOW_S:.3f}s")
    elif dt_gt_0_03:
        warnings.append(f"one isolated dt above {DT_YELLOW_S:.3f}s")
    elif dt_spikes:
        warnings.append("dt exceeded configured warning threshold")

    if bus_events and dt_gt_0_03:
        pairs = items_within_ticks(bus_events, dt_gt_0_03, CORRELATION_WINDOW_TICKS)
        if pairs:
            holds.append("bus event correlates with dt spike")

    saturated_joints = [pct for pct in action_saturation_pct if pct is not None and pct > 0]
    if any(pct > ACTION_SATURATION_RED_PCT for pct in saturated_joints) or len(saturated_joints) > 1:
        holds.append("action saturation is sustained or appears on multiple joints")
    elif saturated_joints:
        warnings.append("isolated action saturation below red threshold")

    if accel_stats and len(accel_stats) == 3 and all(accel_stats):
        means = [item["mean"] for item in accel_stats]
        if abs(means[2]) < abs(means[0]) or abs(means[2]) < abs(means[1]) or means[2] < 0:
            holds.append("accelerometer is not +Z dominant")

    severe_tracking = [
        item
        for item in tracking_stats
        if item and item.get("p95") and item["p95"] > P95_TRACKING_RED_RAD
    ]
    if severe_tracking:
        holds.append(f"tracking p95 above {P95_TRACKING_RED_RAD:.2f} rad")

    yellow_tracking = [
        item
        for item in tracking_stats
        if item and item.get("p95") and item["p95"] > P95_TRACKING_YELLOW_RAD
    ]
    if yellow_tracking:
        warnings.append(f"tracking p95 above {P95_TRACKING_YELLOW_RAD:.2f} rad on at least one joint")

    post_startup_spikes = items_after_startup(tracking_spikes)
    startup_spikes = [item for item in tracking_spikes if item not in post_startup_spikes]
    metrics["post_startup_tracking_spikes"] = len(post_startup_spikes)
    metrics["startup_tracking_spikes"] = len(startup_spikes)
    large_post_startup = [
        item for item in post_startup_spikes if item["abs_error_rad"] > MAX_TRACKING_RED_RAD
    ]
    if large_post_startup:
        holds.append(f"steady-state tracking spike above {MAX_TRACKING_RED_RAD:.2f} rad")
    elif post_startup_spikes:
        warnings.append("post-startup tracking spikes present but below red max threshold")

    large_startup = [
        item for item in startup_spikes if item["abs_error_rad"] > MAX_TRACKING_RED_RAD
    ]
    if large_startup:
        warnings.append(
            f"startup-only tracking spike above {MAX_TRACKING_RED_RAD:.2f} rad; review but do not block by itself"
        )

    if bus_events and post_startup_spikes:
        pairs = items_within_ticks(bus_events, post_startup_spikes, CORRELATION_WINDOW_TICKS)
        if pairs:
            holds.append("bus event correlates with post-startup tracking spike")

    if holds:
        if any("accelerometer" in item for item in holds):
            gate = "HOLD_IMU"
        elif any("action" in item for item in holds):
            gate = "HOLD_ACTION_SATURATION"
        elif any("tracking" in item for item in holds):
            gate = "HOLD_TRACKING"
        else:
            gate = "HOLD_CRC_OR_TIMING"
        return {
            "gate": gate,
            "reason": holds[0],
            "holds": holds,
            "warnings": warnings,
            "metrics": metrics,
        }

    if warnings:
        return {
            "gate": "WARN_PROCEED_WITH_CAUTION",
            "reason": warnings[0],
            "holds": [],
            "warnings": warnings,
            "metrics": metrics,
        }

    return {
        "gate": "PASS_X0",
        "reason": "suspended replay gate passed under threshold policy",
        "holds": [],
        "warnings": [],
        "metrics": metrics,
    }


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
    gate = gate_recommendation(
        records=records,
        terminal=terminal,
        dt_summary=dt,
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
    lines.append(f"gate_recommendation: `{gate['gate']}`")
    lines.append(f"gate_reason: `{gate['reason']}`")
    lines.append("")

    lines.append("## Stop/Go Threshold Status")
    lines.append("")
    lines.append(
        "Nonzero CRC/read retries are warnings unless they correlate with control damage: "
        "dt spikes, action saturation/jumps, post-startup tracking spikes, write failures, "
        "or visible operator-reported twitching."
    )
    lines.append("")
    lines.append(f"read_error_rate_pct: `{fmt(None if gate['metrics']['read_error_rate'] is None else gate['metrics']['read_error_rate'] * 100, 3)}`")
    lines.append(f"bus_event_count: `{gate['metrics']['bus_event_count']}`")
    lines.append(f"bus_read_burst_count: `{gate['metrics']['bus_read_burst_count']}`")
    lines.append(f"bus_write_burst_count: `{gate['metrics']['bus_write_burst_count']}`")
    lines.append(f"dt_gt_0_030_s_count: `{gate['metrics']['dt_gt_0_03_count']}`")
    lines.append(f"dt_gt_0_050_s_count: `{gate['metrics']['dt_gt_0_05_count']}`")
    lines.append(f"startup_tracking_spikes_gt_{args.tracking_spike_threshold}_rad: `{gate['metrics']['startup_tracking_spikes']}`")
    lines.append(f"post_startup_tracking_spikes_gt_{args.tracking_spike_threshold}_rad: `{gate['metrics']['post_startup_tracking_spikes']}`")
    lines.append("")
    lines.append("holds:")
    if gate["holds"]:
        for item in gate["holds"]:
            lines.append(f"- {item}")
    else:
        lines.append("- NONE")
    lines.append("")
    lines.append("warnings:")
    if gate["warnings"]:
        for item in gate["warnings"]:
            lines.append(f"- {item}")
    else:
        lines.append("- NONE")
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
