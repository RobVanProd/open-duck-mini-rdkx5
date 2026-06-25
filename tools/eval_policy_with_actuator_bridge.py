#!/usr/bin/env python3
"""Offline actuator bridge evaluation harness.

The full target is current-policy MuJoCo evaluation with and without the fitted
actuator bridge. This tool also supports a no-robot telemetry replay mode that
uses existing suspended replay logs to validate the bridge metrics while the
MuJoCo policy-loop integration is being wired.
"""

from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
import statistics
import subprocess
import sys
import tempfile
from typing import Sequence

import numpy as np

from actuator_bridge_model import (
    JOINT_NAMES,
    PITCH_CHAIN_JOINTS,
    JointActuatorParams,
    bridge_targets,
    load_fit_json,
    params_from_fit,
    stress_params,
)
from audit_policy_sim_contract import (
    DEFAULT_ENV_PYTHON,
    instantiate_env_contract,
    static_playground_contract,
)
from closed_loop_sim_eval import ClosedLoopConfig, run_closed_loop_sim


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_POLICY = ROOT / "policy" / "BEST_WALK_ONNX_2.onnx"
DEFAULT_FIT_JSON = ROOT / "outputs" / "analysis" / "actuator_response_fit.json"
DEFAULT_OUTPUT_DIR = ROOT / "outputs" / "analysis"
DEFAULT_PLAYGROUND_ROOT = ROOT.parent / "Open_Duck_Playground"


def finite(value) -> bool:
    return value is not None and not (
        isinstance(value, float) and (math.isnan(value) or math.isinf(value))
    )


def percentile(values: Sequence[float], pct: float):
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


def stats(values: Sequence[float]):
    values = [float(value) for value in values if finite(value)]
    if not values:
        return None
    return {
        "p50": percentile(values, 50),
        "p95": percentile(values, 95),
        "p99": percentile(values, 99),
        "max": max(values),
    }


def fmt(value, digits: int = 4) -> str:
    if value is None:
        return "NA"
    return f"{float(value):.{digits}f}"


def load_reward_overrides(path: Path | None, phase_name: str | None) -> dict:
    if path is None:
        return {}
    path = path.expanduser().resolve()
    payload = json.loads(path.read_text())
    selected = payload
    if isinstance(payload, dict) and isinstance(payload.get("phases"), list):
        phases = payload["phases"]
        if phase_name:
            matches = [phase for phase in phases if phase.get("name") == phase_name]
            if not matches:
                raise SystemExit(
                    f"--reward-overrides-phase {phase_name!r} not found in {path}"
                )
            selected = matches[0]
        elif phases:
            selected = phases[0]
    if isinstance(selected, dict) and isinstance(
        selected.get("training_recipe_overrides"), dict
    ):
        selected = selected["training_recipe_overrides"]
    if not isinstance(selected, dict):
        raise SystemExit(f"reward override JSON did not contain an object: {path}")
    return {
        key: value
        for key, value in selected.items()
        if value is not None
        and (
            key.endswith("_scale")
            or key.endswith("_huber_delta")
            or key.startswith("command_progress_")
            or key.startswith("forward_")
            or key.startswith("reward_clip_")
            or key
            in {
                "tracking_sigma",
                "action_rate_huber_delta",
                "action_magnitude_huber_delta",
                "target_rate_huber_delta",
                "actuator_tracking_huber_delta",
            }
        )
    }


def load_records(path: Path, startup_ticks: int) -> list[dict]:
    records = []
    with open(path) as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                print(f"Skipping invalid JSON line {line_no}: {exc}", file=sys.stderr)
                continue
            tick = record.get("tick")
            if tick is not None and int(tick) <= startup_ticks:
                continue
            records.append(record)
    return records


def record_dt(prev: dict | None, cur: dict) -> float:
    dt_s = cur.get("dt_s")
    if finite(dt_s) and float(dt_s) > 0:
        return float(dt_s)
    if prev is not None:
        prev_t = prev.get("timestamp_monotonic_s")
        cur_t = cur.get("timestamp_monotonic_s")
        if finite(prev_t) and finite(cur_t) and float(cur_t) > float(prev_t):
            return float(cur_t) - float(prev_t)
    return 0.02


def nested_vector(record: dict, group: str, field: str):
    values = record.get(group, {}).get(field)
    if values is None:
        return None
    return np.asarray(values, dtype=float)


def telemetry_arrays(records: list[dict]) -> dict:
    sent = []
    actual = []
    actions = []
    dts = []
    ticks = []
    previous = None
    for record in records:
        sent_target = nested_vector(record, "action", "motor_targets_sent_rad")
        if sent_target is None:
            sent_target = nested_vector(record, "joints", "commanded_position_rad")
        actual_position = nested_vector(record, "joints", "actual_position_rad")
        action = nested_vector(record, "action", "onnx_action")
        if sent_target is None or actual_position is None:
            previous = record
            continue
        if sent_target.shape[0] != len(JOINT_NAMES) or actual_position.shape[0] != len(JOINT_NAMES):
            previous = record
            continue
        sent.append(sent_target)
        actual.append(actual_position)
        actions.append(action if action is not None and action.shape[0] == len(JOINT_NAMES) else np.full(len(JOINT_NAMES), np.nan))
        dts.append(record_dt(previous, record))
        ticks.append(record.get("tick"))
        previous = record
    if not sent:
        raise ValueError("telemetry did not contain usable sent target / actual joint vectors")
    return {
        "sent_target": np.vstack(sent),
        "actual_position": np.vstack(actual),
        "onnx_action": np.vstack(actions),
        "dt_s": np.asarray(dts, dtype=float),
        "ticks": ticks,
    }


def abs_velocity(values: np.ndarray, dt_s: np.ndarray) -> np.ndarray:
    if values.shape[0] < 2:
        return np.zeros_like(values)
    dt = np.maximum(dt_s[1:], 1e-6)
    vel = np.abs(np.diff(values, axis=0) / dt[:, None])
    first = np.zeros((1, values.shape[1]))
    return np.vstack([first, vel])


