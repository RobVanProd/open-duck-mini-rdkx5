#!/usr/bin/env python3
"""Read-only CPU audit of short-horizon reset feasibility."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
from typing import Any

import numpy as np

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")
os.environ.setdefault("JAX_PLATFORMS", "cpu")

from actuator_bridge_model import ActuatorBridgeModel, load_fit_json, params_from_fit
from probe_ground_up_oracle_shooting_mpc import LEG_INDICES, simulate_sequence


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def compact(score: float, key: tuple[float, ...], metrics: dict[str, float], bounded: np.ndarray) -> dict[str, Any]:
    return {
        "feasible": bool(metrics["viability_violation"] <= 0.0),
        "score": float(score),
        "rank_key": [float(value) for value in key],
        "metrics": {name: float(value) for name, value in metrics.items()},
        "bounded_action_sha256": hashlib.sha256(np.asarray(bounded, dtype="<f8").tobytes()).hexdigest(),
        "bounded_action": np.asarray(bounded, dtype=float).tolist(),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--fit", type=Path, required=True)
    parser.add_argument("--reference-table", type=Path, required=True)
    parser.add_argument("--source-probe", type=Path, required=True)
    parser.add_argument("--seeds", default="100,101")
    parser.add_argument("--command-x", type=float, default=0.074)
    parser.add_argument("--horizon-ticks", type=int, default=16)
    parser.add_argument("--bank-per-family", type=int, default=1024)
    parser.add_argument("--audit-rng-seed", type=int, default=20260714)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    import jax
    import mujoco

    if any(device.platform != "cpu" for device in jax.devices()):
        raise RuntimeError(f"non-CPU JAX device visible: {jax.devices()}")
    if args.horizon_ticks <= 0 or args.horizon_ticks % 2:
        raise ValueError("horizon must be positive and divisible by two")

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
    params = params_from_fit(load_fit_json(args.fit))
    source_probe = json.loads(args.source_probe.read_text())
    source_by_seed = {int(item["seed"]): item for item in source_probe["seeds"]}
    model = env.mj_model
    home = np.asarray(env._default_actuator, dtype=float)
    action_scale = float(env._config.action_scale)
    dt = float(env.dt)
    n_substeps = int(env.n_substeps)
    max_delta = measured_limits * dt / action_scale
    horizon = int(args.horizon_ticks)
    blocks = horizon // 2
    seeds = [int(value) for value in args.seeds.split(",")]

    seed_results = []
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
        future_reference = np.asarray([
            reference_cycle[(offset + 1) % len(reference_cycle)] for offset in range(horizon)
        ])

        def evaluate(sequence: np.ndarray) -> tuple[float, tuple[float, ...], dict[str, float], np.ndarray]:
            return simulate_sequence(
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
                objective_mode="viability_command_lexicographic",
                dt=dt,
                n_substeps=n_substeps,
            )

        source_actions = np.asarray(source_by_seed[seed]["trace"][:horizon], dtype=object)
        executed = np.asarray([item["action"] for item in source_actions], dtype=float)
        fixed_sequences = {
            "hold_reset_action": np.repeat(previous_action[None, :], horizon, axis=0),
            "home_action": np.zeros((horizon, 14), dtype=float),
            "exact_reference": future_reference.copy(),
            "executed_viability_prefix": executed,
        }
        fixed = {name: compact(*evaluate(sequence)) for name, sequence in fixed_sequences.items()}

        rng = np.random.default_rng(args.audit_rng_seed + seed)
        reference_blocks = future_reference[::2, LEG_INDICES]
        family_blocks = {
            "reference_gaussian_sigma_0p20": rng.normal(
                reference_blocks, 0.20, size=(args.bank_per_family, blocks, len(LEG_INDICES))
            ),
            "home_gaussian_sigma_0p20": rng.normal(
                0.0, 0.20, size=(args.bank_per_family, blocks, len(LEG_INDICES))
            ),
            "uniform_independent": rng.uniform(
                -1.0, 1.0, size=(args.bank_per_family, blocks, len(LEG_INDICES))
            ),
            "uniform_constant": np.repeat(
                rng.uniform(-1.0, 1.0, size=(args.bank_per_family, 1, len(LEG_INDICES))),
                blocks,
                axis=1,
            ),
        }
        families = {}
        for name, candidates in family_blocks.items():
            feasible_count = 0
            best = None
            best_key = None
            for candidate in candidates:
                full_blocks = np.zeros((blocks, 14), dtype=float)
                full_blocks[:, LEG_INDICES] = np.clip(candidate, -1.0, 1.0)
                sequence = np.repeat(full_blocks, 2, axis=0)
                result = evaluate(sequence)
                if result[2]["viability_violation"] <= 0.0:
                    feasible_count += 1
                if best_key is None or result[1] > best_key:
                    best = result
                    best_key = result[1]
            assert best is not None
            families[name] = {
                "candidates": int(args.bank_per_family),
                "feasible_count": int(feasible_count),
                "best": compact(*best),
            }

        fixed_feasible = [name for name, item in fixed.items() if item["feasible"]]
        bank_feasible = sum(item["feasible_count"] for item in families.values())
        seed_results.append({
            "seed": seed,
            "fixed": fixed,
            "fixed_feasible": fixed_feasible,
            "families": families,
            "bank_feasible_count": bank_feasible,
            "bank_candidates": args.bank_per_family * len(families),
            "conclusion": (
                "FEASIBLE_OUTSIDE_ORIGINAL_CEM_WINNER"
                if fixed_feasible or bank_feasible
                else "NO_FEASIBLE_SEQUENCE_FOUND_NOT_PROOF_OF_INFEASIBILITY"
            ),
        })

    payload = {
        "schema_version": "ground_up_reset_feasibility_audit.v1",
        "status": "READ_ONLY_DIAGNOSTIC_COMPLETE",
        "execution": {
            "jax_devices": [str(device) for device in jax.devices()],
            "local_cpu_only": True,
            "robot_access": False,
            "rdk_x5_access": False,
            "gpu_access": False,
        },
        "inputs": {
            "playground_root": str(root),
            "fit": str(args.fit),
            "fit_sha256": sha256(args.fit),
            "reference_table": str(args.reference_table),
            "reference_table_sha256": sha256(args.reference_table),
            "source_probe": str(args.source_probe),
            "source_probe_sha256": sha256(args.source_probe),
            "seeds": seeds,
            "command_x": args.command_x,
        },
        "contract": {
            "horizon_ticks": horizon,
            "action_block_ticks": 2,
            "bank_per_family": args.bank_per_family,
            "audit_rng_seed": args.audit_rng_seed,
            "viability": {"max_abs_roll_pitch_rad": 0.25, "min_height_m": 0.12, "max_abs_action_exclusive": 0.999, "no_fall": True},
            "interpretation": "A found feasible candidate disproves reset-level infeasibility. No found candidate does not prove infeasibility.",
        },
        "seeds": seed_results,
        "training_authorized": False,
        "collection_authorized": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "status": payload["status"],
        "seeds": [{
            "seed": item["seed"],
            "fixed_feasible": item["fixed_feasible"],
            "bank_feasible_count": item["bank_feasible_count"],
            "bank_candidates": item["bank_candidates"],
            "conclusion": item["conclusion"],
        } for item in seed_results],
    }, indent=2))


if __name__ == "__main__":
    main()
