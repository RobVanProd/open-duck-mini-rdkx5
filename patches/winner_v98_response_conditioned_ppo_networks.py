"""Protected reference-residual PPO actor with automatic-response conditioning."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from brax.training import distribution
from brax.training import networks as brax_networks
from brax.training import types
from brax.training.agents.ppo import networks as ppo_networks
import flax
from flax import linen
import jax
import jax.numpy as jnp
import numpy as np


OBS_SIZE = 115
ACTION_SIZE = 14
HIDDEN_SIZE = 64
REFERENCE_CLIP = np.float32(1.0 - 1.0e-5)
ADAPTER_MAX_NORMALIZED = np.float32(0.25)
HIDDEN_OBSERVATION_KEY = "policy_hidden"
CONTEXT_OBSERVATION_KEY = "calibration_context"
PREVIOUS_ACTION_OBSERVATION_KEY = "policy_previous_action"

MAX_ACTION_DELTA = np.asarray(
    [
        0.41919997334480286,
        0.41919997334480286,
        0.11999999731779099,
        0.11999999731779099,
        0.11999999731779099,
        0.41919997334480286,
        0.41919997334480286,
        0.41919997334480286,
        0.41919997334480286,
        0.41919997334480286,
        0.41919997334480286,
        0.09999999403953552,
        0.07999999821186066,
        0.09999999403953552,
    ],
    dtype=np.float32,
)
GUARD_HOME = np.asarray(
    [
        0.002,
        0.053,
        -0.630,
        1.368,
        -0.784,
        0.0,
        0.0,
        0.0,
        0.0,
        -0.003,
        -0.065,
        0.635,
        1.379,
        -0.796,
    ],
    dtype=np.float32,
)
GUARD_MARGIN = np.asarray(
    [1.0e6, 1.0e6, 0.20, 0.20, 0.20, 1.0e6, 1.0e6, 1.0e6, 1.0e6, 1.0e6, 1.0e6, 0.20, 0.20, 0.20],
    dtype=np.float32,
)
GUARD_PITCH_MASK = np.asarray(
    [False, False, True, True, True, False, False, False, False, False, False, True, True, True],
    dtype=np.bool_,
)
GUARD_JOINT_OBS_INDICES = np.arange(13, 27, dtype=np.int32)
GUARD_ACTION_SCALE = np.float32(0.25)
DEADBAND_COMMAND_INDEX = 6
DEADBAND_ABS_LIMIT = np.float32(0.01)


def graph_action_boundary(
    proposed_action: jax.Array,
    raw_observation: jax.Array,
    previous_action: jax.Array,
) -> jax.Array:
    """Apply the selected graph's absolute/rate/guard/deadband hierarchy."""

    proposed = jnp.clip(proposed_action, -1.0, 1.0)
    maximum_delta = jnp.asarray(MAX_ACTION_DELTA)
    lower = jnp.maximum(previous_action - maximum_delta, -1.0)
    upper = jnp.minimum(previous_action + maximum_delta, 1.0)
    rate_bounded = jnp.maximum(jnp.minimum(proposed, upper), lower)
    home = jnp.asarray(GUARD_HOME)
    margin = jnp.asarray(GUARD_MARGIN)
    actual_target = home + jnp.take(
        raw_observation, jnp.asarray(GUARD_JOINT_OBS_INDICES), axis=-1
    )
    desired_target = home + rate_bounded * jnp.float32(GUARD_ACTION_SCALE)
    target = jnp.minimum(
        jnp.maximum(desired_target, actual_target - margin), actual_target + margin
    )
    pitch_action = jnp.clip(
        (target - home) / jnp.float32(GUARD_ACTION_SCALE), -1.0, 1.0
    )
    guarded = jnp.where(jnp.asarray(GUARD_PITCH_MASK), pitch_action, rate_bounded)
    zero_command = (
        jnp.abs(raw_observation[..., DEADBAND_COMMAND_INDEX])
        <= jnp.float32(DEADBAND_ABS_LIMIT)
    )
    return jnp.where(zero_command[..., None], jnp.zeros_like(guarded), guarded)


