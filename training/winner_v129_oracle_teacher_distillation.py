"""Deterministic adapter-head distillation from the exact V126 oracle."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import jax
import jax.numpy as jnp
import numpy as np


ACTION_SIZE = 14
HIDDEN_SIZE = 64
OBS_SIZE = 115
BATCH_SIZE = 256
TORQUE_CORRECTION_EPS = 1.0e-7


def load_teacher_dataset(run_root: Path) -> dict[str, Any]:
    rows = []
    manifest = []
    for trace_path in sorted(run_root.resolve().glob("traces/*_final_*.jsonl")):
        records = [
            json.loads(line)
            for line in trace_path.read_text(encoding="utf-8").splitlines()
            if line
        ]
        if len(records) != 600:
            raise ValueError(f"incomplete V129 teacher trace: {trace_path}")
        manifest.append(
            {
                "name": trace_path.name,
                "rows": len(records),
                "sha256": _sha256(trace_path),
            }
        )
        for record in records:
            oracle = record["exact_torque_oracle"]
            target = np.asarray(oracle["final_action"], dtype=np.float32)
            key = f"{trace_path.name}:{int(record['tick']):03d}"
            rows.append(
                {
                    "key": key,
                    "obs": np.asarray(record["obs_state"], dtype=np.float32),
                    "previous_action": np.asarray(
                        record["policy_state_input"]["previous_action"][0],
                        dtype=np.float32,
                    ),
                    "h_in": np.asarray(
                        record["policy_state_input"]["h_in"][0],
                        dtype=np.float32,
                    ),
                    "target_action": target,
                    "target_h_out": np.asarray(
                        record["policy_state_output"]["h_out"][0],
                        dtype=np.float32,
                    ),
                    "corrected": bool(oracle["projected_joint_indices"]),
                }
            )
    if len(rows) != 4_800 or len(manifest) != 8:
        raise ValueError("V129 teacher dataset must contain 8x600 rows")
    correction_count = sum(int(row["corrected"]) for row in rows)
    if correction_count != 14:
        raise ValueError(
            f"V129 expected 14 corrected rows, got {correction_count}"
        )
    rows.sort(
        key=lambda row: hashlib.sha256(row["key"].encode()).hexdigest()
    )
    corrected = np.asarray(
        [row["corrected"] for row in rows], dtype=np.bool_
    )
    correction_weight = float(
        np.sum(~corrected) / np.sum(corrected)
    )
    weights = np.where(corrected, correction_weight, 1.0).astype(
        np.float32
    )
    return {
        "obs": np.stack([row["obs"] for row in rows]),
        "previous_action": np.stack(
            [row["previous_action"] for row in rows]
        ),
        "h_in": np.stack([row["h_in"] for row in rows]),
        "target_action": np.stack(
            [row["target_action"] for row in rows]
        ),
        "target_h_out": np.stack(
            [row["target_h_out"] for row in rows]
        ),
        "weights": weights,
        "corrected": corrected,
        "keys": [row["key"] for row in rows],
        "manifest": manifest,
        "correction_weight": correction_weight,
        "updates_per_epoch": int(np.ceil(len(rows) / BATCH_SIZE)),
    }


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def head_from_policy(policy_params: Any) -> dict[str, jax.Array]:
    return {
        key: jnp.asarray(value)
        for key, value in policy_params["params"][
            "adapter_location"
        ].items()
    }


def policy_with_head(
    policy_params: Any, head: dict[str, jax.Array]
) -> Any:
    updated = dict(policy_params)
    updated_params = dict(policy_params["params"])
    updated_params["adapter_location"] = head
    updated["params"] = updated_params
    return updated


def deployed_actions(
    network: Any,
    normalizer: Any,
    policy_params: Any,
    obs: jax.Array,
    previous_action: jax.Array,
    h_in: jax.Array,
    transform: dict[str, Any],
) -> tuple[jax.Array, jax.Array]:
    logits, h_out = network.policy_network.apply_with_state(
        normalizer,
        policy_params,
        {"state": obs, "policy_hidden": h_in},
    )
    raw = jnp.tanh(logits[..., :ACTION_SIZE])
    delta = jnp.asarray(
        transform["exact_train_normalized_action_delta"],
        dtype=jnp.float32,
    )
    velocity_bounded = jnp.clip(
        raw, previous_action - delta, previous_action + delta
    )
    home = jnp.asarray(transform["home_target_rad"], dtype=jnp.float32)
    obs_indices = jnp.asarray(
        transform["measured_joint_offset_indices"], dtype=jnp.int32
    )
    pitch_indices = jnp.asarray(
        transform["pitch_chain_action_indices"], dtype=jnp.int32
    )
    pitch_mask = jnp.zeros((ACTION_SIZE,), dtype=jnp.bool_).at[
        pitch_indices
    ].set(True)
    action_scale = jnp.asarray(
        transform["action_scale_rad"], dtype=jnp.float32
    )
    margin = jnp.asarray(transform["g3_margin_rad"], dtype=jnp.float32)
    actual_target = home + jnp.take(obs, obs_indices, axis=-1)
    desired_target = home + velocity_bounded * action_scale
    clipped_target = jnp.clip(
        desired_target, actual_target - margin, actual_target + margin
    )
    guard_action = jnp.clip(
        (clipped_target - home) / action_scale, -1.0, 1.0
    )
    guarded = jnp.where(pitch_mask, guard_action, velocity_bounded)
    command = obs[..., int(transform["command_x_observation_index"])]
    zero = jnp.abs(command) <= float(
        transform["zero_deadband_absolute_command_x"]
    )
    deadbanded = jnp.where(zero[..., None], 0.0, guarded)
    final = jnp.clip(
        deadbanded, previous_action - delta, previous_action + delta
    )
    final = jnp.where(zero[..., None], 0.0, final)
    return final, h_out


def loss_components(
    network: Any,
    normalizer: Any,
    fixed_policy_params: Any,
    head: dict[str, jax.Array],
    batch: dict[str, jax.Array],
    transform: dict[str, Any],
) -> tuple[jax.Array, tuple[jax.Array, jax.Array]]:
    policy_params = policy_with_head(fixed_policy_params, head)
    action, h_out = deployed_actions(
        network,
        normalizer,
        policy_params,
        batch["obs"],
        batch["previous_action"],
        batch["h_in"],
        transform,
    )
    action_per_row = jnp.mean(
        jnp.square(action - batch["target_action"]), axis=-1
    )
    action_loss = jnp.sum(action_per_row * batch["weights"]) / jnp.sum(
        batch["weights"]
    )
    hidden_loss = jnp.mean(jnp.square(h_out - batch["target_h_out"]))
    return action_loss + hidden_loss, (action_loss, hidden_loss)


def padded_epoch_batches(dataset: dict[str, Any]) -> list[dict[str, np.ndarray]]:
    size = int(dataset["obs"].shape[0])
    updates = int(dataset["updates_per_epoch"])
    padded_size = updates * BATCH_SIZE
    batches = []
    for start in range(0, padded_size, BATCH_SIZE):
        indices = np.arange(start, start + BATCH_SIZE)
        valid = indices < size
        clipped = np.minimum(indices, size - 1)
        batch = {
            key: np.asarray(dataset[key][clipped])
            for key in (
                "obs",
                "previous_action",
                "h_in",
                "target_action",
                "target_h_out",
                "weights",
            )
        }
        batch["weights"] = batch["weights"] * valid.astype(np.float32)
        batches.append(batch)
    return batches
