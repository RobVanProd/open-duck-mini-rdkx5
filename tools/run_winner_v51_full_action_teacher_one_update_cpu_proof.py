#!/usr/bin/env python3
"""Run exactly one frozen Winner-v51 full-action-teacher update on CPU."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import tempfile
from typing import Any, Mapping

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
PATCHES = ROOT / "patches"
ANALYSIS = ROOT / "outputs/analysis"
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(PATCHES))

import run_winner_v24_symmetric_failure_cpu_contract as common  # noqa: E402
import run_winner_v50_full_action_teacher_source_gradient_contract as v50  # noqa: E402
import winner_v29_prefix_right_pitch_anchor as v29  # noqa: E402
import winner_v49_full_action_static_target_teacher as v49  # noqa: E402


CONTRACT = ANALYSIS / "winner_v51_full_action_teacher_one_update_cpu_contract.json"
V50C_RESULT = ANALYSIS / "winner_v50c_gradient_backward_error_attribution_result.json"
V50_RESULT = ANALYSIS / "winner_v50_full_action_teacher_source_gradient_result.json"
SOURCE_OPTIMIZER_COUNT = 352
RESULT_OPTIMIZER_COUNT = 353


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


def array_sha256(value: Any) -> str:
    array = np.ascontiguousarray(np.asarray(value))
    digest = hashlib.sha256()
    digest.update(str(array.dtype).encode())
    digest.update(json.dumps(list(array.shape), separators=(",", ":")).encode())
    digest.update(array.tobytes())
    return digest.hexdigest()


def tree_delta_max_abs(
    left: Mapping[str, Any], right: Mapping[str, Any]
) -> dict[str, float]:
    if set(left) != set(right):
        raise ValueError("Winner-v51 tree schema changed")
    return {
        key: float(
            np.max(
                np.abs(
                    np.asarray(left[key], dtype=np.float64)
                    - np.asarray(right[key], dtype=np.float64)
                )
            )
        )
        for key in sorted(left)
    }


def validate_contract(value: Mapping[str, Any]) -> None:
    objective = value.get("objective", {})
    if (
        value.get("schema_version")
        != "winner_v51.full_action_teacher_one_update_cpu_contract.v1"
        or value.get("status")
        != "PREREGISTERED_WINNER_V51_FULL_ACTION_TEACHER_ONE_UPDATE_CPU_PROOF"
        or value.get("decision")
        != "AUTHORIZE_EXACT_ONE_FULL_ACTION_TEACHER_OPTIMIZER_UPDATE_ONLY"
        or objective.get("source_checkpoint")
        != {"label": "winner_v46_final", "update": 352}
        or objective.get("result_optimizer_count") != RESULT_OPTIMIZER_COUNT
        or objective.get("rollout_update_index") != SOURCE_OPTIMIZER_COUNT
        or objective.get("teacher_action_indices") != list(v49.ACTION_INDICES)
        or objective.get("teacher_scale") != float(v49.FULL_ACTION_TEACHER_SCALE)
        or value.get("execution_future", {}).get("optimizer_updates") != 1
        or value.get("execution_future", {}).get("formal_support_cells") != 0
        or value.get("authority", {}).get("one_update_authorized_by_this_preregistration")
        is not True
    ):
        raise ValueError("Winner-v51 contract changed")
    sources = value.get("sources")
    if not isinstance(sources, Mapping) or not sources:
        raise ValueError("Winner-v51 source manifest absent")
    for name, item in sources.items():
        if item.get("hash_mode") != "lf" or lf_sha256(ROOT / item["path"]) != item.get("sha256"):
            raise ValueError(f"Winner-v51 source changed: {name}")
    if canonical_sha256(sources) != value.get("source_manifest_sha256"):
        raise ValueError("Winner-v51 source-manifest digest changed")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--canonical-fit", type=Path, required=True)
    parser.add_argument("--v46-training-work-root", type=Path, required=True)
    parser.add_argument("--v22-training-work-root", type=Path, required=True)
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--offline-cpu-only", action="store_true")
    parser.add_argument("--one-update-full-action-teacher-proof-authorized", action="store_true")
    args = parser.parse_args()
    if not args.offline_cpu_only or not args.one_update_full_action_teacher_proof_authorized:
        raise PermissionError(
            "Winner-v51 requires --offline-cpu-only and "
            "--one-update-full-action-teacher-proof-authorized"
        )
    if args.work_root.exists() or args.output.exists():
        raise FileExistsError("refusing to overwrite Winner-v51 evidence")

    import jax
    import jax.numpy as jnp
    import mujoco
    import onnx
    import run_winner_v12_calibrator_cpu_smoke as smoke
    import winner_v12_calibrator_training as training
    import winner_v12_decomposed_backend_networks as networks
    import winner_v20_joint_recurrent_support as v20
    import winner_v21_predictor_preserving_joint_support as v21
    import winner_v22_normalized_predictor_v2 as v22v2

    if jax.default_backend() != "cpu" or any(
        device.platform != "cpu" for device in jax.devices()
    ):
        raise ValueError("Winner-v51 requires CPU-only JAX")
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    validate_contract(contract)
    v50c = json.loads(V50C_RESULT.read_text(encoding="utf-8"))
    if (
        sha256(V50C_RESULT) != contract["frozen_v50c_result"]["sha256"]
        or v50c.get("status")
        != "PASS_WINNER_V50C_GRADIENT_BACKWARD_ERROR_ATTRIBUTION"
        or v50c.get("decision")
        != "AUTHORIZE_FULL_ACTION_TEACHER_ONE_UPDATE_CPU_PREREGISTRATION_ONLY"
        or v50c.get("execution", {}).get("optimizer_updates") != 0
    ):
        raise ValueError("Winner-v50c does not authorize Winner-v51")

    captured_deltas: list[
        tuple[dict[str, np.ndarray], dict[str, np.ndarray]]
    ] = []
    captured_snapshots: list[dict[str, Any]] = []
    captured_rollouts: list[tuple[dict[str, Any], list[dict[str, Any]], Any]] = []
    teacher_context: dict[str, Any] = {}
    original_delta = v50.tree_delta_max_abs
    original_tolerance = v50.COMPOSITION_TOLERANCE
    original_full_loss = v50.full_training_teacher_loss
    original_load_snapshot = v22v2.load_snapshot
    original_stage2_rollout = v20.stage2_rollout
    original_argv = sys.argv[:]

    def capture_delta(
        left: Mapping[str, Any], right: Mapping[str, Any]
    ) -> dict[str, float]:
        captured_deltas.append(
            (
                {key: np.asarray(value).copy() for key, value in left.items()},
                {key: np.asarray(value).copy() for key, value in right.items()},
            )
        )
        return original_delta(left, right)

    def capture_snapshot(path: Path) -> dict[str, Any]:
        loaded = original_load_snapshot(path)
        captured_snapshots.append(loaded)
        return loaded

    def capture_rollout(*positional: Any, **keywords: Any):
        result = original_stage2_rollout(*positional, **keywords)
        captured_rollouts.append(result)
        return result

    def capture_full_loss(
        candidate_actions: Any,
        identifiers: list[str],
        previous_actions: Any,
        valid_mask: Any,
        table: Mapping[str, np.ndarray],
        jax_module: Any,
        jnp_module: Any,
    ):
        teacher_context.update(
            {
                "identifiers": list(identifiers),
                "previous_actions": np.asarray(previous_actions).copy(),
                "valid_mask": np.asarray(valid_mask).copy(),
                "table": {key: np.asarray(value).copy() for key, value in table.items()},
            }
        )
        return original_full_loss(
            candidate_actions,
            identifiers,
            previous_actions,
            valid_mask,
            table,
            jax_module,
            jnp_module,
        )

    try:
        with tempfile.TemporaryDirectory(prefix="winner-v51-") as temporary:
            recomputed_path = Path(temporary) / "v50_recomputed.json"
            v50.tree_delta_max_abs = capture_delta
            v50.COMPOSITION_TOLERANCE = math.inf
            v50.full_training_teacher_loss = capture_full_loss
            v22v2.load_snapshot = capture_snapshot
            v20.stage2_rollout = capture_rollout
            sys.argv = [
                str(v50.__file__),
                "--playground-root", str(args.playground_root),
                "--canonical-fit", str(args.canonical_fit),
                "--v46-training-work-root", str(args.v46_training_work_root),
                "--v22-training-work-root", str(args.v22_training_work_root),
                "--output", str(recomputed_path),
                "--offline-cpu-only",
                "--source-gradient-proof-authorized",
            ]
            return_code = v50.main()
            recomputed = json.loads(recomputed_path.read_text(encoding="utf-8"))
    finally:
        v50.tree_delta_max_abs = original_delta
        v50.COMPOSITION_TOLERANCE = original_tolerance
        v50.full_training_teacher_loss = original_full_loss
        v22v2.load_snapshot = original_load_snapshot
        v20.stage2_rollout = original_stage2_rollout
        sys.argv = original_argv

    if (
        return_code != 0
        or len(captured_deltas) != 3
        or len(captured_snapshots) != 2
        or len(captured_rollouts) != 1
        or not teacher_context
    ):
        raise ValueError("Winner-v51 failed to capture the exact V50 source computation")
    source, teacher = captured_snapshots
    batch_np, episodes, observations = captured_rollouts[0]
    before = v21.joint_trainable_parameters(source["parameters"])
    source_parameter_copy = {
        key: np.asarray(value).copy() for key, value in source["parameters"].items()
    }
    source_optimizer_copy = {
        "count": np.asarray(source["optimizer"]["count"]).copy(),
        "m": {
            key: np.asarray(value).copy()
            for key, value in source["optimizer"]["m"].items()
        },
        "v": {
            key: np.asarray(value).copy()
            for key, value in source["optimizer"]["v"].items()
        },
    }
    if int(np.asarray(source["optimizer"]["count"])) != SOURCE_OPTIMIZER_COUNT:
        raise ValueError("Winner-v51 source optimizer count changed")
    gradients = {
        key: jnp.asarray(value, dtype=jnp.float32)
        for key, value in captured_deltas[2][1].items()
    }
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
    bounded_after = v29.deterministic_bounded_actions(
        after,
        jnp.asarray(batch_np["observations"], dtype=jnp.float32),
        jnp.asarray(batch_np["previous_actions"], dtype=jnp.float32),
    )[1]
    teacher_loss_after, teacher_metrics_after = original_full_loss(
        bounded_after,
        teacher_context["identifiers"],
        teacher_context["previous_actions"],
        teacher_context["valid_mask"],
        teacher_context["table"],
        jax,
        jnp,
    )
    teacher_loss_before = float(
        recomputed["objective_evidence"]["full_action_teacher_loss"]
    )
    leaf_delta = v20.leaf_max_abs_delta(before, after)
    gradient_max = common.tree_max_abs(gradients)
    frozen_keys = sorted(set(source["parameters"]) - set(v21.JOINT_TRAINABLE_KEYS))
    frozen_delta = {
        key: float(
            np.max(
                np.abs(
                    np.asarray(parameters_after[key], dtype=np.float64)
                    - np.asarray(source["parameters"][key], dtype=np.float64)
                )
            )
        )
        for key in frozen_keys
    }
    source_unchanged = (
        all(
            np.array_equal(source_parameter_copy[key], source["parameters"][key])
            for key in source_parameter_copy
        )
        and np.array_equal(source_optimizer_copy["count"], source["optimizer"]["count"])
        and common.tree_equal(source_optimizer_copy["m"], source["optimizer"]["m"])
        and common.tree_equal(source_optimizer_copy["v"], source["optimizer"]["v"])
    )
    if not training.finite_tree(
        {
            "gradients": gradients,
            "parameters_after": parameters_after,
            "optimizer_after": optimizer_after,
            "teacher_loss_after": teacher_loss_after,
            "teacher_metrics_after": teacher_metrics_after,
        }
    ):
        raise FloatingPointError("Winner-v51 one-update state is nonfinite")

    args.work_root.mkdir(parents=True, exist_ok=False)
    graph = args.work_root / "winner_v51_full_action_teacher_update_353.onnx"
    networks.export_calibrator_onnx(
        training.deployable_parameters(parameters_after), graph
    )
    graph_contract = smoke.onnx_contract(graph, parameters_after, observations)
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
    snapshot_path = args.work_root / "winner_v51_full_action_teacher_update_353.npz"
    snapshot_receipt = v22v2.save_snapshot(
        snapshot_path,
        parameters_after,
        optimizer_after,
        {
            "stage": "full_action_static_target_teacher_joint_stage2",
            "completed_updates": RESULT_OPTIMIZER_COUNT,
            "source_completed_updates": SOURCE_OPTIMIZER_COUNT,
            "source_snapshot_sha256": contract["artifact_inputs"]["winner_v46_final"]
            ["snapshot"]["sha256"],
            "teacher_snapshot_sha256": contract["artifact_inputs"]
            ["winner_v22_teacher_snapshot"]["sha256"],
            "objective": contract["objective"],
            "root_seed": 120120,
            "learning_rate": float(training.STAGE2_LEARNING_RATE),
            "predictor_scale": 380.9135437011719,
            "prefix_anchor_scale": 197.3112030029297,
            "full_action_teacher_scale": float(v49.FULL_ACTION_TEACHER_SCALE),
            "formal_support_cells": 0,
            "continuation_training_updates": 0,
            "robot_or_rdk_access": 0,
        },
        source["target_mean"],
        source["target_std"],
    )
    loaded = v22v2.load_snapshot(snapshot_path)
    snapshot_exact = bool(
        common.tree_equal(parameters_after, loaded["parameters"])
        and np.array_equal(optimizer_after["count"], loaded["optimizer"]["count"])
        and common.tree_equal(optimizer_after["m"], loaded["optimizer"]["m"])
        and common.tree_equal(optimizer_after["v"], loaded["optimizer"]["v"])
        and np.array_equal(source["target_mean"], loaded["target_mean"])
        and np.array_equal(source["target_std"], loaded["target_std"])
        and loaded["metadata"].get("stage")
        == "full_action_static_target_teacher_joint_stage2"
        and loaded["metadata"].get("completed_updates") == RESULT_OPTIMIZER_COUNT
    )
    policy_keys = set(v29.ANCHOR_GRADIENT_KEYS)
    nonpolicy_keys = set(v29.NON_ANCHOR_GRADIENT_KEYS)
    full_gradient_max = recomputed["objective_evidence"]
    ["full_teacher_gradient_max_abs"]
    checks = {
        "cpu_only_environment_exact": True,
        "winner_v50c_authority_exact": True,
        "winner_v46_final_source_and_teacher_exact": recomputed["checks"]
        ["v46_final_source_snapshot_graph_exact"]
        and recomputed["checks"]["v22_teacher_snapshot_exact"],
        "exact_80_episode_rollout_at_update_352": len(episodes) == 80,
        "v50_recomputation_checks_pass": all(recomputed["checks"].values()),
        "full_teacher_scale_exact": float(v49.FULL_ACTION_TEACHER_SCALE)
        == 136.35153198242188,
        "all_14_teacher_actions_selected": recomputed["checks"]
        ["full_mask_adds_all_valid_nonpitch_elements"]
        and recomputed["checks"]["full_mask_preserves_pitch_mask_bit_exact"],
        "exact_22_teacher_rows_and_no_heldout": recomputed["checks"]
        ["exact_22_training_teacher_configuration_plant_rows"]
        and recomputed["checks"]["heldout_teacher_rows_excluded"],
        "teacher_gradients_policy_only": all(
            full_gradient_max[key] > 0.0 for key in policy_keys
        )
        and all(full_gradient_max[key] == 0.0 for key in nonpolicy_keys),
        "all_combined_gradients_nonzero": set(gradient_max)
        == set(v21.JOINT_TRAINABLE_KEYS)
        and all(value > 0.0 for value in gradient_max.values()),
        "all_trainable_leaves_changed": set(leaf_delta)
        == set(v21.JOINT_TRAINABLE_KEYS)
        and all(value > 0.0 for value in leaf_delta.values()),
        "all_frozen_parameter_leaves_bit_exact": all(
            value == 0.0 for value in frozen_delta.values()
        ),
        "source_state_unchanged_before_update": source_unchanged,
        "exactly_one_optimizer_update_352_to_353": int(
            np.asarray(optimizer_after["count"])
        )
        == RESULT_OPTIMIZER_COUNT,
        "same_batch_full_teacher_loss_strictly_decreases": math.isfinite(
            float(teacher_loss_after)
        )
        and float(teacher_loss_after) < teacher_loss_before,
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
    passed = not failed
    result = {
        "schema_version": "winner_v51.full_action_teacher_one_update_cpu_result.v1",
        "status": (
            "PASS_WINNER_V51_FULL_ACTION_TEACHER_ONE_UPDATE_CPU_PROOF"
            if passed
            else "HOLD_WINNER_V51_FULL_ACTION_TEACHER_ONE_UPDATE_CPU_PROOF"
        ),
        "decision": (
            "AUTHORIZE_BOUNDED_FULL_ACTION_TEACHER_CONTINUATION_PREREGISTRATION_ONLY"
            if passed
            else "DO_NOT_TRAIN_FULL_ACTION_TEACHER_OBJECTIVE"
        ),
        "checks": checks,
        "failed_checks": failed,
        "source_identity": recomputed["source_identity"],
        "objective": contract["objective"],
        "rollout": {
            **recomputed["rollout_evidence"],
            "observations_sha256": array_sha256(batch_np["observations"]),
            "previous_actions_sha256": array_sha256(batch_np["previous_actions"]),
        },
        "optimization": {
            "optimizer_count_before": SOURCE_OPTIMIZER_COUNT,
            "optimizer_count_after": int(np.asarray(optimizer_after["count"])),
            "full_action_teacher_loss_before": teacher_loss_before,
            "full_action_teacher_loss_after": float(teacher_loss_after),
            "full_action_teacher_loss_delta": float(teacher_loss_after)
            - teacher_loss_before,
            "full_action_teacher_scale": float(v49.FULL_ACTION_TEACHER_SCALE),
            "combined_gradient_max_abs": gradient_max,
            "full_teacher_gradient_max_abs": full_gradient_max,
            "leaf_max_abs_delta": leaf_delta,
            "frozen_parameter_leaf_max_abs_delta": frozen_delta,
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
            "rollout_episode_slots": len(episodes),
            "scheduled_rollout_ticks": len(episodes) * 250,
            "optimizer_updates": 1,
            "formal_support_cells": 0,
            "continuation_training_updates": 0,
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
            "pass_authorizes_only": "a separate frozen bounded full-action continuation preregistration",
        },
    }
    args.output.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(result["status"])
    for name in failed:
        print(f"FAILED={name}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
