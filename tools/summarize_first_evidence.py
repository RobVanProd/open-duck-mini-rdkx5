#!/usr/bin/env python3
import argparse
import datetime as dt
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


def fmt(value, digits=4):
    if value is None:
        return "MISSING"
    return f"{float(value):.{digits}f}"


def load_json(path):
    if path is None or not path.exists():
        return None
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return None


def load_jsonl(path):
    if path is None or not path.exists():
        return []
    records = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return records


def find_first(directory, patterns):
    for pattern in patterns:
        matches = sorted(directory.glob(pattern))
        if matches:
            return matches[0]
    return None


def extract_warnings(markdown_path):
    if markdown_path is None or not markdown_path.exists():
        return ["MISSING"]
    lines = markdown_path.read_text(errors="replace").splitlines()
    out = []
    in_section = False
    for line in lines:
        if line.strip() == "## Warnings":
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if in_section and line.strip().startswith("- "):
            out.append(line.strip()[2:])
    return out or ["none found"]


def observation_columns(records, start, end):
    columns = {i: [] for i in range(start, end)}
    for record in records:
        obs = record.get("observation", {}).get("raw_vector")
        if obs is None or len(obs) < end:
            continue
        for i in range(start, end):
            columns[i].append(obs[i])
    return columns


def normalization(records):
    for record in records:
        obs = record.get("observation", {})
        mean = obs.get("normalization_mean")
        recip = obs.get("normalization_std_recip")
        if mean and recip:
            return mean, recip
    return None, None


def bus_summary(records):
    read = []
    write = []
    last_error = None
    for record in records:
        bus = record.get("bus", {})
        if finite(bus.get("read_error_count")):
            read.append(bus.get("read_error_count"))
        if finite(bus.get("write_error_count")):
            write.append(bus.get("write_error_count"))
        if bus.get("last_error"):
            last_error = bus.get("last_error")
    return {
        "read_error_count": max(read) if read else None,
        "write_error_count": max(write) if write else None,
        "last_error": last_error,
    }


def tracking_summary(records):
    per_joint = [[] for _ in JOINT_NAMES]
    for record in records:
        err = record.get("joints", {}).get("tracking_error_rad")
        if err is None or len(err) < len(JOINT_NAMES):
            continue
        for i, value in enumerate(err[: len(JOINT_NAMES)]):
            if finite(value):
                per_joint[i].append(abs(float(value)))
    summaries = [stats(values) for values in per_joint]
    largest = []
    for name, summary in zip(JOINT_NAMES, summaries):
        if summary and summary.get("p95") is not None:
            largest.append((summary["p95"], name, summary))
    largest.sort(reverse=True)
    return summaries, largest[:5]


def contact_summary(records):
    samples = 0
    left_true = 0
    right_true = 0
    transitions = 0
    last = None
    for record in records:
        contacts = record.get("control", {}).get("feet_contacts")
        if contacts is None or len(contacts) < 2:
            continue
        current = (bool(contacts[0]), bool(contacts[1]))
        samples += 1
        left_true += int(current[0])
        right_true += int(current[1])
        if last is not None and current != last:
            transitions += 1
        last = current
    if samples == 0:
        return None
    return {
        "samples": samples,
        "left_true_pct": left_true / samples * 100.0,
        "right_true_pct": right_true / samples * 100.0,
        "transitions": transitions,
        "last": last,
    }


def obs_0_6_summary(records):
    cols = observation_columns(records, 0, 6)
    return {i: stats(values) for i, values in cols.items()}


def accel_zscores(records):
    obs_stats = obs_0_6_summary(records)
    mean, recip = normalization(records)
    if mean is None or recip is None:
        return None
    zscores = {}
    for i in range(3, 6):
        summary = obs_stats.get(i)
        if summary is None:
            continue
        zscores[i] = (summary["mean"] - mean[i]) * recip[i]
    return zscores


def gyro_bias(obs_stats):
    return [None if obs_stats.get(i) is None else obs_stats[i]["mean"] for i in range(3)]


def upright_accel(obs_stats):
    return [None if obs_stats.get(i) is None else obs_stats[i]["mean"] for i in range(3, 6)]


def tilt_mapping(records):
    if not records:
        return "MISSING"
    cols = observation_columns(records, 3, 6)
    ranges = {}
    for i, values in cols.items():
        s = stats(values)
        ranges[i] = None if s is None else s["max"] - s["min"]
    if all(value is None for value in ranges.values()):
        return "MISSING"
    dominant = max(
        ((value, i) for i, value in ranges.items() if value is not None),
        default=(None, None),
    )
    return (
        "UNANNOTATED: physical tilt segments are not labeled. "
        f"Largest accel range was obs[{dominant[1]}] with range {fmt(dominant[0])}. "
        "Use operator notes or video to map nose-forward/back and left/right signs."
    )


