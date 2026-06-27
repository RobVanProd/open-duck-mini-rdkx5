#!/usr/bin/env python3
"""Wrap two ONNX policies with an obs[command_x]-based hard gate.

This is an offline diagnostic helper. It does not train, deploy, SSH, or touch
the robot. The wrapper preserves the deployed policy contract:

  obs[1,101] -> continuous_actions[1,14]

For small absolute forward command it returns the low-command policy action.
For larger command it returns the high-command policy action:

  action = where(abs(obs[command_x_index]) <= threshold,
                 low_command_policy(obs),
                 high_command_policy(obs))

The intended use is to test whether zero-command safety can be separated from
the moving-policy tracking plateau without silently padding, truncating, or
changing the runtime observation/action contract.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create an ONNX policy that gates between two policies by command_x."
    )
    parser.add_argument("--low-command-policy", required=True, help="ONNX used near command_x=0")
    parser.add_argument("--high-command-policy", required=True, help="ONNX used above threshold")
    parser.add_argument("--output", required=True, help="output gated ONNX path")
    parser.add_argument("--command-x-index", type=int, default=6)
    parser.add_argument("--threshold", type=float, default=0.02)
    parser.add_argument("--output-name", default="continuous_actions")
    parser.add_argument("--verify-json", help="optional JSON verification report")
    return parser.parse_args()


def tensor_shape(value_info: Any) -> list[int | str | None]:
    shape = value_info.type.tensor_type.shape
    out: list[int | str | None] = []
    for dim in shape.dim:
        if dim.HasField("dim_value"):
            out.append(int(dim.dim_value))
        elif dim.HasField("dim_param"):
            out.append(str(dim.dim_param))
        else:
            out.append(None)
    return out


def prefixed(name: str, prefix: str, obs_name: str) -> str:
    if name == obs_name:
        return "obs"
    return f"{prefix}{name}"


def clone_graph_into(
    target_graph: Any,
    source_model: Any,
    *,
    prefix: str,
    output_alias: str,
) -> None:
    """Append source graph nodes/initializers to target_graph with prefixed names."""
    import onnx

    source_graph = source_model.graph
    obs_name = source_graph.input[0].name
    source_output = source_graph.output[0].name

    for initializer in source_graph.initializer:
        cloned = onnx.TensorProto()
        cloned.CopyFrom(initializer)
        cloned.name = prefixed(initializer.name, prefix, obs_name)
        target_graph.initializer.append(cloned)

    for node in source_graph.node:
        cloned = onnx.NodeProto()
        cloned.CopyFrom(node)
        cloned.name = f"{prefix}{node.name}" if node.name else ""
        cloned.input[:] = [prefixed(name, prefix, obs_name) if name else "" for name in node.input]
        cloned.output[:] = [
            output_alias if name == source_output else prefixed(name, prefix, obs_name)
            for name in node.output
        ]
        target_graph.node.append(cloned)


def verify_model(
    *,
    output_path: Path,
    low_policy: Path,
    high_policy: Path,
    command_x_index: int,
    threshold: float,
) -> dict[str, Any]:
    import onnxruntime as ort

    low_session = ort.InferenceSession(str(low_policy), providers=["CPUExecutionProvider"])
    high_session = ort.InferenceSession(str(high_policy), providers=["CPUExecutionProvider"])
    gated_session = ort.InferenceSession(str(output_path), providers=["CPUExecutionProvider"])

    low_input = low_session.get_inputs()[0].name
    high_input = high_session.get_inputs()[0].name
    gated_input = gated_session.get_inputs()[0].name
    low_output = low_session.get_outputs()[0].name
    high_output = high_session.get_outputs()[0].name
    gated_output = gated_session.get_outputs()[0].name

    rng = np.random.default_rng(1234)
    rows = []
    max_err = 0.0
    for command_x, expected_branch in [
        (0.0, "low"),
        (threshold * 0.5, "low"),
        (threshold * 1.5, "high"),
        (0.08, "high"),
        (-0.08, "high"),
    ]:
        obs = rng.normal(0.0, 0.1, size=(1, 101)).astype(np.float32)
        obs[0, command_x_index] = np.float32(command_x)
        low_action = low_session.run([low_output], {low_input: obs})[0]
        high_action = high_session.run([high_output], {high_input: obs})[0]
        gated_action = gated_session.run([gated_output], {gated_input: obs})[0]
        expected = low_action if abs(command_x) <= threshold else high_action
        err = float(np.max(np.abs(gated_action - expected)))
        max_err = max(max_err, err)
        rows.append(
            {
                "command_x": float(command_x),
                "expected_branch": expected_branch,
                "max_abs_error": err,
            }
        )
    return {
        "output": str(output_path),
        "low_policy": str(low_policy),
        "high_policy": str(high_policy),
        "command_x_index": int(command_x_index),
        "threshold": float(threshold),
        "checks": rows,
        "max_abs_error": max_err,
        "status": "PASS_ONNX_GATE_VERIFY" if max_err <= 1.0e-6 else "HOLD_ONNX_GATE_VERIFY",
    }


def main() -> int:
    args = parse_args()
    if args.threshold < 0.0:
        raise SystemExit("--threshold must be non-negative")

    import onnx
    from onnx import TensorProto, helper, numpy_helper

    low_path = Path(args.low_command_policy)
    high_path = Path(args.high_command_policy)
    output_path = Path(args.output)
    low_model = onnx.load(low_path)
    high_model = onnx.load(high_path)

    for label, model in [("low", low_model), ("high", high_model)]:
        if len(model.graph.input) != 1:
            raise SystemExit(f"{label} policy must have exactly one input")
        if len(model.graph.output) != 1:
            raise SystemExit(f"{label} policy must have exactly one output")
        in_shape = tensor_shape(model.graph.input[0])
        out_shape = tensor_shape(model.graph.output[0])
        if in_shape != [1, 101]:
            raise SystemExit(f"{label} policy input shape must be [1,101], got {in_shape}")
        if out_shape != [1, 14]:
            raise SystemExit(f"{label} policy output shape must be [1,14], got {out_shape}")

    initializers = [
        numpy_helper.from_array(np.asarray([args.command_x_index], dtype=np.int64), name="gate_command_x_index"),
        numpy_helper.from_array(np.asarray([args.threshold], dtype=np.float32), name="gate_threshold"),
    ]
    graph = helper.make_graph(
        [],
        "open_duck_command_gated_policy",
        [helper.make_tensor_value_info("obs", TensorProto.FLOAT, [1, 101])],
        [helper.make_tensor_value_info(args.output_name, TensorProto.FLOAT, [1, 14])],
        initializer=initializers,
    )

    clone_graph_into(graph, low_model, prefix="low_", output_alias="low_actions")
    clone_graph_into(graph, high_model, prefix="high_", output_alias="high_actions")
    graph.node.extend(
        [
            helper.make_node(
                "Gather",
                ["obs", "gate_command_x_index"],
                ["gate_command_x_col"],
                name="gate_gather_command_x",
                axis=1,
            ),
            helper.make_node(
                "Abs",
                ["gate_command_x_col"],
                ["gate_command_x_abs"],
                name="gate_abs_command_x",
            ),
            helper.make_node(
                "LessOrEqual",
                ["gate_command_x_abs", "gate_threshold"],
                ["gate_use_low"],
                name="gate_compare_threshold",
            ),
            helper.make_node(
                "Where",
                ["gate_use_low", "low_actions", "high_actions"],
                [args.output_name],
                name="gate_select_actions",
            ),
        ]
    )

    opset_versions = [
        imp.version for model in [low_model, high_model] for imp in model.opset_import if imp.domain == ""
    ]
    opset = max(opset_versions + [12])
    model = helper.make_model(
        graph,
        producer_name="open-duck-mini-rdkx5",
        opset_imports=[helper.make_operatorsetid("", opset)],
    )
    model.ir_version = min(model.ir_version, 10)
    model.metadata_props.add(key="low_command_policy", value=str(low_path))
    model.metadata_props.add(key="high_command_policy", value=str(high_path))
    model.metadata_props.add(key="command_x_index", value=str(args.command_x_index))
    model.metadata_props.add(key="threshold", value=str(args.threshold))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    onnx.checker.check_model(model)
    onnx.save(model, output_path)
    report = verify_model(
        output_path=output_path,
        low_policy=low_path,
        high_policy=high_path,
        command_x_index=args.command_x_index,
        threshold=args.threshold,
    )
    if args.verify_json:
        verify_path = Path(args.verify_json)
        verify_path.parent.mkdir(parents=True, exist_ok=True)
        verify_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(output_path)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "PASS_ONNX_GATE_VERIFY" else 1


if __name__ == "__main__":
    raise SystemExit(main())
