#!/usr/bin/env python3
"""Validate the recovered V112 training outputs on an explicit CPU topology."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import struct
from typing import Any

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["HIP_VISIBLE_DEVICES"] = ""
os.environ["ROCR_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"
os.environ["JAX_PLATFORM_NAME"] = "cpu"

from flax.training import orbax_utils
import jax
import numpy as np
import onnx
import onnxruntime as ort
from orbax import checkpoint as ocp
from tensorboardX.proto.event_pb2 import Event


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v112_recovered_training_validation.json"
MARKDOWN = ANALYSIS / "WINNER_V112_RECOVERED_TRAINING_VALIDATION_20260724.md"
EXPECTED = {
    "hosted_result": (
        "5204d2ed83d62edfc0e9f91c04979f860d9d5d218e286ff1b3d1892d7e8b3401"
    ),
    "launch_receipt": (
        "91d01e3f7e652a661f3d8b41402603353edce259631672a8e6172c6455502668"
    ),
    "recovery_manifest": (
        "5f631a31c41aac5a4607de17bc4be9aa7a3709c5bf0b9d594c2997cf78c0297d"
    ),
    "recovery_archive": (
        "2f4734ac2e973669fe204c006543421e34e8c1b3aa829fd9b049c0aebd0a64c5"
    ),
    "source_checkpoint": (
        "70d589520d4280c9e2f276d45a3f12ccc90aa25a0691b5bd462cbde464419bbd"
    ),
}
EXPECTED_STEPS = [0, 1_003_520, 2_007_040]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def directory_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    for child in sorted(item for item in path.rglob("*") if item.is_file()):
        digest.update(child.relative_to(path).as_posix().encode())
        digest.update(b"\0")
        with child.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
    return digest.hexdigest()


def path_name(path: tuple[Any, ...]) -> str:
    return "/".join(
        str(getattr(item, "key", getattr(item, "idx", item)))
        for item in path
    )


def tree_deltas(left: Any, right: Any) -> tuple[bool, dict[str, float]]:
    left_rows, left_structure = jax.tree_util.tree_flatten_with_path(left)
    right_rows, right_structure = jax.tree_util.tree_flatten_with_path(right)
    if left_structure != right_structure:
        return False, {}
    deltas: dict[str, float] = {}
    for (left_path, before), (right_path, after) in zip(
        left_rows, right_rows, strict=True
    ):
        if left_path != right_path:
            return False, {}
        before_array = np.asarray(before)
        after_array = np.asarray(after)
        if before_array.dtype.kind not in "biufc":
            deltas[path_name(left_path)] = (
                0.0
                if np.array_equal(before_array, after_array)
                else float("inf")
            )
        else:
            deltas[path_name(left_path)] = float(
                np.max(np.abs(after_array - before_array))
            )
    return True, deltas


def tree_finite(value: Any) -> bool:
    return all(
        np.asarray(leaf).dtype.kind not in "biufc"
        or np.isfinite(np.asarray(leaf)).all()
        for leaf in jax.tree_util.tree_leaves(value)
    )


def step(path: Path) -> int:
    return int(path.stem.rsplit("_", 1)[1])


def event_scalars(path: Path) -> dict[str, list[dict[str, float | int]]]:
    tags: dict[str, list[dict[str, float | int]]] = {}
    with path.open("rb") as stream:
        while True:
            length_bytes = stream.read(8)
            if not length_bytes:
                break
            if len(length_bytes) != 8:
                raise ValueError("truncated event length")
            length = struct.unpack("<Q", length_bytes)[0]
            stream.read(4)
            payload = stream.read(length)
            stream.read(4)
            event = Event()
            event.ParseFromString(payload)
            if not event.HasField("summary"):
                continue
            for value in event.summary.value:
                tags.setdefault(value.tag, []).append(
                    {"step": int(event.step), "value": float(value.simple_value)}
                )
    return tags


def onnx_contract(path: Path) -> dict[str, Any]:
    model = onnx.load(path)
    inputs = {
        item.name: [
            dim.dim_value for dim in item.type.tensor_type.shape.dim
        ]
        for item in model.graph.input
    }
    outputs = {
        item.name: [
            dim.dim_value for dim in item.type.tensor_type.shape.dim
        ]
        for item in model.graph.output
    }
    expected_inputs = {
        "obs": [1, 115],
        "previous_action": [1, 14],
        "h_in": [1, 64],
    }
    expected_outputs = {
        "continuous_actions": [1, 14],
        "previous_action_out": [1, 14],
        "h_out": [1, 64],
    }
    initializers_finite = all(
        np.isfinite(onnx.numpy_helper.to_array(item)).all()
        for item in model.graph.initializer
    )
    session = ort.InferenceSession(
        path.read_bytes(), providers=["CPUExecutionProvider"]
    )
    previous = np.zeros((1, 14), dtype=np.float32)
    hidden = np.zeros((1, 64), dtype=np.float32)
    chain_finite = True
    for tick in range(256):
        obs = np.linspace(-0.2, 0.2, 115, dtype=np.float32)[None]
        obs += np.float32(tick * 1.0e-5)
        action, previous, hidden = session.run(
            ["continuous_actions", "previous_action_out", "h_out"],
            {"obs": obs, "previous_action": previous, "h_in": hidden},
        )
        chain_finite &= bool(
            np.isfinite(action).all()
            and np.isfinite(previous).all()
            and np.isfinite(hidden).all()
        )
    return {
        "step": step(path),
        "sha256": sha256(path),
        "abi_exact": inputs == expected_inputs and outputs == expected_outputs,
        "initializers_finite": bool(initializers_finite),
        "cpu_provider_exact": session.get_providers()
        == ["CPUExecutionProvider"],
        "chain_256_finite": chain_finite,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--recovery-root", type=Path, required=True)
    parser.add_argument("--extracted-root", type=Path, required=True)
    parser.add_argument("--source-checkpoint", type=Path, required=True)
    args = parser.parse_args()
    if OUTPUT.exists() or MARKDOWN.exists():
        raise FileExistsError("refusing to overwrite V112 validation")
    recovery = args.recovery_root.resolve()
    work = (
        args.extracted_root.resolve()
        / "winner_v112_peak_torque_continuation"
    )
    training = work / "training"
    source = args.source_checkpoint.resolve()
    paths = {
        "hosted_result": recovery / "winner_v112_result.json",
        "launch_receipt": recovery / "winner_v112_launch_receipt.json",
        "recovery_manifest": recovery / "winner_v112_recovery_manifest.json",
        "recovery_archive": recovery / "winner_v112_recovery_artifacts.tar.gz",
    }
    hashes = {name: sha256(path) for name, path in paths.items()}
    source_hash = directory_sha256(source)
    manifest = json.loads(
        paths["recovery_manifest"].read_text(encoding="utf-8")
    )
    hosted = json.loads(paths["hosted_result"].read_text(encoding="utf-8"))
    receipt = json.loads(
        paths["launch_receipt"].read_text(encoding="utf-8")
    )
    checkpoints = sorted(
        (path for path in training.iterdir() if path.is_dir()), key=step
    )
    graphs = sorted(training.glob("*.onnx"), key=step)
    checkpoint_steps = [step(path) for path in checkpoints]
    onnx_steps = [step(path) for path in graphs]
    checkpoint_hashes = {
        step(path): directory_sha256(path) for path in checkpoints
    }
    graph_rows = [onnx_contract(path) for path in graphs]
    checkpointer = ocp.PyTreeCheckpointer()
    template = checkpointer.restore(str(source))
    restore_args = orbax_utils.restore_args_from_target(template)
    trees = [
        checkpointer.restore(
            str(path), item=template, restore_args=restore_args
        )
        for path in checkpoints
    ]
    initial_structure, initial_deltas = tree_deltas(template, trees[0])
    trained_rows = []
    for path, tree in zip(checkpoints[1:], trees[1:], strict=True):
        structure, deltas = tree_deltas(trees[0], tree)
        policy_deltas = {
            name: value
            for name, value in deltas.items()
            if name.startswith("1/params/")
        }
        trained_rows.append(
            {
                "step": step(path),
                "structure_exact": structure,
                "tree_finite": tree_finite(tree),
                "policy_leaf_deltas": policy_deltas,
                "every_policy_leaf_updated": bool(policy_deltas)
                and all(value > 0.0 for value in policy_deltas.values()),
            }
        )
    event_file = next(training.glob("events.out.tfevents*"))
    scalars = event_scalars(event_file)
    metric_tags = (
        "eval/episode_cost/peak_torque_exceedance",
        "eval/episode_cost/tracking_tail_exceedance",
        "eval/episode_reward",
        "eval/avg_episode_length",
    )
    metric_evidence = {tag: scalars.get(tag, []) for tag in metric_tags}
    metric_steps_exact = all(
        [row["step"] for row in rows] == EXPECTED_STEPS
        for rows in metric_evidence.values()
    )
    metric_values_finite = all(
        math.isfinite(row["value"])
        for rows in metric_evidence.values()
        for row in rows
    )
    manifest_checkpoint_hashes = {
        int(row["step"]): row["directory_sha256"]
        for row in manifest["checkpoints"]
    }
    manifest_onnx_hashes = {
        int(row["step"]): row["sha256"] for row in manifest["onnx"]
    }
    observed_onnx_hashes = {
        row["step"]: row["sha256"] for row in graph_rows
    }
    checks = {
        "recovery_input_hashes_exact": hashes
        == {name: EXPECTED[name] for name in hashes},
        "source_checkpoint_hash_exact": (
            source_hash == EXPECTED["source_checkpoint"]
        ),
        "hosted_hold_is_post_training_inspection_only": (
            hosted.get("status")
            == "HOLD_WINNER_V112_PEAK_TORQUE_HOSTED_CONTINUATION"
            and "sharding passed to deserialization"
            in hosted.get("error", "")
            and receipt.get("returncode") == 1
            and receipt.get("output_archive_exists") is False
        ),
        "recovery_manifest_exact_exports": (
            manifest.get("status")
            == "RECOVERED_WINNER_V112_COMPLETED_TRAINING_OUTPUTS"
            and manifest.get("checkpoint_steps") == EXPECTED_STEPS
            and manifest.get("onnx_steps") == EXPECTED_STEPS
        ),
        "local_exact_exports": checkpoint_steps == EXPECTED_STEPS
        and onnx_steps == EXPECTED_STEPS,
        "checkpoint_hashes_match_recovery_manifest": (
            checkpoint_hashes == manifest_checkpoint_hashes
        ),
        "onnx_hashes_match_recovery_manifest": (
            observed_onnx_hashes == manifest_onnx_hashes
        ),
        "step_zero_source_restore_structure_exact": initial_structure,
        "step_zero_source_parameters_bit_exact": max(
            initial_deltas.values(), default=0.0
        )
        == 0.0,
        "all_checkpoint_trees_finite": tree_finite(trees[0])
        and all(row["tree_finite"] for row in trained_rows),
        "all_postupdate_structures_exact": all(
            row["structure_exact"] for row in trained_rows
        ),
        "every_policy_leaf_updated_at_both_checkpoints": all(
            row["every_policy_leaf_updated"] for row in trained_rows
        ),
        "all_onnx_contracts_pass": all(
            row["abi_exact"]
            and row["initializers_finite"]
            and row["cpu_provider_exact"]
            and row["chain_256_finite"]
            for row in graph_rows
        ),
        "training_metrics_have_exact_export_steps": metric_steps_exact,
        "training_metrics_all_finite": metric_values_finite,
        "cpu_only_validation": all(
            device.platform == "cpu" for device in jax.devices()
        ),
        "no_training_retry_or_resume": (
            manifest.get("training_retry") is False
            and manifest.get("training_resume") is False
        ),
        "formal_behavior_cells_zero": (
            manifest.get("formal_behavior_cells") == 0
        ),
        "robot_or_rdk_access_zero": (
            manifest.get("robot_or_rdk_access") is False
        ),
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    result = {
        "schema_version": "winner_v112.recovered_training_validation.v1",
        "status": (
            "PASS_WINNER_V112_RECOVERED_TRAINING_VALIDATION"
            if not failed
            else "HOLD_WINNER_V112_RECOVERED_TRAINING_VALIDATION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "classification": {
            "hosted_result": hosted["status"],
            "failure_stage": "post_training_artifact_inspection",
            "training_completed": checkpoint_steps == EXPECTED_STEPS,
            "training_retry": False,
            "training_resume": False,
            "correction_method": (
                "read-only CPU topology remap using the exact source tree as "
                "Orbax restore template"
            ),
        },
        "input_hashes": {**hashes, "source_checkpoint": source_hash},
        "checkpoints": [
            {
                "step": step(path),
                "directory_sha256": checkpoint_hashes[step(path)],
            }
            for path in checkpoints
        ],
        "onnx": graph_rows,
        "trained_checkpoints": trained_rows,
        "training_metric_evidence": metric_evidence,
        "authority": {
            "postexport_transform_preregistration_authorized": not failed,
            "behavior_evaluation_authorized": False,
            "checkpoint_selection_authorized": False,
            "gate5_authorized": False,
            "robot_clearance": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    OUTPUT.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner-v112 recovered training validation\n\n"
        f"Status: `{result['status']}`\n\n"
        f"Failed checks: `{failed}`\n\n"
        "The hosted process completed all frozen training exports, then held "
        "only because its post-training GPU-side Orbax readback omitted an "
        "explicit sharding template. The unchanged artifacts were recovered "
        "and validated on CPU using the exact source tree as that template. "
        "No training retry, resume, behavior evaluation, Gate 5, robot, "
        "torque, or motion is authorized here.\n",
        encoding="utf-8",
    )
    print(result["status"])
    print(f"result_sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
