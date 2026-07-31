#!/usr/bin/env python3
"""Prepare and analyze operator-run low-command hardware telemetry.

This tool is intentionally offline-safe:

- It does not SSH.
- It does not deploy.
- It does not command motors.
- It does not run a walking policy.

Use `plan` to generate the operator handoff packet. Use `analyze` after the
operator has collected JSONL telemetry with a separate approved procedure.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


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

TARGET_PATHS = [
    ("action", "motor_targets_sent_rad"),
    ("action", "motor_targets_post_rate_limit_rad"),
    ("joints", "target_position_rad"),
    ("joints", "commanded_position_rad"),
    ("motors", "sent_target_rad"),
    ("sent_target_rad",),
]

ACTUAL_PATHS = [
    ("joints", "actual_position_rad"),
    ("joints", "present_position_rad"),
    ("motors", "present_position_rad"),
    ("present_position_rad",),
]

ACTION_PATHS = [
    ("action", "onnx_action"),
    ("policy", "action"),
    ("onnx_action",),
]


def finite(value: Any) -> bool:
    try:
        return value is not None and math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def percentile(values: list[float], pct: float) -> float | None:
    clean = sorted(float(value) for value in values if finite(value))
    if not clean:
        return None
    if len(clean) == 1:
        return clean[0]
    k = (len(clean) - 1) * pct / 100.0
    lo = math.floor(k)
    hi = math.ceil(k)
    if lo == hi:
        return clean[lo]
    return clean[lo] * (hi - k) + clean[hi] * (k - lo)


def stats(values: list[float]) -> dict[str, float] | None:
    clean = [float(value) for value in values if finite(value)]
    if not clean:
        return None
    return {
        "p50": percentile(clean, 50) or 0.0,
        "p95": percentile(clean, 95) or 0.0,
        "p99": percentile(clean, 99) or 0.0,
        "max": max(clean),
    }


def fmt(value: Any, digits: int = 4) -> str:
    if value is None:
        return "NA"
    return f"{float(value):.{digits}f}"


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open() as handle:
        for line_no, line in enumerate(handle, 1):
            line = line.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_no}: invalid JSON: {exc}") from exc
            if isinstance(payload, dict):
                records.append(payload)
    return records


def nested(record: dict[str, Any], path: tuple[str, ...]) -> Any:
    cur: Any = record
    for key in path:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(key)
    return cur


def vector_from_value(value: Any) -> list[float] | None:
    if isinstance(value, dict):
        if all(name in value for name in JOINT_NAMES):
            result = []
            for name in JOINT_NAMES:
                if not finite(value[name]):
                    return None
                result.append(float(value[name]))
            return result
        return None
    if isinstance(value, list) and len(value) >= len(JOINT_NAMES):
        result = []
        for item in value[: len(JOINT_NAMES)]:
            if not finite(item):
                return None
            result.append(float(item))
        return result
    return None


def first_vector(record: dict[str, Any], paths: list[tuple[str, ...]]) -> list[float] | None:
    for path in paths:
        vector = vector_from_value(nested(record, path))
        if vector is not None:
            return vector
    return None


def timestamp(record: dict[str, Any]) -> float | None:
    for key in ("timestamp_monotonic_s", "monotonic_s", "time_s", "t_s", "timestamp_s"):
        value = record.get(key)
        if finite(value):
            return float(value)
    return None


def record_dt(prev: dict[str, Any], cur: dict[str, Any], default_dt_s: float) -> float:
    if finite(cur.get("dt_s")) and float(cur["dt_s"]) > 0:
        return float(cur["dt_s"])
    prev_t = timestamp(prev)
    cur_t = timestamp(cur)
    if prev_t is not None and cur_t is not None and cur_t > prev_t:
        return cur_t - prev_t
    return default_dt_s


def bus_counters(record: dict[str, Any]) -> dict[str, int]:
    counters = {"read_errors": 0, "crc_errors": 0, "write_errors": 0}

    def visit(prefix: str, value: Any) -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                visit(f"{prefix}.{key}".strip("."), child)
            return
        if not isinstance(value, (int, float)):
            return
        lower = prefix.lower()
        if "crc" in lower and "error" in lower:
            counters["crc_errors"] += int(value)
        elif "read" in lower and "error" in lower:
            counters["read_errors"] += int(value)
        elif "write" in lower and "error" in lower:
            counters["write_errors"] += int(value)

    visit("", record)
    return counters


def analyze_records(
    records: list[dict[str, Any]],
    *,
    default_dt_s: float,
    tracking_p95_limit_rad: float,
    sent_vel_p95_limit_rad_s: float,
) -> dict[str, Any]:
    per_joint: dict[str, dict[str, Any]] = {}
    target_series = {name: [] for name in JOINT_NAMES}
    actual_series = {name: [] for name in JOINT_NAMES}
    action_series = {name: [] for name in JOINT_NAMES}
    sent_velocities = {name: [] for name in JOINT_NAMES}
    tracking_errors = {name: [] for name in JOINT_NAMES}
    valid_target_actual_samples = 0
    bus_totals = {"read_errors": 0, "crc_errors": 0, "write_errors": 0}

    previous_record: dict[str, Any] | None = None
    previous_target: list[float] | None = None

    for record in records:
        for key, value in bus_counters(record).items():
            bus_totals[key] = max(bus_totals[key], value)
        target = first_vector(record, TARGET_PATHS)
        actual = first_vector(record, ACTUAL_PATHS)
        action = first_vector(record, ACTION_PATHS)

        if target is not None:
            if previous_record is not None and previous_target is not None:
                dt_s = record_dt(previous_record, record, default_dt_s)
                if dt_s > 0:
                    for index, name in enumerate(JOINT_NAMES):
                        sent_velocities[name].append(abs(target[index] - previous_target[index]) / dt_s)
            previous_record = record
            previous_target = target
            for index, name in enumerate(JOINT_NAMES):
                target_series[name].append(target[index])

        if actual is not None:
            for index, name in enumerate(JOINT_NAMES):
                actual_series[name].append(actual[index])

        if action is not None:
            for index, name in enumerate(JOINT_NAMES):
                action_series[name].append(action[index])

        if target is not None and actual is not None:
            valid_target_actual_samples += 1
            for index, name in enumerate(JOINT_NAMES):
                tracking_errors[name].append(abs(target[index] - actual[index]))

    for name in JOINT_NAMES:
        actions = action_series[name]
        per_joint[name] = {
            "samples_target": len(target_series[name]),
            "samples_actual": len(actual_series[name]),
            "sent_target_velocity_rad_s": stats(sent_velocities[name]),
            "tracking_abs_rad": stats(tracking_errors[name]),
            "action_saturation_pct": (
                None
                if not actions
                else sum(abs(value) >= 0.98 for value in actions) / len(actions) * 100.0
            ),
        }

    pitch_vel_p95 = [
        per_joint[name]["sent_target_velocity_rad_s"]["p95"]
        for name in PITCH_CHAIN_JOINTS
        if per_joint[name]["sent_target_velocity_rad_s"] is not None
    ]
    pitch_tracking_p95 = [
        per_joint[name]["tracking_abs_rad"]["p95"]
        for name in PITCH_CHAIN_JOINTS
        if per_joint[name]["tracking_abs_rad"] is not None
    ]
    max_pitch_vel_p95 = max(pitch_vel_p95) if pitch_vel_p95 else None
    max_pitch_tracking_p95 = max(pitch_tracking_p95) if pitch_tracking_p95 else None

    if valid_target_actual_samples == 0:
        status = "HOLD_TELEMETRY_NO_TARGET_ACTUAL"
    elif max_pitch_vel_p95 is not None and max_pitch_vel_p95 > sent_vel_p95_limit_rad_s:
        status = "HOLD_TARGET_VELOCITY_OVER_LIMIT"
    elif max_pitch_tracking_p95 is not None and max_pitch_tracking_p95 > tracking_p95_limit_rad:
        status = "HOLD_TRACKING_P95_OVER_LIMIT"
    else:
        status = "PASS_LOWCOMMAND_HW_TELEMETRY_SUMMARY"

    return {
        "status": status,
        "samples": len(records),
        "valid_target_actual_samples": valid_target_actual_samples,
        "default_dt_s": default_dt_s,
        "limits": {
            "tracking_p95_limit_rad": tracking_p95_limit_rad,
            "sent_vel_p95_limit_rad_s": sent_vel_p95_limit_rad_s,
        },
        "summary": {
            "max_pitch_chain_sent_velocity_p95_rad_s": max_pitch_vel_p95,
            "max_pitch_chain_tracking_p95_rad": max_pitch_tracking_p95,
            "bus_totals": bus_totals,
        },
        "pitch_chain": {name: per_joint[name] for name in PITCH_CHAIN_JOINTS},
        "joints": per_joint,
        "no_robot_tests_run_by_tool": True,
        "no_ssh": True,
        "no_deploy": True,
        "runtime_behavior_changed": False,
    }


def plan_payload(args: argparse.Namespace) -> dict[str, Any]:
    return {
        "status": "PREPARED_OPERATOR_HANDOFF_ONLY",
        "command_x": args.command_x,
        "duration_s": args.duration_s,
        "corrected_knee_required": args.corrected_knee_required,
        "duck_config_hash": args.duck_config_hash,
        "checklist": [
            "operator physically present",
            "robot supported on stand/catch rig",
            "corrected knee offset/hash recorded",
            "motors off before and after procedure unless the operator explicitly enables torque",
            "fixed low command only",
            "JSONL telemetry captured",
            "no grounded replay unless separately approved",
            "no tuning, remap, gain, action-scale, phase, policy, or duck_config change",
        ],
        "telemetry_required_fields": [
            "timestamp or dt_s",
            "action.motor_targets_sent_rad or equivalent 14-vector",
            "joints.actual_position_rad or equivalent 14-vector",
            "action.onnx_action if policy is used",
            "bus/read/write/CRC counters if available",
            "contacts/base pose if available",
        ],
        "operator_command_template": (
            "OPERATOR_ONLY_PLACEHOLDER --fixed-command-x {x:.3f} --duration {duration:.1f} "
            "--jsonl outputs/first_evidence/<timestamp>/instrumented_lowcmd_hw_eval.jsonl"
        ).format(x=args.command_x, duration=args.duration_s),
        "tool_behavior": "This tool only writes the packet or analyzes existing JSONL.",
    }


def write_plan_markdown(payload: dict[str, Any], path: Path) -> None:
    lines = [
        "# Instrumented Low-Command Hardware Eval Handoff",
        "",
        f"status: `{payload['status']}`",
        "",
        "This is an operator handoff packet. The tool did not SSH, deploy, command motors, or run a policy.",
        "",
        "## Scope",
        "",
        f"- fixed command x: `{payload['command_x']}`",
        f"- duration: `{payload['duration_s']}` seconds",
        f"- corrected knee required: `{payload['corrected_knee_required']}`",
        f"- duck_config hash: `{payload.get('duck_config_hash')}`",
        "",
        "## Checklist",
        "",
    ]
    lines.extend(f"- {item}" for item in payload["checklist"])
    lines.extend(["", "## Telemetry Fields", ""])
    lines.extend(f"- {item}" for item in payload["telemetry_required_fields"])
    lines.extend(
        [
            "",
            "## Command Template",
            "",
            "The command below is a placeholder for the operator-approved runtime harness. This tool does not execute it.",
            "",
            "```bash",
            payload["operator_command_template"],
            "```",
            "",
            "## Post-Run Analysis",
            "",
            "After telemetry exists, run:",
            "",
            "```bash",
            "python3 tools/instrumented_lowcmd_hw_eval.py analyze \\",
            "  outputs/first_evidence/<timestamp>/instrumented_lowcmd_hw_eval.jsonl \\",
            "  --output-md outputs/analysis/INSTRUMENTED_LOWCMD_HW_EVAL.md \\",
            "  --output-json outputs/analysis/instrumented_lowcmd_hw_eval.json",
            "```",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines))


def write_analysis_markdown(payload: dict[str, Any], path: Path, telemetry_path: Path) -> None:
    lines = [
        "# Instrumented Low-Command Hardware Eval Analysis",
        "",
        f"status: `{payload['status']}`",
        f"telemetry: `{telemetry_path}`",
        "",
        "This is offline analysis of existing telemetry. The tool did not SSH, deploy, command motors, or run a policy.",
        "",
        "## Summary",
        "",
        f"- samples: `{payload['samples']}`",
        f"- target/actual samples: `{payload['valid_target_actual_samples']}`",
        f"- max pitch-chain sent velocity p95: `{fmt(payload['summary']['max_pitch_chain_sent_velocity_p95_rad_s'])}` rad/s",
        f"- max pitch-chain tracking p95: `{fmt(payload['summary']['max_pitch_chain_tracking_p95_rad'])}` rad",
        f"- bus totals: `{payload['summary']['bus_totals']}`",
        "",
        "## Pitch Chain",
        "",
        "| joint | sent vel p95 | sent vel max | tracking p95 | tracking max | action sat pct |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for joint, item in payload["pitch_chain"].items():
        vel = item.get("sent_target_velocity_rad_s") or {}
        tracking = item.get("tracking_abs_rad") or {}
        lines.append(
            f"| {joint} | {fmt(vel.get('p95'))} | {fmt(vel.get('max'))} | "
            f"{fmt(tracking.get('p95'))} | {fmt(tracking.get('max'))} | "
            f"{fmt(item.get('action_saturation_pct'), 2)} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- `PASS_LOWCOMMAND_HW_TELEMETRY_SUMMARY` means the telemetry stayed under the configured analysis thresholds; it is not an automatic grounded-walking approval.",
            "- Holds should be reviewed before any further robot motion.",
            "- If the corrected-knee actuator fit has not been refreshed, treat this as descriptive telemetry only.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines))


def write_json(payload: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def add_common_output_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--output-md", type=Path)
    parser.add_argument("--output-json", type=Path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    plan_parser = subparsers.add_parser("plan", help="write an operator handoff packet")
    plan_parser.add_argument("--command-x", type=float, default=0.04)
    plan_parser.add_argument("--duration-s", type=float, default=10.0)
    plan_parser.add_argument("--duck-config-hash")
    plan_parser.add_argument(
        "--corrected-knee-required",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="record whether the corrected-knee config is a prerequisite",
    )
    add_common_output_args(plan_parser)

    analyze_parser = subparsers.add_parser("analyze", help="analyze existing JSONL telemetry")
    analyze_parser.add_argument("telemetry_jsonl", type=Path)
    analyze_parser.add_argument("--default-dt-s", type=float, default=0.02)
    analyze_parser.add_argument("--tracking-p95-limit-rad", type=float, default=0.08)
    analyze_parser.add_argument("--sent-vel-p95-limit-rad-s", type=float, default=3.75)
    add_common_output_args(analyze_parser)

    args = parser.parse_args()

    if args.command == "plan":
        payload = plan_payload(args)
        if args.output_md:
            write_plan_markdown(payload, args.output_md)
        if args.output_json:
            write_json(payload, args.output_json)
        if not args.output_md and not args.output_json:
            print(json.dumps(payload, indent=2, sort_keys=True))
        return 0

    records = load_jsonl(args.telemetry_jsonl)
    payload = analyze_records(
        records,
        default_dt_s=args.default_dt_s,
        tracking_p95_limit_rad=args.tracking_p95_limit_rad,
        sent_vel_p95_limit_rad_s=args.sent_vel_p95_limit_rad_s,
    )
    payload["telemetry_jsonl"] = str(args.telemetry_jsonl)
    if args.output_md:
        write_analysis_markdown(payload, args.output_md, args.telemetry_jsonl)
    if args.output_json:
        write_json(payload, args.output_json)
    if not args.output_md and not args.output_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
