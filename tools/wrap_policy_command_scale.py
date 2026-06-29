#!/usr/bin/env python3
"""Wrap an ONNX policy with command-x-dependent action scaling.

This is an offline analysis helper. It does not train, deploy, SSH, or touch the
robot. By default the wrapper preserves the original policy graph and appends:

  scale = low_scale + (high_scale - low_scale) * clip(abs(obs[command_x_index]) / ramp_command_x, 0, 1)
  action = base_action * scale
  action = action * joint_action_scale

Optionally, the scaled action can be converted to a motor target, blended toward
obs[83:97] (the previous sent motor target), velocity-clamped relative to that
same previous target, and converted back to action:

  target = home + scaled_action * action_scale
  target = prev_target + alpha * (target - prev_target)
  target = prev_target + clip(target - prev_target, -limit * dt, limit * dt)
  action = clip((target - home) / action_scale, -1, 1)

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
    parser.add_argument(
        "--joint-action-scale",
        default=None,
        help=(
            "optional comma-separated 14-joint per-joint action scale factors "
            "applied after command scaling; omitted means all ones"
        ),
    )
    parser.add_argument(
        "--target-blend-alpha",
        type=float,
        default=1.0,
        help=(
            "blend factor for desired target relative to obs[83:97] previous "
            "sent target; 1.0 disables target smoothing"
        ),
    )
    parser.add_argument("--previous-target-start", type=int, default=83)
    parser.add_argument("--action-scale-rad", type=float, default=0.25)
    parser.add_argument(
        "--target-delta-limit-rad-s",
        default=None,
        help=(
            "optional comma-separated 14-joint per-joint target velocity limits "
            "in rad/s; clamps target delta relative to obs[83:97] using --control-dt-s"
        ),
    )
    parser.add_argument("--control-dt-s", type=float, default=0.02)
    parser.add_argument(
        "--home",
        default=(
            "0.002,0.053,-0.63,1.368,-0.784,0,0,0,0,"
            "-0.003,-0.065,0.635,1.379,-0.796"
        ),
        help="comma-separated 14-joint home/default actuator target in radians",
    )
    return parser.parse_args()


def parse_float_vector(text: str, *, expected: int, name: str) -> np.ndarray:
    values = [float(part.strip()) for part in text.split(",") if part.strip()]
    if len(values) != expected:
        raise SystemExit(f"{name} expected {expected} values, got {len(values)}")
    return np.asarray(values, dtype=np.float32)


def main() -> int:
    args = parse_args()
    if args.ramp_command_x <= 0.0:
        raise SystemExit("--ramp-command-x must be positive")
    if not 0.0 < args.target_blend_alpha <= 1.0:
        raise SystemExit("--target-blend-alpha must be in (0, 1]")
    if args.action_scale_rad <= 0.0:
        raise SystemExit("--action-scale-rad must be positive")
    if args.control_dt_s <= 0.0:
        raise SystemExit("--control-dt-s must be positive")

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

    joint_action_scale = (
        parse_float_vector(args.joint_action_scale, expected=14, name="--joint-action-scale")
        if args.joint_action_scale
        else np.ones((14,), dtype=np.float32)
    )

    initializers = {
        "command_x_index": np.asarray([args.command_x_index], dtype=np.int64),
        "command_scale_low": np.asarray([args.low_scale], dtype=np.float32),
        "command_scale_delta": np.asarray(
            [args.high_scale - args.low_scale], dtype=np.float32
        ),
        "command_scale_ramp": np.asarray([args.ramp_command_x], dtype=np.float32),
        "command_scale_clip_min": np.asarray([0.0], dtype=np.float32),
        "command_scale_clip_max": np.asarray([1.0], dtype=np.float32),
        "joint_action_scale": joint_action_scale.reshape(1, 14),
    }
    use_target_stage = args.target_blend_alpha < 1.0 or args.target_delta_limit_rad_s
    if use_target_stage:
        home = parse_float_vector(args.home, expected=14, name="--home")
        initializers.update(
            {
                "previous_target_indices": np.arange(
                    args.previous_target_start,
                    args.previous_target_start + 14,
                    dtype=np.int64,
                ),
                "target_home": home.reshape(1, 14),
                "target_action_scale": np.asarray(
                    [args.action_scale_rad], dtype=np.float32
                ),
                "target_blend_alpha": np.asarray(
                    [args.target_blend_alpha], dtype=np.float32
                ),
                "target_clip_min": np.asarray([-1.0], dtype=np.float32),
                "target_clip_max": np.asarray([1.0], dtype=np.float32),
            }
        )
        if args.target_delta_limit_rad_s:
            limits = parse_float_vector(
                args.target_delta_limit_rad_s,
                expected=14,
                name="--target-delta-limit-rad-s",
            )
            if np.any(limits <= 0.0):
                raise SystemExit("--target-delta-limit-rad-s values must be positive")
            delta = limits * float(args.control_dt_s)
            initializers.update(
                {
                    "target_delta_limit_min": (-delta).reshape(1, 14),
                    "target_delta_limit_max": delta.reshape(1, 14),
                }
            )
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
                ["command_scaled_actions"],
                name="command_scale_actions",
            ),
            helper.make_node(
                "Mul",
                ["command_scaled_actions", "joint_action_scale"],
                ["joint_scaled_actions"],
                name="joint_scale_actions",
            ),
        ]
    )
    if use_target_stage:
        target_after_blend = "target_delta_blended"
        graph.node.extend(
            [
                helper.make_node(
                    "Mul",
                    ["joint_scaled_actions", "target_action_scale"],
                    ["desired_target_delta"],
                    name="target_smooth_scale_action",
                ),
                helper.make_node(
                    "Add",
                    ["target_home", "desired_target_delta"],
                    ["desired_target"],
                    name="target_smooth_desired_target",
                ),
                helper.make_node(
                    "Gather",
                    [obs_name, "previous_target_indices"],
                    ["previous_target"],
                    name="target_smooth_gather_previous",
                    axis=1,
                ),
                helper.make_node(
                    "Sub",
                    ["desired_target", "previous_target"],
                    ["target_delta_from_previous"],
                    name="target_smooth_delta",
                ),
                helper.make_node(
                    "Mul",
                    ["target_delta_from_previous", "target_blend_alpha"],
                    ["target_delta_blended"],
                    name="target_smooth_apply_alpha",
                ),
            ]
        )
        if args.target_delta_limit_rad_s:
            target_after_blend = "target_delta_limited"
            graph.node.extend(
                [
                    helper.make_node(
                        "Max",
                        ["target_delta_blended", "target_delta_limit_min"],
                        ["target_delta_limited_lower"],
                        name="target_delta_limit_lower",
                    ),
                    helper.make_node(
                        "Min",
                        ["target_delta_limited_lower", "target_delta_limit_max"],
                        ["target_delta_limited"],
                        name="target_delta_limit_upper",
                    )
                ]
            )
        graph.node.extend(
            [
                helper.make_node(
                    "Add",
                    ["previous_target", target_after_blend],
                    ["smoothed_target"],
                    name="target_smooth_add_previous",
                ),
                helper.make_node(
                    "Sub",
                    ["smoothed_target", "target_home"],
                    ["smoothed_action_delta"],
                    name="target_smooth_remove_home",
                ),
                helper.make_node(
                    "Div",
                    ["smoothed_action_delta", "target_action_scale"],
                    ["smoothed_actions_unclipped"],
                    name="target_smooth_to_action",
                ),
                helper.make_node(
                    "Clip",
                    ["smoothed_actions_unclipped", "target_clip_min", "target_clip_max"],
                    [wrapped_output],
                    name="target_smooth_clip_action",
                ),
            ]
        )
    else:
        graph.node.extend(
            [
                helper.make_node(
                    "Identity",
                    ["joint_scaled_actions"],
                    [wrapped_output],
                    name="command_scale_output_identity",
                )
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
    if args.joint_action_scale:
        print(f"joint action scale: {','.join(f'{value:g}' for value in joint_action_scale)}")
    if args.target_blend_alpha < 1.0:
        print(
            "target smoothing: "
            f"target = obs[{args.previous_target_start}:{args.previous_target_start + 14}] "
            f"+ {args.target_blend_alpha:g} * (desired_target - previous_target)"
        )
    if args.target_delta_limit_rad_s:
        print(
            "target delta limit: "
            f"clip(target - previous_target, +/- limit_rad_s * {args.control_dt_s:g})"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
