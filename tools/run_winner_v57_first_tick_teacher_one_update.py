#!/usr/bin/env python3
"""Run exactly one isolated Winner-v57 first-tick Adam update on CPU."""

from __future__ import annotations

import argparse
from collections.abc import Mapping
import hashlib
import json
import math
import os
from pathlib import Path
import sys
from typing import Any

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
PATCHES = ROOT / "patches"
ANALYSIS = ROOT / "outputs/analysis"
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(PATCHES))

CONTRACT = ANALYSIS / "winner_v57_first_tick_teacher_one_update_contract.json"
V56_RESULT = ANALYSIS / "winner_v56_first_tick_teacher_gradient_result.json"
V42_RESULT = ANALYSIS / "winner_v42_static_target_teacher_table_result.json"
FULL_TRAINING_PREREGISTRATION = ANALYSIS / "winner_v12_full_calibrator_training_preregistration.json"
DOMAIN = ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def validate_contract(value: Mapping[str, Any]) -> None:
    if (
        value.get("schema_version")
        != "winner_v57.first_tick_teacher_one_update_contract.v1"
        or value.get("status")
        != "PREREGISTERED_WINNER_V57_FIRST_TICK_TEACHER_ONE_UPDATE_CPU_PROOF"
        or value.get("decision") != "AUTHORIZE_EXACTLY_ONE_ISOLATED_ADAM_UPDATE_ONLY"
        or value.get("source", {}).get("optimizer_count") != 453
        or value.get("objective", {}).get("result_optimizer_count") != 454
        or value.get("objective", {}).get("scale") != 136.35153198242188
        or value.get("execution_now", {}).get("optimizer_updates") != 0
        or value.get("authority", {}).get("training_authorized") is not True
        or value.get("authority", {}).get("continuation_training_authorized") is not False
    ):
        raise ValueError("Winner-v57 contract identity changed")
    sources = value.get("sources")
    if not isinstance(sources, Mapping) or not sources:
        raise ValueError("Winner-v57 source manifest is absent")
    for name, item in sources.items():
        if (
            set(item) != {"hash_mode", "path", "sha256"}
            or item["hash_mode"] != "lf"
            or lf_sha256(ROOT / item["path"]) != item["sha256"]
        ):
            raise ValueError(f"Winner-v57 source changed: {name}")
    if canonical_sha256(sources) != value.get("source_manifest_sha256"):
        raise ValueError("Winner-v57 source manifest changed")


def finite_tree(value: Any) -> bool:
    if isinstance(value, Mapping):
        return all(finite_tree(item) for item in value.values())
    if isinstance(value, (list, tuple)):
        return all(finite_tree(item) for item in value)
    if isinstance(value, (float, np.floating)):
        return math.isfinite(float(value))
    return True


