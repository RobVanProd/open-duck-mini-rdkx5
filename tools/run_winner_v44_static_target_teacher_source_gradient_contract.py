#!/usr/bin/env python3
"""Run the zero-update Winner-v44 source-gradient CPU proof."""

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
import winner_v29_prefix_right_pitch_anchor as v29  # noqa: E402
import winner_v43_static_target_teacher as v43  # noqa: E402


CONTRACT = ANALYSIS / "winner_v44_static_target_teacher_source_gradient_contract.json"
V22_RESULT = ANALYSIS / "winner_v22_normalized_predictor_training_result.json"
V32_PREREG = ANALYSIS / "winner_v32_prefix_right_pitch_anchor_training_preregistration.json"
V32_RESULT = ANALYSIS / "winner_v32_prefix_right_pitch_anchor_training_result.json"
V42_RESULT = ANALYSIS / "winner_v42_static_target_teacher_table_result.json"
V43_RESULT = ANALYSIS / "winner_v43_static_target_teacher_abi_cpu_result.json"
FULL_PREREG = ANALYSIS / "winner_v12_full_calibrator_training_preregistration.json"
DOMAIN = ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
ROLLOUT_UPDATE_INDEX = 251
PREFIX_ANCHOR_SCALE = np.float32(197.3112030029297)
COMPOSITION_TOLERANCE = 4.0e-6
BALANCE_RELATIVE_TOLERANCE = 2.0e-6
TRAINING_TEACHER_IDS = (
    "COM_X_NEG", "COM_CORNER_00", "COM_CORNER_01", "COM_CORNER_02",
    "COM_CORNER_03", "OPTIONAL_AGGREGATE_HEAVY_AFT", "DISCOVERY_02",
    "DISCOVERY_03", "DISCOVERY_06", "DISCOVERY_09", "DISCOVERY_10",
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
        raise ValueError("Winner-v44 gradient tree schema changed")
    return {
        key: float(
            np.max(
                np.abs(
                    np.asarray(left[key], dtype=np.float64)
                    - np.asarray(right[key], dtype=np.float64)
                )
            )
        )
        for key in left
    }


def validate_artifact(path: Path, receipt: Mapping[str, Any], label: str) -> None:
    if (
        not path.is_file()
        or path.stat().st_size != int(receipt["bytes"])
        or sha256(path) != receipt["sha256"]
    ):
        raise ValueError(f"Winner-v44 {label} artifact changed")


def validate_contract(value: Mapping[str, Any]) -> None:
    if (
        value.get("schema_version")
        != "winner_v44.static_target_teacher_source_gradient_contract.v1"
        or value.get("status")
        != "PREREGISTERED_WINNER_V44_STATIC_TARGET_TEACHER_SOURCE_GRADIENT_CONTRACT"
        or value.get("decision")
        != "AUTHORIZE_ONE_ZERO_UPDATE_SOURCE_GRADIENT_CPU_PROOF_ONLY"
    ):
        raise ValueError("Winner-v44 contract identity changed")
    if value.get("source_selection") != {
        "candidate_checkpoints": {
            "half": {"passes": 99, "failures": 25, "cells": 124},
            "final": {"passes": 94, "failures": 30, "cells": 124},
        },
        "rule": "fewest failures over the identical 124-cell Winner-v33 gate; tie chooses earlier update",
        "selected_label": "half",
        "selected_update": 251,
        "selected_snapshot": value["artifact_inputs"]["winner_v32"]["half"]["snapshot"],
        "selected_graph": value["artifact_inputs"]["winner_v32"]["half"]["graph"],
        "scope": "training-continuation source only, not deployment checkpoint selection",
    }:
        raise ValueError("Winner-v44 source selection changed")
    objective = value.get("objective", {})
    if (
        objective.get("rollout_update_index") != ROLLOUT_UPDATE_INDEX
        or objective.get("episode_slots") != 80
        or objective.get("ticks_per_slot") != 250
        or objective.get("teacher_configuration_ids") != list(TRAINING_TEACHER_IDS)
        or objective.get("heldout_teacher_configuration_ids_excluded")
        != list(HELDOUT_TEACHER_IDS)
        or objective.get("teacher_configuration_rows") != 22
        or objective.get("teacher_action_indices") != list(v43.PITCH_ACTION_INDICES)
        or objective.get("default_off")
        != "baseline gradients and all rollout transition arrays bit-exact"
        or objective.get("no_action_replacement") is not True
        or objective.get("unit_scale_carried_from_v43") is not False
    ):
        raise ValueError("Winner-v44 objective changed")
    if value.get("execution_now") != {
        "rollout_episode_slots": 0,
        "scheduled_rollout_ticks": 0,
        "optimizer_updates": 0,
        "formal_support_cells": 0,
        "locomotion_training_steps": 0,
        "deployable_graph_exports": 0,
        "robot_or_rdk_access": 0,
    } or value.get("authority") != {
        "robot_clearance": False,
        "training_authorized": False,
        "one_update_authorized": False,
        "runtime_implementation_authorized": False,
        "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
        "pass_authorizes_only": (
            "one separately preregistered CPU-only one-update proof using the exact recorded scale"
        ),
    }:
        raise ValueError("Winner-v44 execution authority changed")
    sources = value.get("sources")
    if not isinstance(sources, dict) or not sources:
        raise ValueError("Winner-v44 source manifest is absent")
    for name, item in sources.items():
        if item.get("hash_mode") != "lf" or lf_sha256(ROOT / item["path"]) != item.get("sha256"):
            raise ValueError(f"Winner-v44 source changed: {name}")
    if canonical_sha256(sources) != value.get("source_manifest_sha256"):
        raise ValueError("Winner-v44 source manifest changed")


def build_training_teacher_batch(
    identifiers: list[str], previous_actions: Any, valid_mask: Any,
    table: Mapping[str, np.ndarray], jax: Any, jnp: Any,
) -> tuple[Any, Any, Any]:
    previous = jnp.asarray(previous_actions, dtype=jnp.float32)
    valid = np.asarray(valid_mask, dtype=np.float32)
    if previous.ndim != 3 or previous.shape[-1] != 14 or valid.shape != previous.shape[:2]:
        raise ValueError("Winner-v44 training teacher batch shape changed")
    if len(identifiers) != previous.shape[0]:
        raise ValueError("Winner-v44 training teacher population changed")
    if any(identifiers.count(name) != 2 for name in TRAINING_TEACHER_IDS):
        raise ValueError("Winner-v44 training teacher rows are not two-plant pairs")
    if any(name in identifiers for name in HELDOUT_TEACHER_IDS):
        raise ValueError("Winner-v44 heldout teacher label leaked into training")
    if set(table) != set(v43.CONFIGURATION_IDS):
        raise ValueError("Winner-v44 teacher table changed")
    raw = np.zeros(previous.shape, dtype=np.float32)
    mask = np.zeros(previous.shape, dtype=np.float32)
    pitch = np.asarray(v43.PITCH_ACTION_INDICES, dtype=np.int64)
    selected = set(TRAINING_TEACHER_IDS)
    for environment, identifier in enumerate(identifiers):
        if identifier not in selected:
            continue
        raw[environment, :, :] = table[identifier]
        mask[environment][:, pitch] = valid[environment, :, None]
    raw_jax = jax.lax.stop_gradient(jnp.asarray(raw, dtype=jnp.float32))
    bounded = jax.lax.stop_gradient(
        v43.training.bounded_action(raw_jax, previous)
    )
    return raw_jax, bounded, jnp.asarray(mask, dtype=jnp.float32)


def training_teacher_loss(
    candidate_actions: Any, identifiers: list[str], previous_actions: Any,
    valid_mask: Any, table: Mapping[str, np.ndarray], jax: Any, jnp: Any,
) -> tuple[Any, dict[str, Any]]:
    candidate = jnp.asarray(candidate_actions, dtype=jnp.float32)
    raw, bounded, mask = build_training_teacher_batch(
        identifiers, previous_actions, valid_mask, table, jax, jnp
    )
    if candidate.shape != bounded.shape:
        raise ValueError("Winner-v44 candidate action shape changed")
    denominator = jnp.sum(mask)
    error = candidate - bounded
    selected_abs = jnp.where(mask > 0.0, jnp.abs(error), jnp.float32(0.0))
    loss = jnp.sum(jnp.square(error) * mask) / denominator
    return loss, {
        "static_target_teacher_loss": loss,
        "selected_elements": denominator,
        "maximum_selected_action_delta": jnp.max(selected_abs),
        "raw_target_max_abs": jnp.max(jnp.abs(raw)),
        "bounded_target_max_abs": jnp.max(jnp.abs(bounded)),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--canonical-fit", type=Path, required=True)
    parser.add_argument("--v32-training-work-root", type=Path, required=True)
    parser.add_argument("--v22-training-work-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--offline-cpu-only", action="store_true")
    parser.add_argument("--source-gradient-proof-authorized", action="store_true")
    args = parser.parse_args()
    if not args.offline_cpu_only or not args.source_gradient_proof_authorized:
        raise PermissionError(
            "Winner-v44 requires --offline-cpu-only --source-gradient-proof-authorized"
        )
    if args.output.exists():
        raise FileExistsError("refusing to overwrite Winner-v44 result")

    import jax
    import jax.numpy as jnp
    import mujoco
    import run_winner_v12_calibrator_cpu_smoke as smoke
    import run_winner_v12_full_calibrator_training as full
    import run_winner_v22_normalized_predictor_support_gate as v22_gate
    import run_winner_v33_prefix_right_pitch_anchor_support_gate as v33_gate
    import winner_v12_calibrator_training as training
    import winner_v15_pitch_margin_support as v15
    import winner_v20_joint_recurrent_support as v20
    import winner_v21_predictor_preserving_joint_support as v21
    import winner_v22_normalized_predictor as v22
    import winner_v22_normalized_predictor_v2 as v22v2
    import winner_v24_symmetric_support_failure as v24
    import winner_v24_symmetric_support_failure_v2 as v24v2
    import winner_v24_symmetric_support_failure_v3 as v24v3

    if jax.default_backend() != "cpu" or any(device.platform != "cpu" for device in jax.devices()):
        raise ValueError("Winner-v44 requires CPU-only JAX")
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    validate_contract(contract)
    v43_result = json.loads(V43_RESULT.read_text(encoding="utf-8"))
    if (
        v43_result.get("status") != "PASS_WINNER_V43_STATIC_TARGET_TEACHER_ABI_CPU_CONTRACT"
        or v43_result.get("decision")
        != "AUTHORIZE_STATIC_TARGET_TEACHER_SOURCE_GRADIENT_CPU_CONTRACT_ONLY"
    ):
        raise ValueError("Winner-v43 does not authorize Winner-v44")
    table = v43.load_teacher_table(
        json.loads(V42_RESULT.read_text(encoding="utf-8"))
    )
    artifact_inputs = contract["artifact_inputs"]
    source_snapshot_path = (
        args.v32_training_work_root
        / "snapshots/snapshot_prefix_anchor_update_251.npz"
    )
    source_graph_path = args.v32_training_work_root / "graphs/winner_v32_half.onnx"
    teacher_snapshot_path = (
        args.v22_training_work_root
        / "snapshots/snapshot_normalized_predictor_update_100.npz"
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
    if smoke.sha256(args.canonical_fit) != smoke.P30_FIT_LF_SHA256:
        raise ValueError("Winner-v44 canonical P30 fit changed")
    if smoke.git_output(args.playground_root, "rev-parse", "HEAD") != smoke.CONTROL_COMMIT:
        raise ValueError("Winner-v44 Playground source changed")
    smoke.validate_playground_tree(args.playground_root)
    scene = args.playground_root / smoke.SCENE_RELATIVE

    source = v22v2.load_snapshot(source_snapshot_path)
    teacher = v22v2.load_snapshot(teacher_snapshot_path)
    v33_gate.smoke = smoke
    v33_gate.training = training
    v33_gate.v21 = v21
    v33_gate._TRAINING_PREREG = json.loads(V32_PREREG.read_text(encoding="utf-8"))
    v33_gate._validate_snapshot(
        source, expected_stage="prefix_right_pitch_anchor_joint_stage2"
    )
    v22_gate.smoke = smoke
    v22_gate.training = training
    v22_gate.v21 = v21
    v22_gate._validate_snapshot(
        teacher, expected_stage="normalized_predictor_joint_stage2"
    )
    if not np.array_equal(source["target_mean"], teacher["target_mean"]) or not np.array_equal(
        source["target_std"], teacher["target_std"]
    ):
        raise ValueError("Winner-v44 predictor target normalization changed")

    parameters = source["parameters"]
    parameters_copy = {key: np.asarray(value).copy() for key, value in parameters.items()}
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
        json.loads(FULL_PREREG.read_text(encoding="utf-8")),
        json.loads(DOMAIN.read_text(encoding="utf-8")),
    )
    identifiers = [str(row["id"]) for row in population]
    if len(population) != 80:
        raise ValueError("Winner-v44 training population changed")
    design = json.loads(smoke.CALIBRATOR_PREREG.read_text(encoding="utf-8"))
    observer_type = smoke.load_runtime_observer(args.canonical_fit)
    batch_np, episodes, _ = v20.stage2_rollout(
        smoke=smoke, full=full, training=training, mujoco=mujoco, scene=scene,
        population=population, preregistration=design, observer_type=observer_type,
        canonical_fit=args.canonical_fit, parameters=parameters,
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
        batch_np, episodes, np.asarray(values, dtype=np.float32),
        gamma=training.PPO_GAMMA, gae_lambda=training.PPO_GAE_LAMBDA,
    )
    changed_keys = sorted(
        key for key in batch_np
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
            values_tree, batch, clip_epsilon=training.PPO_CLIP_EPSILON,
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
        return training_teacher_loss(
            candidate_actions, identifiers, batch_np["previous_actions"],
            batch_np["valid_mask"], table, jax, jnp,
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
    (teacher_loss, teacher_metrics), teacher_gradients = jax.value_and_grad(
        teacher_objective, has_aux=True
    )(trainable)
    ppo_predictor_gradients = v22v2.compose_gradients(
        ppo_gradients, predictor_gradients
    )
    baseline_gradients = v29.compose_gradients(
        ppo_predictor_gradients, anchor_gradients,
        PREFIX_ANCHOR_SCALE, enabled=True,
    )
    teacher_scale, balance = v29.gradient_balance_scale(
        baseline_gradients, teacher_gradients
    )
    disabled_gradients = v29.compose_gradients(
        baseline_gradients, teacher_gradients, teacher_scale, enabled=False
    )
    enabled_gradients = v29.compose_gradients(
        baseline_gradients, teacher_gradients, teacher_scale, enabled=True
    )

    def baseline_total(values_tree: Mapping[str, Any]) -> Any:
        current_ppo, _ = ppo_objective(values_tree)
        current_predictor, _ = predictor_objective(values_tree)
        current_anchor, _ = anchor_objective(values_tree)
        return (
            current_ppo
            + jnp.asarray(v22v2.FROZEN_PREDICTOR_SCALE, dtype=jnp.float32)
            * current_predictor
            + jnp.asarray(PREFIX_ANCHOR_SCALE, dtype=jnp.float32) * current_anchor
        )

    def enabled_total(values_tree: Mapping[str, Any]) -> Any:
        current_teacher, _ = teacher_objective(values_tree)
        return baseline_total(values_tree) + jnp.asarray(
            teacher_scale, dtype=jnp.float32
        ) * current_teacher

    direct_baseline_gradients = jax.grad(baseline_total)(trainable)
    direct_enabled_gradients = jax.grad(enabled_total)(trainable)
    baseline_composition_delta = tree_delta_max_abs(
        baseline_gradients, direct_baseline_gradients
    )
    enabled_composition_delta = tree_delta_max_abs(
        enabled_gradients, direct_enabled_gradients
    )
    disabled_delta = tree_delta_max_abs(baseline_gradients, disabled_gradients)
    enabled_delta = tree_delta_max_abs(baseline_gradients, enabled_gradients)
    teacher_max = common.tree_max_abs(teacher_gradients)
    raw_teacher, bounded_teacher, teacher_mask = build_training_teacher_batch(
        identifiers, batch_np["previous_actions"], batch_np["valid_mask"],
        table, jax, jnp,
    )
    teacher_mask_np = np.asarray(teacher_mask, dtype=np.float32)
    selected_rows = int(np.sum(np.any(teacher_mask_np > 0.0, axis=(1, 2))))
    selected_elements = int(np.sum(teacher_mask_np))
    scaled_balance_error = abs(
        balance["scaled_anchor_policy_gradient_rms"]
        - balance["baseline_policy_gradient_rms"]
    ) / balance["baseline_policy_gradient_rms"]
    transitions_unchanged = all(
        np.array_equal(transition_copy[key], objective_batch_np[key])
        for key in transition_copy
    )
    parameters_unchanged = all(
        np.array_equal(parameters_copy[key], np.asarray(parameters[key]))
        for key in parameters_copy
    )
    optimizer_unchanged = (
        np.array_equal(optimizer_copy["count"], source["optimizer"]["count"])
        and common.tree_equal(optimizer_copy["m"], source["optimizer"]["m"])
        and common.tree_equal(optimizer_copy["v"], source["optimizer"]["v"])
    )
    expected_stored = int(
        np.sum(
            batch_np["valid_transition_mask"][:, :-1]
            * batch_np["valid_mask"][:, 1:]
        )
    )
    policy_keys = set(v29.ANCHOR_GRADIENT_KEYS)
    nonpolicy_keys = set(v29.NON_ANCHOR_GRADIENT_KEYS)
    all_numeric = [
        float(ppo_loss), float(predictor_loss), float(anchor_loss),
        float(teacher_loss), float(teacher_scale), scaled_balance_error,
        *balance.values(), *teacher_max.values(), *baseline_composition_delta.values(),
        *enabled_composition_delta.values(), *disabled_delta.values(), *enabled_delta.values(),
    ]
    checks = {
        "cpu_only_environment_exact": True,
        "winner_v32_half_source_snapshot_and_graph_exact": True,
        "winner_v22_teacher_snapshot_exact": True,
        "source_selection_99_of_124_over_94_of_124_exact": True,
        "target_normalizer_bit_exact": True,
        "exact_80_episode_rollout_at_update_251": len(episodes) == 80,
        "episode_receipts_exact": bool(episode_hash),
        "action_boundary_exact": boundary["realized_equals_numpy_bit_exact"]
        and boundary["numpy_equals_jax_bit_exact"],
        "pitch_margin_reward_exact": reward["reward_formula_bit_exact"],
        "winner_v32_baseline_objective_transition_exact": (
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
        "heldout_teacher_configuration_rows_excluded": all(
            name not in identifiers for name in HELDOUT_TEACHER_IDS
        ),
        "teacher_mask_has_valid_pitch_elements_only": selected_elements > 0
        and np.all(
            teacher_mask_np[..., sorted(set(range(14)) - set(v43.PITCH_ACTION_INDICES))]
            == 0.0
        ),
        "teacher_loss_finite_nonzero": math.isfinite(float(teacher_loss))
        and float(teacher_loss) > 0.0,
        "teacher_gradients_nonzero_on_all_six_policy_leaves": all(
            teacher_max[key] > 0.0 for key in policy_keys
        ),
        "teacher_gradients_zero_on_value_logstd_predictor_leaves": all(
            teacher_max[key] == 0.0 for key in nonpolicy_keys
        ),
        "baseline_composed_matches_direct_at_most_4e_6": max(
            baseline_composition_delta.values()
        ) <= COMPOSITION_TOLERANCE,
        "teacher_scale_finite_positive": math.isfinite(float(teacher_scale))
        and float(teacher_scale) > 0.0,
        "scaled_teacher_rms_matches_baseline_at_most_2e_6_relative": (
            scaled_balance_error <= BALANCE_RELATIVE_TOLERANCE
        ),
        "default_off_combined_gradient_bit_exact": max(disabled_delta.values()) == 0.0,
        "enabled_changes_all_six_policy_gradient_leaves": all(
            enabled_delta[key] > 0.0 for key in policy_keys
        ),
        "enabled_preserves_nonpolicy_gradients_bit_exact": all(
            enabled_delta[key] == 0.0 for key in nonpolicy_keys
        ),
        "enabled_direct_loss_gradient_matches_composition_at_most_4e_6": max(
            enabled_composition_delta.values()
        ) <= COMPOSITION_TOLERANCE,
        "predictor_metrics_finite_and_successors_present": training.finite_tree(
            predictor_metrics
        ) and int(predictor_metrics["stored_successor_transition_count"]) == expected_stored
        and expected_stored > 0,
        "ppo_metrics_finite_and_hidden_replay_exact": training.finite_tree(ppo_metrics)
        and float(ppo_metrics["sampled_hidden_replay_max_abs_error"]) <= 1.0e-6,
        "prefix_anchor_metrics_finite_and_exact": training.finite_tree(anchor_metrics)
        and int(anchor_metrics["selected_elements"]) == v29.EXPECTED_ANCHOR_ELEMENTS,
        "teacher_metrics_finite_and_mask_exact": training.finite_tree(teacher_metrics)
        and int(teacher_metrics["selected_elements"]) == selected_elements,
        "all_losses_metrics_gradients_finite": all(math.isfinite(value) for value in all_numeric),
        "transition_arrays_unchanged_by_teacher": transitions_unchanged,
        "parameters_and_optimizer_unchanged_no_update": parameters_unchanged
        and optimizer_unchanged,
        "optimizer_updates_zero": True,
        "formal_support_cells_zero": True,
        "locomotion_training_steps_zero": True,
        "deployable_graph_exports_zero": True,
        "robot_or_rdk_access_zero": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    passed = not failed
    result = {
        "schema_version": "winner_v44.static_target_teacher_source_gradient_result.v1",
        "status": (
            "PASS_WINNER_V44_STATIC_TARGET_TEACHER_SOURCE_GRADIENT_CONTRACT"
            if passed else "HOLD_WINNER_V44_STATIC_TARGET_TEACHER_SOURCE_GRADIENT_CONTRACT"
        ),
        "decision": (
            "AUTHORIZE_ONE_UPDATE_STATIC_TARGET_TEACHER_CPU_PROOF_PREREGISTRATION_ONLY"
            if passed else "DO_NOT_RUN_STATIC_TARGET_TEACHER_UPDATE"
        ),
        "checks": checks,
        "failed_checks": failed,
        "source_identity": {
            "label": "half", "completed_updates": 251,
            "snapshot": artifact_inputs["winner_v32"]["half"]["snapshot"],
            "graph": artifact_inputs["winner_v32"]["half"]["graph"],
            "teacher_snapshot": artifact_inputs["winner_v22"]["snapshot"],
        },
        "rollout_evidence": {
            "rollout_update_index": ROLLOUT_UPDATE_INDEX,
            "episode_slots": len(episodes),
            "episode_receipts_sha256": episode_hash,
            "roll_pitch_failure_count": int(np.sum(failure_mask)),
            "selected_teacher_rows": selected_rows,
            "selected_teacher_elements": selected_elements,
            "observations_sha256": array_sha256(batch_np["observations"]),
            "previous_actions_sha256": array_sha256(batch_np["previous_actions"]),
            "teacher_raw_targets_sha256": array_sha256(np.asarray(raw_teacher)),
            "teacher_bounded_targets_sha256": array_sha256(np.asarray(bounded_teacher)),
            "teacher_mask_sha256": array_sha256(teacher_mask_np),
        },
        "objective_evidence": {
            "ppo_loss": float(ppo_loss),
            "normalized_predictor_loss": float(predictor_loss),
            "prefix_anchor_loss": float(anchor_loss),
            "static_target_teacher_loss": float(teacher_loss),
            "predictor_scale": float(v22v2.FROZEN_PREDICTOR_SCALE),
            "prefix_anchor_scale": float(PREFIX_ANCHOR_SCALE),
            "teacher_scale": float(teacher_scale),
            "balance": balance,
            "teacher_gradient_max_abs": teacher_max,
            "baseline_composition_delta_max_abs": baseline_composition_delta,
            "enabled_composition_delta_max_abs": enabled_composition_delta,
            "enabled_gradient_delta_max_abs": enabled_delta,
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
        "environment": {
            "jax_backend": jax.default_backend(),
            "jax_devices": [device.platform for device in jax.devices()],
            "mujoco_version": mujoco.__version__,
            "numpy_version": np.__version__,
        },
        "sources": contract["sources"],
        "source_manifest_sha256": contract["source_manifest_sha256"],
        "authority": contract["authority"],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
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
