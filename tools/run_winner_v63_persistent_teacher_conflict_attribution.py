#!/usr/bin/env python3
"""Attribute the stalled persistent-teacher objective at Winner-v60 final."""

from __future__ import annotations

import argparse
from collections.abc import Mapping, Sequence
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

PREREGISTRATION = (
    ANALYSIS / "winner_v63_persistent_teacher_conflict_preregistration.json"
)
V60_RESULT = ANALYSIS / "winner_v60_integrated_numeric_guard_training_result.json"
V60_PREREGISTRATION = (
    ANALYSIS / "winner_v60_integrated_numeric_guard_training_preregistration.json"
)
V62_RESULT = ANALYSIS / "winner_v62_residual_teacher_causal_result.json"
V42_RESULT = ANALYSIS / "winner_v42_static_target_teacher_table_result.json"
FULL_PREREGISTRATION = (
    ANALYSIS / "winner_v12_full_calibrator_training_preregistration.json"
)
DOMAIN = ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
ROLLOUT_UPDATE_INDEX = 554
PREFIX_ANCHOR_SCALE = np.float32(197.3112030029297)
TRAINING_TEACHER_IDS = (
    "COM_X_NEG",
    "COM_CORNER_00",
    "COM_CORNER_01",
    "COM_CORNER_02",
    "COM_CORNER_03",
    "OPTIONAL_AGGREGATE_HEAVY_AFT",
    "DISCOVERY_02",
    "DISCOVERY_03",
    "DISCOVERY_06",
    "DISCOVERY_09",
    "DISCOVERY_10",
)
HELDOUT_TEACHER_IDS = ("HELDOUT_04", "HELDOUT_07", "HELDOUT_09", "HELDOUT_15")


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


def validate_artifact(path: Path, receipt: Mapping[str, Any], label: str) -> None:
    if (
        not path.is_file()
        or path.stat().st_size != int(receipt["bytes"])
        or sha256(path) != receipt["sha256"]
    ):
        raise ValueError(f"Winner-v63 {label} artifact changed")


def validate_preregistration(value: Mapping[str, Any]) -> None:
    expected_execution = {
        "rollout_episode_slots": 80,
        "scheduled_rollout_ticks": 20000,
        "counterfactual_in_memory_adam_steps": 2,
        "committed_optimizer_updates": 0,
        "formal_support_cells": 0,
        "locomotion_training_steps": 0,
        "deployable_graph_exports": 0,
        "robot_or_rdk_access": 0,
    }
    if (
        value.get("schema_version")
        != "winner_v63.persistent_teacher_conflict_preregistration.v1"
        or value.get("status")
        != "PREREGISTERED_WINNER_V63_PERSISTENT_TEACHER_CONFLICT_ATTRIBUTION"
        or value.get("decision")
        != "AUTHORIZE_ONE_ZERO_COMMIT_CPU_ATTRIBUTION_ONLY"
        or value.get("frozen_source", {}).get("completed_updates") != 554
        or value.get("frozen_objective", {}).get("rollout_update_index")
        != ROLLOUT_UPDATE_INDEX
        or value.get("frozen_execution") != expected_execution
        or value.get("execution_now")
        != {
            "rollout_episode_slots": 0,
            "scheduled_rollout_ticks": 0,
            "counterfactual_in_memory_adam_steps": 0,
            "committed_optimizer_updates": 0,
            "formal_support_cells": 0,
            "locomotion_training_steps": 0,
            "deployable_graph_exports": 0,
            "robot_or_rdk_access": 0,
        }
    ):
        raise ValueError("Winner-v63 preregistration identity changed")
    sources = value.get("sources")
    if not isinstance(sources, Mapping) or not sources:
        raise ValueError("Winner-v63 source manifest is absent")
    for name, item in sources.items():
        if (
            set(item) != {"hash_mode", "path", "sha256"}
            or item["hash_mode"] != "lf"
            or lf_sha256(ROOT / item["path"]) != item["sha256"]
        ):
            raise ValueError(f"Winner-v63 source changed: {name}")
    if canonical_sha256(sources) != value.get("source_manifest_sha256"):
        raise ValueError("Winner-v63 source manifest changed")


