"""Winner-v96 universal calibrator and response-conditioned locomotion graphs."""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any, Mapping

import jax
import jax.numpy as jnp
import numpy as np

import winner_v6_dynamic_calibration_networks as v6


OBS_SIZE = 115
ACTION_SIZE = 14
HIDDEN_SIZE = 64
CALIBRATION_TICKS = 250
ADAPTER_MAX_NORMALIZED = np.float32(0.25)


def initialize_locomotion_adapter_parameters(seed: int = 60721) -> dict[str, jax.Array]:
    return v6.initialize_locomotion_adapter_parameters(seed=seed)


def response_branch_step(
    parameters: Mapping[str, Any],
    obs: jax.Array,
    previous_action: jax.Array,
    h_in: jax.Array,
    calibration_context: jax.Array,
) -> tuple[jax.Array, jax.Array]:
    hidden_pre = (
        obs @ parameters["obs_weight"]
        + previous_action @ parameters["previous_action_weight"]
        + h_in @ parameters["hidden_weight"]
        + calibration_context @ parameters["context_hidden_weight"]
        + parameters["hidden_bias"]
    )
    h_out = jnp.tanh(hidden_pre)
    delta = jnp.tanh(
        h_out @ parameters["hidden_action_weight"]
        + calibration_context @ parameters["context_action_weight"]
        + parameters["action_bias"]
    ) * jnp.float32(ADAPTER_MAX_NORMALIZED)
    return h_out, delta


def bounded_universal_action(
    target: np.ndarray, previous_action: np.ndarray, maximum_delta: np.ndarray
) -> np.ndarray:
    target = np.asarray(target, dtype=np.float32)
    previous = np.asarray(previous_action, dtype=np.float32)
    delta = np.asarray(maximum_delta, dtype=np.float32)
    absolute = np.clip(target, np.float32(-1.0), np.float32(1.0))
    lower = np.maximum(previous - delta, np.float32(-1.0))
    upper = np.minimum(previous + delta, np.float32(1.0))
    return np.maximum(np.minimum(absolute, upper), lower).astype(np.float32)


def compose_final_action_numpy(
    protected_action: np.ndarray,
    adapter_delta: np.ndarray,
    observation: np.ndarray,
    previous_action: np.ndarray,
    initializers: Mapping[str, np.ndarray],
) -> np.ndarray:
    proposed = np.asarray(protected_action, dtype=np.float32) + np.asarray(
        adapter_delta, dtype=np.float32
    )
    maximum_delta = np.asarray(initializers["max_action_delta"], dtype=np.float32)
    previous = np.asarray(previous_action, dtype=np.float32)
    absolute = np.clip(proposed, np.float32(-1.0), np.float32(1.0))
    lower = np.maximum(previous - maximum_delta, np.float32(-1.0))
    upper = np.minimum(previous + maximum_delta, np.float32(1.0))
    velocity_bounded = np.maximum(np.minimum(absolute, upper), lower)
    obs = np.asarray(observation, dtype=np.float32)
    indices = np.asarray(initializers["guard_joint_obs_indices"], dtype=np.int64)
    home = np.asarray(initializers["guard_home"], dtype=np.float32)
    scale = np.asarray(initializers["guard_action_scale"], dtype=np.float32)
    actual_target = home + obs[:, indices]
    desired_target = home + velocity_bounded * scale
    target_min = actual_target - np.asarray(
        initializers["guard_margin"], dtype=np.float32
    )
    target_max = actual_target + np.asarray(
        initializers["guard_margin"], dtype=np.float32
    )
    clipped = np.minimum(np.maximum(desired_target, target_min), target_max)
    pitch_action = np.clip(
        (clipped - home) / scale,
        np.asarray(initializers["guard_action_min"], dtype=np.float32),
        np.asarray(initializers["guard_action_max"], dtype=np.float32),
    )
    guarded = np.where(
        np.asarray(initializers["guard_pitch_mask"], dtype=np.bool_),
        pitch_action,
        velocity_bounded,
    )
    command_index = np.asarray(
        initializers["deadband_command_index"], dtype=np.int64
    )
    zero_command = np.abs(obs[:, command_index]) <= np.asarray(
        initializers["deadband_abs_limit"], dtype=np.float32
    )
    return np.where(
        zero_command,
        np.asarray(initializers["deadband_zero_action"], dtype=np.float32),
        guarded,
    ).astype(np.float32)


