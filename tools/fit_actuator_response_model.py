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


def grid(start, stop, step):
    values = []
    value = start
    while value <= stop + step / 10.0:
        values.append(round(value, 10))
        value += step
    return values


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


def record_dt(prev, cur):
    dt_s = cur.get("dt_s")
    if finite(dt_s) and float(dt_s) > 0:
        return float(dt_s)
    prev_t = prev.get("timestamp_monotonic_s")
    cur_t = cur.get("timestamp_monotonic_s")
    if finite(prev_t) and finite(cur_t) and float(cur_t) > float(prev_t):
        return float(cur_t) - float(prev_t)
    return None


def vector(record, group, field):
    values = record.get(group, {}).get(field)
    if not values:
        return None
    return values


def joint_series(records, joint_name):
    joint_index = JOINT_NAMES.index(joint_name)
    samples = []
    previous_record = None
    for record in records:
        target = vector(record, "action", "motor_targets_sent_rad")
        if target is None:
            target = record.get("joints", {}).get("commanded_position_rad")
        actual = record.get("joints", {}).get("actual_position_rad")
        if target is None or actual is None:
            previous_record = record
            continue
        if len(target) <= joint_index or len(actual) <= joint_index:
            previous_record = record
            continue
        if not finite(target[joint_index]) or not finite(actual[joint_index]):
            previous_record = record
            continue
        dt_s = None if previous_record is None else record_dt(previous_record, record)
        samples.append(
            {
                "tick": record.get("tick"),
                "time": record.get("timestamp_monotonic_s"),
                "dt_s": dt_s,
                "target": float(target[joint_index]),
                "actual": float(actual[joint_index]),
            }
        )
        previous_record = record
    median_dt = median_dt_s(samples)
    for sample in samples:
        if not sample["dt_s"]:
            sample["dt_s"] = median_dt
    return samples


def median_dt_s(samples):
    values = [sample["dt_s"] for sample in samples if finite(sample.get("dt_s")) and sample["dt_s"] > 0]
    if values:
        return statistics.median(values)
    times = [sample["time"] for sample in samples if finite(sample.get("time"))]
    values = [
        float(right) - float(left)
        for left, right in zip(times, times[1:])
        if float(right) > float(left)
    ]
    if values:
        return statistics.median(values)
    return 0.02


def delayed_target(targets, index, delay_ticks):
    return targets[max(0, index - delay_ticks)]


def clip(value, lower, upper):
    return max(lower, min(upper, value))


def simulate_combined(samples, delay_ticks, tau_s, velocity_limit_rad_s):
    if not samples:
        return []
    targets = [sample["target"] for sample in samples]
    y = samples[0]["actual"]
    output = []
    for index, sample in enumerate(samples):
        dt_s = sample["dt_s"] or 0.02
        target = delayed_target(targets, index, delay_ticks)
        alpha = 1.0 - math.exp(-dt_s / tau_s)
        desired_step = alpha * (target - y)
        max_step = velocity_limit_rad_s * dt_s
        y += clip(desired_step, -max_step, max_step)
        output.append(y)
    return output


def simulate_delay_only(samples, delay_ticks):
    targets = [sample["target"] for sample in samples]
    return [delayed_target(targets, index, delay_ticks) for index in range(len(samples))]


def simulate_first_order_only(samples, tau_s):
    if not samples:
        return []
    y = samples[0]["actual"]
    output = []
    for sample in samples:
        dt_s = sample["dt_s"] or 0.02
        alpha = 1.0 - math.exp(-dt_s / tau_s)
        y += alpha * (sample["target"] - y)
        output.append(y)
    return output


def simulate_velocity_only(samples, velocity_limit_rad_s):
    if not samples:
        return []
    y = samples[0]["actual"]
    output = []
    for sample in samples:
        dt_s = sample["dt_s"] or 0.02
        max_step = velocity_limit_rad_s * dt_s
        y += clip(sample["target"] - y, -max_step, max_step)
        output.append(y)
    return output


def error_metrics(samples, predicted):
    if not samples or not predicted:
        return None
    errors = [float(sample["actual"]) - float(value) for sample, value in zip(samples, predicted)]
    abs_errors = [abs(value) for value in errors]
    sorted_abs = sorted(abs_errors)
    trim_count = max(1, int(math.ceil(len(sorted_abs) * 0.95)))
    trimmed_errors = sorted_abs[:trim_count]
    rmse = math.sqrt(sum(value * value for value in errors) / len(errors))
    return {
        "rmse": rmse,
        "mae": sum(abs_errors) / len(abs_errors),
        "trimmed_rmse_95": math.sqrt(
            sum(value * value for value in trimmed_errors) / len(trimmed_errors)
        ),
        "p95_abs_error": percentile(abs_errors, 95),
        "p99_abs_error": percentile(abs_errors, 99),
        "max_abs_error": max(abs_errors),
    }