class ResponseConditionedPolicy(linen.Module):
    """Frozen selected actor plus the exact Winner-v96 recurrent adapter."""

    action_size: int
    hidden_layer_sizes: Sequence[int]
    recurrent_hidden_size: int

    @linen.compact
    def __call__(
        self,
        raw_observation: jax.Array,
        previous_action: jax.Array,
        hidden_in: jax.Array,
        calibration_context: jax.Array,
    ) -> tuple[jax.Array, jax.Array, jax.Array]:
        protected_obs_mean = self.param(
            "protected_obs_mean", jax.nn.initializers.zeros, (OBS_SIZE,)
        )
        protected_obs_std = self.param(
            "protected_obs_std", jax.nn.initializers.ones, (OBS_SIZE,)
        )
        normalized_observation = (
            raw_observation - protected_obs_mean
        ) / protected_obs_std
        base_hidden = brax_networks.MLP(
            layer_sizes=list(self.hidden_layer_sizes),
            activation=linen.swish,
            activate_final=True,
            name="residual_trunk",
        )(normalized_observation)
        base_residual_location = linen.Dense(
            self.action_size,
            kernel_init=jax.nn.initializers.zeros,
            bias_init=jax.nn.initializers.zeros,
            name="residual_location",
        )(base_hidden)
        scale_logits = linen.Dense(self.action_size, name="scale_logits")(base_hidden)
        base_residual_location = jax.lax.stop_gradient(base_residual_location)
        scale_logits = jax.lax.stop_gradient(scale_logits)
        reference_action = raw_observation[..., -self.action_size :]
        reference_location = jnp.arctanh(
            jnp.clip(reference_action, -REFERENCE_CLIP, REFERENCE_CLIP)
        )
        base_raw_action = jnp.tanh(reference_location + base_residual_location)
        protected_action = graph_action_boundary(
            base_raw_action, raw_observation, previous_action
        )

        obs_weight = self.param(
            "adapter_obs_weight",
            jax.nn.initializers.zeros,
            (OBS_SIZE, self.recurrent_hidden_size),
        )
        previous_weight = self.param(
            "adapter_previous_action_weight",
            jax.nn.initializers.zeros,
            (self.action_size, self.recurrent_hidden_size),
        )
        hidden_weight = self.param(
            "adapter_hidden_weight",
            jax.nn.initializers.zeros,
            (self.recurrent_hidden_size, self.recurrent_hidden_size),
        )
        context_hidden_weight = self.param(
            "adapter_context_hidden_weight",
            jax.nn.initializers.zeros,
            (self.recurrent_hidden_size, self.recurrent_hidden_size),
        )
        hidden_bias = self.param(
            "adapter_hidden_bias",
            jax.nn.initializers.zeros,
            (self.recurrent_hidden_size,),
        )
        hidden_out = jnp.tanh(
            raw_observation @ obs_weight
            + previous_action @ previous_weight
            + hidden_in @ hidden_weight
            + calibration_context @ context_hidden_weight
            + hidden_bias
        )
        hidden_action_weight = self.param(
            "adapter_hidden_action_weight",
            jax.nn.initializers.zeros,
            (self.recurrent_hidden_size, self.action_size),
        )
        context_action_weight = self.param(
            "adapter_context_action_weight",
            jax.nn.initializers.zeros,
            (self.recurrent_hidden_size, self.action_size),
        )
        action_bias = self.param(
            "adapter_action_bias",
            jax.nn.initializers.zeros,
            (self.action_size,),
        )
        adapter_delta = jnp.tanh(
            hidden_out @ hidden_action_weight
            + calibration_context @ context_action_weight
            + action_bias
        ) * jnp.float32(ADAPTER_MAX_NORMALIZED)
        final_action = graph_action_boundary(
            protected_action + adapter_delta, raw_observation, previous_action
        )
        final_location = jnp.arctanh(
            jnp.clip(final_action, -REFERENCE_CLIP, REFERENCE_CLIP)
        )
        return (
            jnp.concatenate([final_location, scale_logits], axis=-1),
            hidden_out,
            final_action,
        )