def snapshot_section(snapshot):
    if snapshot is None:
        return [
            "## Config Snapshot",
            "",
            "MISSING: no `*_rdkx5_config_snapshot.json` found.",
            "",
        ]
    offsets = snapshot.get("joints_offsets") or {}
    lines = [
        "## Config Snapshot",
        "",
        f"- hostname: `{snapshot.get('hostname', 'MISSING')}`",
        f"- snapshot_utc: `{snapshot.get('snapshot_utc', 'MISSING')}`",
        f"- ssh_target: `{snapshot.get('ssh_target', 'MISSING')}`",
        f"- runtime_path: `{snapshot.get('runtime_path', 'MISSING')}`",
        f"- python_env_path: `{snapshot.get('python_env_path', 'MISSING')}`",
        f"- policy_sha256: `{snapshot.get('onnx_policy_sha256', 'MISSING')}`",
        f"- imu_upside_down: `{snapshot.get('imu_upside_down', 'MISSING')}`",
        f"- start_paused: `{(snapshot.get('duck_config') or {}).get('start_paused', 'MISSING')}`",
        f"- phase_frequency_factor_offset: `{snapshot.get('phase_frequency_factor_offset', 'MISSING')}`",
        f"- imu_calib_data_path: `{snapshot.get('imu_calib_data_path', 'MISSING')}`",
        "",
        "Joint offsets summary:",
        "",
        "| joint | offset_rad |",
        "|---|---:|",
    ]
    if offsets:
        for name in JOINT_NAMES:
            lines.append(f"| {name} | {fmt(offsets.get(name))} |")
    else:
        lines.append("| MISSING | MISSING |")
    lines.append("")
    return lines


def home_section(records, warnings):
    lines = ["## Home Pose Analysis", ""]
    if not records:
        lines += ["MISSING: no `home_pose_log_test.jsonl` found.", ""]
        return lines

    obs_stats = obs_0_6_summary(records)
    zscores = accel_zscores(records)
    tracking, largest = tracking_summary(records)
    bus = bus_summary(records)
    contacts = contact_summary(records)

    lines += [
        "Observation `obs[0:6]`:",
        "",
        "| index | channel | mean | std | min | max | accel_zscore |",
        "|---:|---|---:|---:|---:|---:|---:|",
    ]
    names = ["gyro_x", "gyro_y", "gyro_z", "accel_x", "accel_y", "accel_z"]
    for i in range(6):
        s = obs_stats.get(i)
        z = None if zscores is None else zscores.get(i)
        lines.append(
            f"| {i} | {names[i]} | {fmt(None if s is None else s['mean'])} | "
            f"{fmt(None if s is None else s['std'])} | {fmt(None if s is None else s['min'])} | "
            f"{fmt(None if s is None else s['max'])} | {fmt(z, 2)} |"
        )

    lines += [
        "",
        f"- stationary_gyro_bias: `{[fmt(v) for v in gyro_bias(obs_stats)]}`",
        f"- upright_accel_vector: `{[fmt(v) for v in upright_accel(obs_stats)]}`",
        f"- bus_read_error_count: `{bus['read_error_count'] if bus['read_error_count'] is not None else 'MISSING'}`",
        f"- bus_write_error_count: `{bus['write_error_count'] if bus['write_error_count'] is not None else 'MISSING'}`",
        f"- bus_last_error: `{bus['last_error'] or 'none'}`",
    ]
    if contacts:
        lines.append(
            f"- foot_contacts: samples={contacts['samples']}, left_true_pct={fmt(contacts['left_true_pct'], 2)}, "
            f"right_true_pct={fmt(contacts['right_true_pct'], 2)}, transitions={contacts['transitions']}, last={contacts['last']}"
        )
    else:
        lines.append("- foot_contacts: `MISSING`")

    lines += [
        "",
        "Largest joint tracking errors by p95 absolute rad:",
        "",
        "| joint | p50 | p95 | p99 | max |",
        "|---|---:|---:|---:|---:|",
    ]
    if largest:
        for _, name, s in largest:
            lines.append(
                f"| {name} | {fmt(s['p50'])} | {fmt(s['p95'])} | {fmt(s['p99'])} | {fmt(s['max'])} |"
            )
    else:
        lines.append("| MISSING | MISSING | MISSING | MISSING | MISSING |")

    lines += ["", "Analyzer warnings:", ""]
    lines += [f"- {warning}" for warning in warnings]
    lines.append("")
    return lines


def imu_section(records, warnings):
    lines = ["## IMU Tilt Analysis", ""]
    if not records:
        lines += ["MISSING: no `imu_tilt_test.jsonl` found.", ""]
        return lines
    obs_stats = obs_0_6_summary(records)
    lines += [
        f"- aggregate_accel_vector_mean: `{[fmt(v) for v in upright_accel(obs_stats)]}`",
        f"- tilt_axis_mapping: {tilt_mapping(records)}",
        "",
        "Analyzer warnings:",
        "",
    ]
    lines += [f"- {warning}" for warning in warnings]
    lines.append("")
    return lines


