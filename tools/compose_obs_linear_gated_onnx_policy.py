#!/usr/bin/env python3
"""Compose two ONNX policies with an observation-linear branch gate.

This offline helper builds a single stateless ONNX graph:

  obs[1,101] -> continuous_actions[1,14]

It evaluates both policies on the same observation and selects one branch with
a linear score over observation channels:

  score = sum((obs[indices] - centers) * weights)
  action = where(score >= threshold, branch_b_action, branch_a_action)

Use this only as an offline branch-preservation diagnostic after source
behavior has already been gated. It does not train, deploy, SSH, run robot
tests, change robot runtime behavior, or run grounded replay.
"""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

import numpy as np


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--branch-a-policy", required=True, help="ONNX policy used when gate is false")
    parser.add_argument("--branch-b-policy", required=True, help="ONNX policy used when gate is true")
    parser.add_argument("--output", required=True, help="output composed ONNX policy")
    parser.add_argument("--indices", required=True, help="comma-separated obs indices")
    parser.add_argument("--centers", required=True, help="comma-separated centers")
    parser.add_argument("--weights", required=True, help="comma-separated weights")
    parser.add_argument("--threshold", type=float, required=True)
    parser.add_argument(
        "--direction",
        choices=["ge", "le"],
        default="ge",
        help="Use branch B when score >= threshold or <= threshold.",
    )
    parser.add_argument("--output-name", default="continuous_actions")
    parser.add_argument("--branch-a-prefix", default="branch_a")
    parser.add_argument("--branch-b-prefix", default="branch_b")
    parser.add_argument("--verify-json")
    parser.add_argument("--verify-samples", type=int, default=128)
    return parser.parse_args()


def parse_int_vector(text: str, *, name: str) -> np.ndarray:
    values = [int(part.strip()) for part in text.split(",") if part.strip()]
    if not values:
        raise SystemExit(f"{name} must not be empty")
    if any(value < 0 or value >= 101 for value in values):
        raise SystemExit(f"{name} values must be in [0,100]")
    return np.asarray(values, dtype=np.int64)


def parse_float_vector(text: str, *, name: str) -> np.ndarray:
    values = [float(part.strip()) for part in text.split(",") if part.strip()]
    if not values:
        raise SystemExit(f"{name} must not be empty")
    return np.asarray(values, dtype=np.float32)


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


def prefixed(name: str, prefix: str) -> str:
    return f"{prefix}__{name}"


def clone_policy_graph(model: Any, *, prefix: str, shared_input: str) -> tuple[list[Any], list[Any], str]:
    if len(model.graph.input) != 1:
        raise SystemExit(f"{prefix} policy must have exactly one input")
    if len(model.graph.output) != 1:
        raise SystemExit(f"{prefix} policy must have exactly one output")
    input_shape = tensor_shape(model.graph.input[0])
    output_shape = tensor_shape(model.graph.output[0])
    if input_shape != [1, 101]:
        raise SystemExit(f"{prefix} policy input must be [1,101], got {input_shape}")
    if output_shape != [1, 14]:
        raise SystemExit(f"{prefix} policy output must be [1,14], got {output_shape}")

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


