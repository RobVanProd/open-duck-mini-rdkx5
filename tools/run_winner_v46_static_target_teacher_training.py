#!/usr/bin/env python3
"""Run the one frozen 100-update Winner-v46 static-target-teacher CPU arm."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import time
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
import run_winner_v44_static_target_teacher_source_gradient_contract as v44_runner  # noqa: E402
import winner_v29_prefix_right_pitch_anchor as v29  # noqa: E402
import winner_v43_static_target_teacher as v43  # noqa: E402


PREREGISTRATION = ANALYSIS / "winner_v46_static_target_teacher_training_preregistration.json"
V45_RESULT = ANALYSIS / "winner_v45_static_target_teacher_one_update_cpu_result.json"
V42_RESULT = ANALYSIS / "winner_v42_static_target_teacher_table_result.json"
V22_RESULT = ANALYSIS / "winner_v22_normalized_predictor_training_result.json"
FULL_PREREG = ANALYSIS / "winner_v12_full_calibrator_training_preregistration.json"
DOMAIN = ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
UPDATES = 100
SOURCE_COMPLETED_UPDATES = 252
HALF_COMPLETED_UPDATES = 302
FINAL_COMPLETED_UPDATES = 352
PREFIX_ANCHOR_SCALE = np.float32(197.3112030029297)
FROZEN_TEACHER_SCALE = np.float32(58.436370849609375)
TRAINING_TEACHER_IDS = v44_runner.TRAINING_TEACHER_IDS
HELDOUT_TEACHER_IDS = v44_runner.HELDOUT_TEACHER_IDS


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def validate_preregistration(value: Mapping[str, Any]) -> None:
    if (
        value.get("schema_version") != "winner_v46.static_target_teacher_training_preregistration.v1"
        or value.get("status") != "PREREGISTERED_WINNER_V46_STATIC_TARGET_TEACHER_TRAINING"
        or value.get("decision") != "AUTHORIZE_ONE_100_UPDATE_STATIC_TARGET_TEACHER_ARM_ONLY"
        or value.get("execution_now") != {
            "optimizer_updates": 0, "formal_support_cells": 0,
            "locomotion_steps": 0, "robot_or_rdk_access": 0,
        }
    ):
        raise ValueError("Winner-v46 preregistration identity changed")
    frozen = value.get("frozen_training", {})
    if (
        frozen.get("source_completed_updates") != SOURCE_COMPLETED_UPDATES
        or frozen.get("source_optimizer_count") != SOURCE_COMPLETED_UPDATES
        or frozen.get("continuation_optimizer_updates") != UPDATES
        or frozen.get("final_optimizer_count") != FINAL_COMPLETED_UPDATES
        or frozen.get("environments_per_update") != 80
        or frozen.get("ticks_per_environment") != 250
        or frozen.get("scheduled_episode_slots") != 2_000_000
        or frozen.get("training_root_seed") != 120120
        or frozen.get("learning_rate") != 0.0001
        or frozen.get("predictor_scale") != 380.9135437011719
        or frozen.get("prefix_anchor_scale") != float(PREFIX_ANCHOR_SCALE)
        or frozen.get("static_target_teacher_scale") != float(FROZEN_TEACHER_SCALE)
        or frozen.get("persistent_checkpoints")
        != {"half": HALF_COMPLETED_UPDATES, "final": FINAL_COMPLETED_UPDATES}
        or frozen.get("coefficient_or_length_search") is not False
    ):
        raise ValueError("Winner-v46 training constants changed")
    teacher = value.get("objective", {}).get("static_target_teacher", {})
    if (
        teacher.get("configuration_ids") != list(TRAINING_TEACHER_IDS)
        or teacher.get("heldout_ids_excluded") != list(HELDOUT_TEACHER_IDS)
        or teacher.get("configuration_plant_rows") != 22
        or teacher.get("action_indices") != list(v43.PITCH_ACTION_INDICES)
        or teacher.get("scale") != float(FROZEN_TEACHER_SCALE)
        or teacher.get("action_replacement") is not False
        or teacher.get("actor_input_added") is not False
    ):
        raise ValueError("Winner-v46 teacher objective changed")
    sources = value.get("sources")
    if not isinstance(sources, dict) or not sources:
        raise ValueError("Winner-v46 sources are absent")
    for name, item in sources.items():
        if item.get("hash_mode") != "lf" or lf_sha256(ROOT / item["path"]) != item.get("sha256"):
            raise ValueError(f"Winner-v46 source changed: {name}")
    if canonical_sha256(sources) != value.get("source_manifest_sha256"):
        raise ValueError("Winner-v46 source manifest changed")


def validate_artifact(path: Path, receipt: Mapping[str, Any], label: str) -> None:
    if (
        not path.is_file()
        or path.stat().st_size != int(receipt["bytes"])
        or sha256(path) != receipt["sha256"]
    ):
        raise ValueError(f"Winner-v46 {label} artifact changed")


def validate_source_snapshot(snapshot: Mapping[str, Any], v21: Any, source_result: Mapping[str, Any]) -> None:
    if set(snapshot) != {"parameters", "optimizer", "metadata", "target_mean", "target_std"}:
        raise ValueError("Winner-v46 source snapshot state schema changed")
    metadata = snapshot["metadata"]
    if (
        metadata.get("schema_version") != "winner_v21.predictor_preserving_snapshot.v1"
        or metadata.get("stage") != "static_target_teacher_joint_stage2"
        or metadata.get("completed_updates") != SOURCE_COMPLETED_UPDATES
        or metadata.get("source_completed_updates") != 251
        or metadata.get("source_snapshot_sha256")
        != source_result["source_identity"]["source_snapshot"]["sha256"]
        or metadata.get("teacher_snapshot_sha256")
        != source_result["source_identity"]["teacher_snapshot"]["sha256"]
        or metadata.get("root_seed") != 120120
        or metadata.get("learning_rate") != 0.0001
        or metadata.get("predictor_scale") != 380.9135437011719
        or metadata.get("prefix_anchor_scale") != float(PREFIX_ANCHOR_SCALE)
        or metadata.get("static_target_teacher_scale") != float(FROZEN_TEACHER_SCALE)
        or metadata.get("formal_support_cells") != 0
        or metadata.get("continuation_training_updates") != 0
        or metadata.get("robot_or_rdk_access") != 0
        or int(np.asarray(snapshot["optimizer"]["count"])) != SOURCE_COMPLETED_UPDATES
        or set(snapshot["optimizer"]["m"]) != set(v21.JOINT_TRAINABLE_KEYS)
        or set(snapshot["optimizer"]["v"]) != set(v21.JOINT_TRAINABLE_KEYS)
        or set(v21.joint_trainable_parameters(snapshot["parameters"]))
        != set(v21.JOINT_TRAINABLE_KEYS)
    ):
        raise ValueError("Winner-v46 source snapshot metadata changed")
    for name in ("target_mean", "target_std"):
        array = np.asarray(snapshot[name])
        if array.shape != (50,) or array.dtype != np.dtype(np.float32) or not np.all(np.isfinite(array)):
            raise ValueError(f"Winner-v46 source {name} schema changed")
    if np.any(np.asarray(snapshot["target_std"]) <= 0.0):
        raise ValueError("Winner-v46 source target_std is not positive")
    for tree in (snapshot["parameters"], snapshot["optimizer"]["m"], snapshot["optimizer"]["v"]):
        if not all(np.all(np.isfinite(np.asarray(item))) for item in tree.values()):
            raise ValueError("Winner-v46 source snapshot contains nonfinite arrays")


def graph_receipt(
    *, smoke: Any, networks: Any, training: Any, parameters: Mapping[str, Any],
    observations: np.ndarray, path: Path, label: str, completed_updates: int,
) -> dict[str, Any]:
    import onnx

    networks.export_calibrator_onnx(training.deployable_parameters(parameters), path)
    contract = smoke.onnx_contract(path, parameters, observations)
    model = onnx.load(path)
    inventory = "\n".join([
        *(item.name for item in model.graph.initializer),
        *(node.name for node in model.graph.node),
        *(name for node in model.graph.node for name in node.input),
        *(name for node in model.graph.node for name in node.output),
    ]).lower()
    forbidden = [token for token in (
        "teacher", "static_target", "configuration_table", "configuration_id",
        "privileged", "heldout",
    ) if token in inventory]
    if not all(contract[name] for name in (
        "abi_exact", "training_only_tensors_absent", "jax_onnx_at_most_1e_7",
        "previous_action_out_equals_action_bit_exact",
    )) or forbidden:
        raise ValueError(f"Winner-v46 {label} graph contract failed")
    return {
        "label": label, "completed_updates": completed_updates,
        "path": str(path), "sha256": sha256(path), "bytes": path.stat().st_size,
        "contract": contract, "v46_forbidden_tokens_present": forbidden,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--canonical-fit", type=Path, required=True)
    parser.add_argument("--source-snapshot", type=Path, required=True)
    parser.add_argument("--source-graph", type=Path, required=True)
    parser.add_argument("--teacher-snapshot", type=Path, required=True)
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--offline-cpu-only", action="store_true")
    parser.add_argument("--static-target-teacher-training-authorized", action="store_true")
    args = parser.parse_args()
    if not args.offline_cpu_only or not args.static_target_teacher_training_authorized:
        raise PermissionError(
            "Winner-v46 requires --offline-cpu-only --static-target-teacher-training-authorized"
        )
    if args.work_root.exists() or args.output.exists():
        raise FileExistsError("refusing to overwrite Winner-v46 training evidence")

    import jax
    import jax.numpy as jnp
    import mujoco
    import run_winner_v12_calibrator_cpu_smoke as smoke
    import run_winner_v12_full_calibrator_training as full
    import run_winner_v22_normalized_predictor_support_gate as v22_gate
    import winner_v12_calibrator_training as training
    import winner_v12_decomposed_backend_networks as networks
    import winner_v15_pitch_margin_support as v15
    import winner_v20_joint_recurrent_support as v20
    import winner_v21_predictor_preserving_joint_support as v21
    import winner_v22_normalized_predictor as v22
    import winner_v22_normalized_predictor_v2 as v22v2
    import winner_v24_symmetric_support_failure as v24
    import winner_v24_symmetric_support_failure_v2 as v24v2
    import winner_v24_symmetric_support_failure_v3 as v24v3

    if jax.default_backend() != "cpu" or any(device.platform != "cpu" for device in jax.devices()):
        raise ValueError("Winner-v46 requires CPU-only JAX")
    preregistration = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    validate_preregistration(preregistration)
    source_result = json.loads(V45_RESULT.read_text(encoding="utf-8"))
    teacher_result = json.loads(V22_RESULT.read_text(encoding="utf-8"))
    if (
        source_result.get("status") != "PASS_WINNER_V45_STATIC_TARGET_TEACHER_ONE_UPDATE_CPU_PROOF"
        or source_result.get("decision") != "AUTHORIZE_STATIC_TARGET_TEACHER_TRAINING_PREREGISTRATION_ONLY"
        or source_result.get("failed_checks") != []
        or teacher_result.get("status") != "PASS_WINNER_V22_NORMALIZED_PREDICTOR_TRAINING_ARTIFACT"
        or teacher_result.get("failed_checks") != []
    ):
        raise ValueError("Winner-v46 source evidence changed")
    source_receipt = preregistration["source_checkpoint"]["snapshot"]
    source_graph_receipt = preregistration["source_checkpoint"]["graph"]
    teacher_receipt = preregistration["teacher_checkpoint"]["snapshot"]
    validate_artifact(args.source_snapshot, source_receipt, "source snapshot")
    validate_artifact(args.source_graph, source_graph_receipt, "source graph")
    validate_artifact(args.teacher_snapshot, teacher_receipt, "teacher snapshot")

    expected_versions = dict(json.loads(FULL_PREREG.read_text(encoding="utf-8"))["implementation_contract_environment"])
    if expected_versions.pop("platform") != "CPU only" or not smoke.validate_software_versions(
        {"software_versions": expected_versions}
    )["exact"]:
        raise ValueError("Winner-v46 training environment changed")
    if smoke.sha256(args.canonical_fit) != smoke.P30_FIT_LF_SHA256:
        raise ValueError("Winner-v46 P30 fit changed")
    if smoke.git_output(args.playground_root, "rev-parse", "HEAD") != smoke.CONTROL_COMMIT:
        raise ValueError("Winner-v46 Playground source changed")
    smoke.validate_playground_tree(args.playground_root)
    scene = args.playground_root / smoke.SCENE_RELATIVE
    if smoke.sha256(scene) != smoke.SCENE_SHA256:
        raise ValueError("Winner-v46 scene changed")

    restored = v22v2.load_snapshot(args.source_snapshot)
    teacher = v22v2.load_snapshot(args.teacher_snapshot)
    validate_source_snapshot(restored, v21, source_result)
    v22_gate.smoke = smoke
    v22_gate.training = training
    v22_gate.v21 = v21
    v22_gate._validate_snapshot(teacher, expected_stage="normalized_predictor_joint_stage2")
    if (
        teacher["metadata"].get("completed_updates") != 100
        or int(np.asarray(teacher["optimizer"]["count"])) != 100
        or not np.array_equal(restored["target_mean"], teacher["target_mean"])
        or not np.array_equal(restored["target_std"], teacher["target_std"])
    ):
        raise ValueError("Winner-v46 restore boundary changed")
    table = v43.load_teacher_table(json.loads(V42_RESULT.read_text(encoding="utf-8")))
    parameters = restored["parameters"]
    source_trainable = v21.joint_trainable_parameters(parameters)
    frozen_parameter_copy = {
        key: np.asarray(value).copy()
        for key, value in parameters.items() if key not in v21.JOINT_TRAINABLE_KEYS
    }
    teacher_trainable = v21.joint_trainable_parameters(teacher["parameters"])
    teacher_trainable_copy = {key: np.asarray(value).copy() for key, value in teacher_trainable.items()}
    optimizer = restored["optimizer"]
    target_mean = jnp.asarray(restored["target_mean"], dtype=jnp.float32)
    target_std = jnp.asarray(restored["target_std"], dtype=jnp.float32)
    population = full.training_population(
        json.loads(FULL_PREREG.read_text(encoding="utf-8")),
        json.loads(DOMAIN.read_text(encoding="utf-8")),
    )
    identifiers = [str(row["id"]) for row in population]
    if (
        len(population) != 80
        or any(name in identifiers for name in HELDOUT_TEACHER_IDS)
        or any(identifiers.count(name) != 2 for name in TRAINING_TEACHER_IDS)
    ):
        raise ValueError("Winner-v46 training population or teacher split changed")
    design = json.loads(smoke.CALIBRATOR_PREREG.read_text(encoding="utf-8"))
    observer_type = smoke.load_runtime_observer(args.canonical_fit)
    metrics: list[dict[str, Any]] = []
    snapshots: list[dict[str, Any]] = []
    checkpoints: list[dict[str, Any]] = []
    sampled_total = valid_total = 0
    start = time.monotonic()
    args.work_root.mkdir(parents=True, exist_ok=False)
    (args.work_root / "snapshots").mkdir()
    (args.work_root / "graphs").mkdir()

    def ppo_objective(values_tree: Mapping[str, Any], data: Mapping[str, Any]):
        return v20.joint_recurrent_ppo_loss(
            values_tree, data, clip_epsilon=training.PPO_CLIP_EPSILON,
            value_coefficient=training.PPO_VALUE_COEFFICIENT,
            entropy_coefficient=training.PPO_ENTROPY_COEFFICIENT,
        )

    def predictor_objective(values_tree: Mapping[str, Any], data: Mapping[str, Any]):
        return v22.normalized_predictor_loss(values_tree, data, target_mean, target_std)

    ppo_grad = jax.value_and_grad(ppo_objective, has_aux=True)
    predictor_grad = jax.value_and_grad(predictor_objective, has_aux=True)
    for local_index in range(UPDATES):
        rollout_update_index = SOURCE_COMPLETED_UPDATES + local_index
        completed_updates = rollout_update_index + 1
        batch_np, episodes, observations = v20.stage2_rollout(
            smoke=smoke, full=full, training=training, mujoco=mujoco,
            scene=scene, population=population, preregistration=design,
            observer_type=observer_type, canonical_fit=args.canonical_fit,
            parameters=parameters, update_index=rollout_update_index,
        )
        full.validate_stage2_masks(batch_np, episodes)
        episode_hash = full.validate_episode_receipts(
            episodes, population, stage=2, update_index=rollout_update_index
        )
        boundary = full.stage2_action_boundary_evidence(batch_np)
        reward = v15.reward_evidence(batch_np)
        anchor_mask = v29.build_anchor_mask(population, batch_np["valid_mask"])
        _, values = training.stage2_mean_value(parameters, jnp.asarray(batch_np["hidden"], dtype=jnp.float32))
        objective_batch_np, objective_evidence = v24v3.apply_training_objective(
            batch_np, episodes, np.asarray(values, dtype=np.float32),
            gamma=training.PPO_GAMMA, gae_lambda=training.PPO_GAE_LAMBDA,
        )
        changed_keys = sorted(
            key for key in batch_np
            if not np.array_equal(np.asarray(batch_np[key]), objective_batch_np[key])
        )
        failure_mask = v24.roll_pitch_failure_mask(episodes, shape=np.asarray(batch_np["rewards"]).shape)
        if not (
            boundary["realized_equals_numpy_bit_exact"]
            and boundary["numpy_equals_jax_bit_exact"]
            and reward["reward_formula_bit_exact"]
            and (
                (int(np.sum(failure_mask)) > 0 and changed_keys == list(v24v2.MODIFIED_BATCH_KEYS)
                 and objective_evidence["zero_failure_bit_exact_noop"] is False)
                or (int(np.sum(failure_mask)) == 0 and changed_keys == []
                    and objective_evidence["zero_failure_bit_exact_noop"] is True)
            )
        ):
            raise ValueError(f"Winner-v46 transition changed at {completed_updates}")
        batch = {key: jnp.asarray(value) for key, value in objective_batch_np.items()}
        before = v21.joint_trainable_parameters(parameters)

        def anchor_objective(values_tree: Mapping[str, Any]):
            return v29.prefix_anchor_loss(values_tree, teacher_trainable, batch, anchor_mask)

        def static_teacher_objective(values_tree: Mapping[str, Any]):
            _, actions = v29.deterministic_bounded_actions(
                values_tree, batch["observations"], batch["previous_actions"]
            )
            return v44_runner.training_teacher_loss(
                actions, identifiers, batch_np["previous_actions"], batch_np["valid_mask"],
                table, jax, jnp,
            )

        (ppo_loss, ppo_metrics), ppo_gradients = ppo_grad(before, batch)
        (predictor_loss, predictor_metrics), predictor_gradients = predictor_grad(before, batch)
        (anchor_loss, anchor_metrics), anchor_gradients = jax.value_and_grad(anchor_objective, has_aux=True)(before)
        (teacher_loss, teacher_metrics), teacher_gradients = jax.value_and_grad(static_teacher_objective, has_aux=True)(before)
        ppo_predictor_gradients = v22v2.compose_gradients(ppo_gradients, predictor_gradients)
        baseline_gradients = v29.compose_gradients(
            ppo_predictor_gradients, anchor_gradients, PREFIX_ANCHOR_SCALE, enabled=True
        )
        gradients = v29.compose_gradients(
            baseline_gradients, teacher_gradients, FROZEN_TEACHER_SCALE, enabled=True
        )
        combined_loss = (
            ppo_loss
            + jnp.asarray(v22v2.FROZEN_PREDICTOR_SCALE, dtype=jnp.float32) * predictor_loss
            + jnp.asarray(PREFIX_ANCHOR_SCALE, dtype=jnp.float32) * anchor_loss
            + jnp.asarray(FROZEN_TEACHER_SCALE, dtype=jnp.float32) * teacher_loss
        )
        expected_stored = int(np.sum(
            batch_np["valid_transition_mask"][:, :-1] * batch_np["valid_mask"][:, 1:]
        ))
        teacher_gradient_max = common.tree_max_abs(teacher_gradients)
        anchor_gradient_max = common.tree_max_abs(anchor_gradients)
        _, _, teacher_mask = v44_runner.build_training_teacher_batch(
            identifiers, batch_np["previous_actions"], batch_np["valid_mask"], table, jax, jnp
        )
        teacher_mask_np = np.asarray(teacher_mask, dtype=np.float32)
        selected_rows = int(np.sum(np.any(teacher_mask_np > 0.0, axis=(1, 2))))
        selected_elements = int(np.sum(teacher_mask_np))
        if (
            float(ppo_metrics["sampled_hidden_replay_max_abs_error"]) > 1.0e-6
            or int(predictor_metrics["stored_successor_transition_count"]) != expected_stored
            or expected_stored <= 0
            or int(anchor_metrics["selected_elements"]) != v29.EXPECTED_ANCHOR_ELEMENTS
            or int(teacher_metrics["selected_elements"]) != selected_elements
            or selected_rows != 22 or selected_elements <= 0
            or not all(anchor_gradient_max[key] > 0.0 for key in v29.ANCHOR_GRADIENT_KEYS)
            or not all(anchor_gradient_max[key] == 0.0 for key in v29.NON_ANCHOR_GRADIENT_KEYS)
            or not all(teacher_gradient_max[key] > 0.0 for key in v29.ANCHOR_GRADIENT_KEYS)
            or not all(teacher_gradient_max[key] == 0.0 for key in v29.NON_ANCHOR_GRADIENT_KEYS)
        ):
            raise ValueError(f"Winner-v46 replay/teacher contract changed at {completed_updates}")
        after, optimizer = training.adam_step(
            before, gradients, optimizer, learning_rate=training.STAGE2_LEARNING_RATE,
            beta1=training.ADAM_BETA1, beta2=training.ADAM_BETA2,
            epsilon=training.ADAM_EPSILON,
        )
        after = training.clamp_stage2_parameters(after)
        full.validate_log_std(after)
        deltas = v20.leaf_max_abs_delta(before, after)
        gradient_max = common.tree_max_abs(gradients)
        if not all(value > 0.0 for value in gradient_max.values()) or not all(value > 0.0 for value in deltas.values()):
            raise ValueError(f"Winner-v46 closed a leaf at {completed_updates}")
        parameters = v21.merge_joint_trainable(parameters, after)
        if int(np.asarray(optimizer["count"])) != completed_updates or not training.finite_tree({
            "ppo_loss": ppo_loss, "ppo_metrics": ppo_metrics,
            "predictor_loss": predictor_loss, "predictor_metrics": predictor_metrics,
            "anchor_loss": anchor_loss, "anchor_metrics": anchor_metrics,
            "teacher_loss": teacher_loss, "teacher_metrics": teacher_metrics,
            "combined_loss": combined_loss, "gradients": gradients,
            "parameters": parameters, "optimizer": optimizer,
        }):
            raise FloatingPointError(f"Winner-v46 update {completed_updates} invalid")
        sampled = int(np.sum(batch_np["valid_mask"]))
        valid = int(np.sum(batch_np["valid_transition_mask"]))
        sampled_total += sampled
        valid_total += valid
        metrics.append({
            "local_update": local_index + 1,
            "rollout_update_index": rollout_update_index,
            "completed_updates": completed_updates,
            "optimizer_count": int(np.asarray(optimizer["count"])),
            "episode_receipts_sha256": episode_hash,
            "sampled_count": sampled,
            "valid_transition_count": valid,
            "stored_successor_transition_count": expected_stored,
            "roll_pitch_failure_count": int(np.sum(failure_mask)),
            "settled_success_count": sum(item.get("terminal_success_bonus_applied") is True for item in episodes),
            "ppo_loss": float(ppo_loss),
            "normalized_predictor_loss": float(predictor_loss),
            "prefix_anchor_loss": float(anchor_loss),
            "static_target_teacher_loss": float(teacher_loss),
            "maximum_selected_teacher_action_delta": float(teacher_metrics["maximum_selected_action_delta"]),
            "selected_anchor_elements": int(anchor_metrics["selected_elements"]),
            "selected_teacher_rows": selected_rows,
            "selected_teacher_elements": selected_elements,
            "combined_loss": float(combined_loss),
            "sampled_hidden_replay_max_abs_error": float(ppo_metrics["sampled_hidden_replay_max_abs_error"]),
            "anchor_gradient_max_abs": anchor_gradient_max,
            "teacher_gradient_max_abs": teacher_gradient_max,
            "combined_gradient_max_abs": gradient_max,
            "leaf_max_abs_delta": deltas,
            "objective_evidence": objective_evidence,
            "action_boundary_exact": True,
            "pitch_margin_reward_exact": True,
            "heldout_teacher_labels_absent": True,
        })
        snapshot_path = args.work_root / "snapshots" / f"snapshot_static_target_teacher_update_{completed_updates:03d}.npz"
        receipt = v22v2.save_snapshot(
            snapshot_path, parameters, optimizer,
            {
                "stage": "static_target_teacher_joint_stage2",
                "completed_updates": completed_updates,
                "source_completed_updates": SOURCE_COMPLETED_UPDATES,
                "source_snapshot_sha256": source_receipt["sha256"],
                "teacher_snapshot_sha256": teacher_receipt["sha256"],
                "objective": preregistration["objective"],
                "root_seed": 120120,
                "learning_rate": float(training.STAGE2_LEARNING_RATE),
                "predictor_scale": float(v22v2.FROZEN_PREDICTOR_SCALE),
                "prefix_anchor_scale": float(PREFIX_ANCHOR_SCALE),
                "static_target_teacher_scale": float(FROZEN_TEACHER_SCALE),
                "formal_support_cells": 0,
                "locomotion_steps": 0,
                "robot_or_rdk_access": 0,
            },
            restored["target_mean"], restored["target_std"],
        )
        loaded = v22v2.load_snapshot(snapshot_path)
        if not (
            common.tree_equal(parameters, loaded["parameters"])
            and np.array_equal(optimizer["count"], loaded["optimizer"]["count"])
            and common.tree_equal(optimizer["m"], loaded["optimizer"]["m"])
            and common.tree_equal(optimizer["v"], loaded["optimizer"]["v"])
            and np.array_equal(restored["target_mean"], loaded["target_mean"])
            and np.array_equal(restored["target_std"], loaded["target_std"])
            and loaded["metadata"].get("stage") == "static_target_teacher_joint_stage2"
            and loaded["metadata"].get("completed_updates") == completed_updates
        ):
            raise ValueError(f"Winner-v46 snapshot changed at {completed_updates}")
        snapshots.append({"completed_updates": completed_updates, **receipt})
        if completed_updates in {HALF_COMPLETED_UPDATES, FINAL_COMPLETED_UPDATES}:
            label = "half" if completed_updates == HALF_COMPLETED_UPDATES else "final"
            graph = graph_receipt(
                smoke=smoke, networks=networks, training=training, parameters=parameters,
                observations=observations, path=args.work_root / "graphs" / f"winner_v46_{label}.onnx",
                label=label, completed_updates=completed_updates,
            )
            checkpoints.append({
                "label": label, "completed_updates": completed_updates,
                "snapshot": receipt, "graph": graph,
            })

    cumulative = v20.leaf_max_abs_delta(source_trainable, v21.joint_trainable_parameters(parameters))
    teacher_unchanged = all(
        np.array_equal(teacher_trainable_copy[key], np.asarray(teacher_trainable[key]))
        for key in teacher_trainable_copy
    )
    frozen_parameters_unchanged = all(
        np.array_equal(value, np.asarray(parameters[key]))
        for key, value in frozen_parameter_copy.items()
    )
    expected_completed = list(range(253, 353))
    checks = {
        "source_snapshot_graph_and_optimizer_count_252_exact": True,
        "teacher_snapshot_and_optimizer_count_100_exact": True,
        "teacher_trainable_leaves_unchanged": teacher_unchanged,
        "frozen_parameter_leaves_unchanged": frozen_parameters_unchanged,
        "exact_100_continuation_updates": len(metrics) == 100
        and [row["completed_updates"] for row in metrics] == expected_completed,
        "all_100_episode_receipts_present": all(bool(row["episode_receipts_sha256"]) for row in metrics),
        "all_100_action_boundaries_exact": all(row["action_boundary_exact"] for row in metrics),
        "all_100_pitch_margin_rewards_exact": all(row["pitch_margin_reward_exact"] for row in metrics),
        "all_100_objective_failure_or_zero_failure_noop_contracts_exact": all(
            (row["roll_pitch_failure_count"] > 0 and row["objective_evidence"]["zero_failure_bit_exact_noop"] is False)
            or (row["roll_pitch_failure_count"] == 0 and row["objective_evidence"]["zero_failure_bit_exact_noop"] is True)
            for row in metrics
        ),
        "all_100_static_teacher_contracts_exact": all(
            row["selected_teacher_rows"] == 22
            and row["selected_teacher_elements"] > 0
            and row["static_target_teacher_loss"] >= 0.0
            and row["maximum_selected_teacher_action_delta"] >= 0.0
            and row["heldout_teacher_labels_absent"] is True
            and all(row["teacher_gradient_max_abs"][key] > 0.0 for key in v29.ANCHOR_GRADIENT_KEYS)
            and all(row["teacher_gradient_max_abs"][key] == 0.0 for key in v29.NON_ANCHOR_GRADIENT_KEYS)
            for row in metrics
        ),
        "all_100_prefix_anchor_contracts_exact": all(
            row["selected_anchor_elements"] == v29.EXPECTED_ANCHOR_ELEMENTS
            and all(row["anchor_gradient_max_abs"][key] > 0.0 for key in v29.ANCHOR_GRADIENT_KEYS)
            and all(row["anchor_gradient_max_abs"][key] == 0.0 for key in v29.NON_ANCHOR_GRADIENT_KEYS)
            for row in metrics
        ),
        "all_100_hidden_replays_at_most_1e_6": all(row["sampled_hidden_replay_max_abs_error"] <= 1.0e-6 for row in metrics),
        "all_100_stored_successor_masks_nonempty": all(row["stored_successor_transition_count"] > 0 for row in metrics),
        "all_100_updates_all_12_gradients_and_deltas_nonzero": all(
            all(value > 0.0 for value in row["combined_gradient_max_abs"].values())
            and all(value > 0.0 for value in row["leaf_max_abs_delta"].values())
            for row in metrics
        ),
        "all_12_leaves_changed_cumulatively": all(value > 0.0 for value in cumulative.values()),
        "exact_100_atomic_snapshots": len(snapshots) == 100
        and [row["completed_updates"] for row in snapshots] == expected_completed,
        "optimizer_count_352_exact": int(np.asarray(optimizer["count"])) == 352,
        "half_and_final_graphs_present": [
            (row["label"], row["completed_updates"]) for row in checkpoints
        ] == [("half", 302), ("final", 352)],
        "all_updates_finite": True,
        "formal_support_cells_zero": True,
        "locomotion_steps_zero": True,
        "robot_or_rdk_access_zero": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    result = {
        "schema_version": "winner_v46.static_target_teacher_training_result.v1",
        "status": "PASS_WINNER_V46_STATIC_TARGET_TEACHER_TRAINING_ARTIFACT" if not failed else "HOLD_WINNER_V46_STATIC_TARGET_TEACHER_TRAINING_ARTIFACT",
        "decision": "AUTHORIZE_STATIC_TARGET_TEACHER_SUPPORT_GATE_PREREGISTRATION_ONLY" if not failed else "DO_NOT_EVALUATE_WINNER_V46_POLICY",
        "checks": checks,
        "failed_checks": failed,
        "source_snapshot": {
            "sha256": source_receipt["sha256"], "bytes": source_receipt["bytes"],
            "completed_updates": 252, "optimizer_count": 252,
        },
        "source_graph": {
            "sha256": source_graph_receipt["sha256"], "bytes": source_graph_receipt["bytes"],
            "completed_updates": 252,
        },
        "teacher_snapshot": {
            "sha256": teacher_receipt["sha256"], "bytes": teacher_receipt["bytes"],
            "completed_updates": 100, "optimizer_count": 100,
        },
        "objective": preregistration["objective"],
        "metrics": metrics,
        "snapshot_manifest": snapshots,
        "persistent_checkpoints": checkpoints,
        "cumulative_leaf_max_abs_delta": cumulative,
        "elapsed_seconds": time.monotonic() - start,
        "execution": {
            "optimizer_updates": 100, "scheduled_episode_slots": 2_000_000,
            "formal_support_cells": 0, "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "environment": {
            "jax_backend": jax.default_backend(),
            "jax_devices": [str(device) for device in jax.devices()],
        },
        "sources": {
            "preregistration_lf_sha256": lf_sha256(PREREGISTRATION),
            "v45_result_lf_sha256": lf_sha256(V45_RESULT),
            "v42_result_lf_sha256": lf_sha256(V42_RESULT),
            "v22_result_lf_sha256": lf_sha256(V22_RESULT),
            "runner_lf_sha256": lf_sha256(Path(__file__)),
        },
        "authority": {
            "robot_clearance": False,
            "training_executed": True,
            "formal_support_gate_executed": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "pass_authorizes_only": "a separate frozen static-target-teacher support gate preregistration",
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(result["status"])
    for name in failed:
        print(f"FAILED={name}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
