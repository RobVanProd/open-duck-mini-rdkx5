"""Sequence-level recurrent-adapter distillation from the V131 teacher."""

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
TRACE_TICKS = 600
STARTUP_TICKS = 32
TRACE_COUNT = 8
CORRECTION_EPS = 1.0e-7
BACKTRACK_LIMIT = 24
ARMIJO_FRACTION = 1.0e-4
TRAINABLE_MODULES = frozenset(
    {
        "adapter_hidden_bias",
        "adapter_hidden_projection",
        "adapter_location",
        "adapter_obs_projection",
    }
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_teacher_sequences(run_root: Path) -> dict[str, Any]:
    traces = []
    manifest = []
    for trace_path in sorted(run_root.resolve().glob("traces/*_final_*.jsonl")):
        records = [
            json.loads(line)
            for line in trace_path.read_text(encoding="utf-8").splitlines()
            if line
        ]
        if len(records) != TRACE_TICKS:
            raise ValueError(f"incomplete V137 teacher trace: {trace_path}")
        obs = []
        base = []
        target = []
        for record in records:
            obs.append(np.asarray(record["obs_state"], dtype=np.float32))
            base.append(
                np.asarray(record["policy_base_action"], dtype=np.float32)
            )
            target.append(
                np.asarray(
                    record["exact_torque_oracle"]["final_action"],
                    dtype=np.float32,
                )
            )
        base_array = np.stack(base)
        target_array = np.stack(target)
        corrected = (
            np.max(np.abs(target_array - base_array), axis=1)
            > CORRECTION_EPS
        )
        traces.append(
            {
                "obs": np.stack(obs),
                "base_action": base_array,
                "target_action": target_array,
                "corrected": corrected,
            }
        )
        manifest.append(
            {
                "name": trace_path.name,
                "rows": len(records),
                "sha256": _sha256(trace_path),
                "corrected_rows": int(np.sum(corrected)),
                "startup_corrected_rows": int(
                    np.sum(corrected[:STARTUP_TICKS])
                ),
            }
        )
    if len(traces) != TRACE_COUNT:
        raise ValueError("V137 requires exactly eight teacher traces")
    dataset = {
        key: np.stack([trace[key] for trace in traces])
        for key in ("obs", "base_action", "target_action", "corrected")
    }
    if dataset["obs"].shape != (TRACE_COUNT, TRACE_TICKS, OBS_SIZE):
        raise ValueError("V137 observation sequence shape changed")
    if int(np.sum(dataset["corrected"])) != 71:
        raise ValueError("V137 expected 71 full teacher corrections")
    if int(np.sum(dataset["corrected"][:, :STARTUP_TICKS])) != 15:
        raise ValueError("V137 expected 15 startup teacher corrections")
    startup_corrected = dataset["corrected"][:, :STARTUP_TICKS]
    startup_weight = float(
        np.sum(~startup_corrected) / np.sum(startup_corrected)
    )
    dataset["startup_weights"] = np.where(
        startup_corrected, startup_weight, 1.0
    ).astype(np.float32)
    dataset["startup_correction_weight"] = startup_weight
    dataset["manifest"] = manifest
    return dataset


def sequence_outputs(
    network: Any,
    normalizer: Any,
    policy_params: Any,
    obs: jax.Array,
    transform: dict[str, Any],
) -> tuple[jax.Array, jax.Array]:
    batch = obs.shape[0]
    initial = (
        jnp.zeros((batch, ACTION_SIZE), dtype=jnp.float32),
        jnp.zeros((batch, HIDDEN_SIZE), dtype=jnp.float32),
    )

    def step(carry, obs_t):
        previous_action, hidden = carry
        action, hidden_out = deployed_actions(
            network,
            normalizer,
            policy_params,
            obs_t,
            previous_action,
            hidden,
            transform,
        )
        return (action, hidden_out), (action, hidden_out)

    (_, _), (action_t, hidden_t) = jax.lax.scan(
        step,
        initial,
        jnp.swapaxes(obs, 0, 1),
    )
    return jnp.swapaxes(action_t, 0, 1), jnp.swapaxes(hidden_t, 0, 1)


def startup_loss_components(
    network: Any,
    normalizer: Any,
    policy_params: Any,
    obs: jax.Array,
    target_action: jax.Array,
    weights: jax.Array,
    transform: dict[str, Any],
) -> tuple[jax.Array, tuple[jax.Array, jax.Array]]:
    action, hidden = sequence_outputs(
        network, normalizer, policy_params, obs, transform
    )
    row_mse = jnp.mean(jnp.square(action - target_action), axis=-1)
    action_loss = jnp.sum(row_mse * weights) / jnp.sum(weights)
    hidden_energy = jnp.mean(jnp.square(hidden))
    return action_loss, (action_loss, hidden_energy)


def freeze_nonrecurrent_adapter_gradients(grads: Any) -> Any:
    updated = dict(grads)
    params = {}
    for name, value in grads["params"].items():
        params[name] = (
            value
            if name in TRAINABLE_MODULES
            else jax.tree_util.tree_map(jnp.zeros_like, value)
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
