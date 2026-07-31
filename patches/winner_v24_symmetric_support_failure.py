"""Winner-v24 symmetric roll/pitch support-failure objective mechanics.

The frozen Winner-v22 rollout gives a settled episode a +250 terminal bonus but
leaves a roll/pitch boundary crossing at zero.  This module changes only that
training reward to -250 and deterministically recomputes GAE on the already
recorded rollout.  It never reads hidden configuration or changes physics.
"""

from __future__ import annotations

import hashlib
from typing import Any, Mapping, Sequence

import numpy as np


SYMMETRIC_FAILURE_PENALTY = np.float32(-250.0)
MODIFIED_BATCH_KEYS = ("advantages", "returns", "rewards")


def array_sha256(value: np.ndarray) -> str:
    array = np.ascontiguousarray(np.asarray(value))
    digest = hashlib.sha256()
    digest.update(str(array.dtype).encode())
    digest.update(b"\0")
    digest.update(repr(array.shape).encode())
    digest.update(b"\0")
    digest.update(array.tobytes(order="C"))
    return digest.hexdigest()


def roll_pitch_failure_mask(
    episodes: Sequence[Mapping[str, Any]],
    *,
    shape: tuple[int, int],
) -> np.ndarray:
    """Return one true cell for each observed roll/pitch terminal transition."""

    if len(shape) != 2 or len(episodes) != shape[0]:
        raise ValueError("Winner-v24 episode population shape changed")
    mask = np.zeros(shape, dtype=bool)
    seen: set[int] = set()
    for receipt in episodes:
        environment = receipt.get("environment")
        if type(environment) is not int or not 0 <= environment < shape[0]:
            raise ValueError("Winner-v24 episode environment changed")
        if environment in seen:
            raise ValueError("Winner-v24 episode environment repeated")
        seen.add(environment)
        terminal = receipt.get("terminal")
        if terminal is None:
            continue
        checks = terminal.get("checks")
        tick = terminal.get("tick")
        if not isinstance(checks, Mapping) or type(tick) is not int:
            raise ValueError("Winner-v24 terminal evidence changed")
        if checks.get("roll_pitch") is False:
            if not 0 <= tick < shape[1]:
                raise ValueError("Winner-v24 terminal tick changed")
            mask[environment, tick] = True
    if seen != set(range(shape[0])):
        raise ValueError("Winner-v24 episode population is incomplete")
    return mask


