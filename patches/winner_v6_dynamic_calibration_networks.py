"""Winner-v6 dynamic-calibration policy primitives and ONNX exporters.

This module deliberately contains no simulator configuration input.  Both graphs
consume only the deployable 115-D observation, action state, recurrent state,
and the learned calibration context accepted by the runtime schema review.
"""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any, Mapping

import jax
import jax.numpy as jnp
import numpy as np


OBS_SIZE = 115
ACTION_SIZE = 14
HIDDEN_SIZE = 64
CONTROL_DT_S = 0.02
ACTION_SCALE_RAD = 0.25
CALIBRATION_TICKS = 250
VELOCITY_LIMITS_RAD_S = np.asarray(
    [5.24, 5.24, 1.5, 1.5, 1.5, 5.24, 5.24, 5.24, 5.24, 5.24, 5.24, 1.25, 1.0, 1.25],
    dtype=np.float32,
)
MAX_ACTION_DELTA = VELOCITY_LIMITS_RAD_S * np.float32(CONTROL_DT_S / ACTION_SCALE_RAD)

# Training-only self-supervision targets.  Every index is already present in the
# deployable observation: IMU, joint position/velocity, applied target, contacts.
AUXILIARY_RESPONSE_OBS_INDICES = np.asarray(
    list(range(0, 6)) + list(range(13, 41)) + list(range(83, 99)),
    dtype=np.int64,
)


def _array(value: Any) -> jax.Array:
    return jnp.asarray(value, dtype=jnp.float32)


def _random_matrix(
    rng: np.random.Generator,
    shape: tuple[int, ...],
    scale: float,
) -> jax.Array:
    return _array(rng.normal(0.0, scale, shape).astype(np.float32))


def initialize_calibrator_parameters(seed: int = 60720) -> dict[str, jax.Array]:
    """Create deterministic zero-action calibrator parameters.

    The recurrent and auxiliary paths are nonzero and trainable.  The action
    head is exactly zero so the pre-PPO graph cannot move a target at step zero.
    """

    rng = np.random.Generator(np.random.PCG64(seed))
    hidden_weight = np.eye(HIDDEN_SIZE, dtype=np.float32) * np.float32(0.35)
    hidden_weight += rng.normal(0.0, 0.003, hidden_weight.shape).astype(np.float32)
    auxiliary_width = int(AUXILIARY_RESPONSE_OBS_INDICES.size)
    return {
        "obs_weight": _random_matrix(rng, (OBS_SIZE, HIDDEN_SIZE), 0.025),
        "previous_action_weight": _random_matrix(rng, (ACTION_SIZE, HIDDEN_SIZE), 0.04),
        "hidden_weight": _array(hidden_weight),
        "hidden_bias": _random_matrix(rng, (HIDDEN_SIZE,), 0.002),
        "action_weight": jnp.zeros((HIDDEN_SIZE, ACTION_SIZE), dtype=jnp.float32),
        "action_bias": jnp.zeros((ACTION_SIZE,), dtype=jnp.float32),
        "auxiliary_hidden_weight": _random_matrix(
            rng, (HIDDEN_SIZE, auxiliary_width), 0.025
        ),
        "auxiliary_action_weight": _random_matrix(
            rng, (ACTION_SIZE, auxiliary_width), 0.025
        ),
        "auxiliary_bias": jnp.zeros((auxiliary_width,), dtype=jnp.float32),
    }


def initialize_locomotion_adapter_parameters(seed: int = 60721) -> dict[str, jax.Array]:
    """Create a recurrent locomotion adapter with exact-zero action/context heads."""

    rng = np.random.Generator(np.random.PCG64(seed))
    hidden_weight = np.eye(HIDDEN_SIZE, dtype=np.float32) * np.float32(0.35)
    hidden_weight += rng.normal(0.0, 0.003, hidden_weight.shape).astype(np.float32)
    return {
        "obs_weight": _random_matrix(rng, (OBS_SIZE, HIDDEN_SIZE), 0.02),
        "previous_action_weight": _random_matrix(rng, (ACTION_SIZE, HIDDEN_SIZE), 0.03),
        "hidden_weight": _array(hidden_weight),
        "context_hidden_weight": jnp.zeros(
            (HIDDEN_SIZE, HIDDEN_SIZE), dtype=jnp.float32
        ),
        "hidden_bias": _random_matrix(rng, (HIDDEN_SIZE,), 0.002),
        "hidden_action_weight": jnp.zeros(
            (HIDDEN_SIZE, ACTION_SIZE), dtype=jnp.float32
        ),
        "context_action_weight": jnp.zeros(
            (HIDDEN_SIZE, ACTION_SIZE), dtype=jnp.float32
        ),
        "action_bias": jnp.zeros((ACTION_SIZE,), dtype=jnp.float32),
    }