def verify_policy(
    *,
    branch_a_path: Path,
    branch_b_path: Path,
    output_path: Path,
    indices: np.ndarray,
    centers: np.ndarray,
    weights: np.ndarray,
    threshold: float,
    direction: str,
    samples: int,
) -> dict[str, Any]:
    import onnxruntime as ort

    branch_a = ort.InferenceSession(str(branch_a_path), providers=["CPUExecutionProvider"])
    branch_b = ort.InferenceSession(str(branch_b_path), providers=["CPUExecutionProvider"])
    routed = ort.InferenceSession(str(output_path), providers=["CPUExecutionProvider"])
    a_input = branch_a.get_inputs()[0].name
    b_input = branch_b.get_inputs()[0].name
    r_input = routed.get_inputs()[0].name
    a_output = branch_a.get_outputs()[0].name
    b_output = branch_b.get_outputs()[0].name
    r_output = routed.get_outputs()[0].name

    rng = np.random.default_rng(20260705)
    max_err = 0.0
    checks = []
    test_scores = [threshold - 1.0, threshold, threshold + 1.0]
    for target_score in test_scores:
        obs = rng.normal(0.0, 0.5, size=(1, 101)).astype(np.float32)
        obs[0, indices] = centers
        nonzero = np.flatnonzero(np.abs(weights) > 1.0e-9)
        if nonzero.size:
            first = int(nonzero[0])
            obs[0, indices[first]] += np.float32(target_score / float(weights[first]))
        a = branch_a.run([a_output], {a_input: obs})[0]
        b = branch_b.run([b_output], {b_input: obs})[0]
        actual = routed.run([r_output], {r_input: obs})[0]
        score = float(np.sum((obs[0, indices] - centers) * weights))
        use_b = score >= threshold if direction == "ge" else score <= threshold
        expected = b if use_b else a
        err = float(np.max(np.abs(actual - expected)))
        max_err = max(max_err, err)
        checks.append({"score": score, "expected_branch": "b" if use_b else "a", "max_abs_error": err})

    for _ in range(max(0, samples - len(checks))):
        obs = rng.normal(0.0, 0.5, size=(1, 101)).astype(np.float32)
        a = branch_a.run([a_output], {a_input: obs})[0]
        b = branch_b.run([b_output], {b_input: obs})[0]
        actual = routed.run([r_output], {r_input: obs})[0]
        score = float(np.sum((obs[0, indices] - centers) * weights))
        use_b = score >= threshold if direction == "ge" else score <= threshold
        expected = b if use_b else a
        max_err = max(max_err, float(np.max(np.abs(actual - expected))))

    return {
        "status": "PASS_ONNX_OBS_LINEAR_GATE_VERIFY"
        if max_err <= 1.0e-6
        else "HOLD_ONNX_OBS_LINEAR_GATE_VERIFY",
        "branch_a_policy": str(branch_a_path),
        "branch_b_policy": str(branch_b_path),
        "output": str(output_path),
        "indices": [int(value) for value in indices.tolist()],
        "centers": [float(value) for value in centers.tolist()],
        "weights": [float(value) for value in weights.tolist()],
        "threshold": float(threshold),
        "direction": direction,
        "samples": int(samples),
        "checks": checks,
        "max_abs_error": max_err,
    }


