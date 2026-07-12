#!/usr/bin/env python3
"""Verify the pinned upstream environment contract on CPU without training."""

from __future__ import annotations

import argparse
import importlib.metadata as metadata
import json
import os
from pathlib import Path
import sys

EXPECTED = {"jax": "0.8.2", "jaxlib": "0.8.2", "mujoco": "3.9.0", "playground": "0.0.5"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--playground-path", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    versions = {name: metadata.version(name) for name in EXPECTED}
    if versions != EXPECTED:
        raise SystemExit(f"dependency mismatch: expected {EXPECTED}, got {versions}")

    playground_path = Path(args.playground_path).resolve()
    sys.path.insert(0, str(playground_path))
    os.chdir(playground_path)
    import jax
    import jax.numpy as jp
    from playground.open_duck_mini_v2.joystick import Joystick

    if jax.default_backend() != "cpu":
        raise SystemExit(f"refused non-CPU backend: {jax.default_backend()}")
    env = Joystick(task="flat_terrain_backlash")
    expected_obs = {"state": (101,), "privileged_state": (212,)}
    if env.observation_size != expected_obs:
        raise SystemExit(f"observation contract mismatch: {env.observation_size}")
    if env.action_size != 14 or env.dt != 0.02:
        raise SystemExit(f"action/timing mismatch: action={env.action_size}, dt={env.dt}")
    state = env.reset(jax.random.PRNGKey(0))
    state = env.step(state, jp.zeros(env.action_size))
    finite = bool(jp.all(jp.isfinite(state.obs["state"])))
    if not finite:
        raise SystemExit("non-finite observation after one zero-action step")

    result = {
        "status": "PASS_GROUND_UP_CONTROL_CPU_CONTRACT",
        "backend": jax.default_backend(),
        "devices": [str(device) for device in jax.devices()],
        "versions": versions,
        "observation_shape": list(state.obs["state"].shape),
        "privileged_observation_shape": list(state.obs["privileged_state"].shape),
        "action_size": env.action_size,
        "control_dt_s": env.dt,
        "finite_after_reset_and_step": finite,
        "reward_after_zero_step": float(state.reward),
        "done_after_zero_step": float(state.done),
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
