"""T147 command-group risk PPO loss for the composed Playground.

This is the installed Brax 0.14.2 PPO loss with one deliberate actor-only
change: the batch-average clipped surrogate is replaced by the maximum of the
three per-command-group surrogate losses.  Reward GAE, global advantage
normalization, value loss, entropy, KL metrics, optimizer, and policy ABI are
unchanged.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any, Tuple

from brax.training import types
from brax.training.agents.ppo import losses as ppo_losses
from brax.training.agents.ppo import networks as ppo_networks
import jax
import jax.numpy as jnp


COMMAND_ANCHORS = jnp.asarray([0.074, 0.077, 0.080], dtype=jnp.float32)
COMMAND_BOUNDARIES = jnp.asarray([0.0755, 0.0785], dtype=jnp.float32)
COMMAND_OBSERVATION_INDEX = 6


def command_group_ids(command_x: jax.Array) -> jax.Array:
    """Map command x to the nearest frozen behavior-gate anchor."""
    value = jnp.asarray(command_x, dtype=jnp.float32)
    return jnp.where(
        value < COMMAND_BOUNDARIES[0],
        0,
        jnp.where(value < COMMAND_BOUNDARIES[1], 1, 2),
    ).astype(jnp.int32)


def grouped_policy_loss(
    clipped_surrogate: jax.Array,
    command_x: jax.Array,
) -> tuple[jax.Array, dict[str, jax.Array]]:
    """Return the worst present command group's PPO policy loss."""
    surrogate = jnp.asarray(clipped_surrogate, dtype=jnp.float32)
    groups = command_group_ids(command_x)
    if surrogate.shape != groups.shape:
        raise ValueError(
            f"T147 surrogate/group shape mismatch: {surrogate.shape}, "
            f"{groups.shape}"
        )
    flat_surrogate = surrogate.reshape(-1)
    flat_groups = groups.reshape(-1)
    losses = []
    counts = []
    for group_id in range(3):
        mask = (flat_groups == group_id).astype(jnp.float32)
        count = jnp.sum(mask)
        mean = jnp.sum(mask * flat_surrogate) / jnp.maximum(count, 1.0)
        losses.append(jnp.where(count > 0.0, -mean, -jnp.inf))
        counts.append(count)
    group_losses = jnp.stack(losses)
    group_counts = jnp.stack(counts)
    selected = jnp.argmax(group_losses)
    return group_losses[selected], {
        "group_losses": group_losses,
        "group_counts": group_counts,
        "selected_group": selected,
        "all_groups_present": jnp.all(group_counts > 0.0),
    }