def _rename_tensor(graph: Any, old: str, new: str) -> None:
    for node in graph.node:
        for index, name in enumerate(node.input):
            if name == old:
                node.input[index] = new
        for index, name in enumerate(node.output):
            if name == old:
                node.output[index] = new
    for collection in (graph.input, graph.output, graph.value_info):
        for value in collection:
            if value.name == old:
                value.name = new


def _add_array(initializers: Any, name: str, value: Any) -> None:
    from onnx import numpy_helper

    initializers.append(
        numpy_helper.from_array(np.asarray(value, dtype=np.float32), name=name)
    )


def _add_bool(initializers: Any, name: str, value: bool) -> None:
    from onnx import numpy_helper

    initializers.append(
        numpy_helper.from_array(np.asarray(value, dtype=np.bool_), name=name)
    )


def _initializer(model: Any, name: str) -> np.ndarray:
    from onnx import numpy_helper

    matches = [item for item in model.graph.initializer if item.name == name]
    if len(matches) != 1:
        raise ValueError(f"expected one initializer named {name}")
    return np.asarray(numpy_helper.to_array(matches[0]))


def export_universal_calibrator_onnx(
    source_path: str | Path,
    target: np.ndarray,
    output_path: str | Path,
) -> None:
    import onnx
    from onnx import TensorProto, helper

    model = copy.deepcopy(onnx.load(Path(source_path)))
    graph = model.graph
    inputs = {value.name: value for value in graph.input}
    outputs = {value.name: value for value in graph.output}
    if set(inputs) != {"obs", "previous_action", "h_in"} or set(outputs) != {
        "calibration_actions",
        "previous_action_out",
        "h_out",
    }:
        raise ValueError("Winner-v96 source calibrator ABI changed")
    maximum_delta = _initializer(model, "cal_max_action_delta")
    if maximum_delta.shape != (1, ACTION_SIZE):
        raise ValueError("Winner-v96 source calibrator boundary changed")
    _rename_tensor(graph, "calibration_actions", "v96_source_calibration_actions")
    _rename_tensor(graph, "previous_action_out", "v96_source_previous_action_out")
    del graph.output[:]
    _add_array(graph.initializer, "v96_universal_target", np.asarray(target)[None, :])
    _add_array(graph.initializer, "v96_action_minimum", np.asarray(-1.0, np.float32))
    _add_array(graph.initializer, "v96_action_maximum", np.asarray(1.0, np.float32))
    graph.node.extend(
        [
            helper.make_node(
                "Clip",
                ["v96_universal_target", "v96_action_minimum", "v96_action_maximum"],
                ["v96_absolute_target"],
            ),
            helper.make_node(
                "Sub", ["previous_action", "cal_max_action_delta"], ["v96_lower_raw"]
            ),
            helper.make_node(
                "Add", ["previous_action", "cal_max_action_delta"], ["v96_upper_raw"]
            ),
            helper.make_node(
                "Max", ["v96_lower_raw", "v96_action_minimum"], ["v96_lower"]
            ),
            helper.make_node(
                "Min", ["v96_upper_raw", "v96_action_maximum"], ["v96_upper"]
            ),
            helper.make_node(
                "Min", ["v96_absolute_target", "v96_upper"], ["v96_below_upper"]
            ),
            helper.make_node(
                "Max", ["v96_below_upper", "v96_lower"], ["calibration_actions"]
            ),
            helper.make_node(
                "Identity", ["calibration_actions"], ["previous_action_out"]
            ),
        ]
    )
    graph.output.extend(
        [
            helper.make_tensor_value_info(
                "calibration_actions", TensorProto.FLOAT, [1, ACTION_SIZE]
            ),
            helper.make_tensor_value_info(
                "previous_action_out", TensorProto.FLOAT, [1, ACTION_SIZE]
            ),
            helper.make_tensor_value_info("h_out", TensorProto.FLOAT, [1, HIDDEN_SIZE]),
        ]
    )
    graph.name = "winner_v96_universal_response_calibrator"
    model.producer_name = "open-duck-winner-v96"
    model.ir_version = min(model.ir_version, 10)
    onnx.checker.check_model(model)
    onnx.save(model, Path(output_path))