@flax.struct.dataclass
class ResponseConditionedPolicyNetwork:
    init: object
    apply: object
    apply_with_state: object
    apply_action_with_state: object


def _obs_size(observation_size: types.ObservationSize, key: str) -> int:
    value = observation_size[key] if isinstance(observation_size, Mapping) else observation_size
    return int(jax.tree_util.tree_flatten(value)[0][-1])


def make_response_conditioned_ppo_networks(
    observation_size: types.ObservationSize,
    action_size: int,
    preprocess_observations_fn: types.PreprocessObservationFn = types.identity_observation_preprocessor,
    policy_hidden_layer_sizes: Sequence[int] = (512, 256, 128),
    value_hidden_layer_sizes: Sequence[int] = (512, 256, 128),
    policy_obs_key: str = "state",
    value_obs_key: str = "privileged_state",
    recurrent_hidden_size: int = HIDDEN_SIZE,
    **kwargs,
) -> ppo_networks.PPONetworks:
    if not isinstance(observation_size, Mapping):
        raise ValueError("response-conditioned policy requires mapping observations")
    state_size = _obs_size(observation_size, policy_obs_key)
    if state_size != OBS_SIZE or action_size != ACTION_SIZE:
        raise ValueError("response-conditioned 115x14 contract changed")
    expected_extras = {
        HIDDEN_OBSERVATION_KEY: HIDDEN_SIZE,
        CONTEXT_OBSERVATION_KEY: HIDDEN_SIZE,
        PREVIOUS_ACTION_OBSERVATION_KEY: ACTION_SIZE,
    }
    for key, expected in expected_extras.items():
        if _obs_size(observation_size, key) != expected:
            raise ValueError(f"response-conditioned observation key changed: {key}")
    base = ppo_networks.make_ppo_networks(
        observation_size=observation_size,
        action_size=action_size,
        preprocess_observations_fn=preprocess_observations_fn,
        policy_hidden_layer_sizes=policy_hidden_layer_sizes,
        value_hidden_layer_sizes=value_hidden_layer_sizes,
        policy_obs_key=policy_obs_key,
        value_obs_key=value_obs_key,
        **kwargs,
    )
    action_distribution = distribution.NormalTanhDistribution(event_size=action_size)
    module = ResponseConditionedPolicy(
        action_size=action_size,
        hidden_layer_sizes=policy_hidden_layer_sizes,
        recurrent_hidden_size=recurrent_hidden_size,
    )

    def init(key: types.PRNGKey):
        return module.init(
            key,
            jnp.zeros((1, state_size), dtype=jnp.float32),
            jnp.zeros((1, action_size), dtype=jnp.float32),
            jnp.zeros((1, recurrent_hidden_size), dtype=jnp.float32),
            jnp.zeros((1, recurrent_hidden_size), dtype=jnp.float32),
        )

    def apply_with_state(processor_params, policy_params, obs):
        if not isinstance(obs, Mapping):
            raise ValueError("response-conditioned policy requires mapping observation")
        missing = set(expected_extras) - set(obs)
        if missing:
            raise ValueError(f"response-conditioned observation missing: {sorted(missing)}")
        raw = obs[policy_obs_key]
        logits, hidden_out, _ = module.apply(
            policy_params,
            raw,
            obs[PREVIOUS_ACTION_OBSERVATION_KEY],
            obs[HIDDEN_OBSERVATION_KEY],
            obs[CONTEXT_OBSERVATION_KEY],
        )
        return logits, hidden_out

    def apply_action_with_state(processor_params, policy_params, obs):
        if not isinstance(obs, Mapping):
            raise ValueError("response-conditioned policy requires mapping observation")
        missing = set(expected_extras) - set(obs)
        if missing:
            raise ValueError(f"response-conditioned observation missing: {sorted(missing)}")
        _, hidden_out, final_action = module.apply(
            policy_params,
            obs[policy_obs_key],
            obs[PREVIOUS_ACTION_OBSERVATION_KEY],
            obs[HIDDEN_OBSERVATION_KEY],
            obs[CONTEXT_OBSERVATION_KEY],
        )
        return final_action, hidden_out

    def apply(processor_params, policy_params, obs):
        logits, _ = apply_with_state(processor_params, policy_params, obs)
        return logits

    policy_network = ResponseConditionedPolicyNetwork(
        init=init,
        apply=apply,
        apply_with_state=apply_with_state,
        apply_action_with_state=apply_action_with_state,
    )
    return ppo_networks.PPONetworks(
        policy_network=policy_network,
        value_network=base.value_network,
        parametric_action_distribution=action_distribution,
    )


