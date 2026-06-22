#!/usr/bin/env python3
"""Audit Open Duck MJCF/MuJoCo model features without stepping MJX."""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PLAYGROUND = ROOT.parent / "Open_Duck_Playground"
DEFAULT_XML = (
    DEFAULT_PLAYGROUND
    / "playground"
    / "open_duck_mini_v2"
    / "xmls"
    / "scene_flat_terrain.xml"
)
DEFAULT_OUTPUT_MD = ROOT / "outputs" / "analysis" / "ROCM_MJX_MODEL_FEATURE_AUDIT.md"
DEFAULT_OUTPUT_JSON = ROOT / "outputs" / "analysis" / "rocm_mjx_model_feature_audit.json"


CONTACT_ATTRS = [
    "name",
    "type",
    "class",
    "group",
    "contype",
    "conaffinity",
    "condim",
    "friction",
    "solref",
    "solimp",
    "priority",
    "mesh",
]


def parse_xml(path: Path) -> ET.Element:
    return ET.fromstring(path.read_text())


def collect_xml_files(path: Path, seen: set[Path] | None = None) -> list[Path]:
    seen = seen or set()
    path = path.resolve()
    if path in seen:
        return []
    seen.add(path)
    files = [path]
    root = parse_xml(path)
    for include in root.iter("include"):
        include_file = include.attrib.get("file")
        if not include_file:
            continue
        files.extend(collect_xml_files(path.parent / include_file, seen))
    return files


def is_contact_relevant(elem: ET.Element) -> bool:
    if elem.tag == "pair":
        return True
    name = elem.attrib.get("name", "")
    return (
        elem.attrib.get("contype") not in (None, "0")
        or elem.attrib.get("conaffinity") not in (None, "0")
        or elem.attrib.get("condim") is not None
        or name in {"floor", "left_foot_bottom_tpu", "right_foot_bottom_tpu"}
    )


def static_xml_audit(xml_path: Path) -> dict[str, Any]:
    files = collect_xml_files(xml_path)
    tag_counts: Counter[str] = Counter()
    geom_types: Counter[str] = Counter()
    geom_classes: Counter[str] = Counter()
    mesh_assets = []
    mesh_geoms = []
    contact_items = []
    keyframes = []
    sensors = []
    actuators = []
    joints = []
    defaults = []

    for path in files:
        root = parse_xml(path)
        for elem in root.iter():
            tag_counts[elem.tag] += 1
            if elem.tag == "geom":
                geom_types[elem.attrib.get("type", "default")] += 1
                geom_classes[elem.attrib.get("class", "none")] += 1
                if elem.attrib.get("type") == "mesh" or elem.attrib.get("mesh"):
                    mesh_geoms.append({"file": str(path), **elem.attrib})
                if is_contact_relevant(elem):
                    contact_items.append(
                        {"file": str(path), "tag": elem.tag}
                        | {key: elem.attrib.get(key) for key in CONTACT_ATTRS}
                    )
            elif elem.tag == "mesh":
                mesh_assets.append({"file": str(path), **elem.attrib})
            elif elem.tag == "key":
                ctrl_values = (elem.attrib.get("ctrl") or "").split()
                qpos_values = (elem.attrib.get("qpos") or "").split()
                keyframes.append(
                    {
                        "file": str(path),
                        "name": elem.attrib.get("name"),
                        "ctrl_len": len(ctrl_values),
                        "qpos_len": len(qpos_values),
                    }
                )
            elif elem.tag in {
                "gyro",
                "velocimeter",
                "accelerometer",
                "framezaxis",
                "framexaxis",
                "framelinvel",
                "frameangvel",
                "framepos",
                "framequat",
            }:
                sensors.append({"file": str(path), "tag": elem.tag, **elem.attrib})
            elif elem.tag == "position":
                actuators.append({"file": str(path), "tag": elem.tag, **elem.attrib})
            elif elem.tag == "joint":
                joints.append({"file": str(path), **elem.attrib})
            elif elem.tag == "default":
                defaults.append({"file": str(path), **elem.attrib})

    missing_solref = [item for item in contact_items if item.get("solref") is None]
    missing_solimp = [item for item in contact_items if item.get("solimp") is None]
    return {
        "xml_path": str(xml_path),
        "included_files": [str(path) for path in files],
        "tag_counts": dict(sorted(tag_counts.items())),
        "geom_types": dict(sorted(geom_types.items())),
        "geom_classes": dict(sorted(geom_classes.items())),
        "mesh_asset_count": len(mesh_assets),
        "mesh_geom_count": len(mesh_geoms),
        "mesh_assets": mesh_assets,
        "contact_relevant_items": contact_items,
        "missing_solref_count": len(missing_solref),
        "missing_solimp_count": len(missing_solimp),
        "floor_items": [item for item in contact_items if item.get("name") == "floor"],
        "foot_contact_items": [
            item
            for item in contact_items
            if item.get("name") in {"left_foot_bottom_tpu", "right_foot_bottom_tpu"}
        ],
        "keyframes": keyframes,
        "sensor_count": len(sensors),
        "sensors": sensors,
        "position_actuator_defaults": actuators,
        "joint_count_static": len(joints),
        "joints": joints,
        "default_classes": defaults,
    }


