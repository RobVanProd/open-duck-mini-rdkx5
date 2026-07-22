"""Training-safe Winner-v24 objective with an exact zero-failure no-op."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

import numpy as np

import winner_v24_symmetric_support_failure as v1
import winner_v24_symmetric_support_failure_v2 as v2


SYMMETRIC_FAILURE_PENALTY = v2.SYMMETRIC_FAILURE_PENALTY
MODIFIED_BATCH_KEYS = v2.MODIFIED_BATCH_KEYS


def apply_training_objective(
    batch: Mapping[str, np.ndarray],
    episodes: Sequence[Mapping[str, Any]],
    values: np.ndarray,
    *,
    gamma: float,
    gae_lambda: float,
) -> tuple[dict[str, np.ndarray], dict[str, Any]]:
    """Apply v2 when failures exist; otherwise preserve the batch bit-exactly."""

    shape = np.asarray(batch.get("rewards")).shape
    if len(shape) != 2 or np.asarray(values).shape != shape:
        raise ValueError("Winner-v24 v3 batch shape changed")
    failure_mask = v1.roll_pitch_failure_mask(episodes, shape=shape)
    count = int(np.sum(failure_mask))
    if count > 0:
        result, evidence = v2.apply_baseline_anchored_objective(
            batch,
            episodes,
            values,
            enabled=True,
            gamma=gamma,
            gae_lambda=gae_lambda,
        )
        evidence["zero_failure_bit_exact_noop"] = False
        return result, evidence
    result = {key: np.asarray(value).copy() for key, value in batch.items()}
    sample_mask = np.asarray(batch["valid_mask"], dtype=np.float32)
    baseline_raw = np.where(
        sample_mask > 0,
        np.asarray(batch["returns"], dtype=np.float32)
        - np.asarray(values, dtype=np.float32),
        np.float32(0.0),
    ).astype(np.float32)
    delta = np.zeros(shape, dtype=np.float32)
    evidence = {
        "enabled": True,
        "anchor": "recorded_baseline_returns_and_rederived_values",
        "roll_pitch_failure_count": 0,
        "roll_pitch_failure_mask_sha256": v1.array_sha256(
            failure_mask.astype(np.uint8)
        ),
        "penalty": float(SYMMETRIC_FAILURE_PENALTY),
        "modified_batch_keys": [],
        "baseline_raw_advantages_sha256": v1.array_sha256(baseline_raw),
        "analytical_terminal_delta_sha256": v1.array_sha256(delta),
        "analytical_terminal_delta_nonzero_count": 0,
        "analytical_terminal_delta_min": 0.0,
        "analytical_terminal_delta_max": 0.0,
        "zero_failure_bit_exact_noop": True,
    }
    return result, evidence
