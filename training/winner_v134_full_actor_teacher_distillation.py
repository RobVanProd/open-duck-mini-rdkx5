"""Deterministic full-actor distillation from the V131 robust oracle."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import jax
import jax.numpy as jnp
import numpy as np

from winner_v129_oracle_teacher_distillation import deployed_actions


ACTION_SIZE = 14
HIDDEN_SIZE = 64
OBS_SIZE = 115
BATCH_SIZE = 256
CORRECTION_EPS = 1.0e-7
STD_BACKTRACK_LIMIT = 24
ARMIJO_FRACTION = 1.0e-4


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


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
            raise ValueError(f"incomplete V134 teacher trace: {trace_path}")
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
            base = np.asarray(
                record["policy_base_action"], dtype=np.float32
            )
            correction = target - base
            key = f"{trace_path.name}:{int(record['tick']):03d}"
            rows.append(
                {
                    "key": key,
                    "obs": np.asarray(
                        record["obs_state"], dtype=np.float32
                    ),
                    "previous_action": np.asarray(
                        record["policy_state_input"]["previous_action"][0],
                        dtype=np.float32,
                    ),
                    "h_in": np.asarray(
                        record["policy_state_input"]["h_in"][0],
                        dtype=np.float32,
                    ),
                    "base_action": base,
                    "target_action": target,
                    "target_h_out": np.asarray(
                        record["policy_state_output"]["h_out"][0],
                        dtype=np.float32,
                    ),
                    "corrected": bool(
                        np.max(np.abs(correction)) > CORRECTION_EPS
                    ),
                    "torque_projected": bool(
                        oracle["projected_joint_indices"]
                    ),
                }
            )
    if len(rows) != 4_800 or len(manifest) != 8:
        raise ValueError("V134 teacher dataset must contain 8x600 rows")
    rows.sort(key=lambda row: hashlib.sha256(row["key"].encode()).hexdigest())
    corrected = np.asarray(
        [row["corrected"] for row in rows], dtype=np.bool_
    )
    if int(np.sum(corrected)) != 71:
        raise ValueError(
            f"V134 expected 71 final-action corrections, got {np.sum(corrected)}"
        )
    correction_weight = float(np.sum(~corrected) / np.sum(corrected))
    weights = np.where(corrected, correction_weight, 1.0).astype(np.float32)
    return {
        "obs": np.stack([row["obs"] for row in rows]),
        "previous_action": np.stack(
            [row["previous_action"] for row in rows]
        ),
        "h_in": np.stack([row["h_in"] for row in rows]),
        "base_action": np.stack([row["base_action"] for row in rows]),
        "target_action": np.stack(
            [row["target_action"] for row in rows]
        ),
        "target_h_out": np.stack(
            [row["target_h_out"] for row in rows]
        ),
        "weights": weights,
        "corrected": corrected,
        "torque_projected": np.asarray(
            [row["torque_projected"] for row in rows], dtype=np.bool_
        ),
        "keys": [row["key"] for row in rows],
        "manifest": manifest,
        "correction_weight": correction_weight,
    }


def loss_components(
    network: Any,
    normalizer: Any,
    policy_params: Any,
    batch: dict[str, jax.Array],
    transform: dict[str, Any],
) -> tuple[jax.Array, tuple[jax.Array, jax.Array]]:
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


def freeze_scale_gradients(grads: Any) -> Any:
    updated = dict(grads)
    params = dict(grads["params"])
    params["scale_logits"] = jax.tree_util.tree_map(
        jnp.zeros_like, params["scale_logits"]
    )
    updated["params"] = params
    return updated


def gradient_norm(grads: Any) -> jax.Array:
    leaves = jax.tree_util.tree_leaves(grads)
    return jnp.sqrt(sum(jnp.sum(jnp.square(value)) for value in leaves))


def apply_gradient(
    params: Any,
    grads: Any,
    step_size: float | jax.Array,
) -> Any:
    return jax.tree_util.tree_map(
        lambda value, grad: value - step_size * grad,
        params,
        grads,
    )


def smoke_indices(dataset: dict[str, Any]) -> np.ndarray:
    corrected = np.flatnonzero(dataset["corrected"])
    preservation = np.flatnonzero(~dataset["corrected"])[:185]
    indices = np.concatenate([corrected, preservation])
    if indices.shape != (BATCH_SIZE,):
        raise ValueError("V134 smoke batch must be 71+185 rows")
    return indices
