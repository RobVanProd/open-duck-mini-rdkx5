#!/usr/bin/env python3
"""Analyze how ONNX policies react to commanded forward velocity.

This is an offline probe. It feeds a small synthetic upright observation into
one or more ONNX policies while sweeping obs[6] command_x. It does not run
MuJoCo, train, SSH, deploy, or touch the robot.
"""

from __future__ import annotations

import argparse
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import sys
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_MD = ROOT / "outputs" / "analysis" / "POLICY_COMMAND_SENSITIVITY.md"
DEFAULT_OUTPUT_JSON = ROOT / "outputs" / "analysis" / "policy_command_sensitivity.json"
EXPECTED_OBS_DIM = 101
EXPECTED_ACTION_DIM = 14
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


@contextmanager
def suppress_native_stderr():
    """Temporarily silence native-library writes to stderr."""

    stderr_fd = sys.stderr.fileno()
    saved_fd = os.dup(stderr_fd)
    try:
        with open(os.devnull, "w") as devnull:
            os.dup2(devnull.fileno(), stderr_fd)
            yield
    finally:
        os.dup2(saved_fd, stderr_fd)
        os.close(saved_fd)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_policy(value: str) -> tuple[str, Path]:
    if "=" in value:
        label, raw_path = value.split("=", 1)
        return label.strip(), Path(raw_path).expanduser().resolve()
    path = Path(value).expanduser().resolve()
    return path.stem, path


def parse_commands(value: str) -> list[float]:
    commands = [float(part.strip()) for part in value.split(",") if part.strip()]
    if not commands:
        raise argparse.ArgumentTypeError("at least one command value is required")
    return commands


def synthetic_observation(command_x: float, accel_z: float, phase_cos: float, phase_sin: float) -> np.ndarray:
    obs = np.zeros((1, EXPECTED_OBS_DIM), dtype=np.float32)
    obs[0, 5] = accel_z
    obs[0, 6] = command_x
    obs[0, 99] = phase_cos
    obs[0, 100] = phase_sin
    return obs


def load_session(path: Path):
    try:
        import onnxruntime as ort  # noqa: PLC0415
    except Exception as exc:  # noqa: BLE001
        return None, {"status": "HOLD_ONNXRUNTIME_MISSING", "error": f"{type(exc).__name__}: {exc}"}

    options = ort.SessionOptions()
    options.log_severity_level = 3
    try:
        with suppress_native_stderr():
            session = ort.InferenceSession(
                str(path),
                sess_options=options,
                providers=["CPUExecutionProvider"],
            )
    except Exception as exc:  # noqa: BLE001
        return None, {"status": "HOLD_ONNX_SESSION_FAILED", "error": f"{type(exc).__name__}: {exc}"}
    return session, {}


def shape_list(shape: Any) -> list[Any]:
    return [int(dim) if isinstance(dim, int) else str(dim) for dim in shape]


def action_stats(action: np.ndarray) -> dict[str, Any]:
    flat = np.asarray(action, dtype=float).reshape(-1)
    return {
        "l2_norm": float(np.linalg.norm(flat)),
        "mean": float(np.mean(flat)),
        "max_abs": float(np.max(np.abs(flat))),
        "saturation_pct": float(np.mean(np.abs(flat) >= 0.98) * 100.0),
    }


def delta_stats(action: np.ndarray, reference: np.ndarray) -> dict[str, Any]:
    delta = np.asarray(action, dtype=float).reshape(-1) - np.asarray(reference, dtype=float).reshape(-1)
    return {
        "l2_norm": float(np.linalg.norm(delta)),
        "max_abs": float(np.max(np.abs(delta))),
        "mean_abs": float(np.mean(np.abs(delta))),
    }


