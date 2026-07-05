#!/usr/bin/env python3
"""Compose two ONNX policies with a saved observation-MLP branch gate.

This offline helper builds one stateless ONNX policy:

  obs[1,101] -> continuous_actions[1,14]

The gate NPZ must contain `obs_norm`, `hidden_sizes`, and `w_N`/`b_N` layers
from `tools/report_phase2_full8_mlp_router_separability.py`. Branch B is used
when the MLP logit crosses the configured threshold.

This does not train, deploy, SSH, run robot tests, change runtime behavior, or
run grounded replay.
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
    parser.add_argument("--gate-npz", required=True, help="saved MLP gate NPZ")
    parser.add_argument("--output", required=True, help="output composed ONNX policy")
    parser.add_argument("--threshold", type=float, default=0.0)
    parser.add_argument("--direction", choices=["ge", "le"], default="ge")
    parser.add_argument("--output-name", default="continuous_actions")
    parser.add_argument("--branch-a-prefix", default="branch_a")
    parser.add_argument("--branch-b-prefix", default="branch_b")
    parser.add_argument("--gate-prefix", default="gate")
    parser.add_argument("--verify-json")
    parser.add_argument("--verify-samples", type=int, default=128)
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


def load_gate_npz(path: Path) -> dict[str, Any]:
    data = np.load(path, allow_pickle=False)
    norm = np.asarray(data["obs_norm"], dtype=np.float32)
    if norm.shape != (2, 101):
        raise SystemExit(f"gate obs_norm must be [2,101], got {norm.shape}")
    layers = []
    index = 0
    while f"w_{index}" in data and f"b_{index}" in data:
        layers.append((np.asarray(data[f"w_{index}"], dtype=np.float32), np.asarray(data[f"b_{index}"], dtype=np.float32)))
        index += 1
    if not layers:
        raise SystemExit("gate NPZ contains no w_N/b_N layers")
    if layers[-1][0].shape[1] != 1 or layers[-1][1].shape != (1,):
        raise SystemExit("gate final layer must produce one logit")
    return {"norm": norm, "layers": layers}


def forward_gate_np(obs: np.ndarray, gate: dict[str, Any]) -> np.ndarray:
    mean, std = gate["norm"]
    z = (obs - mean) / std
    for index, (weights, bias) in enumerate(gate["layers"]):
        z = z @ weights + bias
        if index < len(gate["layers"]) - 1:
            z = z / (1.0 + np.exp(-z))
    return z.reshape(-1)


def verify_policy(
    *,
    branch_a_path: Path,
    branch_b_path: Path,
    gate: dict[str, Any],
    output_path: Path,
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
    branch_b_count = 0
    checks = []
    for index in range(samples):
        obs = rng.normal(0.0, 0.5, size=(1, 101)).astype(np.float32)
        a = branch_a.run([a_output], {a_input: obs})[0]
        b = branch_b.run([b_output], {b_input: obs})[0]
        actual = routed.run([r_output], {r_input: obs})[0]
        logit = float(forward_gate_np(obs, gate)[0])
        use_b = logit >= threshold if direction == "ge" else logit <= threshold
        branch_b_count += int(use_b)
        expected = b if use_b else a
        err = float(np.max(np.abs(actual - expected)))
        max_err = max(max_err, err)
        if index < 5:
            checks.append({"logit": logit, "expected_branch": "b" if use_b else "a", "max_abs_error": err})
    return {
        "status": "PASS_ONNX_OBS_MLP_GATE_VERIFY" if max_err <= 1.0e-6 else "HOLD_ONNX_OBS_MLP_GATE_VERIFY",
        "branch_a_policy": str(branch_a_path),
        "branch_b_policy": str(branch_b_path),
        "output": str(output_path),
        "threshold": float(threshold),
        "direction": direction,
        "samples": int(samples),
        "branch_b_pct": float(branch_b_count / max(samples, 1) * 100.0),
        "checks": checks,
        "max_abs_error": max_err,
    }


def main() -> int:
    args = parse_args()
    branch_a_path = Path(args.branch_a_policy)
    branch_b_path = Path(args.branch_b_policy)
    gate_path = Path(args.gate_npz)
    output_path = Path(args.output)
    if not branch_a_path.exists():
        raise SystemExit(f"branch A policy does not exist: {branch_a_path}")
    if not branch_b_path.exists():
        raise SystemExit(f"branch B policy does not exist: {branch_b_path}")
    if not gate_path.exists():
        raise SystemExit(f"gate NPZ does not exist: {gate_path}")
    if args.branch_a_prefix == args.branch_b_prefix:
        raise SystemExit("--branch-a-prefix and --branch-b-prefix must differ")

    import onnx
    from onnx import TensorProto, helper, numpy_helper

    gate = load_gate_npz(gate_path)
    branch_a = onnx.load(branch_a_path)
    branch_b = onnx.load(branch_b_path)
    shared_input = "obs"
    a_nodes, a_initializers, a_output = clone_policy_graph(
        branch_a, prefix=args.branch_a_prefix, shared_input=shared_input
    )
    b_nodes, b_initializers, b_output = clone_policy_graph(
        branch_b, prefix=args.branch_b_prefix, shared_input=shared_input
    )

    gate_initializers = [
        numpy_helper.from_array(gate["norm"][0].astype(np.float32), name=prefixed("obs_mean", args.gate_prefix)),
        numpy_helper.from_array(gate["norm"][1].astype(np.float32), name=prefixed("obs_std", args.gate_prefix)),
        numpy_helper.from_array(np.asarray([args.threshold], dtype=np.float32), name=prefixed("threshold", args.gate_prefix)),
    ]
    gate_nodes = [
        helper.make_node("Sub", [shared_input, prefixed("obs_mean", args.gate_prefix)], [prefixed("obs_centered", args.gate_prefix)], name=prefixed("norm_sub", args.gate_prefix)),
        helper.make_node("Div", [prefixed("obs_centered", args.gate_prefix), prefixed("obs_std", args.gate_prefix)], [prefixed("z_0", args.gate_prefix)], name=prefixed("norm_div", args.gate_prefix)),
    ]
    current = prefixed("z_0", args.gate_prefix)
    for index, (weights, bias) in enumerate(gate["layers"]):
        w_name = prefixed(f"w_{index}", args.gate_prefix)
        b_name = prefixed(f"b_{index}", args.gate_prefix)
        pre = prefixed(f"pre_{index}", args.gate_prefix)
        gate_initializers.append(numpy_helper.from_array(weights.astype(np.float32), name=w_name))
        gate_initializers.append(numpy_helper.from_array(bias.astype(np.float32), name=b_name))
        gate_nodes.append(helper.make_node("Gemm", [current, w_name, b_name], [pre], name=prefixed(f"gemm_{index}", args.gate_prefix)))
        if index < len(gate["layers"]) - 1:
            sigmoid = prefixed(f"sigmoid_{index}", args.gate_prefix)
            swish = prefixed(f"swish_{index}", args.gate_prefix)
            gate_nodes.append(helper.make_node("Sigmoid", [pre], [sigmoid], name=prefixed(f"sigmoid_node_{index}", args.gate_prefix)))
            gate_nodes.append(helper.make_node("Mul", [pre, sigmoid], [swish], name=prefixed(f"swish_node_{index}", args.gate_prefix)))
            current = swish
        else:
            current = pre
    compare_node = "GreaterOrEqual" if args.direction == "ge" else "LessOrEqual"
    gate_nodes.extend(
        [
            helper.make_node(compare_node, [current, prefixed("threshold", args.gate_prefix)], [prefixed("use_b", args.gate_prefix)], name=prefixed("compare", args.gate_prefix)),
            helper.make_node("Where", [prefixed("use_b", args.gate_prefix), b_output, a_output], [args.output_name], name=prefixed("select_action", args.gate_prefix)),
        ]
    )

    input_info = helper.make_tensor_value_info(shared_input, TensorProto.FLOAT, [1, 101])
    output_info = helper.make_tensor_value_info(args.output_name, TensorProto.FLOAT, [1, 14])
    graph = helper.make_graph(
        [*a_nodes, *b_nodes, *gate_nodes],
        "obs_mlp_gated_policy",
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
    model.metadata_props.add(key="gate_npz", value=str(gate_path))
    model.metadata_props.add(key="gate_threshold", value=str(args.threshold))
    model.metadata_props.add(key="gate_direction", value=str(args.direction))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    onnx.checker.check_model(model)
    onnx.save(model, output_path)
    report = verify_policy(
        branch_a_path=branch_a_path,
        branch_b_path=branch_b_path,
        gate=gate,
        output_path=output_path,
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
    return 0 if report["status"] == "PASS_ONNX_OBS_MLP_GATE_VERIFY" else 1


if __name__ == "__main__":
    raise SystemExit(main())
