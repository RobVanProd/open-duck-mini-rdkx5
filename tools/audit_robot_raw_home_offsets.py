#!/usr/bin/env python3
"""Audit raw servo positions against the sim home keyframe.

This is a read-only robot-side calibration audit. It does not command motion,
change torque, edit duck_config.json, deploy files, or run a policy.

Important interpretation:

  implied_offset = raw_present_position - sim_home

is the missing/current soft offset only if the robot is physically placed in
the repo-defined sim-home geometry independently of the current offsets. If the
current runtime first commanded home using duck_config.json, then the same
calculation mostly re-derives the current configured offset plus servo tracking
error.
"""

from __future__ import annotations

import argparse
import base64
import datetime as dt
import json
import math
import os
from pathlib import Path
import shlex
import subprocess
import textwrap
import xml.etree.ElementTree as ET
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PLAYGROUND = ROOT.parent / "Open_Duck_Playground"
DEFAULT_SCENE_XML = (
    DEFAULT_PLAYGROUND
    / "playground"
    / "open_duck_mini_v2"
    / "xmls"
    / "scene_flat_terrain.xml"
)
DEFAULT_ROBOT_RUNTIME = "/home/sunrise/project/Open_Duck_Mini_Runtime-2_RDK_X5"
DEFAULT_ROBOT_PYTHON = "/home/sunrise/duck_env/bin/python"
DEFAULT_ROBOT_CONFIG = "/home/sunrise/duck_config.json"

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


def timestamp() -> str:
    return dt.datetime.now(dt.UTC).strftime("%Y%m%dT%H%M%SZ")


def fmt(value: Any, digits: int = 4) -> str:
    if value is None:
        return "NA"
    return f"{float(value):.{digits}f}"


def shell_join(command: list[str]) -> str:
    return " ".join(shlex.quote(part) for part in command)


def parse_home_from_scene_xml(path: Path) -> dict[str, Any]:
    root = ET.parse(path).getroot()
    key = None
    for candidate in root.findall(".//key"):
        if candidate.attrib.get("name") == "home":
            key = candidate
            break
    if key is None:
        raise ValueError(f"no keyframe named home in {path}")
    qpos = [float(item) for item in key.attrib.get("qpos", "").split()]
    ctrl = [float(item) for item in key.attrib.get("ctrl", "").split()]
    if len(ctrl) == len(JOINT_NAMES):
        home = ctrl
        source = "home keyframe ctrl"
    elif len(qpos) >= 7 + len(JOINT_NAMES):
        home = qpos[7 : 7 + len(JOINT_NAMES)]
        source = "home keyframe qpos[7:21]"
    else:
        raise ValueError(
            f"home keyframe does not contain 14 actuator values: qpos={len(qpos)} ctrl={len(ctrl)}"
        )
    return {
        "scene_xml": str(path),
        "source": source,
        "joint_names": JOINT_NAMES,
        "home_rad": home,
        "qpos_len": len(qpos),
        "ctrl_len": len(ctrl),
    }


def remote_read_command(args: argparse.Namespace) -> list[str]:
    remote_code = f"""
import json
import os
import sys
from pathlib import Path

runtime = Path({args.robot_runtime!r})
if runtime.exists():
    sys.path.insert(0, str(runtime))
    sys.path.insert(0, str(runtime / "scripts"))

from mini_bdx_runtime.duck_config import DuckConfig
from mini_bdx_runtime.rustypot_position_hwi import HWI

cfg = DuckConfig(config_json_path={args.robot_config!r})
hwi = HWI(cfg)
joint_names = list(hwi.joints.keys())
servo_ids = list(hwi.joints.values())
raw = hwi._retry(hwi.io.read_present_position, servo_ids)
out = {{
    "schema_version": "open_duck_raw_home_offset_audit_v1",
    "robot_runtime": str(runtime),
    "robot_config": {args.robot_config!r},
    "joint_names": joint_names,
    "servo_ids": servo_ids,
    "raw_present_position_rad": [float(x) for x in raw],
    "config_offsets_rad": [float(hwi.joints_offsets[name]) for name in joint_names],
    "joint_dirs": [float(hwi.joints_dir[name]) for name in joint_names],
    "runtime_init_pos_rad": [float(hwi.init_pos[name]) for name in joint_names],
    "read_only": True,
    "motion_commanded": False,
    "torque_changed": False,
}}
print(json.dumps(out, sort_keys=True))
"""
    encoded = base64.b64encode(remote_code.encode()).decode()
    ssh = [
        "ssh",
        "-o",
        "BatchMode=yes",
        "-o",
        f"ConnectTimeout={args.connect_timeout_s}",
    ]
    if args.identity_file:
        ssh.extend(["-i", os.path.expanduser(args.identity_file)])
    if args.known_hosts:
        ssh.extend(["-o", f"UserKnownHostsFile={os.path.expanduser(args.known_hosts)}"])
    if args.strict_host_key_checking:
        ssh.extend(["-o", f"StrictHostKeyChecking={args.strict_host_key_checking}"])
    ssh.extend(
        [
            args.ssh,
            str(args.robot_python),
            "-c",
            "import base64; exec(base64.b64decode(%r).decode())" % encoded,
        ]
    )
    return ssh


