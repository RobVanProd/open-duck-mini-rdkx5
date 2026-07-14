#!/usr/bin/env python3
"""Audit measured actuator-bridge semantics before any new training arm.

This is an offline contract check.  It does not instantiate MuJoCo, train a
policy, or access robot hardware.  It compares the JAX transition used by the
training environment with the NumPy transition used by offline evaluation and
records the provenance and ordering of the hard target limit and plant bridge.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import jax
import jax.numpy as jnp
import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))

from actuator_bridge_model import (  # noqa: E402
    ActuatorBridgeModel,
    JOINT_NAMES,
    JointActuatorParams,
)


DELAY_TICKS = np.asarray([3, 3, 3, 3, 3, 3, 2, 3, 3, 3, 2, 3, 2, 3], dtype=int)
TAU_S = np.asarray(
    [.015, .015, .005, .010, .010, .120, .120, .120, .120, .020, .035, .010, .030, .005],
    dtype=float,
)
VELOCITY_LIMIT_RAD_S = np.asarray(
    [5.24, 5.24, 1.50, 1.50, 1.75, 5.24, 5.24, 5.24, 5.24, 5.24, 5.24, 1.25, 1.00, 1.25],
    dtype=float,
)
PITCH_INDICES = np.asarray([2, 3, 4, 11, 12, 13], dtype=int)
NON_PITCH_INDICES = np.asarray([i for i in range(14) if i not in set(PITCH_INDICES)], dtype=int)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def ordered(text: str, fragments: list[str]) -> bool:
    cursor = -1
    for fragment in fragments:
        cursor = text.find(fragment, cursor + 1)
        if cursor < 0:
            return False
    return True


def load_combined_fit(path: Path) -> dict[str, dict[str, float]]:
    with path.open() as stream:
        payload = json.load(stream)
    return {
        name: values["combined"]
        for name, values in payload["primary"]["joints"].items()
    }


def jax_bridge_rollout(
    targets: np.ndarray,
    initial: np.ndarray,
    dt_s: float,
) -> np.ndarray:
    """Exact functional equivalent of Joystick._apply_actuator_bridge."""
    delay = jnp.asarray(DELAY_TICKS, dtype=jnp.int32)
    tau = jnp.asarray(TAU_S)
    velocity = jnp.asarray(VELOCITY_LIMIT_RAD_S)
    actuator_count = initial.size
    history = jnp.tile(jnp.asarray(initial), int(DELAY_TICKS.max()) + 1)
    applied = jnp.asarray(initial)
    output = []
    for sent in jnp.asarray(targets):
        history = jnp.roll(history, actuator_count).at[:actuator_count].set(sent)
        history_matrix = history.reshape((-1, actuator_count))
        delayed = history_matrix[delay, jnp.arange(actuator_count)]
        alpha = 1.0 - jnp.exp(-dt_s / jnp.maximum(tau, 1.0e-4))
        lagged = applied + alpha * (delayed - applied)
        max_step = velocity * dt_s
        applied = jnp.clip(lagged, applied - max_step, applied + max_step)
        output.append(applied)
    return np.asarray(jax.device_get(jnp.stack(output)), dtype=float)


def numpy_bridge_rollout(
    targets: np.ndarray,
    initial: np.ndarray,
    dt_s: float,
) -> np.ndarray:
    params = [
        JointActuatorParams(int(delay), float(tau), float(velocity))
        for delay, tau, velocity in zip(DELAY_TICKS, TAU_S, VELOCITY_LIMIT_RAD_S)
    ]
    model = ActuatorBridgeModel(params, initial_target=initial)
    return np.vstack([model.step(target, dt_s) for target in targets])


def make_sequences(initial: np.ndarray, steps: int, dt_s: float) -> dict[str, np.ndarray]:
    tick = np.arange(steps, dtype=float)[:, None]
    joint = np.arange(initial.size, dtype=float)[None, :]
    step = np.tile(initial, (steps, 1))
    step[8:] += np.where((np.arange(initial.size) % 2) == 0, .22, -.17)
    alternating = initial + .18 * np.where(((tick // 5) + joint) % 2 == 0, 1.0, -1.0)
    chirp = initial + .16 * np.sin((.7 + joint * .09) * tick * dt_s * (1.0 + tick / steps))
    rng = np.random.default_rng(20260714)
    bounded_random = np.empty((steps, initial.size), dtype=float)
    bounded_random[0] = initial
    for index in range(1, steps):
        delta = rng.uniform(-VELOCITY_LIMIT_RAD_S, VELOCITY_LIMIT_RAD_S) * dt_s
        bounded_random[index] = bounded_random[index - 1] + delta
    return {
        "home_hold": np.tile(initial, (steps, 1)),
        "step": step,
        "alternating": alternating,
        "chirp": chirp,
        "bounded_random": bounded_random,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--assembled-joystick",
        type=Path,
        default=Path("/tmp/ground_up_hard_vector_contract_321019/playground/open_duck_mini_v2/joystick.py"),
    )
    parser.add_argument(
        "--bridge-joystick",
        type=Path,
        default=Path("/home/lsd/robots/Open_Duck_Playground/playground/open_duck_mini_v2/joystick.py"),
    )
    parser.add_argument("--steps", type=int, default=256)
    parser.add_argument("--dt", type=float, default=.02)
    args = parser.parse_args()

    paths = {
        "hard_vector_patch": REPO / "patches/ground_up_hard_vector_command_support.patch",
        "assembled_ground_up_joystick": args.assembled_joystick,
        "bridge_training_joystick": args.bridge_joystick,
        "offline_bridge_model": REPO / "tools/actuator_bridge_model.py",
        "closed_loop_evaluator": REPO / "tools/closed_loop_sim_eval.py",
        "pitch_fit": REPO / "outputs/analysis/fixed_target_p30_actuator_fit_20260712.json",
        "all_joint_fit": REPO / "outputs/analysis/fixed_target_p30_all_joint_actuator_fit_20260712.json",
        "prior_preregistration": REPO / "outputs/analysis/HARDWARE_VECTOR_BRIDGE_CONSTRAINED_PPO_PREREGISTRATION_20260712.md",
    }
    missing = [str(path) for path in paths.values() if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"missing audit inputs: {missing}")

    initial = np.asarray(
        [-.02, .03, -.24, .47, -.23, 0., 0., 0., 0., .02, -.03, -.24, .47, -.23],
        dtype=float,
    )
    parity: dict[str, Any] = {}
    all_finite = True
    global_max_error = 0.0
    for name, targets in make_sequences(initial, args.steps, args.dt).items():
        expected = numpy_bridge_rollout(targets, initial, args.dt)
        actual = jax_bridge_rollout(targets, initial, args.dt)
        error = np.abs(expected - actual)
        finite = bool(np.isfinite(actual).all() and np.isfinite(expected).all())
        maximum = float(error.max())
        parity[name] = {
            "steps": int(args.steps),
            "finite": finite,
            "max_abs_error_rad": maximum,
            "mean_abs_error_rad": float(error.mean()),
        }
        all_finite &= finite
        global_max_error = max(global_max_error, maximum)

    pitch_fit = load_combined_fit(paths["pitch_fit"])
    all_fit = load_combined_fit(paths["all_joint_fit"])
    fit_delay = np.asarray([all_fit[name]["delay_ticks"] for name in JOINT_NAMES])
    fit_tau = np.asarray([all_fit[name]["tau_s"] for name in JOINT_NAMES])
    pitch_velocity = np.asarray([pitch_fit[JOINT_NAMES[i]]["velocity_limit_rad_s"] for i in PITCH_INDICES])

    assembled_text = paths["assembled_ground_up_joystick"].read_text()
    bridge_text = paths["bridge_training_joystick"].read_text()
    evaluator_text = paths["closed_loop_evaluator"].read_text()
    prereg_text = paths["prior_preregistration"].read_text()

    source_checks = {
        "ground_up_hard_limit_precedes_physics": ordered(
            assembled_text,
            ["velocity_limits = jp.where(", "motor_targets = jp.clip(", "data = mjx_env.step("],
        ),
        "ground_up_realized_action_precedes_reward": ordered(
            assembled_text,
            ["applied_action = (", "rewards = self._get_reward(", "state.info[\"last_act\"] = applied_action"],
        ),
        "ground_up_next_observation_follows_realized_history": ordered(
            assembled_text,
            ["state.info[\"last_act\"] = applied_action", "obs = self._get_obs(data, state.info, contact)"],
        ),
        "bridge_receives_sent_target_and_physics_receives_applied_target": ordered(
            bridge_text,
            ["sent_motor_targets = motor_targets", "self._apply_actuator_bridge(", "mjx_env.step(\n            self.mjx_model, state.data, applied_motor_targets"],
        ),
        "bridge_preserves_sent_target_for_observation_history": ordered(
            bridge_text,
            ["mjx_env.step(\n            self.mjx_model, state.data, applied_motor_targets", "state.info[\"motor_targets\"] = sent_motor_targets"],
        ),
        "offline_evaluator_bridges_before_physics": ordered(
            evaluator_text,
            ["else bridge.step(sent_np, float(env.dt))", "state = apply_motor_target_runner(", "jp.asarray(applied_np)"],
        ),
        "offline_evaluator_preserves_sent_target_history": "state.info[\"motor_targets\"] = sent_target" in evaluator_text,
        "prior_penalty_route_explicitly_closed": "status: `REJECT_CLOSE_PENALTY_PPO`" in (
            REPO / "outputs/analysis/HARDWARE_VECTOR_BRIDGE_CONSTRAINED_PPO_RESULT_20260712.md"
        ).read_text(),
        "old_prereg_identifies_non_pitch_velocity_as_neutral": "non-pitch velocity limits remain neutral at `5.24 rad/s`" in prereg_text,
    }

    provenance_checks = {
        "delay_matches_all_joint_combined_fit": bool(np.array_equal(DELAY_TICKS, fit_delay)),
        "tau_matches_all_joint_combined_fit": bool(np.allclose(TAU_S, fit_tau, rtol=0, atol=1e-12)),
        "pitch_velocity_matches_pitch_combined_fit": bool(
            np.allclose(VELOCITY_LIMIT_RAD_S[PITCH_INDICES], pitch_velocity, rtol=0, atol=1e-12)
        ),
        "non_pitch_velocity_is_neutral_5p24": bool(
            np.allclose(VELOCITY_LIMIT_RAD_S[NON_PITCH_INDICES], 5.24, rtol=0, atol=1e-12)
        ),
    }

    threshold = 1e-6
    passed = bool(
        all_finite
        and global_max_error <= threshold
        and all(source_checks.values())
        and all(provenance_checks.values())
    )
    result = {
        "schema_version": 1,
        "status": "PASS" if passed else "FAIL",
        "scope": "read_only_measured_bridge_integration_audit",
        "authority": {
            "training_authorized": False,
            "robot_or_rdk_authorized": False,
            "gpu_authorized": False,
        },
        "runtime": {
            "jax_backend": jax.default_backend(),
            "jax_version": jax.__version__,
            "dt_s": args.dt,
            "steps_per_sequence": args.steps,
        },
        "frozen_vectors": {
            "joint_order": JOINT_NAMES,
            "delay_ticks": DELAY_TICKS.tolist(),
            "tau_s": TAU_S.tolist(),
            "velocity_limit_rad_s": VELOCITY_LIMIT_RAD_S.tolist(),
            "pitch_indices": PITCH_INDICES.tolist(),
            "non_pitch_velocity_semantics": "neutral_5.24_not_measured_fit",
        },
        "parity": {
            "threshold_rad": threshold,
            "global_max_abs_error_rad": global_max_error,
            "all_finite": all_finite,
            "sequences": parity,
        },
        "provenance_checks": provenance_checks,
        "source_order_checks": source_checks,
        "inputs": {
            name: {"path": str(path), "sha256": sha256(path)} for name, path in paths.items()
        },
        "conclusion": (
            "The exact causal next arm is technically composable as hard-bounded sent target -> "
            "measured delay/tau plus pitch-limit bridge -> physics, with sent target retained in "
            "history and actual joint state returned in observations. This audit does not authorize "
            "training. The previously rejected penalty stack must not be reintroduced."
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "status": result["status"],
        "output": str(args.output),
        "global_max_abs_error_rad": global_max_error,
        "source_checks": source_checks,
        "provenance_checks": provenance_checks,
    }, indent=2, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
