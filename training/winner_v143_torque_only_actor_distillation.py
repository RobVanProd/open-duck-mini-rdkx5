"""Torque-only nonlinear actor distillation from the V131 oracle traces.

V134 treated every final-action change as a correction.  The V142
attribution showed that this moved the closed-loop load from the labeled
startup knee to an unlabeled mature ankle.  V143 therefore changes the
teacher target only on rows where the exact oracle had to project torque;
all other rows explicitly target the frozen source action.
"""

from __future__ import annotations

from typing import Any

import numpy as np

import winner_v134_full_actor_teacher_distillation as v134


ACTION_SIZE = v134.ACTION_SIZE
HIDDEN_SIZE = v134.HIDDEN_SIZE
OBS_SIZE = v134.OBS_SIZE
BATCH_SIZE = v134.BATCH_SIZE
STD_BACKTRACK_LIMIT = v134.STD_BACKTRACK_LIMIT
ARMIJO_FRACTION = v134.ARMIJO_FRACTION

loss_components = v134.loss_components
freeze_scale_gradients = v134.freeze_scale_gradients
gradient_norm = v134.gradient_norm
apply_gradient = v134.apply_gradient
deployed_actions = v134.deployed_actions


def load_teacher_dataset(run_root) -> dict[str, Any]:
    """Return the V134 dataset with torque-only targets and class balance."""
    dataset = v134.load_teacher_dataset(run_root)
    torque = np.asarray(dataset["torque_projected"], dtype=np.bool_)
    if int(np.sum(torque)) != 17:
        raise ValueError("V143 requires exactly 17 torque-projected rows")
    targets = np.where(
        torque[:, None],
        dataset["target_action"],
        dataset["base_action"],
    ).astype(np.float32)
    correction_weight = float(np.sum(~torque) / np.sum(torque))
    weights = np.where(torque, correction_weight, 1.0).astype(np.float32)
    return {
        **dataset,
        "target_action": targets,
        "weights": weights,
        "corrected": torque.copy(),
        "correction_weight": correction_weight,
        "supreme_only_reset_to_source": np.logical_and(
            dataset["corrected"], ~torque
        ),
    }


def smoke_indices(dataset: dict[str, Any]) -> np.ndarray:
    """Use all torque rows plus a deterministic SHA-sorted preservation set."""
    corrected = np.flatnonzero(dataset["corrected"])
    preservation = np.flatnonzero(~dataset["corrected"])[:239]
    indices = np.concatenate([corrected, preservation])
    if indices.shape != (BATCH_SIZE,):
        raise ValueError("V143 smoke batch must be 17+239 rows")
    return indices
