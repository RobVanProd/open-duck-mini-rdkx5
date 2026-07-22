"""Baseline-anchored Winner-v24 symmetric support-failure objective.

This prospective correction does not replay unchanged GAE.  It treats the
recorded baseline returns as authoritative, reconstructs only their associated
raw advantages, and adds the analytically propagated reward delta caused by the
new -250 roll/pitch terminal reward.
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence

import numpy as np

import winner_v24_symmetric_support_failure as v1


SYMMETRIC_FAILURE_PENALTY = v1.SYMMETRIC_FAILURE_PENALTY
MODIFIED_BATCH_KEYS = v1.MODIFIED_BATCH_KEYS


def analytically_propagated_terminal_delta(
    failure_mask: np.ndarray,
    done: np.ndarray,
    sample_mask: np.ndarray,
    *,
    gamma: float,
    gae_lambda: float,
) -> np.ndarray:
    """Propagate only the terminal reward delta through the frozen GAE chain."""

    failure_mask = np.asarray(failure_mask, dtype=bool)
    done = np.asarray(done, dtype=np.float32)
    sample_mask = np.asarray(sample_mask, dtype=np.float32)
    if (
        failure_mask.ndim != 2
        or done.shape != failure_mask.shape
        or sample_mask.shape != failure_mask.shape
        or not np.all((done == 0.0) | (done == 1.0))
        or not np.all((sample_mask == 0.0) | (sample_mask == 1.0))
    ):
        raise ValueError("Winner-v24 v2 terminal-delta tensor schema changed")
    delta = np.zeros(failure_mask.shape, dtype=np.float32)
    factor = np.float32(gamma) * np.float32(gae_lambda)
    for environment in range(failure_mask.shape[0]):
        indices = np.flatnonzero(failure_mask[environment])
        if len(indices) > 1:
            raise ValueError("Winner-v24 v2 has multiple terminal failures in one episode")
        if len(indices) == 0:
            continue
        terminal_tick = int(indices[0])
        count = int(np.sum(sample_mask[environment]))
        if (
            terminal_tick != count - 1
            or done[environment, terminal_tick] != np.float32(1.0)
        ):
            raise ValueError("Winner-v24 v2 failure is not the sampled terminal")
        propagated = np.float32(SYMMETRIC_FAILURE_PENALTY)
        delta[environment, terminal_tick] = propagated
        for tick in range(terminal_tick - 1, -1, -1):
            propagated = (
                factor
                * np.float32(1.0 - done[environment, tick])
                * propagated
            )
            delta[environment, tick] = propagated
    if not np.all(np.isfinite(delta)):
        raise FloatingPointError("Winner-v24 v2 terminal delta is nonfinite")
    return delta


def normalize_sampled_advantages(
    raw_advantages: np.ndarray, sample_mask: np.ndarray
) -> np.ndarray:
    raw = np.asarray(raw_advantages, dtype=np.float32)
    mask = np.asarray(sample_mask, dtype=np.float32)
    if raw.ndim != 2 or mask.shape != raw.shape or not np.any(mask > 0):
        raise ValueError("Winner-v24 v2 advantage normalization schema changed")
    valid = raw[mask.astype(bool)].astype(np.float64)
    mean = float(np.mean(valid, dtype=np.float64))
    std = max(float(np.std(valid, dtype=np.float64, ddof=0)), 1.0e-6)
    normalized = np.where(
        mask > 0,
        (raw - np.float32(mean)) / np.float32(std),
        np.float32(0.0),
    ).astype(np.float32)
    if not np.all(np.isfinite(normalized)):
        raise FloatingPointError("Winner-v24 v2 normalized advantage is nonfinite")
    return normalized


def apply_baseline_anchored_objective(
    batch: Mapping[str, np.ndarray],
    episodes: Sequence[Mapping[str, Any]],
    values: np.ndarray,
    *,
    enabled: bool,
    gamma: float,
    gae_lambda: float,
) -> tuple[dict[str, np.ndarray], dict[str, Any]]:
    """Apply only the analytic terminal delta to recorded baseline returns."""

    required = {
        "advantages",
        "done",
        "returns",
        "rewards",
        "valid_mask",
        "valid_transition_mask",
    }
    if required - set(batch):
        raise KeyError(f"Winner-v24 v2 batch fields missing: {sorted(required - set(batch))}")
    result = {key: np.asarray(value).copy() for key, value in batch.items()}
    shape = np.asarray(batch["rewards"]).shape
    values = np.asarray(values, dtype=np.float32)
    if len(shape) != 2 or values.shape != shape:
        raise ValueError("Winner-v24 v2 batch shape changed")
    failure_mask = v1.roll_pitch_failure_mask(episodes, shape=shape)
    count = int(np.sum(failure_mask))
    evidence = {
        "enabled": bool(enabled),
        "anchor": "recorded_baseline_returns_and_rederived_values",
        "roll_pitch_failure_count": count,
        "roll_pitch_failure_mask_sha256": v1.array_sha256(
            failure_mask.astype(np.uint8)
        ),
        "penalty": float(SYMMETRIC_FAILURE_PENALTY),
        "modified_batch_keys": [] if not enabled else list(MODIFIED_BATCH_KEYS),
    }
    if not enabled:
        return result, evidence
    if count <= 0:
        raise ValueError("Winner-v24 v2 rollout contains no roll/pitch failure")
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
        raise ValueError("Winner-v24 v2 terminal roll/pitch boundary changed")
    rewards[failure_mask] = SYMMETRIC_FAILURE_PENALTY
    baseline_raw_advantages = (
        np.asarray(batch["returns"], dtype=np.float32) - values
    ).astype(np.float32)
    baseline_raw_advantages = np.where(
        sample_mask > 0, baseline_raw_advantages, np.float32(0.0)
    ).astype(np.float32)
    delta = analytically_propagated_terminal_delta(
        failure_mask,
        done,
        sample_mask,
        gamma=gamma,
        gae_lambda=gae_lambda,
    )
    symmetric_raw_advantages = (baseline_raw_advantages + delta).astype(np.float32)
    returns = np.where(
        sample_mask > 0,
        symmetric_raw_advantages + values,
        np.float32(0.0),
    ).astype(np.float32)
    advantages = normalize_sampled_advantages(symmetric_raw_advantages, sample_mask)
    result["rewards"] = rewards
    result["returns"] = returns
    result["advantages"] = advantages
    evidence.update(
        {
            "baseline_raw_advantages_sha256": v1.array_sha256(
                baseline_raw_advantages
            ),
            "analytical_terminal_delta_sha256": v1.array_sha256(delta),
            "analytical_terminal_delta_nonzero_count": int(np.sum(delta != 0.0)),
            "analytical_terminal_delta_min": float(np.min(delta)),
            "analytical_terminal_delta_max": float(np.max(delta)),
        }
    )
    return result, evidence
