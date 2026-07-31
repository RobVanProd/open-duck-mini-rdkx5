#!/usr/bin/env python3
"""CPU-only contract check for the default-off direct joint tracking reward."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


def scalar(value: object) -> float:
    return float(value.item() if hasattr(value, "item") else value)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--playground-path", default=str(ROOT.parent / "Open_Duck_Playground"))
    parser.add_argument("--output-json", required=True)
    args = parser.parse_args()
    output = Path(args.output_json).resolve()

    os.environ["JAX_PLATFORMS"] = "cpu"
    os.environ["JAX_PLATFORM_NAME"] = "cpu"
    os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
    os.environ["HIP_VISIBLE_DEVICES"] = "-1"

    playground = Path(args.playground_path).resolve()
    sys.path.insert(0, str(playground))
    os.chdir(playground)

    import jax  # noqa: PLC0415
    import jax.numpy as jp  # noqa: PLC0415
    from playground.open_duck_mini_v2 import joystick  # noqa: PLC0415

    cfg = joystick.default_config()
    default_scale = scalar(cfg.reward_config.scales.joint_target_tracking)
    default_delta = scalar(cfg.reward_config.joint_target_tracking_huber_delta)
    cfg.push_config.enable = False
    cfg.noise_config.action_min_delay = 0
    cfg.noise_config.action_max_delay = 1
    cfg.actuator_bridge.enable = True
    cfg.actuator_bridge.delay_min_ticks = 3
    cfg.actuator_bridge.delay_max_ticks = 3
    cfg.reward_config.scales.joint_target_tracking = -1.0
    cfg.reward_config.joint_target_tracking_huber_delta = 0.03

    env = joystick.Joystick(config=cfg)
    state = env.reset(jax.random.PRNGKey(0))
    action = jp.zeros(env.action_size)
    for index in (2, 3, 4, 11, 12, 13):
        action = action.at[index].set(0.25)
    state = env.step(state, action)

    cost = scalar(state.info["joint_target_tracking_cost"])
    bridge_cost = scalar(state.info["actuator_bridge_tracking_cost"])
    diagnostic = scalar(state.metrics["diagnostic/joint_target_tracking_cost"])
    scaled_cost = scalar(state.metrics["cost/joint_target_tracking"])
    payload = {
        "status": "PASS_JOINT_TARGET_TRACKING_CONTRACT",
        "backend": jax.default_backend(),
        "devices": [str(device) for device in jax.devices()],
        "gpu_visibility": {
            "CUDA_VISIBLE_DEVICES": os.environ["CUDA_VISIBLE_DEVICES"],
            "HIP_VISIBLE_DEVICES": os.environ["HIP_VISIBLE_DEVICES"],
        },
        "default_off": default_scale == 0.0,
        "default_scale": default_scale,
        "default_huber_delta": default_delta,
        "enabled_scale": -1.0,
        "enabled_huber_delta": 0.03,
        "joint_indices": list(cfg.reward_config.joint_target_tracking_joint_indices),
        "joint_target_tracking_cost": cost,
        "actuator_bridge_tracking_cost": bridge_cost,
        "joint_to_bridge_cost_ratio": None if bridge_cost == 0.0 else cost / bridge_cost,
        "diagnostic_metric": diagnostic,
        "scaled_cost_metric": scaled_cost,
        "finite": bool(jp.isfinite(state.reward) & jp.isfinite(cost)),
        "obs_dim": int(state.obs["state"].shape[0]),
        "action_dim": int(env.action_size),
        "offline_only": True,
    }
    checks = [
        payload["backend"] == "cpu",
        payload["devices"] == ["TFRT_CPU_0"],
        payload["default_off"],
        cost > 0.0,
        abs(diagnostic - cost) <= 1.0e-9,
        abs(scaled_cost - cost) <= 1.0e-9,
        payload["finite"],
        payload["obs_dim"] == 101,
        payload["action_dim"] == 14,
    ]
    if not all(checks):
        payload["status"] = "HOLD_JOINT_TARGET_TRACKING_CONTRACT"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps(payload, indent=2))
    return 0 if all(checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())
