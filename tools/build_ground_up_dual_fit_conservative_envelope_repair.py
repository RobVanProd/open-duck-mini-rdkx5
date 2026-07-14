#!/usr/bin/env python3
"""Build and contract-check the preregistered dual-fit envelope repair."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path

import numpy as np
import onnx
from onnx import numpy_helper
import onnxruntime as ort


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def initializer_map(model: onnx.ModelProto) -> dict[str, np.ndarray]:
    return {item.name: np.asarray(numpy_helper.to_array(item)) for item in model.graph.initializer}


def replace_left_ankle_delta(model: onnx.ModelProto, value: float) -> tuple[float, float]:
    for index, item in enumerate(model.graph.initializer):
        if item.name != "max_action_delta":
            continue
        array = np.asarray(numpy_helper.to_array(item)).copy()
        old = float(array[0, 4])
        array[0, 4] = np.float32(value)
        model.graph.initializer[index].CopyFrom(numpy_helper.from_array(array, name=item.name))
        return old, float(array[0, 4])
    raise KeyError("max_action_delta initializer not found")


def inference_contract(path: Path, commands: list[float]) -> dict:
    session = ort.InferenceSession(str(path), providers=["CPUExecutionProvider"])
    rng = np.random.default_rng(20260714)
    max_zero_action = 0.0
    max_zero_state = 0.0
    max_left_ankle_delta = 0.0
    max_other_pitch_excess = 0.0
    finite = True
    original_bounds = np.asarray([0.12, 0.12, 0.14, 0.10, 0.08, 0.10], dtype=np.float32)
    pitch_indices = np.asarray([2, 3, 4, 11, 12, 13], dtype=int)
    for command in commands:
        previous = np.zeros((1, 14), dtype=np.float32)
        for _ in range(256):
            obs = rng.normal(0.0, 0.5, size=(1, 115)).astype(np.float32)
            obs[:, 6] = command
            # Keep the measured joint-offset slot physically consistent with
            # the previous normalized target. Otherwise the downstream
            # actual-position guard correctly overrides the upstream rate
            # clamp in response to an impossible randomized state.
            obs[:, 13:27] = previous * np.float32(0.25)
            action, state = session.run(None, {"obs": obs, "previous_action": previous})
            finite &= bool(np.all(np.isfinite(action)) and np.all(np.isfinite(state)))
            if command == 0.0:
                max_zero_action = max(max_zero_action, float(np.max(np.abs(action))))
                max_zero_state = max(max_zero_state, float(np.max(np.abs(state))))
            else:
                delta = np.abs(action - previous)[0, pitch_indices]
                max_left_ankle_delta = max(max_left_ankle_delta, float(delta[2]))
                excess = np.maximum(delta - original_bounds, 0.0)
                excess[2] = max(float(delta[2]) - 0.12, 0.0)
                max_other_pitch_excess = max(max_other_pitch_excess, float(np.max(excess)))
            previous = state
    tolerance = 5.0e-7
    return {
        "provider": session.get_providers()[0],
        "all_finite": finite,
        "max_zero_action": max_zero_action,
        "max_zero_state": max_zero_state,
        "max_left_ankle_action_delta": max_left_ankle_delta,
        "max_pitch_bound_excess": max_other_pitch_excess,
        "tolerance": tolerance,
        "pass": (
            session.get_providers()[0] == "CPUExecutionProvider"
            and finite
            and max_zero_action == 0.0
            and max_zero_state == 0.0
            and max_left_ankle_delta <= 0.12 + tolerance
            and max_other_pitch_excess <= tolerance
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
    args.output_root.mkdir(parents=True, exist_ok=True)
    policies = []
    for spec in prereg["source_policies"]:
        source_path = Path(spec["path"])
        source = onnx.load(str(source_path))
        model = copy.deepcopy(source)
        old_value, new_value = replace_left_ankle_delta(model, prereg["transform"]["new_normalized_delta"])
        onnx.checker.check_model(model)
        output_path = args.output_root / f"T2_EQUAL_{spec['step']}.onnx"
        onnx.save(model, output_path)
        source_inits = initializer_map(source)
        output_inits = initializer_map(model)
        changed = []
        all_other_exact = True
        for name, source_value in source_inits.items():
            output_value = output_inits[name]
            if np.array_equal(source_value, output_value):
                continue
            changed.append(name)
            if name != "max_action_delta":
                all_other_exact = False
        delta_source = source_inits["max_action_delta"]
        delta_output = output_inits["max_action_delta"]
        difference_indices = np.argwhere(delta_source != delta_output).tolist()
        policies.append({
            "step": spec["step"],
            "source_path": str(source_path.resolve()),
            "source_sha256": sha256(source_path),
            "expected_source_sha256": spec["sha256"],
            "output_path": str(output_path.resolve()),
            "output_sha256": sha256(output_path),
            "old_value": old_value,
            "new_value": new_value,
            "changed_initializers": changed,
            "changed_initializer_indices": difference_indices,
            "all_other_initializers_exact": all_other_exact,
            "nodes_exact": all(left.SerializeToString() == right.SerializeToString() for left, right in zip(source.graph.node, model.graph.node)) and len(source.graph.node) == len(model.graph.node),
            "inputs_exact": [item.SerializeToString() for item in source.graph.input] == [item.SerializeToString() for item in model.graph.input],
            "outputs_exact": [item.SerializeToString() for item in source.graph.output] == [item.SerializeToString() for item in model.graph.output],
            "inference": inference_contract(output_path, prereg["behavior_matrix"]["commands_x"]),
        })
    checks = {
        "preregistration_valid": prereg["status"] == "PREREGISTERED_CPU_ONLY",
        "exact_two_policies": len(policies) == 2,
        "source_hashes_exact": all(item["source_sha256"] == item["expected_source_sha256"] for item in policies),
        "only_named_initializer_changed": all(item["changed_initializers"] == ["max_action_delta"] for item in policies),
        "only_left_ankle_element_changed": all(item["changed_initializer_indices"] == [[0, 4]] for item in policies),
        "old_and_new_values_exact": all(abs(item["old_value"] - np.float32(0.14)) == 0.0 and abs(item["new_value"] - np.float32(0.12)) == 0.0 for item in policies),
        "all_other_initializers_exact": all(item["all_other_initializers_exact"] for item in policies),
        "nodes_and_interfaces_exact": all(item["nodes_exact"] and item["inputs_exact"] and item["outputs_exact"] for item in policies),
        "all_cpu_inference_contracts_pass": all(item["inference"]["pass"] for item in policies),
    }
    failed = [key for key, value in checks.items() if not value]
    status = "PASS_DUAL_FIT_CONSERVATIVE_ENVELOPE_TRANSFORM_CONTRACT" if not failed else "FAIL_DUAL_FIT_CONSERVATIVE_ENVELOPE_TRANSFORM_CONTRACT"
    payload = {
        "schema_version": "ground_up_dual_fit_conservative_envelope_transform_contract.v1",
        "status": status,
        "checks": checks,
        "failed_checks": failed,
        "policies": policies,
        "authority": {"run_16_cell_cpu_behavior": not failed, "r2_or_later": False, "training": False, "colab": False, "local_gpu": False, "rdk_or_robot": False},
    }
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    lines = ["# Ground-Up Dual-Fit Conservative-Envelope Transform Contract", "", f"status: `{status}`", ""]
    lines.extend(f"- {key}: `{value}`" for key, value in checks.items())
    lines.extend(["", "Passing authorizes only the preregistered 16-cell dual-fit CPU behavior matrix.", "No R2+, training, Colab, RDK-X5, or robot access is authorized.", ""])
    args.output_md.write_text("\n".join(lines))
    print(json.dumps({"status": status, "failed_checks": failed}))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
