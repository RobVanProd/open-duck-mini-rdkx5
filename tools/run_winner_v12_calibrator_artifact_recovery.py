#!/usr/bin/env python3
"""Recover the interrupted Winner-v12 smoke evidence without a new update."""

from __future__ import annotations

import argparse
from collections import Counter
import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np

import run_winner_v12_calibrator_cpu_smoke as smoke


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONTRACT = (
    ROOT / "outputs/analysis/winner_v12_calibrator_artifact_recovery_contract.json"
)
DEFAULT_OUTPUT = (
    ROOT / "outputs/analysis/winner_v12_calibrator_artifact_recovery_result.json"
)
FAILURE_ATTRIBUTION = (
    ROOT / "outputs/analysis/winner_v12_calibrator_cpu_smoke_failure_attribution.json"
)
SMOKE_CONTRACT = ROOT / "outputs/analysis/winner_v12_calibrator_cpu_smoke_contract.json"
CALIBRATOR_PREREG = smoke.CALIBRATOR_PREREG
DOMAIN_PREREG = smoke.DOMAIN_PREREG
EXPECTED_CHECKPOINT_SHA256 = (
    "5748978f050c222f156d733f709b1ddc76e2b27bebaa00ed726ad53d9fca2288"
)
EXPECTED_GRAPH_SHA256 = (
    "9c0d018cd4d496abf9081584f969a917293ef72ecdcd6047483d6c553389aa4c"
)


def validate_recovery_contract(contract: Mapping[str, Any]) -> None:
    if contract.get("status") != "PREREGISTERED_WINNER_V12_READ_ONLY_RECOVERY":
        raise ValueError("recovery contract is not preregistered")
    if contract.get("decision") != "AUTHORIZE_ONE_READ_ONLY_RECOVERY_RUN":
        raise ValueError("recovery authority changed")
    for item in contract["sources"].values():
        path = ROOT / item["path"]
        observed = (
            smoke.lf_sha256(path) if item["hash_mode"] == "lf" else smoke.sha256(path)
        )
        if observed != item["sha256"]:
            raise ValueError(f"recovery source hash mismatch: {item['path']}")


def load_checkpoint(path: Path) -> dict[str, Any]:
    with np.load(path, allow_pickle=False) as archive:
        first = {name: archive[name].copy() for name in archive.files}
    with np.load(path, allow_pickle=False) as archive:
        second = {name: archive[name].copy() for name in archive.files}
    repeated_exact = set(first) == set(second) and all(
        np.array_equal(first[name], second[name]) for name in first
    )
    initial = smoke.training.initialize_training_parameters()
    parameter_keys = set(initial)
    stage1_keys = set(smoke.training.ENCODER_AUXILIARY_KEYS)
    stage2_keys = set(
        smoke.training.DEPLOYABLE_ACTION_KEYS + smoke.training.TRAINING_ONLY_STAGE2_KEYS
    )
    expected_names = {f"parameter.{name}" for name in parameter_keys}
    expected_names |= {"stage1_adam.count", "stage2_adam.count"}
    expected_names |= {
        f"stage1_adam.{moment}.{name}" for moment in ("m", "v") for name in stage1_keys
    }
    expected_names |= {
        f"stage2_adam.{moment}.{name}" for moment in ("m", "v") for name in stage2_keys
    }
    expected_names |= {"target_mean", "target_std"}
    parameters = {name: first[f"parameter.{name}"] for name in sorted(parameter_keys)}
    stage1 = {
        moment: {
            name: first[f"stage1_adam.{moment}.{name}"] for name in sorted(stage1_keys)
        }
        for moment in ("m", "v")
    }
    stage2 = {
        moment: {
            name: first[f"stage2_adam.{moment}.{name}"] for name in sorted(stage2_keys)
        }
        for moment in ("m", "v")
    }
    return {
        "arrays": first,
        "schema_exact": set(first) == expected_names,
        "repeat_load_bit_exact": repeated_exact,
        "all_arrays_finite": all(
            bool(np.all(np.isfinite(value))) for value in first.values()
        ),
        "parameters": parameters,
        "stage1": {
            **stage1,
            "count": int(first["stage1_adam.count"]),
        },
        "stage2": {
            **stage2,
            "count": int(first["stage2_adam.count"]),
        },
        "target_mean": first["target_mean"],
        "target_std": first["target_std"],
    }


