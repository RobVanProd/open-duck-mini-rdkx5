#!/usr/bin/env python3
"""Run exactly one frozen Winner-v45 static-target-teacher update on CPU."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import sys
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


CONTRACT = ANALYSIS / "winner_v45_static_target_teacher_one_update_cpu_contract.json"
V44_RESULT = ANALYSIS / "winner_v44_static_target_teacher_source_gradient_result.json"
V42_RESULT = ANALYSIS / "winner_v42_static_target_teacher_table_result.json"
V32_PREREG = ANALYSIS / "winner_v32_prefix_right_pitch_anchor_training_preregistration.json"
FULL_PREREG = ANALYSIS / "winner_v12_full_calibrator_training_preregistration.json"
DOMAIN = ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
ROLLOUT_UPDATE_INDEX = 251
SOURCE_OPTIMIZER_COUNT = 251
RESULT_OPTIMIZER_COUNT = 252
PREFIX_ANCHOR_SCALE = np.float32(197.3112030029297)
FROZEN_TEACHER_SCALE = np.float32(58.436370849609375)
SCALE_RELATIVE_TOLERANCE = 2.0e-6
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
        raise ValueError("Winner-v45 tree schema changed")
    return {
        key: float(np.max(np.abs(
            np.asarray(left[key], dtype=np.float64)
            - np.asarray(right[key], dtype=np.float64)
        )))
        for key in left
    }


def validate_artifact(path: Path, receipt: Mapping[str, Any], label: str) -> None:
    if (
        not path.is_file()
        or path.stat().st_size != int(receipt["bytes"])
        or sha256(path) != receipt["sha256"]
    ):
        raise ValueError(f"Winner-v45 {label} artifact changed")


def validate_contract(value: Mapping[str, Any]) -> None:
    if (
        value.get("schema_version")
        != "winner_v45.static_target_teacher_one_update_cpu_contract.v1"
        or value.get("status")
        != "PREREGISTERED_WINNER_V45_STATIC_TARGET_TEACHER_ONE_UPDATE_CPU_PROOF"
        or value.get("decision")
        != "AUTHORIZE_EXACT_ONE_STATIC_TARGET_TEACHER_OPTIMIZER_UPDATE_ONLY"
    ):
        raise ValueError("Winner-v45 contract identity changed")
    objective = value.get("objective", {})
    if (
        objective.get("source_checkpoint") != {"label": "winner_v32_half", "update": 251}
        or objective.get("teacher_checkpoint") != {"label": "winner_v22_final", "update": 100}
        or objective.get("rollout_update_index") != ROLLOUT_UPDATE_INDEX
        or objective.get("result_optimizer_count") != RESULT_OPTIMIZER_COUNT
        or objective.get("episode_slots") != 80
        or objective.get("ticks_per_slot") != 250
        or objective.get("teacher_configuration_ids") != list(TRAINING_TEACHER_IDS)
        or objective.get("heldout_teacher_configuration_ids_excluded")
        != list(HELDOUT_TEACHER_IDS)
        or objective.get("teacher_configuration_rows") != 22
        or objective.get("teacher_action_indices") != list(v43.PITCH_ACTION_INDICES)
        or float(objective.get("teacher_scale", math.nan)) != float(FROZEN_TEACHER_SCALE)
        or float(objective.get("predictor_scale", math.nan)) != 380.9135437011719
        or float(objective.get("prefix_anchor_scale", math.nan)) != float(PREFIX_ANCHOR_SCALE)
        or objective.get("no_action_replacement") is not True
    ):
        raise ValueError("Winner-v45 objective changed")
    if value.get("execution_now") != {
        "rollout_episode_slots": 0,
        "scheduled_rollout_ticks": 0,
        "optimizer_updates": 0,
        "formal_support_cells": 0,
        "continuation_training_updates": 0,
        "deployable_graph_exports": 0,
        "robot_or_rdk_access": 0,
    } or value.get("execution_future") != {
        "rollout_episode_slots": 80,
        "scheduled_rollout_ticks": 20000,
        "optimizer_updates": 1,
        "formal_support_cells": 0,
        "continuation_training_updates": 0,
        "deployable_graph_exports": 1,
        "robot_or_rdk_access": 0,
    }:
        raise ValueError("Winner-v45 execution boundary changed")
    sources = value.get("sources")
    if not isinstance(sources, dict) or not sources:
        raise ValueError("Winner-v45 source manifest is absent")
    for name, item in sources.items():
        if item.get("hash_mode") != "lf" or lf_sha256(ROOT / item["path"]) != item.get("sha256"):
            raise ValueError(f"Winner-v45 source changed: {name}")
    if canonical_sha256(sources) != value.get("source_manifest_sha256"):
        raise ValueError("Winner-v45 source manifest changed")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--canonical-fit", type=Path, required=True)
    parser.add_argument("--v32-training-work-root", type=Path, required=True)
    parser.add_argument("--v22-training-work-root", type=Path, required=True)
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--offline-cpu-only", action="store_true")
    parser.add_argument("--one-update-static-target-teacher-proof-authorized", action="store_true")
    args = parser.parse_args()
    if not args.offline_cpu_only or not args.one_update_static_target_teacher_proof_authorized:
        raise PermissionError(
            "Winner-v45 requires --offline-cpu-only and "
            "--one-update-static-target-teacher-proof-authorized"
        )
    if args.work_root.exists() or args.output.exists():
        raise FileExistsError("refusing to overwrite Winner-v45 evidence")

    import jax
    import jax.numpy as jnp
    import mujoco
    import onnx
    import run_winner_v12_calibrator_cpu_smoke as smoke
    import run_winner_v12_full_calibrator_training as full
    import run_winner_v22_normalized_predictor_support_gate as v22_gate
    import run_winner_v33_prefix_right_pitch_anchor_support_gate as v33_gate
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
        raise ValueError("Winner-v45 requires CPU-only JAX")
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    validate_contract(contract)
    v44 = json.loads(V44_RESULT.read_text(encoding="utf-8"))
    if (
        v44.get("status") != "PASS_WINNER_V44_STATIC_TARGET_TEACHER_SOURCE_GRADIENT_CONTRACT"
        or v44.get("decision")
        != "AUTHORIZE_ONE_UPDATE_STATIC_TARGET_TEACHER_CPU_PROOF_PREREGISTRATION_ONLY"
        or v44.get("failed_checks") != []
        or float(v44["objective_evidence"]["teacher_scale"])
        != float(FROZEN_TEACHER_SCALE)
        or v44.get("execution", {}).get("optimizer_updates") != 0
    ):
        raise ValueError("Winner-v44 does not authorize Winner-v45")
    table = v43.load_teacher_table(json.loads(V42_RESULT.read_text(encoding="utf-8")))
    artifact_inputs = contract["artifact_inputs"]
    source_snapshot_path = (
        args.v32_training_work_root / "snapshots/snapshot_prefix_anchor_update_251.npz"
    )
    source_graph_path = args.v32_training_work_root / "graphs/winner_v32_half.onnx"
    teacher_snapshot_path = (
        args.v22_training_work_root / "snapshots/snapshot_normalized_predictor_update_100.npz"
    )
    validate_artifact(
        source_snapshot_path,
        artifact_inputs["winner_v32"]["half"]["snapshot"],
        "Winner-v32 half snapshot",
    )
    validate_artifact(
        source_graph_path,
        artifact_inputs["winner_v32"]["half"]["graph"],
        "Winner-v32 half graph",
    )
    validate_artifact(
        teacher_snapshot_path,
        artifact_inputs["winner_v22"]["snapshot"],
        "Winner-v22 teacher snapshot",
    )
    expected_versions = dict(
        json.loads(FULL_PREREG.read_text(encoding="utf-8"))[
            "implementation_contract_environment"
        ]
    )
    if expected_versions.pop("platform") != "CPU only" or not smoke.validate_software_versions(
        {"software_versions": expected_versions}
    )["exact"]:
        raise ValueError("Winner-v45 software environment changed")
    if smoke.sha256(args.canonical_fit) != smoke.P30_FIT_LF_SHA256:
        raise ValueError("Winner-v45 canonical P30 fit changed")
    if smoke.git_output(args.playground_root, "rev-parse", "HEAD") != smoke.CONTROL_COMMIT:
        raise ValueError("Winner-v45 Playground source changed")
    smoke.validate_playground_tree(args.playground_root)
    scene = args.playground_root / smoke.SCENE_RELATIVE
    if smoke.sha256(scene) != smoke.SCENE_SHA256:
        raise ValueError("Winner-v45 scene changed")

    source = v22v2.load_snapshot(source_snapshot_path)
    teacher = v22v2.load_snapshot(teacher_snapshot_path)
    v33_gate.smoke = smoke
    v33_gate.training = training
    v33_gate.v21 = v21
    v33_gate._TRAINING_PREREG = json.loads(V32_PREREG.read_text(encoding="utf-8"))
    v33_gate._validate_snapshot(source, expected_stage="prefix_right_pitch_anchor_joint_stage2")
    v22_gate.smoke = smoke
    v22_gate.training = training
    v22_gate.v21 = v21
    v22_gate._validate_snapshot(teacher, expected_stage="normalized_predictor_joint_stage2")
    if (
        source["metadata"].get("completed_updates") != SOURCE_OPTIMIZER_COUNT
        or int(np.asarray(source["optimizer"]["count"])) != SOURCE_OPTIMIZER_COUNT
        or teacher["metadata"].get("completed_updates") != 100
        or int(np.asarray(teacher["optimizer"]["count"])) != 100
        or not np.array_equal(source["target_mean"], teacher["target_mean"])
        or not np.array_equal(source["target_std"], teacher["target_std"])
    ):
        raise ValueError("Winner-v45 restore boundary changed")

    parameters = source["parameters"]
    optimizer = source["optimizer"]
    parameters_copy = {key: np.asarray(value).copy() for key, value in parameters.items()}
    optimizer_copy = {
        "count": np.asarray(optimizer["count"]).copy(),
        "m": {key: np.asarray(value).copy() for key, value in optimizer["m"].items()},
        "v": {key: np.asarray(value).copy() for key, value in optimizer["v"].items()},
    }
    before = v21.joint_trainable_parameters(parameters)
    teacher_trainable = v21.joint_trainable_parameters(teacher["parameters"])
    target_mean = jnp.asarray(source["target_mean"], dtype=jnp.float32)
    target_std = jnp.asarray(source["target_std"], dtype=jnp.float32)
    population = full.training_population(
        json.loads(FULL_PREREG.read_text(encoding="utf-8")),
        json.loads(DOMAIN.read_text(encoding="utf-8")),
    )
    identifiers = [str(row["id"]) for row in population]
    if len(population) != 80 or any(name in identifiers for name in HELDOUT_TEACHER_IDS):
        raise ValueError("Winner-v45 training population changed or leaked heldout labels")
    design = json.loads(smoke.CALIBRATOR_PREREG.read_text(encoding="utf-8"))
    observer_type = smoke.load_runtime_observer(args.canonical_fit)
    batch_np, episodes, observations = v20.stage2_rollout(
        smoke=smoke,
        full=full,
        training=training,
        mujoco=mujoco,
        scene=scene,
        population=population,
        preregistration=design,
        observer_type=observer_type,
        canonical_fit=args.canonical_fit,
        parameters=parameters,
        update_index=ROLLOUT_UPDATE_INDEX,
    )
    full.validate_stage2_masks(batch_np, episodes)
    episode_hash = full.validate_episode_receipts(
        episodes, population, stage=2, update_index=ROLLOUT_UPDATE_INDEX
    )
    boundary = full.stage2_action_boundary_evidence(batch_np)
    reward = v15.reward_evidence(batch_np)
    anchor_mask = v29.build_anchor_mask(population, batch_np["valid_mask"])
    _, values = training.stage2_mean_value(
        parameters, jnp.asarray(batch_np["hidden"], dtype=jnp.float32)
    )
    objective_batch_np, objective_evidence = v24v3.apply_training_objective(
        batch_np,
        episodes,
        np.asarray(values, dtype=np.float32),
        gamma=training.PPO_GAMMA,
        gae_lambda=training.PPO_GAE_LAMBDA,
    )
    changed_keys = sorted(
        key for key in batch_np
        if not np.array_equal(np.asarray(batch_np[key]), objective_batch_np[key])
    )
    failure_mask = v24.roll_pitch_failure_mask(
        episodes, shape=np.asarray(batch_np["rewards"]).shape
    )
    batch = {key: jnp.asarray(value) for key, value in objective_batch_np.items()}

    def ppo_objective(values_tree: Mapping[str, Any]):
        return v20.joint_recurrent_ppo_loss(
            values_tree,
            batch,
            clip_epsilon=training.PPO_CLIP_EPSILON,
            value_coefficient=training.PPO_VALUE_COEFFICIENT,
            entropy_coefficient=training.PPO_ENTROPY_COEFFICIENT,
        )

    def predictor_objective(values_tree: Mapping[str, Any]):
        return v22.normalized_predictor_loss(values_tree, batch, target_mean, target_std)

    def anchor_objective(values_tree: Mapping[str, Any]):
        return v29.prefix_anchor_loss(values_tree, teacher_trainable, batch, anchor_mask)

    def teacher_objective(values_tree: Mapping[str, Any]):
        _, candidate_actions = v29.deterministic_bounded_actions(
            values_tree, batch["observations"], batch["previous_actions"]
        )
        return v44_runner.training_teacher_loss(
            candidate_actions,
            identifiers,
            batch_np["previous_actions"],
            batch_np["valid_mask"],
            table,
            jax,
            jnp,
        )

    (ppo_loss, ppo_metrics), ppo_gradients = jax.value_and_grad(
        ppo_objective, has_aux=True
    )(before)
    (predictor_loss, predictor_metrics), predictor_gradients = jax.value_and_grad(
        predictor_objective, has_aux=True
    )(before)
    (anchor_loss, anchor_metrics), anchor_gradients = jax.value_and_grad(
        anchor_objective, has_aux=True
    )(before)
    (teacher_loss_before, teacher_metrics_before), teacher_gradients = jax.value_and_grad(
        teacher_objective, has_aux=True
    )(before)
    ppo_predictor_gradients = v22v2.compose_gradients(ppo_gradients, predictor_gradients)
    baseline_gradients = v29.compose_gradients(
        ppo_predictor_gradients,
        anchor_gradients,
        PREFIX_ANCHOR_SCALE,
        enabled=True,
    )
    recomputed_scale, recomputed_balance = v29.gradient_balance_scale(
        baseline_gradients, teacher_gradients
    )
    disabled_gradients = v29.compose_gradients(
        baseline_gradients, teacher_gradients, FROZEN_TEACHER_SCALE, enabled=False
    )
    gradients = v29.compose_gradients(
        baseline_gradients, teacher_gradients, FROZEN_TEACHER_SCALE, enabled=True
    )
    disabled_delta = tree_delta_max_abs(baseline_gradients, disabled_gradients)
    teacher_gradient_delta = tree_delta_max_abs(baseline_gradients, gradients)
    combined_loss = (
        ppo_loss
        + jnp.asarray(v22v2.FROZEN_PREDICTOR_SCALE, dtype=jnp.float32) * predictor_loss
        + jnp.asarray(PREFIX_ANCHOR_SCALE, dtype=jnp.float32) * anchor_loss
        + jnp.asarray(FROZEN_TEACHER_SCALE, dtype=jnp.float32) * teacher_loss_before
    )
    after, optimizer_after = training.adam_step(
        before,
        gradients,
        optimizer,
        learning_rate=training.STAGE2_LEARNING_RATE,
        beta1=training.ADAM_BETA1,
        beta2=training.ADAM_BETA2,
        epsilon=training.ADAM_EPSILON,
    )
    after = training.clamp_stage2_parameters(after)
    full.validate_log_std(after)
    parameters_after = v21.merge_joint_trainable(parameters, after)
    teacher_loss_after, teacher_metrics_after = teacher_objective(after)
    gradient_max = common.tree_max_abs(gradients)
    teacher_gradient_max = common.tree_max_abs(teacher_gradients)
    leaf_delta = v20.leaf_max_abs_delta(before, after)
    frozen_parameter_keys = sorted(set(parameters) - set(v21.JOINT_TRAINABLE_KEYS))
    frozen_parameter_delta = {
        key: float(np.max(np.abs(
            np.asarray(parameters_after[key], dtype=np.float64)
            - np.asarray(parameters[key], dtype=np.float64)
        )))
        for key in frozen_parameter_keys
    }
    raw_teacher, bounded_teacher, teacher_mask = v44_runner.build_training_teacher_batch(
        identifiers,
        batch_np["previous_actions"],
        batch_np["valid_mask"],
        table,
        jax,
        jnp,
    )
    teacher_mask_np = np.asarray(teacher_mask, dtype=np.float32)
    selected_rows = int(np.sum(np.any(teacher_mask_np > 0.0, axis=(1, 2))))
    selected_elements = int(np.sum(teacher_mask_np))
    source_state_unchanged_before_update = (
        all(np.array_equal(parameters_copy[key], np.asarray(parameters[key])) for key in parameters_copy)
        and np.array_equal(optimizer_copy["count"], optimizer["count"])
        and common.tree_equal(optimizer_copy["m"], optimizer["m"])
        and common.tree_equal(optimizer_copy["v"], optimizer["v"])
    )
    expected_stored = int(np.sum(
        batch_np["valid_transition_mask"][:, :-1] * batch_np["valid_mask"][:, 1:]
    ))
    scale_relative_error = abs(float(recomputed_scale) - float(FROZEN_TEACHER_SCALE)) / float(FROZEN_TEACHER_SCALE)
    if not training.finite_tree({
        "ppo_loss": ppo_loss,
        "predictor_loss": predictor_loss,
        "anchor_loss": anchor_loss,
        "teacher_loss_before": teacher_loss_before,
        "teacher_loss_after": teacher_loss_after,
        "combined_loss": combined_loss,
        "gradients": gradients,
        "parameters": parameters_after,
        "optimizer": optimizer_after,
    }):
        raise FloatingPointError("Winner-v45 one-update state is nonfinite")

    args.work_root.mkdir(parents=True, exist_ok=False)
    graph = args.work_root / "winner_v45_static_target_teacher_update_252.onnx"
    networks.export_calibrator_onnx(training.deployable_parameters(parameters_after), graph)
    graph_contract = smoke.onnx_contract(graph, parameters_after, observations)
    model = onnx.load(graph)
    graph_inventory = "\n".join([
        *(value.name for value in model.graph.initializer),
        *(node.name for node in model.graph.node),
        *(name for node in model.graph.node for name in node.input),
        *(name for node in model.graph.node for name in node.output),
    ]).lower()
    v45_forbidden_tokens = [
        token for token in (
            "teacher", "static_target", "configuration_table", "configuration_id",
            "privileged", "heldout",
        ) if token in graph_inventory
    ]
    snapshot_path = args.work_root / "winner_v45_static_target_teacher_update_252.npz"
    snapshot_receipt = v22v2.save_snapshot(
        snapshot_path,
        parameters_after,
        optimizer_after,
        {
            "stage": "static_target_teacher_joint_stage2",
            "completed_updates": RESULT_OPTIMIZER_COUNT,
            "source_completed_updates": SOURCE_OPTIMIZER_COUNT,
            "source_snapshot_sha256": artifact_inputs["winner_v32"]["half"]["snapshot"]["sha256"],
            "teacher_snapshot_sha256": artifact_inputs["winner_v22"]["snapshot"]["sha256"],
            "objective": contract["objective"],
            "root_seed": 120120,
            "learning_rate": float(training.STAGE2_LEARNING_RATE),
            "predictor_scale": float(v22v2.FROZEN_PREDICTOR_SCALE),
            "prefix_anchor_scale": float(PREFIX_ANCHOR_SCALE),
            "static_target_teacher_scale": float(FROZEN_TEACHER_SCALE),
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
        and loaded["metadata"].get("stage") == "static_target_teacher_joint_stage2"
        and loaded["metadata"].get("completed_updates") == RESULT_OPTIMIZER_COUNT
    )
    policy_keys = set(v29.ANCHOR_GRADIENT_KEYS)
    nonpolicy_keys = set(v29.NON_ANCHOR_GRADIENT_KEYS)
    checks = {
        "cpu_only_environment_exact": True,
        "winner_v32_half_source_snapshot_and_graph_exact": True,
        "winner_v22_teacher_snapshot_exact": True,
        "source_snapshot_optimizer_count_251_exact": True,
        "exact_80_episode_rollout_at_update_251": len(episodes) == 80,
        "episode_receipts_present": bool(episode_hash),
        "action_boundary_exact": boundary["realized_equals_numpy_bit_exact"] and boundary["numpy_equals_jax_bit_exact"],
        "pitch_margin_reward_exact": reward["reward_formula_bit_exact"],
        "winner_v32_baseline_objective_transition_exact": (
            (int(np.sum(failure_mask)) > 0 and changed_keys == list(v24v2.MODIFIED_BATCH_KEYS)
             and objective_evidence["zero_failure_bit_exact_noop"] is False)
            or (int(np.sum(failure_mask)) == 0 and changed_keys == []
                and objective_evidence["zero_failure_bit_exact_noop"] is True)
        ),
        "exact_22_training_teacher_configuration_plant_rows": selected_rows == 22,
        "heldout_teacher_configuration_rows_excluded": all(name not in identifiers for name in HELDOUT_TEACHER_IDS),
        "teacher_mask_has_only_valid_pitch_elements": selected_elements > 0 and np.all(
            teacher_mask_np[..., sorted(set(range(14)) - set(v43.PITCH_ACTION_INDICES))] == 0.0
        ),
        "teacher_loss_before_finite_nonzero": math.isfinite(float(teacher_loss_before)) and float(teacher_loss_before) > 0.0,
        "teacher_scale_reproduced_within_2e_6_relative": scale_relative_error <= SCALE_RELATIVE_TOLERANCE,
        "frozen_recorded_teacher_scale_used": float(FROZEN_TEACHER_SCALE) == 58.436370849609375,
        "default_off_gradient_bit_exact": max(disabled_delta.values()) == 0.0,
        "teacher_changes_all_six_policy_gradient_leaves": all(teacher_gradient_delta[key] > 0.0 for key in policy_keys),
        "teacher_preserves_nonpolicy_gradients_bit_exact": all(teacher_gradient_delta[key] == 0.0 for key in nonpolicy_keys),
        "teacher_gradients_nonzero_on_all_six_policy_leaves": all(teacher_gradient_max[key] > 0.0 for key in policy_keys),
        "teacher_gradients_zero_on_value_logstd_predictor_leaves": all(teacher_gradient_max[key] == 0.0 for key in nonpolicy_keys),
        "predictor_metrics_finite_and_successors_present": training.finite_tree(predictor_metrics)
        and int(predictor_metrics["stored_successor_transition_count"]) == expected_stored and expected_stored > 0,
        "ppo_metrics_finite_and_hidden_replay_exact": training.finite_tree(ppo_metrics)
        and float(ppo_metrics["sampled_hidden_replay_max_abs_error"]) <= 1.0e-6,
        "prefix_anchor_metrics_finite_and_exact": training.finite_tree(anchor_metrics)
        and int(anchor_metrics["selected_elements"]) == v29.EXPECTED_ANCHOR_ELEMENTS,
        "teacher_metrics_finite_and_mask_exact": training.finite_tree(teacher_metrics_before)
        and training.finite_tree(teacher_metrics_after)
        and int(teacher_metrics_before["selected_elements"]) == selected_elements,
        "all_12_combined_gradients_nonzero": set(gradient_max) == set(v21.JOINT_TRAINABLE_KEYS)
        and all(value > 0.0 for value in gradient_max.values()),
        "all_12_trainable_leaves_changed": set(leaf_delta) == set(v21.JOINT_TRAINABLE_KEYS)
        and all(value > 0.0 for value in leaf_delta.values()),
        "all_frozen_parameter_leaves_bit_exact": all(value == 0.0 for value in frozen_parameter_delta.values()),
        "source_state_unchanged_before_update": source_state_unchanged_before_update,
        "exactly_one_optimizer_update_251_to_252": int(np.asarray(optimizer_after["count"])) == RESULT_OPTIMIZER_COUNT,
        "same_batch_teacher_loss_strictly_decreases": math.isfinite(float(teacher_loss_after))
        and float(teacher_loss_after) < float(teacher_loss_before),
        "all_losses_metrics_parameters_optimizer_finite": True,
        "snapshot_readback_exact": snapshot_exact,
        "onnx_abi_exact": graph_contract["abi_exact"],
        "onnx_training_only_tensors_absent": graph_contract["training_only_tensors_absent"],
        "onnx_v45_teacher_privileged_tokens_absent": not v45_forbidden_tokens,
        "onnx_jax_chain_at_most_1e_7": graph_contract["jax_onnx_at_most_1e_7"],
        "onnx_previous_action_chain_exact": graph_contract["previous_action_out_equals_action_bit_exact"],
        "formal_support_continuation_robot_zero": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    passed = not failed
    result = {
        "schema_version": "winner_v45.static_target_teacher_one_update_cpu_result.v1",
        "status": "PASS_WINNER_V45_STATIC_TARGET_TEACHER_ONE_UPDATE_CPU_PROOF" if passed else "HOLD_WINNER_V45_STATIC_TARGET_TEACHER_ONE_UPDATE_CPU_PROOF",
        "decision": "AUTHORIZE_STATIC_TARGET_TEACHER_TRAINING_PREREGISTRATION_ONLY" if passed else "DO_NOT_TRAIN_STATIC_TARGET_TEACHER_OBJECTIVE",
        "checks": checks,
        "failed_checks": failed,
        "source_identity": {
            "source_snapshot": artifact_inputs["winner_v32"]["half"]["snapshot"],
            "source_graph": artifact_inputs["winner_v32"]["half"]["graph"],
            "teacher_snapshot": artifact_inputs["winner_v22"]["snapshot"],
        },
        "objective": contract["objective"],
        "rollout": {
            "update_index": ROLLOUT_UPDATE_INDEX,
            "episode_slots": len(episodes),
            "scheduled_ticks": len(episodes) * 250,
            "episode_receipts_sha256": episode_hash,
            "roll_pitch_failure_count": int(np.sum(failure_mask)),
            "sampled_count": int(np.sum(batch_np["valid_mask"])),
            "valid_transition_count": int(np.sum(batch_np["valid_transition_mask"])),
            "stored_successor_transition_count": expected_stored,
            "changed_batch_keys": changed_keys,
            "selected_teacher_rows": selected_rows,
            "selected_teacher_elements": selected_elements,
            "observations_sha256": array_sha256(batch_np["observations"]),
            "previous_actions_sha256": array_sha256(batch_np["previous_actions"]),
            "teacher_raw_targets_sha256": array_sha256(np.asarray(raw_teacher)),
            "teacher_bounded_targets_sha256": array_sha256(np.asarray(bounded_teacher)),
            "teacher_mask_sha256": array_sha256(teacher_mask_np),
            "cross_worker_byte_hashes_are_not_pass_gates": True,
        },
        "optimization": {
            "optimizer_count_before": SOURCE_OPTIMIZER_COUNT,
            "optimizer_count_after": int(np.asarray(optimizer_after["count"])),
            "ppo_loss": float(ppo_loss),
            "normalized_predictor_loss": float(predictor_loss),
            "prefix_anchor_loss": float(anchor_loss),
            "teacher_loss_before": float(teacher_loss_before),
            "teacher_loss_after": float(teacher_loss_after),
            "teacher_loss_delta": float(teacher_loss_after - teacher_loss_before),
            "combined_loss": float(combined_loss),
            "predictor_scale": float(v22v2.FROZEN_PREDICTOR_SCALE),
            "prefix_anchor_scale": float(PREFIX_ANCHOR_SCALE),
            "teacher_scale": float(FROZEN_TEACHER_SCALE),
            "recomputed_teacher_scale": float(recomputed_scale),
            "recomputed_balance": recomputed_balance,
            "teacher_scale_relative_error": scale_relative_error,
            "combined_gradient_max_abs": gradient_max,
            "teacher_gradient_max_abs": teacher_gradient_max,
            "leaf_max_abs_delta": leaf_delta,
            "frozen_parameter_leaf_max_abs_delta": frozen_parameter_delta,
            "trainable_leaves": list(v21.JOINT_TRAINABLE_KEYS),
            "source_state_unchanged_before_update": source_state_unchanged_before_update,
            "snapshot_readback_exact": snapshot_exact,
        },
        "snapshot": snapshot_receipt,
        "graph": {
            "path": str(graph),
            "sha256": sha256(graph),
            "bytes": graph.stat().st_size,
            "contract": graph_contract,
            "v45_forbidden_tokens_present": v45_forbidden_tokens,
        },
        "execution": {
            "rollout_episode_slots": len(episodes),
            "scheduled_rollout_ticks": len(episodes) * 250,
            "optimizer_updates": 1,
            "formal_support_cells": 0,
            "continuation_training_updates": 0,
            "deployable_graph_exports": 1,
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
            "pass_authorizes_only": "a separate frozen bounded static-target-teacher continuation preregistration",
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(result["status"])
    for name in failed:
        print(f"FAILED={name}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
