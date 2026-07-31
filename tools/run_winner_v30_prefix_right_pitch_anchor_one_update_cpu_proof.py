#!/usr/bin/env python3
"""Run exactly one frozen Winner-v30 prefix-anchor optimizer update on CPU."""

from __future__ import annotations

import argparse
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
import run_winner_v29_prefix_right_pitch_anchor_cpu_contract as v29_runner  # noqa: E402
import winner_v29_prefix_right_pitch_anchor as v29  # noqa: E402


CONTRACT = ANALYSIS / "winner_v30_prefix_right_pitch_anchor_one_update_cpu_contract.json"
V29_RESULT = ANALYSIS / "winner_v29_prefix_right_pitch_anchor_cpu_result.json"
V22_TRAINING = ANALYSIS / "winner_v22_normalized_predictor_training_result.json"
V24_TRAINING = ANALYSIS / "winner_v24_baseline_anchored_training_result.json"
FULL_PREREG = ANALYSIS / "winner_v12_full_calibrator_training_preregistration.json"
DOMAIN = ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
ROLLOUT_UPDATE_INDEX = 200
SOURCE_OPTIMIZER_COUNT = 200
RESULT_OPTIMIZER_COUNT = 201
FROZEN_ANCHOR_SCALE = np.float32(197.3112030029297)