def finite_tree(value: Any) -> bool:
    if isinstance(value, Mapping):
        return all(finite_tree(item) for item in value.values())
    if isinstance(value, (list, tuple)):
        return all(finite_tree(item) for item in value)
    if isinstance(value, (float, np.floating)):
        return math.isfinite(float(value))
    return True


def tree_copy(tree: Mapping[str, Any]) -> dict[str, np.ndarray]:
    return {key: np.asarray(value).copy() for key, value in tree.items()}


def tree_bit_exact(left: Mapping[str, Any], right: Mapping[str, Any]) -> bool:
    return set(left) == set(right) and all(
        np.array_equal(np.asarray(left[key]), np.asarray(right[key])) for key in left
    )


def scaled_tree(tree: Mapping[str, Any], scale: Any, jnp: Any) -> dict[str, Any]:
    scalar = jnp.asarray(scale, dtype=jnp.float32)
    return {
        key: jnp.asarray(value, dtype=jnp.float32) * scalar
        for key, value in tree.items()
    }


def add_trees(*trees: Mapping[str, Any], jnp: Any) -> dict[str, Any]:
    if not trees:
        raise ValueError("Winner-v63 cannot add an empty tree list")
    keys = set(trees[0])
    if any(set(tree) != keys for tree in trees[1:]):
        raise ValueError("Winner-v63 gradient tree keys changed")
    return {
        key: sum(
            (jnp.asarray(tree[key], dtype=jnp.float32) for tree in trees),
            start=jnp.zeros_like(jnp.asarray(trees[0][key], dtype=jnp.float32)),
        )
        for key in sorted(keys)
    }


def flattened(tree: Mapping[str, Any], keys: Sequence[str]) -> np.ndarray:
    return np.concatenate(
        [np.asarray(tree[key], dtype=np.float64).reshape(-1) for key in keys]
    )


def alignment(
    reference: Mapping[str, Any],
    component: Mapping[str, Any],
    keys: Sequence[str],
) -> dict[str, Any]:
    left = flattened(reference, keys)
    right = flattened(component, keys)
    dot = float(np.dot(left, right))
    left_norm = float(np.linalg.norm(left))
    right_norm = float(np.linalg.norm(right))
    cosine = None if left_norm == 0.0 or right_norm == 0.0 else dot / (left_norm * right_norm)
    return {
        "dot_product": dot,
        "reference_l2": left_norm,
        "component_l2": right_norm,
        "cosine": cosine,
        "gradient_descent_first_order_helps_reference": dot > 0.0,
        "gradient_descent_first_order_hurts_reference": dot < 0.0,
    }


def parameter_step_alignment(
    reference_gradient: Mapping[str, Any],
    before: Mapping[str, Any],
    after: Mapping[str, Any],
    keys: Sequence[str],
) -> dict[str, Any]:
    gradient = flattened(reference_gradient, keys)
    delta = flattened(
        {key: np.asarray(after[key]) - np.asarray(before[key]) for key in before},
        keys,
    )
    dot = float(np.dot(gradient, delta))
    gradient_norm = float(np.linalg.norm(gradient))
    delta_norm = float(np.linalg.norm(delta))
    cosine = (
        None
        if gradient_norm == 0.0 or delta_norm == 0.0
        else dot / (gradient_norm * delta_norm)
    )
    return {
        "directional_derivative": dot,
        "teacher_gradient_l2": gradient_norm,
        "parameter_delta_l2": delta_norm,
        "cosine_to_positive_teacher_gradient": cosine,
        "step_first_order_reduces_teacher_loss": dot < 0.0,
    }


