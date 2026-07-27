#!/usr/bin/env python3
"""Build and contract-check the preregistered T23 action-margin policies."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
import onnx
from onnx import helper, numpy_helper
import onnxruntime as ort


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "t28_t23_action_margin_preregistration.json"
T27_RESULT = ANALYSIS / "t27_t23_robustness_matrix_result.json"
OUTPUT = ANALYSIS / "t28_t23_action_margin_transform_contract.json"
OUTPUT_MD = ANALYSIS / "T28_T23_ACTION_MARGIN_TRANSFORM_CONTRACT_20260726.md"
OUTPUT_ROOT = (
    Path(r"D:\CodexArtifacts\open-duck-policy")
    / "t28_t23_action_margin_policies_v1"
)
EXPECTED_INPUTS = [
    "obs",
    "previous_action",
    "h_in",
    "calibration_context",
]
EXPECTED_OUTPUTS = ["continuous_actions", "previous_action_out", "h_out"]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: Any) -> str:
    payload = dict(value)
    payload.pop("result_sha256", None)
    return hashlib.sha256(
        json.dumps(
            payload,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def receipt(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def rename_node_tensor(model: onnx.ModelProto, old: str, new: str) -> None:
    for node in model.graph.node:
        for index, name in enumerate(node.input):
            if name == old:
                node.input[index] = new
        for index, name in enumerate(node.output):
            if name == old:
                node.output[index] = new


def wrap(source: onnx.ModelProto, limit: np.float32) -> onnx.ModelProto:
    model = copy.deepcopy(source)
    rename_node_tensor(
        model,
        "continuous_actions",
        "action_margin_source_actions",
    )
    rename_node_tensor(
        model,
        "previous_action_out",
        "action_margin_source_previous_action",
    )
    model.graph.initializer.extend(
        [
            numpy_helper.from_array(
                np.asarray([-limit], dtype=np.float32),
                name="action_margin_min",
            ),
            numpy_helper.from_array(
                np.asarray([limit], dtype=np.float32),
                name="action_margin_max",
            ),
        ]
    )
    model.graph.node.extend(
        [
            helper.make_node(
                "Clip",
                [
                    "action_margin_source_actions",
                    "action_margin_min",
                    "action_margin_max",
                ],
                ["continuous_actions"],
                name="action_margin_clip_actions",
            ),
            helper.make_node(
                "Clip",
                [
                    "action_margin_source_previous_action",
                    "action_margin_min",
                    "action_margin_max",
                ],
                ["previous_action_out"],
                name="action_margin_clip_previous_action",
            ),
        ]
    )
    onnx.checker.check_model(model)
    return model


def arrays_by_initializer(model: onnx.ModelProto) -> dict[str, np.ndarray]:
    return {
        item.name: np.asarray(numpy_helper.to_array(item))
        for item in model.graph.initializer
    }


def normalized_node_signature(node: onnx.NodeProto) -> tuple[Any, ...]:
    rename = {
        "action_margin_source_actions": "continuous_actions",
        "action_margin_source_previous_action": "previous_action_out",
    }
    return (
        node.op_type,
        node.domain,
        node.name,
        tuple(rename.get(name, name) for name in node.input),
        tuple(rename.get(name, name) for name in node.output),
        tuple(item.SerializeToString() for item in node.attribute),
    )


def sample_trace_rows(
    result: dict[str, Any],
    checkpoint_id: str,
    threshold: float,
) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    for block in result["blocks"]:
        if block["checkpoint_id"] != checkpoint_id:
            continue
        manifest_path = Path(block["manifest"]["path"])
        if sha256(manifest_path) != block["manifest"]["sha256"]:
            raise ValueError(f"changed T27 manifest: {manifest_path}")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for trace in manifest["traces"]:
            path = Path(trace["path"])
            if sha256(path) != trace["sha256"]:
                raise ValueError(f"changed T27 trace: {path}")
            with path.open(encoding="utf-8") as stream:
                for line in stream:
                    row = json.loads(line)
                    event = any(
                        abs(float(value)) >= threshold
                        for value in row["action"]
                    )
                    periodic = int(row["tick"]) % 50 == 0
                    x0 = float(row["command"][0]) == 0.0
                    if event or periodic or (x0 and int(row["tick"]) % 10 == 0):
                        selected.append(row)
    return selected


def graph_contract(
    source_path: Path,
    wrapped_path: Path,
    checkpoint_id: str,
    result: dict[str, Any],
    limit: np.float32,
    threshold: np.float32,
    trace_tolerance: float,
) -> dict[str, Any]:
    source_model = onnx.load(str(source_path))
    wrapped_model = onnx.load(str(wrapped_path))
    source_initializers = arrays_by_initializer(source_model)
    wrapped_initializers = arrays_by_initializer(wrapped_model)
    source_session = ort.InferenceSession(
        str(source_path),
        providers=["CPUExecutionProvider"],
    )
    wrapped_session = ort.InferenceSession(
        str(wrapped_path),
        providers=["CPUExecutionProvider"],
    )
    rows = sample_trace_rows(result, checkpoint_id, float(threshold))
    max_source_trace_action_error = 0.0
    max_source_trace_previous_error = 0.0
    max_source_trace_hidden_error = 0.0
    clipped_action_bit_exact = True
    clipped_previous_bit_exact = True
    hidden_bit_exact = True
    realized_feedback_bit_exact = True
    outputs_strictly_below_threshold = True
    x0_source_bit_exact = True
    interior_source_bit_exact = True
    finite = True
    changed_values = 0
    for row in rows:
        inputs = {
            "obs": np.asarray([row["obs_state"]], dtype=np.float32),
            "previous_action": np.asarray(
                row["policy_state_input"]["previous_action"],
                dtype=np.float32,
            ),
            "h_in": np.asarray(
                row["policy_state_input"]["h_in"],
                dtype=np.float32,
            ),
            "calibration_context": np.zeros((1, 64), dtype=np.float32),
        }
        source_outputs = source_session.run(None, inputs)
        wrapped_outputs = wrapped_session.run(None, inputs)
        trace_action = np.asarray([row["action"]], dtype=np.float32)
        trace_previous = np.asarray(
            row["policy_state_output"]["previous_action_out"],
            dtype=np.float32,
        )
        trace_hidden = np.asarray(
            row["policy_state_output"]["h_out"],
            dtype=np.float32,
        )
        max_source_trace_action_error = max(
            max_source_trace_action_error,
            float(np.max(np.abs(source_outputs[0] - trace_action))),
        )
        max_source_trace_previous_error = max(
            max_source_trace_previous_error,
            float(np.max(np.abs(source_outputs[1] - trace_previous))),
        )
        max_source_trace_hidden_error = max(
            max_source_trace_hidden_error,
            float(np.max(np.abs(source_outputs[2] - trace_hidden))),
        )
        expected_action = np.clip(source_outputs[0], -limit, limit)
        expected_previous = np.clip(source_outputs[1], -limit, limit)
        clipped_action_bit_exact &= np.array_equal(
            wrapped_outputs[0],
            expected_action,
        )
        clipped_previous_bit_exact &= np.array_equal(
            wrapped_outputs[1],
            expected_previous,
        )
        hidden_bit_exact &= np.array_equal(
            wrapped_outputs[2],
            source_outputs[2],
        )
        realized_feedback_bit_exact &= np.array_equal(
            wrapped_outputs[0],
            wrapped_outputs[1],
        )
        outputs_strictly_below_threshold &= bool(
            np.all(np.abs(wrapped_outputs[0]) < threshold)
            and np.all(np.abs(wrapped_outputs[1]) < threshold)
        )
        if float(row["command"][0]) == 0.0:
            x0_source_bit_exact &= bool(
                np.array_equal(wrapped_outputs[0], source_outputs[0])
                and np.array_equal(wrapped_outputs[1], source_outputs[1])
            )
        interior = bool(
            np.all(np.abs(source_outputs[0]) <= limit)
            and np.all(np.abs(source_outputs[1]) <= limit)
        )
        if interior:
            interior_source_bit_exact &= bool(
                np.array_equal(wrapped_outputs[0], source_outputs[0])
                and np.array_equal(wrapped_outputs[1], source_outputs[1])
            )
        changed_values += int(
            np.count_nonzero(wrapped_outputs[0] != source_outputs[0])
        )
        finite &= all(bool(np.all(np.isfinite(item))) for item in wrapped_outputs)
    inputs = [item.name for item in wrapped_model.graph.input]
    outputs = [item.name for item in wrapped_model.graph.output]
    source_initializers_exact = all(
        name in wrapped_initializers
        and np.array_equal(value, wrapped_initializers[name])
        for name, value in source_initializers.items()
    )
    source_node_prefix_exact = all(
        normalized_node_signature(left) == normalized_node_signature(right)
        for left, right in zip(
            source_model.graph.node,
            wrapped_model.graph.node,
            strict=False,
        )
    )
    checks = {
        "external_abi_exact": (
            inputs == EXPECTED_INPUTS and outputs == EXPECTED_OUTPUTS
        ),
        "source_initializers_exact": source_initializers_exact,
        "source_node_prefix_exact": source_node_prefix_exact,
        "exactly_two_nodes_appended": (
            len(wrapped_model.graph.node) - len(source_model.graph.node) == 2
        ),
        "exactly_two_initializers_appended": (
            len(wrapped_model.graph.initializer)
            - len(source_model.graph.initializer)
            == 2
        ),
        "source_trace_replay_within_tolerance": (
            max_source_trace_action_error <= trace_tolerance
            and max_source_trace_previous_error <= trace_tolerance
            and max_source_trace_hidden_error <= trace_tolerance
        ),
        "clipped_action_bit_exact": clipped_action_bit_exact,
        "clipped_previous_action_bit_exact": clipped_previous_bit_exact,
        "hidden_output_bit_exact": hidden_bit_exact,
        "realized_action_feedback_bit_exact": realized_feedback_bit_exact,
        "outputs_strictly_below_threshold": (
            outputs_strictly_below_threshold
        ),
        "x0_source_bit_exact": x0_source_bit_exact,
        "interior_source_bit_exact": interior_source_bit_exact,
        "observed_transform_activation": (
            changed_values > 0 or checkpoint_id == "T23_SUPPORT_HALF"
        ),
        "all_outputs_finite": finite,
        "cpu_provider": (
            wrapped_session.get_providers()[0] == "CPUExecutionProvider"
        ),
    }
    return {
        "checkpoint_id": checkpoint_id,
        "source": receipt(source_path),
        "wrapped": receipt(wrapped_path),
        "inputs": inputs,
        "outputs": outputs,
        "source_nodes": len(source_model.graph.node),
        "wrapped_nodes": len(wrapped_model.graph.node),
        "sampled_trace_rows": len(rows),
        "changed_action_values": changed_values,
        "maximum_source_trace_action_error": max_source_trace_action_error,
        "maximum_source_trace_previous_action_error": (
            max_source_trace_previous_error
        ),
        "maximum_source_trace_hidden_error": max_source_trace_hidden_error,
        "checks": checks,
        "pass": all(checks.values()),
    }


def main() -> int:
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    result = json.loads(T27_RESULT.read_text(encoding="utf-8"))
    expected_prereg_hash = prereg["preregistered_contract_sha256"]
    current_prereg_hash = hashlib.sha256(
        json.dumps(
            {
                key: value
                for key, value in prereg.items()
                if key != "preregistered_contract_sha256"
            },
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()
    if current_prereg_hash != expected_prereg_hash:
        raise ValueError("changed T28 preregistration contract")
    if prereg["status"] != "PREREGISTERED_T28_T23_ACTION_MARGIN_REPAIR":
        raise ValueError("T28 preregistration is not green")
    limit = np.float32(prereg["transform"]["stored_float32_limit_abs"])
    threshold = np.float32(
        prereg["transform"]["saturation_observation_threshold_abs"]
    )
    trace_tolerance = float(
        prereg["cpu_contract"]["source_trace_replay_tolerance"]
    )
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    policies: list[dict[str, Any]] = []
    for spec in prereg["source_policies"]:
        source_path = Path(spec["path"])
        if sha256(source_path) != spec["sha256"]:
            raise ValueError(f"changed T23 source policy: {source_path}")
        source_model = onnx.load(str(source_path))
        wrapped_model = wrap(source_model, limit)
        output_path = OUTPUT_ROOT / (
            f"T28_MARGIN_{int(spec['step'])}.onnx"
        )
        onnx.save(wrapped_model, output_path)
        policies.append(
            graph_contract(
                source_path,
                output_path,
                spec["checkpoint_id"],
                result,
                limit,
                threshold,
                trace_tolerance,
            )
            | {"step": int(spec["step"])}
        )
    checks = {
        "preregistration_hash_exact": (
            current_prereg_hash == expected_prereg_hash
        ),
        "exactly_two_policies": len(policies) == 2,
        "all_policy_contracts_pass": all(item["pass"] for item in policies),
        "both_checkpoints_uniform_limit": all(
            item["checks"]["outputs_strictly_below_threshold"]
            for item in policies
        ),
        "half_is_interior_on_frozen_samples": (
            policies[0]["changed_action_values"] == 0
        ),
        "final_transform_activates_on_frozen_samples": (
            policies[1]["changed_action_values"] > 0
        ),
    }
    failed_checks = [name for name, passed in checks.items() if not passed]
    payload: dict[str, Any] = {
        "schema_version": "open_duck.t28_t23_action_margin_contract.v1",
        "status": (
            "PASS_T28_T23_ACTION_MARGIN_TRANSFORM_CONTRACT"
            if not failed_checks
            else "FAIL_T28_T23_ACTION_MARGIN_TRANSFORM_CONTRACT"
        ),
        "preregistered_contract_sha256": expected_prereg_hash,
        "stored_float32_limit_abs": float(limit),
        "saturation_observation_threshold_abs": float(threshold),
        "policies": policies,
        "checks": checks,
        "failed_checks": failed_checks,
        "authority": {
            "condition_one_preregistration": not failed_checks,
            "behavior_evaluation": False,
            "training": False,
            "colab": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
            "gate5": False,
        },
    }
    payload["result_sha256"] = canonical_sha256(payload)
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    lines = [
        "# T28 T23 action-margin transform contract",
        "",
        f"status: `{payload['status']}`",
        "",
    ]
    lines.extend(f"- {name}: `{passed}`" for name, passed in checks.items())
    lines.extend(
        [
            "",
            (
                f"Both policies use `L={float(limit):.10f}`, strictly below "
                f"the frozen `{float(threshold):.2f}` saturation margin."
            ),
            "",
            "Passing authorizes only preregistration of the 16-cell CPU "
            "floor-friction-0.5 falsifier. It does not authorize training, "
            "Gate 5, RDK-X5, robot, torque, or motion.",
            "",
        ]
    )
    OUTPUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(payload["status"])
    print(f"failed_checks={failed_checks}")
    print(f"result_sha256={payload['result_sha256']}")
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed_checks else 1


if __name__ == "__main__":
    raise SystemExit(main())
