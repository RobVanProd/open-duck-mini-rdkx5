#!/usr/bin/env python3
"""Smoke-test the Open Duck Playground actuator bridge wrapper.

This is an offline sim check only. It does not train, export policies, touch the
robot, SSH, or deploy anything.
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
PITCH_CHAIN = {
    "left_hip_pitch": 2,
    "left_knee": 3,
    "left_ankle": 4,
    "right_hip_pitch": 11,
    "right_knee": 12,
    "right_ankle": 13,
}


def as_float(value: Any) -> float:
    return float(value.item() if hasattr(value, "item") else value)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run a tiny non-training actuator bridge wrapper smoke test."
    )
    parser.add_argument("--playground-path", default=str(DEFAULT_PLAYGROUND))
    parser.add_argument("--platform", default="cpu", choices=["cpu", "gpu"])
    parser.add_argument("--steps", type=int, default=10)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--amplitude", type=float, default=0.25)
    parser.add_argument("--output-json")
    args = parser.parse_args()

    if args.steps < 1:
        raise SystemExit("--steps must be >= 1")

    os.environ.setdefault("JAX_PLATFORM_NAME", args.platform)
    playground = Path(args.playground_path).expanduser().resolve()
    if not (playground / "playground/open_duck_mini_v2/joystick.py").exists():
        print(f"Missing Open Duck Playground checkout: {playground}", file=sys.stderr)
        return 2

    sys.path.insert(0, str(playground))
    os.chdir(playground)

    import jax  # noqa: PLC0415
    import jax.numpy as jp  # noqa: PLC0415
    from playground.open_duck_mini_v2 import joystick  # noqa: PLC0415

    cfg = joystick.default_config()
    if not hasattr(cfg, "actuator_bridge"):
        print(
            "HOLD_ACTUATOR_BRIDGE_NOT_PATCHED: joystick config has no actuator_bridge",
            file=sys.stderr,
        )
        return 3

    cfg.actuator_bridge.enable = True
    cfg.push_config.enable = False
    cfg.noise_config.action_min_delay = 0
    cfg.noise_config.action_max_delay = 1

    env = joystick.Joystick(config=cfg)
    state = env.reset(jax.random.PRNGKey(args.seed))

    max_target_cost = 0.0
    max_tracking_cost = 0.0
    last_obs_finite = True
    action_size = int(env.action_size)

    for step in range(args.steps):
        action = jp.zeros(action_size)
        wave = args.amplitude * math.sin(2.0 * math.pi * (step + 1) / max(args.steps, 2))
        for index in PITCH_CHAIN.values():
            action = action.at[index].set(wave)
        state = env.step(state, action)
        obs = state.obs["state"]
        last_obs_finite = bool(jp.all(jp.isfinite(obs)))
        max_target_cost = max(max_target_cost, as_float(state.info["target_velocity_cost"]))
        max_tracking_cost = max(
            max_tracking_cost, as_float(state.info["actuator_bridge_tracking_cost"])
        )
        if not last_obs_finite:
            break

    result = {
        "status": "PASS_ACTUATOR_BRIDGE_SMOKE" if last_obs_finite else "HOLD_NONFINITE_OBS",
        "playground_path": str(playground),
        "platform": jax.default_backend(),
        "devices": [str(device) for device in jax.devices()],
        "steps": args.steps,
        "action_size": action_size,
        "obs_state_shape": list(state.obs["state"].shape),
        "obs_privileged_shape": list(state.obs["privileged_state"].shape),
        "bridge_delay_ticks": int(state.info["actuator_bridge_delay_ticks"]),
        "bridge_tau_shape": list(state.info["actuator_bridge_tau_s"].shape),
        "bridge_velocity_limit_shape": list(
            state.info["actuator_bridge_velocity_limit_rad_s"].shape
        ),
        "applied_targets_shape": list(state.info["actuator_bridge_applied_targets"].shape),
        "max_target_velocity_cost": max_target_cost,
        "max_actuator_bridge_tracking_cost": max_tracking_cost,
    }

    text = json.dumps(result, indent=2, sort_keys=True)
    print(text)
    if args.output_json:
        Path(args.output_json).write_text(text + "\n")

    return 0 if result["status"].startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
