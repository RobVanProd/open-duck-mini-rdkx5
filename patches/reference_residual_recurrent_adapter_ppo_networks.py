"""Reference-residual PPO actor with a zero-head recurrent adapter."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path

from brax.training import distribution
from brax.training import networks as brax_networks
from brax.training import types
from brax.training.agents.ppo import networks as ppo_networks
import flax
from flax import linen
import jax
import jax.numpy as jnp
import numpy as np


REFERENCE_CLIP = 1.0 - 1.0e-5
HIDDEN_OBSERVATION_KEY = "policy_hidden"


class ReferenceResidualRecurrentAdapterPolicy(linen.Module):
    """Protected reference-residual actor plus a recurrent location residual."""

    action_size: int
    hidden_layer_sizes: Sequence[int]
    recurrent_hidden_size: int

    @linen.compact
    def __call__(self, normalized_obs, raw_reference_action, hidden_in):
        base_hidden = brax_networks.MLP(
            layer_sizes=list(self.hidden_layer_sizes),
            activation=linen.swish,
            activate_final=True,
            name="residual_trunk",
        )(normalized_obs)
        base_residual_location = linen.Dense(
            self.action_size,
            kernel_init=jax.nn.initializers.zeros,
            bias_init=jax.nn.initializers.zeros,
            name="residual_location",
        )(base_hidden)
        scale_logits = linen.Dense(
            self.action_size,
            name="scale_logits",
        )(base_hidden)

        obs_projection = linen.Dense(
            self.recurrent_hidden_size,
            use_bias=False,
            name="adapter_obs_projection",
        )(normalized_obs)
        hidden_projection = linen.Dense(
            self.recurrent_hidden_size,
            use_bias=False,
            name="adapter_hidden_projection",
        )(hidden_in)
        hidden_bias = self.param(
            "adapter_hidden_bias",
            jax.nn.initializers.zeros,
            (self.recurrent_hidden_size,),
        )
        hidden_out = jnp.tanh(obs_projection + hidden_projection + hidden_bias)
        adapter_location = linen.Dense(
            self.action_size,
            kernel_init=jax.nn.initializers.zeros,
            bias_init=jax.nn.initializers.zeros,
            name="adapter_location",
        )(hidden_out)

        safe_reference = jnp.clip(
            raw_reference_action, -REFERENCE_CLIP, REFERENCE_CLIP
        )
        anchored_location = (
            jnp.arctanh(safe_reference)
            + base_residual_location
            + adapter_location
        )
        return jnp.concatenate([anchored_location, scale_logits], axis=-1), hidden_out


@flax.struct.dataclass
class RecurrentAdapterPolicyNetwork:
    init: object
    apply: object
    apply_with_state: object


def _obs_size(observation_size: types.ObservationSize, key: str) -> int:
    value = observation_size[key] if isinstance(observation_size, Mapping) else observation_size
    return int(jax.tree_util.tree_flatten(value)[0][-1])


def make_reference_residual_recurrent_adapter_ppo_networks(
    observation_size: types.ObservationSize,
    action_size: int,
    preprocess_observations_fn: types.PreprocessObservationFn = types.identity_observation_preprocessor,
    policy_hidden_layer_sizes: Sequence[int] = (512, 256, 128),
    value_hidden_layer_sizes: Sequence[int] = (512, 256, 128),
    policy_obs_key: str = "state",
    value_obs_key: str = "privileged_state",
    recurrent_hidden_size: int = 64,
    **kwargs,
) -> ppo_networks.PPONetworks:
    state_size = _obs_size(observation_size, policy_obs_key)
    if state_size < action_size:
        raise ValueError("state cannot contain the projected reference action")
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
    module = ReferenceResidualRecurrentAdapterPolicy(
        action_size=action_size,
        hidden_layer_sizes=policy_hidden_layer_sizes,
        recurrent_hidden_size=recurrent_hidden_size,
    )

    def init(key):
        return module.init(
            key,
            jnp.zeros((1, state_size)),
            jnp.zeros((1, action_size)),
            jnp.zeros((1, recurrent_hidden_size)),
        )

    def apply_with_state(processor_params, policy_params, obs):
        if not isinstance(obs, Mapping) or HIDDEN_OBSERVATION_KEY not in obs:
            raise ValueError("recurrent adapter requires policy_hidden observation")
        raw = obs[policy_obs_key]
        selector = brax_networks.normalizer_select(processor_params, policy_obs_key)
        normalized = preprocess_observations_fn(raw, selector)
        reference_action = raw[..., -action_size:]
        return module.apply(
            policy_params,
            normalized,
            reference_action,
            obs[HIDDEN_OBSERVATION_KEY],
        )

    def apply(processor_params, policy_params, obs):
        logits, _ = apply_with_state(processor_params, policy_params, obs)
        return logits

    policy_network = RecurrentAdapterPolicyNetwork(
        init=init,
        apply=apply,
        apply_with_state=apply_with_state,
    )
    return ppo_networks.PPONetworks(
        policy_network=policy_network,
        value_network=base.value_network,
        parametric_action_distribution=action_distribution,
    )


def make_recurrent_adapter_inference_fn(
    networks: ppo_networks.PPONetworks,
    compute_value: bool = False,
    use_distributional_critic: bool = False,
):
    """Brax inference factory that propagates the adapter state."""

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


def recurrent_adapter_actor_step(env, env_state, policy, key, extra_fields=()):
    """Brax actor step with adapter state reset only on episode termination."""
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


def install_recurrent_adapter_collector_hooks() -> None:
    from brax.training import acting

    acting.actor_step = recurrent_adapter_actor_step
    ppo_networks.make_inference_fn = make_recurrent_adapter_inference_fn


def _policy_params(value):
    policy = getattr(value, "policy", value)
    params = policy.get("params") if hasattr(policy, "get") else None
    if params is None:
        raise ValueError("reference-residual recurrent-adapter params missing")
    return params


def export_reference_residual_recurrent_adapter_onnx(
    params,
    action_size: int,
    obs_size: int,
    hidden_size: int,
    output_path: str | Path,
    hidden_layer_sizes: Sequence[int],
    action_velocity_limits_rad_s: Sequence[float] | None = None,
    control_dt: float = 0.02,
    action_scale: float = 0.25,
) -> dict:
    """Export the deterministic final action plus both recurrent states."""
    import onnx
    from onnx import TensorProto, helper, numpy_helper
    import onnxruntime as ort

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    normalizer = params[0]
    mean = np.asarray(normalizer.mean["state"], dtype=np.float32)
    std = np.asarray(normalizer.std["state"], dtype=np.float32)
    p = _policy_params(params[1])
    reference_indices = np.arange(obs_size - action_size, obs_size, dtype=np.int64)
    initializers = [
        numpy_helper.from_array(mean, name="obs_mean"),
        numpy_helper.from_array(std, name="obs_std"),
        numpy_helper.from_array(reference_indices, name="reference_indices"),
        numpy_helper.from_array(np.asarray(-REFERENCE_CLIP, np.float32), name="clip_min"),
        numpy_helper.from_array(np.asarray(REFERENCE_CLIP, np.float32), name="clip_max"),
    ]
    nodes = [
        helper.make_node("Sub", ["obs", "obs_mean"], ["obs_centered"]),
        helper.make_node("Div", ["obs_centered", "obs_std"], ["obs_normalized"]),
        helper.make_node("Gather", ["obs", "reference_indices"], ["reference_action"], axis=1),
        helper.make_node("Clip", ["reference_action", "clip_min", "clip_max"], ["reference_safe"]),
        helper.make_node("Atanh", ["reference_safe"], ["reference_location"]),
    ]
    base_hidden = "obs_normalized"
    trunk = p["residual_trunk"]
    for index, _ in enumerate(hidden_layer_sizes):
        layer = trunk[f"hidden_{index}"]
        initializers.extend([
            numpy_helper.from_array(np.asarray(layer["kernel"], np.float32), name=f"trunk_{index}_weight"),
            numpy_helper.from_array(np.asarray(layer["bias"], np.float32), name=f"trunk_{index}_bias"),
        ])
        nodes.extend([
            helper.make_node("Gemm", [base_hidden, f"trunk_{index}_weight", f"trunk_{index}_bias"], [f"trunk_{index}_pre"]),
            helper.make_node("Sigmoid", [f"trunk_{index}_pre"], [f"trunk_{index}_sigmoid"]),
            helper.make_node("Mul", [f"trunk_{index}_pre", f"trunk_{index}_sigmoid"], [f"trunk_{index}_out"]),
        ])
        base_hidden = f"trunk_{index}_out"
    for parameter, weight_name, bias_name in (
        (p["residual_location"], "base_residual_weight", "base_residual_bias"),
        (p["adapter_location"], "adapter_weight", "adapter_bias"),
    ):
        initializers.extend([
            numpy_helper.from_array(np.asarray(parameter["kernel"], np.float32), name=weight_name),
            numpy_helper.from_array(np.asarray(parameter["bias"], np.float32), name=bias_name),
        ])
    initializers.extend([
        numpy_helper.from_array(np.asarray(p["adapter_obs_projection"]["kernel"], np.float32), name="adapter_obs_weight"),
        numpy_helper.from_array(np.asarray(p["adapter_hidden_projection"]["kernel"], np.float32), name="adapter_hidden_weight"),
        numpy_helper.from_array(np.asarray(p["adapter_hidden_bias"], np.float32), name="adapter_hidden_bias"),
    ])
    nodes.extend([
        helper.make_node("Gemm", [base_hidden, "base_residual_weight", "base_residual_bias"], ["base_residual_location"]),
        helper.make_node("MatMul", ["obs_normalized", "adapter_obs_weight"], ["adapter_obs_projected"]),
        helper.make_node("MatMul", ["h_in", "adapter_hidden_weight"], ["adapter_hidden_projected"]),
        helper.make_node("Add", ["adapter_obs_projected", "adapter_hidden_projected"], ["adapter_hidden_sum"]),
        helper.make_node("Add", ["adapter_hidden_sum", "adapter_hidden_bias"], ["adapter_hidden_pre"]),
        helper.make_node("Tanh", ["adapter_hidden_pre"], ["h_out"]),
        helper.make_node("Gemm", ["h_out", "adapter_weight", "adapter_bias"], ["adapter_location"]),
        helper.make_node("Add", ["reference_location", "base_residual_location"], ["base_anchored_location"]),
        helper.make_node("Add", ["base_anchored_location", "adapter_location"], ["anchored_location"]),
        helper.make_node("Tanh", ["anchored_location"], ["raw_continuous_actions"]),
    ])
    inputs = [
        helper.make_tensor_value_info("obs", TensorProto.FLOAT, [1, obs_size]),
        helper.make_tensor_value_info("h_in", TensorProto.FLOAT, [1, hidden_size]),
    ]
    outputs = [helper.make_tensor_value_info("continuous_actions", TensorProto.FLOAT, [1, action_size])]
    max_action_delta = None
    if action_velocity_limits_rad_s is not None:
        limits = np.asarray(action_velocity_limits_rad_s, dtype=np.float32)
        if limits.shape != (action_size,) or np.any(limits <= 0.0):
            raise ValueError("invalid action velocity limits")
        max_action_delta = (limits * control_dt / action_scale)[None, :]
        initializers.append(numpy_helper.from_array(max_action_delta, name="max_action_delta"))
        inputs.insert(1, helper.make_tensor_value_info("previous_action", TensorProto.FLOAT, [1, action_size]))
        nodes.extend([
            helper.make_node("Sub", ["previous_action", "max_action_delta"], ["action_min"]),
            helper.make_node("Add", ["previous_action", "max_action_delta"], ["action_max"]),
            helper.make_node("Min", ["raw_continuous_actions", "action_max"], ["actions_below_max"]),
            helper.make_node("Max", ["actions_below_max", "action_min"], ["continuous_actions"]),
            helper.make_node("Identity", ["continuous_actions"], ["previous_action_out"]),
        ])
        outputs.append(helper.make_tensor_value_info("previous_action_out", TensorProto.FLOAT, [1, action_size]))
    else:
        nodes.append(helper.make_node("Identity", ["raw_continuous_actions"], ["continuous_actions"]))
    outputs.append(helper.make_tensor_value_info("h_out", TensorProto.FLOAT, [1, hidden_size]))
    graph = helper.make_graph(nodes, "open_duck_reference_residual_recurrent_adapter", inputs, outputs, initializer=initializers)
    model = helper.make_model(graph, producer_name="open-duck-playground-ground-up", opset_imports=[helper.make_operatorsetid("", 12)])
    model.ir_version = min(model.ir_version, 10)
    onnx.checker.check_model(model)
    onnx.save(model, output_path)

    network = make_reference_residual_recurrent_adapter_ppo_networks(
        {"state": (obs_size,), "privileged_state": (obs_size,), HIDDEN_OBSERVATION_KEY: (hidden_size,)},
        action_size,
        preprocess_observations_fn=lambda value, stats: (value - stats.mean) / stats.std,
        policy_hidden_layer_sizes=hidden_layer_sizes,
        value_hidden_layer_sizes=hidden_layer_sizes,
        value_obs_key="state",
        recurrent_hidden_size=hidden_size,
    )
    session = ort.InferenceSession(str(output_path), providers=["CPUExecutionProvider"])
    hidden_jax = np.zeros((1, hidden_size), np.float32)
    hidden_onnx = hidden_jax.copy()
    previous = np.zeros((1, action_size), np.float32)
    max_action_error = 0.0
    max_hidden_error = 0.0
    for step in range(8):
        obs = np.linspace(-0.25, 0.25, obs_size, dtype=np.float32)[None] + np.float32(step * 0.001)
        logits, next_hidden = network.policy_network.apply_with_state(
            params[0], params[1], {"state": obs, HIDDEN_OBSERVATION_KEY: hidden_jax}
        )
        expected = np.tanh(np.asarray(logits)[:, :action_size])
        feed = {"obs": obs, "h_in": hidden_onnx}
        output_names = ["continuous_actions", "h_out"]
        if max_action_delta is not None:
            feed["previous_action"] = previous
            expected = np.clip(expected, previous - max_action_delta, previous + max_action_delta)
        actual, next_hidden_onnx = session.run(output_names, feed)
        max_action_error = max(max_action_error, float(np.max(np.abs(expected - actual))))
        max_hidden_error = max(max_hidden_error, float(np.max(np.abs(np.asarray(next_hidden) - next_hidden_onnx))))
        previous = actual
        hidden_jax = np.asarray(next_hidden)
        hidden_onnx = next_hidden_onnx
    if max(max_action_error, max_hidden_error) > 1e-7:
        raise ValueError(f"ONNX mismatch action={max_action_error} hidden={max_hidden_error}")
    return {
        "path": str(output_path),
        "steps_checked": 8,
        "max_action_error": max_action_error,
        "max_hidden_error": max_hidden_error,
        "stateful_hard_vector": max_action_delta is not None,
        "max_action_delta": None if max_action_delta is None else max_action_delta[0].tolist(),
    }