def compute_ppo_loss(
    params: ppo_losses.PPONetworkParams,
    normalizer_params: Any,
    data: types.Transition,
    rng: jnp.ndarray,
    ppo_network: ppo_networks.PPONetworks,
    entropy_cost: float = 1e-4,
    discounting: float = 0.9,
    reward_scaling: float = 1.0,
    gae_lambda: float = 0.95,
    clipping_epsilon: float = 0.3,
    normalize_advantage: bool = True,
    vf_coefficient: float = 0.5,
    clipping_epsilon_value: float | None = None,
    use_distributional_critic: bool = False,
) -> Tuple[jnp.ndarray, types.Metrics]:
    """Compute PPO loss with T147's actor-only command-group risk."""
    parametric_action_distribution = (
        ppo_network.parametric_action_distribution
    )
    policy_apply = ppo_network.policy_network.apply
    value_apply = ppo_network.value_network.apply

    # Brax collects [B, T]; the frozen PPO loss operates on [T, B].
    data = jax.tree_util.tree_map(lambda x: jnp.swapaxes(x, 0, 1), data)
    policy_logits = policy_apply(
        normalizer_params, params.policy, data.observation
    )

    if use_distributional_critic:
        baseline, baseline_quantiles = value_apply(
            normalizer_params, params.value, data.observation
        )
        terminal_obs = jax.tree_util.tree_map(
            lambda x: x[-1], data.next_observation
        )
        bootstrap_value, _ = value_apply(
            normalizer_params, params.value, terminal_obs
        )
    else:
        baseline = value_apply(
            normalizer_params, params.value, data.observation
        )
        terminal_obs = jax.tree_util.tree_map(
            lambda x: x[-1], data.next_observation
        )
        bootstrap_value = value_apply(
            normalizer_params, params.value, terminal_obs
        )
        baseline_quantiles = None

    rewards = data.reward * reward_scaling
    truncation = data.extras["state_extras"]["truncation"]
    termination = (1 - data.discount) * (1 - truncation)

    target_action_log_probs = parametric_action_distribution.log_prob(
        policy_logits, data.extras["policy_extras"]["raw_action"]
    )
    behaviour_action_log_probs = data.extras["policy_extras"]["log_prob"]

    vs, advantages = ppo_losses.compute_gae(
        truncation=truncation,
        termination=termination,
        rewards=rewards,
        values=baseline,
        bootstrap_value=bootstrap_value,
        lambda_=gae_lambda,
        discount=discounting,
    )
    gae_returns = jax.lax.stop_gradient(
        jnp.add(advantages, jax.lax.stop_gradient(baseline))
    )
    if normalize_advantage:
        advantages = (advantages - advantages.mean()) / (
            advantages.std() + 1e-8
        )
    rho_s = jnp.exp(
        target_action_log_probs - behaviour_action_log_probs
    )

    surrogate_loss1 = rho_s * advantages
    surrogate_loss2 = (
        jnp.clip(
            rho_s,
            1 - clipping_epsilon,
            1 + clipping_epsilon,
        )
        * advantages
    )
    clipped_surrogate = jnp.minimum(surrogate_loss1, surrogate_loss2)
    command_x = data.observation["state"][
        ..., COMMAND_OBSERVATION_INDEX
    ]
    policy_loss, group_metrics = grouped_policy_loss(
        clipped_surrogate,
        command_x,
    )

    if use_distributional_critic:
        v_loss = (
            ppo_losses.quantile_huber_loss(
                baseline_quantiles,
                gae_returns,
                kappa=clipping_epsilon_value,
            )
            * vf_coefficient
        )
    else:
        v_error = vs - baseline
        v_loss = v_error * v_error
        if clipping_epsilon_value is not None:
            old_values = data.extras["policy_extras"]["value"]
            v_clipped = old_values + jnp.clip(
                baseline - old_values,
                -clipping_epsilon_value,
                clipping_epsilon_value,
            )
            v_loss_clipped = (vs - v_clipped) ** 2
            v_loss = jnp.maximum(v_loss, v_loss_clipped)
        v_loss = jnp.mean(v_loss) * 0.5 * vf_coefficient

    entropy = jnp.mean(
        parametric_action_distribution.entropy(policy_logits, rng)
    )
    entropy_loss = entropy_cost * -entropy
    total_loss = policy_loss + v_loss + entropy_loss

    new_dist = parametric_action_distribution.create_dist(policy_logits)
    if hasattr(new_dist, "kl_divergence"):
        old_dist_params = data.extras["policy_extras"][
            "distribution_params"
        ]
        old_dist = parametric_action_distribution.create_dist(
            old_dist_params
        )
        kl = jnp.mean(new_dist.kl_divergence(old_dist))
    else:
        kl = jnp.array(0.0)

    policy_dist_mean_std = jnp.mean(new_dist.scale)
    policy_dist_max_std = jnp.max(new_dist.scale)
    policy_dist_min_std = jnp.min(new_dist.scale)
    policy_dist_mean_loc = jnp.mean(new_dist.loc)
    policy_dist_max_loc = jnp.max(new_dist.loc)
    policy_dist_min_loc = jnp.min(new_dist.loc)

    return total_loss, {
        "total_loss": total_loss,
        "policy_loss": policy_loss,
        "v_loss": v_loss,
        "entropy_loss": entropy_loss,
        "kl_mean": kl,
        "policy_dist_mean_std": policy_dist_mean_std,
        "policy_dist_max_std": policy_dist_max_std,
        "policy_dist_min_std": policy_dist_min_std,
        "policy_dist_mean_loc": policy_dist_mean_loc,
        "policy_dist_max_loc": policy_dist_max_loc,
        "policy_dist_min_loc": policy_dist_min_loc,
        "command_group_074_loss": group_metrics["group_losses"][0],
        "command_group_077_loss": group_metrics["group_losses"][1],
        "command_group_080_loss": group_metrics["group_losses"][2],
        "command_group_074_count": group_metrics["group_counts"][0],
        "command_group_077_count": group_metrics["group_counts"][1],
        "command_group_080_count": group_metrics["group_counts"][2],
        "command_group_selected": group_metrics["selected_group"],
        "command_groups_all_present": group_metrics[
            "all_groups_present"
        ].astype(jnp.float32),
    }


@contextmanager
def command_group_risk_loss() -> Iterator[None]:
    """Install the T147 actor loss only for the enclosed PPO train call."""
    original = ppo_losses.compute_ppo_loss
    if original is compute_ppo_loss:
        raise RuntimeError("T147 command-group loss is re-entrant")
    print(
        "T147_COMMAND_GROUP_RISK="
        "anchors=.074,.077,.080,boundaries=.0755,.0785,"
        "actor_loss=max_group_clipped_surrogate,"
        "advantage=global,critic=unchanged,entropy=unchanged,"
        "optimizer=unchanged,abi=unchanged"
    )
    ppo_losses.compute_ppo_loss = compute_ppo_loss
    try:
        yield
    finally:
        ppo_losses.compute_ppo_loss = original