def mujoco_compile_audit(xml_path: Path) -> dict[str, Any]:
    try:
        import mujoco
    except Exception as exc:
        return {
            "status": "HOLD_MUJOCO_IMPORT_MISSING",
            "error": f"{type(exc).__name__}: {exc}",
        }

    try:
        model = mujoco.MjModel.from_xml_path(str(xml_path))
    except Exception as exc:
        return {
            "status": "HOLD_MUJOCO_COMPILE_FAILED",
            "error": f"{type(exc).__name__}: {exc}",
        }

    def name_for(obj_type: int, idx: int) -> str:
        return mujoco.mj_id2name(model, obj_type, idx) or f"<unnamed_{idx}>"

    geom_rows = []
    geom_type_counts: Counter[str] = Counter()
    for geom_id in range(model.ngeom):
        geom_name = name_for(mujoco.mjtObj.mjOBJ_GEOM, geom_id)
        geom_type_id = int(model.geom_type[geom_id])
        geom_type_name = mujoco.mjtGeom(geom_type_id).name.replace("mjGEOM_", "").lower()
        geom_type_counts[geom_type_name] += 1
        row = {
            "id": geom_id,
            "name": geom_name,
            "type": geom_type_name,
            "body": name_for(mujoco.mjtObj.mjOBJ_BODY, int(model.geom_bodyid[geom_id])),
            "contype": int(model.geom_contype[geom_id]),
            "conaffinity": int(model.geom_conaffinity[geom_id]),
            "condim": int(model.geom_condim[geom_id]),
            "priority": int(model.geom_priority[geom_id]),
            "friction": [float(x) for x in model.geom_friction[geom_id]],
            "solref": [float(x) for x in model.geom_solref[geom_id]],
            "solimp": [float(x) for x in model.geom_solimp[geom_id]],
        }
        if row["contype"] or row["conaffinity"] or row["name"] in {
            "floor",
            "left_foot_bottom_tpu",
            "right_foot_bottom_tpu",
        }:
            geom_rows.append(row)

    joint_rows = []
    for joint_id in range(model.njnt):
        joint_rows.append(
            {
                "id": joint_id,
                "name": name_for(mujoco.mjtObj.mjOBJ_JOINT, joint_id),
                "type": int(model.jnt_type[joint_id]),
                "range": [float(x) for x in model.jnt_range[joint_id]],
            }
        )

    actuator_rows = []
    for actuator_id in range(model.nu):
        actuator_rows.append(
            {
                "id": actuator_id,
                "name": name_for(mujoco.mjtObj.mjOBJ_ACTUATOR, actuator_id),
                "ctrlrange": [float(x) for x in model.actuator_ctrlrange[actuator_id]],
                "forcerange": [float(x) for x in model.actuator_forcerange[actuator_id]],
                "gear": [float(x) for x in model.actuator_gear[actuator_id]],
            }
        )

    keyframes = []
    for key_id in range(model.nkey):
        keyframes.append(
            {
                "id": key_id,
                "name": name_for(mujoco.mjtObj.mjOBJ_KEY, key_id),
                "qpos_len": int(model.key_qpos[key_id].shape[0]),
                "ctrl_len": int(model.key_ctrl[key_id].shape[0]),
            }
        )

    sensor_rows = []
    for sensor_id in range(model.nsensor):
        sensor_rows.append(
            {
                "id": sensor_id,
                "name": name_for(mujoco.mjtObj.mjOBJ_SENSOR, sensor_id),
                "dim": int(model.sensor_dim[sensor_id]),
                "adr": int(model.sensor_adr[sensor_id]),
                "type": int(model.sensor_type[sensor_id]),
            }
        )

    return {
        "status": "PASS_MUJOCO_COMPILE",
        "mujoco_version": getattr(mujoco, "__version__", None),
        "counts": {
            "nq": int(model.nq),
            "nv": int(model.nv),
            "nu": int(model.nu),
            "nbody": int(model.nbody),
            "njnt": int(model.njnt),
            "ngeom": int(model.ngeom),
            "nsite": int(model.nsite),
            "nsensor": int(model.nsensor),
            "nmesh": int(model.nmesh),
            "npair": int(model.npair),
            "neq": int(model.neq),
            "nkey": int(model.nkey),
        },
        "option": {
            "timestep": float(model.opt.timestep),
            "iterations": int(model.opt.iterations),
            "ls_iterations": int(model.opt.ls_iterations),
            "integrator": int(model.opt.integrator),
            "cone": int(model.opt.cone),
            "jacobian": int(model.opt.jacobian),
            "solver": int(model.opt.solver),
        },
        "geom_type_counts": dict(sorted(geom_type_counts.items())),
        "contact_geoms": geom_rows,
        "joint_rows": joint_rows,
        "actuator_rows": actuator_rows,
        "keyframes": keyframes,
        "sensors": sensor_rows,
    }