def tree_comparison(
    observed: Mapping[str, Any], expected: Mapping[str, Any]
) -> dict[str, Any]:
    if set(observed) != set(expected):
        return {
            "schema_exact": False,
            "bit_exact": False,
            "maximum_absolute_error": math.inf,
        }
    maximum = 0.0
    exact = True
    for key in observed:
        left = np.asarray(observed[key])
        right = np.asarray(expected[key])
        if left.shape != right.shape or left.dtype != right.dtype:
            return {
                "schema_exact": False,
                "bit_exact": False,
                "maximum_absolute_error": math.inf,
            }
        if not np.all(np.isfinite(left)) or not np.all(np.isfinite(right)):
            raise FloatingPointError(f"nonfinite recovery comparison: {key}")
        exact &= np.array_equal(left, right)
        maximum = max(maximum, float(np.max(np.abs(left - right))))
    return {
        "schema_exact": True,
        "bit_exact": bool(exact),
        "maximum_absolute_error": maximum,
    }


def expected_moments(
    gradients: Mapping[str, Any], parameters: Mapping[str, Any]
) -> dict[str, dict[str, Any]]:
    import jax.numpy as jnp

    zeros = {key: jnp.zeros_like(value) for key, value in parameters.items()}
    first = {
        key: (
            jnp.float32(smoke.training.ADAM_BETA1) * zeros[key]
            + jnp.float32(1.0 - smoke.training.ADAM_BETA1) * gradients[key]
        )
        for key in parameters
    }
    second = {
        key: (
            jnp.float32(smoke.training.ADAM_BETA2) * zeros[key]
            + jnp.float32(1.0 - smoke.training.ADAM_BETA2) * jnp.square(gradients[key])
        )
        for key in parameters
    }
    return {"m": first, "v": second}


def parameters_from_moments(
    parameters: Mapping[str, Any],
    moments: Mapping[str, Mapping[str, Any]],
    learning_rate: float,
) -> dict[str, Any]:
    import jax.numpy as jnp

    count = jnp.asarray(1, dtype=jnp.int32)
    correction1 = jnp.float32(1.0) - jnp.float32(smoke.training.ADAM_BETA1) ** count
    correction2 = jnp.float32(1.0) - jnp.float32(smoke.training.ADAM_BETA2) ** count
    return {
        key: (
            jnp.asarray(parameters[key])
            - jnp.float32(learning_rate)
            * (jnp.asarray(moments["m"][key]) / correction1)
            / (
                jnp.sqrt(jnp.asarray(moments["v"][key]) / correction2)
                + jnp.float32(smoke.training.ADAM_EPSILON)
            )
        )
        for key in parameters
    }


def corrected_observer_plant_canary(
    preregistration: Mapping[str, Any],
    observer_type: type[Any],
    canonical_fit: Path,
) -> dict[str, Any]:
    p30_observer = observer_type(canonical_fit, smoke.HOME_RAD)
    p31_observer = observer_type(canonical_fit, smoke.HOME_RAD)
    p30_plant = smoke.ActuatorBridgeModel(
        smoke.plant_parameters(preregistration, smoke.PLANTS[0]),
        smoke.HOME_RAD,
        smoke.HOME_RAD,
    )
    p31_plant = smoke.ActuatorBridgeModel(
        smoke.plant_parameters(preregistration, smoke.PLANTS[1]),
        smoke.HOME_RAD,
        smoke.HOME_RAD,
    )
    generator, _ = smoke.prng_for(99, 0)
    previous = np.zeros(smoke.training.ACTION_SIZE, dtype=np.float32)
    observer_exact = True
    maximum_plant_separation = 0.0
    for _ in range(128):
        raw = previous + generator.uniform(
            -0.15, 0.15, smoke.training.ACTION_SIZE
        ).astype(np.float32)
        action = smoke.bounded_action_numpy(raw, previous)
        target = smoke.HOME_RAD + action.astype(np.float64) * smoke.ACTION_SCALE_RAD
        observer_exact &= np.array_equal(
            p30_observer.step(target), p31_observer.step(target)
        )
        p30_applied = p30_plant.step(target, smoke.CONTROL_DT_S)
        p31_applied = p31_plant.step(target, smoke.CONTROL_DT_S)
        maximum_plant_separation = max(
            maximum_plant_separation,
            float(np.max(np.abs(p30_applied - p31_applied))),
        )
        previous = action
    return {
        "fixed_p30_observer_bit_exact_across_hidden_plant_choice": bool(observer_exact),
        "hidden_physical_plants_are_distinct": maximum_plant_separation > 0.0,
        "maximum_hidden_plant_separation_rad": maximum_plant_separation,
    }


