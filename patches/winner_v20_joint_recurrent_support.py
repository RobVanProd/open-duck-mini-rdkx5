"""Winner-v20 joint recurrent support-training mechanics.

The rollout is the reviewed Winner-v15 transition with one additional tensor:
the complete observation sequence required to recompute the existing recurrent
state inside the PPO gradient.  Reward, sampling, bounds, masks, and episode
semantics are unchanged.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping, Sequence

import jax
import jax.numpy as jnp
import numpy as np

import winner_v12_calibrator_training as base
import winner_v15_pitch_margin_support as v15


RECURRENT_CORE_KEYS = (
    "obs_weight",
    "previous_action_weight",
    "hidden_weight",
    "hidden_bias",
)
FROZEN_AUXILIARY_KEYS = (
    "auxiliary_hidden_weight",
    "auxiliary_action_weight",
    "auxiliary_bias",
)
JOINT_TRAINABLE_KEYS = (
    RECURRENT_CORE_KEYS + base.DEPLOYABLE_ACTION_KEYS + base.TRAINING_ONLY_STAGE2_KEYS
)


def _select(
    parameters: Mapping[str, Any], keys: Sequence[str]
) -> dict[str, jax.Array]:
    if set(keys) - set(parameters):
        raise KeyError(f"missing parameter keys: {sorted(set(keys) - set(parameters))}")
    return {key: jnp.asarray(parameters[key], dtype=jnp.float32) for key in keys}


def joint_trainable_parameters(parameters: Mapping[str, Any]) -> dict[str, jax.Array]:
    """Return exactly the recurrent core and reviewed Stage-2 leaves."""

    return _select(parameters, JOINT_TRAINABLE_KEYS)


def frozen_auxiliary_parameters(parameters: Mapping[str, Any]) -> dict[str, jax.Array]:
    """Return the response-prediction leaves that must remain bit-exact."""

    return _select(parameters, FROZEN_AUXILIARY_KEYS)


def merge_joint_trainable(
    parameters: Mapping[str, Any], trainable: Mapping[str, Any]
) -> dict[str, jax.Array]:
    if set(trainable) != set(JOINT_TRAINABLE_KEYS):
        raise ValueError("Winner-v20 joint-trainable parameter schema changed")
    merged = {key: jnp.asarray(value, dtype=jnp.float32) for key, value in parameters.items()}
    merged.update(
        {key: jnp.asarray(value, dtype=jnp.float32) for key, value in trainable.items()}
    )
    return merged


def load_joint_snapshot(
    path: Path, *, expected_schema_version: str
) -> dict[str, Any]:
    """Read back the exact nine-leaf Winner-v20 optimizer schema."""

    with np.load(path, allow_pickle=False) as archive:
        if len(archive.files) != len(set(archive.files)):
            raise ValueError("Winner-v20 snapshot contains duplicate members")
        arrays = {name: archive[name].copy() for name in archive.files}
    if "metadata_json" not in arrays:
        raise ValueError("Winner-v20 snapshot metadata is absent")
    metadata_array = np.asarray(arrays.pop("metadata_json"))
    if metadata_array.shape != () or metadata_array.dtype.kind != "U":
        raise ValueError("Winner-v20 snapshot metadata layout changed")
    metadata = json.loads(str(metadata_array.item()))
    if (
        not isinstance(metadata, dict)
        or metadata.get("schema_version") != expected_schema_version
        or metadata.get("stage") != "joint_recurrent_stage2"
    ):
        raise ValueError("Winner-v20 snapshot metadata changed")
    parameter_keys = set(
        base.DEPLOYABLE_CALIBRATOR_KEYS + base.TRAINING_ONLY_STAGE2_KEYS
    )
    optimizer_keys = set(JOINT_TRAINABLE_KEYS)
    expected_members = {
        "target_mean",
        "target_std",
        "optimizer.count",
        *(f"parameter.{key}" for key in parameter_keys),
        *(f"optimizer.m.{key}" for key in optimizer_keys),
        *(f"optimizer.v.{key}" for key in optimizer_keys),
    }
    if set(arrays) != expected_members:
        raise ValueError("Winner-v20 snapshot member schema changed")
    parameters = {
        name.removeprefix("parameter."): value
        for name, value in arrays.items()
        if name.startswith("parameter.")
    }
    optimizer = {
        "count": arrays["optimizer.count"],
        "m": {
            name.removeprefix("optimizer.m."): value
            for name, value in arrays.items()
            if name.startswith("optimizer.m.")
        },
        "v": {
            name.removeprefix("optimizer.v."): value
            for name, value in arrays.items()
            if name.startswith("optimizer.v.")
        },
    }
    return {
        "parameters": parameters,
        "optimizer": optimizer,
        "metadata": metadata,
        "target_mean": arrays["target_mean"],
        "target_std": arrays["target_std"],
    }


def recurrent_hidden_trajectory(
    parameters: Mapping[str, Any],
    observations: jax.Array,
    previous_actions: jax.Array,
) -> jax.Array:
    """Recompute the 64-state trajectory with full per-environment BPTT."""

    observations = jnp.asarray(observations, dtype=jnp.float32)
    previous_actions = jnp.asarray(previous_actions, dtype=jnp.float32)
    if observations.ndim != 3 or observations.shape[-1] != base.OBS_SIZE:
        raise ValueError("Winner-v20 observations must have shape [E,T,115]")
    if (
        previous_actions.ndim != 3
        or previous_actions.shape[:2] != observations.shape[:2]
        or previous_actions.shape[-1] != base.ACTION_SIZE
    ):
        raise ValueError("Winner-v20 previous actions must have shape [E,T,14]")

    def run_one(obs: jax.Array, previous: jax.Array) -> jax.Array:
        def step(h_in: jax.Array, values: tuple[jax.Array, jax.Array]):
            obs_t, previous_t = values
            hidden_pre = (
                obs_t @ parameters["obs_weight"]
                + previous_t @ parameters["previous_action_weight"]
                + h_in @ parameters["hidden_weight"]
                + parameters["hidden_bias"]
            )
            h_out = jnp.tanh(hidden_pre)
            return h_out, h_out

        initial = jnp.zeros((base.HIDDEN_SIZE,), dtype=jnp.float32)
        _, hidden = jax.lax.scan(step, initial, (obs, previous))
        return hidden

    return jax.vmap(run_one)(observations, previous_actions)


def joint_recurrent_ppo_loss(
    trainable: Mapping[str, Any],
    batch: Mapping[str, jax.Array],
    *,
    clip_epsilon: float,
    value_coefficient: float,
    entropy_coefficient: float,
) -> tuple[jax.Array, dict[str, jax.Array]]:
    """Apply the reviewed PPO loss to a differentiably recomputed hidden state."""

    hidden = recurrent_hidden_trajectory(
        trainable, batch["observations"], batch["previous_actions"]
    )
    replay_error = jnp.max(jnp.abs(hidden - batch["hidden"]))
    recurrent_batch = dict(batch)
    recurrent_batch["hidden"] = hidden
    loss, metrics = base.stage2_ppo_loss(
        trainable,
        recurrent_batch,
        clip_epsilon=clip_epsilon,
        value_coefficient=value_coefficient,
        entropy_coefficient=entropy_coefficient,
    )
    return loss, {**metrics, "source_hidden_replay_max_abs_error": replay_error}


def stage2_rollout(
    *,
    smoke: Any,
    full: Any,
    training: Any,
    mujoco: Any,
    scene: Path,
    population: Sequence[Mapping[str, Any]],
    preregistration: Mapping[str, Any],
    observer_type: type[Any],
    canonical_fit: Path,
    parameters: Mapping[str, Any],
    update_index: int,
) -> tuple[dict[str, np.ndarray], list[dict[str, Any]], np.ndarray]:
    """Run the Winner-v15 rollout and retain all observations for BPTT."""

    with full.frozen_rollout_context(update_index):
        shape = (smoke.SMOKE_ENVIRONMENTS, smoke.SMOKE_TICKS)
        observations = np.zeros((*shape, training.OBS_SIZE), dtype=np.float32)
        hidden = np.zeros((*shape, training.HIDDEN_SIZE), dtype=np.float32)
        raw_samples = np.zeros((*shape, training.ACTION_SIZE), dtype=np.float32)
        previous_actions = np.zeros((*shape, training.ACTION_SIZE), dtype=np.float32)
        realized_actions = np.zeros((*shape, training.ACTION_SIZE), dtype=np.float32)
        old_log_probability = np.zeros(shape, dtype=np.float32)
        values = np.zeros(shape, dtype=np.float32)
        rewards = np.zeros(shape, dtype=np.float32)
        applied_negative_pitch_penalty = np.zeros(shape, dtype=np.float32)
        next_pitch_rad = np.zeros(shape, dtype=np.float32)
        sample_mask = np.zeros(shape, dtype=np.float32)
        valid_transition_mask = np.zeros(shape, dtype=np.float32)
        done = np.zeros(shape, dtype=np.float32)
        observation_bank: list[np.ndarray] = []
        receipts: list[dict[str, Any]] = []
        for environment, configuration in enumerate(population):
            plant = smoke.PLANTS[environment % 2]
            rng, rng_receipt = smoke.prng_for(2, environment)
            episode = smoke.Episode(
                mujoco,
                scene,
                configuration,
                plant,
                preregistration,
                observer_type,
                canonical_fit,
            )
            if episode.initial_contacts != (1, 1):
                raise ValueError(
                    f"{configuration['id']} does not start with both feet loaded"
                )
            h_in = np.zeros(training.HIDDEN_SIZE, dtype=np.float32)
            terminal = None
            for tick in range(smoke.SMOKE_TICKS):
                observation = episode.observation()
                previous = np.asarray(episode.previous_action, dtype=np.float32).copy()
                h_out, _ = training.response_step(
                    parameters,
                    jnp.asarray(observation),
                    jnp.asarray(previous),
                    jnp.asarray(h_in),
                    jnp.zeros((training.ACTION_SIZE,), dtype=jnp.float32),
                )
                epsilon = rng.normal(0.0, 1.0, training.ACTION_SIZE).astype(np.float32)
                action, raw, log_probability, value = training.sample_stage2_action(
                    parameters,
                    h_out,
                    jnp.asarray(previous),
                    jnp.asarray(epsilon),
                )
                action_np = np.asarray(action, dtype=np.float32)
                valid, _, evidence = episode.step(action_np)
                observations[environment, tick] = observation
                hidden[environment, tick] = np.asarray(h_out, dtype=np.float32)
                raw_samples[environment, tick] = np.asarray(raw, dtype=np.float32)
                previous_actions[environment, tick] = previous
                realized_actions[environment, tick] = action_np
                old_log_probability[environment, tick] = float(log_probability)
                values[environment, tick] = float(value)
                next_pitch_rad[environment, tick] = np.float32(evidence["pitch_rad"])
                sample_mask[environment, tick] = np.float32(1.0)
                observation_bank.append(observation.copy())
                if not valid:
                    done[environment, tick] = np.float32(1.0)
                    terminal = {"tick": tick, **evidence}
                    break
                reward = np.asarray(
                    v15.valid_transition_reward(evidence["pitch_rad"], enabled=True),
                    dtype=np.float32,
                ).item()
                rewards[environment, tick] = reward
                applied_negative_pitch_penalty[environment, tick] = np.float32(
                    1.0 - reward
                )
                valid_transition_mask[environment, tick] = np.float32(1.0)
                h_in = np.asarray(h_out, dtype=np.float32)
            summary = episode.summary()
            settled = bool(
                episode.valid_ticks == smoke.SMOKE_TICKS
                and summary["maximum_final_window_gyro_xy_norm_rad_s"]
                <= smoke.FINAL_GYRO_LIMIT_RAD_S
            )
            if settled:
                rewards[environment, smoke.SMOKE_TICKS - 1] += np.float32(
                    smoke.TERMINAL_BONUS
                )
            if episode.valid_ticks == smoke.SMOKE_TICKS:
                done[environment, smoke.SMOKE_TICKS - 1] = np.float32(1.0)
            receipts.append(
                {
                    "environment": environment,
                    "configuration_id": configuration["id"],
                    "configuration_sha256": smoke.canonical_sha256(configuration),
                    "plant": plant,
                    "prng": rng_receipt,
                    "terminal": terminal,
                    "terminal_success_bonus_applied": settled,
                    "episode": summary,
                }
            )
        if not np.any(valid_transition_mask):
            raise ValueError("Winner-v20 collected no valid transitions")
        advantages = np.zeros(shape, dtype=np.float32)
        returns = np.zeros(shape, dtype=np.float32)
        for environment in range(smoke.SMOKE_ENVIRONMENTS):
            count = int(np.sum(sample_mask[environment]))
            gae = np.float32(0.0)
            for tick in range(count - 1, -1, -1):
                nonterminal = np.float32(1.0 - done[environment, tick])
                next_value = values[environment, tick + 1] if tick + 1 < count else 0.0
                delta = (
                    rewards[environment, tick]
                    + np.float32(training.PPO_GAMMA)
                    * np.float32(next_value)
                    * nonterminal
                    - values[environment, tick]
                )
                gae = delta + (
                    np.float32(training.PPO_GAMMA)
                    * np.float32(training.PPO_GAE_LAMBDA)
                    * nonterminal
                    * gae
                )
                advantages[environment, tick] = gae
                returns[environment, tick] = gae + values[environment, tick]
        valid_advantages = advantages[sample_mask.astype(bool)].astype(np.float64)
        advantage_mean = float(np.mean(valid_advantages, dtype=np.float64))
        advantage_std = max(
            float(np.std(valid_advantages, dtype=np.float64, ddof=0)), 1.0e-6
        )
        advantages = np.where(
            sample_mask > 0,
            (advantages - np.float32(advantage_mean)) / np.float32(advantage_std),
            np.float32(0.0),
        ).astype(np.float32)
        if len(observation_bank) < smoke.SMOKE_TICKS:
            raise ValueError("fewer than 250 valid observations for ONNX chain check")
        batch = {
            "observations": observations,
            "hidden": hidden,
            "raw_samples": raw_samples,
            "previous_actions": previous_actions,
            "realized_actions": realized_actions,
            "old_log_probability": old_log_probability,
            "returns": returns,
            "advantages": advantages,
            "valid_mask": sample_mask,
            "valid_transition_mask": valid_transition_mask,
            "done": done,
            "rewards": rewards,
            "applied_negative_pitch_penalty": applied_negative_pitch_penalty,
            "next_pitch_rad": next_pitch_rad,
        }
        if not all(
            np.all(np.isfinite(value))
            for value in batch.values()
            if np.issubdtype(np.asarray(value).dtype, np.number)
        ):
            raise FloatingPointError("Winner-v20 recurrent rollout is nonfinite")
        return (
            batch,
            receipts,
            np.asarray(observation_bank[: smoke.SMOKE_TICKS], dtype=np.float32),
        )


def leaf_max_abs_delta(
    before: Mapping[str, Any], after: Mapping[str, Any]
) -> dict[str, float]:
    if set(before) != set(after):
        raise ValueError("Winner-v20 delta trees differ")
    return {
        key: float(
            np.max(np.abs(np.asarray(after[key]) - np.asarray(before[key])))
        )
        for key in before
    }