def best_lag(target: np.ndarray, actual: np.ndarray, dt_s: np.ndarray, max_lag_ticks: int) -> dict:
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
            best = {"ticks": lag, "rmse": rmse, "samples": len(pairs)}
    if best is None:
        return {"ticks": None, "ms": None, "rmse": None, "samples": 0}
    median_dt = statistics.median(float(value) for value in dt_s if value > 0)
    best["ms"] = best["ticks"] * median_dt * 1000.0
    return best


def action_saturation(actions: np.ndarray, joint_index: int, threshold: float = 0.98):
    values = actions[:, joint_index]
    values = values[np.isfinite(values)]
    if values.size == 0:
        return None
    return float(np.mean(np.abs(values) >= threshold) * 100.0)


def summarize_mode(
    name: str,
    sent_target: np.ndarray,
    modeled_position: np.ndarray,
    actual_position: np.ndarray | None,
    onnx_action: np.ndarray | None,
    dt_s: np.ndarray,
    max_lag_ticks: int,
) -> dict:
    target_velocity = abs_velocity(sent_target, dt_s)
    applied_velocity = abs_velocity(modeled_position, dt_s)
    tracking = np.abs(sent_target - modeled_position)
    model_error = None if actual_position is None else np.abs(actual_position - modeled_position)
    raw_tracking = None if actual_position is None else np.abs(sent_target - actual_position)
    joints = {}
    for index, joint in enumerate(JOINT_NAMES):
        joints[joint] = {
            "target_velocity_rad_s": stats(target_velocity[:, index]),
            "applied_target_velocity_rad_s": stats(applied_velocity[:, index]),
            "simulated_tracking_error_rad": stats(tracking[:, index]),
            "model_error_vs_real_actual_rad": (
                None if model_error is None else stats(model_error[:, index])
            ),
            "real_raw_tracking_error_rad": (
                None if raw_tracking is None else stats(raw_tracking[:, index])
            ),
            "estimated_lag": best_lag(
                sent_target[:, index], modeled_position[:, index], dt_s, max_lag_ticks
            ),
            "action_saturation_pct": (
                None if onnx_action is None else action_saturation(onnx_action, index)
            ),
        }
    return {"mode": name, "joints": joints}


def pitch_chain_gate(fitted_summary: dict) -> dict:
    ratios = []
    p95_model_errors = []
    for joint in PITCH_CHAIN_JOINTS:
        item = fitted_summary["joints"].get(joint, {})
        sim_tracking = item.get("simulated_tracking_error_rad") or {}
        real_tracking = item.get("real_raw_tracking_error_rad") or {}
        sim_p95 = sim_tracking.get("p95")
        real_p95 = real_tracking.get("p95")
        model_error = item.get("model_error_vs_real_actual_rad") or {}
        if finite(sim_p95) and finite(real_p95) and real_p95 > 1e-9:
            ratios.append(sim_p95 / real_p95)
        if finite(model_error.get("p95")):
            p95_model_errors.append(model_error["p95"])
    if not ratios:
        return {
            "status": "HOLD_NO_REAL_COMPARISON",
            "median_sim_to_real_p95_tracking_ratio": None,
            "max_p95_model_error": None,
        }
    median_ratio = statistics.median(ratios)
    max_model_error = max(p95_model_errors) if p95_model_errors else None
    if 0.65 <= median_ratio <= 1.35 and (max_model_error is None or max_model_error < 0.05):
        status = "PASS_TELEMETRY_REPLAY_REPRODUCTION"
    else:
        status = "HOLD_MODEL_INCOMPLETE"
    return {
        "status": status,
        "median_sim_to_real_p95_tracking_ratio": median_ratio,
        "max_p95_model_error": max_model_error,
    }


def inspect_policy(
    policy_path: Path,
    expected_observation_dim: int,
    expected_action_dim: int,
    inspect_policy_io: bool,
) -> dict:
    payload = {"path": str(policy_path), "exists": policy_path.exists()}
    if not policy_path.exists():
        payload["status"] = "HOLD_POLICY_MISSING"
        return payload
    if not inspect_policy_io:
        payload.update(
            {
                "status": "PASS_POLICY_CONTRACT_ASSUMED",
                "input_shape": [1, expected_observation_dim],
                "output_shape": [1, expected_action_dim],
                "note": (
                    "Policy IO inspection skipped; using audited BEST_WALK_ONNX_2 "
                    "contract. Pass --inspect-policy-io to query ONNX Runtime."
                ),
            }
        )
        return payload
    try:
        import onnxruntime as ort

        session = ort.InferenceSession(str(policy_path), providers=["CPUExecutionProvider"])
        inputs = session.get_inputs()
        outputs = session.get_outputs()
        payload.update(
            {
                "status": "PASS_POLICY_IO",
                "input_name": inputs[0].name if inputs else None,
                "input_shape": inputs[0].shape if inputs else None,
                "input_type": inputs[0].type if inputs else None,
                "output_name": outputs[0].name if outputs else None,
                "output_shape": outputs[0].shape if outputs else None,
                "output_type": outputs[0].type if outputs else None,
            }
        )
    except Exception as exc:  # pragma: no cover - environment-dependent
        payload.update({"status": "WARN_POLICY_IO_UNAVAILABLE", "error": f"{type(exc).__name__}: {exc}"})
    return payload


