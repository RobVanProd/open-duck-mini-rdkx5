"""Training-only Winner-v12 calibrator primitives.

The deployable network remains ``winner_v12_decomposed_backend_networks``.
This module owns only the two preregistered training objectives and keeps the
auxiliary predictor, Gaussian scale, and value head out of the export mapping.
It deliberately has no simulator-configuration argument or privileged input.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import jax
import jax.numpy as jnp
import numpy as np

import winner_v12_decomposed_backend_networks as networks


OBS_SIZE = 115
ACTION_SIZE = 14
HIDDEN_SIZE = 64
AUXILIARY_INDICES = np.asarray(
    list(range(0, 6)) + list(range(13, 41)) + list(range(83, 99)),
    dtype=np.int64,
)
ENCODER_AUXILIARY_KEYS = (
    "obs_weight",
    "previous_action_weight",
    "hidden_weight",
    "hidden_bias",
    "auxiliary_hidden_weight",
    "auxiliary_action_weight",
    "auxiliary_bias",
)
DEPLOYABLE_ACTION_KEYS = ("action_weight", "action_bias")
TRAINING_ONLY_STAGE2_KEYS = (
    "training_only_log_std",
    "training_only_value_weight",
    "training_only_value_bias",
)
DEPLOYABLE_CALIBRATOR_KEYS = ENCODER_AUXILIARY_KEYS + DEPLOYABLE_ACTION_KEYS
STAGE1_LEARNING_RATE = 1.0e-4
STAGE2_LEARNING_RATE = 1.0e-4
ADAM_BETA1 = 0.9
ADAM_BETA2 = 0.999
ADAM_EPSILON = 1.0e-8
PPO_GAMMA = 1.0
PPO_GAE_LAMBDA = 0.95
PPO_CLIP_EPSILON = 0.2
PPO_VALUE_COEFFICIENT = 0.5
PPO_ENTROPY_COEFFICIENT = 0.001
LOG_STD_MIN = -5.0
LOG_STD_MAX = 1.0


def _select(
    parameters: Mapping[str, jax.Array], keys: tuple[str, ...]
) -> dict[str, jax.Array]:
    if set(keys) - set(parameters):
        raise KeyError(f"missing parameter keys: {sorted(set(keys) - set(parameters))}")
    return {key: jnp.asarray(parameters[key], dtype=jnp.float32) for key in keys}


def deployable_parameters(parameters: Mapping[str, jax.Array]) -> dict[str, jax.Array]:
    """Return the only mapping permitted to enter the inherited ONNX exporter."""

    return _select(parameters, DEPLOYABLE_CALIBRATOR_KEYS)


def initialize_training_parameters(seed: int = 60720) -> dict[str, jax.Array]:
    parameters = dict(networks.initialize_calibrator_parameters(seed=seed))
    parameters.update(
        {
            "training_only_log_std": jnp.log(
                jnp.asarray(networks.INTERNAL_ACTION_DELTA, dtype=jnp.float32)
                * jnp.float32(0.25)
            ),
            "training_only_value_weight": jnp.zeros((HIDDEN_SIZE,), dtype=jnp.float32),
            "training_only_value_bias": jnp.zeros((), dtype=jnp.float32),
        }
    )
    return parameters


def stage1_parameters(parameters: Mapping[str, jax.Array]) -> dict[str, jax.Array]:
    return _select(parameters, ENCODER_AUXILIARY_KEYS)


def stage2_parameters(parameters: Mapping[str, jax.Array]) -> dict[str, jax.Array]:
    return _select(parameters, DEPLOYABLE_ACTION_KEYS + TRAINING_ONLY_STAGE2_KEYS)


def merge_stage1(
    parameters: Mapping[str, jax.Array], stage1: Mapping[str, jax.Array]
) -> dict[str, jax.Array]:
    if set(stage1) != set(ENCODER_AUXILIARY_KEYS):
        raise ValueError("stage-1 parameter schema changed")
    merged = dict(parameters)
    merged.update(stage1)
    return merged


def merge_stage2(
    parameters: Mapping[str, jax.Array], stage2: Mapping[str, jax.Array]
) -> dict[str, jax.Array]:
    expected = set(DEPLOYABLE_ACTION_KEYS + TRAINING_ONLY_STAGE2_KEYS)
    if set(stage2) != expected:
        raise ValueError("stage-2 parameter schema changed")
    merged = dict(parameters)
    merged.update(stage2)
    return merged


def response_step(
    parameters: Mapping[str, jax.Array],
    observation: jax.Array,
    previous_action: jax.Array,
    h_in: jax.Array,
    realized_action: jax.Array,
) -> tuple[jax.Array, jax.Array]:
    """Return h_out and the training-only next-response prediction."""

    hidden_pre = (
        observation @ parameters["obs_weight"]
        + previous_action @ parameters["previous_action_weight"]
        + h_in @ parameters["hidden_weight"]
        + parameters["hidden_bias"]
    )
    h_out = jnp.tanh(hidden_pre)
    prediction = (
        h_out @ parameters["auxiliary_hidden_weight"]
        + realized_action @ parameters["auxiliary_action_weight"]
        + parameters["auxiliary_bias"]
    )
    return h_out, prediction


def stage1_predictions(
    parameters: Mapping[str, jax.Array],
    observations: jax.Array,
    previous_actions: jax.Array,
    realized_actions: jax.Array,
) -> tuple[jax.Array, jax.Array, jax.Array]:
    """Run full 250-tick BPTT independently over each environment."""

    def run_one(obs: jax.Array, previous: jax.Array, realized: jax.Array):
        def step(h_in: jax.Array, values: tuple[jax.Array, ...]):
            obs_t, previous_t, realized_t = values
            h_out, prediction = response_step(
                parameters, obs_t, previous_t, h_in, realized_t
            )
            return h_out, (h_out, prediction)

        initial = jnp.zeros((HIDDEN_SIZE,), dtype=jnp.float32)
        final_hidden, (hidden, prediction) = jax.lax.scan(
            step, initial, (obs, previous, realized)
        )
        return final_hidden, hidden, prediction

    return jax.vmap(run_one)(observations, previous_actions, realized_actions)


def stage1_loss(
    parameters: Mapping[str, jax.Array],
    batch: Mapping[str, jax.Array],
    target_mean: jax.Array,
    target_std: jax.Array,
) -> jax.Array:
    _, _, predictions = stage1_predictions(
        parameters,
        batch["observations"],
        batch["previous_actions"],
        batch["realized_actions"],
    )
    mask = batch["valid_mask"][..., None]
    denominator = jnp.maximum(
        jnp.sum(mask) * jnp.float32(predictions.shape[-1]), jnp.float32(1.0)
    )
    # target_mean is used by the exact normalization transform even though it
    # cancels algebraically when both prediction and target share the mean.
    prediction_normalized = (predictions - target_mean) / target_std
    target_normalized = (batch["targets"] - target_mean) / target_std
    normalized_error = prediction_normalized - target_normalized
    return jnp.sum(jnp.square(normalized_error) * mask) / denominator


def clamp_stage2_parameters(
    parameters: Mapping[str, jax.Array],
) -> dict[str, jax.Array]:
    """Apply the only post-optimizer constraint in the frozen CPU smoke."""

    updated = dict(parameters)
    updated["training_only_log_std"] = jnp.clip(
        updated["training_only_log_std"],
        jnp.float32(LOG_STD_MIN),
        jnp.float32(LOG_STD_MAX),
    )
    return updated


def bounded_action(raw_action: jax.Array, previous_action: jax.Array) -> jax.Array:
    delta = jnp.asarray(networks.INTERNAL_ACTION_DELTA, dtype=jnp.float32)
    absolute = jnp.clip(raw_action, -1.0, 1.0)
    lower = jnp.maximum(previous_action - delta, -1.0)
    upper = jnp.minimum(previous_action + delta, 1.0)
    return jnp.maximum(jnp.minimum(absolute, upper), lower)


def stage2_mean_value(
    parameters: Mapping[str, jax.Array], hidden: jax.Array
) -> tuple[jax.Array, jax.Array]:
    mean = jnp.tanh(hidden @ parameters["action_weight"] + parameters["action_bias"])
    value = (
        hidden @ parameters["training_only_value_weight"]
        + parameters["training_only_value_bias"]
    )
    return mean, value


def diagonal_gaussian_log_probability(
    sample: jax.Array, mean: jax.Array, log_std: jax.Array
) -> jax.Array:
    inverse_std = jnp.exp(-log_std)
    normalized = (sample - mean) * inverse_std
    return -jnp.sum(
        jnp.float32(0.5) * jnp.square(normalized)
        + log_std
        + jnp.float32(0.5 * np.log(2.0 * np.pi)),
        axis=-1,
    )


def diagonal_gaussian_entropy(log_std: jax.Array) -> jax.Array:
    return jnp.sum(log_std + jnp.float32(0.5 * np.log(2.0 * np.pi * np.e)), axis=-1)


def sample_stage2_action(
    parameters: Mapping[str, jax.Array],
    hidden: jax.Array,
    previous_action: jax.Array,
    epsilon: jax.Array,
) -> tuple[jax.Array, jax.Array, jax.Array, jax.Array]:
    mean, value = stage2_mean_value(parameters, hidden)
    log_std = parameters["training_only_log_std"]
    raw_sample = mean + jnp.exp(log_std) * epsilon
    action = bounded_action(raw_sample, previous_action)
    log_probability = diagonal_gaussian_log_probability(raw_sample, mean, log_std)
    return action, raw_sample, log_probability, value


def stage2_ppo_loss(
    parameters: Mapping[str, jax.Array],
    batch: Mapping[str, jax.Array],
    *,
    clip_epsilon: float,
    value_coefficient: float,
    entropy_coefficient: float,
) -> tuple[jax.Array, dict[str, jax.Array]]:
    mean, value = stage2_mean_value(parameters, batch["hidden"])
    log_std = parameters["training_only_log_std"]
    log_probability = diagonal_gaussian_log_probability(
        batch["raw_samples"], mean, log_std
    )
    ratio = jnp.exp(log_probability - batch["old_log_probability"])
    clipped_ratio = jnp.clip(
        ratio, jnp.float32(1.0 - clip_epsilon), jnp.float32(1.0 + clip_epsilon)
    )
    surrogate = jnp.minimum(
        ratio * batch["advantages"], clipped_ratio * batch["advantages"]
    )
    mask = batch["valid_mask"]
    denominator = jnp.maximum(jnp.sum(mask), jnp.float32(1.0))
    policy_loss = -jnp.sum(surrogate * mask) / denominator
    value_loss = (
        jnp.float32(0.5)
        * jnp.sum(jnp.square(value - batch["returns"]) * mask)
        / denominator
    )
    entropy = diagonal_gaussian_entropy(log_std)
    entropy_mean = jnp.sum(entropy * mask) / denominator
    total = (
        policy_loss
        + jnp.float32(value_coefficient) * value_loss
        - jnp.float32(entropy_coefficient) * entropy_mean
    )
    return total, {
        "policy_loss": policy_loss,
        "value_loss": value_loss,
        "entropy": entropy_mean,
        "ratio_min": jnp.min(jnp.where(mask > 0, ratio, jnp.inf)),
        "ratio_max": jnp.max(jnp.where(mask > 0, ratio, -jnp.inf)),
    }


def adam_initialize(parameters: Mapping[str, jax.Array]) -> dict[str, Any]:
    return {
        "count": jnp.asarray(0, dtype=jnp.int32),
        "m": jax.tree_util.tree_map(jnp.zeros_like, parameters),
        "v": jax.tree_util.tree_map(jnp.zeros_like, parameters),
    }


def adam_step(
    parameters: Mapping[str, jax.Array],
    gradients: Mapping[str, jax.Array],
    state: Mapping[str, Any],
    *,
    learning_rate: float,
    beta1: float,
    beta2: float,
    epsilon: float,
) -> tuple[dict[str, jax.Array], dict[str, Any]]:
    count = state["count"] + jnp.asarray(1, dtype=jnp.int32)
    m = jax.tree_util.tree_map(
        lambda old, grad: jnp.float32(beta1) * old + jnp.float32(1.0 - beta1) * grad,
        state["m"],
        gradients,
    )
    v = jax.tree_util.tree_map(
        lambda old, grad: (
            jnp.float32(beta2) * old + jnp.float32(1.0 - beta2) * jnp.square(grad)
        ),
        state["v"],
        gradients,
    )
    correction1 = jnp.float32(1.0) - jnp.float32(beta1) ** count
    correction2 = jnp.float32(1.0) - jnp.float32(beta2) ** count
    updated = jax.tree_util.tree_map(
        lambda value, first, second: (
            value
            - jnp.float32(learning_rate)
            * (first / correction1)
            / (jnp.sqrt(second / correction2) + jnp.float32(epsilon))
        ),
        parameters,
        m,
        v,
    )
    return updated, {"count": count, "m": m, "v": v}


def finite_tree(value: Any) -> bool:
    return all(
        bool(np.all(np.isfinite(np.asarray(leaf))))
        for leaf in jax.tree_util.tree_leaves(value)
    )


def leaf_max_abs_delta(
    before: Mapping[str, jax.Array], after: Mapping[str, jax.Array]
) -> dict[str, float]:
    if set(before) != set(after):
        raise ValueError("parameter schema changed")
    return {
        key: float(np.max(np.abs(np.asarray(after[key]) - np.asarray(before[key]))))
        for key in sorted(before)
    }