def _bounded_action(raw_action: jax.Array, previous_action: jax.Array) -> jax.Array:
    maximum_delta = _array(MAX_ACTION_DELTA)[None, :]
    absolute_bounded = jnp.clip(raw_action, -1.0, 1.0)
    lower = jnp.maximum(previous_action - maximum_delta, -1.0)
    upper = jnp.minimum(previous_action + maximum_delta, 1.0)
    return jnp.maximum(jnp.minimum(absolute_bounded, upper), lower)


def calibrator_step(
    parameters: Mapping[str, jax.Array],
    obs: jax.Array,
    previous_action: jax.Array,
    h_in: jax.Array,
) -> tuple[jax.Array, jax.Array, jax.Array]:
    """Run one calibrator step with graph-owned absolute and slew bounds."""

    hidden_pre = (
        obs @ parameters["obs_weight"]
        + previous_action @ parameters["previous_action_weight"]
        + h_in @ parameters["hidden_weight"]
        + parameters["hidden_bias"]
    )
    h_out = jnp.tanh(hidden_pre)
    raw_action = jnp.tanh(
        h_out @ parameters["action_weight"] + parameters["action_bias"]
    )
    action = _bounded_action(raw_action, previous_action)
    return action, action, h_out


def calibrator_auxiliary_prediction(
    parameters: Mapping[str, jax.Array],
    h_out: jax.Array,
    realized_action: jax.Array,
) -> jax.Array:
    """Predict the next deployable response fields; this head is never exported."""

    return (
        h_out @ parameters["auxiliary_hidden_weight"]
        + realized_action @ parameters["auxiliary_action_weight"]
        + parameters["auxiliary_bias"]
    )


def validate_calibration_handoff(
    h_out: np.ndarray,
    *,
    completed_ticks: int,
    all_ticks_valid: bool,
    support_valid: bool,
) -> np.ndarray:
    """Return an immutable session context or fail closed before arming."""

    context = np.asarray(h_out)
    if context.dtype != np.float32 or context.shape != (1, HIDDEN_SIZE):
        raise ValueError("calibration context must be float32 with shape [1,64]")
    if completed_ticks != CALIBRATION_TICKS:
        raise ValueError("calibration did not complete exactly 250 ticks")
    if not all_ticks_valid or not support_valid:
        raise ValueError("calibration evidence or support predicate failed")
    if not np.isfinite(context).all():
        raise ValueError("calibration context is nonfinite")
    if np.any(context < -1.0) or np.any(context > 1.0):
        raise ValueError("calibration context is outside [-1,1]")
    immutable = context.copy()
    immutable.flags.writeable = False
    return immutable


def onnx_initializers(model: Any) -> dict[str, jax.Array]:
    """Read float/integer initializers needed by the protected JAX reference."""

    from onnx import numpy_helper

    return {
        item.name: jnp.asarray(numpy_helper.to_array(item))
        for item in model.graph.initializer
    }