def foot_section(records, summary_path):
    lines = ["## Foot Contact Summary", ""]
    if summary_path and summary_path.exists():
        lines += ["Operator/analyzer summary:", ""]
        lines += [f"> {line}" if line else ">" for line in summary_path.read_text(errors="replace").splitlines()]
        lines.append("")
    contacts = contact_summary(records)
    if contacts:
        lines += [
            "JSONL-derived contact stats:",
            "",
            f"- samples: `{contacts['samples']}`",
            f"- left_true_pct: `{fmt(contacts['left_true_pct'], 2)}`",
            f"- right_true_pct: `{fmt(contacts['right_true_pct'], 2)}`",
            f"- transitions: `{contacts['transitions']}`",
            f"- last: `{contacts['last']}`",
            "",
        ]
    elif summary_path is None or not summary_path.exists():
        lines += ["MISSING: no foot contact summary or JSONL found.", ""]
    return lines


def recommendation(home_records, imu_records, foot_records):
    if not home_records:
        return "run home_pose_log_test"
    if not imu_records:
        return "run imu_tilt_test"
    if not foot_records:
        return "run foot_contact_test"
    return "review first evidence gates and decide whether to run joint_identity_test"


def build_summary(evidence_dir):
    snapshot_path = find_first(evidence_dir, ["*_rdkx5_config_snapshot.json", "*config_snapshot*.json"])
    home_log = find_first(evidence_dir, ["home_pose_log_test.jsonl", "*home*pose*.jsonl"])
    home_analysis = find_first(evidence_dir, ["home_pose_analysis.md", "*home*analysis*.md"])
    imu_log = find_first(evidence_dir, ["imu_tilt_test.jsonl", "*imu*tilt*.jsonl"])
    imu_analysis = find_first(evidence_dir, ["imu_tilt_analysis.md", "*imu*analysis*.md"])
    foot_log = find_first(evidence_dir, ["foot_contact_test.jsonl", "*foot*contact*.jsonl"])
    foot_summary = find_first(evidence_dir, ["foot_contact_summary.md", "*foot*summary*.md"])

    snapshot = load_json(snapshot_path)
    home_records = load_jsonl(home_log)
    imu_records = load_jsonl(imu_log)
    foot_records = load_jsonl(foot_log)

    lines = [
        "# First Evidence Summary",
        "",
        f"- generated_utc: `{dt.datetime.now(dt.timezone.utc).isoformat()}`",
        f"- evidence_directory: `{evidence_dir}`",
        f"- config_snapshot: `{snapshot_path if snapshot_path else 'MISSING'}`",
        f"- home_pose_log: `{home_log if home_log else 'MISSING'}`",
        f"- home_pose_analysis: `{home_analysis if home_analysis else 'MISSING'}`",
        f"- imu_tilt_log: `{imu_log if imu_log else 'MISSING'}`",
        f"- imu_tilt_analysis: `{imu_analysis if imu_analysis else 'MISSING'}`",
        f"- foot_contact_log: `{foot_log if foot_log else 'MISSING'}`",
        f"- foot_contact_summary: `{foot_summary if foot_summary else 'MISSING'}`",
        "",
    ]
    lines += snapshot_section(snapshot)
    lines += home_section(home_records, extract_warnings(home_analysis))
    lines += imu_section(imu_records, extract_warnings(imu_analysis))
    lines += foot_section(foot_records, foot_summary)
    lines += [
        "## Warnings And Missing Evidence",
        "",
    ]
    missing = []
    for label, path in [
        ("config snapshot", snapshot_path),
        ("home pose log", home_log),
        ("home pose analysis", home_analysis),
        ("IMU tilt log", imu_log),
        ("IMU tilt analysis", imu_analysis),
        ("foot contact log", foot_log),
        ("foot contact summary", foot_summary),
    ]:
        if path is None:
            missing.append(label)
    if missing:
        lines += [f"- MISSING: {item}" for item in missing]
    else:
        lines.append("- none")
    lines += [
        "",
        "## Recommended Next Gate",
        "",
        f"`{recommendation(home_records, imu_records, foot_records)}`",
        "",
    ]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Summarize first Open Duck evidence packet.")
    parser.add_argument("evidence_dir", help="Directory containing first evidence files.")
    parser.add_argument(
        "--output",
        default="outputs/analysis/FIRST_EVIDENCE_SUMMARY.md",
        help="Markdown output path.",
    )
    args = parser.parse_args()

    evidence_dir = Path(args.evidence_dir)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    summary = build_summary(evidence_dir)
    output.write_text(summary + "\n")
    print(output)


if __name__ == "__main__":
    main()
