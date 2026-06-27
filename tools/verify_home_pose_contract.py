#!/usr/bin/env python3
"""Verify the offline sim/runtime home-pose contract.

This tool reads repository files only. It does not SSH, command motors, deploy
files, or edit configuration. Its job is to make the start-pose contract
auditable from source:

  runtime HWI.init_pos == Playground sim home keyframe ctrl
  normal raw servo home target = joint_dir * home + duck_config offset

It also reports why "raw sim-home" commands are not equivalent to runtime home
when nonzero soft offsets are configured.
"""

from __future__ import annotations

import argparse
import ast
import datetime as dt
import json
from pathlib import Path
import xml.etree.ElementTree as ET
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_HWI = (
    ROOT
    / "runtime"
    / "mini_bdx_runtime"
    / "mini_bdx_runtime"
    / "rustypot_position_hwi.py"
)
DEFAULT_SCENE_XML = (
    ROOT.parent
    / "Open_Duck_Playground"
    / "playground"
    / "open_duck_mini_v2"
    / "xmls"
    / "scene_flat_terrain.xml"
)
DEFAULT_CONFIG_SNAPSHOT = (
    ROOT
    / "outputs"
    / "first_evidence"
    / "20260627T003945Z_physical_start_pose_gate"
    / "20260627T003909Z_rdkx5_config_snapshot.json"
)


def fmt(value: Any, digits: int = 4) -> str:
    if value is None:
        return "NA"
    return f"{float(value):.{digits}f}"


def literal_dict_from_hwi(path: Path, attr_name: str) -> dict[str, float | int]:
    tree = ast.parse(path.read_text())
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if (
                isinstance(target, ast.Attribute)
                and target.attr == attr_name
                and isinstance(target.value, ast.Name)
                and target.value.id == "self"
            ):
                value = ast.literal_eval(node.value)
                if not isinstance(value, dict):
                    raise ValueError(f"self.{attr_name} in {path} is not a dict")
                return value
    raise ValueError(f"could not find self.{attr_name} assignment in {path}")


def parse_hwi(path: Path) -> dict[str, Any]:
    joints = literal_dict_from_hwi(path, "joints")
    zero_pos = literal_dict_from_hwi(path, "zero_pos")
    init_pos = literal_dict_from_hwi(path, "init_pos")
    joint_names = list(joints.keys())
    missing_zero = [name for name in joint_names if name not in zero_pos]
    missing_home = [name for name in joint_names if name not in init_pos]
    if missing_zero or missing_home:
        raise ValueError(
            f"HWI dictionaries do not align: missing_zero={missing_zero}, missing_home={missing_home}"
        )
    return {
        "path": str(path),
        "joint_names": joint_names,
        "servo_ids": {name: int(joints[name]) for name in joint_names},
        "zero_pos_rad": {name: float(zero_pos[name]) for name in joint_names},
        "init_pos_rad": {name: float(init_pos[name]) for name in joint_names},
        "joint_dirs": {name: 1.0 for name in joint_names},
        "joint_dir_source": "runtime source sets self.joints_dir = {name: 1.0 for name in self.joints}",
    }


def parse_home_ctrl(path: Path, joint_names: list[str]) -> dict[str, Any]:
    root = ET.parse(path).getroot()
    home_key = None
    for key in root.findall(".//key"):
        if key.attrib.get("name") == "home":
            home_key = key
            break
    if home_key is None:
        raise ValueError(f"no home keyframe found in {path}")
    ctrl = [float(value) for value in home_key.attrib.get("ctrl", "").split()]
    qpos = [float(value) for value in home_key.attrib.get("qpos", "").split()]
    if len(ctrl) != len(joint_names):
        raise ValueError(
            f"home keyframe ctrl length {len(ctrl)} does not match joints {len(joint_names)}"
        )
    return {
        "path": str(path),
        "source": "home keyframe ctrl",
        "ctrl_len": len(ctrl),
        "qpos_len": len(qpos),
        "home_rad": {name: float(ctrl[i]) for i, name in enumerate(joint_names)},
    }