def selection_score(metrics, selection_metric):
    if selection_metric == "rmse":
        return metrics["rmse"]
    if selection_metric == "trimmed_rmse_95":
        return metrics["trimmed_rmse_95"]
    if selection_metric == "p95_abs_error":
        return metrics["p95_abs_error"]
    if selection_metric == "mae":
        return metrics["mae"]
    raise ValueError(f"unknown selection metric: {selection_metric}")


def fit_delay_only(samples, delay_values, selection_metric):
    best = None
    for delay in delay_values:
        metrics = error_metrics(samples, simulate_delay_only(samples, delay))
        if metrics and (
            best is None
            or selection_score(metrics, selection_metric) < best["selection_score"]
        ):
            best = {
                "delay_ticks": delay,
                "selection_metric": selection_metric,
                "selection_score": selection_score(metrics, selection_metric),
                **metrics,
            }
    return best


def fit_first_order_only(samples, tau_values, selection_metric):
    best = None
    for tau_s in tau_values:
        metrics = error_metrics(samples, simulate_first_order_only(samples, tau_s))
        if metrics and (
            best is None
            or selection_score(metrics, selection_metric) < best["selection_score"]
        ):
            best = {
                "tau_s": tau_s,
                "selection_metric": selection_metric,
                "selection_score": selection_score(metrics, selection_metric),
                **metrics,
            }
    return best


def fit_velocity_only(samples, velocity_values, selection_metric):
    best = None
    for velocity in velocity_values:
        metrics = error_metrics(samples, simulate_velocity_only(samples, velocity))
        if metrics and (
            best is None
            or selection_score(metrics, selection_metric) < best["selection_score"]
        ):
            best = {
                "velocity_limit_rad_s": velocity,
                "selection_metric": selection_metric,
                "selection_score": selection_score(metrics, selection_metric),
                **metrics,
            }
    return best


def fit_combined(samples, delay_values, tau_values, velocity_values, selection_metric):
    best = None
    for delay in delay_values:
        for tau_s in tau_values:
            for velocity in velocity_values:
                predicted = simulate_combined(samples, delay, tau_s, velocity)
                metrics = error_metrics(samples, predicted)
                if metrics and (
                    best is None
                    or selection_score(metrics, selection_metric) < best["selection_score"]
                ):
                    best = {
                        "delay_ticks": delay,
                        "tau_s": tau_s,
                        "velocity_limit_rad_s": velocity,
                        "selection_metric": selection_metric,
                        "selection_score": selection_score(metrics, selection_metric),
                        **metrics,
                    }
    return best


def series_stats(samples):
    targets = [sample["target"] for sample in samples]
    actuals = [sample["actual"] for sample in samples]
    target_vel = []
    actual_vel = []
    for before, after in zip(samples, samples[1:]):
        dt_s = after["dt_s"] or 0.02
        if dt_s <= 0:
            continue
        target_vel.append(abs(after["target"] - before["target"]) / dt_s)
        actual_vel.append(abs(after["actual"] - before["actual"]) / dt_s)
    target_range = max(targets) - min(targets) if targets else None
    actual_range = max(actuals) - min(actuals) if actuals else None
    return {
        "samples": len(samples),
        "target_range": target_range,
        "actual_range": actual_range,
        "amplitude_ratio": None
        if not target_range
        else (actual_range / target_range if actual_range is not None else None),
        "sent_target_velocity": stats(target_vel),
        "actual_velocity": stats(actual_vel),
    }


def cross_correlation_lag(samples, max_lag_ticks):
    if not samples:
        return None
    target = [sample["target"] for sample in samples]
    actual = [sample["actual"] for sample in samples]
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
            best = {"lag_ticks": lag, "rmse": rmse, "samples": len(pairs)}
    if best is not None:
        dt_s = median_dt_s(samples)
        best["lag_ms"] = best["lag_ticks"] * dt_s * 1000.0
    return best


def fit_quality(combined, raw_tracking_p95):
    if combined is None or raw_tracking_p95 is None:
        return "UNKNOWN"
    if combined["p95_abs_error"] <= 0.05:
        return "GOOD"
    if combined["p95_abs_error"] <= raw_tracking_p95 * 0.60:
        return "USEFUL"
    return "POOR"


