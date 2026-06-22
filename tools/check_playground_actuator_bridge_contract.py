#!/usr/bin/env python3
"""Check the Open Duck Playground actuator bridge contract.

This is an offline sim/config check. It does not train, touch the robot, SSH, or
deploy anything.
"""

from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PLAYGROUND = ROOT.parent / "Open_Duck_Playground"
REQUIRED_RUNNER_FLAGS = [
    "--enable_actuator_bridge",
    "--actuator_bridge_delay_min_ticks",
    "--actuator_bridge_delay_max_ticks",
    "--actuator_bridge_tau_min_s",
    "--actuator_bridge_tau_max_s",
    "--actuator_bridge_velocity_limit_min_rad_s",
    "--actuator_bridge_velocity_limit_max_rad_s",
    "--actuator_bridge_per_joint_variation",
    "--target_rate_scale",
    "--actuator_tracking_scale",
]
REQUIRED_METRICS = [
    "diagnostic/target_velocity_cost",
    "diagnostic/actuator_bridge_tracking_cost",
    "diagnostic/actuator_bridge_delay_ticks",
    "diagnostic/actuator_bridge_tau_mean_s",
    "diagnostic/actuator_bridge_velocity_limit_mean_rad_s",
]


def as_float(value: Any) -> float:
    return float(value.item() if hasattr(value, "item") else value)


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def check_runner_flags(playground: Path) -> dict[str, Any]:
    runner = playground / "playground/open_duck_mini_v2/runner.py"
    if not runner.exists():
        return {"status": "HOLD_RUNNER_MISSING", "path": str(runner)}
    text = runner.read_text()
    missing = [flag for flag in REQUIRED_RUNNER_FLAGS if flag not in text]
    return {
        "status": "PASS_RUNNER_FLAGS" if not missing else "HOLD_RUNNER_FLAGS",
        "path": str(runner),
        "missing": missing,
    }


def validate_config(cfg: Any) -> dict[str, Any]:
    required = [
        ("actuator_bridge.enable", cfg.actuator_bridge.enable, False),
        ("actuator_bridge.delay_min_ticks", cfg.actuator_bridge.delay_min_ticks, 3),
        ("actuator_bridge.delay_max_ticks", cfg.actuator_bridge.delay_max_ticks, 8),
        ("actuator_bridge.tau_min_s", cfg.actuator_bridge.tau_min_s, 0.06),
        ("actuator_bridge.tau_max_s", cfg.actuator_bridge.tau_max_s, 0.14),
        (
            "actuator_bridge.velocity_limit_min_rad_s",
            cfg.actuator_bridge.velocity_limit_min_rad_s,
            2.5,
        ),
        (
            "actuator_bridge.velocity_limit_max_rad_s",
            cfg.actuator_bridge.velocity_limit_max_rad_s,
            4.7,
        ),
        ("actuator_bridge.per_joint_variation", cfg.actuator_bridge.per_joint_variation, 0.15),
        ("reward_config.scales.target_rate", cfg.reward_config.scales.target_rate, 0.0),
        (
            "reward_config.scales.actuator_tracking",
            cfg.reward_config.scales.actuator_tracking,
            0.0,
        ),
    ]
    checks = []
    for name, actual, expected in required:
        if isinstance(expected, float):
            passed = math.isclose(float(actual), expected, rel_tol=0.0, abs_tol=1.0e-9)
        else:
            passed = actual == expected
        checks.append({"name": name, "actual": actual, "expected": expected, "pass": passed})
    return {
        "status": "PASS_DEFAULT_CONFIG" if all(item["pass"] for item in checks) else "HOLD_DEFAULT_CONFIG",
        "checks": checks,
    }


