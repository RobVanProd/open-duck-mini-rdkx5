#!/usr/bin/env python3
"""Wrap an ONNX policy with command-x-dependent action scaling.

This is an offline analysis helper. It does not train, deploy, SSH, or touch the
robot. The wrapper preserves the original policy graph and appends:

  scale = low_scale + (high_scale - low_scale) * clip(abs(obs[command_x_index]) / ramp_command_x, 0, 1)
  action = base_action * scale

The intended use is to test whether a standstill-stabilizing scale near
command_x=0 can coexist with full source policy action at command_x=0.08.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Append command-x action scaling to an ONNX policy."
    )
    parser.add_argument("--input", required=True, help="input ONNX policy")
    parser.add_argument("--output", required=True, help="output wrapped ONNX policy")
    parser.add_argument("--command-x-index", type=int, default=6)
    parser.add_argument("--low-scale", type=float, default=0.75)
    parser.add_argument("--high-scale", type=float, default=1.0)
    parser.add_argument("--ramp-command-x", type=float, default=0.08)
    parser.add_argument(
        "--output-name",
        default="continuous_actions_command_scaled",
        help="name for the wrapped policy output",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.ramp_command_x <= 0.0:
        raise SystemExit("--ramp-command-x must be positive")

    import onnx
    from onnx import TensorProto, helper, numpy_helper

    input_path = Path(args.input)
    output_path = Path(args.output)
    model = onnx.load(input_path)
    graph = model.graph
    if not graph.input:
        raise SystemExit(f"{input_path} has no graph inputs")
    if not graph.output:
        raise SystemExit(f"{input_path} has no graph outputs")

    obs_name = graph.input[0].name
    base_output = graph.output[0].name
    wrapped_output = args.output_name
    if wrapped_output == base_output:
        raise SystemExit("--output-name must differ from the base policy output")

    initializers = {
        "command_x_index": np.asarray([args.command_x_index], dtype=np.int64),
        "command_scale_low": np.asarray([args.low_scale], dtype=np.float32),
        "command_scale_delta": np.asarray(
            [args.high_scale - args.low_scale], dtype=np.float32
        ),
        "command_scale_ramp": np.asarray([args.ramp_command_x], dtype=np.float32),
        "command_scale_clip_min": np.asarray([0.0], dtype=np.float32),
        "command_scale_clip_max": np.asarray([1.0], dtype=np.float32),
    }
    for name, value in initializers.items():
        graph.initializer.append(numpy_helper.from_array(value, name=name))

    graph.node.extend(
        [
            helper.make_node(
                "Gather",
                [obs_name, "command_x_index"],
                ["command_x_col"],
                name="command_scale_gather_x",
                axis=1,
            ),
            helper.make_node(
                "Abs",
                ["command_x_col"],
                ["command_x_abs"],
                name="command_scale_abs_x",
            ),
            helper.make_node(
                "Div",
                ["command_x_abs", "command_scale_ramp"],
                ["command_x_ramp_unit"],
                name="command_scale_div_ramp",
            ),
            helper.make_node(
                "Clip",
                [
                    "command_x_ramp_unit",
                    "command_scale_clip_min",
                    "command_scale_clip_max",
                ],
                ["command_x_ramp_clipped"],
                name="command_scale_clip",
            ),
            helper.make_node(
                "Mul",
                ["command_x_ramp_clipped", "command_scale_delta"],
                ["command_scale_delta_applied"],
                name="command_scale_mul_delta",
            ),
            helper.make_node(
                "Add",
                ["command_scale_low", "command_scale_delta_applied"],
                ["command_action_scale"],
                name="command_scale_add_low",
            ),
            helper.make_node(
                "Mul",
                [base_output, "command_action_scale"],
                [wrapped_output],
                name="command_scale_actions",
            ),
        ]
    )

    original_output = graph.output[0]
    graph.output.remove(original_output)
    graph.output.append(
        helper.make_tensor_value_info(wrapped_output, TensorProto.FLOAT, [1, 14])
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    onnx.checker.check_model(model)
    onnx.save(model, output_path)
    print(output_path)
    print(
        "scale = "
        f"{args.low_scale:g} + ({args.high_scale:g} - {args.low_scale:g}) "
        f"* clip(abs(obs[{args.command_x_index}]) / {args.ramp_command_x:g}, 0, 1)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