def boundary_warnings(combined, args):
    warnings = []
    if not combined:
        return warnings
    if combined["tau_s"] <= args.tau_min:
        warnings.append("tau_s hit lower grid bound")
    if combined["tau_s"] >= args.tau_max:
        warnings.append("tau_s hit upper grid bound")
    if combined["velocity_limit_rad_s"] <= args.velocity_min:
        warnings.append("velocity limit hit lower grid bound")
    if combined["velocity_limit_rad_s"] >= args.velocity_max:
        warnings.append("velocity limit hit upper grid bound")
    if combined["delay_ticks"] <= args.delay_min:
        warnings.append("delay hit lower grid bound")
    if combined["delay_ticks"] >= args.delay_max:
        warnings.append("delay hit upper grid bound")
    return warnings


def analyze_joint(samples, args):
    delay_values = list(range(args.delay_min, args.delay_max + 1))
    tau_values = grid(args.tau_min, args.tau_max, args.tau_step)
    velocity_values = grid(args.velocity_min, args.velocity_max, args.velocity_step)
    series = series_stats(samples)
    target_error = [abs(sample["actual"] - sample["target"]) for sample in samples]
    raw_tracking = stats(target_error)
    delay_only = fit_delay_only(samples, delay_values, args.selection_metric)
    first_order_only = fit_first_order_only(samples, tau_values, args.selection_metric)
    velocity_only = fit_velocity_only(samples, velocity_values, args.selection_metric)
    combined = fit_combined(
        samples, delay_values, tau_values, velocity_values, args.selection_metric
    )
    lag = cross_correlation_lag(samples, args.max_lag_ticks)
    return {
        "series": series,
        "raw_tracking": raw_tracking,
        "cross_correlation_lag": lag,
        "delay_only": delay_only,
        "first_order_only": first_order_only,
        "velocity_only": velocity_only,
        "combined": combined,
        "fit_quality": fit_quality(combined, None if raw_tracking is None else raw_tracking["p95"]),
        "warnings": boundary_warnings(combined, args),
    }


def summarize_recommendations(results):
    pitch = [item for item in results.values() if item.get("combined")]
    if not pitch:
        return {
            "delay_ticks": [3, 8],
            "tau_s": [0.06, 0.14],
            "velocity_limit_rad_s": [2.5, 4.7],
            "confidence": "LOW",
        }
    delays = [item["combined"]["delay_ticks"] for item in pitch]
    taus = [item["combined"]["tau_s"] for item in pitch]
    velocities = [item["combined"]["velocity_limit_rad_s"] for item in pitch]
    qualities = [item["fit_quality"] for item in pitch]
    return {
        "fit_delay_ticks_range": [min(delays), max(delays)],
        "fit_tau_s_range": [min(taus), max(taus)],
        "fit_velocity_limit_rad_s_range": [min(velocities), max(velocities)],
        "recommended_training_delay_ticks": [3, 8],
        "recommended_training_tau_s": [0.06, 0.14],
        "recommended_training_velocity_limit_rad_s": [2.5, 4.7],
        "confidence": "MEDIUM" if any(q in {"GOOD", "USEFUL"} for q in qualities) else "LOW",
    }


def collect_bus(records):
    read_values = []
    write_values = []
    last_error = None
    for record in records:
        bus = record.get("bus", {})
        if finite(bus.get("read_error_count")):
            read_values.append(int(bus["read_error_count"]))
        if finite(bus.get("write_error_count")):
            write_values.append(int(bus["write_error_count"]))
        if bus.get("last_error"):
            last_error = bus["last_error"]
    return {
        "read_error_count": max(read_values) if read_values else None,
        "write_error_count": max(write_values) if write_values else None,
        "last_error": last_error,
    }


def analyze_file(path, args):
    records = load_records(path, args.startup_ticks)
    results = {}
    for joint in args.joints:
        samples = joint_series(records, joint)
        if len(samples) < 30:
            results[joint] = {"error": "not enough samples", "samples": len(samples)}
            continue
        results[joint] = analyze_joint(samples, args)
    return {
        "telemetry_jsonl": str(path),
        "startup_ticks": args.startup_ticks,
        "selection_metric": args.selection_metric,
        "bus": collect_bus(records),
        "joints": results,
        "recommendations": summarize_recommendations(results),
    }