def analyze_policy(
    label: str,
    path: Path,
    commands: list[float],
    base_command: float,
    accel_z: float,
    phase_cos: float,
    phase_sin: float,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "label": label,
        "path": str(path),
        "status": "UNKNOWN",
    }
    if not path.exists():
        payload.update({"status": "MISSING_POLICY", "error": "policy path does not exist"})
        return payload

    payload["sha256"] = sha256_file(path)
    session, error = load_session(path)
    if session is None:
        payload.update(error)
        return payload

    inputs = session.get_inputs()
    outputs = session.get_outputs()
    payload["input_name"] = inputs[0].name if inputs else None
    payload["output_name"] = outputs[0].name if outputs else None
    payload["input_shape"] = shape_list(inputs[0].shape) if inputs else None
    payload["output_shape"] = shape_list(outputs[0].shape) if outputs else None
    if not inputs or not outputs:
        payload.update({"status": "HOLD_POLICY_CONTRACT", "error": "missing ONNX inputs or outputs"})
        return payload

    input_dim = payload["input_shape"][-1]
    output_dim = payload["output_shape"][-1]
    if input_dim != EXPECTED_OBS_DIM or output_dim != EXPECTED_ACTION_DIM:
        payload.update(
            {
                "status": "HOLD_POLICY_CONTRACT",
                "error": f"expected {EXPECTED_OBS_DIM}->{EXPECTED_ACTION_DIM}, got {input_dim}->{output_dim}",
            }
        )
        return payload

    actions: dict[str, list[float]] = {}
    metrics: dict[str, dict[str, Any]] = {}
    with suppress_native_stderr():
        for command_x in commands:
            obs = synthetic_observation(command_x, accel_z, phase_cos, phase_sin)
            action = session.run([outputs[0].name], {inputs[0].name: obs})[0].astype(float).reshape(-1)
            key = f"{command_x:g}"
            actions[key] = [float(value) for value in action]
            metrics[key] = action_stats(action)

    base_key = f"{base_command:g}"
    if base_key not in actions:
        obs = synthetic_observation(base_command, accel_z, phase_cos, phase_sin)
        with suppress_native_stderr():
            action = session.run([outputs[0].name], {inputs[0].name: obs})[0].astype(float).reshape(-1)
        actions[base_key] = [float(value) for value in action]
        metrics[base_key] = action_stats(action)

    base_action = np.asarray(actions[base_key], dtype=float)
    deltas: dict[str, dict[str, Any]] = {}
    top_deltas: dict[str, list[dict[str, Any]]] = {}
    for key, values in actions.items():
        action = np.asarray(values, dtype=float)
        deltas[key] = delta_stats(action, base_action)
        diff = action - base_action
        ranked = sorted(
            (
                {
                    "joint": JOINT_NAMES[index],
                    "index": index,
                    "base_action": float(base_action[index]),
                    "action": float(action[index]),
                    "delta": float(diff[index]),
                    "abs_delta": float(abs(diff[index])),
                }
                for index in range(len(JOINT_NAMES))
            ),
            key=lambda item: item["abs_delta"],
            reverse=True,
        )
        top_deltas[key] = ranked[:6]

    positive_key = max(
        actions,
        key=lambda key: float(key) if float(key) >= base_command else -1.0e9,
    )
    payload.update(
        {
            "status": "PASS_COMMAND_SENSITIVITY_ANALYSIS",
            "base_command_x": base_command,
            "commands": commands,
            "actions": actions,
            "action_metrics": metrics,
            "delta_from_base": deltas,
            "top_delta_joints": top_deltas,
            "largest_positive_command_key": positive_key,
        }
    )
    return payload


def fmt(value: Any, digits: int = 4) -> str:
    if value is None:
        return "NA"
    if isinstance(value, int | float):
        return f"{float(value):.{digits}f}"
    return str(value)