def validate_contract(value: Mapping[str, Any]) -> None:
    if (
        value.get("schema_version")
        != "winner_v30.prefix_right_pitch_anchor_one_update_cpu_contract.v1"
        or value.get("status")
        != "PREREGISTERED_WINNER_V30_PREFIX_RIGHT_PITCH_ANCHOR_ONE_UPDATE_CPU_PROOF"
        or value.get("decision")
        != "AUTHORIZE_EXACT_ONE_PREFIX_RIGHT_PITCH_ANCHOR_OPTIMIZER_UPDATE_ONLY"
        or value.get("execution_now")
        != {
            "rollout_episode_slots": 0,
            "optimizer_updates": 0,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        }
        or value.get("execution_future")
        != {
            "rollout_episode_slots": 80,
            "optimizer_updates": 1,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        }
    ):
        raise ValueError("Winner-v30 authority changed")
    if value.get("objective") != {
        "candidate_checkpoint": {"label": "winner_v24_final", "update": 200},
        "teacher_checkpoint": {"label": "winner_v22_final", "update": 100},
        "rollout_update_index": ROLLOUT_UPDATE_INDEX,
        "selected_training_configuration_ids": list(
            v29.SELECTED_TRAINING_CONFIGURATION_IDS
        ),
        "prefix_ticks": list(range(v29.PREFIX_TICKS)),
        "action_indices": list(v29.RIGHT_PITCH_ACTION_INDICES),
        "selected_elements": v29.EXPECTED_ANCHOR_ELEMENTS,
        "anchor_scale": float(FROZEN_ANCHOR_SCALE),
        "baseline": (
            "unchanged Winner-v24 baseline-anchored PPO gradient plus frozen Winner-v22 "
            "normalized-predictor gradient at scale 380.9135437011719"
        ),
        "combined_gradient": (
            "baseline combined gradient plus 197.3112030029297 times the frozen "
            "Winner-v29 prefix-anchor gradient"
        ),
        "optimizer": "restore exact Winner-v24 Adam count 200 and execute one update to 201",
        "post_update_gate": (
            "on the identical frozen batch, selected raw anchor MSE must be finite and "
            "strictly lower after the update"
        ),
        "no_action_replacement": True,
    }:
        raise ValueError("Winner-v30 objective changed")
    sources = value.get("sources")
    if not isinstance(sources, dict) or not sources:
        raise ValueError("Winner-v30 source manifest is absent")
    for name, item in sources.items():
        path = ROOT / item["path"]
        if (
            set(item) != {"hash_mode", "path", "sha256"}
            or item["hash_mode"] != "lf"
            or not path.is_file()
            or common.lf_sha256(path) != item["sha256"]
        ):
            raise ValueError(f"Winner-v30 source changed: {name}")
    if common.canonical_sha256(sources) != value.get("source_manifest_sha256"):
        raise ValueError("Winner-v30 source manifest changed")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--canonical-fit", type=Path, required=True)
    parser.add_argument("--v22-training-work-root", type=Path, required=True)
    parser.add_argument("--v24-training-work-root", type=Path, required=True)
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--offline-cpu-only", action="store_true")
    parser.add_argument(
        "--one-update-prefix-right-pitch-anchor-proof-authorized",
        action="store_true",
    )
    args = parser.parse_args()
    if (
        not args.offline_cpu_only
        or not args.one_update_prefix_right_pitch_anchor_proof_authorized
    ):
        raise PermissionError(
            "Winner-v30 proof requires --offline-cpu-only and "
            "--one-update-prefix-right-pitch-anchor-proof-authorized"
        )
    if args.work_root.exists() or args.output.exists():
        raise FileExistsError("refusing to overwrite Winner-v30 evidence")

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

    if jax.default_backend() != "cpu" or any(
        device.platform != "cpu" for device in jax.devices()
    ):
        raise ValueError("Winner-v30 requires CPU-only JAX")
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    validate_contract(contract)
    zero_update = json.loads(V29_RESULT.read_text(encoding="utf-8"))
    if (
        zero_update.get("status")
        != "PASS_WINNER_V29_PREFIX_RIGHT_PITCH_ANCHOR_CPU_CONTRACT"
        or zero_update.get("decision")
        != "AUTHORIZE_SEPARATE_ONE_UPDATE_PREFIX_RIGHT_PITCH_ANCHOR_CPU_PROOF_PREREGISTRATION_ONLY"
        or zero_update.get("failed_checks") != []
        or zero_update.get("execution")
        != {
            "rollout_episode_slots": 80,
            "optimizer_updates": 0,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        }
        or float(zero_update["objective_evidence"]["anchor_scale"])
        != float(FROZEN_ANCHOR_SCALE)
    ):
        raise ValueError("Winner-v30 source authority changed")
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
    v29_runner.validate_artifact(
        source_snapshot_path, source_receipt["source_snapshot"], "teacher snapshot"
    )
    v29_runner.validate_artifact(
        source_graph_path, source_receipt["source_graph"], "teacher graph"
    )
    v29_runner.validate_artifact(
        candidate_snapshot_path,
        candidate_receipt["final"]["snapshot"],
        "candidate snapshot",
    )
    v29_runner.validate_artifact(
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
        raise ValueError("Winner-v30 software environment changed")
    if smoke.sha256(args.canonical_fit) != smoke.P30_FIT_LF_SHA256:
        raise ValueError("Winner-v30 canonical P30 fit changed")
    if smoke.git_output(args.playground_root, "rev-parse", "HEAD") != smoke.CONTROL_COMMIT:
        raise ValueError("Winner-v30 Playground source changed")
    smoke.validate_playground_tree(args.playground_root)
    scene = args.playground_root / smoke.SCENE_RELATIVE
    if smoke.sha256(scene) != smoke.SCENE_SHA256:
        raise ValueError("Winner-v30 scene changed")

    v22_gate.smoke = smoke
    v22_gate.training = training
    v22_gate.v21 = v21
    teacher = v22v2.load_snapshot(source_snapshot_path)
    candidate = v22v2.load_snapshot(candidate_snapshot_path)
    v22_gate._validate_snapshot(teacher, expected_stage="normalized_predictor_joint_stage2")
    if (
        teacher["metadata"].get("completed_updates") != 100
        or int(np.asarray(teacher["optimizer"]["count"])) != 100
        or candidate["metadata"].get("stage")
        != "baseline_anchored_symmetric_failure_joint_stage2"
        or candidate["metadata"].get("completed_updates") != SOURCE_OPTIMIZER_COUNT
        or int(np.asarray(candidate["optimizer"]["count"])) != SOURCE_OPTIMIZER_COUNT
    ):
        raise ValueError("Winner-v30 restore boundary changed")
    if not np.array_equal(teacher["target_mean"], candidate["target_mean"]) or not np.array_equal(
        teacher["target_std"], candidate["target_std"]
    ):
        raise ValueError("Winner-v30 target normalizer changed")

    teacher_parameters = teacher["parameters"]
    parameters = candidate["parameters"]
    optimizer = candidate["optimizer"]
    source_parameters_copy = {
        key: np.asarray(value).copy() for key, value in parameters.items()
    }
    source_optimizer_copy = {
        "count": np.asarray(optimizer["count"]).copy(),
        "m": {key: np.asarray(value).copy() for key, value in optimizer["m"].items()},
        "v": {key: np.asarray(value).copy() for key, value in optimizer["v"].items()},
    }
    population = full.training_population(
        json.loads(FULL_PREREG.read_text(encoding="utf-8")),
        json.loads(DOMAIN.read_text(encoding="utf-8")),
    )
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
        key
        for key in batch_np
        if not np.array_equal(batch_np[key], objective_batch_np[key])
    )
    failure_mask = v24.roll_pitch_failure_mask(
        episodes, shape=np.asarray(batch_np["rewards"]).shape
    )
    batch = {key: jnp.asarray(value) for key, value in objective_batch_np.items()}
    before = v21.joint_trainable_parameters(parameters)
    teacher_trainable = v21.joint_trainable_parameters(teacher_parameters)
    target_mean = jnp.asarray(candidate["target_mean"], dtype=jnp.float32)
    target_std = jnp.asarray(candidate["target_std"], dtype=jnp.float32)

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

    (ppo_loss, ppo_metrics), ppo_gradients = jax.value_and_grad(
        ppo_objective, has_aux=True
    )(before)
    (predictor_loss, predictor_metrics), predictor_gradients = jax.value_and_grad(
        predictor_objective, has_aux=True
    )(before)
    (anchor_loss_before, anchor_metrics), anchor_gradients = jax.value_and_grad(
        anchor_objective, has_aux=True
    )(before)
    baseline_gradients = v22v2.compose_gradients(ppo_gradients, predictor_gradients)
    recomputed_scale, balance = v29.gradient_balance_scale(
        baseline_gradients, anchor_gradients
    )
    gradients = v29.compose_gradients(
        baseline_gradients, anchor_gradients, FROZEN_ANCHOR_SCALE, enabled=True
    )
    combined_loss = (
        ppo_loss
        + jnp.asarray(v22v2.FROZEN_PREDICTOR_SCALE, dtype=jnp.float32)
        * predictor_loss
        + jnp.asarray(FROZEN_ANCHOR_SCALE, dtype=jnp.float32) * anchor_loss_before
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
    anchor_loss_after, anchor_metrics_after = anchor_objective(after)
    gradient_max = common.tree_max_abs(gradients)
    leaf_delta = v20.leaf_max_abs_delta(before, after)
    expected_stored = int(
        np.sum(
            batch_np["valid_transition_mask"][:, :-1]
            * batch_np["valid_mask"][:, 1:]
        )
    )
    source_unchanged_before_update = all(
        np.array_equal(source_parameters_copy[key], np.asarray(parameters[key]))
        for key in source_parameters_copy
    ) and common.tree_equal(source_optimizer_copy["m"], optimizer["m"])
    exact_v29_batch = (
        episode_hash == zero_update["rollout_evidence"]["episode_receipts_sha256"]
        and v29_runner.array_sha256(batch_np["observations"])
        == zero_update["rollout_evidence"]["observations_sha256"]
        and v29_runner.array_sha256(batch_np["previous_actions"])
        == zero_update["rollout_evidence"]["previous_actions_sha256"]
        and v29_runner.array_sha256(anchor_mask)
        == zero_update["rollout_evidence"]["anchor_mask_sha256"]
        and {
            key: v29_runner.array_sha256(value)
            for key, value in sorted(objective_batch_np.items())
        }
        == zero_update["rollout_evidence"]["transition_hashes"]
    )
    exact_v29_objective = (
        float(anchor_loss_before)
        == zero_update["objective_evidence"]["raw_anchor_loss"]
        and float(recomputed_scale) == float(FROZEN_ANCHOR_SCALE)
        and balance == zero_update["objective_evidence"]["balance"]
        and common.tree_max_abs(anchor_gradients)
        == zero_update["objective_evidence"]["anchor_gradient_max_abs"]
    )
    if not training.finite_tree(
        {
            "ppo_loss": ppo_loss,
            "ppo_metrics": ppo_metrics,
            "predictor_loss": predictor_loss,
            "predictor_metrics": predictor_metrics,
            "anchor_loss_before": anchor_loss_before,
            "anchor_loss_after": anchor_loss_after,
            "combined_loss": combined_loss,
            "gradients": gradients,
            "parameters": parameters_after,
            "optimizer": optimizer_after,
        }
    ):
        raise FloatingPointError("Winner-v30 one-update state is nonfinite")

    args.work_root.mkdir(parents=True, exist_ok=False)
    graph = args.work_root / "winner_v30_prefix_right_pitch_anchor_update_201.onnx"
    networks.export_calibrator_onnx(training.deployable_parameters(parameters_after), graph)
    graph_contract = smoke.onnx_contract(graph, parameters_after, observations)
    snapshot_path = args.work_root / "winner_v30_prefix_right_pitch_anchor_update_201.npz"
    snapshot_receipt = v22v2.save_snapshot(
        snapshot_path,
        parameters_after,
        optimizer_after,
        {
            "stage": "prefix_right_pitch_anchor_joint_stage2",
            "completed_updates": RESULT_OPTIMIZER_COUNT,
            "source_completed_updates": SOURCE_OPTIMIZER_COUNT,
            "source_snapshot_sha256": candidate_receipt["final"]["snapshot"]["sha256"],
            "teacher_snapshot_sha256": source_receipt["source_snapshot"]["sha256"],
            "objective": contract["objective"],
            "root_seed": 120120,
            "learning_rate": float(training.STAGE2_LEARNING_RATE),
            "predictor_scale": float(v22v2.FROZEN_PREDICTOR_SCALE),
            "anchor_scale": float(FROZEN_ANCHOR_SCALE),
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        candidate["target_mean"],
        candidate["target_std"],
    )
    loaded = v22v2.load_snapshot(snapshot_path)
    snapshot_exact = bool(
        common.tree_equal(parameters_after, loaded["parameters"])
        and np.array_equal(optimizer_after["count"], loaded["optimizer"]["count"])
        and common.tree_equal(optimizer_after["m"], loaded["optimizer"]["m"])
        and common.tree_equal(optimizer_after["v"], loaded["optimizer"]["v"])
        and np.array_equal(candidate["target_mean"], loaded["target_mean"])
        and np.array_equal(candidate["target_std"], loaded["target_std"])
        and loaded["metadata"].get("stage")
        == "prefix_right_pitch_anchor_joint_stage2"
        and loaded["metadata"].get("completed_updates") == RESULT_OPTIMIZER_COUNT
    )
    checks = {
        "source_v29_zero_update_result_exact": True,
        "source_teacher_and_candidate_artifacts_exact": True,
        "source_snapshot_and_optimizer_count_200_exact": True,
        "exact_v29_update_200_batch_reproduced": exact_v29_batch,
        "exact_v29_anchor_loss_gradient_and_scale_reproduced": exact_v29_objective,
        "exact_80_episode_population": len(episodes) == 80,
        "action_boundary_exact": boundary["realized_equals_numpy_bit_exact"]
        and boundary["numpy_equals_jax_bit_exact"],
        "pitch_margin_reward_exact": reward["reward_formula_bit_exact"],
        "v24_baseline_objective_exact": (
            int(np.sum(failure_mask)) > 0
            and changed_keys == list(v24v2.MODIFIED_BATCH_KEYS)
            and objective_evidence["zero_failure_bit_exact_noop"] is False
        ),
        "selected_384_anchor_elements_exact": int(np.sum(anchor_mask))
        == v29.EXPECTED_ANCHOR_ELEMENTS,
        "sampled_hidden_replay_at_most_1e_6": float(
            ppo_metrics["sampled_hidden_replay_max_abs_error"]
        )
        <= 1.0e-6,
        "stored_successor_mask_exact_nonzero": int(
            predictor_metrics["stored_successor_transition_count"]
        )
        == expected_stored
        and expected_stored > 0,
        "all_12_combined_gradients_nonzero": set(gradient_max)
        == set(v21.JOINT_TRAINABLE_KEYS)
        and all(value > 0.0 for value in gradient_max.values()),
        "all_12_trainable_leaves_changed": set(leaf_delta)
        == set(v21.JOINT_TRAINABLE_KEYS)
        and all(value > 0.0 for value in leaf_delta.values()),
        "source_state_unchanged_before_update": source_unchanged_before_update,
        "exactly_one_optimizer_update_200_to_201": int(
            np.asarray(optimizer_after["count"])
        )
        == RESULT_OPTIMIZER_COUNT,
        "same_batch_anchor_loss_strictly_decreases": math.isfinite(
            float(anchor_loss_after)
        )
        and float(anchor_loss_after) < float(anchor_loss_before),
        "all_losses_metrics_parameters_optimizer_finite": True,
        "snapshot_readback_exact": snapshot_exact,
        "onnx_abi_exact": graph_contract["abi_exact"],
        "onnx_training_only_tensors_absent": graph_contract[
            "training_only_tensors_absent"
        ],
        "onnx_jax_chain_at_most_1e_7": graph_contract["jax_onnx_at_most_1e_7"],
        "onnx_previous_action_chain_exact": graph_contract[
            "previous_action_out_equals_action_bit_exact"
        ],
        "formal_support_locomotion_robot_zero": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    result = {
        "schema_version": "winner_v30.prefix_right_pitch_anchor_one_update_cpu_result.v1",
        "status": (
            "PASS_WINNER_V30_PREFIX_RIGHT_PITCH_ANCHOR_ONE_UPDATE_CPU_PROOF"
            if not failed
            else "HOLD_WINNER_V30_PREFIX_RIGHT_PITCH_ANCHOR_ONE_UPDATE_CPU_PROOF"
        ),
        "decision": (
            "AUTHORIZE_SEPARATE_PREFIX_RIGHT_PITCH_ANCHOR_TRAINING_PREREGISTRATION_ONLY"
            if not failed
            else "DO_NOT_TRAIN_PREFIX_RIGHT_PITCH_ANCHOR_OBJECTIVE"
        ),
        "checks": {name: bool(value) for name, value in checks.items()},
        "failed_checks": failed,
        "source_identity": {
            "teacher_snapshot": source_receipt["source_snapshot"],
            "teacher_graph": source_receipt["source_graph"],
            "candidate_snapshot": candidate_receipt["final"]["snapshot"],
            "candidate_graph": candidate_receipt["final"]["graph"],
        },
        "objective": contract["objective"],
        "rollout": {
            "update_index": ROLLOUT_UPDATE_INDEX,
            "episode_slots": len(episodes),
            "episode_receipts_sha256": episode_hash,
            "roll_pitch_failure_count": int(np.sum(failure_mask)),
            "sampled_count": int(np.sum(batch_np["valid_mask"])),
            "valid_transition_count": int(
                np.sum(batch_np["valid_transition_mask"])
            ),
            "stored_successor_transition_count": expected_stored,
            "changed_batch_keys": changed_keys,
            "selected_anchor_elements": int(np.sum(anchor_mask)),
            "exact_v29_batch_reproduced": exact_v29_batch,
            "exact_v29_objective_reproduced": exact_v29_objective,
        },
        "optimization": {
            "optimizer_count_before": SOURCE_OPTIMIZER_COUNT,
            "optimizer_count_after": int(np.asarray(optimizer_after["count"])),
            "ppo_loss": float(ppo_loss),
            "normalized_predictor_loss": float(predictor_loss),
            "anchor_loss_before": float(anchor_loss_before),
            "anchor_loss_after": float(anchor_loss_after),
            "anchor_loss_delta": float(anchor_loss_after - anchor_loss_before),
            "maximum_selected_action_delta_before": float(
                anchor_metrics["maximum_selected_action_delta"]
            ),
            "maximum_selected_action_delta_after": float(
                anchor_metrics_after["maximum_selected_action_delta"]
            ),
            "combined_loss": float(combined_loss),
            "predictor_scale": float(v22v2.FROZEN_PREDICTOR_SCALE),
            "anchor_scale": float(FROZEN_ANCHOR_SCALE),
            "combined_gradient_max_abs": gradient_max,
            "leaf_max_abs_delta": leaf_delta,
            "trainable_leaves": list(v21.JOINT_TRAINABLE_KEYS),
            "source_state_unchanged_before_update": source_unchanged_before_update,
            "snapshot_readback_exact": snapshot_exact,
        },
        "snapshot": snapshot_receipt,
        "graph": {
            "path": str(graph),
            "sha256": common.sha256(graph),
            "bytes": graph.stat().st_size,
            "contract": graph_contract,
        },
        "execution": {
            "rollout_episode_slots": len(episodes),
            "optimizer_updates": 1,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "environment": {
            "jax_backend": jax.default_backend(),
            "jax_devices": [str(device) for device in jax.devices()],
            "mujoco_version": mujoco.__version__,
        },
        "sources": contract["sources"],
        "source_manifest_sha256": contract["source_manifest_sha256"],
        "authority": {
            "robot_clearance": False,
            "training_executed": False,
            "formal_support_gate_executed": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "pass_authorizes_only": (
                "a separate frozen prefix right-pitch anchor training preregistration"
            ),
        },
    }
    if not all(
        math.isfinite(float(value))
        for value in (
            ppo_loss,
            predictor_loss,
            anchor_loss_before,
            anchor_loss_after,
            combined_loss,
            *gradient_max.values(),
            *leaf_delta.values(),
        )
    ):
        raise FloatingPointError("Winner-v30 result is nonfinite")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(result["status"])
    for name in failed:
        print(f"FAILED={name}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