def model_support_label(item):
    combined = item.get("combined")
    delay = item.get("delay_only")
    first = item.get("first_order_only")
    velocity = item.get("velocity_only")
    if not combined:
        return "UNKNOWN"
    labels = []
    if delay and combined["rmse"] < delay["rmse"] * 0.85:
        labels.append("lag/velocity improves over delay-only")
    if first and combined["rmse"] < first["rmse"] * 0.90:
        labels.append("delay improves over lag-only")
    if velocity and combined["rmse"] < velocity["rmse"] * 0.90:
        labels.append("lag/delay improves over velocity-only")
    return "; ".join(labels) if labels else "simple model families are similar"


def build_markdown(primary, comparison):
    recommendations = primary["recommendations"]
    lines = ["# Actuator Response Fit", ""]
    lines.append("## Executive Summary")
    lines.append("")
    lines.append(f"primary_telemetry: `{primary['telemetry_jsonl']}`")
    lines.append(f"startup_ticks_ignored: `{primary['startup_ticks']}`")
    lines.append(f"selection_metric: `{primary.get('selection_metric', 'rmse')}`")
    lines.append(
        "recommended_training_delay_ticks: "
        f"`{recommendations['recommended_training_delay_ticks']}`"
    )
    lines.append(
        "recommended_training_tau_s: "
        f"`{recommendations['recommended_training_tau_s']}`"
    )
    lines.append(
        "recommended_training_velocity_limit_rad_s: "
        f"`{recommendations['recommended_training_velocity_limit_rad_s']}`"
    )
    lines.append(f"confidence: `{recommendations['confidence']}`")
    lines.append("")
    lines.append(
        "The fitted parameters are evidence for training randomization ranges, "
        "not a precise servo-internal model. The combined model is intended to "
        "capture delay, first-order lag, and effective velocity limiting visible "
        "in telemetry."
    )
    lines.append("")

    lines.append("## Per-Joint Combined Fit")
    lines.append("")
    lines.append(
        "| joint | delay_ticks | delay_ms | tau_s | velocity_limit | selected | rmse | "
        "trimmed_rmse_95 | model_p95 | raw_p95 | target_range | actual_range | amp_ratio | "
        "target_vel_p95 | actual_vel_p95 | xcorr_lag | fit_quality | warnings |"
    )
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|")
    for joint, item in primary["joints"].items():
        if item.get("error"):
            lines.append(
                f"| {joint} | NA | NA | NA | NA | NA | NA | NA | NA | NA | NA | "
                f"NA | NA | NA | NA | NA | {item['error']} | NA |"
            )
            continue
        combined = item["combined"]
        series = item["series"]
        raw = item["raw_tracking"]
        lag = item["cross_correlation_lag"] or {}
        dt_ms = None
        if lag.get("lag_ticks") not in {None, 0} and lag.get("lag_ms") is not None:
            dt_ms = abs(lag["lag_ms"] / lag["lag_ticks"])
        delay_ms = None if dt_ms is None else combined["delay_ticks"] * dt_ms
        target_vel = series["sent_target_velocity"] or {}
        actual_vel = series["actual_velocity"] or {}
        lines.append(
            f"| {joint} | {combined['delay_ticks']} | {fmt(delay_ms, 1)} | "
            f"{fmt(combined['tau_s'], 3)} | {fmt(combined['velocity_limit_rad_s'], 2)} | "
            f"{fmt(combined.get('selection_score'))} | {fmt(combined['rmse'])} | "
            f"{fmt(combined.get('trimmed_rmse_95'))} | "
            f"{fmt(combined['p95_abs_error'])} | "
            f"{fmt(raw.get('p95'))} | {fmt(series['target_range'])} | "
            f"{fmt(series['actual_range'])} | {fmt(series['amplitude_ratio'], 3)} | "
            f"{fmt(target_vel.get('p95'))} | {fmt(actual_vel.get('p95'))} | "
            f"{fmt(lag.get('lag_ticks'), 0)} | {item['fit_quality']} | "
            f"{', '.join(item.get('warnings') or ['none'])} |"
        )
    lines.append("")

    lines.append("## Model Family Comparison")
    lines.append("")
    lines.append("| joint | delay_only_rmse | first_order_rmse | velocity_only_rmse | combined_rmse | support |")
    lines.append("|---|---:|---:|---:|---:|---|")
    for joint, item in primary["joints"].items():
        if item.get("error"):
            continue
        lines.append(
            f"| {joint} | {fmt(item['delay_only']['rmse'])} | "
            f"{fmt(item['first_order_only']['rmse'])} | "
            f"{fmt(item['velocity_only']['rmse'])} | "
            f"{fmt(item['combined']['rmse'])} | {model_support_label(item)} |"
        )
    lines.append("")

    lines.append("## Recommended Training Ranges")
    lines.append("")
    lines.append("| parameter | range | reason |")
    lines.append("|---|---:|---|")
    lines.append("| delay_ticks | `3-8` | covers replay cross-correlation lag and expected training stress range |")
    lines.append("| tau_s | `0.06-0.14` | matches measured effective 80-130 ms behavior and bridge spec |")
    lines.append("| effective_velocity_limit_rad_s | `2.5-4.7` | below/near ST3215 no-load speed; stress-tests loaded gait |")
    lines.append("| per_joint_asymmetry | enabled | fit and tracking differ across hip/knee/ankle and left/right |")
    lines.append("")

    lines.append("## Warnings")
    lines.append("")
    lines.append("- Fit quality is limited by telemetry cadence and by using commanded target/feedback logs, not servo-internal current-loop data.")
    lines.append("- CRC/read errors remain a watch item, but this fit does not model packet-level dropouts.")
    lines.append("- Use `--selection-metric trimmed_rmse_95` or `--selection-metric p95_abs_error` to test whether stale-but-finite read outliers are biasing the fitted velocity ceiling.")
    lines.append("- Do not use these numbers to tune runtime behavior directly; use them to configure sim/training experiments first.")
    lines.append("")

    if comparison:
        lines.append("## Comparison Telemetry")
        lines.append("")
        lines.append(f"comparison_telemetry: `{comparison['telemetry_jsonl']}`")
        lines.append(f"bus: `{comparison['bus']}`")
        lines.append("")
        lines.append("| joint | raw_p95 | target_vel_p95 | combined_rmse | combined_p95 |")
        lines.append("|---|---:|---:|---:|---:|")
        for joint, item in comparison["joints"].items():
            if item.get("error"):
                continue
            target_vel = (item["series"]["sent_target_velocity"] or {}).get("p95")
            lines.append(
                f"| {joint} | {fmt(item['raw_tracking'].get('p95'))} | "
                f"{fmt(target_vel)} | {fmt(item['combined']['rmse'])} | "
                f"{fmt(item['combined']['p95_abs_error'])} |"
            )
        lines.append("")
    return "\n".join(lines).rstrip()


