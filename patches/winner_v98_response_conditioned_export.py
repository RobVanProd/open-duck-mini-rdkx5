"""Export a trained Winner-v98 adapter around the selected protected ONNX graph."""

from __future__ import annotations

import copy
import hashlib
from pathlib import Path
from typing import Any

import numpy as np

from playground.common.winner_v98_response_conditioned_ppo_networks import (
    ACTION_SIZE,
    ADAPTER_MAX_NORMALIZED,
    HIDDEN_SIZE,
    adapter_parameters_from_flax,
)


PROTECTED_POLICY_SHA256 = (
    "99d3afce0dfac127816c6327665c35b3c403e005f25cd0a505dfcb37f01304de"
)


def validate_protected_policy_path(path: str | Path) -> Path:
    source = Path(path)
    if hashlib.sha256(source.read_bytes()).hexdigest() != PROTECTED_POLICY_SHA256:
        raise ValueError("Winner-v98 protected policy SHA-256 changed")
    return source


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


def export_response_conditioned_onnx(
    params: Any,
    protected_policy_path: str | Path,
    output_path: str | Path,
) -> dict[str, Any]:
    import onnx
    from onnx import TensorProto, helper

    adapter = adapter_parameters_from_flax(params[1])
    model = copy.deepcopy(onnx.load(validate_protected_policy_path(protected_policy_path)))
    graph = model.graph
    if {value.name for value in graph.input} != {"obs", "previous_action"}:
        raise ValueError("Winner-v98 protected policy input ABI changed")
    if {value.name for value in graph.output} != {
        "continuous_actions",
        "previous_action_out",
    }:
        raise ValueError("Winner-v98 protected policy output ABI changed")
    _rename_tensor(graph, "continuous_actions", "v98_protected_action")
    _rename_tensor(graph, "previous_action_out", "v98_protected_previous_action")
    del graph.output[:]
    graph.input.extend(
        [
            helper.make_tensor_value_info("h_in", TensorProto.FLOAT, [1, HIDDEN_SIZE]),
            helper.make_tensor_value_info(
                "calibration_context", TensorProto.FLOAT, [1, HIDDEN_SIZE]
            ),
        ]
    )
    for name, value in adapter.items():
        _add_array(graph.initializer, f"v98_{name}", value)
    _add_array(
        graph.initializer,
        "v98_adapter_max_normalized",
        np.asarray(ADAPTER_MAX_NORMALIZED, dtype=np.float32),
    )
    _add_array(graph.initializer, "v98_action_minimum", np.asarray(-1.0, np.float32))
    _add_array(graph.initializer, "v98_action_maximum", np.asarray(1.0, np.float32))
    graph.node.extend(
        [
            helper.make_node("MatMul", ["obs", "v98_obs_weight"], ["v98_obs_hidden"]),
            helper.make_node(
                "MatMul",
                ["previous_action", "v98_previous_action_weight"],
                ["v98_previous_hidden"],
            ),
            helper.make_node(
                "MatMul", ["h_in", "v98_hidden_weight"], ["v98_state_hidden"]
            ),
            helper.make_node(
                "MatMul",
                ["calibration_context", "v98_context_hidden_weight"],
                ["v98_context_hidden"],
            ),
            helper.make_node(
                "Add", ["v98_obs_hidden", "v98_previous_hidden"], ["v98_hidden_0"]
            ),
            helper.make_node(
                "Add", ["v98_hidden_0", "v98_state_hidden"], ["v98_hidden_1"]
            ),
            helper.make_node(
                "Add", ["v98_hidden_1", "v98_context_hidden"], ["v98_hidden_2"]
            ),
            helper.make_node(
                "Add", ["v98_hidden_2", "v98_hidden_bias"], ["v98_hidden_pre"]
            ),
            helper.make_node("Tanh", ["v98_hidden_pre"], ["h_out"]),
            helper.make_node(
                "MatMul",
                ["h_out", "v98_hidden_action_weight"],
                ["v98_hidden_action"],
            ),
            helper.make_node(
                "MatMul",
                ["calibration_context", "v98_context_action_weight"],
                ["v98_context_action"],
            ),
            helper.make_node(
                "Add", ["v98_hidden_action", "v98_context_action"], ["v98_delta_0"]
            ),
            helper.make_node(
                "Add", ["v98_delta_0", "v98_action_bias"], ["v98_delta_pre"]
            ),
            helper.make_node("Tanh", ["v98_delta_pre"], ["v98_delta_tanh"]),
            helper.make_node(
                "Mul",
                ["v98_delta_tanh", "v98_adapter_max_normalized"],
                ["v98_adapter_delta"],
            ),
            helper.make_node(
                "Add", ["v98_protected_action", "v98_adapter_delta"], ["v98_proposed"]
            ),
            helper.make_node(
                "Clip",
                ["v98_proposed", "v98_action_minimum", "v98_action_maximum"],
                ["v98_absolute"],
            ),
            helper.make_node(
                "Sub", ["previous_action", "max_action_delta"], ["v98_rate_lower_raw"]
            ),
            helper.make_node(
                "Add", ["previous_action", "max_action_delta"], ["v98_rate_upper_raw"]
            ),
            helper.make_node(
                "Max", ["v98_rate_lower_raw", "v98_action_minimum"], ["v98_rate_lower"]
            ),
            helper.make_node(
                "Min", ["v98_rate_upper_raw", "v98_action_maximum"], ["v98_rate_upper"]
            ),
            helper.make_node("Min", ["v98_absolute", "v98_rate_upper"], ["v98_rate_below"]),
            helper.make_node("Max", ["v98_rate_below", "v98_rate_lower"], ["v98_rate_bounded"]),
            helper.make_node(
                "Gather", ["obs", "guard_joint_obs_indices"], ["v98_joint_offsets"], axis=1
            ),
            helper.make_node("Add", ["guard_home", "v98_joint_offsets"], ["v98_actual_target"]),
            helper.make_node(
                "Mul", ["v98_rate_bounded", "guard_action_scale"], ["v98_target_delta"]
            ),
            helper.make_node("Add", ["guard_home", "v98_target_delta"], ["v98_desired_target"]),
            helper.make_node("Sub", ["v98_actual_target", "guard_margin"], ["v98_target_min"]),
            helper.make_node("Add", ["v98_actual_target", "guard_margin"], ["v98_target_max"]),
            helper.make_node("Max", ["v98_desired_target", "v98_target_min"], ["v98_target_above"]),
            helper.make_node("Min", ["v98_target_above", "v98_target_max"], ["v98_target_clipped"]),
            helper.make_node("Sub", ["v98_target_clipped", "guard_home"], ["v98_guard_delta"]),
            helper.make_node("Div", ["v98_guard_delta", "guard_action_scale"], ["v98_pitch_raw"]),
            helper.make_node(
                "Clip",
                ["v98_pitch_raw", "guard_action_min", "guard_action_max"],
                ["v98_pitch_action"],
            ),
            helper.make_node(
                "Where",
                ["guard_pitch_mask", "v98_pitch_action", "v98_rate_bounded"],
                ["v98_guarded_action"],
            ),
            helper.make_node(
                "Gather", ["obs", "deadband_command_index"], ["v98_command_x"], axis=1
            ),
            helper.make_node("Abs", ["v98_command_x"], ["v98_abs_command_x"]),
            helper.make_node(
                "LessOrEqual",
                ["v98_abs_command_x", "deadband_abs_limit"],
                ["v98_zero_command"],
            ),
            helper.make_node(
                "Where",
                ["v98_zero_command", "deadband_zero_action", "v98_guarded_action"],
                ["continuous_actions"],
            ),
            helper.make_node("Identity", ["continuous_actions"], ["previous_action_out"]),
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
    graph.name = "winner_v98_response_conditioned_locomotion"
    model.producer_name = "open-duck-winner-v98"
    model.ir_version = min(model.ir_version, 10)
    onnx.checker.check_model(model)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    onnx.save(model, output)
    return {
        "path": str(output),
        "inputs": [item.name for item in graph.input],
        "outputs": [item.name for item in graph.output],
    }
