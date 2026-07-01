#!/usr/bin/env python3
"""Compose two ONNX policies with a command-x gate.

This offline helper builds a single deployable feed-forward ONNX graph:

  obs[1,101] -> continuous_actions[1,14]

The low-command policy is used near zero command, and the high-command policy is
used near the configured command ramp:

  high_weight = clip(abs(obs[command_x_index]) / ramp_command_x, 0, 1)
  action = low_action * (1 - high_weight) + high_action * high_weight

It does not train, deploy, SSH, or touch the robot. It is intended for
diagnostic candidate composition after separate low-command recovery and
nonzero-command walking components have each passed their local offline gates.
"""

from __future__ import annotations

import argparse
import copy
from pathlib import Path

import numpy as np


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--low-policy", required=True, help="ONNX policy used at command_x ~= 0")
    parser.add_argument("--high-policy", required=True, help="ONNX policy used at command_x >= ramp")
    parser.add_argument("--output", required=True, help="output composed ONNX policy")
    parser.add_argument("--command-x-index", type=int, default=6)
    parser.add_argument("--ramp-command-x", type=float, default=0.08)
    parser.add_argument("--output-name", default="continuous_actions")
    parser.add_argument("--low-prefix", default="low")
    parser.add_argument("--high-prefix", default="high")
    return parser.parse_args()


def prefixed(name: str, prefix: str) -> str:
    return f"{prefix}__{name}"


def clone_policy_graph(model, *, prefix: str, shared_input: str) -> tuple[list, list, str]:
    if len(model.graph.input) != 1:
        raise SystemExit(f"{prefix} policy must have exactly one input")
    if len(model.graph.output) != 1:
        raise SystemExit(f"{prefix} policy must have exactly one output")
    input_name = model.graph.input[0].name
    output_name = model.graph.output[0].name
    initializer_names = {item.name for item in model.graph.initializer}

    def rename_value(name: str) -> str:
        if name == "":
            return name
        if name == input_name and name not in initializer_names:
            return shared_input
        return prefixed(name, prefix)

    nodes = []
    for node in model.graph.node:
        cloned = copy.deepcopy(node)
        cloned.name = prefixed(cloned.name or cloned.op_type, prefix)
        cloned.input[:] = [rename_value(name) for name in cloned.input]
        cloned.output[:] = [rename_value(name) for name in cloned.output]
        nodes.append(cloned)

    initializers = []
    for initializer in model.graph.initializer:
        cloned = copy.deepcopy(initializer)
        cloned.name = prefixed(cloned.name, prefix)
        initializers.append(cloned)

    return nodes, initializers, rename_value(output_name)


def main() -> int:
    args = parse_args()
    if args.ramp_command_x <= 0.0:
        raise SystemExit("--ramp-command-x must be positive")
    if args.low_prefix == args.high_prefix:
        raise SystemExit("--low-prefix and --high-prefix must differ")

    import onnx
    from onnx import TensorProto, helper, numpy_helper

    low = onnx.load(args.low_policy)
    high = onnx.load(args.high_policy)
    shared_input = "obs"
    low_input = low.graph.input[0]
    high_input = high.graph.input[0]
    if [d.dim_value for d in low_input.type.tensor_type.shape.dim] != [1, 101]:
        raise SystemExit("--low-policy input must be shaped [1,101]")
    if [d.dim_value for d in high_input.type.tensor_type.shape.dim] != [1, 101]:
        raise SystemExit("--high-policy input must be shaped [1,101]")

    low_nodes, low_initializers, low_output = clone_policy_graph(
        low, prefix=args.low_prefix, shared_input=shared_input
    )
    high_nodes, high_initializers, high_output = clone_policy_graph(
        high, prefix=args.high_prefix, shared_input=shared_input
    )

    gate_initializers = [
        numpy_helper.from_array(np.asarray([args.command_x_index], dtype=np.int64), name="gate_command_x_index"),
        numpy_helper.from_array(np.asarray([args.ramp_command_x], dtype=np.float32), name="gate_ramp_command_x"),
        numpy_helper.from_array(np.asarray([0.0], dtype=np.float32), name="gate_clip_min"),
        numpy_helper.from_array(np.asarray([1.0], dtype=np.float32), name="gate_clip_max"),
        numpy_helper.from_array(np.asarray([1.0], dtype=np.float32), name="gate_one"),
    ]
    gate_nodes = [
        helper.make_node(
            "Gather",
            [shared_input, "gate_command_x_index"],
            ["gate_command_x"],
            name="gate_gather_command_x",
            axis=1,
        ),
        helper.make_node("Abs", ["gate_command_x"], ["gate_abs_command_x"], name="gate_abs"),
        helper.make_node(
            "Div",
            ["gate_abs_command_x", "gate_ramp_command_x"],
            ["gate_raw_high_weight"],
            name="gate_div_ramp",
        ),
        helper.make_node(
            "Clip",
            ["gate_raw_high_weight", "gate_clip_min", "gate_clip_max"],
            ["gate_high_weight"],
            name="gate_clip_high_weight",
        ),
        helper.make_node(
            "Sub",
            ["gate_one", "gate_high_weight"],
            ["gate_low_weight"],
            name="gate_low_weight",
        ),
        helper.make_node(
            "Mul",
            [low_output, "gate_low_weight"],
            ["gate_weighted_low_action"],
            name="gate_weight_low_action",
        ),
        helper.make_node(
            "Mul",
            [high_output, "gate_high_weight"],
            ["gate_weighted_high_action"],
            name="gate_weight_high_action",
        ),
        helper.make_node(
            "Add",
            ["gate_weighted_low_action", "gate_weighted_high_action"],
            [args.output_name],
            name="gate_add_actions",
        ),
    ]

    input_info = helper.make_tensor_value_info(shared_input, TensorProto.FLOAT, [1, 101])
    output_info = helper.make_tensor_value_info(args.output_name, TensorProto.FLOAT, [1, 14])
    graph = helper.make_graph(
        [*low_nodes, *high_nodes, *gate_nodes],
        "command_gated_policy",
        [input_info],
        [output_info],
        [*low_initializers, *high_initializers, *gate_initializers],
    )
    opsets = {item.domain: item.version for item in list(low.opset_import) + list(high.opset_import)}
    opsets[""] = max(opsets.get("", 13), 13)
    model = helper.make_model(
        graph,
        opset_imports=[helper.make_operatorsetid(domain, version) for domain, version in sorted(opsets.items())],
    )
    model.ir_version = max(low.ir_version, high.ir_version)
    model.metadata_props.add(key="low_policy", value=str(args.low_policy))
    model.metadata_props.add(key="high_policy", value=str(args.high_policy))
    model.metadata_props.add(key="command_x_index", value=str(args.command_x_index))
    model.metadata_props.add(key="ramp_command_x", value=str(args.ramp_command_x))

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    onnx.checker.check_model(model)
    onnx.save(model, output_path)
    print(output_path)
    print(
        "high_weight = "
        f"clip(abs(obs[{args.command_x_index}]) / {args.ramp_command_x:g}, 0, 1)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