def run_sim_preflight(policy: dict, playground: dict) -> dict:
    policy_action_dim = None
    output_shape = policy.get("output_shape") or []
    if output_shape and isinstance(output_shape[-1], int):
        policy_action_dim = output_shape[-1]
    policy_obs_dim = None
    input_shape = policy.get("input_shape") or []
    if input_shape and isinstance(input_shape[-1], int):
        policy_obs_dim = input_shape[-1]

    instantiated = playground.get("instantiated", {})
    static = playground.get("static", {})
    sim_action_dim = instantiated.get("action_size")
    sim_obs_shape = (instantiated.get("observation_size") or {}).get("state")
    sim_obs_dim = sim_obs_shape[0] if isinstance(sim_obs_shape, list) and sim_obs_shape else None
    actuator_names = instantiated.get("actuator_names") or []
    if policy_action_dim and sim_action_dim and policy_action_dim != sim_action_dim:
        return {
            "status": "HOLD_POLICY_SIM_CONTRACT_MISMATCH",
            "reason": (
                f"policy action dim is {policy_action_dim}, but instantiated playground "
                f"action_size is {sim_action_dim}"
            ),
            "policy_action_dim": policy_action_dim,
            "sim_action_dim": sim_action_dim,
            "sim_env_path": static.get("open_duck_dir"),
            "sim_actuator_names": actuator_names,
            "recommended_next_command": "python3 tools/audit_policy_sim_contract.py --policy policy/BEST_WALK_ONNX_2.onnx --playground-path ../Open_Duck_Playground",
        }
    if policy_obs_dim and sim_obs_dim and policy_obs_dim != sim_obs_dim:
        return {
            "status": "HOLD_POLICY_SIM_CONTRACT_MISMATCH",
            "reason": (
                f"policy observation dim is {policy_obs_dim}, but instantiated playground "
                f"state observation dim is {sim_obs_dim}"
            ),
            "policy_obs_dim": policy_obs_dim,
            "sim_obs_dim": sim_obs_dim,
            "sim_env_path": static.get("open_duck_dir"),
            "sim_actuator_names": actuator_names,
            "recommended_next_command": "python3 tools/audit_policy_sim_contract.py --policy policy/BEST_WALK_ONNX_2.onnx --playground-path ../Open_Duck_Playground",
        }
    if instantiated.get("status", "").startswith("HOLD"):
        return {
            "status": instantiated["status"],
            "reason": instantiated.get("error", "playground env could not be instantiated"),
            "sim_env_path": static.get("open_duck_dir"),
            "recommended_next_command": "python3 tools/audit_policy_sim_contract.py --policy policy/BEST_WALK_ONNX_2.onnx --playground-path ../Open_Duck_Playground",
        }
    static_14 = bool(static.get("candidate_14_actuator_xmls"))
    return {
        "status": "HOLD_SIM_INTEGRATION_PENDING",
        "reason": (
            "Policy and local Playground dimensions appear compatible, but the "
            "closed-loop JAX/MJX policy eval path with actuator bridge is not wired yet."
        ),
        "policy_obs_dim": policy_obs_dim,
        "policy_action_dim": policy_action_dim,
        "sim_obs_dim": sim_obs_dim,
        "sim_action_dim": sim_action_dim,
        "sim_env_path": static.get("open_duck_dir"),
        "sim_actuator_names": actuator_names,
        "static_14_actuator_xml_found": static_14,
        "recommended_next_command": "python3 tools/audit_policy_sim_contract.py --policy policy/BEST_WALK_ONNX_2.onnx --playground-path ../Open_Duck_Playground",
    }


def run_telemetry_replay(args, fit: dict) -> dict:
    records = load_records(Path(args.telemetry_jsonl), args.startup_ticks)
    arrays = telemetry_arrays(records)
    sent = arrays["sent_target"]
    actual = arrays["actual_position"]
    dts = arrays["dt_s"]
    actions = arrays["onnx_action"]

    vanilla = sent.copy()
    fitted = bridge_targets(sent, dts, params_from_fit(fit, JOINT_NAMES))
    stress = bridge_targets(
        sent,
        dts,
        stress_params(
            JOINT_NAMES,
            delay_ticks=args.stress_delay_ticks,
            tau_s=args.stress_tau_s,
            default_velocity_limit_rad_s=args.stress_velocity_limit_rad_s,
        ),
    )
    summaries = {
        "vanilla_no_bridge": summarize_mode(
            "vanilla_no_bridge", sent, vanilla, actual, actions, dts, args.max_lag_ticks
        ),
        "fitted_bridge": summarize_mode(
            "fitted_bridge", sent, fitted, actual, actions, dts, args.max_lag_ticks
        ),
        "stress_bridge": summarize_mode(
            "stress_bridge", sent, stress, actual, actions, dts, args.max_lag_ticks
        ),
    }
    gate = pitch_chain_gate(summaries["fitted_bridge"])
    return {
        "status": gate["status"],
        "telemetry_jsonl": str(args.telemetry_jsonl),
        "samples_after_startup_filter": len(records),
        "startup_ticks": args.startup_ticks,
        "command_x": args.command_x,
        "duration_s": args.duration,
        "gate": gate,
        "modes": summaries,
    }


def resolve_jax_platforms(jax_platform: str | None, jax_platforms: str | None) -> str | None:
    if jax_platforms:
        return str(jax_platforms)
    if jax_platform == "cpu":
        return "cpu"
    return None


def build_jax_env(jax_platform: str | None, jax_platforms: str | None) -> dict[str, str] | None:
    resolved_platforms = resolve_jax_platforms(jax_platform, jax_platforms)
    if not jax_platform and not resolved_platforms:
        return None
    env = os.environ.copy()
    if jax_platform:
        env["JAX_PLATFORM_NAME"] = str(jax_platform)
    if resolved_platforms:
        env["JAX_PLATFORMS"] = resolved_platforms
    return env


def apply_jax_platform_env(jax_platform: str | None, jax_platforms: str | None) -> None:
    resolved_platforms = resolve_jax_platforms(jax_platform, jax_platforms)
    if jax_platform:
        os.environ["JAX_PLATFORM_NAME"] = str(jax_platform)
    if resolved_platforms:
        os.environ["JAX_PLATFORMS"] = resolved_platforms