def main() -> int:
    args = parse_args()
    branch_a_path = Path(args.branch_a_policy)
    branch_b_path = Path(args.branch_b_policy)
    output_path = Path(args.output)
    if not branch_a_path.exists():
        raise SystemExit(f"branch A policy does not exist: {branch_a_path}")
    if not branch_b_path.exists():
        raise SystemExit(f"branch B policy does not exist: {branch_b_path}")
    if args.branch_a_prefix == args.branch_b_prefix:
        raise SystemExit("--branch-a-prefix and --branch-b-prefix must differ")

    indices = parse_int_vector(args.indices, name="--indices")
    centers = parse_float_vector(args.centers, name="--centers")
    weights = parse_float_vector(args.weights, name="--weights")
    if not (len(indices) == len(centers) == len(weights)):
        raise SystemExit("--indices, --centers, and --weights must have equal length")

    import onnx
    from onnx import TensorProto, helper, numpy_helper

    branch_a = onnx.load(branch_a_path)
    branch_b = onnx.load(branch_b_path)
    shared_input = "obs"
    a_nodes, a_initializers, a_output = clone_policy_graph(
        branch_a, prefix=args.branch_a_prefix, shared_input=shared_input
    )
    b_nodes, b_initializers, b_output = clone_policy_graph(
        branch_b, prefix=args.branch_b_prefix, shared_input=shared_input
    )
    compare_node = "GreaterOrEqual" if args.direction == "ge" else "LessOrEqual"
    gate_initializers = [
        numpy_helper.from_array(indices, name="obs_linear_gate_indices"),
        numpy_helper.from_array(centers.reshape(1, -1), name="obs_linear_gate_centers"),
        numpy_helper.from_array(weights.reshape(1, -1), name="obs_linear_gate_weights"),
        numpy_helper.from_array(np.asarray([1], dtype=np.int64), name="obs_linear_gate_reduce_axes"),
        numpy_helper.from_array(np.asarray([args.threshold], dtype=np.float32), name="obs_linear_gate_threshold"),
    ]
    gate_nodes = [
        helper.make_node(
            "Gather",
            [shared_input, "obs_linear_gate_indices"],
            ["obs_linear_gate_channels"],
            name="obs_linear_gate_gather",
            axis=1,
        ),
        helper.make_node(
            "Sub",
            ["obs_linear_gate_channels", "obs_linear_gate_centers"],
            ["obs_linear_gate_centered"],
            name="obs_linear_gate_center",
        ),
        helper.make_node(
            "Mul",
            ["obs_linear_gate_centered", "obs_linear_gate_weights"],
            ["obs_linear_gate_weighted"],
            name="obs_linear_gate_weight",
        ),
        helper.make_node(
            "ReduceSum",
            ["obs_linear_gate_weighted", "obs_linear_gate_reduce_axes"],
            ["obs_linear_gate_score"],
            name="obs_linear_gate_reduce_sum",
            keepdims=1,
        ),
        helper.make_node(
            compare_node,
            ["obs_linear_gate_score", "obs_linear_gate_threshold"],
            ["obs_linear_gate_use_b"],
            name="obs_linear_gate_compare",
        ),
        helper.make_node(
            "Where",
            ["obs_linear_gate_use_b", b_output, a_output],
            [args.output_name],
            name="obs_linear_gate_select_action",
        ),
    ]

    input_info = helper.make_tensor_value_info(shared_input, TensorProto.FLOAT, [1, 101])
    output_info = helper.make_tensor_value_info(args.output_name, TensorProto.FLOAT, [1, 14])
    graph = helper.make_graph(
        [*a_nodes, *b_nodes, *gate_nodes],
        "obs_linear_gated_policy",
        [input_info],
        [output_info],
        [*a_initializers, *b_initializers, *gate_initializers],
    )
    opsets = {item.domain: item.version for item in list(branch_a.opset_import) + list(branch_b.opset_import)}
    opsets[""] = max(opsets.get("", 13), 13)
    model = helper.make_model(
        graph,
        opset_imports=[helper.make_operatorsetid(domain, version) for domain, version in sorted(opsets.items())],
    )
    model.ir_version = max(branch_a.ir_version, branch_b.ir_version)
    model.metadata_props.add(key="branch_a_policy", value=str(branch_a_path))
    model.metadata_props.add(key="branch_b_policy", value=str(branch_b_path))
    model.metadata_props.add(key="obs_linear_gate_indices", value=",".join(str(int(v)) for v in indices))
    model.metadata_props.add(key="obs_linear_gate_centers", value=",".join(f"{float(v):.9g}" for v in centers))
    model.metadata_props.add(key="obs_linear_gate_weights", value=",".join(f"{float(v):.9g}" for v in weights))
    model.metadata_props.add(key="obs_linear_gate_threshold", value=str(args.threshold))
    model.metadata_props.add(key="obs_linear_gate_direction", value=str(args.direction))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    onnx.checker.check_model(model)
    onnx.save(model, output_path)
    report = verify_policy(
        branch_a_path=branch_a_path,
        branch_b_path=branch_b_path,
        output_path=output_path,
        indices=indices,
        centers=centers,
        weights=weights,
        threshold=float(args.threshold),
        direction=str(args.direction),
        samples=int(args.verify_samples),
    )
    if args.verify_json:
        verify_path = Path(args.verify_json)
        verify_path.parent.mkdir(parents=True, exist_ok=True)
        verify_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(output_path)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "PASS_ONNX_OBS_LINEAR_GATE_VERIFY" else 1


if __name__ == "__main__":
    raise SystemExit(main())
