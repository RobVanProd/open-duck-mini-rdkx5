# Copyright 2026 The Brax Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""V171 reward/cost actor objectives and Euclidean tangent audit.

This module is development-only.  It does not change the deployed policy
graph.  The audit computes the raw reward-descent direction, the dense-cost
gradient, and the minimum Euclidean projection of that reward direction onto
the first-order cost-nonincreasing half-space.
"""

from __future__ import annotations

from typing import Any

from brax.training import types
from brax.training.agents.ppo import networks as ppo_networks
import jax
import jax.numpy as jnp

from playground.common import winner_v127_constrained_ppo_losses as v127_losses


def compute_actor_objective(
    params: v127_losses.PPONetworkParams,
    normalizer_params: Any,
    data: types.Transition,
    rng: jax.Array,
    *,
    objective: str,
    ppo_network: ppo_networks.PPONetworks,
    entropy_cost: float,
    discounting: float,
    reward_scaling: float,
    gae_lambda: float,
    clipping_epsilon: float,
    normalize_advantage: bool,
) -> tuple[jax.Array, dict[str, jax.Array]]:
  """Returns a reward+entropy or conservative cost actor objective.

  The reward and cost advantages are constructed exactly as in V127.  Value
  losses are deliberately absent: this function is used only to audit actor
  gradient geometry.
  """
  if objective not in ('reward', 'cost'):
    raise ValueError(f'unsupported V171 actor objective: {objective}')

  distribution = ppo_network.parametric_action_distribution
  policy_apply = ppo_network.policy_network.apply
  value_apply = ppo_network.value_network.apply
  data = jax.tree_util.tree_map(lambda x: jnp.swapaxes(x, 0, 1), data)
  policy_logits = policy_apply(
      normalizer_params, params.policy, data.observation
  )
  reward_baseline = value_apply(
      normalizer_params, params.value, data.observation
  )
  cost_baseline = value_apply(
      normalizer_params, params.cost_value, data.observation
  )
  terminal_obs = jax.tree_util.tree_map(
      lambda x: x[-1], data.next_observation
  )
  reward_bootstrap = value_apply(
      normalizer_params, params.value, terminal_obs
  )
  cost_bootstrap = value_apply(
      normalizer_params, params.cost_value, terminal_obs
  )

  rewards = data.reward * reward_scaling
  costs = data.extras['state_extras'][
      'winner_v127_dense_torque_exceedance_cost'
  ]
  truncation = data.extras['state_extras']['truncation']
  termination = (1 - data.discount) * (1 - truncation)
  target_log_prob = distribution.log_prob(
      policy_logits, data.extras['policy_extras']['raw_action']
  )
  behavior_log_prob = data.extras['policy_extras']['log_prob']

  _, reward_advantage = v127_losses.compute_gae(
      truncation=truncation,
      termination=termination,
      rewards=rewards,
      values=reward_baseline,
      bootstrap_value=reward_bootstrap,
      lambda_=gae_lambda,
      discount=discounting,
  )
  _, cost_advantage = v127_losses.compute_gae(
      truncation=truncation,
      termination=termination,
      rewards=costs,
      values=cost_baseline,
      bootstrap_value=cost_bootstrap,
      lambda_=gae_lambda,
      discount=1.0,
  )
  if normalize_advantage:
    reward_advantage = (
        reward_advantage - reward_advantage.mean()
    ) / (reward_advantage.std() + 1e-8)
    cost_advantage = (
        cost_advantage - cost_advantage.mean()
    ) / (cost_advantage.std() + 1e-8)

  rho = jnp.exp(target_log_prob - behavior_log_prob)
  if objective == 'reward':
    surrogate_1 = rho * reward_advantage
    surrogate_2 = (
        jnp.clip(rho, 1 - clipping_epsilon, 1 + clipping_epsilon)
        * reward_advantage
    )
    policy_loss = -jnp.mean(jnp.minimum(surrogate_1, surrogate_2))
    entropy = jnp.mean(distribution.entropy(policy_logits, rng))
    loss = policy_loss - entropy_cost * entropy
  else:
    surrogate_1 = rho * cost_advantage
    surrogate_2 = (
        jnp.clip(rho, 1 - clipping_epsilon, 1 + clipping_epsilon)
        * cost_advantage
    )
    # Minimizing the upper surrogate is the cost analogue of PPO's
    # conservative clipped reward objective.
    policy_loss = jnp.mean(jnp.maximum(surrogate_1, surrogate_2))
    entropy = jnp.asarray(0.0, dtype=policy_loss.dtype)
    loss = policy_loss

  return loss, {
      'objective_loss': loss,
      'policy_loss': policy_loss,
      'entropy': entropy,
      'dense_cost_mean': jnp.mean(costs),
  }


def _tree_dot(left, right) -> jax.Array:
  products = [
      jnp.vdot(jnp.asarray(a), jnp.asarray(b))
      for a, b in zip(
          jax.tree_util.tree_leaves(left),
          jax.tree_util.tree_leaves(right),
          strict=True,
      )
  ]
  return sum(products, jnp.asarray(0.0, dtype=jnp.float32))


def tangent_geometry(reward_gradient, cost_gradient) -> dict[str, jax.Array]:
  """Audits the exact Euclidean projection of reward descent.

  With ``d_r=-g_r``, the half-space is ``g_c dot d <= 0``.  If the reward
  descent would increase first-order cost, the returned direction is its
  minimum Euclidean projection onto the boundary.
  """
  reward_descent = jax.tree_util.tree_map(lambda leaf: -leaf, reward_gradient)
  reward_norm_sq = _tree_dot(reward_descent, reward_descent)
  cost_norm_sq = _tree_dot(cost_gradient, cost_gradient)
  before = _tree_dot(cost_gradient, reward_descent)
  cost_nonzero = cost_norm_sq > 0.0
  active = jnp.logical_and(before > 0.0, cost_nonzero)
  coefficient = jnp.where(
      active,
      before / jnp.maximum(cost_norm_sq, jnp.finfo(jnp.float32).tiny),
      0.0,
  )
  projected = jax.tree_util.tree_map(
      lambda direction, gradient: direction - coefficient * gradient,
      reward_descent,
      cost_gradient,
  )
  projected_norm_sq = _tree_dot(projected, projected)
  after = _tree_dot(cost_gradient, projected)
  norm_product = jnp.sqrt(
      jnp.maximum(reward_norm_sq * cost_norm_sq, 0.0)
  )
  cosine = jnp.where(
      norm_product > 0.0,
      _tree_dot(reward_gradient, cost_gradient) / norm_product,
      0.0,
  )
  retention = jnp.where(
      reward_norm_sq > 0.0,
      jnp.sqrt(jnp.maximum(projected_norm_sq, 0.0) / reward_norm_sq),
      0.0,
  )
  return {
      'reward_gradient_norm': jnp.sqrt(jnp.maximum(reward_norm_sq, 0.0)),
      'cost_gradient_norm': jnp.sqrt(jnp.maximum(cost_norm_sq, 0.0)),
      'reward_cost_gradient_cosine': cosine,
      'reward_descent_cost_derivative_before': before,
      'projected_cost_derivative_after': after,
      'projected_reward_direction_retention': retention,
      'projection_active': active.astype(jnp.float32),
      'cost_descent_derivative': -cost_norm_sq,
  }
