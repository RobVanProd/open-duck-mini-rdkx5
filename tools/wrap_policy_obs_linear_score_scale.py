#!/usr/bin/env python3
"""Wrap an ONNX policy with an observation linear-score output scale.

This is an offline packaging helper. It does not train, deploy, SSH, or touch
the robot. The output contract remains:

  obs[1,101] -> continuous_actions[1,14]

The wrapper computes the base policy action, then applies a constant scale only
when a linear score over selected observation channels crosses a threshold:

  score = sum((obs[indices] - centers) * weights)
  action = where(score >= threshold, base_action * scale, base_action)
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="input ONNX policy")
    parser.add_argument("--output", required=True, help="output ONNX policy")
    parser.add_argument("--indices", required=True, help="comma-separated obs indices")
    parser.add_argument("--centers", required=True, help="comma-separated centers")
    parser.add_argument("--weights", required=True, help="comma-separated weights")
    parser.add_argument("--threshold", type=float, required=True)
    parser.add_argument("--scale", type=float, required=True)
    parser.add_argument(
        "--direction",
        choices=["ge", "le"],
        default="ge",
        help="Apply scale when score >= threshold or <= threshold.",
    )
    parser.add_argument("--output-name", default="continuous_actions")
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


def verify_policy(
    *,
    input_path: Path,
    output_path: Path,
    indices: np.ndarray,
    centers: np.ndarray,
    weights: np.ndarray,
    threshold: float,
    scale: float,
    direction: str,
    samples: int,
) -> dict[str, Any]:
    import onnxruntime as ort

    base_session = ort.InferenceSession(str(input_path), providers=["CPUExecutionProvider"])
    wrapped_session = ort.InferenceSession(str(output_path), providers=["CPUExecutionProvider"])
    base_input = base_session.get_inputs()[0].name
    wrapped_input = wrapped_session.get_inputs()[0].name
    base_output = base_session.get_outputs()[0].name
    wrapped_output = wrapped_session.get_outputs()[0].name

    rng = np.random.default_rng(20260704)
    max_err = 0.0
    rows = []

    for target_score in [threshold - 1.0, threshold, threshold + 1.0]:
        obs = rng.normal(0.0, 0.5, size=(1, 101)).astype(np.float32)
        obs[0, indices] = centers
        nonzero = np.flatnonzero(np.abs(weights) > 1.0e-9)
        if nonzero.size:
            first = int(nonzero[0])
            obs[0, indices[first]] += np.float32(target_score / float(weights[first]))
        base = base_session.run([base_output], {base_input: obs})[0]
        wrapped = wrapped_session.run([wrapped_output], {wrapped_input: obs})[0]
        score = float(np.sum((obs[0, indices] - centers) * weights))
        use_scale = score >= threshold if direction == "ge" else score <= threshold
        expected = base * np.float32(scale) if use_scale else base
        err = float(np.max(np.abs(wrapped - expected)))
        max_err = max(max_err, err)
        rows.append(
            {
                "score": score,
                "expected_scaled": bool(use_scale),
                "max_abs_error": err,
            }
        )

    for _ in range(max(0, samples - len(rows))):
        obs = rng.normal(0.0, 0.5, size=(1, 101)).astype(np.float32)
        base = base_session.run([base_output], {base_input: obs})[0]
        wrapped = wrapped_session.run([wrapped_output], {wrapped_input: obs})[0]
        score = float(np.sum((obs[0, indices] - centers) * weights))
        use_scale = score >= threshold if direction == "ge" else score <= threshold
        expected = base * np.float32(scale) if use_scale else base
        max_err = max(max_err, float(np.max(np.abs(wrapped - expected))))

    return {
        "status": "PASS_ONNX_OBS_LINEAR_SCORE_SCALE_VERIFY"
        if max_err <= 1.0e-6
        else "HOLD_ONNX_OBS_LINEAR_SCORE_SCALE_VERIFY",
        "input": str(input_path),
        "output": str(output_path),
        "indices": [int(value) for value in indices.tolist()],
        "centers": [float(value) for value in centers.tolist()],
        "weights": [float(value) for value in weights.tolist()],
        "threshold": float(threshold),
        "scale": float(scale),
        "direction": direction,
        "samples": int(samples),
        "checks": rows,
        "max_abs_error": max_err,
    }


def main() -> int:
    args = parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)
    if not input_path.exists():
        raise SystemExit(f"input ONNX does not exist: {input_path}")
    if not 0.0 <= float(args.scale) <= 1.0:
        raise SystemExit("--scale must be in [0,1]")

    indices = parse_int_vector(args.indices, name="--indices")
    centers = parse_float_vector(args.centers, name="--centers")
    weights = parse_float_vector(args.weights, name="--weights")
    if not (len(indices) == len(centers) == len(weights)):
        raise SystemExit("--indices, --centers, and --weights must have equal length")

    import onnx
    from onnx import helper, numpy_helper

    model = onnx.load(input_path)
    if len(model.graph.input) != 1:
        raise SystemExit("policy must have exactly one input")
    if len(model.graph.output) != 1:
        raise SystemExit("policy must have exactly one output")
    input_shape = tensor_shape(model.graph.input[0])
    output_shape = tensor_shape(model.graph.output[0])
    if input_shape != [1, 101]:
        raise SystemExit(f"policy input shape must be [1,101], got {input_shape}")
    if output_shape != [1, 14]:
        raise SystemExit(f"policy output shape must be [1,14], got {output_shape}")

    original_output = model.graph.output[0].name
    internal_output = f"{original_output}_unwrapped"
    for node in model.graph.node:
        for index, name in enumerate(node.output):
            if name == original_output:
                node.output[index] = internal_output

    model.graph.initializer.extend(
        [
            numpy_helper.from_array(indices, name="obs_linear_indices"),
            numpy_helper.from_array(centers.reshape(1, -1), name="obs_linear_centers"),
            numpy_helper.from_array(weights.reshape(1, -1), name="obs_linear_weights"),
            numpy_helper.from_array(np.asarray([1], dtype=np.int64), name="obs_linear_reduce_axes"),
            numpy_helper.from_array(np.asarray([args.threshold], dtype=np.float32), name="obs_linear_threshold"),
            numpy_helper.from_array(np.asarray([args.scale], dtype=np.float32), name="obs_linear_scale"),
        ]
    )
    compare_node = "GreaterOrEqual" if args.direction == "ge" else "LessOrEqual"
    model.graph.node.extend(
        [
            helper.make_node(
                "Gather",
                [model.graph.input[0].name, "obs_linear_indices"],
                ["obs_linear_channels"],
                name="obs_linear_gather",
                axis=1,
            ),
            helper.make_node(
                "Sub",
                ["obs_linear_channels", "obs_linear_centers"],
                ["obs_linear_centered"],
                name="obs_linear_center",
            ),
            helper.make_node(
                "Mul",
                ["obs_linear_centered", "obs_linear_weights"],
                ["obs_linear_weighted"],
                name="obs_linear_weight",
            ),
            helper.make_node(
                "ReduceSum",
                ["obs_linear_weighted", "obs_linear_reduce_axes"],
                ["obs_linear_score"],
                name="obs_linear_reduce_sum",
                keepdims=1,
            ),
            helper.make_node(
                compare_node,
                ["obs_linear_score", "obs_linear_threshold"],
                ["obs_linear_use_scaled"],
                name="obs_linear_compare",
            ),
            helper.make_node(
                "Mul",
                [internal_output, "obs_linear_scale"],
                ["obs_linear_scaled_actions"],
                name="obs_linear_scale_actions",
            ),
            helper.make_node(
                "Where",
                ["obs_linear_use_scaled", "obs_linear_scaled_actions", internal_output],
                [args.output_name],
                name="obs_linear_select_actions",
            ),
        ]
    )
    model.graph.output[0].name = args.output_name
    model.metadata_props.add(key="obs_linear_source_policy", value=str(input_path))
    model.metadata_props.add(key="obs_linear_indices", value=",".join(str(int(v)) for v in indices))
    model.metadata_props.add(key="obs_linear_centers", value=",".join(f"{float(v):.9g}" for v in centers))
    model.metadata_props.add(key="obs_linear_weights", value=",".join(f"{float(v):.9g}" for v in weights))
    model.metadata_props.add(key="obs_linear_threshold", value=str(args.threshold))
    model.metadata_props.add(key="obs_linear_scale", value=str(args.scale))
    model.metadata_props.add(key="obs_linear_direction", value=str(args.direction))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    onnx.checker.check_model(model)
    onnx.save(model, output_path)
    report = verify_policy(
        input_path=input_path,
        output_path=output_path,
        indices=indices,
        centers=centers,
        weights=weights,
        threshold=float(args.threshold),
        scale=float(args.scale),
        direction=str(args.direction),
        samples=int(args.verify_samples),
    )
    if args.verify_json:
        verify_path = Path(args.verify_json)
        verify_path.parent.mkdir(parents=True, exist_ok=True)
        verify_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(output_path)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "PASS_ONNX_OBS_LINEAR_SCORE_SCALE_VERIFY" else 1


if __name__ == "__main__":
    raise SystemExit(main())
