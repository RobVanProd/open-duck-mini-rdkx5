#!/usr/bin/env python3
"""CPU worker proving T227's actual 8x4 training reset lattice."""

from __future__ import annotations

import argparse
import functools
import json
import os
from pathlib import Path
import sys
from typing import Any

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["HIP_VISIBLE_DEVICES"] = ""
os.environ["ROCR_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"
os.environ["JAX_PLATFORM_NAME"] = "cpu"
os.environ["XLA_PYTHON_CLIENT_PREALLOCATE"] = "false"

import jax
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from run_t19_support_trainthrough_cpu_contract import (  # noqa: E402
    configure_environment,
)


POPULATION = 32
TORSO_BODY_ID = 2


def run(playground: Path, reference: Path, seed: int) -> dict[str, Any]:
    sys.path.insert(0, str(playground))
    from playground.common import t227_command_atom_bank as atom
    from playground.common import t66_endpoint_core_continuation as endpoint
    from playground.common import winner_v3_variable_configuration as winner_v3
    from playground.common.t19_support_trainthrough import (
        SupportPrefixWrapper,
    )
    from playground.open_duck_mini_v2 import joystick

    config = configure_environment(
        joystick,
        reference,
        enabled=True,
        deviation_scale=1.0,
    )
    config.winner_t31_action_margin_trainthrough = True
    config.winner_v127_constrained_cost = True
    config.winner_t215b_axis_complete_tilt_cost = True
    config.winner_t227_command_atom_bank = True
    base_env = joystick.Joystick(
        task="flat_terrain_backlash",
        config=config,
    )
    env = SupportPrefixWrapper(base_env)
    torso_body_id = int(
        base_env.mj_model.body(winner_v3.TORSO_BODY_NAME).id
    )
    randomizer = winner_v3.make_winner_v3_configuration_randomizer(
        torso_body_id=torso_body_id,
        deviation_scale=1.0,
    )
    randomizer = endpoint.make_endpoint_bank_randomizer(
        randomizer,
        torso_body_id=torso_body_id,
    )
    randomization_rng = jax.random.split(
        jax.random.PRNGKey(seed),
        POPULATION,
    )
    randomized_model, _ = randomizer(
        env.mjx_model,
        randomization_rng,
    )
    wrapped = atom.wrap_for_brax_training(
        env,
        episode_length=600,
        action_repeat=1,
        randomization_fn=functools.partial(
            randomizer,
            rng=randomization_rng,
        ),
    )
    reset_rng = jax.random.split(
        jax.random.PRNGKey(seed + 1),
        POPULATION,
    )
    state = jax.jit(wrapped.reset)(reset_rng)
    commands = np.asarray(jax.device_get(state.info["command"]))

    direct_rng = jax.random.split(
        jax.random.PRNGKey(seed + 2),
        POPULATION,
    )
    direct_commands = np.asarray(
        jax.device_get(
            jax.vmap(
                base_env.sample_command,
                axis_name=atom.AXIS_NAME,
            )(direct_rng)
        )
    )
    configuration_ids = np.asarray(
        atom.configuration_category_ids(POPULATION)
    )
    command_ids = np.asarray(atom.command_category_ids(POPULATION))
    expected_offsets = np.asarray(
        endpoint.ENDPOINT_OFFSETS_M[configuration_ids]
    )
    model_offsets = np.asarray(
        jax.device_get(
            randomized_model.body_ipos[:, TORSO_BODY_ID, :]
            - env.mjx_model.body_ipos[TORSO_BODY_ID, :]
        )
    )

    expected_atom_values = {
        1: np.float32(0.074),
        2: np.float32(0.077),
        3: np.float32(0.080),
    }
    pair_counts = {
        f"configuration_{config_id}:command_{command_id}": int(
            np.sum(
                (configuration_ids == config_id)
                & (command_ids == command_id)
            )
        )
        for command_id in range(atom.COMMAND_STRATA)
        for config_id in range(atom.CONFIGURATION_STRATA)
    }
    atom_exact = all(
        np.array_equal(
            commands[command_ids == command_id, 0],
            np.full(
                int(np.sum(command_ids == command_id)),
                value,
                dtype=np.float32,
            ),
        )
        and np.array_equal(
            direct_commands[command_ids == command_id, 0],
            np.full(
                int(np.sum(command_ids == command_id)),
                value,
                dtype=np.float32,
            ),
        )
        for command_id, value in expected_atom_values.items()
    )
    broad_reset = commands[command_ids == 0, 0]
    broad_direct = direct_commands[command_ids == 0, 0]
    non_broad = configuration_ids != 0
    checks = {
        "cpu_only": sorted(
            {device.platform for device in jax.devices()}
        )
        == ["cpu"],
        "population_exact": commands.shape == (POPULATION, 7),
        "observation_abi_unchanged": (
            np.asarray(jax.device_get(state.obs["state"])).shape
            == (POPULATION, 115)
        ),
        "all_32_cartesian_pairs_present_once": (
            len(pair_counts) == 32
            and set(pair_counts.values()) == {1}
        ),
        "configuration_index_matches_existing_modulo_eight": (
            np.array_equal(
                configuration_ids,
                np.arange(POPULATION, dtype=np.int32) % 8,
            )
        ),
        "seven_isolated_configuration_strata_exact": np.array_equal(
            model_offsets[non_broad],
            expected_offsets[non_broad],
        ),
        "exact_command_atoms_survive_t19_reset_and_resample": atom_exact,
        "broad_command_stratum_stays_within_frozen_support": (
            bool(np.all(broad_reset >= np.float32(0.074)))
            and bool(np.all(broad_reset < np.float32(0.080)))
            and bool(np.all(broad_direct >= np.float32(0.074)))
            and bool(np.all(broad_direct < np.float32(0.080)))
        ),
        "lateral_yaw_and_head_commands_remain_zero": (
            np.count_nonzero(commands[:, 1:]) == 0
            and np.count_nonzero(direct_commands[:, 1:]) == 0
        ),
        "reset_state_finite": all(
            np.isfinite(value).all()
            for value in (
                commands,
                np.asarray(jax.device_get(state.obs["state"])),
                model_offsets,
            )
        ),
    }
    checks = {name: bool(value) for name, value in checks.items()}
    return {
        "schema_version": "open_duck.t227_environment_contract.v1",
        "status": (
            "PASS_T227_COMMAND_ATOM_ENVIRONMENT_CONTRACT"
            if all(checks.values())
            else "HOLD_T227_COMMAND_ATOM_ENVIRONMENT_CONTRACT"
        ),
        "checks": checks,
        "failed_checks": sorted(
            name for name, passed in checks.items() if not passed
        ),
        "population": POPULATION,
        "pair_counts": pair_counts,
        "commands_x": commands[:, 0].tolist(),
        "direct_resample_commands_x": direct_commands[:, 0].tolist(),
        "configuration_ids": configuration_ids.tolist(),
        "command_ids": command_ids.tolist(),
        "model_offsets_m": model_offsets.tolist(),
        "expected_isolated_offsets_m": expected_offsets.tolist(),
        "simulator_prefix_transitions": POPULATION * 250,
        "optimizer_steps": 0,
        "formal_behavior_cells": 0,
        "hosted_compute_units": 0,
        "robot_or_rdk_access": 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--playground", type=Path, required=True)
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=227)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    value = run(
        args.playground.resolve(),
        args.reference.resolve(),
        args.seed,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"failed_checks={value['failed_checks']}")
    return 0 if not value["failed_checks"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
