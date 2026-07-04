#!/usr/bin/env python3
"""Wrap an ONNX policy with an observation-threshold output scale.

This is an offline packaging helper. It does not train, deploy, SSH, or touch
the robot. The output contract remains:

  obs[1,101] -> continuous_actions[1,14]

The wrapper computes the base policy action, then applies a constant scale only
when an observation channel crosses a threshold:

  action = where(obs[index] >= threshold, base_action * scale, base_action)

Use this only as a diagnostic/deployable-candidate packaging step after a
separate offline gate shows the threshold is meaningful. It must not be used to
silently change command semantics or bypass corrected-envelope gates.
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
    parser.add_argument("--obs-index", type=int, required=True)
    parser.add_argument("--threshold", type=float, required=True)
    parser.add_argument("--scale", type=float, required=True)
    parser.add_argument(
        "--direction",
        choices=["ge", "le"],
        default="ge",
        help="Apply scale when obs[index] >= threshold or <= threshold.",
    )
    parser.add_argument("--output-name", default="continuous_actions")
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


def verify_policy(
    *,
    input_path: Path,
    output_path: Path,
    obs_index: int,
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
    test_values = [
        threshold - 0.25,
        threshold,
        threshold + 0.25,
    ]
    for value in test_values:
        obs = rng.normal(0.0, 0.5, size=(1, 101)).astype(np.float32)
        obs[0, obs_index] = np.float32(value)
        base = base_session.run([base_output], {base_input: obs})[0]
        wrapped = wrapped_session.run([wrapped_output], {wrapped_input: obs})[0]
        use_scale = value >= threshold if direction == "ge" else value <= threshold
        expected = base * np.float32(scale) if use_scale else base
        err = float(np.max(np.abs(wrapped - expected)))
        max_err = max(max_err, err)
        rows.append(
            {
                "obs_value": float(value),
                "expected_scaled": bool(use_scale),
                "max_abs_error": err,
            }
        )

    for _ in range(max(0, samples - len(test_values))):
        obs = rng.normal(0.0, 0.5, size=(1, 101)).astype(np.float32)
        base = base_session.run([base_output], {base_input: obs})[0]
        wrapped = wrapped_session.run([wrapped_output], {wrapped_input: obs})[0]
        value = float(obs[0, obs_index])
        use_scale = value >= threshold if direction == "ge" else value <= threshold
        expected = base * np.float32(scale) if use_scale else base
        max_err = max(max_err, float(np.max(np.abs(wrapped - expected))))

    return {
        "status": "PASS_ONNX_OBS_THRESHOLD_SCALE_VERIFY"
        if max_err <= 1.0e-6
        else "HOLD_ONNX_OBS_THRESHOLD_SCALE_VERIFY",
        "input": str(input_path),
        "output": str(output_path),
        "obs_index": int(obs_index),
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
    if not 0 <= int(args.obs_index) < 101:
        raise SystemExit("--obs-index must be in [0,100]")
    if not 0.0 <= float(args.scale) <= 1.0:
        raise SystemExit("--scale must be in [0,1]")

    import onnx
    from onnx import TensorProto, helper, numpy_helper

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
            numpy_helper.from_array(
                np.asarray([args.obs_index], dtype=np.int64),
                name="obs_threshold_index",
            ),
            numpy_helper.from_array(
                np.asarray([args.threshold], dtype=np.float32),
                name="obs_threshold_value",
            ),
            numpy_helper.from_array(
                np.asarray([args.scale], dtype=np.float32),
                name="obs_threshold_scale",
            ),
        ]
    )
    compare_node = "GreaterOrEqual" if args.direction == "ge" else "LessOrEqual"
    model.graph.node.extend(
        [
            helper.make_node(
                "Gather",
                [model.graph.input[0].name, "obs_threshold_index"],
                ["obs_threshold_channel"],
                name="obs_threshold_gather",
                axis=1,
            ),
            helper.make_node(
                compare_node,
                ["obs_threshold_channel", "obs_threshold_value"],
                ["obs_threshold_use_scaled"],
                name="obs_threshold_compare",
            ),
            helper.make_node(
                "Mul",
                [internal_output, "obs_threshold_scale"],
                ["obs_threshold_scaled_actions"],
                name="obs_threshold_scale_actions",
            ),
            helper.make_node(
                "Where",
                ["obs_threshold_use_scaled", "obs_threshold_scaled_actions", internal_output],
                [args.output_name],
                name="obs_threshold_select_actions",
            ),
        ]
    )
    model.graph.output[0].name = args.output_name
    model.metadata_props.add(key="obs_threshold_source_policy", value=str(input_path))
    model.metadata_props.add(key="obs_threshold_index", value=str(args.obs_index))
    model.metadata_props.add(key="obs_threshold", value=str(args.threshold))
    model.metadata_props.add(key="obs_threshold_scale", value=str(args.scale))
    model.metadata_props.add(key="obs_threshold_direction", value=str(args.direction))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    onnx.checker.check_model(model)
    onnx.save(model, output_path)
    report = verify_policy(
        input_path=input_path,
        output_path=output_path,
        obs_index=int(args.obs_index),
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
    return 0 if report["status"] == "PASS_ONNX_OBS_THRESHOLD_SCALE_VERIFY" else 1


if __name__ == "__main__":
    raise SystemExit(main())
