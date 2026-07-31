#!/usr/bin/env python3
"""Create an ONNX policy with a constant output action scale.

This is an offline packaging helper. It does not train, deploy, SSH, or touch
the robot. The output contract remains:

  obs[1,101] -> continuous_actions[1,14]

The intended use is to convert an evaluator-side `policy_action_gain` screen
into a real ONNX artifact that can be gated without eval-only multipliers.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scale an ONNX policy action output.")
    parser.add_argument("--input", required=True, help="input ONNX policy")
    parser.add_argument("--output", required=True, help="output ONNX policy")
    parser.add_argument("--scale", type=float, required=True, help="constant action multiplier")
    parser.add_argument("--output-name", default="continuous_actions")
    parser.add_argument("--verify-json", help="optional JSON verification report")
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


def verify_scaled_policy(
    *,
    input_path: Path,
    output_path: Path,
    scale: float,
    samples: int,
) -> dict[str, Any]:
    import onnxruntime as ort

    base_session = ort.InferenceSession(str(input_path), providers=["CPUExecutionProvider"])
    scaled_session = ort.InferenceSession(str(output_path), providers=["CPUExecutionProvider"])

    base_input = base_session.get_inputs()[0].name
    scaled_input = scaled_session.get_inputs()[0].name
    base_output = base_session.get_outputs()[0].name
    scaled_output = scaled_session.get_outputs()[0].name

    rng = np.random.default_rng(20260629)
    max_err = 0.0
    p95_values: list[float] = []
    for _ in range(samples):
        obs = rng.normal(0.0, 0.5, size=(1, 101)).astype(np.float32)
        base_action = base_session.run([base_output], {base_input: obs})[0]
        scaled_action = scaled_session.run([scaled_output], {scaled_input: obs})[0]
        err = np.abs(scaled_action - (base_action * np.float32(scale)))
        max_err = max(max_err, float(np.max(err)))
        p95_values.append(float(np.percentile(err, 95)))

    p95 = float(np.percentile(p95_values, 95)) if p95_values else 0.0
    return {
        "input": str(input_path),
        "output": str(output_path),
        "scale": float(scale),
        "samples": int(samples),
        "max_abs_error": float(max_err),
        "p95_abs_error": p95,
        "status": "PASS_ONNX_OUTPUT_SCALE_VERIFY" if max_err <= 1.0e-6 else "HOLD_ONNX_OUTPUT_SCALE_VERIFY",
    }


def main() -> int:
    args = parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)
    if not input_path.exists():
        raise SystemExit(f"input ONNX does not exist: {input_path}")

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
    internal_output = f"{original_output}_unscaled"
    for node in model.graph.node:
        for index, name in enumerate(node.output):
            if name == original_output:
                node.output[index] = internal_output

    scale_name = "policy_output_scale"
    model.graph.initializer.append(
        numpy_helper.from_array(np.asarray([args.scale], dtype=np.float32), name=scale_name)
    )
    model.graph.node.append(
        helper.make_node(
            "Mul",
            [internal_output, scale_name],
            [args.output_name],
            name="scale_policy_actions",
        )
    )
    model.graph.output[0].name = args.output_name
    model.metadata_props.add(key="output_action_scale", value=str(args.scale))
    model.metadata_props.add(key="source_policy", value=str(input_path))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    onnx.checker.check_model(model)
    onnx.save(model, output_path)

    report = verify_scaled_policy(
        input_path=input_path,
        output_path=output_path,
        scale=float(args.scale),
        samples=int(args.verify_samples),
    )
    if args.verify_json:
        verify_path = Path(args.verify_json)
        verify_path.parent.mkdir(parents=True, exist_ok=True)
        verify_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(output_path)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "PASS_ONNX_OUTPUT_SCALE_VERIFY" else 1


if __name__ == "__main__":
    raise SystemExit(main())