def terminal_encoding_exact(
    batch: Mapping[str, np.ndarray], episodes: list[dict[str, Any]]
) -> bool:
    exact = True
    for environment, episode in enumerate(episodes):
        sample_count = int(np.sum(batch["valid_mask"][environment]))
        valid_count = int(np.sum(batch["valid_transition_mask"][environment]))
        done_indices = np.flatnonzero(batch["done"][environment])
        if episode["terminal"] is None:
            exact &= bool(
                sample_count == valid_count == smoke.SMOKE_TICKS
                and np.array_equal(done_indices, np.asarray([smoke.SMOKE_TICKS - 1]))
            )
        else:
            tick = int(episode["terminal"]["tick"])
            exact &= bool(
                sample_count == valid_count + 1 == tick + 1
                and np.array_equal(done_indices, np.asarray([tick]))
                and batch["valid_transition_mask"][environment, tick] == 0.0
                and batch["valid_mask"][environment, tick] == 1.0
            )
    return bool(exact)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--policy-half", type=Path, required=True)
    parser.add_argument("--policy-final", type=Path, required=True)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--graph", type=Path, required=True)
    parser.add_argument("--canonical-fit", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(f"refusing to overwrite recovery result: {args.output}")

    contract = json.loads(args.contract.read_text(encoding="utf-8"))
    validate_recovery_contract(contract)
    smoke_contract = json.loads(SMOKE_CONTRACT.read_text(encoding="utf-8"))
    smoke.validate_contract(smoke_contract)
    failure = json.loads(FAILURE_ATTRIBUTION.read_text(encoding="utf-8"))
    if failure.get("status") != "HOLD_WINNER_V12_CALIBRATOR_CPU_SMOKE_NO_RESULT":
        raise ValueError("failure attribution changed")
    if smoke.sha256(args.checkpoint) != EXPECTED_CHECKPOINT_SHA256:
        raise ValueError("recovered checkpoint hash mismatch")
    if smoke.sha256(args.graph) != EXPECTED_GRAPH_SHA256:
        raise ValueError("recovered graph hash mismatch")
    if smoke.sha256(args.canonical_fit) != smoke.P30_FIT_LF_SHA256:
        raise ValueError("recovered canonical P30 fit hash mismatch")
    protected_before = {
        "half": smoke.sha256(args.policy_half),
        "final": smoke.sha256(args.policy_final),
    }
    if protected_before != smoke.PROTECTED_POLICY_HASHES:
        raise ValueError("protected policy hash mismatch")
    if (
        smoke.git_output(args.playground_root, "rev-parse", "HEAD")
        != smoke.CONTROL_COMMIT
    ):
        raise ValueError("Playground commit mismatch")
    playground_receipt = smoke.validate_playground_tree(args.playground_root)
    model_path = args.playground_root / smoke.MODEL_RELATIVE
    scene_path = args.playground_root / smoke.SCENE_RELATIVE
    if smoke.sha256(model_path) != smoke.MODEL_SHA256:
        raise ValueError("recovered model XML hash mismatch")
    if smoke.sha256(scene_path) != smoke.SCENE_SHA256:
        raise ValueError("recovered scene XML hash mismatch")
    software_versions = smoke.validate_software_versions(contract)

    import jax
    import jax.numpy as jnp
    import mujoco

    if jax.default_backend() != "cpu" or any(
        device.platform != "cpu" for device in jax.devices()
    ):
        raise ValueError("artifact recovery requires CPU-only JAX")
    checkpoint_hash_before = smoke.sha256(args.checkpoint)
    graph_hash_before = smoke.sha256(args.graph)
    recovered = load_checkpoint(args.checkpoint)
    initial = smoke.training.initialize_training_parameters()
    locomotion_adapter = smoke.networks.initialize_locomotion_adapter_parameters()
    locomotion_adapter_hash_before = smoke.tree_sha256(locomotion_adapter)
    checkpoint_parameters = recovered["parameters"]
    preregistration = json.loads(CALIBRATOR_PREREG.read_text(encoding="utf-8"))
    domain = json.loads(DOMAIN_PREREG.read_text(encoding="utf-8"))
    population = domain["evaluation_matrix"]["fixed_anchors"][
        : smoke.SMOKE_ENVIRONMENTS
    ]
    if [row["id"] for row in population] != contract["population"]["configuration_ids"]:
        raise ValueError("recovery population drifted")
    observer_type = smoke.load_runtime_observer(args.canonical_fit)

    stage1_batch_np, stage1_episodes, stage1_evidence = smoke.stage1_rollout(
        mujoco,
        scene_path,
        population,
        preregistration,
        observer_type,
        args.canonical_fit,
    )
    normalization = stage1_evidence.pop("normalization")
    target_mean = np.asarray(normalization.pop("mean"), dtype=np.float32)
    target_std = np.asarray(normalization.pop("std"), dtype=np.float32)
    stage1_batch = {key: jnp.asarray(value) for key, value in stage1_batch_np.items()}
    stage1_initial = smoke.training.stage1_parameters(initial)
    stage1_loss_grad = jax.value_and_grad(smoke.training.stage1_loss)
    stage1_loss_before, stage1_gradients = stage1_loss_grad(
        stage1_initial,
        stage1_batch,
        jnp.asarray(target_mean),
        jnp.asarray(target_std),
    )
    stage1_expected_moments = expected_moments(stage1_gradients, stage1_initial)
    stage1_m_comparison = tree_comparison(
        recovered["stage1"]["m"], stage1_expected_moments["m"]
    )
    stage1_v_comparison = tree_comparison(
        recovered["stage1"]["v"], stage1_expected_moments["v"]
    )
    stage1_expected_parameters = parameters_from_moments(
        stage1_initial,
        {"m": recovered["stage1"]["m"], "v": recovered["stage1"]["v"]},
        smoke.training.STAGE1_LEARNING_RATE,
    )
    stage1_checkpoint_parameters = {
        key: checkpoint_parameters[key] for key in smoke.training.ENCODER_AUXILIARY_KEYS
    }
    stage1_parameter_comparison = tree_comparison(
        stage1_checkpoint_parameters, stage1_expected_parameters
    )
    stage1_loss_after = smoke.training.stage1_loss(
        stage1_checkpoint_parameters,
        stage1_batch,
        jnp.asarray(target_mean),
        jnp.asarray(target_std),
    )
    after_stage1 = dict(initial)
    after_stage1.update(
        {key: jnp.asarray(value) for key, value in stage1_checkpoint_parameters.items()}
    )

    stage2_batch_np, stage2_episodes, onnx_observations = smoke.stage2_rollout(
        mujoco,
        scene_path,
        population,
        preregistration,
        observer_type,
        args.canonical_fit,
        after_stage1,
    )
    stage2_batch = {key: jnp.asarray(value) for key, value in stage2_batch_np.items()}
    stage2_initial = smoke.training.stage2_parameters(after_stage1)

    def stage2_objective(parameters: Mapping[str, Any]):
        return smoke.training.stage2_ppo_loss(
            parameters,
            stage2_batch,
            clip_epsilon=smoke.training.PPO_CLIP_EPSILON,
            value_coefficient=smoke.training.PPO_VALUE_COEFFICIENT,
            entropy_coefficient=smoke.training.PPO_ENTROPY_COEFFICIENT,
        )

    (stage2_loss_before, stage2_metrics_before), stage2_gradients = jax.value_and_grad(
        stage2_objective, has_aux=True
    )(stage2_initial)
    stage2_expected_moments = expected_moments(stage2_gradients, stage2_initial)
    stage2_m_comparison = tree_comparison(
        recovered["stage2"]["m"], stage2_expected_moments["m"]
    )
    stage2_v_comparison = tree_comparison(
        recovered["stage2"]["v"], stage2_expected_moments["v"]
    )
    stage2_expected_parameters = parameters_from_moments(
        stage2_initial,
        {"m": recovered["stage2"]["m"], "v": recovered["stage2"]["v"]},
        smoke.training.STAGE2_LEARNING_RATE,
    )
    stage2_expected_parameters = smoke.training.clamp_stage2_parameters(
        stage2_expected_parameters
    )
    stage2_checkpoint_parameters = {
        key: checkpoint_parameters[key]
        for key in (
            smoke.training.DEPLOYABLE_ACTION_KEYS
            + smoke.training.TRAINING_ONLY_STAGE2_KEYS
        )
    }
    stage2_parameter_comparison = tree_comparison(
        stage2_checkpoint_parameters, stage2_expected_parameters
    )
    stage2_loss_after, stage2_metrics_after = stage2_objective(
        stage2_checkpoint_parameters
    )

    action_bound_rng = np.random.default_rng(smoke.SMOKE_SEED)
    action_bound_exact = True
    for _ in range(256):
        raw = action_bound_rng.uniform(-1.5, 1.5, 14).astype(np.float32)
        previous = action_bound_rng.uniform(-1.0, 1.0, 14).astype(np.float32)
        action_bound_exact &= np.array_equal(
            smoke.bounded_action_numpy(raw, previous),
            np.asarray(
                smoke.training.bounded_action(jnp.asarray(raw), jnp.asarray(previous))
            ),
        )

    graph = smoke.onnx_contract(
        args.graph,
        smoke.training.deployable_parameters(checkpoint_parameters),
        onnx_observations,
    )
    support_canary = smoke.support_boundary_canary()
    observer_canary = corrected_observer_plant_canary(
        preregistration, observer_type, args.canonical_fit
    )
    force_ranges = smoke.force_range_contract(mujoco, scene_path)
    stage1_gradient_max = {
        key: float(np.max(np.abs(np.asarray(value))))
        for key, value in stage1_gradients.items()
    }
    stage1_deltas = smoke.training.leaf_max_abs_delta(
        stage1_initial, stage1_checkpoint_parameters
    )
    stage2_deltas = smoke.training.leaf_max_abs_delta(
        stage2_initial, stage2_checkpoint_parameters
    )
    stage1_valid = int(np.sum(stage1_batch_np["valid_mask"]))
    stage2_samples = int(np.sum(stage2_batch_np["valid_mask"]))
    stage2_valid = int(np.sum(stage2_batch_np["valid_transition_mask"]))
    plant_counts = Counter(row["plant"] for row in stage1_episodes)
    protected_after = {
        "half": smoke.sha256(args.policy_half),
        "final": smoke.sha256(args.policy_final),
    }
    checkpoint_hash_after = smoke.sha256(args.checkpoint)
    graph_hash_after = smoke.sha256(args.graph)

    checks = {
        "cpu_only": jax.default_backend() == "cpu"
        and all(device.platform == "cpu" for device in jax.devices()),
        "software_versions_exact": software_versions["exact"],
        "checkpoint_hash_exact_and_unchanged": checkpoint_hash_before
        == checkpoint_hash_after
        == EXPECTED_CHECKPOINT_SHA256,
        "graph_hash_exact_and_unchanged": graph_hash_before
        == graph_hash_after
        == EXPECTED_GRAPH_SHA256,
        "checkpoint_schema_exact": recovered["schema_exact"],
        "checkpoint_repeat_load_bit_exact": recovered["repeat_load_bit_exact"],
        "checkpoint_all_arrays_finite": recovered["all_arrays_finite"],
        "checkpoint_counts_exactly_one": recovered["stage1"]["count"] == 1
        and recovered["stage2"]["count"] == 1,
        "normalization_mean_bit_exact": np.array_equal(
            target_mean, recovered["target_mean"]
        ),
        "normalization_std_bit_exact": np.array_equal(
            target_std, recovered["target_std"]
        ),
        "stage1_moments_reproduce": stage1_m_comparison["bit_exact"]
        and stage1_v_comparison["bit_exact"],
        "stage1_parameters_reproduce": stage1_parameter_comparison["bit_exact"],
        "stage1_previous_action_gradient_nonzero": stage1_gradient_max[
            "previous_action_weight"
        ]
        > 0.0,
        "stage1_auxiliary_action_gradient_nonzero": stage1_gradient_max[
            "auxiliary_action_weight"
        ]
        > 0.0,
        "stage1_optimizer_schema_excludes_action_head": set(recovered["stage1"]["m"])
        == set(smoke.training.ENCODER_AUXILIARY_KEYS)
        and set(recovered["stage1"]["v"]) == set(smoke.training.ENCODER_AUXILIARY_KEYS),
        "stage2_moments_reproduce": stage2_m_comparison["bit_exact"]
        and stage2_v_comparison["bit_exact"],
        "stage2_parameters_reproduce": stage2_parameter_comparison["bit_exact"],
        "every_stage2_leaf_changed": all(
            value > 0.0 for value in stage2_deltas.values()
        ),
        "stage2_optimizer_schema_excludes_encoder_auxiliary": set(
            recovered["stage2"]["m"]
        )
        == set(
            smoke.training.DEPLOYABLE_ACTION_KEYS
            + smoke.training.TRAINING_ONLY_STAGE2_KEYS
        )
        and set(recovered["stage2"]["v"])
        == set(
            smoke.training.DEPLOYABLE_ACTION_KEYS
            + smoke.training.TRAINING_ONLY_STAGE2_KEYS
        ),
        "stage1_losses_gradients_finite": math.isfinite(float(stage1_loss_before))
        and math.isfinite(float(stage1_loss_after))
        and smoke.training.finite_tree(stage1_gradients),
        "stage2_losses_gradients_metrics_finite": smoke.training.finite_tree(
            {
                "before": stage2_loss_before,
                "after": stage2_loss_after,
                **stage2_metrics_before,
                **{
                    f"after_{key}": value for key, value in stage2_metrics_after.items()
                },
                **stage2_gradients,
            }
        ),
        "action_boundary_numpy_jax_bit_exact": bool(action_bound_exact),
        "exact_population": len(population) == smoke.SMOKE_ENVIRONMENTS
        and [row["id"] for row in population]
        == contract["population"]["configuration_ids"],
        "balanced_hidden_plants": plant_counts
        == Counter({smoke.PLANTS[0]: 8, smoke.PLANTS[1]: 8}),
        "all_initial_contacts_loaded": all(
            row["episode"]["initial_contacts"] == [1, 1]
            for row in stage1_episodes + stage2_episodes
        ),
        "stage1_has_valid_transitions": stage1_valid > 0,
        "stage2_has_valid_transitions": stage2_valid > 0,
        "stage2_attempted_samples_include_valid_transitions": stage2_samples
        >= stage2_valid
        > 0,
        "stage2_terminal_encoding_exact": terminal_encoding_exact(
            stage2_batch_np, stage2_episodes
        ),
        "realized_action_chain_exact": stage1_evidence["realized_action_chain_exact"],
        "fixed_p30_observer_slot_exact": stage1_evidence[
            "fixed_p30_observer_slot_exact"
        ],
        "support_boundary_canary_all_exact": all(support_canary.values()),
        "corrected_observer_canary_pass": observer_canary[
            "fixed_p30_observer_bit_exact_across_hidden_plant_choice"
        ]
        and observer_canary["hidden_physical_plants_are_distinct"],
        "xml_force_ranges_inside_independent_torque_limit": bool(
            force_ranges["actuator_count"] == 14
            and force_ranges["all_force_limited"]
            and force_ranges["all_ranges_within_independent_threshold"]
        ),
        "onnx_abi_exact": graph["abi_exact"],
        "onnx_initializers_finite": graph["all_initializers_finite"],
        "onnx_chain_outputs_finite": graph["all_chain_outputs_finite"],
        "onnx_training_only_tensors_absent": graph["training_only_tensors_absent"],
        "onnx_jax_error_at_most_1e_7": graph["jax_onnx_at_most_1e_7"],
        "onnx_previous_action_chain_exact": graph[
            "previous_action_out_equals_action_bit_exact"
        ],
        "protected_policies_bit_exact_and_unused": protected_before
        == protected_after
        == smoke.PROTECTED_POLICY_HASHES,
        "locomotion_adapter_bit_exact_and_unused": smoke.tree_sha256(locomotion_adapter)
        == locomotion_adapter_hash_before,
        "log_std_clamp_respected": bool(
            np.all(
                stage2_checkpoint_parameters["training_only_log_std"]
                >= smoke.training.LOG_STD_MIN
            )
            and np.all(
                stage2_checkpoint_parameters["training_only_log_std"]
                <= smoke.training.LOG_STD_MAX
            )
        ),
        "no_new_optimizer_update_or_candidate_artifact": True,
    }
    failed = [name for name, passed in checks.items() if not passed]
    passed = not failed
    payload = {
        "schema_version": "winner_v12.calibrator_artifact_recovery_result.v1",
        "status": (
            "PASS_WINNER_V12_CALIBRATOR_ARTIFACT_RECOVERY"
            if passed
            else "HOLD_WINNER_V12_CALIBRATOR_ARTIFACT_RECOVERY"
        ),
        "decision": (
            "AUTHORIZE_FULL_CALIBRATOR_TRAINING_PREREGISTRATION_ONLY"
            if passed
            else "STOP_WINNER_V12_CALIBRATOR_ROUTE"
        ),
        "contract": {
            "path": str(args.contract),
            "canonical_lf_sha256": smoke.lf_sha256(args.contract),
            "hash_mode": "lf",
        },
        "failed_smoke": {
            "run_id": failure["github"]["run_id"],
            "checkpoint_sha256": checkpoint_hash_before,
            "graph_sha256": graph_hash_before,
        },
        "environment": {
            "software_versions": software_versions,
            "playground_commit": smoke.CONTROL_COMMIT,
            "composition_receipt": playground_receipt,
        },
        "execution": {
            "optimizer_updates": {"stage1": 0, "stage2": 0},
            "new_checkpoints_written": 0,
            "new_onnx_graphs_written": 0,
            "formal_support_cells": 0,
            "locomotion_training_steps": 0,
            "locomotion_behavior_cells": 0,
            "protected_policy_inference_calls": 0,
            "robot_or_rdk_access": 0,
            "retry_of_failed_smoke": False,
        },
        "population": {
            "configuration_ids": [row["id"] for row in population],
            "plant_counts": dict(plant_counts),
            "stage1_valid_transitions": stage1_valid,
            "stage2_attempted_samples": stage2_samples,
            "stage2_valid_transitions": stage2_valid,
        },
        "stage1": {
            "loss_before": float(stage1_loss_before),
            "loss_after": float(stage1_loss_after),
            "gradient_max_abs_by_leaf": stage1_gradient_max,
            "parameter_max_abs_delta_by_leaf": stage1_deltas,
            "m_comparison": stage1_m_comparison,
            "v_comparison": stage1_v_comparison,
            "parameter_comparison": stage1_parameter_comparison,
            "normalization": normalization,
            "rollout": stage1_evidence,
            "episodes": stage1_episodes,
        },
        "stage2": {
            "loss_before": float(stage2_loss_before),
            "loss_after": float(stage2_loss_after),
            "metrics_before": {
                key: float(value) for key, value in stage2_metrics_before.items()
            },
            "metrics_after": {
                key: float(value) for key, value in stage2_metrics_after.items()
            },
            "parameter_max_abs_delta_by_leaf": stage2_deltas,
            "m_comparison": stage2_m_comparison,
            "v_comparison": stage2_v_comparison,
            "parameter_comparison": stage2_parameter_comparison,
            "episodes": stage2_episodes,
        },
        "support_boundary_canary": support_canary,
        "corrected_observer_plant_canary": observer_canary,
        "force_range_contract": force_ranges,
        "onnx": graph,
        "checks": checks,
        "failed_checks": failed,
        "authority": {
            "full_training_executed": False,
            "formal_behavior_evaluation_executed": False,
            "robot_clearance": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "pass_authorizes_only": (
                "a separate prospective full-calibrator training preregistration"
            ),
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": payload["status"],
                "failed_checks": failed,
                "result_sha256": smoke.sha256(args.output),
            },
            sort_keys=True,
        )
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
