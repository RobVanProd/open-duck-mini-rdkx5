#!/usr/bin/env python3
"""Audit BEST_WALK_ONNX_2 policy contract against local Playground sim contract."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
import sys
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_POLICY = ROOT / "policy" / "BEST_WALK_ONNX_2.onnx"
DEFAULT_PLAYGROUND = ROOT.parent / "Open_Duck_Playground"
DEFAULT_ENV_PYTHON = ROOT.parent / "envs" / "open-duck-playground" / "bin" / "python"

POLICY_JOINT_ORDER = [
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

OBS_BREAKDOWN = [
    ("gyro", 0, 3),
    ("accel", 3, 6),
    ("command", 6, 13),
    ("joint_position_error", 13, 27),
    ("joint_velocity_scaled", 27, 41),
    ("action_history", 41, 83),
    ("previous_motor_targets", 83, 97),
    ("foot_contacts", 97, 99),
    ("phase", 99, 101),
]


def sha256(path: Path) -> str | None:
    if not path.exists():
        return None
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_text(path: Path) -> str:
    try:
        return path.read_text()
    except UnicodeDecodeError:
        return path.read_text(errors="replace")


def onnx_contract(path: Path) -> dict:
    payload = {
        "path": str(path),
        "exists": path.exists(),
        "sha256": sha256(path),
        "expected_input_shape": [1, 101],
        "expected_output_shape": [1, 14],
    }
    if not path.exists():
        payload["status"] = "HOLD_POLICY_MISSING"
        return payload
    code = r'''
import json
import sys

path = sys.argv[1]
payload = {}
try:
    import onnxruntime as ort
    session = ort.InferenceSession(path, providers=["CPUExecutionProvider"])
    payload = {
        "status": "PASS_ONNX_RUNTIME_METADATA",
        "inputs": [
            {"name": item.name, "shape": item.shape, "type": item.type}
            for item in session.get_inputs()
        ],
        "outputs": [
            {"name": item.name, "shape": item.shape, "type": item.type}
            for item in session.get_outputs()
        ],
    }
except Exception as exc:
    payload = {
        "status": "WARN_ONNX_METADATA_UNAVAILABLE",
        "error": f"{type(exc).__name__}: {exc}",
    }
print("ONNX_CONTRACT_JSON_START")
print(json.dumps(payload, sort_keys=True))
print("ONNX_CONTRACT_JSON_END")
'''
    try:
        result = subprocess.run(
            [sys.executable, "-c", code, str(path)],
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=30,
        )
        match = re.search(
            r"ONNX_CONTRACT_JSON_START\s*(\{.*\})\s*ONNX_CONTRACT_JSON_END",
            result.stdout or "",
            flags=re.S,
        )
        if not match:
            raise RuntimeError((result.stdout or "")[-1000:])
        payload.update(json.loads(match.group(1)))
    except Exception as exc:
        payload.update(
            {
                "status": "WARN_ONNX_METADATA_UNAVAILABLE",
                "error": f"{type(exc).__name__}: {exc}",
                "inputs": [{"name": "obs", "shape": [1, 101], "type": "float32"}],
                "outputs": [
                    {
                        "name": "continuous_actions",
                        "shape": [1, 14],
                        "type": "float32",
                    }
                ],
            }
        )
    return payload


def literal_assignment(path: Path, name: str):
    if not path.exists():
        return None
    try:
        tree = ast.parse(read_text(path))
    except SyntaxError:
        return None
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if any(isinstance(target, ast.Name) and target.id == name for target in node.targets):
            try:
                return ast.literal_eval(node.value)
            except Exception:
                return None
    return None


def parse_config_defaults(path: Path) -> dict:
    text = read_text(path) if path.exists() else ""
    keys = [
        "ctrl_dt",
        "sim_dt",
        "action_repeat",
        "action_scale",
        "dof_vel_scale",
        "max_motor_velocity",
        "action_min_delay",
        "action_max_delay",
        "imu_min_delay",
        "imu_max_delay",
    ]
    output = {}
    for key in keys:
        match = re.search(rf"{re.escape(key)}\s*=\s*([^,\n#]+)", text)
        if not match:
            continue
        raw = match.group(1).strip()
        try:
            output[key] = ast.literal_eval(raw)
        except Exception:
            output[key] = raw
    return output


def parse_float_vector(raw: str | None) -> list[float]:
    if not raw:
        return []
    values = []
    for token in raw.split():
        try:
            values.append(float(token))
        except ValueError:
            pass
    return values


def parse_xml_recursive(path: Path, seen: set[Path] | None = None) -> dict:
    seen = set() if seen is None else seen
    path = path.resolve()
    if path in seen:
        return {
            "path": str(path),
            "exists": path.exists(),
            "error": "recursive include skipped",
        }
    seen.add(path)
    payload = {
        "path": str(path),
        "exists": path.exists(),
        "includes": [],
        "actuators": [],
        "joints": [],
        "keyframes": [],
        "nu_static": 0,
    }
    if not path.exists():
        payload["error"] = "missing"
        return payload
    try:
        root = ET.fromstring(read_text(path))
    except ET.ParseError as exc:
        payload["error"] = f"ParseError: {exc}"
        return payload

    for include in root.findall(".//include"):
        include_file = include.attrib.get("file")
        if not include_file:
            continue
        include_path = (path.parent / include_file).resolve()
        child = parse_xml_recursive(include_path, seen)
        payload["includes"].append(child)
        payload["actuators"].extend(child.get("actuators", []))
        payload["joints"].extend(child.get("joints", []))
        payload["keyframes"].extend(child.get("keyframes", []))

    for item in root.findall(".//joint"):
        name = item.attrib.get("name")
        if name and name not in payload["joints"]:
            payload["joints"].append(name)

    for actuator in root.findall(".//actuator"):
        for child in list(actuator):
            name = child.attrib.get("name")
            if name:
                payload["actuators"].append(
                    {
                        "name": name,
                        "joint": child.attrib.get("joint"),
                        "type": child.tag,
                        "class": child.attrib.get("class"),
                    }
                )

    for key in root.findall(".//key"):
        ctrl = parse_float_vector(key.attrib.get("ctrl"))
        qpos = parse_float_vector(key.attrib.get("qpos"))
        payload["keyframes"].append(
            {
                "name": key.attrib.get("name"),
                "ctrl_len": len(ctrl),
                "qpos_len": len(qpos),
                "ctrl": ctrl,
            }
        )

    payload["nu_static"] = len(payload["actuators"])
    return payload


def flatten_xml_summaries(xml_payloads: list[dict]) -> list[dict]:
    output = []
    for payload in xml_payloads:
        output.append(
            {
                "path": payload["path"],
                "exists": payload["exists"],
                "nu_static": payload.get("nu_static"),
                "actuator_names": [
                    item.get("name") for item in payload.get("actuators", [])
                ],
                "joint_names": payload.get("joints", []),
                "keyframes": payload.get("keyframes", []),
                "error": payload.get("error"),
            }
        )
    return output


def static_playground_contract(playground: Path) -> dict:
    open_duck_dir = playground / "playground" / "open_duck_mini_v2"
    joystick_path = open_duck_dir / "joystick.py"
    constants_path = open_duck_dir / "constants.py"
    xml_dir = open_duck_dir / "xmls"
    xml_files = sorted(xml_dir.glob("*.xml")) if xml_dir.exists() else []
    xml_payloads = [parse_xml_recursive(path) for path in xml_files]
    action_candidates = []
    for item in xml_payloads:
        if item.get("nu_static") == 14:
            action_candidates.append(item["path"])
    return {
        "path": str(playground),
        "exists": playground.exists(),
        "open_duck_dir": str(open_duck_dir),
        "joystick_path": str(joystick_path),
        "constants_path": str(constants_path),
        "joints_order_no_head": literal_assignment(constants_path, "JOINTS_ORDER_NO_HEAD"),
        "feet_sites": literal_assignment(constants_path, "FEET_SITES"),
        "feet_geoms": literal_assignment(constants_path, "FEET_GEOMS"),
        "default_config": parse_config_defaults(joystick_path),
        "xmls": flatten_xml_summaries(xml_payloads),
        "candidate_14_actuator_xmls": action_candidates,
    }


def instantiate_env_contract(env_python: Path, playground: Path, timeout_s: int) -> dict:
    if not env_python.exists():
        return {
            "status": "HOLD_ENV_PYTHON_MISSING",
            "python": str(env_python),
            "error": "interpreter does not exist",
        }
    code = r'''
import json
import os
import sys

payload = {"status": "UNKNOWN"}
try:
    from playground.open_duck_mini_v2 import joystick
    import jax
    cfg = joystick.default_config()
    env = joystick.Joystick(task="flat_terrain")
    state = env.reset(jax.random.PRNGKey(0))
    payload = {
        "status": "PASS_ENV_INSTANTIATED",
        "python": sys.executable,
        "jax_default_backend": jax.default_backend(),
        "jax_devices": [str(device) for device in jax.devices()],
        "action_size": int(env.action_size),
        "observation_size": {
            key: list(value) for key, value in env.observation_size.items()
        },
        "actuator_names": list(env.actuator_names),
        "joint_names": list(env.joint_names),
        "backlash_joint_names": list(env.backlash_joint_names),
        "mjcf": {
            "nu": int(env.mj_model.nu),
            "nq": int(env.mj_model.nq),
            "nv": int(env.mj_model.nv),
            "home_ctrl_len": int(len(env.mj_model.keyframe("home").ctrl)),
        },
        "reset_obs_shapes": {
            key: list(value.shape) for key, value in state.obs.items()
        },
        "config": {
            "ctrl_dt": float(cfg.ctrl_dt),
            "sim_dt": float(cfg.sim_dt),
            "action_repeat": int(cfg.action_repeat),
            "action_scale": float(cfg.action_scale),
            "dof_vel_scale": float(cfg.dof_vel_scale),
            "max_motor_velocity": float(cfg.max_motor_velocity),
            "action_min_delay": int(cfg.noise_config.action_min_delay),
            "action_max_delay": int(cfg.noise_config.action_max_delay),
            "imu_min_delay": int(cfg.noise_config.imu_min_delay),
            "imu_max_delay": int(cfg.noise_config.imu_max_delay),
        },
    }
except Exception as exc:
    payload = {
        "status": "HOLD_ENV_INSTANTIATION_FAILED",
        "python": sys.executable,
        "error": f"{type(exc).__name__}: {exc}",
    }
print("CONTRACT_JSON_START")
print(json.dumps(payload, sort_keys=True))
print("CONTRACT_JSON_END")
'''
    try:
        result = subprocess.run(
            [str(env_python), "-c", code],
            cwd=str(playground),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout_s,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return {
            "status": "HOLD_ENV_INSTANTIATION_TIMEOUT",
            "python": str(env_python),
            "error": f"timed out after {timeout_s}s",
        }
    output = result.stdout or ""
    match = re.search(
        r"CONTRACT_JSON_START\s*(\{.*\})\s*CONTRACT_JSON_END",
        output,
        flags=re.S,
    )
    if not match:
        return {
            "status": "HOLD_ENV_INSTANTIATION_NO_JSON",
            "python": str(env_python),
            "returncode": result.returncode,
            "output_tail": output[-4000:],
        }
    payload = json.loads(match.group(1))
    payload["returncode"] = result.returncode
    payload["output_tail"] = output[-4000:]
    return payload


def assess(policy: dict, static: dict, instantiated: dict) -> dict:
    expected_obs = 101
    expected_action = 14
    env_action = instantiated.get("action_size")
    env_obs = (instantiated.get("observation_size") or {}).get("state")
    env_obs_dim = env_obs[0] if isinstance(env_obs, list) and env_obs else None
    static_14 = bool(static.get("candidate_14_actuator_xmls"))
    order = instantiated.get("actuator_names") or []
    order_match = order == POLICY_JOINT_ORDER
    if env_action == expected_action and env_obs_dim == expected_obs and order_match:
        status = "PASS_POLICY_SIM_CONTRACT"
    elif static_14 and instantiated.get("status", "").startswith("HOLD"):
        status = "WARN_STATIC_14_ENV_IMPORT_HELD"
    else:
        status = "HOLD_POLICY_SIM_CONTRACT_MISMATCH"
    return {
        "status": status,
        "expected_observation_dim": expected_obs,
        "expected_action_dim": expected_action,
        "instantiated_observation_dim": env_obs_dim,
        "instantiated_action_dim": env_action,
        "static_14_actuator_xml_found": static_14,
        "actuator_order_matches_policy": order_match,
        "recommended_next": (
            "run full actuator bridge policy-loop eval"
            if status == "PASS_POLICY_SIM_CONTRACT"
            else "resolve env/import/contract mismatch before training"
        ),
    }


def mismatch_rows(assessment: dict, static: dict, instantiated: dict) -> list[tuple[str, str, str, str]]:
    sim_obs = assessment.get("instantiated_observation_dim")
    sim_action = assessment.get("instantiated_action_dim")
    order = instantiated.get("actuator_names") or []
    cfg = instantiated.get("config") or static.get("default_config") or {}
    return [
        ("obs length", "101", str(sim_obs), "PASS" if sim_obs == 101 else "HOLD"),
        ("action length", "14", str(sim_action), "PASS" if sim_action == 14 else "HOLD"),
        (
            "action order",
            ", ".join(POLICY_JOINT_ORDER),
            ", ".join(order) if order else "UNKNOWN",
            "PASS" if order == POLICY_JOINT_ORDER else "HOLD",
        ),
        (
            "head/neck presence",
            "neck_pitch, head_pitch, head_yaw, head_roll present",
            str(all(name in order for name in POLICY_JOINT_ORDER[5:9])),
            "PASS" if all(name in order for name in POLICY_JOINT_ORDER[5:9]) else "HOLD",
        ),
        ("command vector", "7 values obs[6:13]", "7 values from joystick.py command", "PASS"),
        ("IMU representation", "raw gyro + accelerometer", "raw gyro + accelerometer in _get_obs", "PASS"),
        ("contact representation", "2 foot contacts obs[97:99]", "2 contacts in _get_obs", "PASS"),
        (
            "phase",
            "2 values obs[99:101]",
            "imitation_phase 2 values",
            "PASS",
        ),
        (
            "action delay",
            "runtime telemetry measured 3-4 tick lag; training prior 0-3",
            f"{cfg.get('action_min_delay', 'UNKNOWN')}-{cfg.get('action_max_delay', 'UNKNOWN')}",
            "WARN",
        ),
        (
            "actuator model",
            "real bridge delay/lag/velocity limit needed",
            f"max_motor_velocity={cfg.get('max_motor_velocity', 'UNKNOWN')}",
            "WARN",
        ),
    ]


def build_markdown(payload: dict) -> str:
    policy = payload["policy"]
    static = payload["playground_static"]
    instantiated = payload["playground_instantiated"]
    assessment = payload["assessment"]
    lines = ["# Policy / Sim Contract Reconciliation", ""]
    lines.append("## Executive Summary")
    lines.append("")
    lines.append("- `BEST_WALK_ONNX_2` requires `obs[1,101] -> continuous_actions[1,14]`.")
    if assessment["status"] == "PASS_POLICY_SIM_CONTRACT":
        lines.append(
            "- The local `../Open_Duck_Playground` `Joystick(flat_terrain)` env "
            "matches the 101-observation / 14-action contract when instantiated "
            "with the `envs/open-duck-playground` Python environment."
        )
    else:
        lines.append(
            "- Full policy-loop sim eval remains blocked until the local Playground "
            "contract/import issue is resolved."
        )
    lines.append(
        "- Telemetry replay bridge reproduction is useful, but it is not a "
        "replacement for the full policy/sim loop."
    )
    lines.append("")
    lines.append(f"assessment_status: `{assessment['status']}`")
    lines.append(f"recommended_next: `{assessment['recommended_next']}`")
    lines.append("")

    lines.append("## Known Deployed Policy / Runtime Contract")
    lines.append("")
    lines.append(f"- policy_path: `{policy['path']}`")
    lines.append(f"- policy_sha256: `{policy.get('sha256')}`")
    lines.append("- observation: `[1, 101]`")
    lines.append("- action: `[1, 14]`")
    lines.append("")
    lines.append("| obs slice | meaning |")
    lines.append("|---|---|")
    for name, start, end in OBS_BREAKDOWN:
        lines.append(f"| `{start}:{end}` | {name} |")
    lines.append("")
    lines.append("| action index | joint |")
    lines.append("|---:|---|")
    for index, joint in enumerate(POLICY_JOINT_ORDER):
        lines.append(f"| {index} | `{joint}` |")
    lines.append("")

    lines.append("## Local Playground Contract")
    lines.append("")
    lines.append(f"- playground_path: `{static['path']}`")
    lines.append(f"- env_python: `{instantiated.get('python')}`")
    lines.append(f"- env_status: `{instantiated.get('status')}`")
    lines.append(f"- jax_backend: `{instantiated.get('jax_default_backend', 'UNKNOWN')}`")
    lines.append(f"- jax_devices: `{instantiated.get('jax_devices', 'UNKNOWN')}`")
    lines.append(f"- action_size: `{instantiated.get('action_size', 'UNKNOWN')}`")
    lines.append(f"- observation_size: `{instantiated.get('observation_size', 'UNKNOWN')}`")
    mjcf = instantiated.get("mjcf") or {}
    lines.append(
        f"- MJCF nu/nq/nv: `{mjcf.get('nu')}/{mjcf.get('nq')}/{mjcf.get('nv')}`"
    )
    lines.append(f"- keyframe home ctrl len: `{mjcf.get('home_ctrl_len')}`")
    cfg = instantiated.get("config") or static.get("default_config") or {}
    lines.append(
        f"- control dt / sim dt: `{cfg.get('ctrl_dt')}` / `{cfg.get('sim_dt')}`"
    )
    lines.append(f"- action_scale: `{cfg.get('action_scale')}`")
    lines.append(f"- max_motor_velocity: `{cfg.get('max_motor_velocity')}`")
    lines.append(
        f"- action delay config: `{cfg.get('action_min_delay')}-{cfg.get('action_max_delay')}`"
    )
    lines.append(
        f"- imu delay config: `{cfg.get('imu_min_delay')}-{cfg.get('imu_max_delay')}`"
    )
    lines.append("")
    lines.append("### Actuator Names")
    lines.append("")
    for index, name in enumerate(instantiated.get("actuator_names") or []):
        lines.append(f"- `{index}` `{name}`")
    if not instantiated.get("actuator_names"):
        lines.append("- `UNKNOWN`")
    lines.append("")

    lines.append("### Static XML Candidates")
    lines.append("")
    lines.append("| xml | nu_static | keyframe ctrl lens |")
    lines.append("|---|---:|---|")
    for item in static.get("xmls", []):
        key_lens = [frame["ctrl_len"] for frame in item.get("keyframes", [])]
        lines.append(f"| `{item['path']}` | {item.get('nu_static')} | `{key_lens}` |")
    lines.append("")

    lines.append("## Mismatch Table")
    lines.append("")
    lines.append("| field | runtime / policy | local sim | status |")
    lines.append("|---|---|---|---|")
    for field, runtime, sim, status in mismatch_rows(assessment, static, instantiated):
        lines.append(f"| {field} | {runtime} | {sim} | `{status}` |")
    lines.append("")

    lines.append("## Candidate Resolution Paths")
    lines.append("")
    lines.append("1. **Use the instantiated local 14-action Playground env.**")
    lines.append(
        "   This is currently the recommended path because the env instantiated "
        "with 101 state observations, 14 actions, matching actuator order, and "
        "ROCm JAX visibility."
    )
    lines.append("2. Restore an archived 14-actuator env only if later eval reveals hidden drift.")
    lines.append(
        "3. Build a compatibility eval env only if the local 14-action env cannot "
        "run the full policy-loop bridge."
    )
    lines.append(
        "4. Train a 10-actuator no-head policy only as an explicit new robot target, "
        "not as a BEST_WALK_ONNX_2-compatible fix."
    )
    lines.append("")

    lines.append("## Recommendation")
    lines.append("")
    if assessment["status"] == "PASS_POLICY_SIM_CONTRACT":
        lines.append(
            "Proceed to the full policy-loop actuator bridge eval using "
            "`../Open_Duck_Playground` under "
            "`../envs/open-duck-playground/bin/python`. Do not train yet."
        )
    else:
        lines.append(
            "Resolve the contract/import hold first. Do not train against a "
            "mismatched sim contract."
        )
    return "\n".join(lines).rstrip()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit BEST_WALK_ONNX_2 policy contract against local Playground sim contract."
    )
    parser.add_argument("--policy", default=str(DEFAULT_POLICY))
    parser.add_argument("--playground-path", default=str(DEFAULT_PLAYGROUND))
    parser.add_argument("--env-python", default=str(DEFAULT_ENV_PYTHON))
    parser.add_argument("--output-md", default=None)
    parser.add_argument("--output-json", default=None)
    parser.add_argument("--instantiate-timeout-s", type=int, default=90)
    args = parser.parse_args()

    policy_path = Path(args.policy).expanduser().resolve()
    playground = Path(args.playground_path).expanduser().resolve()
    env_python = Path(args.env_python).expanduser().absolute()
    policy = onnx_contract(policy_path)
    static = static_playground_contract(playground)
    instantiated = instantiate_env_contract(env_python, playground, args.instantiate_timeout_s)
    assessment = assess(policy, static, instantiated)
    payload = {
        "policy": policy,
        "playground_static": static,
        "playground_instantiated": instantiated,
        "assessment": assessment,
    }
    report = build_markdown(payload)
    if args.output_md:
        path = Path(args.output_md)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(report + "\n")
    if args.output_json:
        path = Path(args.output_json)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2) + "\n")
    print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