def protected_policy_step(
    initializers: Mapping[str, jax.Array],
    obs: jax.Array,
    previous_action: jax.Array,
) -> tuple[jax.Array, jax.Array]:
    """JAX transcription of the frozen repaired G1/T2 ONNX graph."""

    normalized = (obs - initializers["obs_mean"]) / initializers["obs_std"]
    reference = jnp.take(obs, initializers["reference_indices"], axis=1)
    reference = jnp.clip(
        reference, initializers["clip_min"], initializers["clip_max"]
    )
    location = jnp.arctanh(reference)
    hidden = normalized
    for index in range(3):
        hidden = hidden @ initializers[f"trunk_{index}_weight"]
        hidden = hidden + initializers[f"trunk_{index}_bias"]
        hidden = hidden * jax.nn.sigmoid(hidden)
    residual = hidden @ initializers["residual_weight"]
    residual = residual + initializers["residual_bias"]
    raw_action = jnp.tanh(location + residual)
    action_min = previous_action - initializers["max_action_delta"]
    action_max = previous_action + initializers["max_action_delta"]
    velocity_bounded = jnp.maximum(jnp.minimum(raw_action, action_max), action_min)

    joint_offsets = jnp.take(obs, initializers["guard_joint_obs_indices"], axis=1)
    actual_target = initializers["guard_home"] + joint_offsets
    desired_target = (
        initializers["guard_home"]
        + velocity_bounded * initializers["guard_action_scale"]
    )
    target_min = actual_target - initializers["guard_margin"]
    target_max = actual_target + initializers["guard_margin"]
    clipped_target = jnp.minimum(jnp.maximum(desired_target, target_min), target_max)
    pitch_actions = (
        clipped_target - initializers["guard_home"]
    ) / initializers["guard_action_scale"]
    pitch_actions = jnp.clip(
        pitch_actions,
        initializers["guard_action_min"],
        initializers["guard_action_max"],
    )
    source_actions = jnp.where(
        initializers["guard_pitch_mask"], pitch_actions, velocity_bounded
    )
    command_x = jnp.take(obs, initializers["deadband_command_index"], axis=1)
    zero_command = jnp.abs(command_x) <= initializers["deadband_abs_limit"]
    actions = jnp.where(
        zero_command, initializers["deadband_zero_action"], source_actions
    )
    return actions, actions


def locomotion_step(
    protected_initializers: Mapping[str, jax.Array],
    adapter_parameters: Mapping[str, jax.Array],
    obs: jax.Array,
    previous_action: jax.Array,
    h_in: jax.Array,
    calibration_context: jax.Array,
) -> tuple[jax.Array, jax.Array, jax.Array]:
    """Run the protected actor plus the exact-zero initialized response adapter."""

    protected_action, _ = protected_policy_step(
        protected_initializers, obs, previous_action
    )
    hidden_pre = (
        obs @ adapter_parameters["obs_weight"]
        + previous_action @ adapter_parameters["previous_action_weight"]
        + h_in @ adapter_parameters["hidden_weight"]
        + calibration_context @ adapter_parameters["context_hidden_weight"]
        + adapter_parameters["hidden_bias"]
    )
    h_out = jnp.tanh(hidden_pre)
    adapter_delta = jnp.tanh(
        h_out @ adapter_parameters["hidden_action_weight"]
        + calibration_context @ adapter_parameters["context_action_weight"]
        + adapter_parameters["action_bias"]
    ) * np.float32(ACTION_SCALE_RAD)
    action = _bounded_action(protected_action + adapter_delta, previous_action)
    return action, action, h_out


def _add_array(initializers: list[Any], name: str, value: Any) -> None:
    from onnx import numpy_helper

    initializers.append(
        numpy_helper.from_array(np.asarray(value, dtype=np.float32), name=name)
    )


