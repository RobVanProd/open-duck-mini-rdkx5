"""Winner-v15 one-sided negative-pitch support objective.

This module intentionally copies the reviewed Stage-2 rollout boundary so the
frozen v12/v13 implementations remain byte-identical.  The only enabled-path
semantic change is the valid-transition reward defined below.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np


PITCH_BOUNDARY_RAD = np.float32(0.35)


def valid_transition_reward(
    next_pitch_rad: np.ndarray | float,
    *,
    enabled: bool,
) -> np.ndarray:
    """Return the frozen alive reward or its bounded negative-pitch margin."""

    pitch = np.asarray(next_pitch_rad, dtype=np.float32)
    if not enabled:
        return np.ones_like(pitch, dtype=np.float32)
    normalized = np.clip(
        np.maximum(np.float32(0.0), -pitch) / PITCH_BOUNDARY_RAD,
        np.float32(0.0),
        np.float32(1.0),
    ).astype(np.float32)
    return (
        np.float32(1.0) - np.square(normalized).astype(np.float32)
    ).astype(np.float32)


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
    enabled: bool,
) -> tuple[dict[str, np.ndarray], list[dict[str, Any]], np.ndarray]:
    """Run the reviewed Stage-2 transition with one optional reward change."""

    import jax.numpy as jnp

    with full.frozen_rollout_context(update_index):
        shape = (smoke.SMOKE_ENVIRONMENTS, smoke.SMOKE_TICKS)
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
                    valid_transition_reward(evidence["pitch_rad"], enabled=enabled),
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
            raise ValueError("stage 2 collected no valid transitions")
        advantages = np.zeros(shape, dtype=np.float32)
        returns = np.zeros(shape, dtype=np.float32)
        for environment in range(smoke.SMOKE_ENVIRONMENTS):
            count = int(np.sum(sample_mask[environment]))
            gae = np.float32(0.0)
            for tick in range(count - 1, -1, -1):
                nonterminal = np.float32(1.0 - done[environment, tick])
                next_value = (
                    values[environment, tick + 1] if tick + 1 < count else 0.0
                )
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
            raise FloatingPointError("Winner-v15 pitch-margin rollout is nonfinite")
        return (
            batch,
            receipts,
            np.asarray(observation_bank[: smoke.SMOKE_TICKS], dtype=np.float32),
        )


def reward_evidence(batch: Mapping[str, np.ndarray]) -> dict[str, Any]:
    valid = np.asarray(batch["valid_transition_mask"], dtype=bool)
    rewards = np.asarray(batch["rewards"], dtype=np.float32)
    penalties = np.asarray(
        batch["applied_negative_pitch_penalty"], dtype=np.float32
    )
    pitch = np.asarray(batch["next_pitch_rad"], dtype=np.float32)
    if not np.any(valid):
        raise ValueError("pitch-margin reward evidence has no valid transitions")
    expected = np.asarray(valid_transition_reward(pitch, enabled=True), dtype=np.float32)
    terminal_bonus = rewards - np.where(valid, expected, np.float32(0.0))
    return {
        "valid_transition_count": int(np.sum(valid)),
        "reward_min": float(np.min(rewards[valid])),
        "reward_max_without_terminal_bonus": float(np.max(expected[valid])),
        "penalty_min": float(np.min(penalties[valid])),
        "penalty_max": float(np.max(penalties[valid])),
        "nonzero_penalty_count": int(np.sum(penalties[valid] > 0.0)),
        "reward_formula_bit_exact": bool(
            np.array_equal(
                rewards[valid] - terminal_bonus[valid],
                expected[valid],
            )
        ),
        "penalty_formula_bit_exact": bool(
            np.array_equal(
                penalties[valid],
                (np.float32(1.0) - expected[valid]).astype(np.float32),
            )
        ),
        "only_zero_or_settled_bonus": bool(
            np.all(
                (terminal_bonus == np.float32(0.0))
                | (terminal_bonus == np.float32(250.0))
            )
        ),
        "all_rewards_nonnegative": bool(np.all(rewards >= 0.0)),
        "all_penalties_in_unit_interval": bool(
            np.all((penalties >= 0.0) & (penalties <= 1.0))
        ),
    }
