#!/usr/bin/env python3
"""Run the zero-update Winner-v29 right-pitch prefix-anchor CPU contract."""

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
import run_winner_v25_directional_support_control_diagnostic as v25  # noqa: E402
import winner_v29_prefix_right_pitch_anchor as v29  # noqa: E402


CONTRACT = ANALYSIS / "winner_v29_prefix_right_pitch_anchor_cpu_contract.json"
V28_RESULT = ANALYSIS / "winner_v28_prefix_joint_group_causal_screen_result.json"
V22_TRAINING = ANALYSIS / "winner_v22_normalized_predictor_training_result.json"
V24_TRAINING = ANALYSIS / "winner_v24_baseline_anchored_training_result.json"
V24_SUPPORT = ANALYSIS / "winner_v24_baseline_anchored_support_gate_result.json"
FULL_PREREG = ANALYSIS / "winner_v12_full_calibrator_training_preregistration.json"
DOMAIN = ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
ROLLOUT_UPDATE_INDEX = 200
COMPOSITION_TOLERANCE = 4.0e-6
GRAPH_TOLERANCE = 1.0e-7
BALANCE_RELATIVE_TOLERANCE = 2.0e-6


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
    array = np.ascontiguousarray(value)
    digest = hashlib.sha256()
    digest.update(str(array.dtype).encode())
    digest.update(b"|")
    digest.update(json.dumps(list(array.shape), separators=(",", ":")).encode())
    digest.update(b"|")
    digest.update(array.tobytes())
    return digest.hexdigest()


def tree_delta_max_abs(
    left: Mapping[str, Any], right: Mapping[str, Any]
) -> dict[str, float]:
    if set(left) != set(right):
        raise ValueError("Winner-v29 tree schema changed")
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


def validate_contract(value: Mapping[str, Any]) -> None:
    if (
        value.get("schema_version")
        != "winner_v29.prefix_right_pitch_anchor_cpu_contract.v1"
        or value.get("status")
        != "PREREGISTERED_WINNER_V29_PREFIX_RIGHT_PITCH_ANCHOR_CPU_CONTRACT"
        or value.get("decision")
        != "AUTHORIZE_ONE_ZERO_UPDATE_PREFIX_RIGHT_PITCH_ANCHOR_CPU_PROOF_ONLY"
        or value.get("execution_now")
        != {
            "rollout_episode_slots": 0,
            "optimizer_updates": 0,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        }
    ):
        raise ValueError("Winner-v29 contract authority changed")
    expected_objective = {
        "candidate_checkpoint": {"label": "winner_v24_final", "update": 200},
        "source_checkpoint": {"label": "winner_v22_final", "update": 100},
        "rollout_update_index": ROLLOUT_UPDATE_INDEX,
        "selected_training_configuration_ids": list(
            v29.SELECTED_TRAINING_CONFIGURATION_IDS
        ),
        "selected_episode_slots": v29.EXPECTED_SELECTED_EPISODES,
        "prefix_ticks": list(range(v29.PREFIX_TICKS)),
        "action_indices": list(v29.RIGHT_PITCH_ACTION_INDICES),
        "action_labels": ["right_hip_pitch", "right_knee", "right_ankle"],
        "selected_elements": v29.EXPECTED_ANCHOR_ELEMENTS,
        "candidate_action": (
            "deterministic graph-authoritative bounded mean action recomputed with "
            "Winner-v24 final on its rollout observations and realized previous actions"
        ),
        "source_action": (
            "stop-gradient deterministic graph-authoritative bounded mean action from "
            "Winner-v22 final on the same candidate observations and realized previous "
            "actions with its own shadow recurrent hidden state"
        ),
        "raw_loss": "mean squared candidate-minus-source action over selected elements",
        "baseline": (
            "unchanged Winner-v24 baseline-anchored PPO gradient plus frozen Winner-v22 "
            "normalized-predictor gradient at scale 380.9135437011719"
        ),
        "scale_rule": (
            "once on the exact zero-update batch, set anchor scale to baseline-gradient "
            "RMS divided by raw-anchor-gradient RMS over recurrent-core plus action-head "
            "leaves; freeze the resulting scalar for any later one-update preregistration"
        ),
        "gradient_balance_keys": list(v29.ANCHOR_GRADIENT_KEYS),
        "default_off": "bit-exact unchanged Winner-v24 gradient and all transition arrays",
        "no_action_replacement": True,
    }
    if value.get("objective") != expected_objective:
        raise ValueError("Winner-v29 objective changed")
    sources = value.get("sources")
    if not isinstance(sources, dict) or not sources:
        raise ValueError("Winner-v29 source manifest is absent")
    for name, item in sources.items():
        path = ROOT / item["path"]
        if (
            item.get("hash_mode") != "lf"
            or not path.is_file()
            or lf_sha256(path) != item.get("sha256")
        ):
            raise ValueError(f"Winner-v29 source changed: {name}")
    if canonical_sha256(sources) != value.get("source_manifest_sha256"):
        raise ValueError("Winner-v29 source manifest changed")


