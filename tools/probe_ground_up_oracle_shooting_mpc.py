#!/usr/bin/env python3
"""CPU-only receding-horizon shooting probe for a ground-up oracle teacher."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import os
from pathlib import Path
import sys
from typing import Any

import numpy as np

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")
os.environ.setdefault("JAX_PLATFORMS", "cpu")

from actuator_bridge_model import ActuatorBridgeModel, load_fit_json, params_from_fit


LEG_INDICES = np.asarray([0, 1, 2, 3, 4, 9, 10, 11, 12, 13], dtype=int)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def rpy_from_wxyz(quat: np.ndarray) -> tuple[float, float, float]:
    w, x, y, z = [float(value) for value in quat]
    roll = math.atan2(2 * (w * x + y * z), 1 - 2 * (x * x + y * y))
    pitch = math.asin(np.clip(2 * (w * y - z * x), -1.0, 1.0))
    yaw = math.atan2(2 * (w * z + x * y), 1 - 2 * (y * y + z * z))
    return roll, pitch, yaw


def clone_bridge(bridge: ActuatorBridgeModel) -> ActuatorBridgeModel:
    output = ActuatorBridgeModel(bridge.params, initial_target=bridge.value)
    output._queues = [queue.copy() for queue in bridge._queues]  # noqa: SLF001
    return output


def contacts(data, foot_geom_ids: np.ndarray, floor_geom_id: int) -> np.ndarray:
    result = np.zeros(2, dtype=bool)
    for index in range(int(data.ncon)):
        geom1 = int(data.contact[index].geom1)
        geom2 = int(data.contact[index].geom2)
        for foot, geom in enumerate(foot_geom_ids):
            if (geom1 == int(geom) and geom2 == floor_geom_id) or (
                geom2 == int(geom) and geom1 == floor_geom_id
            ):
                result[foot] = True
    return result


def rate_bound(sequence: np.ndarray, previous: np.ndarray, max_delta: np.ndarray) -> np.ndarray:
    bounded = np.empty_like(sequence)
    prior = previous.copy()
    for index, action in enumerate(sequence):
        bounded[index] = np.clip(action, prior - max_delta, prior + max_delta)
        bounded[index] = np.clip(bounded[index], -1.0, 1.0)
        prior = bounded[index]
    return bounded


def simulate_sequence(
    *,
    mujoco,
    model,
    source_data,
    source_bridge,
    source_sent: np.ndarray,
    source_action: np.ndarray,
    sequence: np.ndarray,
    reference: np.ndarray,
    home: np.ndarray,
    action_scale: float,
    env_rate_limit: float,
    measured_max_delta: np.ndarray,
    command_x: float,
    objective_mode: str,
    dt: float,
    n_substeps: int,
) -> tuple[float, tuple[float, ...], dict[str, float], np.ndarray]:
    data = mujoco.MjData(model)
    mujoco.mj_copyData(data, model, source_data)
    bridge = clone_bridge(source_bridge)
    sent = source_sent.copy()
    bounded = rate_bound(sequence, source_action, measured_max_delta)
    start_x = float(data.qpos[0])
    start_y = float(data.qpos[1])
    _start_roll, _start_pitch, start_yaw = rpy_from_wxyz(np.asarray(data.qpos[3:7]))
    body_forward_progress = 0.0
    body_lateral_progress = 0.0
    min_height = float(data.qpos[2])
    max_abs_tilt = 0.0
    local_vx_values = []
    local_vy_values = []
    fell = False
    for action in bounded:
        target = home + action * action_scale
        sent = np.clip(target, sent - env_rate_limit * dt, sent + env_rate_limit * dt)
        applied = bridge.step(sent, dt)
        data.ctrl[:] = applied
        for _ in range(n_substeps):
            mujoco.mj_step(model, data)
        roll, pitch, current_yaw = rpy_from_wxyz(np.asarray(data.qpos[3:7]))
        local_vx = math.cos(current_yaw) * float(data.qvel[0]) + math.sin(current_yaw) * float(data.qvel[1])
        local_vy = -math.sin(current_yaw) * float(data.qvel[0]) + math.cos(current_yaw) * float(data.qvel[1])
        local_vx_values.append(local_vx)
        local_vy_values.append(local_vy)
        body_forward_progress += local_vx * dt
        body_lateral_progress += local_vy * dt
        min_height = min(min_height, float(data.qpos[2]))
        max_abs_tilt = max(max_abs_tilt, abs(roll), abs(pitch))
        if not np.all(np.isfinite(data.qpos)) or min_height < 0.08 or max(abs(roll), abs(pitch)) > 0.8:
            fell = True
            break
    roll, pitch, yaw = rpy_from_wxyz(np.asarray(data.qpos[3:7]))
    yaw_error = math.atan2(math.sin(yaw - start_yaw), math.cos(yaw - start_yaw))
    world_dx = float(data.qpos[0]) - start_x
    world_dy = float(data.qpos[1]) - start_y
    final_vx = math.cos(yaw) * float(data.qvel[0]) + math.sin(yaw) * float(data.qvel[1])
    height_shortfall = max(0.0, 0.12 - min_height)
    residual_mse = float(np.mean(np.square(bounded - reference[: len(bounded)])))
    delta_mse = float(np.mean(np.square(np.diff(
        np.concatenate([source_action[None, :], bounded], axis=0), axis=0
    ))))
    velocity_tracking_rmse = float(np.sqrt(np.mean(np.square(
        np.asarray(local_vx_values, dtype=float) - command_x
    ))))
    lateral_velocity_rmse = float(np.sqrt(np.mean(np.square(local_vy_values))))
    max_abs_action = float(np.max(np.abs(bounded)))
    viability_violation = max(
        float(fell),
        max(0.0, max_abs_tilt / 0.25 - 1.0),
        max(0.0, 0.12 / max(min_height, 1.0e-9) - 1.0),
        max(0.0, max_abs_action / 0.999 - 1.0),
    )
    score = (
        100.0 * body_forward_progress
        + 2.0 * final_vx
        - 25.0 * abs(body_lateral_progress)
        - 12.0 * (roll * roll + pitch * pitch)
        - 3.0 * yaw_error * yaw_error
        - 150.0 * height_shortfall * height_shortfall
        - 0.25 * residual_mse
        - 0.10 * delta_mse
        - 100.0 * float(fell)
    )
    if objective_mode == "viability_command_lexicographic":
        rank_key = (
            float(viability_violation <= 0.0),
            -viability_violation,
            -velocity_tracking_rmse,
            -lateral_velocity_rmse,
            -abs(yaw_error),
            -residual_mse,
            -delta_mse,
        )
        score = -velocity_tracking_rmse if viability_violation <= 0.0 else -1.0 - viability_violation
    else:
        rank_key = (score,)
    return score, rank_key, {
        "dx": body_forward_progress,
        "dy": body_lateral_progress,
        "world_dx": world_dx,
        "world_dy": world_dy,
        "final_vx": final_vx,
        "roll": roll,
        "pitch": pitch,
        "yaw": yaw_error,
        "world_yaw": yaw,
        "min_height": min_height,
        "max_abs_tilt": max_abs_tilt,
        "max_abs_action": max_abs_action,
        "fell": float(fell),
        "viability_violation": viability_violation,
        "velocity_tracking_rmse": velocity_tracking_rmse,
        "lateral_velocity_rmse": lateral_velocity_rmse,
        "reference_residual_mse": residual_mse,
        "action_delta_mse": delta_mse,
    }, bounded


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--fit", type=Path, required=True)
    parser.add_argument("--reference-table", type=Path, required=True)
    parser.add_argument("--seeds", default="100,101")
    parser.add_argument("--command-x", type=float, default=0.074)
    parser.add_argument("--duration-s", type=float, default=1.08)
    parser.add_argument("--horizon-ticks", type=int, default=8)
    parser.add_argument(
        "--objective-mode",
        choices=("unbounded_progress", "viability_command_lexicographic"),
        default="unbounded_progress",
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    import jax
    import mujoco

    if any(device.platform != "cpu" for device in jax.devices()):
        raise RuntimeError(f"non-CPU JAX device visible: {jax.devices()}")
    root = args.playground_root.resolve()
    sys.path.insert(0, str(root))
    original_cwd = Path.cwd()
    os.chdir(root)
    try:
        from playground.open_duck_mini_v2 import joystick

        env = joystick.Joystick(
            task="flat_terrain_backlash",
            config=joystick.default_config(),
            config_overrides={
                "push_config.enable": False,
                "lin_vel_x": [args.command_x, args.command_x],
                "lin_vel_y": [0.0, 0.0],
                "ang_vel_yaw": [0.0, 0.0],
                "neck_pitch_range": [0.0, 0.0],
                "head_pitch_range": [0.0, 0.0],
                "head_yaw_range": [0.0, 0.0],
                "head_roll_range": [0.0, 0.0],
                "noise_config.level": 0.0,
                "noise_config.action_min_delay": 0,
                "noise_config.action_max_delay": 1,
            },
        )
    finally:
        os.chdir(original_cwd)

    table = np.load(args.reference_table)
    command_rows = np.asarray(table["commands"])
    row = int(np.argmin(np.sum(np.abs(command_rows - [args.command_x, 0.0, 0.0]), axis=1)))
    reference_cycle = np.asarray(table["actions"][row], dtype=float)
    measured_limits = np.asarray(table["velocity_limits_rad_s"], dtype=float)
    fit = load_fit_json(args.fit)
    params = params_from_fit(fit)
    model = env.mj_model
    home = np.asarray(env._default_actuator, dtype=float)
    action_scale = float(env._config.action_scale)
    dt = float(env.dt)
    n_substeps = int(env.n_substeps)
    max_delta = measured_limits * dt / action_scale
    block = 2
    horizon = int(args.horizon_ticks)
    if horizon <= 0 or horizon % block:
        raise ValueError("horizon ticks must be positive and divisible by action block 2")
    blocks = horizon // block
    population = 64
    elites = 8
    iterations = 4
    sim_steps = int(round(args.duration_s / dt))
    seeds = [int(value) for value in args.seeds.split(",")]
    foot_geom_ids = np.asarray(env._feet_geom_id, dtype=int)
    floor_geom_id = int(env._floor_geom_id)

    seed_results: list[dict[str, Any]] = []
    for seed in seeds:
        reset = env.reset(jax.random.PRNGKey(seed))
        data = mujoco.MjData(model)
        data.qpos[:] = np.asarray(jax.device_get(reset.data.qpos), dtype=float)
        data.qvel[:] = np.asarray(jax.device_get(reset.data.qvel), dtype=float)
        data.ctrl[:] = home
        mujoco.mj_forward(model, data)
        sent = np.asarray(jax.device_get(reset.info["motor_targets"]), dtype=float)
        bridge = ActuatorBridgeModel(params, initial_target=sent)
        previous_action = np.clip((sent - home) / action_scale, -1.0, 1.0)
        initial_x = float(data.qpos[0])
        initial_y = float(data.qpos[1])
        body_forward_progress = 0.0
        body_lateral_progress = 0.0
        initial_contacts = contacts(data, foot_geom_ids, floor_geom_id)
        prior_contacts = initial_contacts.copy()
        contact_transitions = np.zeros(2, dtype=int)
        actions = []
        trace = []
        fell = False
        rng = np.random.default_rng(seed)

        for tick in range(sim_steps):
            future_reference = np.asarray([
                reference_cycle[(tick + offset + 1) % len(reference_cycle)]
                for offset in range(horizon)
            ])
            mean = future_reference[::block][:, LEG_INDICES].copy()
            std = np.full_like(mean, 0.20)
            best_score = -math.inf
            best_key = None
            best_sequence = None
            best_metrics = None
            for _iteration in range(iterations):
                samples = rng.normal(mean, std, size=(population, blocks, len(LEG_INDICES)))
                samples = np.clip(samples, -1.0, 1.0)
                scores = np.empty(population, dtype=float)
                rank_keys = []
                bounded_sequences = []
                metrics = []
                for candidate in range(population):
                    full_blocks = np.zeros((blocks, 14), dtype=float)
                    full_blocks[:, LEG_INDICES] = samples[candidate]
                    sequence = np.repeat(full_blocks, block, axis=0)
                    score, rank_key, item, bounded = simulate_sequence(
                        mujoco=mujoco,
                        model=model,
                        source_data=data,
                        source_bridge=bridge,
                        source_sent=sent,
                        source_action=previous_action,
                        sequence=sequence,
                        reference=future_reference,
                        home=home,
                        action_scale=action_scale,
                        env_rate_limit=float(env._config.max_motor_velocity),
                        measured_max_delta=max_delta,
                        command_x=args.command_x,
                        objective_mode=args.objective_mode,
                        dt=dt,
                        n_substeps=n_substeps,
                    )
                    scores[candidate] = score
                    rank_keys.append(rank_key)
                    bounded_sequences.append(bounded)
                    metrics.append(item)
                order = sorted(range(population), key=lambda index: rank_keys[index])[-elites:]
                elite = samples[order]
                mean = np.mean(elite, axis=0)
                std = np.maximum(np.std(elite, axis=0), 0.03)
                winner = max(range(population), key=lambda index: rank_keys[index])
                if best_key is None or rank_keys[winner] > best_key:
                    best_score = float(scores[winner])
                    best_key = rank_keys[winner]
                    best_sequence = bounded_sequences[winner]
                    best_metrics = metrics[winner]

            assert best_sequence is not None and best_metrics is not None
            action = best_sequence[0]
            target = home + action * action_scale
            sent = np.clip(
                target,
                sent - float(env._config.max_motor_velocity) * dt,
                sent + float(env._config.max_motor_velocity) * dt,
            )
            applied = bridge.step(sent, dt)
            data.ctrl[:] = applied
            for _ in range(n_substeps):
                mujoco.mj_step(model, data)
            current_contacts = contacts(data, foot_geom_ids, floor_geom_id)
            contact_transitions += current_contacts != prior_contacts
            prior_contacts = current_contacts
            roll, pitch, yaw = rpy_from_wxyz(np.asarray(data.qpos[3:7]))
            local_vx = math.cos(yaw) * float(data.qvel[0]) + math.sin(yaw) * float(data.qvel[1])
            local_vy = -math.sin(yaw) * float(data.qvel[0]) + math.cos(yaw) * float(data.qvel[1])
            body_forward_progress += local_vx * dt
            body_lateral_progress += local_vy * dt
            fell = (
                not np.all(np.isfinite(data.qpos))
                or float(data.qpos[2]) < 0.08
                or max(abs(roll), abs(pitch)) > 0.8
            )
            rate = np.abs(action - previous_action) * action_scale / dt
            actions.append(action.copy())
            trace.append({
                "tick": tick,
                "x": float(data.qpos[0]),
                "y": float(data.qpos[1]),
                "height": float(data.qpos[2]),
                "roll": roll,
                "pitch": pitch,
                "yaw": yaw,
                "world_vx": float(data.qvel[0]),
                "body_local_vx": local_vx,
                "body_forward_progress": body_forward_progress,
                "contacts": current_contacts.astype(int).tolist(),
                "action": action.tolist(),
                "action_rate_rad_s": rate.tolist(),
                "shooting_score": best_score,
                "shooting_rank_key": list(best_key) if best_key is not None else None,
                "shooting_terminal": best_metrics,
            })
            previous_action = action.copy()
            if fell:
                break

        action_array = np.asarray(actions)
        elapsed = len(actions) * dt
        world_dx = float(data.qpos[0]) - initial_x
        world_dy = float(data.qpos[1]) - initial_y
        max_rate = (
            np.max(np.asarray([item["action_rate_rad_s"] for item in trace]), axis=0)
            if trace else np.zeros(14)
        )
        excess = np.maximum(max_rate - measured_limits, 0.0)
        seed_results.append({
            "seed": seed,
            "status": "PASS_SOURCE_PROBE" if (
                not fell
                and len(actions) == sim_steps
                and body_forward_progress > 0.0
                and body_forward_progress / elapsed > 0.0
                and body_forward_progress / elapsed >= 0.25 * args.command_x
                and body_forward_progress / elapsed <= 1.35 * args.command_x
                and np.all(contact_transitions > 0)
                and max((abs(item["roll"]) for item in trace), default=0.0) <= 0.25
                and max((abs(item["pitch"]) for item in trace), default=0.0) <= 0.25
                and min((item["height"] for item in trace), default=1.0) >= 0.12
                and (not action_array.size or float(np.max(np.abs(action_array))) < 0.999)
                and float(np.max(excess)) <= 1.0e-6
            ) else "HOLD_SOURCE_PROBE",
            "ticks": len(actions),
            "duration_complete": len(actions) == sim_steps and not fell,
            "fell": bool(fell),
            "progress_x_m": body_forward_progress,
            "progress_y_m": body_lateral_progress,
            "world_progress_x_m": world_dx,
            "world_progress_y_m": world_dy,
            "mean_velocity_x_m_s": body_forward_progress / elapsed if elapsed else None,
            "max_abs_roll_rad": max((abs(item["roll"]) for item in trace), default=None),
            "max_abs_pitch_rad": max((abs(item["pitch"]) for item in trace), default=None),
            "min_height_m": min((item["height"] for item in trace), default=None),
            "contact_transitions": contact_transitions.tolist(),
            "max_abs_action": float(np.max(np.abs(action_array))) if action_array.size else None,
            "max_rate_by_joint_rad_s": max_rate.tolist(),
            "max_rate_excess_rad_s": float(np.max(excess)),
            "trace": trace,
        })

    passes = sum(item["status"] == "PASS_SOURCE_PROBE" for item in seed_results)
    payload = {
        "schema_version": "ground_up_oracle_shooting_mpc_probe.v1",
        "status": "PASS_ORACLE_SHOOTING_MPC_SOURCE_PROBE" if passes == len(seeds) else "HOLD_ORACLE_SHOOTING_MPC_SOURCE_PROBE",
        "execution": {
            "jax_devices": [str(device) for device in jax.devices()],
            "robot_access": False,
            "local_gpu_access": False,
        },
        "inputs": {
            "playground_root": str(root),
            "fit": str(args.fit),
            "fit_sha256": sha256(args.fit),
            "reference_table": str(args.reference_table),
            "reference_table_sha256": sha256(args.reference_table),
            "command_x": args.command_x,
            "duration_s": args.duration_s,
            "seeds": seeds,
        },
        "contract": {
            "horizon_ticks": horizon,
            "action_block_ticks": block,
            "population": population,
            "elites": elites,
            "iterations": iterations,
            "initial_std": 0.20,
            "minimum_std": 0.03,
            "objective_mode": args.objective_mode,
            "objective": (
                "lexicographic(feasible(max_abs_roll_pitch<=0.25,min_height>=0.12,max_abs_action<0.999,no_fall),-viability_violation,-body_vx_tracking_RMSE,-body_vy_RMSE,-abs(relative_yaw),-reference_residual_MSE,-action_delta_MSE)"
                if args.objective_mode == "viability_command_lexicographic"
                else "100*body_forward_progress + 2*final_body_vx - 25*abs(body_lateral_progress) - 12*(roll^2+pitch^2) - 3*body_yaw_delta^2 - 150*height_shortfall^2 - 0.25*reference_residual_MSE - 0.10*action_delta_MSE - 100*fall"
            ),
            "source_gate": {
                "mean_body_vx_ratio": [0.25, 1.35],
                "max_abs_roll_rad": 0.25,
                "max_abs_pitch_rad": 0.25,
                "min_height_m": 0.12,
                "max_abs_action_exclusive": 0.999,
                "max_rate_excess_rad_s": 0.0,
                "bilateral_contact_transitions": True,
            },
        },
        "passes": passes,
        "required_passes": len(seeds),
        "seeds": seed_results,
        "training_authorized": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "status": payload["status"],
        "passes": passes,
        "required_passes": len(seeds),
        "seeds": [{
            "seed": item["seed"],
            "status": item["status"],
            "dx": item["progress_x_m"],
            "vx": item["mean_velocity_x_m_s"],
            "fell": item["fell"],
        } for item in seed_results],
    }, indent=2))


if __name__ == "__main__":
    main()
