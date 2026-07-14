#!/usr/bin/env python3
"""Verify the preregistered hard-vector continuation CPU smoke."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

from flax.training import orbax_utils
import jax
import numpy as np
import onnx
import onnxruntime as ort
from orbax import checkpoint as ocp
from tensorboard.backend.event_processing.event_accumulator import EventAccumulator


VELOCITY_LIMITS = np.array(
    [
        5.24,
        5.24,
        1.50,
        1.50,
        1.75,
        5.24,
        5.24,
        5.24,
        5.24,
        5.24,
        5.24,
        1.25,
        1.00,
        1.25,
    ],
    dtype=np.float32,
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_directory(path: Path) -> str:
    digest = hashlib.sha256()
    for child in sorted(item for item in path.rglob("*") if item.is_file()):
        digest.update(str(child.relative_to(path)).encode())
        digest.update(b"\0")
        with child.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
    return digest.hexdigest()


def require_cpu() -> None:
    if os.environ.get("JAX_PLATFORMS") != "cpu":
        raise RuntimeError("set JAX_PLATFORMS=cpu")
    if any(device.platform != "cpu" for device in jax.devices()):
        raise RuntimeError(f"non-CPU JAX device visible: {jax.devices()}")


def restore_and_compare(source: Path, step_zero: Path, final: Path) -> dict:
    checkpointer = ocp.PyTreeCheckpointer()
    step_zero_tree = checkpointer.restore(str(step_zero))
    restore_args = orbax_utils.restore_args_from_target(step_zero_tree)
    source_tree = checkpointer.restore(
        str(source), item=step_zero_tree, restore_args=restore_args
    )
    final_tree = checkpointer.restore(str(final))

    source_leaves = jax.tree_util.tree_leaves(source_tree)
    step_zero_leaves = jax.tree_util.tree_leaves(step_zero_tree)
    final_leaves = jax.tree_util.tree_leaves(final_tree)
    if not (
        jax.tree_util.tree_structure(source_tree)
        == jax.tree_util.tree_structure(step_zero_tree)
        == jax.tree_util.tree_structure(final_tree)
    ):
        raise AssertionError("checkpoint tree structures differ")

    source_zero_errors = [
        float(np.max(np.abs(np.asarray(source) - np.asarray(zero))))
        for source, zero in zip(source_leaves, step_zero_leaves, strict=True)
    ]
    final_deltas = [
        float(np.max(np.abs(np.asarray(final_value) - np.asarray(zero))))
        for final_value, zero in zip(final_leaves, step_zero_leaves, strict=True)
    ]
    policy_zero = jax.tree_util.tree_leaves(step_zero_tree[1])
    policy_final = jax.tree_util.tree_leaves(final_tree[1])
    policy_deltas = [
        float(np.max(np.abs(np.asarray(final_value) - np.asarray(zero))))
        for final_value, zero in zip(policy_final, policy_zero, strict=True)
    ]
    finite = all(
        np.all(np.isfinite(np.asarray(leaf)))
        for leaf in (*source_leaves, *step_zero_leaves, *final_leaves)
    )
    return {
        "checks": {
            "step_zero_exactly_matches_protected_source": max(source_zero_errors) == 0.0,
            "all_checkpoint_leaves_finite": bool(finite),
            "at_least_one_policy_leaf_changed": max(policy_deltas) > 0.0,
        },
        "leaf_count": len(source_leaves),
        "policy_leaf_count": len(policy_zero),
        "max_source_to_step_zero_error": max(source_zero_errors),
        "changed_final_leaf_count": sum(delta > 0.0 for delta in final_deltas),
        "changed_policy_leaf_count": sum(delta > 0.0 for delta in policy_deltas),
        "max_policy_leaf_delta": max(policy_deltas),
        "source_directory_sha256": sha256_directory(source),
        "step_zero_directory_sha256": sha256_directory(step_zero),
        "final_directory_sha256": sha256_directory(final),
    }


def inspect_onnx(path: Path) -> dict:
    model = onnx.load(path)
    onnx.checker.check_model(model)
    input_names = [value.name for value in model.graph.input]
    output_names = [value.name for value in model.graph.output]
    session = ort.InferenceSession(str(path), providers=["CPUExecutionProvider"])
    obs_size = session.get_inputs()[0].shape[-1]
    obs = np.zeros((1, obs_size), dtype=np.float32)
    previous = np.zeros((1, 14), dtype=np.float32)
    max_delta = VELOCITY_LIMITS * 0.02 / 0.25
    bound_excess = []
    state_errors = []
    all_finite = True
    for index in range(8):
        obs[:, -14:] = 0.8 if index % 2 == 0 else -0.8
        action, previous_out = session.run(
            output_names, {"obs": obs, "previous_action": previous}
        )
        all_finite &= bool(np.all(np.isfinite(action)))
        bound_excess.append(float(np.max(np.abs(action - previous) - max_delta)))
        state_errors.append(float(np.max(np.abs(previous_out - action))))
        previous = previous_out
    checks = {
        "interface_exact": input_names == ["obs", "previous_action"]
        and output_names == ["continuous_actions", "previous_action_out"],
        "actions_finite": all_finite,
        "eight_tick_bound_excess_at_most_1e_6": max(bound_excess) <= 1.0e-6,
        "state_output_exact": max(state_errors) <= 1.0e-7,
    }
    return {
        "path": str(path),
        "sha256": sha256_file(path),
        "graph_name": model.graph.name,
        "inputs": input_names,
        "outputs": output_names,
        "max_bound_excess": max(bound_excess),
        "max_state_output_error": max(state_errors),
        "checks": checks,
    }


def read_metrics(event_file: Path) -> dict:
    accumulator = EventAccumulator(str(event_file), size_guidance={"scalars": 0})
    accumulator.Reload()
    values = {}
    for tag in accumulator.Tags().get("scalars", []):
        values[tag] = [
            {"step": int(event.step), "value": float(event.value)}
            for event in accumulator.Scalars(tag)
        ]
    flattened = [entry["value"] for entries in values.values() for entry in entries]
    return {
        "checks": {
            "metrics_present": bool(flattened),
            "all_metrics_finite": bool(flattened)
            and bool(np.all(np.isfinite(flattened))),
            "contains_step_zero_and_1024": {0, 1024}.issubset(
                {entry["step"] for entries in values.values() for entry in entries}
            ),
        },
        "path": str(event_file),
        "sha256": sha256_file(event_file),
        "scalars": values,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-checkpoint", type=Path, required=True)
    parser.add_argument("--step-zero-checkpoint", type=Path, required=True)
    parser.add_argument("--final-checkpoint", type=Path, required=True)
    parser.add_argument("--step-zero-onnx", type=Path, required=True)
    parser.add_argument("--final-onnx", type=Path, required=True)
    parser.add_argument("--event-file", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-md", type=Path, required=True)
    args = parser.parse_args()

    require_cpu()
    checkpoints = restore_and_compare(
        args.source_checkpoint.resolve(),
        args.step_zero_checkpoint.resolve(),
        args.final_checkpoint.resolve(),
    )
    step_zero_onnx = inspect_onnx(args.step_zero_onnx.resolve())
    final_onnx = inspect_onnx(args.final_onnx.resolve())
    metrics = read_metrics(args.event_file.resolve())
    checks = {
        **checkpoints["checks"],
        **{f"step_zero_onnx_{key}": value for key, value in step_zero_onnx["checks"].items()},
        **{f"final_onnx_{key}": value for key, value in final_onnx["checks"].items()},
        **metrics["checks"],
    }
    failed = [name for name, value in checks.items() if not value]
    status = (
        "PASS_CPU_HARD_VECTOR_CONTINUATION_SMOKE"
        if not failed
        else "FAIL_CPU_HARD_VECTOR_CONTINUATION_SMOKE"
    )
    payload = {
        "schema_version": "ground_up_hard_vector_continuation_smoke.v1",
        "status": status,
        "execution": {
            "jax_backend": jax.default_backend(),
            "jax_devices": [str(device) for device in jax.devices()],
            "robot_access": False,
            "rdk_access": False,
            "local_gpu_access": False,
            "colab_access": False,
        },
        "checks": checks,
        "checkpoints": checkpoints,
        "step_zero_onnx": step_zero_onnx,
        "final_onnx": final_onnx,
        "metrics": metrics,
        "failed_invocation": {
            "updated_policy": False,
            "reason": (
                "Absolute script invocation resolved playground.common.runner from the "
                "editable canonical checkout; it stopped before initial evaluation, "
                "checkpoint callback, or update. Retry added only the patched checkout "
                "to PYTHONPATH."
            ),
        },
        "interpretation": (
            "This passes or rejects restore/update/export compatibility only. Reward is "
            "not policy-selection evidence and no robot clearance follows."
        ),
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    lines = [
        "# Ground-Up Hard-Vector Continuation CPU Smoke Result",
        "",
        f"status: `{status}`",
        "",
        f"failed checks: `{', '.join(failed) if failed else 'none'}`",
        "",
        f"source-to-step-zero max error: `{checkpoints['max_source_to_step_zero_error']}`",
        f"changed policy leaves: `{checkpoints['changed_policy_leaf_count']}` / "
        f"`{checkpoints['policy_leaf_count']}`",
        f"final ONNX max chained bound excess: `{final_onnx['max_bound_excess']}`",
        "",
        "The first invocation imported the wrong editable checkout and stopped before "
        "evaluation, checkpointing, or update. The isolated retry changed only "
        "`PYTHONPATH` and used the exact preregistered recipe.",
        "",
        payload["interpretation"],
        "",
    ]
    args.output_md.write_text("\n".join(lines))
    print(json.dumps({"status": status, "failed": failed}, sort_keys=True))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
