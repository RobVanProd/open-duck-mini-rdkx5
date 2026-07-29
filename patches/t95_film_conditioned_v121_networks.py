"""V121 recurrent actor with zero-initialized calibration FiLM gains.

The calibration vector does not select an expert or add a static action bias.
It multiplicatively schedules the already learned recurrent state-feedback
features before their full-rank action head.  The new kernel initializes to
exact zero, so an expanded source checkpoint is action- and state-equivalent
before the first optimizer update.  The exporter owns the complete deployment
hierarchy:

raw actor -> trained rate -> actual-centered guard -> x=0 deadband
          -> final trained-rate projection -> restored x=0 deadband.
"""

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


OBS_SIZE = 115
ACTION_SIZE = 14
HIDDEN_SIZE = 64
REFERENCE_CLIP = np.float32(1.0 - 1.0e-5)
HIDDEN_OBSERVATION_KEY = "policy_hidden"
CONTEXT_OBSERVATION_KEY = "calibration_context"
PREVIOUS_ACTION_OBSERVATION_KEY = "policy_previous_action"

V121_HOME = np.asarray(
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
V121_PITCH_MASK = np.asarray(
    [
        False,
        False,
        True,
        True,
        True,
        False,
        False,
        False,
        False,
        False,
        False,
        True,
        True,
        True,
    ],
    dtype=np.bool_,
)
V121_GUARD_MARGIN_RAD = np.float32(0.165)
V121_ACTION_SCALE_RAD = np.float32(0.25)
V121_COMMAND_INDEX = 6
V121_DEADBAND_ABS_X = np.float32(0.01)
V121_JOINT_OBS_INDICES = np.arange(13, 27, dtype=np.int64)


class ResponseConditionedV121Policy(linen.Module):
    """V121 actor plus a zero-initialized context/state bilinear path."""

    action_size: int
    hidden_layer_sizes: Sequence[int]
    recurrent_hidden_size: int

    @linen.compact
    def __call__(
        self,
        normalized_obs: jax.Array,
        raw_reference_action: jax.Array,
        hidden_in: jax.Array,
        calibration_context: jax.Array,
    ) -> tuple[jax.Array, jax.Array]:
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
        context_film_scale = linen.Dense(
            self.recurrent_hidden_size,
            use_bias=False,
            kernel_init=jax.nn.initializers.zeros,
            name="context_film_scale",
        )(calibration_context)
        hidden_bias = self.param(
            "adapter_hidden_bias",
            jax.nn.initializers.zeros,
            (self.recurrent_hidden_size,),
        )
        hidden_out = jnp.tanh(
            obs_projection + hidden_projection + hidden_bias
        )
        film_hidden = hidden_out + hidden_out * context_film_scale
        adapter_location = linen.Dense(
            self.action_size,
            kernel_init=jax.nn.initializers.zeros,
            bias_init=jax.nn.initializers.zeros,
            name="adapter_location",
        )(film_hidden)

        safe_reference = jnp.clip(
            raw_reference_action, -REFERENCE_CLIP, REFERENCE_CLIP
        )
        anchored_location = (
            jnp.arctanh(safe_reference)
            + base_residual_location
            + adapter_location
        )
        logits = jnp.concatenate(
            [anchored_location, scale_logits],
            axis=-1,
        )
        return logits, hidden_out


@flax.struct.dataclass
class ResponseConditionedV121Network:
    init: object
    apply: object
    apply_with_state: object


def _obs_size(observation_size: types.ObservationSize, key: str) -> int:
    value = (
        observation_size[key]
        if isinstance(observation_size, Mapping)
        else observation_size
    )
    return int(jax.tree_util.tree_flatten(value)[0][-1])


def make_response_conditioned_v121_ppo_networks(
    observation_size: types.ObservationSize,
    action_size: int,
    preprocess_observations_fn: types.PreprocessObservationFn = (
        types.identity_observation_preprocessor
    ),
    policy_hidden_layer_sizes: Sequence[int] = (512, 256, 128),
    value_hidden_layer_sizes: Sequence[int] = (512, 256, 128),
    policy_obs_key: str = "state",
    value_obs_key: str = "privileged_state",
    recurrent_hidden_size: int = HIDDEN_SIZE,
    **kwargs,
) -> ppo_networks.PPONetworks:
    if not isinstance(observation_size, Mapping):
        raise ValueError("T10 requires mapping observations")
    if _obs_size(observation_size, policy_obs_key) != OBS_SIZE:
        raise ValueError("T10 state observation must remain 115-D")
    if action_size != ACTION_SIZE or recurrent_hidden_size != HIDDEN_SIZE:
        raise ValueError("T10 policy ABI must remain 115x14 with 64 state")
    required = {
        HIDDEN_OBSERVATION_KEY: HIDDEN_SIZE,
        CONTEXT_OBSERVATION_KEY: HIDDEN_SIZE,
        PREVIOUS_ACTION_OBSERVATION_KEY: ACTION_SIZE,
    }
    for key, width in required.items():
        if _obs_size(observation_size, key) != width:
            raise ValueError(f"T10 observation key changed: {key}")

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
    module = ResponseConditionedV121Policy(
        action_size=action_size,
        hidden_layer_sizes=policy_hidden_layer_sizes,
        recurrent_hidden_size=recurrent_hidden_size,
    )

    def init(key: types.PRNGKey):
        return module.init(
            key,
            jnp.zeros((1, OBS_SIZE), dtype=jnp.float32),
            jnp.zeros((1, ACTION_SIZE), dtype=jnp.float32),
            jnp.zeros((1, HIDDEN_SIZE), dtype=jnp.float32),
            jnp.zeros((1, HIDDEN_SIZE), dtype=jnp.float32),
        )

    def apply_with_state(processor_params, policy_params, obs):
        if not isinstance(obs, Mapping):
            raise ValueError("T10 requires mapping observations")
        missing = set(required) - set(obs)
        if missing:
            raise ValueError(f"T10 observation missing: {sorted(missing)}")
        raw = obs[policy_obs_key]
        selector = brax_networks.normalizer_select(
            processor_params,
            policy_obs_key,
        )
        normalized = preprocess_observations_fn(raw, selector)
        reference_action = raw[..., -ACTION_SIZE:]
        return module.apply(
            policy_params,
            normalized,
            reference_action,
            obs[HIDDEN_OBSERVATION_KEY],
            obs[CONTEXT_OBSERVATION_KEY],
        )

    def apply(processor_params, policy_params, obs):
        logits, _ = apply_with_state(processor_params, policy_params, obs)
        return logits

    policy_network = ResponseConditionedV121Network(
        init=init,
        apply=apply,
        apply_with_state=apply_with_state,
    )
    return ppo_networks.PPONetworks(
        policy_network=policy_network,
        value_network=base.value_network,
        parametric_action_distribution=distribution.NormalTanhDistribution(
            event_size=action_size
        ),
    )


def make_response_conditioned_v121_inference_fn(
    networks: ppo_networks.PPONetworks,
    compute_value: bool = False,
    use_distributional_critic: bool = False,
):
    def make_policy(params: types.Params, deterministic: bool = False):
        def policy(observations: types.Observation, key_sample: types.PRNGKey):
            logits, hidden_out = networks.policy_network.apply_with_state(
                params[0],
                params[1],
                observations,
            )
            action_distribution = networks.parametric_action_distribution
            if deterministic:
                action = action_distribution.mode(logits)
                extras = {"policy_hidden_out": hidden_out}
            else:
                raw_action = action_distribution.sample_no_postprocessing(
                    logits,
                    key_sample,
                )
                action = action_distribution.postprocess(raw_action)
                extras = {
                    "log_prob": action_distribution.log_prob(
                        logits,
                        raw_action,
                    ),
                    "raw_action": raw_action,
                    "distribution_params": logits,
                    "policy_hidden_out": hidden_out,
                }
            if compute_value:
                value = networks.value_network.apply(
                    params[0],
                    params[2],
                    observations,
                )
                if use_distributional_critic:
                    value, quantiles = value
                    extras["quantiles"] = quantiles
                extras["value"] = value
            return action, extras

        return policy

    return make_policy


def response_conditioned_v121_actor_step(
    env,
    env_state,
    policy,
    key,
    extra_fields=(),
):
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
    state_extras = {
        name: next_state.info[name] for name in extra_fields
    }
    return next_state, acting.Transition(
        observation=env_state.obs,
        action=actions,
        reward=next_state.reward,
        discount=1 - next_state.done,
        next_observation=next_state.obs,
        extras={
            "policy_extras": policy_extras,
            "state_extras": state_extras,
        },
    )


def install_response_conditioned_v121_collector_hooks() -> None:
    from brax.training import acting

    acting.actor_step = response_conditioned_v121_actor_step
    ppo_networks.make_inference_fn = (
        make_response_conditioned_v121_inference_fn
    )


def _policy_params(value):
    policy = getattr(value, "policy", value)
    params = policy.get("params") if hasattr(policy, "get") else None
    if params is None:
        raise ValueError("T10 policy params missing")
    return params


def _array(initializers, name: str, value) -> None:
    from onnx import numpy_helper

    initializers.append(
        numpy_helper.from_array(np.asarray(value), name=name)
    )


def _add_v121_boundary(
    *,
    nodes,
    initializers,
    first_rate_action: str,
    previous_action: str,
) -> str:
    from onnx import helper

    _array(
        initializers,
        "guard_joint_obs_indices",
        V121_JOINT_OBS_INDICES,
    )
    _array(initializers, "guard_home", V121_HOME[None])
    _array(
        initializers,
        "guard_action_scale",
        np.asarray([V121_ACTION_SCALE_RAD], dtype=np.float32),
    )
    _array(
        initializers,
        "guard_margin",
        np.full((1, ACTION_SIZE), V121_GUARD_MARGIN_RAD, np.float32),
    )
    _array(initializers, "guard_pitch_mask", V121_PITCH_MASK[None])
    _array(
        initializers,
        "guard_action_min",
        np.asarray([-1.0], dtype=np.float32),
    )
    _array(
        initializers,
        "guard_action_max",
        np.asarray([1.0], dtype=np.float32),
    )
    _array(
        initializers,
        "deadband_command_index",
        np.asarray([V121_COMMAND_INDEX], dtype=np.int64),
    )
    _array(
        initializers,
        "deadband_abs_limit",
        np.asarray([V121_DEADBAND_ABS_X], dtype=np.float32),
    )
    _array(
        initializers,
        "deadband_zero_action",
        np.zeros((1, ACTION_SIZE), dtype=np.float32),
    )
    nodes.extend(
        [
            helper.make_node(
                "Gather",
                ["obs", "guard_joint_obs_indices"],
                ["guard_joint_offsets"],
                axis=1,
            ),
            helper.make_node(
                "Add",
                ["guard_home", "guard_joint_offsets"],
                ["guard_actual_target"],
            ),
            helper.make_node(
                "Mul",
                [first_rate_action, "guard_action_scale"],
                ["guard_desired_offset"],
            ),
            helper.make_node(
                "Add",
                ["guard_home", "guard_desired_offset"],
                ["guard_desired_target"],
            ),
            helper.make_node(
                "Sub",
                ["guard_actual_target", "guard_margin"],
                ["guard_target_min"],
            ),
            helper.make_node(
                "Add",
                ["guard_actual_target", "guard_margin"],
                ["guard_target_max"],
            ),
            helper.make_node(
                "Max",
                ["guard_desired_target", "guard_target_min"],
                ["guard_target_above_min"],
            ),
            helper.make_node(
                "Min",
                ["guard_target_above_min", "guard_target_max"],
                ["guard_clipped_target"],
            ),
            helper.make_node(
                "Sub",
                ["guard_clipped_target", "guard_home"],
                ["guard_clipped_offset"],
            ),
            helper.make_node(
                "Div",
                ["guard_clipped_offset", "guard_action_scale"],
                ["guard_pitch_actions_unclipped"],
            ),
            helper.make_node(
                "Clip",
                [
                    "guard_pitch_actions_unclipped",
                    "guard_action_min",
                    "guard_action_max",
                ],
                ["guard_pitch_actions"],
            ),
            helper.make_node(
                "Where",
                [
                    "guard_pitch_mask",
                    "guard_pitch_actions",
                    first_rate_action,
                ],
                ["deadband_source_actions"],
            ),
            helper.make_node(
                "Gather",
                ["obs", "deadband_command_index"],
                ["deadband_command_x"],
                axis=1,
            ),
            helper.make_node(
                "Abs",
                ["deadband_command_x"],
                ["deadband_abs_command_x"],
            ),
            helper.make_node(
                "LessOrEqual",
                ["deadband_abs_command_x", "deadband_abs_limit"],
                ["deadband_is_zero_command"],
            ),
            helper.make_node(
                "Where",
                [
                    "deadband_is_zero_command",
                    "deadband_zero_action",
                    "deadband_source_actions",
                ],
                ["v121_preprojection_action"],
            ),
            helper.make_node(
                "Sub",
                [previous_action, "max_action_delta"],
                ["v121_final_rate_lower"],
            ),
            helper.make_node(
                "Add",
                [previous_action, "max_action_delta"],
                ["v121_final_rate_upper"],
            ),
            helper.make_node(
                "Max",
                ["v121_preprojection_action", "v121_final_rate_lower"],
                ["v121_final_above_lower"],
            ),
            helper.make_node(
                "Min",
                ["v121_final_above_lower", "v121_final_rate_upper"],
                ["v121_final_rate_action"],
            ),
            helper.make_node(
                "Where",
                [
                    "deadband_is_zero_command",
                    "deadband_zero_action",
                    "v121_final_rate_action",
                ],
                ["continuous_actions"],
            ),
            helper.make_node(
                "Identity",
                ["continuous_actions"],
                ["previous_action_out"],
            ),
        ]
    )
    return "continuous_actions"


def export_response_conditioned_v121_onnx(
    params,
    action_size: int,
    obs_size: int,
    hidden_size: int,
    output_path: str | Path,
    hidden_layer_sizes: Sequence[int],
    action_velocity_limits_rad_s: Sequence[float],
    control_dt: float = 0.02,
    action_scale: float = 0.25,
) -> dict:
    """Export the deterministic context-conditioned V121 deployment graph."""

    import onnx
    from onnx import TensorProto, helper

    if (action_size, obs_size, hidden_size) != (
        ACTION_SIZE,
        OBS_SIZE,
        HIDDEN_SIZE,
    ):
        raise ValueError("T10 export ABI changed")
    limits = np.asarray(
        action_velocity_limits_rad_s,
        dtype=np.float32,
    )
    if limits.shape != (ACTION_SIZE,) or np.any(limits <= 0.0):
        raise ValueError("T10 rate vector changed")
    max_action_delta = (
        limits
        * np.float32(control_dt)
        / np.float32(action_scale)
    )[None].astype(np.float32)

    normalizer = params[0]
    mean = np.asarray(normalizer.mean["state"], dtype=np.float32)
    std = np.asarray(normalizer.std["state"], dtype=np.float32)
    p = _policy_params(params[1])
    initializers = []
    _array(initializers, "obs_mean", mean)
    _array(initializers, "obs_std", std)
    _array(
        initializers,
        "reference_indices",
        np.arange(OBS_SIZE - ACTION_SIZE, OBS_SIZE, dtype=np.int64),
    )
    _array(
        initializers,
        "reference_clip_min",
        np.asarray(-REFERENCE_CLIP, dtype=np.float32),
    )
    _array(
        initializers,
        "reference_clip_max",
        np.asarray(REFERENCE_CLIP, dtype=np.float32),
    )
    _array(initializers, "max_action_delta", max_action_delta)

    nodes = [
        helper.make_node("Sub", ["obs", "obs_mean"], ["obs_centered"]),
        helper.make_node(
            "Div",
            ["obs_centered", "obs_std"],
            ["obs_normalized"],
        ),
        helper.make_node(
            "Gather",
            ["obs", "reference_indices"],
            ["reference_action"],
            axis=1,
        ),
        helper.make_node(
            "Clip",
            [
                "reference_action",
                "reference_clip_min",
                "reference_clip_max",
            ],
            ["reference_safe"],
        ),
        helper.make_node(
            "Atanh",
            ["reference_safe"],
            ["reference_location"],
        ),
    ]
    base_hidden = "obs_normalized"
    trunk = p["residual_trunk"]
    for index, _ in enumerate(hidden_layer_sizes):
        layer = trunk[f"hidden_{index}"]
        _array(
            initializers,
            f"trunk_{index}_weight",
            np.asarray(layer["kernel"], dtype=np.float32),
        )
        _array(
            initializers,
            f"trunk_{index}_bias",
            np.asarray(layer["bias"], dtype=np.float32),
        )
        nodes.extend(
            [
                helper.make_node(
                    "Gemm",
                    [
                        base_hidden,
                        f"trunk_{index}_weight",
                        f"trunk_{index}_bias",
                    ],
                    [f"trunk_{index}_pre"],
                ),
                helper.make_node(
                    "Sigmoid",
                    [f"trunk_{index}_pre"],
                    [f"trunk_{index}_sigmoid"],
                ),
                helper.make_node(
                    "Mul",
                    [
                        f"trunk_{index}_pre",
                        f"trunk_{index}_sigmoid",
                    ],
                    [f"trunk_{index}_out"],
                ),
            ]
        )
        base_hidden = f"trunk_{index}_out"

    for parameter, weight_name, bias_name in (
        (
            p["residual_location"],
            "base_residual_weight",
            "base_residual_bias",
        ),
        (
            p["adapter_location"],
            "adapter_weight",
            "adapter_bias",
        ),
    ):
        _array(
            initializers,
            weight_name,
            np.asarray(parameter["kernel"], dtype=np.float32),
        )
        _array(
            initializers,
            bias_name,
            np.asarray(parameter["bias"], dtype=np.float32),
        )
    _array(
        initializers,
        "adapter_obs_weight",
        np.asarray(
            p["adapter_obs_projection"]["kernel"],
            dtype=np.float32,
        ),
    )
    _array(
        initializers,
        "adapter_hidden_weight",
        np.asarray(
            p["adapter_hidden_projection"]["kernel"],
            dtype=np.float32,
        ),
    )
    _array(
        initializers,
        "adapter_hidden_bias",
        np.asarray(p["adapter_hidden_bias"], dtype=np.float32),
    )
    _array(
        initializers,
        "context_film_weight",
        np.asarray(
            p["context_film_scale"]["kernel"],
            dtype=np.float32,
        ),
    )
    nodes.extend(
        [
            helper.make_node(
                "Gemm",
                [
                    base_hidden,
                    "base_residual_weight",
                    "base_residual_bias",
                ],
                ["base_residual_location"],
            ),
            helper.make_node(
                "MatMul",
                ["obs_normalized", "adapter_obs_weight"],
                ["adapter_obs_projected"],
            ),
            helper.make_node(
                "MatMul",
                ["h_in", "adapter_hidden_weight"],
                ["adapter_hidden_projected"],
            ),
            helper.make_node(
                "MatMul",
                ["calibration_context", "context_film_weight"],
                ["context_film_scale"],
            ),
            helper.make_node(
                "Add",
                ["adapter_obs_projected", "adapter_hidden_projected"],
                ["adapter_hidden_sum"],
            ),
            helper.make_node(
                "Add",
                ["adapter_hidden_sum", "adapter_hidden_bias"],
                ["adapter_hidden_pre"],
            ),
            helper.make_node(
                "Tanh",
                ["adapter_hidden_pre"],
                ["h_out"],
            ),
            helper.make_node(
                "Mul",
                ["h_out", "context_film_scale"],
                ["context_film_delta"],
            ),
            helper.make_node(
                "Add",
                ["h_out", "context_film_delta"],
                ["film_hidden"],
            ),
            helper.make_node(
                "Gemm",
                ["film_hidden", "adapter_weight", "adapter_bias"],
                ["adapter_location"],
            ),
            helper.make_node(
                "Add",
                ["reference_location", "base_residual_location"],
                ["base_anchored_location"],
            ),
            helper.make_node(
                "Add",
                ["base_anchored_location", "adapter_location"],
                ["anchored_location"],
            ),
            helper.make_node(
                "Tanh",
                ["anchored_location"],
                ["raw_continuous_actions"],
            ),
            helper.make_node(
                "Sub",
                ["previous_action", "max_action_delta"],
                ["first_rate_lower"],
            ),
            helper.make_node(
                "Add",
                ["previous_action", "max_action_delta"],
                ["first_rate_upper"],
            ),
            helper.make_node(
                "Max",
                ["raw_continuous_actions", "first_rate_lower"],
                ["first_rate_above_lower"],
            ),
            helper.make_node(
                "Min",
                ["first_rate_above_lower", "first_rate_upper"],
                ["first_rate_action"],
            ),
        ]
    )
    _add_v121_boundary(
        nodes=nodes,
        initializers=initializers,
        first_rate_action="first_rate_action",
        previous_action="previous_action",
    )
    inputs = [
        helper.make_tensor_value_info(
            "obs",
            TensorProto.FLOAT,
            [1, OBS_SIZE],
        ),
        helper.make_tensor_value_info(
            "previous_action",
            TensorProto.FLOAT,
            [1, ACTION_SIZE],
        ),
        helper.make_tensor_value_info(
            "h_in",
            TensorProto.FLOAT,
            [1, HIDDEN_SIZE],
        ),
        helper.make_tensor_value_info(
            "calibration_context",
            TensorProto.FLOAT,
            [1, HIDDEN_SIZE],
        ),
    ]
    outputs = [
        helper.make_tensor_value_info(
            "continuous_actions",
            TensorProto.FLOAT,
            [1, ACTION_SIZE],
        ),
        helper.make_tensor_value_info(
            "previous_action_out",
            TensorProto.FLOAT,
            [1, ACTION_SIZE],
        ),
        helper.make_tensor_value_info(
            "h_out",
            TensorProto.FLOAT,
            [1, HIDDEN_SIZE],
        ),
    ]
    graph = helper.make_graph(
        nodes,
        "open_duck_t10_response_conditioned_v121",
        inputs,
        outputs,
        initializer=initializers,
    )
    model = helper.make_model(
        graph,
        producer_name="open-duck-t10",
        opset_imports=[helper.make_operatorsetid("", 12)],
    )
    model.ir_version = min(model.ir_version, 10)
    onnx.checker.check_model(model)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    onnx.save(model, output)
    return {
        "path": str(output),
        "inputs": {
            "obs": [1, OBS_SIZE],
            "previous_action": [1, ACTION_SIZE],
            "h_in": [1, HIDDEN_SIZE],
            "calibration_context": [1, HIDDEN_SIZE],
        },
        "outputs": {
            "continuous_actions": [1, ACTION_SIZE],
            "previous_action_out": [1, ACTION_SIZE],
            "h_out": [1, HIDDEN_SIZE],
        },
        "max_action_delta": max_action_delta[0].tolist(),
    }
