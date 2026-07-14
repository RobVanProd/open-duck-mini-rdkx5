"""Reference-anchored residual PPO actor and deterministic ONNX export."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path

from brax.training import distribution
from brax.training import networks as brax_networks
from brax.training import types
from brax.training.agents.ppo import networks as ppo_networks
from flax import linen
import jax
import jax.numpy as jnp
import numpy as np


REFERENCE_CLIP = 1.0 - 1.0e-5


class ReferenceResidualPolicy(linen.Module):
    """Policy distribution centered on reference action plus learned residual."""

    action_size: int
    hidden_layer_sizes: Sequence[int]

    @linen.compact
    def __call__(self, normalized_obs, raw_reference_action):
        hidden = brax_networks.MLP(
            layer_sizes=list(self.hidden_layer_sizes),
            activation=linen.swish,
            activate_final=True,
            name="residual_trunk",
        )(normalized_obs)
        residual_location = linen.Dense(
            self.action_size,
            kernel_init=jax.nn.initializers.zeros,
            bias_init=jax.nn.initializers.zeros,
            name="residual_location",
        )(hidden)
        scale_logits = linen.Dense(
            self.action_size,
            name="scale_logits",
        )(hidden)
        safe_reference = jnp.clip(
            raw_reference_action, -REFERENCE_CLIP, REFERENCE_CLIP
        )
        anchored_location = jnp.arctanh(safe_reference) + residual_location
        return jnp.concatenate([anchored_location, scale_logits], axis=-1)


def _obs_size(observation_size: types.ObservationSize, key: str) -> int:
    value = observation_size[key] if isinstance(observation_size, Mapping) else observation_size
    return int(jax.tree_util.tree_flatten(value)[0][-1])


def make_reference_residual_ppo_networks(
    observation_size: types.ObservationSize,
    action_size: int,
    preprocess_observations_fn: types.PreprocessObservationFn = types.identity_observation_preprocessor,
    policy_hidden_layer_sizes: Sequence[int] = (512, 256, 128),
    value_hidden_layer_sizes: Sequence[int] = (512, 256, 128),
    policy_obs_key: str = "state",
    value_obs_key: str = "privileged_state",
    **kwargs,
) -> ppo_networks.PPONetworks:
    state_size = _obs_size(observation_size, policy_obs_key)
    if state_size < action_size:
        raise ValueError(
            f"reference-residual state {state_size} cannot contain {action_size} reference actions"
        )
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
    module = ReferenceResidualPolicy(
        action_size=action_size,
        hidden_layer_sizes=policy_hidden_layer_sizes,
    )

    def init(key):
        return module.init(
            key,
            jnp.zeros((1, state_size)),
            jnp.zeros((1, action_size)),
        )

    def apply(processor_params, policy_params, obs):
        raw = obs[policy_obs_key] if isinstance(obs, Mapping) else obs
        selector = (
            brax_networks.normalizer_select(processor_params, policy_obs_key)
            if isinstance(obs, Mapping)
            else processor_params
        )
        normalized = preprocess_observations_fn(raw, selector)
        reference_action = raw[..., -action_size:]
        return module.apply(policy_params, normalized, reference_action)

    policy_network = brax_networks.FeedForwardNetwork(init=init, apply=apply)
    return ppo_networks.PPONetworks(
        policy_network=policy_network,
        value_network=base.value_network,
        parametric_action_distribution=action_distribution,
    )


def _policy_params(value):
    policy = getattr(value, "policy", value)
    params = policy.get("params") if hasattr(policy, "get") else None
    if params is None:
        raise ValueError("reference-residual policy params missing")
    return params


def export_reference_residual_onnx(
    params,
    action_size: int,
    obs_size: int,
    output_path: str | Path,
    hidden_layer_sizes: Sequence[int],
) -> dict:
    """Export final deterministic action and verify ONNX against JAX."""
    import onnx
    from onnx import TensorProto, helper, numpy_helper
    import onnxruntime as ort

    output_path = Path(output_path)
    normalizer = params[0]
    mean = np.asarray(normalizer.mean["state"], dtype=np.float32)
    std = np.asarray(normalizer.std["state"], dtype=np.float32)
    policy_params = _policy_params(params[1])
    reference_indices = np.arange(obs_size - action_size, obs_size, dtype=np.int64)

    initializers = [
        numpy_helper.from_array(mean, name="obs_mean"),
        numpy_helper.from_array(std, name="obs_std"),
        numpy_helper.from_array(reference_indices, name="reference_indices"),
        numpy_helper.from_array(np.asarray(-REFERENCE_CLIP, dtype=np.float32), name="clip_min"),
        numpy_helper.from_array(np.asarray(REFERENCE_CLIP, dtype=np.float32), name="clip_max"),
    ]
    nodes = [
        helper.make_node("Sub", ["obs", "obs_mean"], ["obs_centered"]),
        helper.make_node("Div", ["obs_centered", "obs_std"], ["obs_normalized"]),
        helper.make_node(
            "Gather", ["obs", "reference_indices"], ["reference_action"], axis=1
        ),
        helper.make_node(
            "Clip", ["reference_action", "clip_min", "clip_max"], ["reference_safe"]
        ),
        helper.make_node("Atanh", ["reference_safe"], ["reference_location"]),
    ]

    hidden = "obs_normalized"
    trunk = policy_params["residual_trunk"]
    for index, _ in enumerate(hidden_layer_sizes):
        layer = trunk[f"hidden_{index}"]
        weight = f"trunk_{index}_weight"
        bias = f"trunk_{index}_bias"
        pre = f"trunk_{index}_pre"
        sigmoid = f"trunk_{index}_sigmoid"
        out = f"trunk_{index}_out"
        initializers.extend(
            [
                numpy_helper.from_array(np.asarray(layer["kernel"], dtype=np.float32), name=weight),
                numpy_helper.from_array(np.asarray(layer["bias"], dtype=np.float32), name=bias),
            ]
        )
        nodes.extend(
            [
                helper.make_node("Gemm", [hidden, weight, bias], [pre]),
                helper.make_node("Sigmoid", [pre], [sigmoid]),
                helper.make_node("Mul", [pre, sigmoid], [out]),
            ]
        )
        hidden = out

    residual = policy_params["residual_location"]
    initializers.extend(
        [
            numpy_helper.from_array(
                np.asarray(residual["kernel"], dtype=np.float32), name="residual_weight"
            ),
            numpy_helper.from_array(
                np.asarray(residual["bias"], dtype=np.float32), name="residual_bias"
            ),
        ]
    )
    nodes.extend(
        [
            helper.make_node(
                "Gemm", [hidden, "residual_weight", "residual_bias"], ["residual_location"]
            ),
            helper.make_node(
                "Add", ["reference_location", "residual_location"], ["anchored_location"]
            ),
            helper.make_node("Tanh", ["anchored_location"], ["continuous_actions"]),
        ]
    )
    graph = helper.make_graph(
        nodes,
        "open_duck_reference_anchored_residual_final_action",
        [helper.make_tensor_value_info("obs", TensorProto.FLOAT, [1, obs_size])],
        [helper.make_tensor_value_info("continuous_actions", TensorProto.FLOAT, [1, action_size])],
        initializer=initializers,
    )
    model = helper.make_model(
        graph,
        producer_name="open-duck-playground-ground-up",
        opset_imports=[helper.make_operatorsetid("", 12)],
    )
    model.ir_version = min(model.ir_version, 10)
    onnx.checker.check_model(model)
    onnx.save(model, output_path)

    dummy = np.linspace(-0.25, 0.25, obs_size, dtype=np.float32)[None, :]
    network = make_reference_residual_ppo_networks(
        {"state": (obs_size,), "privileged_state": (obs_size,)},
        action_size,
        preprocess_observations_fn=lambda value, stats: (value - stats.mean) / stats.std,
        policy_hidden_layer_sizes=hidden_layer_sizes,
        value_hidden_layer_sizes=hidden_layer_sizes,
        value_obs_key="state",
    )
    logits = np.asarray(network.policy_network.apply(params[0], params[1], {"state": dummy}))
    expected = np.tanh(logits[:, :action_size])
    session = ort.InferenceSession(str(output_path), providers=["CPUExecutionProvider"])
    actual = session.run(["continuous_actions"], {"obs": dummy})[0]
    max_error = float(np.max(np.abs(expected - actual)))
    if max_error > 1.0e-5:
        raise ValueError(f"reference-residual ONNX mismatch: {max_error}")
    return {"path": str(output_path), "max_action_error": max_error}