def build_reset_batch(
    *,
    smoke: Any,
    gate: Any,
    mujoco: Any,
    scene: Path,
    by_id: Mapping[str, Mapping[str, Any]],
    table: Mapping[str, np.ndarray],
    calibrator_design: Mapping[str, Any],
    observer_type: type[Any],
    canonical_fit: Path,
) -> tuple[dict[str, np.ndarray], list[dict[str, str]]]:
    observations: list[np.ndarray] = []
    targets: list[np.ndarray] = []
    variants: list[int] = []
    identifiers: list[dict[str, str]] = []
    for configuration_id in TRAINING_TEACHER_IDS:
        raw_teacher = np.asarray(table[configuration_id], dtype=np.float32)
        target = smoke.bounded_action_numpy(
            raw_teacher, np.zeros((14,), dtype=np.float32)
        )
        for plant in smoke.PLANTS:
            episode = smoke.Episode(
                mujoco,
                scene,
                by_id[configuration_id],
                plant,
                calibrator_design,
                observer_type,
                canonical_fit,
            )
            raw = gate.ObservationTransport(None, None).observe(episode.observation())
            quantized = gate.native_quantize_observation(raw)
            for variant, observation in enumerate((raw, quantized)):
                observations.append(observation)
                targets.append(target)
                variants.append(variant)
                identifiers.append(
                    {
                        "configuration_id": configuration_id,
                        "plant": plant,
                        "variant": "raw" if variant == 0 else "native_quantized",
                    }
                )
    return (
        {
            "observations": np.asarray(observations, dtype=np.float32),
            "targets": np.asarray(targets, dtype=np.float32),
            "variant": np.asarray(variants, dtype=np.int32),
        },
        identifiers,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--training-work-root", type=Path, required=True)
    parser.add_argument("--teacher-snapshot", type=Path, required=True)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--canonical-fit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--markdown", type=Path)
    parser.add_argument("--offline-cpu-only", action="store_true")
    parser.add_argument("--conflict-attribution-authorized", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if not args.offline_cpu_only or not args.conflict_attribution_authorized:
        raise PermissionError(
            "Winner-v63 requires --offline-cpu-only "
            "--conflict-attribution-authorized"
        )
    if args.output.exists():
        raise FileExistsError(f"refusing to overwrite Winner-v63 result: {args.output}")
    markdown = args.markdown or args.output.with_suffix(".md")
    if markdown.exists():
        raise FileExistsError(f"refusing to overwrite Winner-v63 summary: {markdown}")

    import jax
    import jax.numpy as jnp
    import mujoco
    import run_winner_v50_full_action_teacher_source_gradient_contract as v50
    import run_winner_v62_residual_teacher_causal as v62
    import winner_v12_calibrator_training as training
    import winner_v15_pitch_margin_support as v15
    import winner_v20_joint_recurrent_support as v20
    import winner_v21_predictor_preserving_joint_support as v21
    import winner_v22_normalized_predictor as v22
    import winner_v22_normalized_predictor_v2 as v22v2
    import winner_v24_symmetric_support_failure as v24
    import winner_v24_symmetric_support_failure_v2 as v24v2
    import winner_v24_symmetric_support_failure_v3 as v24v3
    import winner_v29_prefix_right_pitch_anchor as v29
    import winner_v43_static_target_teacher as v43
    import winner_v49_full_action_static_target_teacher as v49
    import winner_v56_first_tick_teacher_mapping as v56
    import run_winner_v12_full_calibrator_training as full

    if jax.default_backend() != "cpu" or any(
        device.platform != "cpu" for device in jax.devices()
    ):
        raise ValueError("Winner-v63 requires CPU-only JAX")
    preregistration = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    validate_preregistration(preregistration)
    v60_result = json.loads(V60_RESULT.read_text(encoding="utf-8"))
    v62_result = json.loads(V62_RESULT.read_text(encoding="utf-8"))
    if (
        sha256(V60_RESULT) != preregistration["frozen_source"]["v60_result_sha256"]
        or sha256(V62_RESULT) != preregistration["frozen_source"]["v62_result_sha256"]
        or v62_result.get("decision")
        != "SELECT_NEXT_MECHANISM_FROM_FROZEN_RESIDUAL_CLASSIFICATION_ONLY"
        or v62_result.get("findings", {}).get("support_pass_counts", {}).get(
            "full_teacher"
        )
        != 13
    ):
        raise ValueError("Winner-v63 causal source changed")

    smoke, gate, v61 = v62.configure_v61_modules()
    final_receipt = next(
        row for row in v60_result["persistent_checkpoints"] if row["label"] == "final"
    )
    checkpoint_path, graph_path = v61.checkpoint_paths(args.training_work_root, "final")
    validate_artifact(checkpoint_path, final_receipt["snapshot"], "final snapshot")
    validate_artifact(graph_path, final_receipt["graph"], "final graph")
    snapshot = v61.load_snapshot_for_reviewed_gate(checkpoint_path)
    v61.validate_snapshot_for_reviewed_gate(snapshot)
    teacher_receipt = preregistration["frozen_source"]["teacher_snapshot"]
    validate_artifact(args.teacher_snapshot, teacher_receipt, "teacher snapshot")
    teacher = v22v2.load_snapshot(args.teacher_snapshot)
    if (
        int(np.asarray(snapshot["optimizer"]["count"])) != 554
        or int(np.asarray(teacher["optimizer"]["count"])) != 100
        or snapshot["metadata"].get("stage")
        != "integrated_first_tick_teacher_joint_stage2"
        or snapshot["metadata"].get("teacher_snapshot_sha256")
        != teacher_receipt["sha256"]
        or not np.array_equal(snapshot["target_mean"], teacher["target_mean"])
        or not np.array_equal(snapshot["target_std"], teacher["target_std"])
    ):
        raise ValueError("Winner-v63 snapshot boundary changed")

    if smoke.git_output(args.playground_root, "rev-parse", "HEAD") != smoke.CONTROL_COMMIT:
        raise ValueError("Winner-v63 Playground commit changed")
    smoke.validate_playground_tree(args.playground_root)
    if smoke.sha256(args.canonical_fit) != smoke.P30_FIT_LF_SHA256:
        raise ValueError("Winner-v63 canonical P30 fit changed")
    scene = args.playground_root / smoke.SCENE_RELATIVE
    observer_type = smoke.load_runtime_observer(args.canonical_fit)
    full_design = json.loads(FULL_PREREGISTRATION.read_text(encoding="utf-8"))
    calibrator_design = gate.load_calibrator_design(full_design)
    domain = json.loads(DOMAIN.read_text(encoding="utf-8"))
    matrix = domain["evaluation_matrix"]
    configurations = (
        matrix["fixed_anchors"] + matrix["discovery_samples"] + matrix["heldout_samples"]
    )
    by_id = {row["id"]: row for row in configurations}
    table = v43.load_teacher_table(json.loads(V42_RESULT.read_text(encoding="utf-8")))
    population = full.training_population(full_design, domain)
    identifiers = [str(row["id"]) for row in population]
    if (
        len(population) != 80
        or tuple(name for name in TRAINING_TEACHER_IDS if identifiers.count(name) != 2)
        or any(name in identifiers for name in HELDOUT_TEACHER_IDS)
    ):
        raise ValueError("Winner-v63 population changed")

    parameters = snapshot["parameters"]
    source_parameter_copy = tree_copy(parameters)
    source_optimizer_copy = {
        "count": np.asarray(snapshot["optimizer"]["count"]).copy(),
        "m": tree_copy(snapshot["optimizer"]["m"]),
        "v": tree_copy(snapshot["optimizer"]["v"]),
    }
    batch_np, episodes, _ = v20.stage2_rollout(
        smoke=smoke,
        full=full,
        training=training,
        mujoco=mujoco,
        scene=scene,
        population=population,
        preregistration=calibrator_design,
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
    failure_mask = v24.roll_pitch_failure_mask(
        episodes, shape=np.asarray(batch_np["rewards"]).shape
    )
    changed_keys = sorted(
        key
        for key in batch_np
        if not np.array_equal(np.asarray(batch_np[key]), objective_batch_np[key])
    )
    batch = {key: jnp.asarray(value) for key, value in objective_batch_np.items()}
    before = v21.joint_trainable_parameters(parameters)
    teacher_trainable = v21.joint_trainable_parameters(teacher["parameters"])
    target_mean = jnp.asarray(snapshot["target_mean"], dtype=jnp.float32)
    target_std = jnp.asarray(snapshot["target_std"], dtype=jnp.float32)
    reset_np, reset_identifiers = build_reset_batch(
        smoke=smoke,
        gate=gate,
        mujoco=mujoco,
        scene=scene,
        by_id=by_id,
        table=table,
        calibrator_design=calibrator_design,
        observer_type=observer_type,
        canonical_fit=args.canonical_fit,
    )
    reset_batch = {key: jnp.asarray(value) for key, value in reset_np.items()}

    def ppo_objective(values_tree: Mapping[str, Any]):
        return v20.joint_recurrent_ppo_loss(
            values_tree,
            batch,
            clip_epsilon=training.PPO_CLIP_EPSILON,
            value_coefficient=training.PPO_VALUE_COEFFICIENT,
            entropy_coefficient=training.PPO_ENTROPY_COEFFICIENT,
        )

    def predictor_objective(values_tree: Mapping[str, Any]):
        return v22.normalized_predictor_loss(
            values_tree, batch, target_mean, target_std
        )

    def anchor_objective(values_tree: Mapping[str, Any]):
        return v29.prefix_anchor_loss(
            values_tree, teacher_trainable, batch, anchor_mask
        )

    def teacher_objective(values_tree: Mapping[str, Any]):
        actions = v29.deterministic_bounded_actions(
            values_tree, batch["observations"], batch["previous_actions"]
        )[1]
        return v50.full_training_teacher_loss(
            actions,
            identifiers,
            batch_np["previous_actions"],
            batch_np["valid_mask"],
            table,
            jax,
            jnp,
        )

    def reset_objective(values_tree: Mapping[str, Any]):
        return v56.first_tick_teacher_loss(values_tree, reset_batch)

    (ppo_loss, ppo_metrics), ppo_gradient = jax.value_and_grad(
        ppo_objective, has_aux=True
    )(before)
    (predictor_loss, predictor_metrics), predictor_gradient = jax.value_and_grad(
        predictor_objective, has_aux=True
    )(before)
    (anchor_loss, anchor_metrics), anchor_gradient = jax.value_and_grad(
        anchor_objective, has_aux=True
    )(before)
    (teacher_loss, teacher_metrics), teacher_gradient = jax.value_and_grad(
        teacher_objective, has_aux=True
    )(before)
    (reset_loss, reset_metrics), reset_gradient = jax.value_and_grad(
        reset_objective, has_aux=True
    )(before)

    predictor_scaled = scaled_tree(
        predictor_gradient, v22v2.FROZEN_PREDICTOR_SCALE, jnp
    )
    anchor_scaled = scaled_tree(anchor_gradient, PREFIX_ANCHOR_SCALE, jnp)
    teacher_scaled = scaled_tree(teacher_gradient, v49.FULL_ACTION_TEACHER_SCALE, jnp)
    reset_scaled = scaled_tree(reset_gradient, v56.RESET_TEACHER_SCALE, jnp)
    ppo_predictor_composed = v22v2.compose_gradients(
        ppo_gradient, predictor_gradient
    )
    baseline_composed = v29.compose_gradients(
        ppo_predictor_composed,
        anchor_gradient,
        PREFIX_ANCHOR_SCALE,
        enabled=True,
    )
    full_horizon_composed = v29.compose_gradients(
        baseline_composed,
        teacher_gradient,
        v49.FULL_ACTION_TEACHER_SCALE,
        enabled=True,
    )
    composed = v29.compose_gradients(
        full_horizon_composed,
        reset_gradient,
        v56.RESET_TEACHER_SCALE,
        enabled=True,
    )
    other_gradient = add_trees(
        baseline_composed, reset_scaled, jnp=jnp
    )
    total_gradient = composed
    independently_composed = v29.compose_gradients(
        v29.compose_gradients(
            v22v2.compose_gradients(ppo_gradient, predictor_gradient),
            anchor_gradient,
            PREFIX_ANCHOR_SCALE,
            enabled=True,
        ),
        teacher_gradient,
        v49.FULL_ACTION_TEACHER_SCALE,
        enabled=True,
    )
    independently_composed = v29.compose_gradients(
        independently_composed,
        reset_gradient,
        v56.RESET_TEACHER_SCALE,
        enabled=True,
    )
    composition_exact = tree_bit_exact(total_gradient, independently_composed)

    integrated_after, integrated_optimizer = training.adam_step(
        before,
        total_gradient,
        snapshot["optimizer"],
        learning_rate=training.STAGE2_LEARNING_RATE,
        beta1=training.ADAM_BETA1,
        beta2=training.ADAM_BETA2,
        epsilon=training.ADAM_EPSILON,
    )
    integrated_after = training.clamp_stage2_parameters(integrated_after)
    teacher_after, teacher_optimizer = training.adam_step(
        before,
        teacher_scaled,
        snapshot["optimizer"],
        learning_rate=training.STAGE2_LEARNING_RATE,
        beta1=training.ADAM_BETA1,
        beta2=training.ADAM_BETA2,
        epsilon=training.ADAM_EPSILON,
    )
    teacher_after = training.clamp_stage2_parameters(teacher_after)
    integrated_teacher_loss = float(teacher_objective(integrated_after)[0])
    isolated_teacher_loss = float(teacher_objective(teacher_after)[0])
    teacher_loss_float = float(teacher_loss)

    policy_keys = tuple(v29.ANCHOR_GRADIENT_KEYS)
    recurrent_keys = tuple(v20.RECURRENT_CORE_KEYS)
    action_keys = tuple(training.DEPLOYABLE_ACTION_KEYS)
    alignments = {
        "policy": {
            "ppo": alignment(teacher_scaled, ppo_gradient, policy_keys),
            "predictor_scaled": alignment(
                teacher_scaled, predictor_scaled, policy_keys
            ),
            "prefix_anchor_scaled": alignment(
                teacher_scaled, anchor_scaled, policy_keys
            ),
            "first_tick_scaled": alignment(teacher_scaled, reset_scaled, policy_keys),
            "all_other_terms": alignment(teacher_scaled, other_gradient, policy_keys),
            "integrated_total": alignment(teacher_scaled, total_gradient, policy_keys),
        },
        "recurrent_core": {
            "all_other_terms": alignment(
                teacher_scaled, other_gradient, recurrent_keys
            ),
            "integrated_total": alignment(
                teacher_scaled, total_gradient, recurrent_keys
            ),
        },
        "action_head": {
            "all_other_terms": alignment(teacher_scaled, other_gradient, action_keys),
            "integrated_total": alignment(
                teacher_scaled, total_gradient, action_keys
            ),
        },
    }
    counterfactual = {
        "integrated": {
            "teacher_loss_before": teacher_loss_float,
            "teacher_loss_after": integrated_teacher_loss,
            "teacher_loss_delta": integrated_teacher_loss - teacher_loss_float,
            "step_alignment": parameter_step_alignment(
                teacher_scaled, before, integrated_after, policy_keys
            ),
            "returned_optimizer_count": int(np.asarray(integrated_optimizer["count"])),
        },
        "teacher_only_with_inherited_adam_state": {
            "teacher_loss_before": teacher_loss_float,
            "teacher_loss_after": isolated_teacher_loss,
            "teacher_loss_delta": isolated_teacher_loss - teacher_loss_float,
            "step_alignment": parameter_step_alignment(
                teacher_scaled, before, teacher_after, policy_keys
            ),
            "returned_optimizer_count": int(np.asarray(teacher_optimizer["count"])),
        },
    }
    other_dot = alignments["policy"]["all_other_terms"]["dot_product"]
    total_dot = alignments["policy"]["integrated_total"]["dot_product"]
    if isolated_teacher_loss >= teacher_loss_float:
        classification = "INHERITED_ADAM_STATE_BLOCKS_ISOLATED_TEACHER_DESCENT"
        next_mechanism = "PREREGISTER_FRESH_MOMENT_PERSISTENT_TEACHER_STEP_CONTRACT"
    elif integrated_teacher_loss >= teacher_loss_float:
        classification = "INTEGRATED_STEP_BLOCKS_PERSISTENT_TEACHER_DESCENT"
        next_mechanism = "PREREGISTER_ISOLATED_PERSISTENT_TEACHER_STEP_CONTRACT"
    elif other_dot < 0.0:
        classification = "OTHER_OBJECTIVES_OPPOSE_PERSISTENT_TEACHER_GRADIENT"
        next_mechanism = "PREREGISTER_CONFLICT_PROJECTED_PERSISTENT_TEACHER_STEP_CONTRACT"
    elif total_dot <= 0.0:
        classification = "TOTAL_GRADIENT_OPPOSES_PERSISTENT_TEACHER_GRADIENT"
        next_mechanism = "PREREGISTER_ISOLATED_PERSISTENT_TEACHER_STEP_CONTRACT"
    else:
        classification = "NO_LOCAL_OPTIMIZATION_CONFLICT"
        next_mechanism = "PREREGISTER_TEACHER_TRAJECTORY_PERSISTENT_PREFIX_CONTRACT"

    expected_stored = int(
        np.sum(
            batch_np["valid_transition_mask"][:, :-1]
            * batch_np["valid_mask"][:, 1:]
        )
    )
    source_unchanged = tree_bit_exact(parameters, source_parameter_copy) and (
        np.array_equal(
            np.asarray(snapshot["optimizer"]["count"]),
            source_optimizer_copy["count"],
        )
        and tree_bit_exact(snapshot["optimizer"]["m"], source_optimizer_copy["m"])
        and tree_bit_exact(snapshot["optimizer"]["v"], source_optimizer_copy["v"])
    )
    teacher_gradient_max = {
        key: float(np.max(np.abs(np.asarray(value))))
        for key, value in teacher_gradient.items()
    }
    checks = {
        "source_artifacts_exact": True,
        "cpu_only_environment_exact": True,
        "exact_80_episode_rollout_at_update_554": len(episodes) == 80,
        "episode_receipts_exact": bool(episode_hash),
        "action_boundary_exact": boundary["realized_equals_numpy_bit_exact"]
        and boundary["numpy_equals_jax_bit_exact"],
        "reward_and_failure_transition_rule_exact": reward["reward_formula_bit_exact"]
        and (
            (
                int(np.sum(failure_mask)) > 0
                and changed_keys == list(v24v2.MODIFIED_BATCH_KEYS)
                and objective_evidence["zero_failure_bit_exact_noop"] is False
            )
            or (
                int(np.sum(failure_mask)) == 0
                and changed_keys == []
                and objective_evidence["zero_failure_bit_exact_noop"] is True
            )
        ),
        "hidden_replay_within_v59_bound": float(
            ppo_metrics["sampled_hidden_replay_max_abs_error"]
        )
        <= 2.0e-6,
        "predictor_successors_present": int(
            predictor_metrics["stored_successor_transition_count"]
        )
        == expected_stored
        and expected_stored > 0,
        "anchor_elements_exact": int(anchor_metrics["selected_elements"])
        == v29.EXPECTED_ANCHOR_ELEMENTS,
        "full_teacher_elements_and_rows_exact": int(
            teacher_metrics["selected_elements"]
        )
        > 0
        and sum(identifiers.count(name) for name in TRAINING_TEACHER_IDS) == 22,
        "reset_batch_exact_and_heldout_absent": reset_np["observations"].shape
        == (44, 115)
        and reset_np["targets"].shape == (44, 14)
        and int(reset_metrics["selected_elements"]) == 616
        and not any(
            row["configuration_id"] in HELDOUT_TEACHER_IDS
            for row in reset_identifiers
        ),
        "teacher_gradient_policy_only": all(
            teacher_gradient_max[key] > 0.0 for key in policy_keys
        )
        and all(
            teacher_gradient_max[key] == 0.0
            for key in v29.NON_ANCHOR_GRADIENT_KEYS
        ),
        "composed_gradient_bit_exact": composition_exact,
        "all_losses_gradients_alignments_finite": finite_tree(
            {
                "ppo_loss": float(ppo_loss),
                "predictor_loss": float(predictor_loss),
                "anchor_loss": float(anchor_loss),
                "teacher_loss": teacher_loss_float,
                "reset_loss": float(reset_loss),
                "alignments": alignments,
                "counterfactual": counterfactual,
            }
        ),
        "counterfactual_counts_exact": int(
            np.asarray(integrated_optimizer["count"])
        )
        == 555
        and int(np.asarray(teacher_optimizer["count"])) == 555,
        "source_parameters_and_optimizer_unchanged": source_unchanged,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    valid = not failed
    result = {
        "schema_version": "winner_v63.persistent_teacher_conflict_result.v1",
        "status": (
            "PASS_WINNER_V63_PERSISTENT_TEACHER_CONFLICT_ATTRIBUTION"
            if valid
            else "INVALID_WINNER_V63_PERSISTENT_TEACHER_CONFLICT_ATTRIBUTION"
        ),
        "decision": next_mechanism if valid else "DO_NOT_SELECT_NEXT_POLICY_MECHANISM",
        "classification": classification if valid else None,
        "checks": checks,
        "failed_checks": failed,
        "rollout": {
            "update_index": ROLLOUT_UPDATE_INDEX,
            "episode_slots": len(episodes),
            "scheduled_ticks": 20000,
            "sampled_ticks": int(np.sum(batch_np["valid_mask"])),
            "valid_transition_count": int(np.sum(batch_np["valid_transition_mask"])),
            "roll_pitch_failure_count": int(np.sum(failure_mask)),
            "episode_receipts_sha256": episode_hash,
        },
        "losses": {
            "ppo": float(ppo_loss),
            "normalized_predictor": float(predictor_loss),
            "prefix_anchor": float(anchor_loss),
            "persistent_full_action_teacher": teacher_loss_float,
            "first_tick_teacher": float(reset_loss),
        },
        "gradient_alignment_to_persistent_teacher": alignments,
        "counterfactual_same_batch_steps": counterfactual,
        "gradient_max_abs": {
            "persistent_teacher": teacher_gradient_max,
            "integrated_total": {
                key: float(np.max(np.abs(np.asarray(value))))
                for key, value in total_gradient.items()
            },
        },
        "source": {
            "completed_updates": 554,
            "snapshot_sha256": sha256(checkpoint_path),
            "onnx_sha256": sha256(graph_path),
            "teacher_snapshot_sha256": sha256(args.teacher_snapshot),
        },
        "sources": {
            "preregistration_lf_sha256": lf_sha256(PREREGISTRATION),
            "runner_lf_sha256": lf_sha256(Path(__file__)),
            "v60_result_sha256": sha256(V60_RESULT),
            "v62_result_sha256": sha256(V62_RESULT),
        },
        "execution": {
            "rollout_episode_slots": len(episodes),
            "scheduled_rollout_ticks": 20000,
            "counterfactual_in_memory_adam_steps": 2,
            "committed_optimizer_updates": 0,
            "formal_support_cells": 0,
            "locomotion_training_steps": 0,
            "deployable_graph_exports": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "robot_clearance": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "result_authorizes_only": (
                "one separately preregistered CPU mechanism selected by the frozen classification"
            ),
        },
    }
    if not finite_tree(result):
        raise FloatingPointError("Winner-v63 result contains nonfinite values")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    markdown.write_text(
        "\n".join(
            [
                "# Winner-v63 persistent-teacher conflict attribution",
                "",
                f"- Status: `{result['status']}`",
                f"- Classification: `{result['classification']}`",
                f"- Decision: `{result['decision']}`",
                f"- Teacher loss before/integrated/isolated: `{teacher_loss_float} / {integrated_teacher_loss} / {isolated_teacher_loss}`",
                f"- Other-term teacher dot product: `{other_dot}`",
                f"- Integrated teacher dot product: `{total_dot}`",
                "- Committed optimizer / support / robot: `0 / 0 / 0`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(result["status"])
    print(json.dumps({
        "classification": result["classification"],
        "decision": result["decision"],
        "teacher_loss_before": teacher_loss_float,
        "teacher_loss_after_integrated": integrated_teacher_loss,
        "teacher_loss_after_isolated": isolated_teacher_loss,
        "other_dot": other_dot,
        "total_dot": total_dot,
    }, sort_keys=True))
    return 0 if valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