def validate_artifact(path: Path, receipt: Mapping[str, Any], label: str) -> None:
    if (
        not path.is_file()
        or path.stat().st_size != int(receipt["bytes"])
        or sha256(path) != receipt["sha256"]
    ):
        raise ValueError(f"Winner-v29 {label} artifact changed")


def graph_replay_error(
    *,
    ort: Any,
    source_graph: Path,
    candidate_graph: Path,
    batch: Mapping[str, np.ndarray],
    anchor_mask: np.ndarray,
    source_hidden: np.ndarray,
    source_actions: np.ndarray,
    candidate_hidden: np.ndarray,
    candidate_actions: np.ndarray,
) -> dict[str, Any]:
    source_session = v25.graph_session(ort, source_graph)
    candidate_session = v25.graph_session(ort, candidate_graph)
    selected_environment = np.any(anchor_mask > 0, axis=(1, 2))
    maximum = {
        "source_action": 0.0,
        "source_hidden": 0.0,
        "candidate_action": 0.0,
        "candidate_hidden": 0.0,
    }
    rows = 0
    for environment in np.flatnonzero(selected_environment):
        source_h_in = np.zeros((64,), dtype=np.float32)
        candidate_h_in = np.zeros((64,), dtype=np.float32)
        for tick in range(v29.PREFIX_TICKS):
            observation = np.asarray(batch["observations"][environment, tick])
            previous = np.asarray(batch["previous_actions"][environment, tick])
            source_action, source_h_out = v25.infer(
                source_session, observation, previous, source_h_in
            )
            candidate_action, candidate_h_out = v25.infer(
                candidate_session, observation, previous, candidate_h_in
            )
            maximum["source_action"] = max(
                maximum["source_action"],
                float(np.max(np.abs(source_action - source_actions[environment, tick]))),
            )
            maximum["source_hidden"] = max(
                maximum["source_hidden"],
                float(np.max(np.abs(source_h_out - source_hidden[environment, tick]))),
            )
            maximum["candidate_action"] = max(
                maximum["candidate_action"],
                float(
                    np.max(
                        np.abs(candidate_action - candidate_actions[environment, tick])
                    )
                ),
            )
            maximum["candidate_hidden"] = max(
                maximum["candidate_hidden"],
                float(
                    np.max(
                        np.abs(candidate_h_out - candidate_hidden[environment, tick])
                    )
                ),
            )
            source_h_in = source_h_out
            candidate_h_in = candidate_h_out
            rows += 1
    return {"rows": rows, "maximum_abs_error": maximum}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--canonical-fit", type=Path, required=True)
    parser.add_argument("--v22-training-work-root", type=Path, required=True)
    parser.add_argument("--v24-training-work-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--offline-cpu-only", action="store_true")
    parser.add_argument(
        "--zero-update-prefix-right-pitch-anchor-proof-authorized",
        action="store_true",
    )
    args = parser.parse_args()
    if (
        not args.offline_cpu_only
        or not args.zero_update_prefix_right_pitch_anchor_proof_authorized
    ):
        raise PermissionError(
            "Winner-v29 proof requires --offline-cpu-only and "
            "--zero-update-prefix-right-pitch-anchor-proof-authorized"
        )
    if args.output.exists():
        raise FileExistsError("refusing to overwrite Winner-v29 evidence")

    import jax
    import jax.numpy as jnp
    import mujoco
    import onnxruntime as ort
    import run_winner_v12_calibrator_cpu_smoke as smoke
    import run_winner_v12_full_calibrator_training as full
    import run_winner_v22_normalized_predictor_support_gate as v22_gate
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
        raise ValueError("Winner-v29 requires CPU-only JAX")
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    validate_contract(contract)
    v28 = json.loads(V28_RESULT.read_text(encoding="utf-8"))
    v22_result = json.loads(V22_TRAINING.read_text(encoding="utf-8"))
    v24_result = json.loads(V24_TRAINING.read_text(encoding="utf-8"))
    v24_support = json.loads(V24_SUPPORT.read_text(encoding="utf-8"))
    if (
        v28.get("status") != "PASS_WINNER_V28_PREFIX_JOINT_GROUP_CAUSAL_SCREEN"
        or v28.get("classification") != "SINGLE_PREFIX_JOINT_GROUP_CAUSAL_LOCALIZATION"
        or v28.get("selected_group") != "RIGHT_PITCH_CHAIN"
        or v28.get("decision")
        != "AUTHORIZE_SELECTED_PREFIX_GROUP_OBJECTIVE_CPU_CONTRACT_PREREGISTRATION_ONLY"
        or v22_result.get("status")
        != "PASS_WINNER_V22_NORMALIZED_PREDICTOR_TRAINING_ARTIFACT"
        or v24_result.get("status")
        != "PASS_WINNER_V24_BASELINE_ANCHORED_TRAINING_ARTIFACT"
        or v24_support.get("status")
        != "HOLD_WINNER_V24_BASELINE_ANCHORED_SUPPORT_GATE"
    ):
        raise ValueError("Winner-v29 source authority changed")

    source_receipt = contract["artifact_inputs"]["winner_v22_training"]
    candidate_receipt = contract["artifact_inputs"]["winner_v24_training"]
    source_snapshot_path = (
        args.v22_training_work_root
        / "snapshots/snapshot_normalized_predictor_update_100.npz"
    )
    source_graph_path = args.v22_training_work_root / "graphs/winner_v22_final.onnx"
    candidate_snapshot_path = (
        args.v24_training_work_root
        / "snapshots/snapshot_baseline_anchored_update_200.npz"
    )
    candidate_graph_path = args.v24_training_work_root / "graphs/winner_v24_final.onnx"
    validate_artifact(
        source_snapshot_path, source_receipt["source_snapshot"], "source snapshot"
    )
    validate_artifact(source_graph_path, source_receipt["source_graph"], "source graph")
    validate_artifact(
        candidate_snapshot_path,
        candidate_receipt["final"]["snapshot"],
        "candidate snapshot",
    )
    validate_artifact(
        candidate_graph_path,
        candidate_receipt["final"]["graph"],
        "candidate graph",
    )

    expected_versions = dict(
        json.loads(FULL_PREREG.read_text(encoding="utf-8"))[
            "implementation_contract_environment"
        ]
    )
    if expected_versions.pop("platform") != "CPU only" or not smoke.validate_software_versions(
        {"software_versions": expected_versions}
    )["exact"]:
        raise ValueError("Winner-v29 software environment changed")
    if smoke.sha256(args.canonical_fit) != smoke.P30_FIT_LF_SHA256:
        raise ValueError("Winner-v29 canonical P30 fit changed")
    if smoke.git_output(args.playground_root, "rev-parse", "HEAD") != smoke.CONTROL_COMMIT:
        raise ValueError("Winner-v29 Playground source changed")
    smoke.validate_playground_tree(args.playground_root)
    scene = args.playground_root / smoke.SCENE_RELATIVE
    if smoke.sha256(scene) != smoke.SCENE_SHA256:
        raise ValueError("Winner-v29 scene changed")

    v22_gate.smoke = smoke
    v22_gate.training = training
    v22_gate.v21 = v21
    source_snapshot = v22v2.load_snapshot(source_snapshot_path)
    candidate_snapshot = v22v2.load_snapshot(candidate_snapshot_path)
    v22_gate._validate_snapshot(
        source_snapshot, expected_stage="normalized_predictor_joint_stage2"
    )
    if (
        source_snapshot["metadata"].get("completed_updates") != 100
        or int(np.asarray(source_snapshot["optimizer"]["count"])) != 100
        or candidate_snapshot["metadata"].get("stage")
        != "baseline_anchored_symmetric_failure_joint_stage2"
        or candidate_snapshot["metadata"].get("completed_updates") != 200
        or int(np.asarray(candidate_snapshot["optimizer"]["count"])) != 200
    ):
        raise ValueError("Winner-v29 snapshot boundary changed")
    if not np.array_equal(
        source_snapshot["target_mean"], candidate_snapshot["target_mean"]
    ) or not np.array_equal(source_snapshot["target_std"], candidate_snapshot["target_std"]):
        raise ValueError("Winner-v29 target normalizer changed")

    source_parameters = source_snapshot["parameters"]
    candidate_parameters = candidate_snapshot["parameters"]
    source_parameters_copy = {
        key: np.asarray(value).copy() for key, value in source_parameters.items()
    }
    candidate_parameters_copy = {
        key: np.asarray(value).copy() for key, value in candidate_parameters.items()
    }
    candidate_optimizer_copy = {
        "count": np.asarray(candidate_snapshot["optimizer"]["count"]).copy(),
        "m": {
            key: np.asarray(value).copy()
            for key, value in candidate_snapshot["optimizer"]["m"].items()
        },
        "v": {
            key: np.asarray(value).copy()
            for key, value in candidate_snapshot["optimizer"]["v"].items()
        },
    }
    full_prereg = json.loads(FULL_PREREG.read_text(encoding="utf-8"))
    domain = json.loads(DOMAIN.read_text(encoding="utf-8"))
    population = full.training_population(full_prereg, domain)
    observer_type = smoke.load_runtime_observer(args.canonical_fit)
    design = json.loads(smoke.CALIBRATOR_PREREG.read_text(encoding="utf-8"))
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
        parameters=candidate_parameters,
        update_index=ROLLOUT_UPDATE_INDEX,
    )
    full.validate_stage2_masks(batch_np, episodes)
    episode_hash = full.validate_episode_receipts(
        episodes, population, stage=2, update_index=ROLLOUT_UPDATE_INDEX
    )
    boundary = full.stage2_action_boundary_evidence(batch_np)
    reward = v15.reward_evidence(batch_np)
    anchor_mask = v29.build_anchor_mask(population, batch_np["valid_mask"])
    selected_episode_slots = int(np.sum(np.any(anchor_mask > 0, axis=(1, 2))))

    _, value_jax = training.stage2_mean_value(
        candidate_parameters, jnp.asarray(batch_np["hidden"], dtype=jnp.float32)
    )
    objective_batch_np, objective_evidence = v24v3.apply_training_objective(
        batch_np,
        episodes,
        np.asarray(value_jax, dtype=np.float32),
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
    transition_arrays_copy = {
        key: np.asarray(value).copy() for key, value in objective_batch_np.items()
    }
    batch = {key: jnp.asarray(value) for key, value in objective_batch_np.items()}
    trainable = v21.joint_trainable_parameters(candidate_parameters)
    target_mean = jnp.asarray(candidate_snapshot["target_mean"], dtype=jnp.float32)
    target_std = jnp.asarray(candidate_snapshot["target_std"], dtype=jnp.float32)
    source_trainable = v21.joint_trainable_parameters(source_parameters)

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
        return v29.prefix_anchor_loss(
            values_tree, source_trainable, batch, anchor_mask
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
    baseline_gradients = v22v2.compose_gradients(ppo_gradients, predictor_gradients)
    anchor_scale, balance = v29.gradient_balance_scale(
        baseline_gradients, anchor_gradients
    )
    disabled_gradients = v29.compose_gradients(
        baseline_gradients, anchor_gradients, anchor_scale, enabled=False
    )
    enabled_gradients = v29.compose_gradients(
        baseline_gradients, anchor_gradients, anchor_scale, enabled=True
    )

    def total_objective(values_tree: Mapping[str, Any]) -> Any:
        current_ppo, _ = ppo_objective(values_tree)
        current_predictor, _ = predictor_objective(values_tree)
        current_anchor, _ = anchor_objective(values_tree)
        return (
            current_ppo
            + jnp.asarray(v22v2.FROZEN_PREDICTOR_SCALE, dtype=jnp.float32)
            * current_predictor
            + jnp.asarray(anchor_scale, dtype=jnp.float32) * current_anchor
        )

    direct_enabled_gradients = jax.grad(total_objective)(trainable)
    direct_composition_delta = tree_delta_max_abs(
        enabled_gradients, direct_enabled_gradients
    )
    disabled_delta = tree_delta_max_abs(baseline_gradients, disabled_gradients)
    enabled_delta = tree_delta_max_abs(baseline_gradients, enabled_gradients)
    anchor_max = common.tree_max_abs(anchor_gradients)

    candidate_hidden, candidate_actions = v29.deterministic_bounded_actions(
        trainable, batch["observations"], batch["previous_actions"]
    )
    source_hidden, source_actions = v29.deterministic_bounded_actions(
        source_trainable, batch["observations"], batch["previous_actions"]
    )
    graph_replay = graph_replay_error(
        ort=ort,
        source_graph=source_graph_path,
        candidate_graph=candidate_graph_path,
        batch=batch_np,
        anchor_mask=anchor_mask,
        source_hidden=np.asarray(source_hidden, dtype=np.float32),
        source_actions=np.asarray(source_actions, dtype=np.float32),
        candidate_hidden=np.asarray(candidate_hidden, dtype=np.float32),
        candidate_actions=np.asarray(candidate_actions, dtype=np.float32),
    )
    all_graph_errors = list(graph_replay["maximum_abs_error"].values())
    parameters_unchanged = all(
        np.array_equal(candidate_parameters_copy[key], np.asarray(candidate_parameters[key]))
        for key in candidate_parameters_copy
    ) and all(
        np.array_equal(source_parameters_copy[key], np.asarray(source_parameters[key]))
        for key in source_parameters_copy
    )
    optimizer_unchanged = (
        np.array_equal(
            candidate_optimizer_copy["count"], candidate_snapshot["optimizer"]["count"]
        )
        and common.tree_equal(
            candidate_optimizer_copy["m"], candidate_snapshot["optimizer"]["m"]
        )
        and common.tree_equal(
            candidate_optimizer_copy["v"], candidate_snapshot["optimizer"]["v"]
        )
    )
    transitions_unchanged = all(
        np.array_equal(transition_arrays_copy[key], objective_batch_np[key])
        for key in transition_arrays_copy
    )
    non_anchor_zero = all(anchor_max[key] == 0.0 for key in v29.NON_ANCHOR_GRADIENT_KEYS)
    anchor_selected_nonzero = all(
        anchor_max[key] > 0.0 for key in v29.ANCHOR_GRADIENT_KEYS
    )
    enabled_non_anchor_exact = all(
        enabled_delta[key] == 0.0 for key in v29.NON_ANCHOR_GRADIENT_KEYS
    )
    scaled_balance_error = abs(
        balance["scaled_anchor_policy_gradient_rms"]
        - balance["baseline_policy_gradient_rms"]
    ) / balance["baseline_policy_gradient_rms"]
    all_numeric = [
        float(ppo_loss),
        float(predictor_loss),
        float(anchor_loss),
        float(anchor_scale),
        scaled_balance_error,
        *balance.values(),
        *direct_composition_delta.values(),
        *enabled_delta.values(),
        *anchor_max.values(),
        *all_graph_errors,
    ]
    checks = {
        "source_v22_snapshot_and_graph_exact": True,
        "candidate_v24_final_snapshot_and_graph_exact": True,
        "v28_selected_right_pitch_chain_authority_exact": True,
        "target_normalizer_bit_exact": True,
        "cpu_only_environment_exact": True,
        "exact_80_episode_rollout_at_update_200": len(episodes) == 80,
        "episode_receipts_exact": bool(episode_hash),
        "action_boundary_exact": boundary["realized_equals_numpy_bit_exact"]
        and boundary["numpy_equals_jax_bit_exact"],
        "pitch_margin_reward_exact": reward["reward_formula_bit_exact"],
        "v24_baseline_objective_exact": (
            (int(np.sum(failure_mask)) > 0 and changed_keys == list(v24v2.MODIFIED_BATCH_KEYS))
            or (int(np.sum(failure_mask)) == 0 and changed_keys == [])
        )
        and objective_evidence["zero_failure_bit_exact_noop"]
        == (int(np.sum(failure_mask)) == 0),
        "selected_16_episode_slots_exact": selected_episode_slots
        == v29.EXPECTED_SELECTED_EPISODES,
        "selected_384_prefix_action_elements_exact": int(np.sum(anchor_mask))
        == v29.EXPECTED_ANCHOR_ELEMENTS,
        "selected_mask_only_ticks_0_7_and_indices_11_13": bool(
            np.all(anchor_mask[:, v29.PREFIX_TICKS :, :] == 0.0)
            and np.all(anchor_mask[:, :, :11] == 0.0)
        ),
        "source_and_candidate_jax_match_frozen_onnx_at_most_1e_7": graph_replay["rows"]
        == v29.EXPECTED_SELECTED_EPISODES * v29.PREFIX_TICKS
        and max(all_graph_errors) <= GRAPH_TOLERANCE,
        "raw_anchor_loss_finite_nonzero": math.isfinite(float(anchor_loss))
        and float(anchor_loss) > 0.0,
        "selected_source_candidate_actions_differ": float(
            anchor_metrics["maximum_selected_action_delta"]
        )
        > 0.0,
        "anchor_gradients_nonzero_on_all_six_selected_policy_leaves": anchor_selected_nonzero,
        "anchor_gradients_zero_on_value_logstd_and_predictor_leaves": non_anchor_zero,
        "gradient_balance_scale_finite_positive": math.isfinite(float(anchor_scale))
        and float(anchor_scale) > 0.0,
        "scaled_anchor_rms_matches_baseline_at_most_2e_6_relative": scaled_balance_error
        <= BALANCE_RELATIVE_TOLERANCE,
        "default_off_combined_gradient_bit_exact": max(disabled_delta.values()) == 0.0,
        "enabled_changes_recurrent_and_action_gradients": all(
            enabled_delta[key] > 0.0 for key in v29.ANCHOR_GRADIENT_KEYS
        ),
        "enabled_preserves_non_anchor_gradients_bit_exact": enabled_non_anchor_exact,
        "enabled_direct_loss_gradient_matches_composition_at_most_4e_6": max(
            direct_composition_delta.values()
        )
        <= COMPOSITION_TOLERANCE,
        "predictor_metrics_finite_and_stored_successors_present": training.finite_tree(
            predictor_metrics
        )
        and int(predictor_metrics["stored_successor_transition_count"]) > 0,
        "ppo_metrics_finite_and_hidden_replay_exact": training.finite_tree(ppo_metrics)
        and float(ppo_metrics["sampled_hidden_replay_max_abs_error"]) <= 1.0e-6,
        "all_losses_metrics_gradients_finite": all(math.isfinite(value) for value in all_numeric),
        "transition_arrays_unchanged_by_anchor": transitions_unchanged,
        "parameters_and_source_unchanged_no_optimizer_step": parameters_unchanged
        and optimizer_unchanged,
        "optimizer_updates_zero": True,
        "formal_support_cells_zero": True,
        "locomotion_steps_zero": True,
        "robot_or_rdk_access_zero": True,
    }
    failed_checks = sorted(name for name, passed in checks.items() if not passed)
    result = {
        "schema_version": "winner_v29.prefix_right_pitch_anchor_cpu_result.v1",
        "status": (
            "PASS_WINNER_V29_PREFIX_RIGHT_PITCH_ANCHOR_CPU_CONTRACT"
            if not failed_checks
            else "HOLD_WINNER_V29_PREFIX_RIGHT_PITCH_ANCHOR_CPU_CONTRACT"
        ),
        "decision": (
            "AUTHORIZE_SEPARATE_ONE_UPDATE_PREFIX_RIGHT_PITCH_ANCHOR_CPU_PROOF_PREREGISTRATION_ONLY"
            if not failed_checks
            else "DO_NOT_RUN_OPTIMIZER_UPDATE"
        ),
        "failed_checks": failed_checks,
        "checks": checks,
        "source_identity": {
            "winner_v22_snapshot": source_receipt["source_snapshot"],
            "winner_v22_graph": source_receipt["source_graph"],
            "winner_v24_final_snapshot": candidate_receipt["final"]["snapshot"],
            "winner_v24_final_graph": candidate_receipt["final"]["graph"],
        },
        "rollout_evidence": {
            "rollout_update_index": ROLLOUT_UPDATE_INDEX,
            "episode_slots": len(episodes),
            "episode_receipts_sha256": episode_hash,
            "roll_pitch_failure_count": int(np.sum(failure_mask)),
            "v24_objective_modified_batch_keys": changed_keys,
            "selected_configuration_ids": list(
                v29.SELECTED_TRAINING_CONFIGURATION_IDS
            ),
            "selected_episode_slots": selected_episode_slots,
            "prefix_ticks": list(range(v29.PREFIX_TICKS)),
            "action_indices": list(v29.RIGHT_PITCH_ACTION_INDICES),
            "selected_elements": int(np.sum(anchor_mask)),
            "observations_sha256": array_sha256(batch_np["observations"]),
            "previous_actions_sha256": array_sha256(batch_np["previous_actions"]),
            "anchor_mask_sha256": array_sha256(anchor_mask),
            "transition_hashes": {
                key: array_sha256(value) for key, value in sorted(objective_batch_np.items())
            },
        },
        "objective_evidence": {
            "raw_anchor_loss": float(anchor_loss),
            "maximum_selected_action_delta": float(
                anchor_metrics["maximum_selected_action_delta"]
            ),
            "anchor_scale": float(anchor_scale),
            "balance": balance,
            "gradient_balance_keys": list(v29.ANCHOR_GRADIENT_KEYS),
            "baseline_ppo_loss": float(ppo_loss),
            "baseline_normalized_predictor_loss": float(predictor_loss),
            "frozen_predictor_scale": float(v22v2.FROZEN_PREDICTOR_SCALE),
            "anchor_gradient_max_abs": anchor_max,
            "enabled_gradient_delta_max_abs": enabled_delta,
            "direct_composition_delta_max_abs": direct_composition_delta,
            "graph_replay": graph_replay,
        },
        "execution": {
            "rollout_episode_slots": len(episodes),
            "optimizer_updates": 0,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "environment": {
            "jax_backend": jax.default_backend(),
            "jax_devices": [device.platform for device in jax.devices()],
            "mujoco_version": mujoco.__version__,
            "onnxruntime_version": ort.__version__,
        },
        "sources": contract["sources"],
        "source_manifest_sha256": contract["source_manifest_sha256"],
        "authority": {
            "robot_clearance": False,
            "training_authorized": False,
            "one_update_authorized": False,
            "runtime_implementation_authorized": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "pass_authorizes_only": (
                "one separately preregistered CPU-only one-update proof using the exact "
                "recorded anchor scale"
            ),
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(result["status"])
    if failed_checks:
        print(json.dumps(failed_checks))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