def tree_equal(left: Mapping[str, Any], right: Mapping[str, Any]) -> bool:
    return set(left) == set(right) and all(
        np.array_equal(np.asarray(left[key]), np.asarray(right[key])) for key in left
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--training-work-root", type=Path, required=True)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--canonical-fit", type=Path, required=True)
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--markdown", type=Path)
    parser.add_argument("--offline-cpu-only", action="store_true")
    parser.add_argument("--one-update-authorized", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if not args.offline_cpu_only or not args.one_update_authorized:
        raise PermissionError(
            "Winner-v57 requires --offline-cpu-only --one-update-authorized"
        )
    if args.work_root.exists() or args.output.exists():
        raise FileExistsError("refusing to overwrite Winner-v57 evidence")
    markdown = args.markdown or args.output.with_suffix(".md")
    if markdown.exists():
        raise FileExistsError(f"refusing to overwrite Winner-v57 summary: {markdown}")

    import jax
    import jax.numpy as jnp
    import mujoco
    import onnx
    import run_winner_v54_residual_teacher_causal as v54
    import winner_v12_calibrator_training as training
    import winner_v12_decomposed_backend_networks as networks
    import winner_v21_predictor_preserving_joint_support as v21
    import winner_v22_normalized_predictor_v2 as v22v2
    import winner_v43_static_target_teacher as v43
    import winner_v56_first_tick_teacher_mapping as v56

    if jax.default_backend() != "cpu" or any(
        device.platform != "cpu" for device in jax.devices()
    ):
        raise ValueError("Winner-v57 requires CPU-only JAX")
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    validate_contract(contract)
    v56_result = json.loads(V56_RESULT.read_text(encoding="utf-8"))
    if sha256(V56_RESULT) != contract["source"]["v56_result_sha256"]:
        raise ValueError("Winner-v57 V56 source changed")
    smoke, gate, v53 = v54.configure_v53_modules()
    calibrator_design = gate.load_calibrator_design(
        json.loads(FULL_TRAINING_PREREGISTRATION.read_text(encoding="utf-8"))
    )
    matrix = json.loads(DOMAIN.read_text(encoding="utf-8"))["evaluation_matrix"]
    configurations = (
        matrix["fixed_anchors"] + matrix["discovery_samples"] + matrix["heldout_samples"]
    )
    by_id = {row["id"]: row for row in configurations}
    table = v43.load_teacher_table(
        json.loads(V42_RESULT.read_text(encoding="utf-8"))
    )
    scene = args.playground_root / smoke.SCENE_RELATIVE
    if not scene.is_file():
        raise FileNotFoundError(scene)
    if smoke.git_output(args.playground_root, "rev-parse", "HEAD") != smoke.CONTROL_COMMIT:
        raise ValueError("Winner-v57 Playground commit changed")
    smoke.validate_playground_tree(args.playground_root)
    if smoke.sha256(args.canonical_fit) != smoke.P30_FIT_LF_SHA256:
        raise ValueError("Winner-v57 canonical fit changed")
    observer_type = smoke.load_runtime_observer(args.canonical_fit)
    checkpoint_path, graph_path = v53.checkpoint_paths(args.training_work_root, "final")
    if (
        sha256(checkpoint_path) != contract["source"]["snapshot_sha256"]
        or sha256(graph_path) != contract["source"]["onnx_sha256"]
    ):
        raise ValueError("Winner-v57 source artifacts changed")
    source = v22v2.load_snapshot(checkpoint_path)
    if int(np.asarray(source["optimizer"]["count"])) != 453:
        raise ValueError("Winner-v57 source optimizer count changed")

    identifiers = v56_result["objective"]["identifiers"]
    training_ids = list(dict.fromkeys(row["configuration_id"] for row in identifiers))
    plants = list(dict.fromkeys(row["plant"] for row in identifiers))
    observations = []
    targets = []
    variants = []
    rebuilt_identifiers = []
    zero = np.zeros((14,), dtype=np.float32)
    for configuration_id in training_ids:
        target = smoke.bounded_action_numpy(
            np.asarray(table[configuration_id], dtype=np.float32), zero
        )
        for plant in plants:
            episode = smoke.Episode(
                mujoco,
                scene,
                by_id[configuration_id],
                plant,
                calibrator_design,
                observer_type,
                args.canonical_fit,
            )
            raw = gate.ObservationTransport(None, None).observe(episode.observation())
            quantized = gate.native_quantize_observation(raw)
            for variant, observation in enumerate((raw, quantized)):
                observations.append(observation)
                targets.append(target)
                variants.append(variant)
                rebuilt_identifiers.append(
                    {
                        "configuration_id": configuration_id,
                        "plant": plant,
                        "variant": "raw" if variant == 0 else "native_quantized",
                    }
                )
    if rebuilt_identifiers != identifiers:
        raise ValueError("Winner-v57 reset population changed")
    batch = {
        "observations": jnp.asarray(np.asarray(observations, dtype=np.float32)),
        "targets": jnp.asarray(np.asarray(targets, dtype=np.float32)),
        "variant": jnp.asarray(np.asarray(variants, dtype=np.int32)),
    }
    before = v21.joint_trainable_parameters(source["parameters"])
    source_parameters_copy = {
        key: np.asarray(value).copy() for key, value in source["parameters"].items()
    }
    source_optimizer_copy = {
        "count": np.asarray(source["optimizer"]["count"]).copy(),
        "m": {key: np.asarray(value).copy() for key, value in source["optimizer"]["m"].items()},
        "v": {key: np.asarray(value).copy() for key, value in source["optimizer"]["v"].items()},
    }

    def loss_fn(values: Mapping[str, Any]):
        return v56.first_tick_teacher_loss(values, batch)

    (loss_before, metrics_before), unit_gradients = jax.value_and_grad(
        loss_fn, has_aux=True
    )(before)
    gradients = jax.tree_util.tree_map(
        lambda value: jnp.asarray(v56.RESET_TEACHER_SCALE) * value,
        unit_gradients,
    )
    gradient_max = {
        key: float(np.max(np.abs(np.asarray(value))))
        for key, value in sorted(gradients.items())
    }
    if (
        float(loss_before) != v56_result["objective"]["loss"]
        or gradient_max != v56_result["objective"]["scaled_gradient_max_abs"]
    ):
        raise ValueError("Winner-v57 V56 recomputation changed")
    after, optimizer_after = training.adam_step(
        before,
        gradients,
        source["optimizer"],
        learning_rate=training.STAGE2_LEARNING_RATE,
        beta1=training.ADAM_BETA1,
        beta2=training.ADAM_BETA2,
        epsilon=training.ADAM_EPSILON,
    )
    after = training.clamp_stage2_parameters(after)
    parameters_after = v21.merge_joint_trainable(source["parameters"], after)
    loss_after, metrics_after = v56.first_tick_teacher_loss(after, batch)
    leaf_delta = {
        key: float(np.max(np.abs(np.asarray(after[key]) - np.asarray(before[key]))))
        for key in sorted(before)
    }
    source_unchanged = (
        all(
            np.array_equal(source_parameters_copy[key], np.asarray(source["parameters"][key]))
            for key in source_parameters_copy
        )
        and np.array_equal(source_optimizer_copy["count"], source["optimizer"]["count"])
        and tree_equal(source_optimizer_copy["m"], source["optimizer"]["m"])
        and tree_equal(source_optimizer_copy["v"], source["optimizer"]["v"])
    )
    if not training.finite_tree(
        {
            "parameters": parameters_after,
            "optimizer": optimizer_after,
            "loss_before": loss_before,
            "loss_after": loss_after,
            "metrics_before": metrics_before,
            "metrics_after": metrics_after,
        }
    ):
        raise FloatingPointError("Winner-v57 update is nonfinite")

    args.work_root.mkdir(parents=True, exist_ok=False)
    graph = args.work_root / "winner_v57_first_tick_teacher_update_454.onnx"
    networks.export_calibrator_onnx(
        training.deployable_parameters(parameters_after), graph
    )
    graph_contract = smoke.onnx_contract(
        graph, parameters_after, np.asarray(observations, dtype=np.float32)
    )
    model = onnx.load(graph)
    inventory = "\n".join(
        [
            *(value.name for value in model.graph.initializer),
            *(node.name for node in model.graph.node),
            *(name for node in model.graph.node for name in node.input),
            *(name for node in model.graph.node for name in node.output),
        ]
    ).lower()
    forbidden = [
        token
        for token in (
            "teacher",
            "static_target",
            "configuration_table",
            "configuration_id",
            "privileged",
            "heldout",
        )
        if token in inventory
    ]
    snapshot_path = args.work_root / "winner_v57_first_tick_teacher_update_454.npz"
    snapshot_receipt = v22v2.save_snapshot(
        snapshot_path,
        parameters_after,
        optimizer_after,
        {
            "stage": "first_tick_teacher_joint_stage2",
            "completed_updates": 454,
            "source_completed_updates": 453,
            "source_snapshot_sha256": contract["source"]["snapshot_sha256"],
            "objective": contract["objective"],
            "root_seed": 120120,
            "learning_rate": float(training.STAGE2_LEARNING_RATE),
            "first_tick_teacher_scale": float(v56.RESET_TEACHER_SCALE),
            "formal_support_cells": 0,
            "continuation_training_updates": 0,
            "robot_or_rdk_access": 0,
        },
        source["target_mean"],
        source["target_std"],
    )
    loaded = v22v2.load_snapshot(snapshot_path)
    snapshot_exact = bool(
        tree_equal(parameters_after, loaded["parameters"])
        and np.array_equal(optimizer_after["count"], loaded["optimizer"]["count"])
        and tree_equal(optimizer_after["m"], loaded["optimizer"]["m"])
        and tree_equal(optimizer_after["v"], loaded["optimizer"]["v"])
        and np.array_equal(source["target_mean"], loaded["target_mean"])
        and np.array_equal(source["target_std"], loaded["target_std"])
        and loaded["metadata"].get("stage") == "first_tick_teacher_joint_stage2"
        and loaded["metadata"].get("completed_updates") == 454
    )
    checks = {
        "cpu_only_environment_exact": True,
        "source_snapshot_onnx_optimizer_exact": True,
        "v56_loss_metrics_and_gradient_recompute_exact": float(loss_before)
        == v56_result["objective"]["loss"]
        and gradient_max == v56_result["objective"]["scaled_gradient_max_abs"],
        "source_state_unchanged_before_update": source_unchanged,
        "exactly_one_optimizer_update_453_to_454": int(
            np.asarray(optimizer_after["count"])
        )
        == 454,
        "same_batch_total_loss_strictly_decreases": float(loss_after)
        < float(loss_before),
        "same_batch_raw_loss_strictly_decreases": float(metrics_after["raw_reset_mse"])
        < float(metrics_before["raw_reset_mse"]),
        "same_batch_quantized_loss_strictly_decreases": float(
            metrics_after["quantized_reset_mse"]
        )
        < float(metrics_before["quantized_reset_mse"]),
        "all_12_trainable_leaves_changed": set(leaf_delta)
        == set(v21.JOINT_TRAINABLE_KEYS)
        and all(value > 0.0 for value in leaf_delta.values()),
        "all_parameters_optimizer_metrics_finite": True,
        "snapshot_readback_exact": snapshot_exact,
        "onnx_abi_exact": graph_contract["abi_exact"],
        "onnx_training_only_tensors_absent": graph_contract[
            "training_only_tensors_absent"
        ],
        "onnx_teacher_privileged_tokens_absent": not forbidden,
        "onnx_jax_chain_at_most_1e_7": graph_contract["jax_onnx_at_most_1e_7"],
        "onnx_previous_action_chain_exact": graph_contract[
            "previous_action_out_equals_action_bit_exact"
        ],
        "formal_support_continuation_robot_zero": True,
    }
    checks = {key: bool(value) for key, value in checks.items()}
    failed = sorted(key for key, value in checks.items() if not value)
    result = {
        "schema_version": "winner_v57.first_tick_teacher_one_update_result.v1",
        "status": (
            "PASS_WINNER_V57_FIRST_TICK_TEACHER_ONE_UPDATE_CPU_PROOF"
            if not failed
            else "HOLD_WINNER_V57_FIRST_TICK_TEACHER_ONE_UPDATE_CPU_PROOF"
        ),
        "decision": (
            "AUTHORIZE_INTEGRATED_FIRST_TICK_TEACHER_CONTINUATION_PREREGISTRATION_ONLY"
            if not failed
            else "DO_NOT_TRAIN_FIRST_TICK_TEACHER_OBJECTIVE"
        ),
        "checks": checks,
        "failed_checks": failed,
        "source": contract["source"],
        "objective": contract["objective"],
        "optimization": {
            "optimizer_count_before": 453,
            "optimizer_count_after": int(np.asarray(optimizer_after["count"])),
            "loss_before": float(loss_before),
            "loss_after": float(loss_after),
            "loss_delta": float(loss_after) - float(loss_before),
            "raw_loss_before": float(metrics_before["raw_reset_mse"]),
            "raw_loss_after": float(metrics_after["raw_reset_mse"]),
            "quantized_loss_before": float(metrics_before["quantized_reset_mse"]),
            "quantized_loss_after": float(metrics_after["quantized_reset_mse"]),
            "pitch_rms_before": float(metrics_before["pitch_rms"]),
            "pitch_rms_after": float(metrics_after["pitch_rms"]),
            "nonpitch_rms_before": float(metrics_before["nonpitch_rms"]),
            "nonpitch_rms_after": float(metrics_after["nonpitch_rms"]),
            "scaled_gradient_max_abs": gradient_max,
            "leaf_max_abs_delta": leaf_delta,
            "source_state_unchanged_before_update": source_unchanged,
            "snapshot_readback_exact": snapshot_exact,
        },
        "snapshot": snapshot_receipt,
        "graph": {
            "path": str(graph),
            "sha256": sha256(graph),
            "bytes": graph.stat().st_size,
            "contract": graph_contract,
            "forbidden_tokens_present": forbidden,
        },
        "execution": {
            "reset_rows": 44,
            "simulator_steps": 0,
            "optimizer_updates": 1,
            "continuation_updates": 0,
            "formal_support_cells": 0,
            "candidate_graph_exports": 1,
            "robot_or_rdk_access": 0,
        },
        "environment": {
            "jax_backend": jax.default_backend(),
            "jax_devices": [device.platform for device in jax.devices()],
            "mujoco_version": mujoco.__version__,
            "numpy_version": np.__version__,
        },
        "sources": contract["sources"],
        "source_manifest_sha256": contract["source_manifest_sha256"],
        "authority": {
            "robot_clearance": False,
            "continuation_training_executed": False,
            "formal_support_gate_executed": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "pass_authorizes_only": "a separate integrated bounded continuation preregistration",
        },
    }
    if not finite_tree(result):
        raise FloatingPointError("Winner-v57 result contains nonfinite values")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    markdown.write_text(
        "\n".join(
            [
                "# Winner-v57 first-tick teacher one-update result",
                "",
                f"- Status: `{result['status']}`",
                f"- Decision: `{result['decision']}`",
                f"- Optimizer count: `453 -> {result['optimization']['optimizer_count_after']}`",
                f"- Loss: `{float(loss_before)} -> {float(loss_after)}`",
                f"- Pitch RMS: `{float(metrics_before['pitch_rms'])} -> {float(metrics_after['pitch_rms'])}`",
                f"- Snapshot SHA-256: `{snapshot_receipt['sha256']}`",
                f"- ONNX SHA-256: `{result['graph']['sha256']}`",
                "- Continuation / support / robot: `0 / 0 / 0`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(result["status"])
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
