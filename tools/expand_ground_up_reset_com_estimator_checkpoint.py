#!/usr/bin/env python3
"""Expand the protected T2 checkpoint for the reset-latched COM coordinate."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
from typing import Any

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")
os.environ.setdefault("JAX_PLATFORMS", "cpu")

import jax
import jax.numpy as jnp
import numpy as np
from brax.training import types
from brax.training.acme import running_statistics
from orbax import checkpoint as ocp


INSERT_INDEX = 101
SOURCE_STATE_SIZE = 115
SOURCE_PRIVILEGED_SIZE = 226
EXPANDED_STATE_SIZE = 116
EXPANDED_PRIVILEGED_SIZE = 227
ACTION_SIZE = 14
EXPECTED_COUNT_HI = 0
EXPECTED_COUNT_LO = 8_048_640
EXPECTED_STD_EPS = 0.0
EXPECTED_SOURCE_DIRECTORY_SHA256 = (
    "b37a86f1b736d0d1276e60fb69d1f473683c593dec26f9592b0b794858dbb44a"
)
EQUALITY_TOLERANCE = 1e-7


def sha256_directory(path: Path) -> str:
    digest = hashlib.sha256()
    for child in sorted(item for item in path.rglob("*") if item.is_file()):
        digest.update(str(child.relative_to(path)).encode())
        digest.update(b"\0")
        with child.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
    return digest.hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def insert(array: Any, value: float | np.ndarray, axis: int = 0) -> jax.Array:
    source = jnp.asarray(array)
    shape = list(source.shape)
    shape[axis] = 1
    inserted = jnp.asarray(value, dtype=source.dtype)
    inserted = jnp.broadcast_to(inserted, shape)
    return jnp.concatenate(
        [
            jnp.take(source, jnp.arange(INSERT_INDEX), axis=axis),
            inserted,
            jnp.take(source, jnp.arange(INSERT_INDEX, source.shape[axis]), axis=axis),
        ],
        axis=axis,
    )


def remove(array: Any, axis: int = 0) -> jax.Array:
    source = jnp.asarray(array)
    return jnp.concatenate(
        [
            jnp.take(source, jnp.arange(INSERT_INDEX), axis=axis),
            jnp.take(
                source, jnp.arange(INSERT_INDEX + 1, source.shape[axis]), axis=axis
            ),
        ],
        axis=axis,
    )


def expand_checkpoint(source: list[Any]) -> list[Any]:
    expanded = copy.deepcopy(source)
    normalizer = expanded[0]
    count_float = float(EXPECTED_COUNT_LO)
    for stream in ("state", "privileged_state"):
        normalizer["mean"][stream] = insert(normalizer["mean"][stream], 0.0)
        normalizer["std"][stream] = insert(normalizer["std"][stream], 1.0)
        normalizer["summed_variance"][stream] = insert(
            normalizer["summed_variance"][stream], count_float
        )
    actor_kernel = expanded[1]["params"]["residual_trunk"]["hidden_0"]["kernel"]
    expanded[1]["params"]["residual_trunk"]["hidden_0"]["kernel"] = insert(
        actor_kernel, np.zeros((1, actor_kernel.shape[1]), dtype=np.float32)
    )
    critic_kernel = expanded[2]["params"]["hidden_0"]["kernel"]
    expanded[2]["params"]["hidden_0"]["kernel"] = insert(
        critic_kernel, np.zeros((1, critic_kernel.shape[1]), dtype=np.float32)
    )
    return expanded


def collapse_checkpoint(expanded: list[Any]) -> list[Any]:
    collapsed = copy.deepcopy(expanded)
    for stream in ("state", "privileged_state"):
        for family in ("mean", "std", "summed_variance"):
            collapsed[0][family][stream] = remove(collapsed[0][family][stream])
    collapsed[1]["params"]["residual_trunk"]["hidden_0"]["kernel"] = remove(
        collapsed[1]["params"]["residual_trunk"]["hidden_0"]["kernel"]
    )
    collapsed[2]["params"]["hidden_0"]["kernel"] = remove(
        collapsed[2]["params"]["hidden_0"]["kernel"]
    )
    return collapsed


def normalizer_state(value: dict[str, Any]) -> running_statistics.RunningStatisticsState:
    return running_statistics.RunningStatisticsState(
        mean=value["mean"],
        std=value["std"],
        count=types.UInt64(hi=value["count"]["hi"], lo=value["count"]["lo"]),
        summed_variance=value["summed_variance"],
        std_eps=value["std_eps"],
    )


def tree_max_error(left: Any, right: Any) -> tuple[bool, float]:
    same = jax.tree_util.tree_structure(left) == jax.tree_util.tree_structure(right)
    if not same:
        return False, float("inf")
    errors = [
        float(np.max(np.abs(np.asarray(a) - np.asarray(b))))
        for a, b in zip(
            jax.tree_util.tree_leaves(left),
            jax.tree_util.tree_leaves(right),
            strict=True,
        )
    ]
    return True, max(errors, default=0.0)


def output_equivalence(source: list[Any], expanded: list[Any]) -> dict[str, Any]:
    from playground.common.reference_residual_ppo_networks import (
        make_reference_residual_ppo_networks,
    )

    old_networks = make_reference_residual_ppo_networks(
        {"state": (SOURCE_STATE_SIZE,), "privileged_state": (SOURCE_PRIVILEGED_SIZE,)},
        ACTION_SIZE,
    )
    new_networks = make_reference_residual_ppo_networks(
        {"state": (EXPANDED_STATE_SIZE,), "privileged_state": (EXPANDED_PRIVILEGED_SIZE,)},
        ACTION_SIZE,
    )
    old_normalizer = normalizer_state(source[0])
    new_normalizer = normalizer_state(expanded[0])
    old_state = jnp.linspace(-0.25, 0.25, SOURCE_STATE_SIZE, dtype=jnp.float32)[None]
    old_privileged = jnp.linspace(
        -0.5, 0.5, SOURCE_PRIVILEGED_SIZE, dtype=jnp.float32
    )[None]
    old_obs = {"state": old_state, "privileged_state": old_privileged}
    old_actor = old_networks.policy_network.apply(old_normalizer, source[1], old_obs)
    old_critic = old_networks.value_network.apply(old_normalizer, source[2], old_obs)
    cells = []
    for z in (-1.0, 0.0, 1.0):
        state = insert(old_state, z, axis=1)
        privileged = insert(old_privileged, z, axis=1)
        new_obs = {"state": state, "privileged_state": privileged}
        new_actor = new_networks.policy_network.apply(
            new_normalizer, expanded[1], new_obs
        )
        new_critic = new_networks.value_network.apply(
            new_normalizer, expanded[2], new_obs
        )
        cells.append(
            {
                "z": z,
                "actor_max_abs_error": float(
                    np.max(np.abs(np.asarray(new_actor) - np.asarray(old_actor)))
                ),
                "critic_max_abs_error": float(
                    np.max(np.abs(np.asarray(new_critic) - np.asarray(old_critic)))
                ),
                "reference_action_preserved_as_final_14": bool(
                    np.array_equal(np.asarray(state)[0, -ACTION_SIZE:], np.asarray(old_state)[0, -ACTION_SIZE:])
                ),
            }
        )
    return {"cells": cells}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--destination", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source_path = args.source.resolve()
    destination = args.destination.resolve()
    output = args.output.resolve()
    if os.environ.get("JAX_PLATFORMS") != "cpu" or any(
        device.platform != "cpu" for device in jax.devices()
    ):
        raise RuntimeError("CPU-only JAX is required")
    if destination.exists():
        raise FileExistsError(f"destination already exists: {destination}")

    source_hash = sha256_directory(source_path)
    checkpointer = ocp.PyTreeCheckpointer()
    source = checkpointer.restore(str(source_path))
    expanded = expand_checkpoint(source)
    destination.parent.mkdir(parents=True, exist_ok=True)
    checkpointer.save(str(destination), expanded)
    restored = checkpointer.restore(str(destination))

    source_shapes = {
        "state": list(np.asarray(source[0]["mean"]["state"]).shape),
        "privileged_state": list(np.asarray(source[0]["mean"]["privileged_state"]).shape),
        "actor_first_kernel": list(np.asarray(source[1]["params"]["residual_trunk"]["hidden_0"]["kernel"]).shape),
        "critic_first_kernel": list(np.asarray(source[2]["params"]["hidden_0"]["kernel"]).shape),
    }
    expanded_shapes = {
        "state": list(np.asarray(restored[0]["mean"]["state"]).shape),
        "privileged_state": list(np.asarray(restored[0]["mean"]["privileged_state"]).shape),
        "actor_first_kernel": list(np.asarray(restored[1]["params"]["residual_trunk"]["hidden_0"]["kernel"]).shape),
        "critic_first_kernel": list(np.asarray(restored[2]["params"]["hidden_0"]["kernel"]).shape),
    }
    collapsed = collapse_checkpoint(restored)
    preserved_structure, preserved_error = tree_max_error(source, collapsed)
    save_structure, save_error = tree_max_error(expanded, restored)
    equivalence = output_equivalence(source, restored)
    all_output_errors = [
        cell[key]
        for cell in equivalence["cells"]
        for key in ("actor_max_abs_error", "critic_max_abs_error")
    ]
    inserted_values = {
        stream: {
            family: float(np.asarray(restored[0][family][stream])[INSERT_INDEX])
            for family in ("mean", "std", "summed_variance")
        }
        for stream in ("state", "privileged_state")
    }
    actor_zero_row = np.asarray(
        restored[1]["params"]["residual_trunk"]["hidden_0"]["kernel"]
    )[INSERT_INDEX]
    critic_zero_row = np.asarray(restored[2]["params"]["hidden_0"]["kernel"])[
        INSERT_INDEX
    ]
    checks = {
        "cpu_only": jax.default_backend() == "cpu"
        and all(device.platform == "cpu" for device in jax.devices()),
        "source_directory_hash_exact": source_hash == EXPECTED_SOURCE_DIRECTORY_SHA256,
        "source_tree_has_exact_three_members": isinstance(source, list) and len(source) == 3,
        "source_shapes_exact": source_shapes
        == {
            "state": [115], "privileged_state": [226],
            "actor_first_kernel": [115, 512], "critic_first_kernel": [226, 512],
        },
        "source_count_and_epsilon_exact": int(np.asarray(source[0]["count"]["hi"])) == EXPECTED_COUNT_HI
        and int(np.asarray(source[0]["count"]["lo"])) == EXPECTED_COUNT_LO
        and float(np.asarray(source[0]["std_eps"])) == EXPECTED_STD_EPS,
        "expanded_shapes_exact": expanded_shapes
        == {
            "state": [116], "privileged_state": [227],
            "actor_first_kernel": [116, 512], "critic_first_kernel": [227, 512],
        },
        "inserted_normalizer_values_exact": all(
            values == {"mean": 0.0, "std": 1.0, "summed_variance": 8_048_640.0}
            for values in inserted_values.values()
        ),
        "inserted_actor_and_critic_rows_exact_zero": bool(
            np.count_nonzero(actor_zero_row) == 0 and np.count_nonzero(critic_zero_row) == 0
        ),
        "all_other_checkpoint_values_bit_exact": preserved_structure and preserved_error == 0.0,
        "expanded_checkpoint_save_restore_bit_exact": save_structure and save_error == 0.0,
        "actor_and_critic_step_zero_outputs_preserved": max(all_output_errors) <= EQUALITY_TOLERANCE,
        "reference_action_remains_final_14": all(
            cell["reference_action_preserved_as_final_14"] for cell in equivalence["cells"]
        ),
        "all_values_finite": all(
            np.isfinite(np.asarray(leaf)).all() for leaf in jax.tree_util.tree_leaves(restored)
        ),
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    status = "PASS_RESET_COM_ESTIMATOR_CHECKPOINT_EXPANSION" if not failed else "FAIL_RESET_COM_ESTIMATOR_CHECKPOINT_EXPANSION"
    payload = {
        "schema_version": "ground_up_reset_com_estimator_checkpoint_expansion.v1",
        "status": status,
        "tool_sha256": sha256_file(Path(__file__)),
        "checks": checks,
        "failed_checks": failed,
        "source": {"path": str(source_path), "directory_sha256": source_hash, "shapes": source_shapes},
        "expanded": {"path": str(destination), "directory_sha256": sha256_directory(destination), "shapes": expanded_shapes},
        "insert_index": INSERT_INDEX,
        "inserted_normalizer_values": inserted_values,
        "max_other_value_error": preserved_error,
        "max_save_restore_error": save_error,
        "output_equivalence": equivalence,
        "execution": {
            "devices": [str(device) for device in jax.devices()],
            "training_steps": 0,
            "dynamic_behavior_cells": 0,
            "colab": False,
            "robot_or_rdk": False,
        },
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": status, "failed_checks": failed}, sort_keys=True))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