def export_locomotion_onnx(
    protected_path: str | Path,
    adapter_parameters: Mapping[str, Any],
    output_path: str | Path,
    *,
    adapter_enabled: bool,
    expose_adapter_delta: bool = False,
) -> None:
    import onnx
    from onnx import TensorProto, helper

    model = copy.deepcopy(onnx.load(Path(protected_path)))
    graph = model.graph
    if {value.name for value in graph.input} != {"obs", "previous_action"}:
        raise ValueError("Winner-v96 protected policy input ABI changed")
    if {value.name for value in graph.output} != {
        "continuous_actions",
        "previous_action_out",
    }:
        raise ValueError("Winner-v96 protected policy output ABI changed")
    _rename_tensor(graph, "continuous_actions", "v96_protected_action")
    _rename_tensor(graph, "previous_action_out", "v96_protected_previous_action")
    del graph.output[:]
    graph.input.extend(
        [
            helper.make_tensor_value_info("h_in", TensorProto.FLOAT, [1, HIDDEN_SIZE]),
            helper.make_tensor_value_info(
                "calibration_context", TensorProto.FLOAT, [1, HIDDEN_SIZE]
            ),
        ]
    )
    for name in (
        "obs_weight",
        "previous_action_weight",
        "hidden_weight",
        "context_hidden_weight",
        "hidden_bias",
        "hidden_action_weight",
        "context_action_weight",
        "action_bias",
    ):
        _add_array(graph.initializer, f"v96_{name}", adapter_parameters[name])
    _add_array(
        graph.initializer,
        "v96_adapter_max_normalized",
        np.asarray(ADAPTER_MAX_NORMALIZED, np.float32),
    )
    _add_array(graph.initializer, "v96_action_minimum", np.asarray(-1.0, np.float32))
    _add_array(graph.initializer, "v96_action_maximum", np.asarray(1.0, np.float32))
    _add_bool(graph.initializer, "v96_adapter_enabled", adapter_enabled)
    graph.node.extend(
        [
            helper.make_node("MatMul", ["obs", "v96_obs_weight"], ["v96_obs_hidden"]),
            helper.make_node(
                "MatMul",
                ["previous_action", "v96_previous_action_weight"],
                ["v96_previous_hidden"],
            ),
            helper.make_node(
                "MatMul", ["h_in", "v96_hidden_weight"], ["v96_state_hidden"]
            ),
            helper.make_node(
                "MatMul",
                ["calibration_context", "v96_context_hidden_weight"],
                ["v96_context_hidden"],
            ),
            helper.make_node(
                "Add", ["v96_obs_hidden", "v96_previous_hidden"], ["v96_hidden_0"]
            ),
            helper.make_node(
                "Add", ["v96_hidden_0", "v96_state_hidden"], ["v96_hidden_1"]
            ),
            helper.make_node(
                "Add", ["v96_hidden_1", "v96_context_hidden"], ["v96_hidden_2"]
            ),
            helper.make_node(
                "Add", ["v96_hidden_2", "v96_hidden_bias"], ["v96_hidden_pre"]
            ),
            helper.make_node("Tanh", ["v96_hidden_pre"], ["h_out"]),
            helper.make_node(
                "MatMul",
                ["h_out", "v96_hidden_action_weight"],
                ["v96_hidden_action"],
            ),
            helper.make_node(
                "MatMul",
                ["calibration_context", "v96_context_action_weight"],
                ["v96_context_action"],
            ),
            helper.make_node(
                "Add", ["v96_hidden_action", "v96_context_action"], ["v96_delta_0"]
            ),
            helper.make_node(
                "Add", ["v96_delta_0", "v96_action_bias"], ["v96_delta_pre"]
            ),
            helper.make_node("Tanh", ["v96_delta_pre"], ["v96_delta_tanh"]),
            helper.make_node(
                "Mul",
                ["v96_delta_tanh", "v96_adapter_max_normalized"],
                ["v96_adapter_delta"],
            ),
            helper.make_node(
                "Add", ["v96_protected_action", "v96_adapter_delta"], ["v96_proposed"]
            ),
            helper.make_node(
                "Clip",
                ["v96_proposed", "v96_action_minimum", "v96_action_maximum"],
                ["v96_absolute"],
            ),
            helper.make_node(
                "Sub", ["previous_action", "max_action_delta"], ["v96_rate_lower_raw"]
            ),
            helper.make_node(
                "Add", ["previous_action", "max_action_delta"], ["v96_rate_upper_raw"]
            ),
            helper.make_node(
                "Max", ["v96_rate_lower_raw", "v96_action_minimum"], ["v96_rate_lower"]
            ),
            helper.make_node(
                "Min", ["v96_rate_upper_raw", "v96_action_maximum"], ["v96_rate_upper"]
            ),
            helper.make_node(
                "Min", ["v96_absolute", "v96_rate_upper"], ["v96_rate_below"]
            ),
            helper.make_node(
                "Max", ["v96_rate_below", "v96_rate_lower"], ["v96_rate_bounded"]
            ),
            helper.make_node(
                "Gather",
                ["obs", "guard_joint_obs_indices"],
                ["v96_joint_offsets"],
                axis=1,
            ),
            helper.make_node(
                "Add", ["guard_home", "v96_joint_offsets"], ["v96_actual_target"]
            ),
            helper.make_node(
                "Mul",
                ["v96_rate_bounded", "guard_action_scale"],
                ["v96_target_delta"],
            ),
            helper.make_node(
                "Add", ["guard_home", "v96_target_delta"], ["v96_desired_target"]
            ),
            helper.make_node(
                "Sub", ["v96_actual_target", "guard_margin"], ["v96_target_min"]
            ),
            helper.make_node(
                "Add", ["v96_actual_target", "guard_margin"], ["v96_target_max"]
            ),
            helper.make_node(
                "Max", ["v96_desired_target", "v96_target_min"], ["v96_target_above"]
            ),
            helper.make_node(
                "Min", ["v96_target_above", "v96_target_max"], ["v96_target_clipped"]
            ),
            helper.make_node(
                "Sub", ["v96_target_clipped", "guard_home"], ["v96_guard_delta"]
            ),
            helper.make_node(
                "Div", ["v96_guard_delta", "guard_action_scale"], ["v96_pitch_raw"]
            ),
            helper.make_node(
                "Clip",
                ["v96_pitch_raw", "guard_action_min", "guard_action_max"],
                ["v96_pitch_action"],
            ),
            helper.make_node(
                "Where",
                ["guard_pitch_mask", "v96_pitch_action", "v96_rate_bounded"],
                ["v96_guarded_action"],
            ),
            helper.make_node(
                "Gather",
                ["obs", "deadband_command_index"],
                ["v96_command_x"],
                axis=1,
            ),
            helper.make_node("Abs", ["v96_command_x"], ["v96_abs_command_x"]),
            helper.make_node(
                "LessOrEqual",
                ["v96_abs_command_x", "deadband_abs_limit"],
                ["v96_zero_command"],
            ),
            helper.make_node(
                "Where",
                ["v96_zero_command", "deadband_zero_action", "v96_guarded_action"],
                ["v96_enabled_action"],
            ),
            helper.make_node(
                "Where",
                ["v96_adapter_enabled", "v96_enabled_action", "v96_protected_action"],
                ["continuous_actions"],
            ),
            helper.make_node(
                "Identity", ["continuous_actions"], ["previous_action_out"]
            ),
        ]
    )
    graph.output.extend(
        [
            helper.make_tensor_value_info(
                "continuous_actions", TensorProto.FLOAT, [1, ACTION_SIZE]
            ),
            helper.make_tensor_value_info(
                "previous_action_out", TensorProto.FLOAT, [1, ACTION_SIZE]
            ),
            helper.make_tensor_value_info("h_out", TensorProto.FLOAT, [1, HIDDEN_SIZE]),
        ]
    )
    if expose_adapter_delta:
        graph.output.extend(
            [
                helper.make_tensor_value_info(
                    "v96_adapter_delta", TensorProto.FLOAT, [1, ACTION_SIZE]
                )
            ]
        )
    graph.name = "winner_v96_response_conditioned_locomotion"
    model.producer_name = "open-duck-winner-v96"
    model.ir_version = min(model.ir_version, 10)
    onnx.checker.check_model(model)
    onnx.save(model, Path(output_path))


def validate_calibration_handoff(
    h_out: np.ndarray,
    *,
    completed_ticks: int,
    all_ticks_valid: bool,
    support_valid: bool,
) -> np.ndarray:
    return v6.validate_calibration_handoff(
        h_out,
        completed_ticks=completed_ticks,
        all_ticks_valid=all_ticks_valid,
        support_valid=support_valid,
    )
