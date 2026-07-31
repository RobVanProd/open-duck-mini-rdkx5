#!/usr/bin/env python3
"""Run one frozen Winner-v24 baseline-anchored optimizer update on CPU."""

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

CONTRACT = ANALYSIS / "winner_v24_baseline_anchored_one_update_cpu_contract.json"
ZERO_UPDATE_RESULT = ANALYSIS / "winner_v24_baseline_anchored_cpu_result_v2.json"
V22_TRAINING = ANALYSIS / "winner_v22_normalized_predictor_training_result.json"
FULL_PREREG = ANALYSIS / "winner_v12_full_calibrator_training_preregistration.json"
DOMAIN = ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
ROLLOUT_UPDATE_INDEX = 100


def validate_contract(value: Mapping[str, Any], common: Any) -> None:
    if (
        value.get("schema_version")
        != "winner_v24.baseline_anchored_one_update_cpu_contract.v1"
        or value.get("status")
        != "FROZEN_WINNER_V24_BASELINE_ANCHORED_ONE_UPDATE_CPU_CONTRACT"
        or value.get("decision")
        != "AUTHORIZE_EXACT_ONE_BASELINE_ANCHORED_OPTIMIZER_UPDATE_ONLY"
        or value.get("execution_now")
        != {
            "rollout_episode_slots": 0,
            "optimizer_updates": 0,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        }
    ):
        raise ValueError("Winner-v24 one-update contract changed")
    if value.get("execution_future") != {
        "rollout_episode_slots": 80,
        "optimizer_updates": 1,
        "formal_support_cells": 0,
        "locomotion_steps": 0,
        "robot_or_rdk_access": 0,
    }:
        raise ValueError("Winner-v24 one-update execution changed")
    sources = value.get("sources")
    if not isinstance(sources, dict) or not sources:
        raise ValueError("Winner-v24 one-update sources are absent")
    for name, item in sources.items():
        path = ROOT / item["path"]
        if (
            set(item) != {"hash_mode", "path", "sha256"}
            or item["hash_mode"] != "lf"
            or common.lf_sha256(path) != item["sha256"]
        ):
            raise ValueError(f"Winner-v24 one-update source changed: {name}")
    if common.canonical_sha256(sources) != value.get("source_manifest_sha256"):
        raise ValueError("Winner-v24 one-update source manifest changed")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--canonical-fit", type=Path, required=True)
    parser.add_argument("--final-snapshot", type=Path, required=True)
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--offline-cpu-only", action="store_true")
    parser.add_argument(
        "--one-update-baseline-anchored-proof-authorized", action="store_true"
    )
    args = parser.parse_args()
    if (
        not args.offline_cpu_only
        or not args.one_update_baseline_anchored_proof_authorized
    ):
        raise PermissionError(
            "Winner-v24 one-update proof requires --offline-cpu-only "
            "--one-update-baseline-anchored-proof-authorized"
        )
    if args.work_root.exists() or args.output.exists():
        raise FileExistsError("refusing to overwrite Winner-v24 one-update evidence")

    import jax
    import jax.numpy as jnp
    import mujoco
    import run_winner_v12_calibrator_cpu_smoke as smoke
    import run_winner_v12_full_calibrator_training as full
    import run_winner_v22_normalized_predictor_support_gate as v22_gate
    import run_winner_v24_symmetric_failure_cpu_contract as common
    import winner_v12_calibrator_training as training
    import winner_v12_decomposed_backend_networks as networks
    import winner_v15_pitch_margin_support as v15
    import winner_v20_joint_recurrent_support as v20
    import winner_v21_predictor_preserving_joint_support as v21
    import winner_v22_normalized_predictor as v22
    import winner_v22_normalized_predictor_v2 as v22v2
    import winner_v24_symmetric_support_failure as v24
    import winner_v24_symmetric_support_failure_v2 as v24v2

    if jax.default_backend() != "cpu" or any(
        device.platform != "cpu" for device in jax.devices()
    ):
        raise ValueError("Winner-v24 one-update proof requires CPU-only JAX")
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    validate_contract(contract, common)
    zero_update = json.loads(ZERO_UPDATE_RESULT.read_text(encoding="utf-8"))
    training_result = json.loads(V22_TRAINING.read_text(encoding="utf-8"))
    if (
        zero_update.get("status")
        != "PASS_WINNER_V24_BASELINE_ANCHORED_CPU_CONTRACT"
        or zero_update.get("decision")
        != "AUTHORIZE_SEPARATE_ONE_UPDATE_BASELINE_ANCHORED_CPU_PROOF_PREREGISTRATION_ONLY"
        or zero_update.get("failed_checks") != []
        or zero_update.get("execution")
        != {
            "rollout_episode_slots": 80,
            "optimizer_updates": 0,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        }
        or training_result.get("status")
        != "PASS_WINNER_V22_NORMALIZED_PREDICTOR_TRAINING_ARTIFACT"
        or training_result.get("failed_checks") != []
    ):
        raise ValueError("Winner-v24 one-update source evidence changed")
    final_receipt = training_result["snapshot_manifest"][99]
    if (
        final_receipt.get("completed_updates") != 100
        or common.sha256(args.final_snapshot) != final_receipt.get("sha256")
        or args.final_snapshot.stat().st_size != final_receipt.get("bytes")
    ):
        raise ValueError("Winner-v24 one-update snapshot bytes changed")

    expected_versions = dict(
        json.loads(FULL_PREREG.read_text(encoding="utf-8"))[
            "implementation_contract_environment"
        ]
    )
    if expected_versions.pop("platform") != "CPU only" or not smoke.validate_software_versions(
        {"software_versions": expected_versions}
    )["exact"]:
        raise ValueError("Winner-v24 one-update software environment changed")
    if smoke.sha256(args.canonical_fit) != smoke.P30_FIT_LF_SHA256:
        raise ValueError("Winner-v24 one-update P30 fit changed")
    if smoke.git_output(args.playground_root, "rev-parse", "HEAD") != smoke.CONTROL_COMMIT:
        raise ValueError("Winner-v24 one-update Playground source changed")
    smoke.validate_playground_tree(args.playground_root)
    scene = args.playground_root / smoke.SCENE_RELATIVE
    if smoke.sha256(scene) != smoke.SCENE_SHA256:
        raise ValueError("Winner-v24 one-update scene changed")

    v22_gate.smoke = smoke
    v22_gate.training = training
    v22_gate.v21 = v21
    restored = v22v2.load_snapshot(args.final_snapshot)
    v22_gate._validate_snapshot(
        restored, expected_stage="normalized_predictor_joint_stage2"
    )
    if (
        restored["metadata"].get("completed_updates") != 100
        or int(np.asarray(restored["optimizer"]["count"])) != 100
    ):
        raise ValueError("Winner-v24 one-update restore boundary changed")
    source_parameters = {
        key: np.asarray(value).copy()
        for key, value in restored["parameters"].items()
    }
    source_optimizer = {
        "count": np.asarray(restored["optimizer"]["count"]).copy(),
        "m": {
            key: np.asarray(value).copy()
            for key, value in restored["optimizer"]["m"].items()
        },
        "v": {
            key: np.asarray(value).copy()
            for key, value in restored["optimizer"]["v"].items()
        },
    }
    parameters = restored["parameters"]
    optimizer = restored["optimizer"]
    population = full.training_population(
        json.loads(FULL_PREREG.read_text(encoding="utf-8")),
        json.loads(DOMAIN.read_text(encoding="utf-8")),
    )
    if len(population) != 80:
        raise ValueError("Winner-v24 one-update population changed")
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
    _, values = training.stage2_mean_value(
        parameters, jnp.asarray(batch_np["hidden"], dtype=jnp.float32)
    )
    values_np = np.asarray(values, dtype=np.float32)
    default_batch, default_evidence = v24v2.apply_baseline_anchored_objective(
        batch_np,
        episodes,
        values_np,
        enabled=False,
        gamma=training.PPO_GAMMA,
        gae_lambda=training.PPO_GAE_LAMBDA,
    )
    objective_batch_np, objective_evidence = v24v2.apply_baseline_anchored_objective(
        batch_np,
        episodes,
        values_np,
        enabled=True,
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
    settled_count = sum(
        receipt.get("terminal_success_bonus_applied") is True for receipt in episodes
    )
    default_exact = all(
        np.array_equal(default_batch[key], np.asarray(batch_np[key]))
        for key in batch_np
    ) and default_evidence["modified_batch_keys"] == []
    objective_locality_exact = bool(
        changed_keys == list(v24v2.MODIFIED_BATCH_KEYS)
        and np.all(
            objective_batch_np["rewards"][failure_mask]
            == v24v2.SYMMETRIC_FAILURE_PENALTY
        )
        and np.array_equal(
            objective_batch_np["rewards"][~failure_mask],
            np.asarray(batch_np["rewards"])[~failure_mask],
        )
    )

    batch = {key: jnp.asarray(value) for key, value in objective_batch_np.items()}
    before = v21.joint_trainable_parameters(parameters)
    target_mean = jnp.asarray(restored["target_mean"], dtype=jnp.float32)
    target_std = jnp.asarray(restored["target_std"], dtype=jnp.float32)

    def ppo_objective(values_tree: Mapping[str, Any], data: Mapping[str, Any]):
        return v20.joint_recurrent_ppo_loss(
            values_tree,
            data,
            clip_epsilon=training.PPO_CLIP_EPSILON,
            value_coefficient=training.PPO_VALUE_COEFFICIENT,
            entropy_coefficient=training.PPO_ENTROPY_COEFFICIENT,
        )

    def predictor_objective(values_tree: Mapping[str, Any], data: Mapping[str, Any]):
        return v22.normalized_predictor_loss(values_tree, data, target_mean, target_std)

    (ppo_loss, ppo_metrics), ppo_gradients = jax.value_and_grad(
        ppo_objective, has_aux=True
    )(before, batch)
    (predictor_loss, predictor_metrics), predictor_gradients = jax.value_and_grad(
        predictor_objective, has_aux=True
    )(before, batch)
    gradients = v22v2.compose_gradients(ppo_gradients, predictor_gradients)
    combined_loss = ppo_loss + jnp.asarray(v22v2.FROZEN_PREDICTOR_SCALE) * predictor_loss
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
    gradient_max = common.tree_max_abs(gradients)
    leaf_delta = v20.leaf_max_abs_delta(before, after)
    expected_stored = int(
        np.sum(
            batch_np["valid_transition_mask"][:, :-1]
            * batch_np["valid_mask"][:, 1:]
        )
    )
    source_unchanged_before_update = all(
        np.array_equal(source_parameters[key], np.asarray(parameters[key]))
        for key in source_parameters
    ) and common.tree_equal(source_optimizer["m"], optimizer["m"])
    if not training.finite_tree(
        {
            "ppo_loss": ppo_loss,
            "ppo_metrics": ppo_metrics,
            "predictor_loss": predictor_loss,
            "predictor_metrics": predictor_metrics,
            "combined_loss": combined_loss,
            "gradients": gradients,
            "parameters": parameters_after,
            "optimizer": optimizer_after,
        }
    ):
        raise FloatingPointError("Winner-v24 one-update state is nonfinite")

    args.work_root.mkdir(parents=True, exist_ok=False)
    graph = args.work_root / "winner_v24_baseline_anchored_update_101.onnx"
    networks.export_calibrator_onnx(
        training.deployable_parameters(parameters_after), graph
    )
    graph_contract = smoke.onnx_contract(graph, parameters_after, observations)
    snapshot_path = args.work_root / "winner_v24_baseline_anchored_update_101.npz"
    snapshot_receipt = v22v2.save_snapshot(
        snapshot_path,
        parameters_after,
        optimizer_after,
        {
            "stage": "baseline_anchored_symmetric_failure_joint_stage2",
            "completed_updates": 101,
            "source_completed_updates": 100,
            "source_snapshot_sha256": final_receipt["sha256"],
            "objective": contract["objective"],
            "root_seed": 120120,
            "learning_rate": float(training.STAGE2_LEARNING_RATE),
            "predictor_scale": float(v22v2.FROZEN_PREDICTOR_SCALE),
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        restored["target_mean"],
        restored["target_std"],
    )
    loaded = v22v2.load_snapshot(snapshot_path)
    snapshot_exact = bool(
        common.tree_equal(parameters_after, loaded["parameters"])
        and np.array_equal(
            np.asarray(optimizer_after["count"]),
            np.asarray(loaded["optimizer"]["count"]),
        )
        and common.tree_equal(optimizer_after["m"], loaded["optimizer"]["m"])
        and common.tree_equal(optimizer_after["v"], loaded["optimizer"]["v"])
        and np.array_equal(restored["target_mean"], loaded["target_mean"])
        and np.array_equal(restored["target_std"], loaded["target_std"])
    )
    checks = {
        "source_zero_update_result_exact": True,
        "source_snapshot_and_optimizer_count_100_exact": True,
        "exact_80_episode_population": len(episodes) == 80,
        "episode_receipts_exact": bool(episode_hash),
        "action_boundary_exact": boundary["realized_equals_numpy_bit_exact"]
        and boundary["numpy_equals_jax_bit_exact"],
        "pitch_margin_reward_exact": reward["reward_formula_bit_exact"],
        "default_off_batch_bit_exact": default_exact,
        "failure_and_success_population_present": int(np.sum(failure_mask)) > 0
        and settled_count > 0,
        "objective_locality_exact": objective_locality_exact,
        "analytic_delta_nonzero": objective_evidence[
            "analytical_terminal_delta_nonzero_count"
        ]
        > int(np.sum(failure_mask)),
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
        "exactly_one_optimizer_update_100_to_101": int(
            np.asarray(optimizer_after["count"])
        )
        == 101,
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
        "schema_version": "winner_v24.baseline_anchored_one_update_cpu_result.v1",
        "status": (
            "PASS_WINNER_V24_BASELINE_ANCHORED_ONE_UPDATE_CPU_PROOF"
            if not failed
            else "HOLD_WINNER_V24_BASELINE_ANCHORED_ONE_UPDATE_CPU_PROOF"
        ),
        "decision": (
            "AUTHORIZE_SEPARATE_BASELINE_ANCHORED_TRAINING_PREREGISTRATION_ONLY"
            if not failed
            else "DO_NOT_TRAIN_WINNER_V24_BASELINE_ANCHORED_OBJECTIVE"
        ),
        "checks": {name: bool(value) for name, value in checks.items()},
        "failed_checks": failed,
        "source_snapshot": {
            "sha256": final_receipt["sha256"],
            "bytes": final_receipt["bytes"],
            "completed_updates": 100,
            "optimizer_count": 100,
        },
        "objective": contract["objective"],
        "rollout": {
            "update_index": ROLLOUT_UPDATE_INDEX,
            "episode_slots": len(episodes),
            "episode_receipts_sha256": episode_hash,
            "roll_pitch_failure_count": int(np.sum(failure_mask)),
            "settled_success_count": settled_count,
            "sampled_count": int(np.sum(batch_np["valid_mask"])),
            "valid_transition_count": int(
                np.sum(batch_np["valid_transition_mask"])
            ),
            "stored_successor_transition_count": expected_stored,
            "changed_batch_keys": changed_keys,
            "objective_evidence": objective_evidence,
            "action_boundary": boundary,
            "pitch_margin_reward": reward,
            "default_off_batch_bit_exact": default_exact,
            "objective_locality_exact": objective_locality_exact,
            "sampled_hidden_replay_max_abs_error": float(
                ppo_metrics["sampled_hidden_replay_max_abs_error"]
            ),
            "stored_successor_mask_exact": int(
                predictor_metrics["stored_successor_transition_count"]
            )
            == expected_stored,
        },
        "optimization": {
            "optimizer_count_before": 100,
            "optimizer_count_after": int(np.asarray(optimizer_after["count"])),
            "ppo_loss": float(ppo_loss),
            "normalized_predictor_loss": float(predictor_loss),
            "combined_loss": float(combined_loss),
            "predictor_scale": float(v22v2.FROZEN_PREDICTOR_SCALE),
            "combined_gradient_max_abs": gradient_max,
            "leaf_max_abs_delta": leaf_delta,
            "trainable_leaves": list(v21.JOINT_TRAINABLE_KEYS),
            "source_state_unchanged_before_update": source_unchanged_before_update,
            "all_finite": True,
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
        },
        "sources": {
            "contract_lf_sha256": common.lf_sha256(CONTRACT),
            "zero_update_result_lf_sha256": common.lf_sha256(ZERO_UPDATE_RESULT),
            "v22_training_lf_sha256": common.lf_sha256(V22_TRAINING),
            "mechanics_lf_sha256": common.lf_sha256(
                ROOT / "patches/winner_v24_symmetric_support_failure_v2.py"
            ),
            "runner_lf_sha256": common.lf_sha256(Path(__file__)),
        },
        "authority": {
            "robot_clearance": False,
            "training_executed": False,
            "formal_support_gate_executed": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "manual_mass_com_inertia_measurements_required": False,
            "pass_authorizes_only": (
                "a separate frozen baseline-anchored training preregistration"
            ),
        },
    }
    if not all(math.isfinite(float(value)) for value in (
        ppo_loss,
        predictor_loss,
        combined_loss,
        *gradient_max.values(),
        *leaf_delta.values(),
    )):
        raise FloatingPointError("Winner-v24 one-update result is nonfinite")
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
