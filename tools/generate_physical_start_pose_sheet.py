#!/usr/bin/env python3
"""Generate a field sheet for checking physical home/start pose.

This intentionally avoids a PyYAML dependency because the joint map is simple
and the sheet is meant to run in whatever Python environment is available.
"""

from __future__ import annotations

import argparse
import math
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_JOINT_MAP = ROOT / "docs" / "joint_map_template.yaml"
DEFAULT_GATE = ROOT / "docs" / "PHYSICAL_START_POSE_CALIBRATION_GATE.md"


FIELD_RE = re.compile(r"^\s{4}([a-zA-Z0-9_]+):\s*(.*)\s*$")
ITEM_RE = re.compile(r"^\s{2}-\s+([a-zA-Z0-9_]+):\s*(.*)\s*$")


def parse_scalar(raw: str):
    raw = raw.strip()
    if raw in {"true", "false"}:
        return raw == "true"
    if raw == "UNKNOWN":
        return raw
    try:
        if any(ch in raw for ch in ".eE"):
            return float(raw)
        return int(raw)
    except ValueError:
        return raw.strip('"')


def load_joints(path: Path) -> list[dict]:
    joints: list[dict] = []
    current: dict | None = None
    in_joints = False
    for line in path.read_text().splitlines():
        if line.startswith("joints:"):
            in_joints = True
            continue
        if not in_joints:
            continue
        item = ITEM_RE.match(line)
        if item:
            if current:
                joints.append(current)
            current = {item.group(1): parse_scalar(item.group(2))}
            continue
        field = FIELD_RE.match(line)
        if field and current is not None:
            current[field.group(1)] = parse_scalar(field.group(2))
    if current:
        joints.append(current)
    return joints


def fmt(value, digits: int = 4) -> str:
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def rad_to_deg(value) -> str:
    if not isinstance(value, (float, int)):
        return "NA"
    return f"{math.degrees(float(value)):.1f}"


def build_sheet(joints: list[dict], source: Path, gate_path: Path) -> str:
    lines: list[str] = []
    lines.append("# Physical Start-Pose Field Sheet")
    lines.append("")
    lines.append("Use this while the robot is supported for the repo soft-offset and home-pose checks.")
    lines.append("The primary check is numeric soft-offset calibration; visual home inspection is secondary.")
    lines.append("Telemetry alone cannot pass this gate because offsets are applied on both command and readback.")
    lines.append("")
    lines.append(f"source_joint_map: `{source}`")
    lines.append(f"gate_doc: `{gate_path}`")
    lines.append("")
    lines.append("## Repo Contract")
    lines.append("")
    lines.append("- `find_soft_offsets.py` sets physical zero by computing `offset = new_pos - current_pos`.")
    lines.append("- Runtime writes `servo_goal = command + offset` for the current all-`+1` joint directions.")
    lines.append("- Runtime reads `reported_position = servo_present - offset`.")
    lines.append("- `zero_pos` is all zeros; `init_pos` below must match the sim `home` keyframe.")
    lines.append("")
    lines.append("## Joint Targets")
    lines.append("")
    lines.append(
        "| idx | joint | side | physical joint | zero checked | home rad | home deg | live offset rad | home checked | notes |"
    )
    lines.append("|---:|---|---|---|---|---:|---:|---:|---|---|")
    for joint in joints:
        lines.append(
            "| {idx} | `{name}` | {side} | {physical} | [ ] | {home} | {deg} | {offset} | [ ] | |".format(
                idx=joint.get("policy_index", "NA"),
                name=joint.get("name", "UNKNOWN"),
                side=joint.get("side", "UNKNOWN"),
                physical=joint.get("physical_joint", "UNKNOWN"),
                home=fmt(joint.get("home_rad", "NA"), 4),
                deg=rad_to_deg(joint.get("home_rad")),
                offset=fmt(joint.get("real_zero_offset_rad", "NA"), 4),
            )
        )
    lines.append("")
    lines.append("## Soft-Offset Procedure")
    lines.append("")
    lines.append("- [ ] live `duck_config.json` backed up before any calibration")
    lines.append("- [ ] `find_soft_offsets.py` run/audited with robot supported")
    lines.append("- [ ] printed offsets saved in a log")
    lines.append("- [ ] old/new offsets compared before editing `duck_config.json`")
    lines.append("- [ ] changed offsets copied into `duck_config.json` only after review")
    lines.append("")
    lines.append("## Secondary Photos / Video")
    lines.append("")
    lines.append("- [ ] front view at home")
    lines.append("- [ ] left side view at home")
    lines.append("- [ ] right side view at home")
    lines.append("- [ ] rear view at home")
    lines.append("- [ ] close-up of left knee and ankle")
    lines.append("- [ ] close-up of right knee and ankle")
    lines.append("")
    lines.append("## Mechanical Checks")
    lines.append("")
    lines.append("- [ ] left knee geometry matches the expected home bend")
    lines.append("- [ ] right knee geometry matches the expected home bend")
    lines.append("- [ ] left/right knee geometry is symmetric enough to trust")
    lines.append("- [ ] left/right ankle geometry is symmetric enough to trust")
    lines.append("- [ ] feet are similarly placed relative to the body")
    lines.append("- [ ] no horn/link appears one tooth off")
    lines.append("- [ ] no cable strain is pulling a leg away from home")
    lines.append("")
    lines.append("## Telemetry Checks After Any Offset Change")
    lines.append("")
    lines.append("- [ ] new `duck_config.json` snapshot captured")
    lines.append("- [ ] `home_pose_log_test` rerun")
    lines.append("- [ ] joint tracking errors remain small")
    lines.append("- [ ] gyro stable")
    lines.append("- [ ] upright accel remains +Z dominant")
    lines.append("- [ ] no repeated bus read/write errors while holding home")
    lines.append("")
    lines.append("## Decision")
    lines.append("")
    lines.append("- [ ] PASS: physical home pose matches spec and telemetry passes")
    lines.append("- [ ] HOLD: physical pose is off, offsets changed without new telemetry, or left knee remains unexplained")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--joint-map", type=Path, default=DEFAULT_JOINT_MAP)
    parser.add_argument("--gate-doc", type=Path, default=DEFAULT_GATE)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    joints = load_joints(args.joint_map)
    if len(joints) != 14:
        raise SystemExit(f"expected 14 joints in {args.joint_map}, got {len(joints)}")
    sheet = build_sheet(joints, args.joint_map, args.gate_doc)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(sheet + "\n")
    else:
        print(sheet)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