def export_calibrator_onnx(
    parameters: Mapping[str, jax.Array], output_path: str | Path
) -> None:
    """Export the exact reviewed calibrator ABI."""

    import onnx
    from onnx import TensorProto, helper

    initializers: list[Any] = []
    for name in (
        "obs_weight", "previous_action_weight", "hidden_weight", "hidden_bias",
        "action_weight", "action_bias",
    ):
        _add_array(initializers, f"cal_{name}", parameters[name])
    _add_array(initializers, "cal_max_action_delta", MAX_ACTION_DELTA[None, :])
    _add_array(initializers, "cal_action_minimum", np.asarray(-1.0, np.float32))
    _add_array(initializers, "cal_action_maximum", np.asarray(1.0, np.float32))
    nodes = [
        helper.make_node("MatMul", ["obs", "cal_obs_weight"], ["cal_obs_hidden"]),
        helper.make_node(
            "MatMul", ["previous_action", "cal_previous_action_weight"],
            ["cal_previous_hidden"],
        ),
        helper.make_node("MatMul", ["h_in", "cal_hidden_weight"], ["cal_state_hidden"]),
        helper.make_node("Add", ["cal_obs_hidden", "cal_previous_hidden"], ["cal_hidden_sum_0"]),
        helper.make_node("Add", ["cal_hidden_sum_0", "cal_state_hidden"], ["cal_hidden_sum_1"]),
        helper.make_node("Add", ["cal_hidden_sum_1", "cal_hidden_bias"], ["cal_hidden_pre"]),
        helper.make_node("Tanh", ["cal_hidden_pre"], ["h_out"]),
        helper.make_node("Gemm", ["h_out", "cal_action_weight", "cal_action_bias"], ["cal_action_pre"]),
        helper.make_node("Tanh", ["cal_action_pre"], ["cal_raw_action"]),
        helper.make_node("Clip", ["cal_raw_action", "cal_action_minimum", "cal_action_maximum"], ["cal_absolute_action"]),
        helper.make_node("Sub", ["previous_action", "cal_max_action_delta"], ["cal_slew_min_raw"]),
        helper.make_node("Add", ["previous_action", "cal_max_action_delta"], ["cal_slew_max_raw"]),
        helper.make_node("Max", ["cal_slew_min_raw", "cal_action_minimum"], ["cal_slew_min"]),
        helper.make_node("Min", ["cal_slew_max_raw", "cal_action_maximum"], ["cal_slew_max"]),
        helper.make_node("Min", ["cal_absolute_action", "cal_slew_max"], ["cal_action_below_max"]),
        helper.make_node("Max", ["cal_action_below_max", "cal_slew_min"], ["calibration_actions"]),
        helper.make_node("Identity", ["calibration_actions"], ["previous_action_out"]),
    ]
    inputs = [
        helper.make_tensor_value_info("obs", TensorProto.FLOAT, [1, OBS_SIZE]),
        helper.make_tensor_value_info(
            "previous_action", TensorProto.FLOAT, [1, ACTION_SIZE]
        ),
        helper.make_tensor_value_info("h_in", TensorProto.FLOAT, [1, HIDDEN_SIZE]),
    ]
    outputs = [
        helper.make_tensor_value_info(
            "calibration_actions", TensorProto.FLOAT, [1, ACTION_SIZE]
        ),
        helper.make_tensor_value_info(
            "previous_action_out", TensorProto.FLOAT, [1, ACTION_SIZE]
        ),
        helper.make_tensor_value_info("h_out", TensorProto.FLOAT, [1, HIDDEN_SIZE]),
    ]
    graph = helper.make_graph(
        nodes, "winner_v6_dynamic_support_calibrator", inputs, outputs, initializers
    )
    model = helper.make_model(
        graph,
        producer_name="open-duck-winner-v6",
        opset_imports=[helper.make_operatorsetid("", 12)],
    )
    model.ir_version = min(model.ir_version, 10)
    onnx.checker.check_model(model)
    onnx.save(model, Path(output_path))


