#!/usr/bin/env python3
"""Wrap four ONNX policies with smooth phase-conditioned blending.

This is the smooth counterpart to wrap_policy_phase_quadrant_gate.py. It
preserves the deployed policy contract:

  obs[1,101] -> continuous_actions[1,14]

and blends four phase-head policies using the two cyclic phase observations
obs[99:101] by default:

  s_a = clip((obs[a] + 1) / 2, 0, 1)
  s_b = clip((obs[b] + 1) / 2, 0, 1)
  w0 = s_a       * s_b
  w1 = (1 - s_a) * s_b
  w2 = (1 - s_a) * (1 - s_b)
  w3 = s_a       * (1 - s_b)

This intentionally avoids hard discontinuities at phase quadrant boundaries.
It is offline-only and does not train, deploy, SSH, or touch the robot.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase0-policy", required=True)
    parser.add_argument("--phase1-policy", required=True)
    parser.add_argument("--phase2-policy", required=True)
    parser.add_argument("--phase3-policy", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--phase-a-index", type=int, default=99)
    parser.add_argument("--phase-b-index", type=int, default=100)
    parser.add_argument("--output-name", default="continuous_actions")
    parser.add_argument("--verify-json")
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


def clone_graph_into(target_graph: Any, source_model: Any, *, prefix: str, output_alias: str) -> None:
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


def blend_weights(phase_a: float, phase_b: float) -> np.ndarray:
    sa = np.clip((float(phase_a) + 1.0) * 0.5, 0.0, 1.0)
    sb = np.clip((float(phase_b) + 1.0) * 0.5, 0.0, 1.0)
    return np.asarray(
        [
            sa * sb,
            (1.0 - sa) * sb,
            (1.0 - sa) * (1.0 - sb),
            sa * (1.0 - sb),
        ],
        dtype=np.float32,
    )


def verify_model(
    output_path: Path,
    policies: list[Path],
    phase_a_index: int,
    phase_b_index: int,
) -> dict[str, Any]:
    import onnxruntime as ort

    head_sessions = [ort.InferenceSession(str(path), providers=["CPUExecutionProvider"]) for path in policies]
    gated_session = ort.InferenceSession(str(output_path), providers=["CPUExecutionProvider"])
    gated_input = gated_session.get_inputs()[0].name
    gated_output = gated_session.get_outputs()[0].name
    phase_values = [
        (1.0, 1.0),
        (-1.0, 1.0),
        (-1.0, -1.0),
        (1.0, -1.0),
        (0.0, 0.0),
        (0.4, -0.2),
    ]
    rng = np.random.default_rng(8765)
    rows = []
    max_err = 0.0
    for phase_a, phase_b in phase_values:
        obs = rng.normal(0.0, 0.1, size=(1, 101)).astype(np.float32)
        obs[0, phase_a_index] = np.float32(phase_a)
        obs[0, phase_b_index] = np.float32(phase_b)
        weights = blend_weights(phase_a, phase_b)
        expected = np.zeros((1, 14), dtype=np.float32)
        for weight, session in zip(weights, head_sessions, strict=True):
            expected += weight * session.run(
                [session.get_outputs()[0].name], {session.get_inputs()[0].name: obs}
            )[0]
        actual = gated_session.run([gated_output], {gated_input: obs})[0]
        err = float(np.max(np.abs(actual - expected)))
        max_err = max(max_err, err)
        rows.append(
            {
                "phase_a": float(phase_a),
                "phase_b": float(phase_b),
                "weights": [float(v) for v in weights],
                "weight_sum": float(np.sum(weights)),
                "max_abs_error": err,
            }
        )
    return {
        "status": "PASS_ONNX_PHASE_SMOOTH_BLEND_VERIFY"
        if max_err <= 1.0e-6
        else "HOLD_ONNX_PHASE_SMOOTH_BLEND_VERIFY",
        "output": str(output_path),
        "policies": [str(path) for path in policies],
        "phase_a_index": int(phase_a_index),
        "phase_b_index": int(phase_b_index),
        "checks": rows,
        "max_abs_error": max_err,
    }


def main() -> int:
    args = parse_args()
    import onnx
    from onnx import TensorProto, helper, numpy_helper

    policies = [
        Path(args.phase0_policy),
        Path(args.phase1_policy),
        Path(args.phase2_policy),
        Path(args.phase3_policy),
    ]
    models = [onnx.load(path) for path in policies]
    for index, model in enumerate(models):
        if len(model.graph.input) != 1 or len(model.graph.output) != 1:
            raise SystemExit(f"phase {index} policy must have exactly one input and one output")
        in_shape = tensor_shape(model.graph.input[0])
        out_shape = tensor_shape(model.graph.output[0])
        if in_shape != [1, 101]:
            raise SystemExit(f"phase {index} input shape must be [1,101], got {in_shape}")
        if out_shape != [1, 14]:
            raise SystemExit(f"phase {index} output shape must be [1,14], got {out_shape}")

    graph = helper.make_graph(
        [],
        "open_duck_phase_smooth_blend_policy",
        [helper.make_tensor_value_info("obs", TensorProto.FLOAT, [1, 101])],
        [helper.make_tensor_value_info(args.output_name, TensorProto.FLOAT, [1, 14])],
        initializer=[
            numpy_helper.from_array(np.asarray([args.phase_a_index], dtype=np.int64), name="phase_a_index"),
            numpy_helper.from_array(np.asarray([args.phase_b_index], dtype=np.int64), name="phase_b_index"),
            numpy_helper.from_array(np.asarray([1.0], dtype=np.float32), name="one"),
            numpy_helper.from_array(np.asarray([0.5], dtype=np.float32), name="half"),
            numpy_helper.from_array(np.asarray([0.0], dtype=np.float32), name="zero"),
        ],
    )
    for index, model in enumerate(models):
        clone_graph_into(graph, model, prefix=f"phase{index}_", output_alias=f"phase{index}_actions")

    graph.node.extend(
        [
            helper.make_node("Gather", ["obs", "phase_a_index"], ["phase_a"], name="phase_smooth_gather_a", axis=1),
            helper.make_node("Gather", ["obs", "phase_b_index"], ["phase_b"], name="phase_smooth_gather_b", axis=1),
            helper.make_node("Add", ["phase_a", "one"], ["phase_a_plus_one"], name="phase_smooth_a_plus_one"),
            helper.make_node("Add", ["phase_b", "one"], ["phase_b_plus_one"], name="phase_smooth_b_plus_one"),
            helper.make_node("Mul", ["phase_a_plus_one", "half"], ["phase_a_unit_raw"], name="phase_smooth_a_half"),
            helper.make_node("Mul", ["phase_b_plus_one", "half"], ["phase_b_unit_raw"], name="phase_smooth_b_half"),
            helper.make_node("Clip", ["phase_a_unit_raw", "zero", "one"], ["phase_a_unit"], name="phase_smooth_a_clip"),
            helper.make_node("Clip", ["phase_b_unit_raw", "zero", "one"], ["phase_b_unit"], name="phase_smooth_b_clip"),
            helper.make_node("Sub", ["one", "phase_a_unit"], ["phase_a_inv"], name="phase_smooth_a_inv"),
            helper.make_node("Sub", ["one", "phase_b_unit"], ["phase_b_inv"], name="phase_smooth_b_inv"),
            helper.make_node("Mul", ["phase_a_unit", "phase_b_unit"], ["w0"], name="phase_smooth_w0"),
            helper.make_node("Mul", ["phase_a_inv", "phase_b_unit"], ["w1"], name="phase_smooth_w1"),
            helper.make_node("Mul", ["phase_a_inv", "phase_b_inv"], ["w2"], name="phase_smooth_w2"),
            helper.make_node("Mul", ["phase_a_unit", "phase_b_inv"], ["w3"], name="phase_smooth_w3"),
            helper.make_node("Mul", ["phase0_actions", "w0"], ["weighted0"], name="phase_smooth_weight0"),
            helper.make_node("Mul", ["phase1_actions", "w1"], ["weighted1"], name="phase_smooth_weight1"),
            helper.make_node("Mul", ["phase2_actions", "w2"], ["weighted2"], name="phase_smooth_weight2"),
            helper.make_node("Mul", ["phase3_actions", "w3"], ["weighted3"], name="phase_smooth_weight3"),
            helper.make_node("Add", ["weighted0", "weighted1"], ["weighted01"], name="phase_smooth_add01"),
            helper.make_node("Add", ["weighted2", "weighted3"], ["weighted23"], name="phase_smooth_add23"),
            helper.make_node("Add", ["weighted01", "weighted23"], [args.output_name], name="phase_smooth_output"),
        ]
    )

    opset_versions = [
        imp.version for model in models for imp in model.opset_import if imp.domain == ""
    ]
    model = helper.make_model(
        graph,
        producer_name="open-duck-mini-rdkx5",
        opset_imports=[helper.make_operatorsetid("", max(opset_versions + [12]))],
    )
    model.ir_version = min(model.ir_version, 10)
    for index, policy in enumerate(policies):
        model.metadata_props.add(key=f"phase{index}_policy", value=str(policy))
    model.metadata_props.add(key="phase_a_index", value=str(args.phase_a_index))
    model.metadata_props.add(key="phase_b_index", value=str(args.phase_b_index))
    model.metadata_props.add(key="blend_rule", value="bilinear_from_clipped_phase_plus_one_half")

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    onnx.checker.check_model(model)
    onnx.save(model, output_path)
    report = verify_model(output_path, policies, int(args.phase_a_index), int(args.phase_b_index))
    if args.verify_json:
        verify_path = Path(args.verify_json)
        verify_path.parent.mkdir(parents=True, exist_ok=True)
        verify_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(output_path)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "PASS_ONNX_PHASE_SMOOTH_BLEND_VERIFY" else 1


if __name__ == "__main__":
    raise SystemExit(main())