def load_offsets(path: Path, joint_names: list[str]) -> dict[str, Any]:
    payload = json.loads(path.read_text())
    offsets = payload.get("joints_offsets")
    if offsets is None:
        offsets = (payload.get("duck_config") or {}).get("joints_offsets")
    if offsets is None:
        raise ValueError(f"could not find joints_offsets in {path}")
    missing = [name for name in joint_names if name not in offsets]
    if missing:
        raise ValueError(f"offset snapshot {path} missing joints: {missing}")
    return {
        "path": str(path),
        "sha256": payload.get("duck_config_sha256"),
        "offsets_rad": {name: float(offsets[name]) for name in joint_names},
    }


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    hwi = parse_hwi(Path(args.hwi_source))
    scene = parse_home_ctrl(Path(args.scene_xml), hwi["joint_names"])
    offsets = load_offsets(Path(args.config_snapshot), hwi["joint_names"])
    tolerance = float(args.tolerance_rad)

    rows = []
    max_abs_home_delta = 0.0
    max_abs_zero = 0.0
    max_abs_raw_bypass_delta = 0.0
    for index, name in enumerate(hwi["joint_names"]):
        runtime_home = float(hwi["init_pos_rad"][name])
        sim_home = float(scene["home_rad"][name])
        home_delta = runtime_home - sim_home
        zero = float(hwi["zero_pos_rad"][name])
        joint_dir = float(hwi["joint_dirs"][name])
        offset = float(offsets["offsets_rad"][name])
        normal_raw_home = joint_dir * sim_home + offset
        raw_bypass_home = joint_dir * sim_home
        raw_bypass_minus_normal = raw_bypass_home - normal_raw_home
        max_abs_home_delta = max(max_abs_home_delta, abs(home_delta))
        max_abs_zero = max(max_abs_zero, abs(zero))
        max_abs_raw_bypass_delta = max(
            max_abs_raw_bypass_delta, abs(raw_bypass_minus_normal)
        )
        rows.append(
            {
                "index": index,
                "joint": name,
                "servo_id": hwi["servo_ids"][name],
                "runtime_home_rad": runtime_home,
                "sim_home_rad": sim_home,
                "runtime_minus_sim_home_rad": home_delta,
                "runtime_zero_rad": zero,
                "joint_dir": joint_dir,
                "config_offset_rad": offset,
                "normal_raw_home_target_rad": normal_raw_home,
                "raw_bypass_home_target_rad": raw_bypass_home,
                "raw_bypass_minus_normal_home_rad": raw_bypass_minus_normal,
                "home_contract_ok": abs(home_delta) <= tolerance,
                "zero_contract_ok": abs(zero) <= tolerance,
            }
        )

    status = (
        "PASS_HOME_POSE_CONTRACT"
        if max_abs_home_delta <= tolerance and max_abs_zero <= tolerance
        else "HOLD_HOME_POSE_CONTRACT_MISMATCH"
    )
    return {
        "schema_version": "open_duck_home_pose_contract_audit_v1",
        "status": status,
        "created_utc": dt.datetime.now(dt.UTC).isoformat(),
        "tolerance_rad": tolerance,
        "hwi": hwi,
        "sim_home": scene,
        "offset_snapshot": offsets,
        "summary": {
            "max_abs_runtime_minus_sim_home_rad": max_abs_home_delta,
            "max_abs_runtime_zero_rad": max_abs_zero,
            "max_abs_raw_bypass_minus_normal_home_rad": max_abs_raw_bypass_delta,
            "home_mismatch_joints": [
                row["joint"] for row in rows if not row["home_contract_ok"]
            ],
            "zero_mismatch_joints": [
                row["joint"] for row in rows if not row["zero_contract_ok"]
            ],
        },
        "interpretation": {
            "home_contract": (
                "The deployed runtime HWI.init_pos values should match the "
                "Playground scene home keyframe ctrl values in policy action order."
            ),
            "normal_raw_home_target": (
                "This is the raw servo goal the runtime writes for sim home: "
                "joint_dir * sim_home + configured soft offset."
            ),
            "raw_bypass_home_target": (
                "This is the unsafe shortcut of sending sim_home directly as a "
                "raw servo value. It ignores configured soft offsets."
            ),
        },
        "rows": rows,
    }


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Home Pose Contract Audit",
        "",
        f"status: `{report['status']}`",
        f"tolerance_rad: `{report['tolerance_rad']}`",
        "",
        "This is an offline source/config audit. It does not SSH, command motors,",
        "deploy files, edit `duck_config.json`, or run a policy.",
        "",
        "## Summary",
        "",
        f"- max_abs_runtime_minus_sim_home_rad: `{fmt(report['summary']['max_abs_runtime_minus_sim_home_rad'])}`",
        f"- max_abs_runtime_zero_rad: `{fmt(report['summary']['max_abs_runtime_zero_rad'])}`",
        f"- max_abs_raw_bypass_minus_normal_home_rad: `{fmt(report['summary']['max_abs_raw_bypass_minus_normal_home_rad'])}`",
        f"- home_mismatch_joints: `{report['summary']['home_mismatch_joints']}`",
        f"- zero_mismatch_joints: `{report['summary']['zero_mismatch_joints']}`",
        "",
        "## Interpretation",
        "",
        "- Runtime `init_pos` matches sim `home` if `runtime_minus_sim_home_rad` is near zero.",
        "- Runtime raw home command is `joint_dir * sim_home + config_offset`.",
        "- Raw-bypass home command is just `joint_dir * sim_home`; it ignores offsets and is not a safe calibration shortcut.",
        "",
        "## Joint Table",
        "",
        "| idx | joint | id | runtime home | sim home | diff | offset | normal raw home | raw-bypass home | bypass-normal |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report["rows"]:
        lines.append(
            "| {idx} | `{joint}` | {servo_id} | {runtime} | {sim} | {diff} | {offset} | {normal} | {raw} | {delta} |".format(
                idx=row["index"],
                joint=row["joint"],
                servo_id=row["servo_id"],
                runtime=fmt(row["runtime_home_rad"]),
                sim=fmt(row["sim_home_rad"]),
                diff=fmt(row["runtime_minus_sim_home_rad"]),
                offset=fmt(row["config_offset_rad"]),
                normal=fmt(row["normal_raw_home_target_rad"]),
                raw=fmt(row["raw_bypass_home_target_rad"]),
                delta=fmt(row["raw_bypass_minus_normal_home_rad"]),
            )
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "This audit can prove the source-level sim/runtime home contract. It",
            "cannot prove that the physical robot was freshly calibrated to that",
            "contract. Physical proof still requires either the repo",
            "`find_soft_offsets.py` procedure or a read-only raw-position audit while",
            "the robot is independently placed in the repo-defined home geometry.",
            "",
            "Do not command raw-bypass sim home. Use the runtime compensated home",
            "command or the read-only raw audit instead.",
            "",
        ]
    )
    path.write_text("\n".join(lines))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hwi-source", default=str(DEFAULT_HWI))
    parser.add_argument("--scene-xml", default=str(DEFAULT_SCENE_XML))
    parser.add_argument("--config-snapshot", default=str(DEFAULT_CONFIG_SNAPSHOT))
    parser.add_argument("--tolerance-rad", type=float, default=1e-9)
    parser.add_argument(
        "--output-json",
        default="outputs/analysis/home_pose_contract_audit.json",
    )
    parser.add_argument(
        "--output-md",
        default="outputs/analysis/HOME_POSE_CONTRACT_AUDIT.md",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report(args)
    output_json = Path(args.output_json)
    output_md = Path(args.output_md)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(report, indent=2) + "\n")
    write_markdown(output_md, report)
    print(report["status"])
    print(f"wrote {output_md}")
    print(f"wrote {output_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