def read_robot(args: argparse.Namespace) -> dict[str, Any]:
    if not args.ssh:
        raise ValueError("--ssh is required for robot raw-position reads")
    command = remote_read_command(args)
    proc = subprocess.run(
        command,
        text=True,
        capture_output=True,
        timeout=args.timeout_s,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip())
    lines = [line for line in proc.stdout.splitlines() if line.strip()]
    if not lines:
        raise RuntimeError("robot raw-position read produced no stdout")
    return json.loads(lines[-1])


def build_report(
    *,
    sim_home: dict[str, Any],
    robot: dict[str, Any],
    pose_source: str,
    tolerance_rad: float,
) -> dict[str, Any]:
    names = list(robot["joint_names"])
    if names != JOINT_NAMES:
        raise ValueError(f"unexpected robot joint order: {names}")
    sim = [float(value) for value in sim_home["home_rad"]]
    raw = [float(value) for value in robot["raw_present_position_rad"]]
    offsets = [float(value) for value in robot["config_offsets_rad"]]
    dirs = [float(value) for value in robot["joint_dirs"]]
    runtime_home = [float(value) for value in robot["runtime_init_pos_rad"]]

    rows = []
    max_abs_config_delta = 0.0
    max_abs_compensated_delta = 0.0
    for i, name in enumerate(names):
        # General formula: raw = dir * joint_position + offset.
        implied_offset = raw[i] - dirs[i] * sim[i]
        config_delta = implied_offset - offsets[i]
        compensated_position = dirs[i] * (raw[i] - offsets[i])
        compensated_delta = compensated_position - sim[i]
        rows.append(
            {
                "index": i,
                "joint": name,
                "servo_id": int(robot["servo_ids"][i]),
                "sim_home_rad": sim[i],
                "runtime_init_pos_rad": runtime_home[i],
                "raw_present_position_rad": raw[i],
                "config_offset_rad": offsets[i],
                "implied_offset_if_physical_home_rad": implied_offset,
                "implied_minus_config_offset_rad": config_delta,
                "compensated_position_rad": compensated_position,
                "compensated_minus_sim_home_rad": compensated_delta,
                "within_tolerance": abs(config_delta) <= tolerance_rad,
            }
        )
        max_abs_config_delta = max(max_abs_config_delta, abs(config_delta))
        max_abs_compensated_delta = max(max_abs_compensated_delta, abs(compensated_delta))

    if pose_source == "physically_aligned_home":
        status = (
            "PASS_RAW_HOME_OFFSET_AUDIT"
            if max_abs_config_delta <= tolerance_rad
            else "HOLD_RAW_HOME_OFFSET_MISMATCH"
        )
    elif pose_source == "commanded_home":
        status = "INFO_COMMANDED_HOME_RAW_OFFSET_AUDIT"
    else:
        status = "INFO_RAW_HOME_OFFSET_AUDIT_POSE_SOURCE_UNKNOWN"

    return {
        "schema_version": "open_duck_raw_home_offset_audit_report_v1",
        "status": status,
        "created_utc": dt.datetime.now(dt.UTC).isoformat(),
        "pose_source": pose_source,
        "tolerance_rad": float(tolerance_rad),
        "interpretation": {
            "implied_offset_if_physical_home_rad": (
                "raw_present_position - joint_dir * sim_home. This is a candidate soft "
                "offset only when the robot was physically placed in sim-home geometry "
                "independently of the current offsets."
            ),
            "implied_minus_config_offset_rad": (
                "candidate offset minus current duck_config offset. If pose_source is "
                "commanded_home, this is mostly compensated tracking error, not proof "
                "that physical zero is correct."
            ),
            "compensated_minus_sim_home_rad": (
                "runtime get_present_positions()-style readback minus sim home."
            ),
        },
        "sim_home": sim_home,
        "robot_read": robot,
        "summary": {
            "max_abs_implied_minus_config_offset_rad": max_abs_config_delta,
            "max_abs_compensated_minus_sim_home_rad": max_abs_compensated_delta,
            "joints_over_tolerance": [
                row["joint"] for row in rows if not row["within_tolerance"]
            ],
        },
        "rows": rows,
    }


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Raw Servo Home Offset Audit",
        "",
        f"status: `{report['status']}`",
        f"pose_source: `{report['pose_source']}`",
        f"tolerance_rad: `{report['tolerance_rad']}`",
        "",
        "This is a read-only audit. It does not command motion, change torque,",
        "edit `duck_config.json`, deploy files, or run a policy.",
        "",
        "## Interpretation",
        "",
        "`implied_offset_if_physical_home_rad = raw_present_position - joint_dir * sim_home`.",
        "",
        "That value is a candidate/missing soft offset only if the robot was",
        "physically placed in the repo-defined sim-home geometry independently of",
        "the current offsets. If the robot was first commanded to home with the",
        "current config, the same difference mostly re-derives the current offset",
        "plus tracking error.",
        "",
        "## Summary",
        "",
        f"- max_abs_implied_minus_config_offset_rad: `{fmt(report['summary']['max_abs_implied_minus_config_offset_rad'])}`",
        f"- max_abs_compensated_minus_sim_home_rad: `{fmt(report['summary']['max_abs_compensated_minus_sim_home_rad'])}`",
        f"- joints_over_tolerance: `{report['summary']['joints_over_tolerance']}`",
        "",
        "## Joint Table",
        "",
        "| idx | joint | id | sim home | raw present | config offset | implied offset | implied-config | compensated-sim | ok |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in report["rows"]:
        lines.append(
            "| {idx} | `{joint}` | {servo_id} | {sim} | {raw} | {cfg} | {impl} | {delta} | {comp} | `{ok}` |".format(
                idx=row["index"],
                joint=row["joint"],
                servo_id=row["servo_id"],
                sim=fmt(row["sim_home_rad"]),
                raw=fmt(row["raw_present_position_rad"]),
                cfg=fmt(row["config_offset_rad"]),
                impl=fmt(row["implied_offset_if_physical_home_rad"]),
                delta=fmt(row["implied_minus_config_offset_rad"]),
                comp=fmt(row["compensated_minus_sim_home_rad"]),
                ok=row["within_tolerance"],
            )
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "If this was a true physically-aligned-home read and any joint is over",
            "tolerance, do not walk the robot. Re-run the repo `find_soft_offsets.py`",
            "procedure or manually update offsets only after backing up the current",
            "config and recording the new values.",
            "",
            "If this was a commanded-home read, use this only as a raw/readback",
            "sanity check. It does not independently prove the physical zero because",
            "the same configured offsets were used to command the pose.",
            "",
        ]
    )
    path.write_text("\n".join(lines))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Read raw servo positions and compare implied offsets against sim home."
    )
    parser.add_argument("--ssh", default=None, help="Robot SSH target, e.g. sunrise@duck")
    parser.add_argument("--identity-file", default="/home/lsd/robots/.duck_access/rdk_key")
    parser.add_argument("--known-hosts", default="/home/lsd/robots/.duck_access/known_hosts")
    parser.add_argument(
        "--strict-host-key-checking",
        choices=["yes", "no", "accept-new"],
        default="yes",
    )
    parser.add_argument("--connect-timeout-s", type=int, default=5)
    parser.add_argument("--timeout-s", type=int, default=20)
    parser.add_argument("--robot-runtime", default=DEFAULT_ROBOT_RUNTIME)
    parser.add_argument("--robot-python", default=DEFAULT_ROBOT_PYTHON)
    parser.add_argument("--robot-config", default=DEFAULT_ROBOT_CONFIG)
    parser.add_argument("--scene-xml", default=str(DEFAULT_SCENE_XML))
    parser.add_argument(
        "--pose-source",
        choices=["unknown", "commanded_home", "physically_aligned_home"],
        default="unknown",
        help=(
            "How the robot was placed before the read. Use physically_aligned_home "
            "only if the pose was set by physical alignment, not by trusting current offsets."
        ),
    )
    parser.add_argument("--tolerance-rad", type=float, default=0.01745)
    parser.add_argument("--output-json", default=None)
    parser.add_argument("--output-md", default=None)
    parser.add_argument("--print-command-only", action="store_true")
    args = parser.parse_args()

    sim_home = parse_home_from_scene_xml(Path(args.scene_xml))
    if args.print_command_only:
        command = remote_read_command(args)
        print(shell_join(command))
        return 0

    robot = read_robot(args)
    report = build_report(
        sim_home=sim_home,
        robot=robot,
        pose_source=args.pose_source,
        tolerance_rad=args.tolerance_rad,
    )
    output_json = Path(args.output_json) if args.output_json else (
        ROOT / "outputs" / "analysis" / f"raw_home_offset_audit_{timestamp()}.json"
    )
    output_md = Path(args.output_md) if args.output_md else output_json.with_suffix(".md")
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(report, indent=2) + "\n")
    write_markdown(output_md, report)
    print(report["status"])
    print(f"wrote {output_md}")
    print(f"wrote {output_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