def build_markdown(payload: dict[str, Any]) -> str:
    static = payload["static_xml"]
    compiled = payload["compiled_model"]
    counts = compiled.get("counts") or {}
    lines = [
        "# ROCm MJX Model Feature Audit",
        "",
        f"xml: `{payload['xml_path']}`",
        f"playground_path: `{payload['playground_path']}`",
        "",
        "## Executive Summary",
        "",
        f"- compile_status: `{compiled.get('status')}`",
        f"- compiled nq/nv/nu: `{counts.get('nq')}/{counts.get('nv')}/{counts.get('nu')}`",
        f"- compiled bodies/joints/geoms/sites/sensors: `{counts.get('nbody')}/{counts.get('njnt')}/{counts.get('ngeom')}/{counts.get('nsite')}/{counts.get('nsensor')}`",
        f"- static mesh assets/geoms: `{static['mesh_asset_count']}/{static['mesh_geom_count']}`",
        f"- static contact-relevant items: `{len(static['contact_relevant_items'])}`",
        f"- contact items missing explicit solref/solimp: `{static['missing_solref_count']}/{static['missing_solimp_count']}`",
        "",
        "This audit does not step physics. It is safe for offline ROCm/MJX",
        "debugging and does not involve robot hardware, SSH, deployment, or",
        "training.",
        "",
        "## Compiled Counts",
        "",
        "| field | value |",
        "|---|---:|",
    ]
    for key, value in (compiled.get("counts") or {}).items():
        lines.append(f"| `{key}` | {value} |")
    lines.extend(["", "## MuJoCo Options", "", "| option | value |", "|---|---:|"])
    for key, value in (compiled.get("option") or {}).items():
        lines.append(f"| `{key}` | {value} |")
    lines.extend(
        [
            "",
            "## Contact-Relevant Geoms",
            "",
            "| name | type | body | contype | conaffinity | condim | friction | solref | solimp |",
            "|---|---|---|---:|---:|---:|---|---|---|",
        ]
    )
    for row in compiled.get("contact_geoms") or []:
        lines.append(
            f"| `{row['name']}` | `{row['type']}` | `{row['body']}` | "
            f"{row['contype']} | {row['conaffinity']} | {row['condim']} | "
            f"`{row['friction']}` | `{row['solref']}` | `{row['solimp']}` |"
        )
    lines.extend(
        [
            "",
            "## Static Contact Items",
            "",
            "| file | name | tag | type | class | contype | conaffinity | condim | friction | solref | solimp |",
            "|---|---|---|---|---|---|---|---|---|---|---|",
        ]
    )
    for row in static["contact_relevant_items"]:
        lines.append(
            f"| `{Path(row['file']).name}` | `{row.get('name')}` | `{row.get('tag')}` | "
            f"`{row.get('type')}` | `{row.get('class')}` | `{row.get('contype')}` | "
            f"`{row.get('conaffinity')}` | `{row.get('condim')}` | "
            f"`{row.get('friction')}` | `{row.get('solref')}` | `{row.get('solimp')}` |"
        )
    lines.extend(
        [
            "",
            "## Actuator Order",
            "",
            "| id | name | ctrlrange | forcerange |",
            "|---:|---|---|---|",
        ]
    )
    for row in compiled.get("actuator_rows") or []:
        lines.append(
            f"| {row['id']} | `{row['name']}` | `{row['ctrlrange']}` | `{row['forcerange']}` |"
        )
    lines.extend(
        [
            "",
            "## Sensors",
            "",
            "| id | name | dim | adr | type |",
            "|---:|---|---:|---:|---:|",
        ]
    )
    for row in compiled.get("sensors") or []:
        lines.append(
            f"| {row['id']} | `{row['name']}` | {row['dim']} | {row['adr']} | {row['type']} |"
        )
    lines.extend(
        [
            "",
            "## ROCm Debugging Interpretation",
            "",
            "- The model compiles and can be reset in compatible local envs, while the",
            "  local 7900 XTX hold appears at `mjx_env.step(...)`.",
            "- The audit highlights the candidate feature area for future minimization:",
            "  mesh foot collision against the floor plane plus reset-time collision",
            "  checks.",
            "- CPU and CUDA remain valid correctness paths; this audit is only for the",
            "  local ROCm backend-debug workstream.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit Open Duck MJCF model features without stepping physics."
    )
    parser.add_argument("--playground-path", type=Path, default=DEFAULT_PLAYGROUND)
    parser.add_argument("--xml", type=Path, default=DEFAULT_XML)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    args = parser.parse_args()

    args.playground_path = args.playground_path.expanduser().absolute()
    args.xml = args.xml.expanduser().absolute()
    args.output_md = args.output_md.expanduser().absolute()
    args.output_json = args.output_json.expanduser().absolute()

    if not args.xml.exists():
        raise SystemExit(f"XML file not found: {args.xml}")

    payload = {
        "mission": "Open Duck MJX model feature audit",
        "playground_path": str(args.playground_path),
        "xml_path": str(args.xml),
        "python": sys.version,
        "static_xml": static_xml_audit(args.xml),
        "compiled_model": mujoco_compile_audit(args.xml),
    }
    args.output_md.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_md.write_text(build_markdown(payload))
    args.output_json.write_text(json.dumps(payload, indent=2) + "\n")
    print(args.output_md)
    print(args.output_json)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