def write_markdown(results: list[dict[str, Any]], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Policy Command Sensitivity",
        "",
        "Offline ONNX probe using a synthetic upright observation. This report",
        "does not run MuJoCo, train, SSH, deploy, or touch the robot.",
        "",
        "The purpose is to separate command insensitivity from closed-loop",
        "locomotion failure. A policy can react to `obs[6]` and still fail to",
        "produce useful forward motion in sim.",
        "",
        "## Summary",
        "",
        "| policy | status | action dim | base norm | x=0.08 delta L2 | x=0.08 delta max | x=0.08 action max | x=0.08 sat % |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for result in results:
        metrics = result.get("action_metrics") if isinstance(result.get("action_metrics"), dict) else {}
        deltas = result.get("delta_from_base") if isinstance(result.get("delta_from_base"), dict) else {}
        base_key = f"{float(result.get('base_command_x', 0.0)):g}"
        x008_key = "0.08"
        base = metrics.get(base_key, {}) if isinstance(metrics.get(base_key), dict) else {}
        x008 = metrics.get(x008_key, {}) if isinstance(metrics.get(x008_key), dict) else {}
        delta = deltas.get(x008_key, {}) if isinstance(deltas.get(x008_key), dict) else {}
        lines.append(
            "| `{label}` | `{status}` | {dim} | {base_norm} | {delta_l2} | {delta_max} | {action_max} | {sat} |".format(
                label=result.get("label"),
                status=result.get("status"),
                dim=(result.get("output_shape") or ["NA"])[-1],
                base_norm=fmt(base.get("l2_norm")),
                delta_l2=fmt(delta.get("l2_norm")),
                delta_max=fmt(delta.get("max_abs")),
                action_max=fmt(x008.get("max_abs")),
                sat=fmt(x008.get("saturation_pct")),
            )
        )

    lines.extend(["", "## Top x=0.08 Action Changes", ""])
    for result in results:
        lines.extend(
            [
                f"### {result.get('label')}",
                "",
                f"- status: `{result.get('status')}`",
                f"- path: `{result.get('path')}`",
                f"- sha256: `{result.get('sha256', 'NA')}`",
                "",
                "| joint | index | action@0 | action@0.08 | delta |",
                "|---|---:|---:|---:|---:|",
            ]
        )
        top = result.get("top_delta_joints", {}).get("0.08", [])
        if not top:
            lines.append("| NA | NA | NA | NA | NA |")
        for item in top:
            lines.append(
                "| `{joint}` | {index} | {base} | {action} | {delta} |".format(
                    joint=item.get("joint"),
                    index=item.get("index"),
                    base=fmt(item.get("base_action")),
                    action=fmt(item.get("action")),
                    delta=fmt(item.get("delta")),
                )
            )
        lines.append("")

    lines.extend(
        [
            "## Interpretation",
            "",
            "- Nonzero `x=0.08 delta L2` means the ONNX policy changes its action",
            "  when `command_x` changes in the synthetic observation.",
            "- A command-sensitive policy can still fail the closed-loop gate if the",
            "  action sequence does not generate effective locomotion under the",
            "  actuator bridge and environment dynamics.",
            "- This probe uses one synthetic upright observation, so it is evidence",
            "  about static command dependence, not a replacement for closed-loop",
            "  MuJoCo gates.",
            "",
        ]
    )
    output.write_text("\n".join(lines))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "policies",
        nargs="+",
        help="ONNX policy paths, optionally as label=/path/to/policy.onnx",
    )
    parser.add_argument(
        "--commands",
        type=parse_commands,
        default=parse_commands("-0.08,0.0,0.04,0.08,0.12"),
        help="comma-separated command_x values to probe",
    )
    parser.add_argument("--base-command-x", type=float, default=0.0)
    parser.add_argument("--accel-z", type=float, default=9.490142)
    parser.add_argument("--phase-cos", type=float, default=1.0)
    parser.add_argument("--phase-sin", type=float, default=0.0)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    args = parser.parse_args()

    results = [
        analyze_policy(
            label,
            path,
            args.commands,
            args.base_command_x,
            args.accel_z,
            args.phase_cos,
            args.phase_sin,
        )
        for label, path in (parse_policy(value) for value in args.policies)
    ]
    payload = {
        "status": "PASS_POLICY_COMMAND_SENSITIVITY_REPORT",
        "observation_contract": {
            "shape": [1, EXPECTED_OBS_DIM],
            "gyro_indices": [0, 1, 2],
            "accel_indices": [3, 4, 5],
            "command_x_index": 6,
            "phase_indices": [99, 100],
            "synthetic_accel_z": args.accel_z,
            "synthetic_phase": [args.phase_cos, args.phase_sin],
        },
        "results": results,
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2))
    write_markdown(results, args.output_md)
    print(f"Wrote {args.output_md}")
    print(f"Wrote {args.output_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
