#!/usr/bin/env python3
"""Verify the reference-anchored residual actor without robot or GPU access."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys

import jax
import jax.numpy as jnp
import numpy as np
import onnx
import onnxruntime as ort


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location("reference_residual_ppo_networks", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def inspect_onnx(path: Path, reference: np.ndarray, expected_reference: bool) -> dict:
    model = onnx.load(path)
    onnx.checker.check_model(model)
    graph = model.graph
    ops = [node.op_type for node in graph.node]
    inputs = [[dim.dim_value for dim in value.type.tensor_type.shape.dim] for value in graph.input]
    outputs = [[dim.dim_value for dim in value.type.tensor_type.shape.dim] for value in graph.output]
    obs = np.zeros((1, 115), dtype=np.float32)
    obs[0, -14:] = reference
    session = ort.InferenceSession(str(path), providers=["CPUExecutionProvider"])
    action = session.run(None, {session.get_inputs()[0].name: obs})[0]
    clipped_reference = np.clip(reference, -1.0 + 1.0e-5, 1.0 - 1.0e-5)
    error = float(np.max(np.abs(action[0] - clipped_reference)))
    result = {
        "path": str(path),
        "sha256": sha256(path),
        "graph_name": graph.name,
        "operators": ops,
        "input_shapes": inputs,
        "output_shapes": outputs,
        "finite": bool(np.all(np.isfinite(action))),
        "max_abs_action": float(np.max(np.abs(action))),
        "max_reference_error": error,
    }
    if graph.name != "open_duck_reference_anchored_residual_final_action":
        raise AssertionError(f"unexpected ONNX graph name: {graph.name}")
    if inputs != [[1, 115]] or outputs != [[1, 14]]:
        raise AssertionError(f"unexpected ONNX interface: {inputs} -> {outputs}")
    if not {"Gather", "Clip", "Atanh", "Add", "Tanh"}.issubset(ops):
        raise AssertionError("ONNX graph is missing a required reference-residual operator")
    if not result["finite"] or result["max_abs_action"] > 1.000001:
        raise AssertionError("ONNX action is non-finite or outside [-1, 1]")
    if expected_reference and error > 1.0e-5:
        raise AssertionError(f"step-zero ONNX is not reference anchored: {error}")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--patch", type=Path, required=True)
    parser.add_argument("--table", type=Path, required=True)
    parser.add_argument("--step-zero-onnx", type=Path, required=True)
    parser.add_argument("--trained-smoke-onnx", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    if os.environ.get("JAX_PLATFORMS") != "cpu":
        raise RuntimeError("set JAX_PLATFORMS=cpu for this contract check")
    if any(device.platform != "cpu" for device in jax.devices()):
        raise RuntimeError(f"non-CPU JAX device visible: {jax.devices()}")

    module = load_module(args.source)
    network = module.make_reference_residual_ppo_networks(
        115,
        14,
        preprocess_observations_fn=lambda value, _stats: value,
        policy_hidden_layer_sizes=(512, 256, 128),
        value_hidden_layer_sizes=(512, 256, 128),
    )
    policy_params = network.policy_network.init(jax.random.PRNGKey(100))

    table = np.load(args.table)
    commands = table["commands"]
    command_index = int(np.argmin(np.linalg.norm(commands - np.array([0.074, 0.0, 0.0]), axis=1)))
    reference = np.asarray(table["actions"][command_index, 0], dtype=np.float32)
    obs = np.zeros((1, 115), dtype=np.float32)
    obs[0, -14:] = reference
    logits = network.policy_network.apply(None, policy_params, jnp.asarray(obs))
    initial_action = network.parametric_action_distribution.mode(logits)
    sampled_action = network.parametric_action_distribution.sample(
        logits, jax.random.PRNGKey(101)
    )
    log_prob = network.parametric_action_distribution.log_prob(logits, sampled_action)
    expected = np.clip(reference, -1.0 + 1.0e-5, 1.0 - 1.0e-5)
    initial_error = float(np.max(np.abs(np.asarray(initial_action)[0] - expected)))

    zero_obs = np.zeros((1, 115), dtype=np.float32)
    zero_logits = network.policy_network.apply(None, policy_params, jnp.asarray(zero_obs))
    zero_action = network.parametric_action_distribution.mode(zero_logits)
    zero_error = float(np.max(np.abs(np.asarray(zero_action))))

    if tuple(logits.shape) != (1, 28):
        raise AssertionError(f"unexpected policy logits shape {logits.shape}")
    if initial_error > 1.0e-6 or zero_error > 1.0e-7:
        raise AssertionError(
            f"initial anchoring failed: reference={initial_error}, zero={zero_error}"
        )
    if not np.all(np.isfinite(np.asarray(logits))) or not np.all(np.isfinite(np.asarray(log_prob))):
        raise AssertionError("non-finite PPO logits or log probability")

    step_zero = inspect_onnx(args.step_zero_onnx, reference, expected_reference=True)
    trained_smoke = inspect_onnx(args.trained_smoke_onnx, reference, expected_reference=False)
    result = {
        "schema_version": "ground_up_reference_residual_actor_contract.v1",
        "status": "PASS_CPU_REFERENCE_RESIDUAL_ACTOR_CONTRACT",
        "robot_access": False,
        "rdk_access": False,
        "local_gpu_access": False,
        "jax_devices": [str(device) for device in jax.devices()],
        "source": {"path": str(args.source), "sha256": sha256(args.source)},
        "runner_patch": {"path": str(args.patch), "sha256": sha256(args.patch)},
        "projected_reference_table": {
            "path": str(args.table),
            "sha256": sha256(args.table),
            "shape": list(table["actions"].shape),
            "selected_command_index": command_index,
            "selected_command": commands[command_index].tolist(),
        },
        "jax_policy": {
            "observation_size": 115,
            "action_size": 14,
            "logits_shape": list(logits.shape),
            "initial_reference_max_error": initial_error,
            "zero_reference_max_action": zero_error,
            "sampled_action_finite": bool(np.all(np.isfinite(np.asarray(sampled_action)))),
            "sampled_log_probability": float(np.asarray(log_prob)[0]),
        },
        "step_zero_onnx": step_zero,
        "trained_1024_step_smoke_onnx": trained_smoke,
        "interpretation": (
            "The actor, PPO probability path, one-update training export, and final-action "
            "ONNX composition are CPU-verified. This is a software contract pass, not a "
            "behavior-policy result or robot clearance."
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