def make_response_conditioned_inference_fn(
    networks: ppo_networks.PPONetworks,
    compute_value: bool = False,
    use_distributional_critic: bool = False,
):
    def make_policy(params: types.Params, deterministic: bool = False):
        def policy(observations: types.Observation, key_sample: types.PRNGKey):
            logits, hidden_out = networks.policy_network.apply_with_state(
                params[0], params[1], observations
            )
            action_distribution = networks.parametric_action_distribution
            if deterministic:
                action = action_distribution.mode(logits)
                extras = {"policy_hidden_out": hidden_out}
            else:
                raw_action = action_distribution.sample_no_postprocessing(
                    logits, key_sample
                )
                action = action_distribution.postprocess(raw_action)
                extras = {
                    "log_prob": action_distribution.log_prob(logits, raw_action),
                    "raw_action": raw_action,
                    "distribution_params": logits,
                    "policy_hidden_out": hidden_out,
                }
            if compute_value:
                value = networks.value_network.apply(params[0], params[2], observations)
                if use_distributional_critic:
                    value, quantiles = value
                    extras["quantiles"] = quantiles
                extras["value"] = value
            return action, extras

        return policy

    return make_policy


def response_conditioned_actor_step(env, env_state, policy, key, extra_fields=()):
    from brax.training import acting

    actions, policy_extras = policy(env_state.obs, key)
    hidden_out = policy_extras["policy_hidden_out"]
    next_state = env.step(env_state, actions)
    keep = 1.0 - next_state.done
    while keep.ndim < hidden_out.ndim:
        keep = keep[..., None]
    next_obs = dict(next_state.obs)
    next_obs[HIDDEN_OBSERVATION_KEY] = hidden_out * keep
    next_state = next_state.replace(obs=next_obs)
    state_extras = {name: next_state.info[name] for name in extra_fields}
    return next_state, acting.Transition(
        observation=env_state.obs,
        action=actions,
        reward=next_state.reward,
        discount=1 - next_state.done,
        next_observation=next_state.obs,
        extras={"policy_extras": policy_extras, "state_extras": state_extras},
    )


def install_response_conditioned_collector_hooks() -> None:
    from brax.training import acting

    acting.actor_step = response_conditioned_actor_step
    ppo_networks.make_inference_fn = make_response_conditioned_inference_fn


def adapter_parameters_from_flax(policy_parameters: Mapping[str, object]) -> dict[str, np.ndarray]:
    policy = getattr(policy_parameters, "policy", policy_parameters)
    params = policy.get("params") if hasattr(policy, "get") else None
    if params is None:
        raise ValueError("response-conditioned policy params missing")
    mapping = {
        "obs_weight": "adapter_obs_weight",
        "previous_action_weight": "adapter_previous_action_weight",
        "hidden_weight": "adapter_hidden_weight",
        "context_hidden_weight": "adapter_context_hidden_weight",
        "hidden_bias": "adapter_hidden_bias",
        "hidden_action_weight": "adapter_hidden_action_weight",
        "context_action_weight": "adapter_context_action_weight",
        "action_bias": "adapter_action_bias",
    }
    return {
        output: np.asarray(params[source], dtype=np.float32)
        for output, source in mapping.items()
    }
