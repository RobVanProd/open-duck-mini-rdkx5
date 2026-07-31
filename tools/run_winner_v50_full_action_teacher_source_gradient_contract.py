#!/usr/bin/env python3
"""Run the zero-update Winner-v50 source-gradient CPU proof."""

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
import run_winner_v44_static_target_teacher_source_gradient_contract as v44  # noqa: E402
import winner_v29_prefix_right_pitch_anchor as v29  # noqa: E402
import winner_v43_static_target_teacher as v43  # noqa: E402
import winner_v49_full_action_static_target_teacher as v49  # noqa: E402


CONTRACT = ANALYSIS / "winner_v50_full_action_teacher_source_gradient_contract.json"
V46_RESULT = ANALYSIS / "winner_v46_static_target_teacher_training_result.json"
V46_PREREGISTRATION = (
    ANALYSIS / "winner_v46_static_target_teacher_training_preregistration.json"
)
V22_RESULT = ANALYSIS / "winner_v22_normalized_predictor_training_result.json"
V42_RESULT = ANALYSIS / "winner_v42_static_target_teacher_table_result.json"
FULL_PREREGISTRATION = (
    ANALYSIS / "winner_v12_full_calibrator_training_preregistration.json"
)
DOMAIN = ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
ROLLOUT_UPDATE_INDEX = 352
PREFIX_ANCHOR_SCALE = np.float32(197.3112030029297)
COMPOSITION_TOLERANCE = 4.0e-6
TRAINING_TEACHER_IDS = v44.TRAINING_TEACHER_IDS
HELDOUT_TEACHER_IDS = v44.HELDOUT_TEACHER_IDS


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
        raise ValueError(f"Winner-v50 {label} artifact changed")


def tree_delta_max_abs(
    left: Mapping[str, Any], right: Mapping[str, Any]
) -> dict[str, float]:
    if set(left) != set(right):
        raise ValueError("Winner-v50 gradient tree keys changed")
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
    if (
        value.get("schema_version")
        != "winner_v50.full_action_teacher_source_gradient_contract.v1"
        or value.get("status")
        != "PREREGISTERED_WINNER_V50_FULL_ACTION_TEACHER_SOURCE_GRADIENT_CONTRACT"
        or value.get("decision")
        != "AUTHORIZE_ONE_ZERO_UPDATE_FULL_ACTION_SOURCE_GRADIENT_CPU_PROOF_ONLY"
        or value.get("source_selection", {}).get("selected_update") != 352
        or value.get("source_selection", {}).get("deployment_checkpoint_selected")
        is not False
        or value.get("objective", {}).get("rollout_update_index")
        != ROLLOUT_UPDATE_INDEX
        or value.get("objective", {}).get("new_supervised_indices")
        != list(v49.ACTION_INDICES)
        or value.get("objective", {}).get("new_teacher_scale")
        != float(v49.FULL_ACTION_TEACHER_SCALE)
        or value.get("execution_now")
        != {
            "rollout_episode_slots": 0,
            "scheduled_rollout_ticks": 0,
            "optimizer_updates": 0,
            "formal_support_cells": 0,
            "locomotion_training_steps": 0,
            "deployable_graph_exports": 0,
            "robot_or_rdk_access": 0,
        }
    ):
        raise ValueError("Winner-v50 contract changed")
    sources = value.get("sources")
    if not isinstance(sources, Mapping) or not sources:
        raise ValueError("Winner-v50 source manifest is absent")
    for name, item in sources.items():
        if item.get("hash_mode") != "lf" or lf_sha256(ROOT / item["path"]) != item.get("sha256"):
            raise ValueError(f"Winner-v50 source changed: {name}")
    if canonical_sha256(sources) != value.get("source_manifest_sha256"):
        raise ValueError("Winner-v50 source-manifest digest changed")