def export_locomotion_onnx(
    protected_path: str | Path,
    adapter_parameters: Mapping[str, jax.Array],
    output_path: str | Path,
) -> None:
    """Add the reviewed state/context ABI around a protected G1/T2 graph."""

    import onnx
    from onnx import TensorProto, helper

    model = copy.deepcopy(onnx.load(Path(protected_path)))
    graph = model.graph
    for node in graph.node:
        for index, output in enumerate(node.output):
            if output == "continuous_actions":
                node.output[index] = "protected_continuous_actions"
            elif output == "previous_action_out":
                node.output[index] = "protected_previous_action_out"
    del graph.output[:]
    graph.input.extend([
        helper.make_tensor_value_info("h_in", TensorProto.FLOAT, [1, HIDDEN_SIZE]),
        helper.make_tensor_value_info(
            "calibration_context", TensorProto.FLOAT, [1, HIDDEN_SIZE]
        ),
    ])
    for name in (
        "obs_weight", "previous_action_weight", "hidden_weight",
        "context_hidden_weight", "hidden_bias", "hidden_action_weight",
        "context_action_weight", "action_bias",
    ):
        _add_array(graph.initializer, f"v6_{name}", adapter_parameters[name])
    _add_array(graph.initializer, "v6_adapter_scale", np.asarray(ACTION_SCALE_RAD, np.float32))
    _add_array(graph.initializer, "v6_max_action_delta", MAX_ACTION_DELTA[None, :])
    _add_array(graph.initializer, "v6_action_minimum", np.asarray(-1.0, np.float32))
    _add_array(graph.initializer, "v6_action_maximum", np.asarray(1.0, np.float32))
    graph.node.extend([
        helper.make_node("MatMul", ["obs", "v6_obs_weight"], ["v6_obs_hidden"]),
        helper.make_node("MatMul", ["previous_action", "v6_previous_action_weight"], ["v6_previous_hidden"]),
        helper.make_node("MatMul", ["h_in", "v6_hidden_weight"], ["v6_state_hidden"]),
        helper.make_node("MatMul", ["calibration_context", "v6_context_hidden_weight"], ["v6_context_hidden"]),
        helper.make_node("Add", ["v6_obs_hidden", "v6_previous_hidden"], ["v6_hidden_sum_0"]),
        helper.make_node("Add", ["v6_hidden_sum_0", "v6_state_hidden"], ["v6_hidden_sum_1"]),
        helper.make_node("Add", ["v6_hidden_sum_1", "v6_context_hidden"], ["v6_hidden_sum_2"]),
        helper.make_node("Add", ["v6_hidden_sum_2", "v6_hidden_bias"], ["v6_hidden_pre"]),
        helper.make_node("Tanh", ["v6_hidden_pre"], ["h_out"]),
        helper.make_node("MatMul", ["h_out", "v6_hidden_action_weight"], ["v6_hidden_action"]),
        helper.make_node("MatMul", ["calibration_context", "v6_context_action_weight"], ["v6_context_action"]),
        helper.make_node("Add", ["v6_hidden_action", "v6_context_action"], ["v6_adapter_sum"]),
        helper.make_node("Add", ["v6_adapter_sum", "v6_action_bias"], ["v6_adapter_pre"]),
        helper.make_node("Tanh", ["v6_adapter_pre"], ["v6_adapter_tanh"]),
        helper.make_node("Mul", ["v6_adapter_tanh", "v6_adapter_scale"], ["v6_adapter_delta"]),
        helper.make_node("Add", ["protected_continuous_actions", "v6_adapter_delta"], ["v6_proposed_action"]),
        helper.make_node("Clip", ["v6_proposed_action", "v6_action_minimum", "v6_action_maximum"], ["v6_absolute_action"]),
        helper.make_node("Sub", ["previous_action", "v6_max_action_delta"], ["v6_slew_min_raw"]),
        helper.make_node("Add", ["previous_action", "v6_max_action_delta"], ["v6_slew_max_raw"]),
        helper.make_node("Max", ["v6_slew_min_raw", "v6_action_minimum"], ["v6_slew_min"]),
        helper.make_node("Min", ["v6_slew_max_raw", "v6_action_maximum"], ["v6_slew_max"]),
        helper.make_node("Min", ["v6_absolute_action", "v6_slew_max"], ["v6_action_below_max"]),
        helper.make_node("Max", ["v6_action_below_max", "v6_slew_min"], ["continuous_actions"]),
        helper.make_node("Identity", ["continuous_actions"], ["previous_action_out"]),
    ])
    graph.output.extend([
        helper.make_tensor_value_info(
            "continuous_actions", TensorProto.FLOAT, [1, ACTION_SIZE]
        ),
        helper.make_tensor_value_info(
            "previous_action_out", TensorProto.FLOAT, [1, ACTION_SIZE]
        ),
        helper.make_tensor_value_info("h_out", TensorProto.FLOAT, [1, HIDDEN_SIZE]),
    ])
    graph.name = "winner_v6_response_conditioned_locomotion"
    model.producer_name = "open-duck-winner-v6"
    model.ir_version = min(model.ir_version, 10)
    onnx.checker.check_model(model)
    onnx.save(model, Path(output_path))