def main():
    parser = argparse.ArgumentParser(
        description="Fit a simple delayed/lagged/velocity-limited actuator response model from telemetry."
    )
    parser.add_argument("telemetry_jsonl")
    parser.add_argument("--comparison-jsonl", default=None)
    parser.add_argument("--output-md", default=None)
    parser.add_argument("--output-json", default=None)
    parser.add_argument("--startup-ticks", type=int, default=50)
    parser.add_argument("--delay-min", type=int, default=0)
    parser.add_argument("--delay-max", type=int, default=10)
    parser.add_argument("--tau-min", type=float, default=0.02)
    parser.add_argument("--tau-max", type=float, default=0.20)
    parser.add_argument("--tau-step", type=float, default=0.02)
    parser.add_argument("--velocity-min", type=float, default=1.0)
    parser.add_argument("--velocity-max", type=float, default=6.0)
    parser.add_argument("--velocity-step", type=float, default=0.25)
    parser.add_argument("--max-lag-ticks", type=int, default=12)
    parser.add_argument("--joints", nargs="+", default=PITCH_CHAIN_JOINTS)
    parser.add_argument(
        "--selection-metric",
        choices=["rmse", "trimmed_rmse_95", "p95_abs_error", "mae"],
        default="rmse",
        help=(
            "Metric used to select the best grid-search parameters. rmse "
            "preserves the original behavior. trimmed_rmse_95 and "
            "p95_abs_error are robust to stale-but-finite read outliers."
        ),
    )
    args = parser.parse_args()

    primary = analyze_file(Path(args.telemetry_jsonl), args)
    comparison = (
        analyze_file(Path(args.comparison_jsonl), args) if args.comparison_jsonl else None
    )
    report = build_markdown(primary, comparison)

    if args.output_md:
        Path(args.output_md).parent.mkdir(parents=True, exist_ok=True)
        with open(args.output_md, "w") as f:
            f.write(report)
            f.write("\n")
    if args.output_json:
        Path(args.output_json).parent.mkdir(parents=True, exist_ok=True)
        with open(args.output_json, "w") as f:
            json.dump({"primary": primary, "comparison": comparison}, f, indent=2)
            f.write("\n")
    print(report)


if __name__ == "__main__":
    main()
