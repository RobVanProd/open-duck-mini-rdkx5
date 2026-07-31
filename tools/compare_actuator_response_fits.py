#!/usr/bin/env python3
"""Compare two actuator response fit JSON files.

This is an offline reporting tool. It does not run robot tests, SSH, deploy,
train, or change runtime behavior.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


PITCH_CHAIN_JOINTS = [
    "left_hip_pitch",
    "left_knee",
    "left_ankle",
    "right_hip_pitch",
    "right_knee",
    "right_ankle",
]


def fmt(value: Any, digits: int = 4) -> str:
    if value is None:
        return "NA"
    return f"{float(value):.{digits}f}"


def load_fit(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text())
    primary = payload.get("primary") if isinstance(payload.get("primary"), dict) else payload
    joints = primary.get("joints")
    if not isinstance(joints, dict):
        raise ValueError(f"{path} does not contain primary.joints or joints")
    return {
        "path": str(path),
        "telemetry_jsonl": primary.get("telemetry_jsonl"),
        "startup_ticks": primary.get("startup_ticks"),
        "bus": primary.get("bus"),
        "recommendations": primary.get("recommendations"),
        "joints": joints,
    }


def get_nested(mapping: dict[str, Any], *keys: str):
    cur: Any = mapping
    for key in keys:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(key)
    return cur


def delta(new_value, old_value):
    if new_value is None or old_value is None:
        return None
    return float(new_value) - float(old_value)


def joint_row(joint: str, old: dict[str, Any], new: dict[str, Any]) -> dict[str, Any]:
    old_joint = old["joints"].get(joint, {})
    new_joint = new["joints"].get(joint, {})
    old_combined = old_joint.get("combined") or {}
    new_combined = new_joint.get("combined") or {}
    old_series = old_joint.get("series") or {}
    new_series = new_joint.get("series") or {}
    old_raw = old_joint.get("raw_tracking") or {}
    new_raw = new_joint.get("raw_tracking") or {}
    values = {
        "joint": joint,
        "old_delay_ticks": old_combined.get("delay_ticks"),
        "new_delay_ticks": new_combined.get("delay_ticks"),
        "old_tau_s": old_combined.get("tau_s"),
        "new_tau_s": new_combined.get("tau_s"),
        "old_velocity_limit_rad_s": old_combined.get("velocity_limit_rad_s"),
        "new_velocity_limit_rad_s": new_combined.get("velocity_limit_rad_s"),
        "old_model_p95_rad": old_combined.get("p95_abs_error"),
        "new_model_p95_rad": new_combined.get("p95_abs_error"),
        "old_raw_tracking_p95_rad": old_raw.get("p95"),
        "new_raw_tracking_p95_rad": new_raw.get("p95"),
        "old_target_velocity_p95_rad_s": get_nested(old_series, "sent_target_velocity", "p95"),
        "new_target_velocity_p95_rad_s": get_nested(new_series, "sent_target_velocity", "p95"),
        "old_actual_velocity_p95_rad_s": get_nested(old_series, "actual_velocity", "p95"),
        "new_actual_velocity_p95_rad_s": get_nested(new_series, "actual_velocity", "p95"),
        "old_fit_quality": old_joint.get("fit_quality"),
        "new_fit_quality": new_joint.get("fit_quality"),
        "old_warnings": old_joint.get("warnings") or [],
        "new_warnings": new_joint.get("warnings") or [],
    }
    for key in [
        "delay_ticks",
        "tau_s",
        "velocity_limit_rad_s",
        "model_p95_rad",
        "raw_tracking_p95_rad",
        "target_velocity_p95_rad_s",
        "actual_velocity_p95_rad_s",
    ]:
        values[f"delta_{key}"] = delta(values.get(f"new_{key}"), values.get(f"old_{key}"))
    return values


def asymmetry(rows: list[dict[str, Any]], left: str, right: str, field: str) -> dict[str, Any]:
    by_joint = {row["joint"]: row for row in rows}
    left_value = by_joint.get(left, {}).get(field)
    right_value = by_joint.get(right, {}).get(field)
    return {
        "left_joint": left,
        "right_joint": right,
        "field": field,
        "left": left_value,
        "right": right_value,
        "left_minus_right": delta(left_value, right_value),
    }


def build_payload(old_path: Path, new_path: Path) -> dict[str, Any]:
    old = load_fit(old_path)
    new = load_fit(new_path)
    joints = sorted(set(PITCH_CHAIN_JOINTS) | set(old["joints"]) | set(new["joints"]))
    rows = [joint_row(joint, old, new) for joint in joints]
    return {
        "status": "PASS_ACTUATOR_FIT_COMPARE_READY",
        "old_fit": old,
        "new_fit": new,
        "joints": rows,
        "asymmetry": {
            "left_right_knee_new_velocity_limit": asymmetry(
                rows, "left_knee", "right_knee", "new_velocity_limit_rad_s"
            ),
            "left_right_knee_new_raw_tracking_p95": asymmetry(
                rows, "left_knee", "right_knee", "new_raw_tracking_p95_rad"
            ),
            "left_right_knee_new_model_p95": asymmetry(
                rows, "left_knee", "right_knee", "new_model_p95_rad"
            ),
        },
        "no_robot_tests": True,
        "no_deploy": True,
        "runtime_behavior_changed": False,
    }


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    lines = [
        "# Actuator Response Fit Compare",
        "",
        f"status: `{payload['status']}`",
        "",
        "Offline comparison only. No robot tests, SSH, deployment, training, or runtime behavior changes were performed.",
        "",
        "## Inputs",
        "",
        f"- old fit: `{payload['old_fit']['path']}`",
        f"- old telemetry: `{payload['old_fit'].get('telemetry_jsonl')}`",
        f"- new fit: `{payload['new_fit']['path']}`",
        f"- new telemetry: `{payload['new_fit'].get('telemetry_jsonl')}`",
        "",
        "## Per-Joint Delta",
        "",
        "| joint | delay old->new | tau old->new | vel old->new | model p95 old->new | raw p95 old->new | target vel p95 old->new | actual vel p95 old->new | quality old->new | warnings |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|---|",
    ]
    for row in payload["joints"]:
        lines.append(
            "| {joint} | {od}->{nd} ({dd}) | {ot}->{nt} ({dt}) | {ov}->{nv} ({dv}) | "
            "{om}->{nm} ({dm}) | {oraw}->{nraw} ({draw}) | {otv}->{ntv} ({dtv}) | "
            "{oav}->{nav} ({dav}) | `{oq}`->`{nq}` | {warnings} |".format(
                joint=row["joint"],
                od=fmt(row.get("old_delay_ticks"), 0),
                nd=fmt(row.get("new_delay_ticks"), 0),
                dd=fmt(row.get("delta_delay_ticks"), 0),
                ot=fmt(row.get("old_tau_s"), 3),
                nt=fmt(row.get("new_tau_s"), 3),
                dt=fmt(row.get("delta_tau_s"), 3),
                ov=fmt(row.get("old_velocity_limit_rad_s"), 2),
                nv=fmt(row.get("new_velocity_limit_rad_s"), 2),
                dv=fmt(row.get("delta_velocity_limit_rad_s"), 2),
                om=fmt(row.get("old_model_p95_rad")),
                nm=fmt(row.get("new_model_p95_rad")),
                dm=fmt(row.get("delta_model_p95_rad")),
                oraw=fmt(row.get("old_raw_tracking_p95_rad")),
                nraw=fmt(row.get("new_raw_tracking_p95_rad")),
                draw=fmt(row.get("delta_raw_tracking_p95_rad")),
                otv=fmt(row.get("old_target_velocity_p95_rad_s")),
                ntv=fmt(row.get("new_target_velocity_p95_rad_s")),
                dtv=fmt(row.get("delta_target_velocity_p95_rad_s")),
                oav=fmt(row.get("old_actual_velocity_p95_rad_s")),
                nav=fmt(row.get("new_actual_velocity_p95_rad_s")),
                dav=fmt(row.get("delta_actual_velocity_p95_rad_s")),
                oq=row.get("old_fit_quality"),
                nq=row.get("new_fit_quality"),
                warnings=", ".join(row.get("new_warnings") or ["none"]),
            )
        )
    lines.extend(["", "## Knee Asymmetry", ""])
    for name, item in payload["asymmetry"].items():
        lines.append(
            f"- `{name}`: `{fmt(item.get('left'))}` vs `{fmt(item.get('right'))}`, "
            f"left_minus_right `{fmt(item.get('left_minus_right'))}`"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- Use this comparison to decide whether the corrected-knee hardware changed the actuator bridge ranges.",
            "- If the new fit is sine-only, do not treat it as walking-policy dynamic evidence.",
            "- If left/right knee asymmetry remains large, inspect hardware before training around it.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--old", required=True, type=Path)
    parser.add_argument("--new", required=True, type=Path)
    parser.add_argument("--output-md", required=True, type=Path)
    parser.add_argument("--output-json", required=True, type=Path)
    args = parser.parse_args()

    payload = build_payload(args.old, args.new)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    write_markdown(payload, args.output_md)
    print(payload["status"])
    print(f"wrote {args.output_md}")
    print(f"wrote {args.output_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
