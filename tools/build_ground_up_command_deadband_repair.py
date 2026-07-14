#!/usr/bin/env python3
"""Build and contract-check the preregistered zero-command ONNX repair."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path

import numpy as np
import onnx
from onnx import helper, numpy_helper
import onnxruntime as ort


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rename_tensor(model: onnx.ModelProto, old: str, new: str) -> None:
    for node in model.graph.node:
        for index, name in enumerate(node.input):
            if name == old:
                node.input[index] = new
        for index, name in enumerate(node.output):
            if name == old:
                node.output[index] = new


def wrap(source: onnx.ModelProto, command_index: int, deadband: float) -> onnx.ModelProto:
    model = copy.deepcopy(source)
    rename_tensor(model, "continuous_actions", "deadband_source_actions")
    rename_tensor(model, "previous_action_out", "deadband_source_state")
    values = {
        "deadband_command_index": np.asarray([command_index], dtype=np.int64),
        "deadband_abs_limit": np.asarray([deadband], dtype=np.float32),
        "deadband_zero_action": np.zeros((1, 14), dtype=np.float32),
    }
    model.graph.initializer.extend(
        numpy_helper.from_array(value, name=name) for name, value in values.items()
    )
    model.graph.node.extend(
        [
            helper.make_node("Gather", ["obs", "deadband_command_index"], ["deadband_command_x"], axis=1, name="deadband_gather_command_x"),
            helper.make_node("Abs", ["deadband_command_x"], ["deadband_abs_command_x"], name="deadband_abs_command"),
            helper.make_node("LessOrEqual", ["deadband_abs_command_x", "deadband_abs_limit"], ["deadband_is_zero_command"], name="deadband_compare"),
            helper.make_node("Where", ["deadband_is_zero_command", "deadband_zero_action", "deadband_source_actions"], ["continuous_actions"], name="deadband_select_action"),
            helper.make_node("Where", ["deadband_is_zero_command", "deadband_zero_action", "deadband_source_state"], ["previous_action_out"], name="deadband_select_state"),
        ]
    )
    onnx.checker.check_model(model)
    return model


def contract(source_path: Path, wrapped_path: Path, command_index: int) -> dict:
    source = ort.InferenceSession(str(source_path), providers=["CPUExecutionProvider"])
    wrapped = ort.InferenceSession(str(wrapped_path), providers=["CPUExecutionProvider"])
    rng = np.random.default_rng(20260714)
    max_zero_action = 0.0
    max_zero_state = 0.0
    max_positive_action_error = 0.0
    max_positive_state_error = 0.0
    all_finite = True
    for command_x in (0.0, 0.074, 0.077, 0.080):
        for _ in range(128):
            obs = rng.normal(0.0, 1.0, size=(1, 115)).astype(np.float32)
            obs[:, command_index] = command_x
            previous = rng.uniform(-1.0, 1.0, size=(1, 14)).astype(np.float32)
            source_action, source_state = source.run(None, {"obs": obs, "previous_action": previous})
            action, state = wrapped.run(None, {"obs": obs, "previous_action": previous})
            all_finite = all_finite and bool(np.all(np.isfinite(action)) and np.all(np.isfinite(state)))
            if command_x == 0.0:
                max_zero_action = max(max_zero_action, float(np.max(np.abs(action))))
                max_zero_state = max(max_zero_state, float(np.max(np.abs(state))))
            else:
                max_positive_action_error = max(
                    max_positive_action_error, float(np.max(np.abs(action - source_action)))
                )
                max_positive_state_error = max(
                    max_positive_state_error, float(np.max(np.abs(state - source_state)))
                )
    return {
        "provider": wrapped.get_providers()[0],
        "all_finite": all_finite,
        "max_zero_action": max_zero_action,
        "max_zero_state": max_zero_state,
        "max_positive_action_error": max_positive_action_error,
        "max_positive_state_error": max_positive_state_error,
        "pass": (
            all_finite
            and max_zero_action == 0.0
            and max_zero_state == 0.0
            and max_positive_action_error == 0.0
            and max_positive_state_error == 0.0
            and wrapped.get_providers()[0] == "CPUExecutionProvider"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preregistration", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-md", type=Path, required=True)
    args = parser.parse_args()
    prereg = json.loads(args.preregistration.read_text())
    command_index = int(prereg["transform"]["command_x_observation_index"])
    deadband = float(prereg["transform"]["zero_deadband_absolute_command_x"])
    args.output_root.mkdir(parents=True, exist_ok=True)
    policies = []
    for spec in prereg["source_policies"]:
        source_path = Path(spec["path"])
        source_model = onnx.load(str(source_path))
        source_initializers = {
            item.name: np.asarray(numpy_helper.to_array(item))
            for item in source_model.graph.initializer
        }
        model = wrap(source_model, command_index, deadband)
        output_path = args.output_root / f"T2_EQUAL_{spec['step']}.onnx"
        onnx.save(model, output_path)
        wrapped_initializers = {
            item.name: np.asarray(numpy_helper.to_array(item))
            for item in model.graph.initializer
        }
        source_initializers_exact = all(
            name in wrapped_initializers and np.array_equal(value, wrapped_initializers[name])
            for name, value in source_initializers.items()
        )
        inference = contract(source_path, output_path, command_index)
        policies.append(
            {
                "step": spec["step"],
                "source_path": str(source_path.resolve()),
                "source_sha256": sha256(source_path),
                "output_path": str(output_path.resolve()),
                "output_sha256": sha256(output_path),
                "inputs": [item.name for item in model.graph.input],
                "outputs": [item.name for item in model.graph.output],
                "source_initializers_exact": source_initializers_exact,
                "source_node_types_and_attributes_prefix_exact": all(
                    left.op_type == right.op_type and list(left.attribute) == list(right.attribute)
                    for left, right in zip(source_model.graph.node, model.graph.node)
                ),
                "appended_node_count": len(model.graph.node) - len(source_model.graph.node),
                "inference_contract": inference,
            }
        )
    checks = {
        "preregistration_status_valid": prereg["status"] == "PREREGISTERED_CPU_ONLY",
        "exactly_two_policies_built": len(policies) == 2,
        "external_interfaces_exact": all(
            item["inputs"] == ["obs", "previous_action"]
            and item["outputs"] == ["continuous_actions", "previous_action_out"]
            for item in policies
        ),
        "all_source_initializers_exact": all(item["source_initializers_exact"] for item in policies),
        "all_source_node_prefixes_preserved": all(item["source_node_types_and_attributes_prefix_exact"] for item in policies),
        "all_append_exactly_five_nodes": all(item["appended_node_count"] == 5 for item in policies),
        "all_cpu_inference_contracts_pass": all(item["inference_contract"]["pass"] for item in policies),
    }
    failed = [name for name, passed in checks.items() if not passed]
    status = "PASS_COMMAND_DEADBAND_REPAIR_TRANSFORM_CONTRACT" if not failed else "FAIL_COMMAND_DEADBAND_REPAIR_TRANSFORM_CONTRACT"
    payload = {
        "schema_version": "ground_up_command_deadband_repair_transform_contract.v1",
        "status": status,
        "checks": checks,
        "failed_checks": failed,
        "policies": policies,
        "authority": {
            "cpu_behavior_eval": not failed,
            "robustness_ladder": False,
            "training": False,
            "colab": False,
            "local_gpu": False,
            "rdk_or_robot": False,
        },
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    lines = ["# Ground-Up Command-Deadband Repair Transform Contract", "", f"status: `{status}`", ""]
    lines.extend(f"- {name}: `{passed}`" for name, passed in checks.items())
    lines.extend(["", "Passing authorizes only the preregistered 16-cell CPU behavior matrix.", "No robustness ladder, training, RDK-X5, or robot access is authorized.", ""])
    args.output_md.write_text("\n".join(lines))
    print(json.dumps({"status": status, "failed": failed, "policies": len(policies)}))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