def build_full_training_teacher_batch(
    identifiers: list[str],
    previous_actions: Any,
    valid_mask: Any,
    table: Mapping[str, np.ndarray],
    jax: Any,
    jnp: Any,
) -> tuple[Any, Any, Any]:
    raw, bounded, old_mask = v44.build_training_teacher_batch(
        identifiers, previous_actions, valid_mask, table, jax, jnp
    )
    old_mask_np = np.asarray(old_mask, dtype=np.float32)
    valid = np.asarray(valid_mask, dtype=np.float32)
    mask = np.zeros_like(np.asarray(previous_actions, dtype=np.float32))
    selected = set(TRAINING_TEACHER_IDS)
    for environment, identifier in enumerate(identifiers):
        if identifier in selected:
            mask[environment, :, :] = valid[environment, :, None]
    if not np.array_equal(mask[..., np.asarray(v49.PITCH_ACTION_INDICES)], old_mask_np[..., np.asarray(v49.PITCH_ACTION_INDICES)]):
        raise ValueError("Winner-v50 full mask changed old pitch supervision")
    return raw, bounded, jnp.asarray(mask, dtype=jnp.float32)


def full_training_teacher_loss(
    candidate_actions: Any,
    identifiers: list[str],
    previous_actions: Any,
    valid_mask: Any,
    table: Mapping[str, np.ndarray],
    jax: Any,
    jnp: Any,
) -> tuple[Any, dict[str, Any]]:
    candidate = jnp.asarray(candidate_actions, dtype=jnp.float32)
    raw, bounded, mask = build_full_training_teacher_batch(
        identifiers, previous_actions, valid_mask, table, jax, jnp
    )
    error = candidate - bounded
    denominator = jnp.sum(mask)
    loss = jnp.sum(jnp.square(error) * mask) / denominator
    return loss, {
        "full_action_teacher_loss": loss,
        "selected_elements": denominator,
        "maximum_selected_action_delta": jnp.max(
            jnp.where(mask > 0.0, jnp.abs(error), jnp.float32(0.0))
        ),
        "raw_target_max_abs": jnp.max(jnp.abs(raw)),
        "bounded_target_max_abs": jnp.max(jnp.abs(bounded)),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--canonical-fit", type=Path, required=True)
    parser.add_argument("--v46-training-work-root", type=Path, required=True)
    parser.add_argument("--v22-training-work-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--offline-cpu-only", action="store_true")
    parser.add_argument("--source-gradient-proof-authorized", action="store_true")
    args = parser.parse_args()
    if not args.offline_cpu_only or not args.source_gradient_proof_authorized:
        raise PermissionError(
            "Winner-v50 requires --offline-cpu-only --source-gradient-proof-authorized"
        )
    if args.output.exists():
        raise FileExistsError(f"refusing to overwrite Winner-v50 result: {args.output}")

    import jax
    import jax.numpy as jnp
    import mujoco
    import run_winner_v12_calibrator_cpu_smoke as smoke
    import run_winner_v12_full_calibrator_training as full
    import run_winner_v22_normalized_predictor_support_gate as v22_gate
    import run_winner_v47_static_target_teacher_support_gate as v47
    import winner_v12_calibrator_training as training
    import winner_v15_pitch_margin_support as v15
    import winner_v20_joint_recurrent_support as v20
    import winner_v21_predictor_preserving_joint_support as v21
    import winner_v22_normalized_predictor as v22
    import winner_v22_normalized_predictor_v2 as v22v2
    import winner_v24_symmetric_support_failure as v24
    import winner_v24_symmetric_support_failure_v2 as v24v2
    import winner_v24_symmetric_support_failure_v3 as v24v3

    if jax.default_backend() != "cpu" or any(
        device.platform != "cpu" for device in jax.devices()
    ):
        raise ValueError("Winner-v50 requires CPU-only JAX")
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    validate_contract(contract)
    source_receipt = contract["artifact_inputs"]["winner_v46_final"]["snapshot"]
    graph_receipt = contract["artifact_inputs"]["winner_v46_final"]["graph"]
    teacher_receipt = contract["artifact_inputs"]["winner_v22_teacher_snapshot"]
    source_path = (
        args.v46_training_work_root
        / "snapshots/snapshot_static_target_teacher_update_352.npz"
    )
    graph_path = args.v46_training_work_root / "graphs/winner_v46_final.onnx"
    teacher_path = (
        args.v22_training_work_root
        / "snapshots/snapshot_normalized_predictor_update_100.npz"
    )
    validate_artifact(source_path, source_receipt, "V46 final snapshot")
    validate_artifact(graph_path, graph_receipt, "V46 final graph")
    validate_artifact(teacher_path, teacher_receipt, "V22 teacher snapshot")
    if smoke.sha256(args.canonical_fit) != smoke.P30_FIT_LF_SHA256:
        raise ValueError("Winner-v50 canonical P30 fit changed")
    if smoke.git_output(args.playground_root, "rev-parse", "HEAD") != smoke.CONTROL_COMMIT:
        raise ValueError("Winner-v50 Playground source changed")
    smoke.validate_playground_tree(args.playground_root)
    scene = args.playground_root / smoke.SCENE_RELATIVE

    source = v22v2.load_snapshot(source_path)
    teacher = v22v2.load_snapshot(teacher_path)
    v47.smoke = smoke
    v47.training = training
    v47.v21 = v21
    v47._TRAINING_PREREG = json.loads(
        V46_PREREGISTRATION.read_text(encoding="utf-8")
    )
    v47._validate_snapshot(source, expected_stage="static_target_teacher_joint_stage2")
    v22_gate.smoke = smoke
    v22_gate.training = training
    v22_gate.v21 = v21
    v22_gate._validate_snapshot(
        teacher, expected_stage="normalized_predictor_joint_stage2"
    )
    if (
        int(np.asarray(source["optimizer"]["count"])) != 352
        or int(np.asarray(teacher["optimizer"]["count"])) != 100
        or not np.array_equal(source["target_mean"], teacher["target_mean"])
        or not np.array_equal(source["target_std"], teacher["target_std"])
    ):
        raise ValueError("Winner-v50 source boundary changed")

    table = v43.load_teacher_table(json.loads(V42_RESULT.read_text(encoding="utf-8")))
    parameters = source["parameters"]
    parameter_copy = {key: np.asarray(value).copy() for key, value in parameters.items()}
    optimizer_copy = {
        "count": np.asarray(source["optimizer"]["count"]).copy(),
        "m": {key: np.asarray(value).copy() for key, value in source["optimizer"]["m"].items()},
        "v": {key: np.asarray(value).copy() for key, value in source["optimizer"]["v"].items()},
    }
    trainable = v21.joint_trainable_parameters(parameters)
    teacher_trainable = v21.joint_trainable_parameters(teacher["parameters"])
    target_mean = jnp.asarray(source["target_mean"], dtype=jnp.float32)
    target_std = jnp.asarray(source["target_std"], dtype=jnp.float32)
    population = full.training_population(
        json.loads(FULL_PREREGISTRATION.read_text(encoding="utf-8")),
        json.loads(DOMAIN.read_text(encoding="utf-8")),
    )
    identifiers = [str(row["id"]) for row in population]
    if (
        len(population) != 80
        or any(name in identifiers for name in HELDOUT_TEACHER_IDS)
        or any(identifiers.count(name) != 2 for name in TRAINING_TEACHER_IDS)
    ):
        raise ValueError("Winner-v50 teacher population changed")
    design = json.loads(smoke.CALIBRATOR_PREREG.read_text(encoding="utf-8"))
    observer_type = smoke.load_runtime_observer(args.canonical_fit)
    batch_np, episodes, _ = v20.stage2_rollout(
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
        key
        for key in batch_np
        if not np.array_equal(np.asarray(batch_np[key]), objective_batch_np[key])
    )
    failure_mask = v24.roll_pitch_failure_mask(
        episodes, shape=np.asarray(batch_np["rewards"]).shape
    )
    transition_copy = {
        key: np.asarray(value).copy() for key, value in objective_batch_np.items()
    }
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
        return v22.normalized_predictor_loss(
            values_tree, batch, target_mean, target_std
        )

    def anchor_objective(values_tree: Mapping[str, Any]):
        return v29.prefix_anchor_loss(
            values_tree, teacher_trainable, batch, anchor_mask
        )

    def actions_for(values_tree: Mapping[str, Any]):
        return v29.deterministic_bounded_actions(
            values_tree, batch["observations"], batch["previous_actions"]
        )[1]

    def pitch_teacher_objective(values_tree: Mapping[str, Any]):
        return v44.training_teacher_loss(
            actions_for(values_tree),
            identifiers,
            batch_np["previous_actions"],
            batch_np["valid_mask"],
            table,
            jax,
            jnp,
        )

    def full_teacher_objective(values_tree: Mapping[str, Any]):
        return full_training_teacher_loss(
            actions_for(values_tree),
            identifiers,
            batch_np["previous_actions"],
            batch_np["valid_mask"],
            table,
            jax,
            jnp,
        )

    (ppo_loss, ppo_metrics), ppo_gradients = jax.value_and_grad(
        ppo_objective, has_aux=True
    )(trainable)
    (predictor_loss, predictor_metrics), predictor_gradients = jax.value_and_grad(
        predictor_objective, has_aux=True
    )(trainable)
    (anchor_loss, anchor_metrics), anchor_gradients = jax.value_and_grad(
        anchor_objective, has_aux=True
    )(trainable)
    (pitch_loss, pitch_metrics), pitch_gradients = jax.value_and_grad(
        pitch_teacher_objective, has_aux=True
    )(trainable)
    (full_loss, full_metrics), full_gradients = jax.value_and_grad(
        full_teacher_objective, has_aux=True
    )(trainable)
    ppo_predictor = v22v2.compose_gradients(ppo_gradients, predictor_gradients)
    baseline_gradients = v29.compose_gradients(
        ppo_predictor,
        anchor_gradients,
        PREFIX_ANCHOR_SCALE,
        enabled=True,
    )
    old_gradients = v29.compose_gradients(
        baseline_gradients,
        pitch_gradients,
        v49.OLD_PITCH_TEACHER_SCALE,
        enabled=True,
    )
    new_gradients = v29.compose_gradients(
        baseline_gradients,
        full_gradients,
        v49.FULL_ACTION_TEACHER_SCALE,
        enabled=True,
    )
    disabled_gradients = v29.compose_gradients(
        old_gradients,
        full_gradients,
        v49.FULL_ACTION_TEACHER_SCALE,
        enabled=False,
    )

    def baseline_loss(values_tree: Mapping[str, Any]):
        current_ppo, _ = ppo_objective(values_tree)
        current_predictor, _ = predictor_objective(values_tree)
        current_anchor, _ = anchor_objective(values_tree)
        return (
            current_ppo
            + jnp.asarray(v22v2.FROZEN_PREDICTOR_SCALE) * current_predictor
            + jnp.asarray(PREFIX_ANCHOR_SCALE) * current_anchor
        )

    def old_total(values_tree: Mapping[str, Any]):
        current_pitch, _ = pitch_teacher_objective(values_tree)
        return baseline_loss(values_tree) + jnp.asarray(
            v49.OLD_PITCH_TEACHER_SCALE
        ) * current_pitch

    def new_total(values_tree: Mapping[str, Any]):
        current_full, _ = full_teacher_objective(values_tree)
        return baseline_loss(values_tree) + jnp.asarray(
            v49.FULL_ACTION_TEACHER_SCALE
        ) * current_full

    old_direct = jax.grad(old_total)(trainable)
    new_direct = jax.grad(new_total)(trainable)
    old_composition_error = max(
        tree_delta_max_abs(old_direct, old_gradients).values()
    )
    new_composition_error = max(
        tree_delta_max_abs(new_direct, new_gradients).values()
    )
    replacement_delta = tree_delta_max_abs(old_gradients, new_gradients)
    pitch_gradient_max = common.tree_max_abs(pitch_gradients)
    full_gradient_max = common.tree_max_abs(full_gradients)
    _, _, pitch_mask = v44.build_training_teacher_batch(
        identifiers,
        batch_np["previous_actions"],
        batch_np["valid_mask"],
        table,
        jax,
        jnp,
    )
    _, _, full_mask = build_full_training_teacher_batch(
        identifiers,
        batch_np["previous_actions"],
        batch_np["valid_mask"],
        table,
        jax,
        jnp,
    )
    pitch_mask_np = np.asarray(pitch_mask, dtype=np.float32)
    full_mask_np = np.asarray(full_mask, dtype=np.float32)
    selected_rows = int(np.sum(np.any(full_mask_np > 0.0, axis=(1, 2))))
    expected_stored = int(
        np.sum(
            batch_np["valid_transition_mask"][:, :-1]
            * batch_np["valid_mask"][:, 1:]
        )
    )
    transition_unchanged = all(
        np.array_equal(transition_copy[key], np.asarray(objective_batch_np[key]))
        for key in transition_copy
    )
    parameters_unchanged = all(
        np.array_equal(parameter_copy[key], np.asarray(parameters[key]))
        for key in parameter_copy
    )
    optimizer_unchanged = (
        np.array_equal(optimizer_copy["count"], np.asarray(source["optimizer"]["count"]))
        and all(
            np.array_equal(optimizer_copy[group][key], np.asarray(source["optimizer"][group][key]))
            for group in ("m", "v")
            for key in optimizer_copy[group]
        )
    )
    nonpolicy = v29.NON_ANCHOR_GRADIENT_KEYS
    policy = v29.ANCHOR_GRADIENT_KEYS
    checks = {
        "cpu_only_environment_exact": True,
        "v46_final_source_snapshot_graph_exact": True,
        "v22_teacher_snapshot_exact": True,
        "exact_80_episode_rollout_at_update_352": len(episodes) == 80,
        "episode_receipts_exact": bool(episode_hash),
        "action_boundary_exact": boundary["realized_equals_numpy_bit_exact"]
        and boundary["numpy_equals_jax_bit_exact"],
        "pitch_margin_reward_exact": reward["reward_formula_bit_exact"],
        "objective_transition_rule_exact": (
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
        "exact_22_training_teacher_configuration_plant_rows": selected_rows == 22,
        "heldout_teacher_rows_excluded": not any(
            name in identifiers for name in HELDOUT_TEACHER_IDS
        ),
        "full_mask_preserves_pitch_mask_bit_exact": np.array_equal(
            full_mask_np[..., np.asarray(v49.PITCH_ACTION_INDICES)],
            pitch_mask_np[..., np.asarray(v49.PITCH_ACTION_INDICES)],
        ),
        "full_mask_adds_all_valid_nonpitch_elements": np.array_equal(
            full_mask_np[..., np.asarray(v49.NONPITCH_ACTION_INDICES)],
            np.repeat(
                np.any(pitch_mask_np > 0.0, axis=2)[..., None],
                len(v49.NONPITCH_ACTION_INDICES),
                axis=2,
            ).astype(np.float32),
        ),
        "full_selected_elements_exact": int(full_metrics["selected_elements"])
        == int(np.sum(full_mask_np)),
        "old_selected_elements_exact": int(pitch_metrics["selected_elements"])
        == int(np.sum(pitch_mask_np)),
        "old_teacher_gradients_policy_only": all(
            pitch_gradient_max[key] > 0.0 for key in policy
        )
        and all(pitch_gradient_max[key] == 0.0 for key in nonpolicy),
        "full_teacher_gradients_policy_only": all(
            full_gradient_max[key] > 0.0 for key in policy
        )
        and all(full_gradient_max[key] == 0.0 for key in nonpolicy),
        "replacement_changes_all_policy_gradient_leaves": all(
            replacement_delta[key] > 0.0 for key in policy
        ),
        "replacement_preserves_nonpolicy_gradients_bit_exact": all(
            replacement_delta[key] == 0.0 for key in nonpolicy
        ),
        "default_off_old_gradient_bit_exact": all(
            np.array_equal(np.asarray(disabled_gradients[key]), np.asarray(old_gradients[key]))
            for key in old_gradients
        ),
        "old_direct_composition_at_most_4e_6": old_composition_error
        <= COMPOSITION_TOLERANCE,
        "new_direct_composition_at_most_4e_6": new_composition_error
        <= COMPOSITION_TOLERANCE,
        "ppo_hidden_replay_exact": float(
            ppo_metrics["sampled_hidden_replay_max_abs_error"]
        )
        <= 1.0e-6,
        "predictor_successors_present": int(
            predictor_metrics["stored_successor_transition_count"]
        )
        == expected_stored
        and expected_stored > 0,
        "anchor_elements_exact": int(anchor_metrics["selected_elements"])
        == v29.EXPECTED_ANCHOR_ELEMENTS,
        "transition_arrays_unchanged": transition_unchanged,
        "parameters_and_optimizer_unchanged": parameters_unchanged
        and optimizer_unchanged,
        "all_losses_metrics_gradients_finite": training.finite_tree(
            {
                "ppo_loss": ppo_loss,
                "predictor_loss": predictor_loss,
                "anchor_loss": anchor_loss,
                "pitch_loss": pitch_loss,
                "full_loss": full_loss,
                "old_gradients": old_gradients,
                "new_gradients": new_gradients,
            }
        )
        and all(
            math.isfinite(value)
            for value in (old_composition_error, new_composition_error)
        ),
        "optimizer_updates_zero": True,
        "formal_support_cells_zero": True,
        "locomotion_training_steps_zero": True,
        "deployable_graph_exports_zero": True,
        "robot_or_rdk_access_zero": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    passed = not failed
    result = {
        "schema_version": "winner_v50.full_action_teacher_source_gradient_result.v1",
        "status": (
            "PASS_WINNER_V50_FULL_ACTION_TEACHER_SOURCE_GRADIENT_CPU_PROOF"
            if passed
            else "HOLD_WINNER_V50_FULL_ACTION_TEACHER_SOURCE_GRADIENT_CPU_PROOF"
        ),
        "decision": (
            "AUTHORIZE_FULL_ACTION_TEACHER_ONE_UPDATE_CPU_PREREGISTRATION_ONLY"
            if passed
            else "DO_NOT_UPDATE_FULL_ACTION_TEACHER_POLICY"
        ),
        "checks": checks,
        "failed_checks": failed,
        "source_identity": {
            "completed_updates": 352,
            "snapshot_sha256": sha256(source_path),
            "graph_sha256": sha256(graph_path),
            "teacher_snapshot_sha256": sha256(teacher_path),
        },
        "rollout_evidence": {
            "update_index": ROLLOUT_UPDATE_INDEX,
            "episode_slots": len(episodes),
            "scheduled_ticks": len(episodes) * 250,
            "episode_receipts_sha256": episode_hash,
            "sampled_ticks": int(np.sum(batch_np["valid_mask"])),
            "valid_transition_count": int(
                np.sum(batch_np["valid_transition_mask"])
            ),
            "roll_pitch_failure_count": int(np.sum(failure_mask)),
        },
        "objective_evidence": {
            "ppo_loss": float(ppo_loss),
            "normalized_predictor_loss": float(predictor_loss),
            "prefix_anchor_loss": float(anchor_loss),
            "old_pitch_teacher_loss": float(pitch_loss),
            "full_action_teacher_loss": float(full_loss),
            "old_pitch_teacher_scale": float(v49.OLD_PITCH_TEACHER_SCALE),
            "full_action_teacher_scale": float(v49.FULL_ACTION_TEACHER_SCALE),
            "old_selected_elements": int(pitch_metrics["selected_elements"]),
            "full_selected_elements": int(full_metrics["selected_elements"]),
            "old_direct_composition_max_abs_error": old_composition_error,
            "new_direct_composition_max_abs_error": new_composition_error,
            "replacement_leaf_max_abs_delta": replacement_delta,
            "old_teacher_gradient_max_abs": pitch_gradient_max,
            "full_teacher_gradient_max_abs": full_gradient_max,
        },
        "execution": {
            "rollout_episode_slots": len(episodes),
            "scheduled_rollout_ticks": len(episodes) * 250,
            "optimizer_updates": 0,
            "formal_support_cells": 0,
            "locomotion_training_steps": 0,
            "deployable_graph_exports": 0,
            "robot_or_rdk_access": 0,
        },
        "sources": contract["sources"],
        "source_manifest_sha256": contract["source_manifest_sha256"],
        "authority": {
            "one_update_authorized": False,
            "training_authorized": False,
            "robot_clearance": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "pass_authorizes_only": "one separately preregistered CPU-only one-update proof",
        },
    }
    args.output.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(result["status"])
    if failed:
        print(json.dumps(failed))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