def run_closed_loop_worker(args) -> dict:
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w",
        prefix="closed_loop_worker_",
        suffix=".json",
        dir=output_dir,
        delete=False,
    ) as tmp:
        worker_json = Path(tmp.name)
    # Preserve virtualenv launcher/symlink semantics. Resolving this path can
    # bypass the environment's site-packages and launch the bare base Python.
    worker_python = Path(args.env_python).expanduser().absolute()
    cmd = [
        str(worker_python),
        str(Path(__file__).resolve()),
        "--mode",
        "closed-loop-sim",
        "--policy",
        str(args.policy),
        "--fit-json",
        str(args.fit_json),
        "--playground-root",
        str(args.playground_root),
        "--env-python",
        str(args.env_python),
        "--command-x",
        str(args.command_x),
        "--command-y",
        str(args.command_y),
        "--command-yaw",
        str(args.command_yaw),
        "--duration",
        str(args.duration),
        "--task",
        str(args.task),
        "--seed",
        str(args.seed),
        "--bridge-mode",
        str(args.bridge_mode),
        "--output-dir",
        str(args.output_dir),
        "--startup-ticks",
        str(args.startup_ticks),
        "--max-lag-ticks",
        str(args.max_lag_ticks),
        "--stress-delay-ticks",
        str(args.stress_delay_ticks),
        "--stress-tau-s",
        str(args.stress_tau_s),
        "--stress-velocity-limit-rad-s",
        str(args.stress_velocity_limit_rad_s),
        "--expected-observation-dim",
        str(args.expected_observation_dim),
        "--expected-action-dim",
        str(args.expected_action_dim),
        "--eval-role",
        str(args.eval_role),
        "--mjx-step-loop-mode",
        str(args.mjx_step_loop_mode),
        "--policy-action-gain",
        str(args.policy_action_gain),
        "--forward-diagnostic-required-ratio",
        str(args.forward_diagnostic_required_ratio),
        "--forward-diagnostic-deadband",
        str(args.forward_diagnostic_deadband),
        "--sim-preflight-timeout-s",
        str(args.sim_preflight_timeout_s),
        "--_closed-loop-worker",
        "--_closed-loop-worker-json",
        str(worker_json),
    ]
    if args.reward_overrides_json:
        cmd.extend(["--reward-overrides-json", str(args.reward_overrides_json)])
    if args.reward_overrides_phase:
        cmd.extend(["--reward-overrides-phase", str(args.reward_overrides_phase)])
    if args.trace_jsonl:
        cmd.extend(["--trace-jsonl", str(args.trace_jsonl)])
    if args.jax_platform:
        cmd.extend(["--jax-platform", str(args.jax_platform)])
    if args.jax_platforms:
        cmd.extend(["--jax-platforms", str(args.jax_platforms)])
    if args.max_motor_velocity_override_rad_s is not None:
        cmd.extend(
            [
                "--max-motor-velocity-override-rad-s",
                str(args.max_motor_velocity_override_rad_s),
            ]
        )
    if args.inspect_policy_io:
        cmd.append("--inspect-policy-io")
    env = build_jax_env(args.jax_platform, args.jax_platforms)
    try:
        result = subprocess.run(
            cmd,
            cwd=str(Path.cwd()),
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=args.closed_loop_timeout_s,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        return {
            "status": "HOLD_SIM_RUNTIME_ERROR",
            "error": f"closed-loop worker timed out after {args.closed_loop_timeout_s}s",
            "worker_command": cmd,
            "worker_output_tail": (exc.stdout or "")[-12000:]
            if isinstance(exc.stdout, str)
            else None,
        }
    if worker_json.exists() and worker_json.stat().st_size > 0:
        try:
            payload = json.loads(worker_json.read_text())
            payload["worker_returncode"] = result.returncode
            payload["worker_output_tail"] = (result.stdout or "")[-12000:]
            payload["worker_command"] = cmd
            return payload
        except json.JSONDecodeError:
            pass
    return {
        "status": "HOLD_SIM_RUNTIME_ERROR",
        "error": f"closed-loop worker exited {result.returncode} before writing JSON",
        "worker_returncode": result.returncode,
        "worker_command": cmd,
        "worker_output_tail": (result.stdout or "")[-12000:],
    }


def fmt_status(value) -> str:
    return "NA" if value is None else str(value)


def closed_loop_pitch_rows(closed_loop: dict) -> list[str]:
    rows = []
    modes = closed_loop.get("modes", {})
    for mode_name in ["vanilla", "fitted", "stress"]:
        mode = modes.get(mode_name)
        if not mode:
            continue
        for joint in PITCH_CHAIN_JOINTS:
            item = (mode.get("joints") or {}).get(joint, {})
            sent_vel = item.get("sent_target_velocity_rad_s") or {}
            applied_vel = item.get("applied_target_velocity_rad_s") or {}
            bridge = item.get("bridge_tracking_error_rad") or {}
            joint_tracking = item.get("joint_target_tracking_error_rad") or {}
            lag_applied = item.get("estimated_lag_sent_to_applied") or {}
            rows.append(
                f"| {mode_name} | {joint} | {fmt(sent_vel.get('p95'))} | "
                f"{fmt(applied_vel.get('p95'))} | {fmt(bridge.get('p95'))} | "
                f"{fmt(joint_tracking.get('p95'))} | {fmt(lag_applied.get('ticks'), 0)} | "
                f"{fmt(item.get('action_saturation_pct'), 2)} |"
            )
    return rows


def build_markdown(payload: dict) -> str:
    lines = ["# Sim Actuator Bridge Eval", ""]
    lines.append(f"overall_status: `{payload['overall_status']}`")
    lines.append(f"policy: `{payload['policy'].get('path')}`")
    lines.append(f"fit_json: `{payload['fit_json']}`")
    if payload.get("task") is not None:
        lines.append(f"task: `{payload.get('task')}`")
    lines.append(f"command_x: `{payload['command_x']}`")
    if payload.get("command_y") is not None:
        lines.append(f"command_y: `{payload.get('command_y')}`")
    if payload.get("command_yaw") is not None:
        lines.append(f"command_yaw: `{payload.get('command_yaw')}`")
    lines.append(f"duration_s: `{payload['duration_s']}`")
    lines.append(f"seed: `{payload.get('seed')}`")
    lines.append(f"eval_role: `{payload.get('eval_role')}`")
    lines.append(f"jax_platform_requested: `{payload.get('jax_platform')}`")
    lines.append("")
    lines.append("## Contract Preflight")
    lines.append("")
    lines.append(f"- policy_status: `{payload['policy'].get('status')}`")
    lines.append(f"- policy_input_shape: `{payload['policy'].get('input_shape')}`")
    lines.append(f"- policy_output_shape: `{payload['policy'].get('output_shape')}`")
    playground_static = payload["playground"].get("static", {})
    playground_instantiated = payload["playground"].get("instantiated", {})
    lines.append(f"- playground_static_path: `{playground_static.get('open_duck_dir')}`")
    lines.append(f"- playground_env_python: `{payload['playground'].get('env_python')}`")
    lines.append(f"- playground_instantiated_status: `{playground_instantiated.get('status')}`")
    lines.append(f"- playground_action_size: `{playground_instantiated.get('action_size')}`")
    lines.append(f"- playground_observation_size: `{playground_instantiated.get('observation_size')}`")
    lines.append(f"- playground_actuator_names: `{playground_instantiated.get('actuator_names')}`")
    lines.append(f"- sim_preflight_status: `{payload['sim_preflight'].get('status')}`")
    lines.append(f"- sim_preflight_reason: {payload['sim_preflight'].get('reason', 'NA')}")
    if payload["sim_preflight"].get("recommended_next_command"):
        lines.append(
            "- recommended_next_command: "
            f"`{payload['sim_preflight']['recommended_next_command']}`"
        )
    lines.append("")
    if payload.get("telemetry_replay"):
        replay = payload["telemetry_replay"]
        lines.append("## Telemetry Replay Bridge Check")
        lines.append("")
        lines.append(f"status: `{replay['status']}`")
        lines.append(f"telemetry_jsonl: `{replay['telemetry_jsonl']}`")
        lines.append(f"samples_after_startup_filter: `{replay['samples_after_startup_filter']}`")
        gate = replay["gate"]
        lines.append(
            "- fitted_bridge median sim/real p95 tracking ratio: "
            f"`{fmt(gate.get('median_sim_to_real_p95_tracking_ratio'), 3)}`"
        )
        lines.append(
            f"- fitted_bridge max p95 model error: `{fmt(gate.get('max_p95_model_error'))}`"
        )
        lines.append("")
        lines.append("### Pitch-Chain Summary")
        lines.append("")
        lines.append(
            "| mode | joint | target_vel_p95 | applied_vel_p95 | "
            "sim_tracking_p95 | real_tracking_p95 | model_error_p95 | lag_ticks |"
        )
        lines.append("|---|---|---:|---:|---:|---:|---:|---:|")
        for mode_name in ["vanilla_no_bridge", "fitted_bridge", "stress_bridge"]:
            mode = replay["modes"][mode_name]
            for joint in PITCH_CHAIN_JOINTS:
                item = mode["joints"][joint]
                target_vel = item["target_velocity_rad_s"] or {}
                applied_vel = item["applied_target_velocity_rad_s"] or {}
                sim_tracking = item["simulated_tracking_error_rad"] or {}
                real_tracking = item["real_raw_tracking_error_rad"] or {}
                model_error = item["model_error_vs_real_actual_rad"] or {}
                lag = item["estimated_lag"] or {}
                lines.append(
                    f"| {mode_name} | {joint} | {fmt(target_vel.get('p95'))} | "
                    f"{fmt(applied_vel.get('p95'))} | {fmt(sim_tracking.get('p95'))} | "
                    f"{fmt(real_tracking.get('p95'))} | {fmt(model_error.get('p95'))} | "
                    f"{fmt(lag.get('ticks'), 0)} |"
                )
        lines.append("")
    if payload.get("closed_loop_sim"):
        closed_loop = payload["closed_loop_sim"]
        lines.append("## Closed-Loop Sim Eval")
        lines.append("")
        lines.append(f"status: `{closed_loop.get('status')}`")
        if closed_loop.get("eval_role"):
            lines.append(f"eval_role: `{closed_loop.get('eval_role')}`")
        if closed_loop.get("policy_action_gain") is not None:
            lines.append(f"policy_action_gain: `{closed_loop.get('policy_action_gain')}`")
        env = closed_loop.get("env", {})
        insertion = closed_loop.get("insertion_point", {})
        lines.append(f"env: `{env.get('env_class')}` / task `{env.get('task')}`")
        lines.append(f"obs/action dims: `{env.get('observation_size')}` / `{env.get('action_size')}`")
        lines.append(f"actuator_names: `{env.get('actuator_names')}`")
        lines.append(f"ctrl_dt: `{env.get('ctrl_dt')}`")
        lines.append(f"sim_dt: `{env.get('sim_dt')}`")
        lines.append(f"mjx_step_loop_mode: `{env.get('mjx_step_loop_mode')}`")
        lines.append(f"max_motor_velocity: `{env.get('max_motor_velocity')}`")
        if env.get("max_motor_velocity_override_rad_s") is not None:
            lines.append(
                "max_motor_velocity_override_rad_s: "
                f"`{env.get('max_motor_velocity_override_rad_s')}`"
            )
        lines.append(f"jax: `{env.get('jax_backend')}` `{env.get('jax_devices')}`")
        lines.append(f"insertion_point: `{insertion.get('type')}`")
        lines.append(f"double_rate_limit: `{insertion.get('double_rate_limit')}`")
        if closed_loop.get("error"):
            lines.append(f"worker_error: `{closed_loop.get('error')}`")
        if closed_loop.get("worker_returncode") is not None:
            lines.append(f"worker_returncode: `{closed_loop.get('worker_returncode')}`")
        worker_tail = closed_loop.get("worker_output_tail") or ""
        if worker_tail:
            interesting = [
                line
                for line in worker_tail.splitlines()
                if any(
                    token in line
                    for token in [
                        "ROCM_ERROR",
                        "JaxRuntimeError",
                        "Traceback",
                        "HOLD",
                        "Exception",
                        "error",
                        "failed",
                        "Failed",
                    ]
                )
            ]
            if interesting:
                excerpt = "\n".join(line.rstrip() for line in interesting[:20])
            else:
                excerpt = "\n".join(line.rstrip() for line in worker_tail[-1000:].splitlines())
            lines.append("")
            lines.append("Worker output excerpt:")
            lines.append("")
            lines.append("```text")
            lines.append(excerpt)
            lines.append("```")
        lines.append("")
        if closed_loop.get("candidate_gate"):
            gate = closed_loop["candidate_gate"]
            metrics = gate.get("metrics") or {}
            thresholds = gate.get("thresholds") or {}
            lines.append("### Candidate Gate")
            lines.append("")
            lines.append(f"status: `{gate.get('status')}`")
            lines.append("")
            lines.append("| metric | value | threshold |")
            lines.append("|---|---:|---:|")
            for key in [
                "max_action_saturation_pct",
                "max_pitch_tracking_p95_rad",
                "max_sent_target_velocity_p95_rad_s",
                "max_abs_body_pitch_p95_rad",
                "min_base_height_m",
                "min_reward_mean",
                "min_forward_command_tracking_ratio",
                "max_abs_forward_velocity_error_m_s",
                "max_forward_shortfall_cost_mean",
            ]:
                lines.append(
                    f"| `{key}` | {fmt(metrics.get(key))} | {fmt(thresholds.get(key))} |"
                )
            lines.append("")
        lines.append("### Mode Summary")
        lines.append("")
        lines.append(
            "| mode | samples | termination | body_pitch_p95 | base_height_min | "
            "mean_local_vx | track_ratio | reward_mean |"
        )
        lines.append("|---|---:|---|---:|---:|---:|---:|---:|")
        for mode_name, mode in (closed_loop.get("modes") or {}).items():
            body = mode.get("body_pitch_rad") or {}
            height = mode.get("base_height_m") or {}
            forward = mode.get("forward_motion") or {}
            reward = mode.get("reward") or {}
            lines.append(
                f"| {mode_name} | {mode.get('samples')} | {mode.get('termination_reason')} | "
                f"{fmt(body.get('p95'))} | {fmt(height.get('min'))} | "
                f"{fmt(forward.get('mean_velocity_x_m_s'))} | "
                f"{fmt(forward.get('command_tracking_ratio'))} | "
                f"{fmt(reward.get('mean'))} |"
            )
        lines.append("")
        reward_rows = []
        for mode_name, mode in (closed_loop.get("modes") or {}).items():
            for term_name, stats in (mode.get("reward_terms") or {}).items():
                stats = stats or {}
                reward_rows.append(
                    f"| {mode_name} | `{term_name}` | {fmt(stats.get('mean'))} | "
                    f"{fmt(stats.get('p95'))} | {fmt(stats.get('max'))} |"
                )
        if reward_rows:
            lines.append("### Reward-Term Summary")
            lines.append("")
            lines.append("| mode | term | mean | p95 | max |")
            lines.append("|---|---|---:|---:|---:|")
            lines.extend(reward_rows)
            lines.append("")
        shortfall_rows = []
        for mode_name, mode in (closed_loop.get("modes") or {}).items():
            diag = mode.get("forward_shortfall_diagnostic") or {}
            progress = diag.get("progress_ratio") or {}
            shortfall = diag.get("normalized_shortfall") or {}
            cost = diag.get("shortfall_cost") or {}
            shortfall_rows.append(
                f"| {mode_name} | `{diag.get('status')}` | "
                f"{fmt(diag.get('required_ratio'))} | "
                f"{fmt(progress.get('mean'))} | {fmt(progress.get('p95'))} | "
                f"{fmt(shortfall.get('mean'))} | {fmt(cost.get('mean'))} |"
            )
        if shortfall_rows:
            lines.append("### Forward Shortfall Diagnostic")
            lines.append("")
            lines.append(
                "| mode | status | required_ratio | progress_ratio_mean | "
                "progress_ratio_p95 | normalized_shortfall_mean | shortfall_cost_mean |"
            )
            lines.append("|---|---|---:|---:|---:|---:|---:|")
            lines.extend(shortfall_rows)
            lines.append("")
        lines.append("### Pitch-Chain Summary")
        lines.append("")
        lines.append(
            "| mode | joint | sent_vel_p95 | applied_vel_p95 | bridge_tracking_p95 | "
            "joint_tracking_p95 | lag_ticks | action_sat_pct |"
        )
        lines.append("|---|---|---:|---:|---:|---:|---:|---:|")
        rows = closed_loop_pitch_rows(closed_loop)
        if rows:
            lines.extend(rows)
        else:
            lines.append("| NA | NA | NA | NA | NA | NA | NA | NA |")
        lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    closed_status = (payload.get("closed_loop_sim") or {}).get("status")
    if payload["sim_preflight"].get("status") == "HOLD_POLICY_SIM_CONTRACT_MISMATCH":
        lines.append(
            "- Full MuJoCo policy-loop reproduction is blocked by a policy/playground "
            "contract mismatch. Do not train until the exact 101-observation / "
            "14-action training environment is located or reconstructed."
        )
    elif payload["sim_preflight"].get("status", "").startswith("HOLD") and not closed_status:
        lines.append("- Full MuJoCo policy-loop reproduction is not complete yet.")
    if payload.get("telemetry_replay"):
        lines.append(
            "- Telemetry replay validates the actuator bridge against existing real "
            "sent-target / actual-position evidence, but it is not a replacement for "
            "closed-loop sim reproduction."
        )
    if payload.get("closed_loop_sim"):
        status = payload["closed_loop_sim"].get("status")
        if status == "PASS_CLOSED_LOOP_REPRODUCTION":
            modes = set((payload["closed_loop_sim"].get("modes") or {}).keys())
            if modes == {"vanilla"}:
                lines.append(
                    "- Closed-loop vanilla sim eval completed for the requested "
                    "policy, command, task, and horizon. Interpret this as an "
                    "offline sim result only; it does not approve robot motion."
                )
            elif {"fitted", "stress"} & modes:
                lines.append(
                    "- The fitted/stress actuator bridge modes completed and can "
                    "be compared against real suspended evidence. Next step is "
                    "offline review, not robot motion."
                )
            else:
                lines.append(
                    "- Closed-loop sim reproduction completed for the requested "
                    "mode set. Review the mode summary before choosing the next "
                    "offline task."
                )
        elif status == "HOLD_BRIDGE_INSERTION_UNCLEAR":
            lines.append(
                "- The eval could not safely map the bridge insertion point. Add a "
                "small Playground adapter before training."
            )
        elif status == "PASS_CANDIDATE_SIM_GATE":
            lines.append(
                "- Candidate sim gate passed for this offline eval horizon. This "
                "does not approve robot testing; it only means the candidate cleared "
                "the configured sim-side tracking, saturation, posture, reward, "
                "and command-tracking checks."
            )
        elif str(status).startswith("HOLD_CANDIDATE"):
            lines.append(
                "- Candidate sim gate is holding. Do not use this policy on the robot."
            )
        elif status:
            lines.append(f"- Closed-loop sim gate result: `{status}`.")
    lines.append("- No robot motion, deployment, runtime behavior change, or training was performed.")
    return "\n".join(lines).rstrip()


def write_outputs(payload: dict, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    md_path = output_dir / "SIM_ACTUATOR_BRIDGE_EVAL.md"
    json_path = output_dir / "sim_actuator_bridge_eval.json"
    md_path.write_text(build_markdown(payload) + "\n")
    json_path.write_text(json.dumps(payload, indent=2) + "\n")
    print(md_path)
    print(json_path)
    if payload.get("closed_loop_sim"):
        closed_md = output_dir / "CLOSED_LOOP_ACTUATOR_BRIDGE_EVAL.md"
        closed_json = output_dir / "closed_loop_actuator_bridge_eval.json"
        closed_payload = {
            "overall_status": payload["overall_status"],
            "policy": payload["policy"],
            "fit_json": payload["fit_json"],
            "playground": payload["playground"],
            "sim_preflight": payload["sim_preflight"],
            "command_x": payload["command_x"],
            "command_y": payload["command_y"],
            "command_yaw": payload["command_yaw"],
            "task": payload["task"],
            "duration_s": payload["duration_s"],
            "seed": payload.get("seed"),
            "eval_role": payload.get("eval_role"),
            "jax_platform": payload.get("jax_platform"),
            "mjx_step_loop_mode": payload.get("mjx_step_loop_mode"),
            "telemetry_replay": None,
            "closed_loop_sim": payload["closed_loop_sim"],
        }
        closed_md.write_text(build_markdown(closed_payload) + "\n")
        closed_json.write_text(json.dumps(closed_payload, indent=2) + "\n")
        print(closed_md)
        print(closed_json)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Evaluate current policy target dynamics with fitted actuator bridge offline."
    )
    parser.add_argument("--policy", default=str(DEFAULT_POLICY))
    parser.add_argument("--fit-json", default=str(DEFAULT_FIT_JSON))
    parser.add_argument(
        "--playground-root",
        "--playground-path",
        dest="playground_root",
        default=str(DEFAULT_PLAYGROUND_ROOT),
    )
    parser.add_argument("--env-python", default=str(DEFAULT_ENV_PYTHON))
    parser.add_argument("--command-x", type=float, default=0.08)
    parser.add_argument("--command-y", type=float, default=0.0)
    parser.add_argument("--command-yaw", type=float, default=0.0)
    parser.add_argument("--task", default="flat_terrain")
    parser.add_argument("--duration", type=float, default=15.0)
    parser.add_argument(
        "--seed",
        type=int,
        default=0,
        help="JAX PRNG seed for closed-loop sim reset and delay sampling",
    )
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument(
        "--mode",
        choices=["auto", "sim", "telemetry-replay", "closed-loop-sim"],
        default="auto",
        help="auto uses telemetry replay when --telemetry-jsonl is provided; otherwise sim preflight only",
    )
    parser.add_argument(
        "--bridge-mode",
        choices=["vanilla", "fitted", "stress", "all"],
        default="all",
        help="closed-loop sim actuator bridge mode",
    )
    parser.add_argument(
        "--eval-role",
        choices=["reproduction", "candidate"],
        default="reproduction",
        help=(
            "reproduction checks whether the fitted bridge reproduces real x=0.08 "
            "baseline degradation; candidate checks whether a new policy clears "
            "offline sim-side gates"
        ),
    )
    parser.add_argument("--telemetry-jsonl", default=None)
    parser.add_argument("--startup-ticks", type=int, default=50)
    parser.add_argument("--max-lag-ticks", type=int, default=12)
    parser.add_argument("--stress-delay-ticks", type=int, default=6)
    parser.add_argument("--stress-tau-s", type=float, default=0.10)
    parser.add_argument("--stress-velocity-limit-rad-s", type=float, default=3.2)
    parser.add_argument("--expected-observation-dim", type=int, default=101)
    parser.add_argument("--expected-action-dim", type=int, default=14)
    parser.add_argument(
        "--inspect-policy-io",
        action="store_true",
        help="query ONNX Runtime for model IO metadata; default uses audited contract",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="return nonzero on HOLD status; default is report-only",
    )
    parser.add_argument(
        "--closed-loop-timeout-s",
        type=int,
        default=900,
        help="timeout for the contained closed-loop worker process",
    )
    parser.add_argument(
        "--jax-platform",
        choices=["cpu", "gpu", "tpu"],
        default=None,
        help=(
            "set JAX_PLATFORM_NAME for closed-loop worker subprocesses. Use "
            "`--jax-platform cpu` for local CPU candidate gates when the default "
            "environment would otherwise select the blocked ROCm backend."
        ),
    )
    parser.add_argument(
        "--jax-platforms",
        default=None,
        help=(
            "Optional JAX_PLATFORMS override for closed-loop worker subprocesses. "
            "When omitted, `--jax-platform cpu` automatically uses "
            "`JAX_PLATFORMS=cpu` so local CPU gates do not probe a broken GPU "
            "backend."
        ),
    )
    parser.add_argument(
        "--mjx-step-loop-mode",
        choices=["default", "scan", "python", "python_block_each"],
        default="default",
        help=(
            "closed-loop MJX substep mode. default/scan uses the Playground "
            "lax.scan helper; python/python_block_each use a slow host-driven "
            "substep loop for local ROCm correctness checks."
        ),
    )
    parser.add_argument(
        "--policy-action-gain",
        type=float,
        default=1.0,
        help=(
            "Eval-only multiplier applied to ONNX policy actions before the "
            "sim step. Default 1.0 preserves the policy exactly; values below "
            "1.0 approximate an ONNX output-damping wrapper and do not modify "
            "the policy file or robot runtime."
        ),
    )
    parser.add_argument(
        "--max-motor-velocity-override-rad-s",
        type=float,
        default=None,
        help=(
            "Eval-only override for the Playground max_motor_velocity target "
            "slew limit. Default None preserves the env/runtime value. Use this "
            "only for offline diagnostics of lower target-rate limits."
        ),
    )
    parser.add_argument(
        "--forward-diagnostic-required-ratio",
        type=float,
        default=0.5,
        help=(
            "Reward-config-independent forward shortfall diagnostic ratio. "
            "At command x, the diagnostic reports shortfall below "
            "abs(command_x) * this ratio. It does not change policy or robot "
            "behavior."
        ),
    )
    parser.add_argument(
        "--forward-diagnostic-deadband",
        type=float,
        default=0.02,
        help=(
            "Deadband for the reward-config-independent forward shortfall "
            "diagnostic. Commands below this magnitude are treated as no "
            "forward-progress requirement."
        ),
    )
    parser.add_argument(
        "--sim-preflight-timeout-s",
        type=int,
        default=90,
        help="timeout for the Playground contract instantiation preflight",
    )
    parser.add_argument(
        "--trace-jsonl",
        default=None,
        help=(
            "Optional closed-loop per-tick trace output. This is intended for "
            "small failure forensics; normal eval summaries stay compact."
        ),
    )
    parser.add_argument(
        "--reward-overrides-json",
        default=None,
        help=(
            "Optional JSON file containing staged-curriculum phase reward "
            "overrides. When provided, closed-loop eval replays the same reward "
            "scales, command-progress failure settings, and reward clip bounds "
            "used during training."
        ),
    )
    parser.add_argument(
        "--reward-overrides-phase",
        default=None,
        help=(
            "Phase name to select from --reward-overrides-json when the file "
            "contains a staged plan with a phases array. Defaults to the first "
            "phase."
        ),
    )
    parser.add_argument(
        "--_closed-loop-worker",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--_closed-loop-worker-json",
        default=None,
        help=argparse.SUPPRESS,
    )
    args = parser.parse_args()
    apply_jax_platform_env(args.jax_platform, args.jax_platforms)

    policy_path = Path(args.policy).expanduser().resolve()
    fit_path = Path(args.fit_json).expanduser().resolve()
    playground_root = Path(args.playground_root).expanduser().resolve()
    env_python = Path(args.env_python).expanduser().absolute()
    fit = load_fit_json(fit_path)
    reward_overrides = load_reward_overrides(
        None if args.reward_overrides_json is None else Path(args.reward_overrides_json),
        args.reward_overrides_phase,
    )

    policy = inspect_policy(
        policy_path,
        args.expected_observation_dim,
        args.expected_action_dim,
        args.inspect_policy_io,
    )
    playground = {
        "static": static_playground_contract(playground_root),
        "instantiated": instantiate_env_contract(
            env_python, playground_root, args.sim_preflight_timeout_s
        ),
        "env_python": str(env_python),
    }
    sim_preflight = run_sim_preflight(policy, playground)
    run_replay = args.mode == "telemetry-replay" or (
        args.mode == "auto" and args.telemetry_jsonl
    )
    telemetry_replay = run_telemetry_replay(args, fit) if run_replay else None
    closed_loop_sim = None
    if args.mode == "closed-loop-sim":
        preflight_status = str(sim_preflight.get("status", ""))
        preflight_hold = (
            sim_preflight.get("status") not in {"HOLD_SIM_INTEGRATION_PENDING"}
            and preflight_status.startswith("HOLD")
        )
        if args._closed_loop_worker:
            if preflight_hold:
                closed_loop_sim = {
                    "status": sim_preflight["status"],
                    "error": sim_preflight.get("reason", "contract preflight failed"),
                    "sim_preflight": sim_preflight,
                }
            else:
                closed_loop_sim = run_closed_loop_sim(
                    ClosedLoopConfig(
                        policy_path=policy_path,
                        fit=fit,
                        playground_root=playground_root,
                        command_x=args.command_x,
                        command_y=args.command_y,
                        command_yaw=args.command_yaw,
                        duration_s=args.duration,
                        task=args.task,
                        seed=args.seed,
                        bridge_mode=args.bridge_mode,
                        expected_observation_dim=args.expected_observation_dim,
                        expected_action_dim=args.expected_action_dim,
                        eval_role=args.eval_role,
                        mjx_step_loop_mode=args.mjx_step_loop_mode,
                        policy_action_gain=args.policy_action_gain,
                        max_motor_velocity_override_rad_s=(
                            args.max_motor_velocity_override_rad_s
                        ),
                        forward_diagnostic_required_ratio=(
                            args.forward_diagnostic_required_ratio
                        ),
                        forward_diagnostic_deadband=(
                            args.forward_diagnostic_deadband
                        ),
                        reward_overrides=reward_overrides,
                        trace_jsonl=(
                            None if args.trace_jsonl is None else Path(args.trace_jsonl)
                        ),
                    )
                )
            if args._closed_loop_worker_json:
                Path(args._closed_loop_worker_json).write_text(
                    json.dumps(closed_loop_sim, indent=2) + "\n"
                )
                return 0
        elif preflight_hold:
            closed_loop_sim = {
                "status": sim_preflight["status"],
                "error": sim_preflight.get("reason", "contract preflight failed"),
            }
        else:
            closed_loop_sim = run_closed_loop_worker(args)

    if closed_loop_sim:
        overall = closed_loop_sim.get("status", "HOLD_SIM_RUNTIME_ERROR")
    elif args.mode == "sim" and sim_preflight["status"].startswith("HOLD"):
        overall = sim_preflight["status"]
    elif telemetry_replay:
        if sim_preflight["status"].startswith("HOLD"):
            overall = sim_preflight["status"]
        else:
            overall = telemetry_replay["status"]
    else:
        overall = sim_preflight["status"]

    payload = {
        "overall_status": overall,
        "policy": policy,
        "fit_json": str(fit_path),
        "playground": playground,
        "sim_preflight": sim_preflight,
        "command_x": args.command_x,
        "command_y": args.command_y,
        "command_yaw": args.command_yaw,
        "task": args.task,
        "duration_s": args.duration,
        "seed": args.seed,
        "eval_role": args.eval_role,
        "jax_platform": args.jax_platform,
        "mjx_step_loop_mode": args.mjx_step_loop_mode,
        "reward_overrides_json": args.reward_overrides_json,
        "reward_overrides_phase": args.reward_overrides_phase,
        "reward_overrides": reward_overrides,
        "telemetry_replay": telemetry_replay,
        "closed_loop_sim": closed_loop_sim,
    }
    write_outputs(payload, Path(args.output_dir))
    if args.strict and str(overall).startswith("HOLD"):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