def run_step_check(playground: Path, platform: str, enabled: bool) -> dict[str, Any]:
    os.environ["JAX_PLATFORM_NAME"] = platform
    sys.path.insert(0, str(playground))
    os.chdir(playground)

    import jax  # noqa: PLC0415
    import jax.numpy as jp  # noqa: PLC0415
    from playground.open_duck_mini_v2 import joystick  # noqa: PLC0415

    cfg = joystick.default_config()
    cfg.push_config.enable = False
    cfg.noise_config.action_min_delay = 0
    cfg.noise_config.action_max_delay = 1
    cfg.actuator_bridge.enable = enabled

    env = joystick.Joystick(config=cfg)
    state = env.reset(jax.random.PRNGKey(0))
    action = jp.zeros(env.action_size)
    if enabled:
        for index in (2, 3, 4, 11, 12, 13):
            action = action.at[index].set(0.25)
    state = env.step(state, action)

    missing_metrics = [key for key in REQUIRED_METRICS if key not in state.metrics]
    obs_finite = bool(jp.all(jp.isfinite(state.obs["state"])))
    tracking_cost = as_float(state.info["actuator_bridge_tracking_cost"])
    expected_tracking_positive = enabled
    tracking_ok = tracking_cost > 0.0 if expected_tracking_positive else tracking_cost == 0.0

    return {
        "status": (
            "PASS_STEP_CHECK"
            if obs_finite and not missing_metrics and tracking_ok
            else "HOLD_STEP_CHECK"
        ),
        "platform": jax.default_backend(),
        "devices": [str(device) for device in jax.devices()],
        "bridge_enabled": enabled,
        "action_size": int(env.action_size),
        "obs_state_shape": list(state.obs["state"].shape),
        "obs_privileged_shape": list(state.obs["privileged_state"].shape),
        "missing_metrics": missing_metrics,
        "obs_finite": obs_finite,
        "target_velocity_cost": as_float(state.info["target_velocity_cost"]),
        "actuator_bridge_tracking_cost": tracking_cost,
        "delay_ticks": int(state.info["actuator_bridge_delay_ticks"]),
        "tau_mean_s": as_float(jp.mean(state.info["actuator_bridge_tau_s"])),
        "velocity_limit_mean_rad_s": as_float(
            jp.mean(state.info["actuator_bridge_velocity_limit_rad_s"])
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check Playground actuator bridge default-off contract."
    )
    parser.add_argument("--playground-path", default=str(DEFAULT_PLAYGROUND))
    parser.add_argument("--platform", choices=["cpu", "gpu"], default="cpu")
    parser.add_argument(
        "--step-check",
        action="store_true",
        help="Run slow CPU/GPU env step checks. Prefer smoke_actuator_bridge_wrapper.py for routine validation.",
    )
    parser.add_argument("--output-json")
    args = parser.parse_args()

    playground = Path(args.playground_path).expanduser().resolve()
    if not (playground / "playground/open_duck_mini_v2/joystick.py").exists():
        fail(f"missing Open Duck Playground checkout: {playground}")

    sys.path.insert(0, str(playground))
    try:
        from playground.open_duck_mini_v2 import joystick  # noqa: PLC0415
    except ModuleNotFoundError as exc:
        payload = {
            "status": "HOLD_IMPORT_MISSING",
            "playground_path": str(playground),
            "missing_module": exc.name,
            "recommended_python": str(ROOT.parent / "envs/open-duck-playground/bin/python"),
        }
        text = json.dumps(payload, indent=2, sort_keys=True)
        print(text)
        if args.output_json:
            output = Path(args.output_json)
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(text + "\n")
        return 1

    cfg = joystick.default_config()
    payload: dict[str, Any] = {
        "playground_path": str(playground),
        "runner_flags": check_runner_flags(playground),
        "default_config": validate_config(cfg),
        "expected_obs_dim": 101,
        "expected_action_dim": 14,
    }

    if args.step_check:
        payload["step_disabled"] = run_step_check(playground, args.platform, enabled=False)
        payload["step_enabled"] = run_step_check(playground, args.platform, enabled=True)

    holds = []
    if not payload["runner_flags"]["status"].startswith("PASS"):
        holds.append(payload["runner_flags"]["status"])
    if not payload["default_config"]["status"].startswith("PASS"):
        holds.append(payload["default_config"]["status"])
    for key in ("step_disabled", "step_enabled"):
        if key in payload and not payload[key]["status"].startswith("PASS"):
            holds.append(f"{key}:{payload[key]['status']}")
    payload["status"] = "PASS_ACTUATOR_BRIDGE_CONTRACT" if not holds else "HOLD_ACTUATOR_BRIDGE_CONTRACT"
    payload["holds"] = holds

    text = json.dumps(payload, indent=2, sort_keys=True)
    print(text)
    if args.output_json:
        output = Path(args.output_json)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text + "\n")
    return 0 if payload["status"].startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