def recompute_gae(
    *,
    rewards: np.ndarray,
    values: np.ndarray,
    done: np.ndarray,
    sample_mask: np.ndarray,
    gamma: float,
    gae_lambda: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Reproduce the frozen float32 GAE and sampled-advantage normalization."""

    rewards = np.asarray(rewards, dtype=np.float32)
    values = np.asarray(values, dtype=np.float32)
    done = np.asarray(done, dtype=np.float32)
    sample_mask = np.asarray(sample_mask, dtype=np.float32)
    if (
        rewards.ndim != 2
        or values.shape != rewards.shape
        or done.shape != rewards.shape
        or sample_mask.shape != rewards.shape
        or not np.all((sample_mask == 0.0) | (sample_mask == 1.0))
        or not np.all((done == 0.0) | (done == 1.0))
    ):
        raise ValueError("Winner-v24 GAE tensor schema changed")
    if not all(np.all(np.isfinite(value)) for value in (rewards, values, done, sample_mask)):
        raise FloatingPointError("Winner-v24 GAE input is nonfinite")
    advantages = np.zeros_like(rewards, dtype=np.float32)
    returns = np.zeros_like(rewards, dtype=np.float32)
    for environment in range(rewards.shape[0]):
        count = int(np.sum(sample_mask[environment]))
        if count <= 0 or not np.all(sample_mask[environment, :count] == 1.0):
            raise ValueError("Winner-v24 sampled prefix changed")
        if not np.all(sample_mask[environment, count:] == 0.0):
            raise ValueError("Winner-v24 sampled padding changed")
        gae = np.float32(0.0)
        for tick in range(count - 1, -1, -1):
            nonterminal = np.float32(1.0 - done[environment, tick])
            next_value = values[environment, tick + 1] if tick + 1 < count else 0.0
            delta = (
                rewards[environment, tick]
                + np.float32(gamma) * np.float32(next_value) * nonterminal
                - values[environment, tick]
            )
            gae = delta + (
                np.float32(gamma)
                * np.float32(gae_lambda)
                * nonterminal
                * gae
            )
            advantages[environment, tick] = gae
            returns[environment, tick] = gae + values[environment, tick]
    valid = advantages[sample_mask.astype(bool)].astype(np.float64)
    mean = float(np.mean(valid, dtype=np.float64))
    std = max(float(np.std(valid, dtype=np.float64, ddof=0)), 1.0e-6)
    advantages = np.where(
        sample_mask > 0,
        (advantages - np.float32(mean)) / np.float32(std),
        np.float32(0.0),
    ).astype(np.float32)
    if not np.all(np.isfinite(advantages)) or not np.all(np.isfinite(returns)):
        raise FloatingPointError("Winner-v24 GAE output is nonfinite")
    return returns, advantages


def apply_symmetric_failure_objective(
    batch: Mapping[str, np.ndarray],
    episodes: Sequence[Mapping[str, Any]],
    values: np.ndarray,
    *,
    enabled: bool,
    gamma: float,
    gae_lambda: float,
) -> tuple[dict[str, np.ndarray], dict[str, Any]]:
    """Apply only the frozen -250 roll/pitch terminal reward when enabled."""

    required = {
        "advantages",
        "done",
        "returns",
        "rewards",
        "valid_mask",
        "valid_transition_mask",
    }
    if required - set(batch):
        raise KeyError(f"Winner-v24 batch fields missing: {sorted(required - set(batch))}")
    result = {key: np.asarray(value).copy() for key, value in batch.items()}
    shape = np.asarray(batch["rewards"]).shape
    if len(shape) != 2 or np.asarray(values).shape != shape:
        raise ValueError("Winner-v24 batch shape changed")
    failure_mask = roll_pitch_failure_mask(episodes, shape=shape)
    count = int(np.sum(failure_mask))
    evidence = {
        "enabled": bool(enabled),
        "roll_pitch_failure_count": count,
        "roll_pitch_failure_mask_sha256": array_sha256(failure_mask.astype(np.uint8)),
        "penalty": float(SYMMETRIC_FAILURE_PENALTY),
        "modified_batch_keys": [] if not enabled else list(MODIFIED_BATCH_KEYS),
    }
    if not enabled:
        return result, evidence
    if count <= 0:
        raise ValueError("Winner-v24 rollout contains no roll/pitch failure")
    sample_mask = np.asarray(batch["valid_mask"], dtype=np.float32)
    valid_transition = np.asarray(batch["valid_transition_mask"], dtype=np.float32)
    done = np.asarray(batch["done"], dtype=np.float32)
    rewards = np.asarray(batch["rewards"], dtype=np.float32).copy()
    if (
        not np.all(sample_mask[failure_mask] == np.float32(1.0))
        or not np.all(valid_transition[failure_mask] == np.float32(0.0))
        or not np.all(done[failure_mask] == np.float32(1.0))
        or not np.all(rewards[failure_mask] == np.float32(0.0))
    ):
        raise ValueError("Winner-v24 terminal roll/pitch boundary changed")
    rewards[failure_mask] = SYMMETRIC_FAILURE_PENALTY
    returns, advantages = recompute_gae(
        rewards=rewards,
        values=values,
        done=done,
        sample_mask=sample_mask,
        gamma=gamma,
        gae_lambda=gae_lambda,
    )
    result["rewards"] = rewards
    result["returns"] = returns
    result["advantages"] = advantages
    return result, evidence
