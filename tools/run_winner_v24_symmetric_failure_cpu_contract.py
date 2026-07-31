#!/usr/bin/env python3
"""Run the zero-update Winner-v24 symmetric support-failure CPU contract."""

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

CONTRACT = ANALYSIS / "winner_v24_symmetric_failure_cpu_contract.json"
V23_RESULT = ANALYSIS / "winner_v23_negative_x_response_use_diagnostic_result.json"
V22_TRAINING = ANALYSIS / "winner_v22_normalized_predictor_training_result.json"
FULL_PREREG = ANALYSIS / "winner_v12_full_calibrator_training_preregistration.json"
DOMAIN = ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
MECHANICS = ROOT / "patches/winner_v24_symmetric_support_failure.py"
ROLLOUT_UPDATE_INDEX = 100
COMBINED_DELTA_TOLERANCE = 2.0e-6


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


def validate_contract(value: Mapping[str, Any]) -> None:
    if (
        value.get("schema_version") != "winner_v24.symmetric_failure_cpu_contract.v1"
        or value.get("status") != "FROZEN_WINNER_V24_SYMMETRIC_FAILURE_CPU_CONTRACT"
        or value.get("decision")
        != "AUTHORIZE_ONE_ZERO_UPDATE_SYMMETRIC_FAILURE_OBJECTIVE_PROOF_ONLY"
        or value.get("execution_now")
        != {
            "rollout_episode_slots": 0,
            "optimizer_updates": 0,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        }
    ):
        raise ValueError("Winner-v24 CPU contract changed")
    objective = value.get("objective", {})
    if (
        objective.get("source_rollout_update_index") != ROLLOUT_UPDATE_INDEX
        or objective.get("settled_success_bonus") != 250.0
        or objective.get("roll_pitch_failure_penalty") != -250.0
        or objective.get("failure_selector") != "terminal.checks.roll_pitch is false"
        or objective.get("reads_hidden_configuration") is not False
        or objective.get("changes_rollout_or_policy_action") is not False
        or objective.get("modified_batch_keys") != ["advantages", "returns", "rewards"]
        or objective.get("combined_delta_tolerance") != COMBINED_DELTA_TOLERANCE
    ):
        raise ValueError("Winner-v24 objective changed")
    sources = value.get("sources")
    if not isinstance(sources, dict) or not sources:
        raise ValueError("Winner-v24 source manifest is absent")
    for name, item in sources.items():
        path = ROOT / item["path"]
        if (
            set(item) != {"hash_mode", "path", "sha256"}
            or item["hash_mode"] != "lf"
            or lf_sha256(path) != item["sha256"]
        ):
            raise ValueError(f"Winner-v24 source changed: {name}")
    if canonical_sha256(sources) != value.get("source_manifest_sha256"):
        raise ValueError("Winner-v24 source manifest changed")


def tree_max_abs(tree: Mapping[str, Any]) -> dict[str, float]:
    return {
        key: float(np.max(np.abs(np.asarray(value, dtype=np.float64))))
        for key, value in tree.items()
    }


def tree_delta_max_abs(
    left: Mapping[str, Any], right: Mapping[str, Any]
) -> dict[str, float]:
    if set(left) != set(right):
        raise ValueError("Winner-v24 gradient trees differ")
    return {
        key: float(
            np.max(
                np.abs(
                    np.asarray(right[key], dtype=np.float64)
                    - np.asarray(left[key], dtype=np.float64)
                )
            )
        )
        for key in left
    }


def tree_equal(left: Mapping[str, Any], right: Mapping[str, Any]) -> bool:
    return set(left) == set(right) and all(
        np.array_equal(np.asarray(left[key]), np.asarray(right[key])) for key in left
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--canonical-fit", type=Path, required=True)
    parser.add_argument("--final-snapshot", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--offline-cpu-only", action="store_true")
    parser.add_argument("--zero-update-objective-proof-authorized", action="store_true")
    args = parser.parse_args()
    if not args.offline_cpu_only or not args.zero_update_objective_proof_authorized:
        raise PermissionError(
            "Winner-v24 requires --offline-cpu-only "
            "--zero-update-objective-proof-authorized"
        )
    if args.output.exists():
        raise FileExistsError("refusing to overwrite Winner-v24 CPU evidence")

    import jax
    import jax.numpy as jnp
    import mujoco
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

    if jax.default_backend() != "cpu" or any(
        device.platform != "cpu" for device in jax.devices()
    ):
        raise ValueError("Winner-v24 requires CPU-only JAX")
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    validate_contract(contract)
    v23 = json.loads(V23_RESULT.read_text(encoding="utf-8"))
    v22_training = json.loads(V22_TRAINING.read_text(encoding="utf-8"))
    if (
        v23.get("status") != "PASS_WINNER_V23_NEGATIVE_X_RESPONSE_USE_DIAGNOSTIC"
        or v23.get("classification")
        != "RESPONSE_STATE_PRESENT_AND_USED_SUPPORT_CONTROL_INADEQUATE"
        or v23.get("decision")
        != "AUTHORIZE_NEGATIVE_X_SUPPORT_CONTROL_OBJECTIVE_CPU_CONTRACT_ONLY"
        or v23.get("failed_checks") != []
        or v22_training.get("status")
        != "PASS_WINNER_V22_NORMALIZED_PREDICTOR_TRAINING_ARTIFACT"
        or v22_training.get("failed_checks") != []
    ):
        raise ValueError("Winner-v24 source evidence changed")
    final_receipt = v22_training["snapshot_manifest"][99]
    if (
        final_receipt.get("completed_updates") != 100
        or sha256(args.final_snapshot) != final_receipt.get("sha256")
        or args.final_snapshot.stat().st_size != final_receipt.get("bytes")
    ):
        raise ValueError("Winner-v24 final snapshot bytes changed")

    expected_versions = dict(
        json.loads(FULL_PREREG.read_text(encoding="utf-8"))[
            "implementation_contract_environment"
        ]
    )
    if expected_versions.pop("platform") != "CPU only" or not smoke.validate_software_versions(
        {"software_versions": expected_versions}
    )["exact"]:
        raise ValueError("Winner-v24 software environment changed")
    if smoke.sha256(args.canonical_fit) != smoke.P30_FIT_LF_SHA256:
        raise ValueError("Winner-v24 canonical P30 fit changed")
    if smoke.git_output(args.playground_root, "rev-parse", "HEAD") != smoke.CONTROL_COMMIT:
        raise ValueError("Winner-v24 Playground source changed")
    smoke.validate_playground_tree(args.playground_root)
    scene = args.playground_root / smoke.SCENE_RELATIVE
    if smoke.sha256(scene) != smoke.SCENE_SHA256:
        raise ValueError("Winner-v24 scene changed")

    v22_gate.smoke = smoke
    v22_gate.training = training
    v22_gate.v21 = v21
    snapshot = v22v2.load_snapshot(args.final_snapshot)
    v22_gate._validate_snapshot(
        snapshot, expected_stage="normalized_predictor_joint_stage2"
    )
    if snapshot["metadata"]["completed_updates"] != 100:
        raise ValueError("Winner-v24 final checkpoint boundary changed")
    parameters = snapshot["parameters"]
    source_parameters = {
        key: np.asarray(value).copy() for key, value in parameters.items()
    }
    full_prereg = json.loads(FULL_PREREG.read_text(encoding="utf-8"))
    domain = json.loads(DOMAIN.read_text(encoding="utf-8"))
    design = json.loads(smoke.CALIBRATOR_PREREG.read_text(encoding="utf-8"))
    population = full.training_population(full_prereg, domain)
    if len(population) != 80:
        raise ValueError("Winner-v24 population changed")
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
    baseline_reward = v15.reward_evidence(batch_np)
    _, values = training.stage2_mean_value(
        parameters, jnp.asarray(batch_np["hidden"], dtype=jnp.float32)
    )
    values_np = np.asarray(values, dtype=np.float32)
    replay_returns, replay_advantages = v24.recompute_gae(
        rewards=batch_np["rewards"],
        values=values_np,
        done=batch_np["done"],
        sample_mask=batch_np["valid_mask"],
        gamma=training.PPO_GAMMA,
        gae_lambda=training.PPO_GAE_LAMBDA,
    )
    baseline_return_error = float(
        np.max(np.abs(replay_returns - np.asarray(batch_np["returns"])))
    )
    baseline_advantage_error = float(
        np.max(np.abs(replay_advantages - np.asarray(batch_np["advantages"])))
    )
    disabled_batch, disabled_evidence = v24.apply_symmetric_failure_objective(
        batch_np,
        episodes,
        values_np,
        enabled=False,
        gamma=training.PPO_GAMMA,
        gae_lambda=training.PPO_GAE_LAMBDA,
    )
    symmetric_batch, symmetric_evidence = v24.apply_symmetric_failure_objective(
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
        if not np.array_equal(np.asarray(batch_np[key]), symmetric_batch[key])
    )
    failure_mask = v24.roll_pitch_failure_mask(
        episodes, shape=np.asarray(batch_np["rewards"]).shape
    )
    settled_count = sum(
        receipt.get("terminal_success_bonus_applied") is True for receipt in episodes
    )
    unchanged_reward_mask = ~failure_mask
    other_rewards_exact = bool(
        np.array_equal(
            np.asarray(batch_np["rewards"])[unchanged_reward_mask],
            symmetric_batch["rewards"][unchanged_reward_mask],
        )
    )

    baseline_batch = {key: jnp.asarray(value) for key, value in batch_np.items()}
    objective_batch = {key: jnp.asarray(value) for key, value in symmetric_batch.items()}
    trainable = v21.joint_trainable_parameters(parameters)
    target_mean = jnp.asarray(snapshot["target_mean"], dtype=jnp.float32)
    target_std = jnp.asarray(snapshot["target_std"], dtype=jnp.float32)

    def ppo_objective(values_tree: Mapping[str, Any], data: Mapping[str, Any]):
        return v20.joint_recurrent_ppo_loss(
            values_tree,
            data,
            clip_epsilon=training.PPO_CLIP_EPSILON,
            value_coefficient=training.PPO_VALUE_COEFFICIENT,
            entropy_coefficient=training.PPO_ENTROPY_COEFFICIENT,
        )

    def predictor_objective(values_tree: Mapping[str, Any], data: Mapping[str, Any]):
        return v22.normalized_predictor_loss(
            values_tree, data, target_mean, target_std
        )

    (baseline_ppo_loss, baseline_ppo_metrics), baseline_ppo_gradients = (
        jax.value_and_grad(ppo_objective, has_aux=True)(trainable, baseline_batch)
    )
    (symmetric_ppo_loss, symmetric_ppo_metrics), symmetric_ppo_gradients = (
        jax.value_and_grad(ppo_objective, has_aux=True)(trainable, objective_batch)
    )
    (baseline_predictor_loss, _), baseline_predictor_gradients = jax.value_and_grad(
        predictor_objective, has_aux=True
    )(trainable, baseline_batch)
    (symmetric_predictor_loss, _), symmetric_predictor_gradients = jax.value_and_grad(
        predictor_objective, has_aux=True
    )(trainable, objective_batch)
    baseline_combined = v22v2.compose_gradients(
        baseline_ppo_gradients, baseline_predictor_gradients
    )
    symmetric_combined = v22v2.compose_gradients(
        symmetric_ppo_gradients, symmetric_predictor_gradients
    )
    ppo_delta = tree_delta_max_abs(baseline_ppo_gradients, symmetric_ppo_gradients)
    combined_delta = tree_delta_max_abs(baseline_combined, symmetric_combined)
    composition_error = max(
        float(
            np.max(
                np.abs(
                    (
                        np.asarray(symmetric_combined[key], dtype=np.float64)
                        - np.asarray(baseline_combined[key], dtype=np.float64)
                    )
                    - (
                        np.asarray(symmetric_ppo_gradients[key], dtype=np.float64)
                        - np.asarray(baseline_ppo_gradients[key], dtype=np.float64)
                    )
                )
            )
        )
        for key in v21.JOINT_TRAINABLE_KEYS
    )
    predictor_gradients_exact = tree_equal(
        baseline_predictor_gradients, symmetric_predictor_gradients
    )
    all_numeric = [
        float(baseline_ppo_loss),
        float(symmetric_ppo_loss),
        float(baseline_predictor_loss),
        float(symmetric_predictor_loss),
        baseline_return_error,
        baseline_advantage_error,
        composition_error,
        *ppo_delta.values(),
        *combined_delta.values(),
        *tree_max_abs(baseline_ppo_gradients).values(),
        *tree_max_abs(symmetric_ppo_gradients).values(),
    ]
    default_off_exact = all(
        np.array_equal(disabled_batch[key], np.asarray(batch_np[key]))
        for key in batch_np
    ) and disabled_evidence["modified_batch_keys"] == []
    terminal_penalty_exact = bool(
        np.all(
            symmetric_batch["rewards"][failure_mask]
            == v24.SYMMETRIC_FAILURE_PENALTY
        )
    )
    parameters_unchanged = all(
        np.array_equal(source_parameters[key], np.asarray(parameters[key]))
        for key in source_parameters
    )
    checks = {
        "source_final_snapshot_exact": True,
        "exact_80_episode_population": len(episodes) == 80,
        "episode_receipts_exact": bool(episode_hash),
        "action_boundary_exact": boundary["realized_equals_numpy_bit_exact"]
        and boundary["numpy_equals_jax_bit_exact"],
        "baseline_pitch_margin_reward_exact": baseline_reward[
            "reward_formula_bit_exact"
        ],
        "baseline_gae_replay_at_most_1e_6": max(
            baseline_return_error, baseline_advantage_error
        )
        <= 1.0e-6,
        "default_off_batch_bit_exact": default_off_exact,
        "roll_pitch_failures_and_settled_successes_both_present": int(
            np.sum(failure_mask)
        )
        > 0
        and settled_count > 0,
        "enabled_changes_only_rewards_returns_advantages": changed_keys
        == list(v24.MODIFIED_BATCH_KEYS),
        "terminal_failure_penalty_exact": terminal_penalty_exact,
        "all_other_rewards_bit_exact": other_rewards_exact,
        "predictor_loss_and_gradients_bit_exact": float(baseline_predictor_loss)
        == float(symmetric_predictor_loss)
        and predictor_gradients_exact,
        "ppo_action_head_gradient_changes": max(
            ppo_delta["action_weight"], ppo_delta["action_bias"]
        )
        > 0.0,
        "ppo_recurrent_gradient_changes": max(
            ppo_delta[key] for key in v21.RECURRENT_KEYS
        )
        > 0.0,
        "combined_delta_matches_ppo_delta_at_most_2e_6": composition_error
        <= COMBINED_DELTA_TOLERANCE,
        "all_losses_metrics_and_gradients_finite": all(
            math.isfinite(value) for value in all_numeric
        )
        and training.finite_tree(baseline_ppo_metrics)
        and training.finite_tree(symmetric_ppo_metrics),
        "parameters_unchanged_no_optimizer_step": parameters_unchanged,
        "optimizer_updates_zero": True,
        "formal_support_cells_zero": True,
        "locomotion_steps_zero": True,
        "robot_or_rdk_access_zero": True,
    }
    failed_checks = sorted(name for name, passed in checks.items() if not passed)
    result = {
        "schema_version": "winner_v24.symmetric_failure_cpu_result.v1",
        "status": (
            "PASS_WINNER_V24_SYMMETRIC_FAILURE_CPU_CONTRACT"
            if not failed_checks
            else "HOLD_WINNER_V24_SYMMETRIC_FAILURE_CPU_CONTRACT"
        ),
        "decision": (
            "AUTHORIZE_SEPARATE_ONE_UPDATE_SYMMETRIC_FAILURE_CPU_PROOF_PREREGISTRATION_ONLY"
            if not failed_checks
            else "DO_NOT_RUN_WINNER_V24_OPTIMIZER_UPDATE"
        ),
        "checks": checks,
        "failed_checks": failed_checks,
        "source_checkpoint": {
            "label": "final",
            "completed_updates": 100,
            "sha256": sha256(args.final_snapshot),
            "bytes": args.final_snapshot.stat().st_size,
        },
        "objective": {
            "settled_success_bonus": 250.0,
            "roll_pitch_failure_penalty": float(v24.SYMMETRIC_FAILURE_PENALTY),
            "failure_selector": "terminal.checks.roll_pitch is false",
            "source_rollout_update_index": ROLLOUT_UPDATE_INDEX,
            "reads_hidden_configuration": False,
            "changes_rollout_or_policy_action": False,
            "modified_batch_keys": list(v24.MODIFIED_BATCH_KEYS),
            "combined_delta_tolerance": COMBINED_DELTA_TOLERANCE,
        },
        "population": {
            "episode_slots": len(episodes),
            "roll_pitch_failure_count": int(np.sum(failure_mask)),
            "settled_success_count": settled_count,
            "episode_receipts_sha256": episode_hash,
        },
        "batch_evidence": {
            "action_boundary": boundary,
            "baseline_reward": baseline_reward,
            "default_off_batch_bit_exact": default_off_exact,
            "terminal_failure_penalty_exact": terminal_penalty_exact,
            "all_other_rewards_bit_exact": other_rewards_exact,
            "parameters_unchanged": parameters_unchanged,
            "disabled": disabled_evidence,
            "enabled": symmetric_evidence,
            "changed_keys": changed_keys,
            "baseline_return_replay_max_abs_error": baseline_return_error,
            "baseline_advantage_replay_max_abs_error": baseline_advantage_error,
            "baseline_rewards_sha256": v24.array_sha256(batch_np["rewards"]),
            "symmetric_rewards_sha256": v24.array_sha256(
                symmetric_batch["rewards"]
            ),
            "baseline_returns_sha256": v24.array_sha256(batch_np["returns"]),
            "symmetric_returns_sha256": v24.array_sha256(
                symmetric_batch["returns"]
            ),
            "baseline_advantages_sha256": v24.array_sha256(
                batch_np["advantages"]
            ),
            "symmetric_advantages_sha256": v24.array_sha256(
                symmetric_batch["advantages"]
            ),
        },
        "gradient_evidence": {
            "baseline_ppo_loss": float(baseline_ppo_loss),
            "symmetric_ppo_loss": float(symmetric_ppo_loss),
            "baseline_normalized_predictor_loss": float(baseline_predictor_loss),
            "symmetric_normalized_predictor_loss": float(symmetric_predictor_loss),
            "baseline_ppo_gradient_max_abs": tree_max_abs(
                baseline_ppo_gradients
            ),
            "symmetric_ppo_gradient_max_abs": tree_max_abs(
                symmetric_ppo_gradients
            ),
            "ppo_gradient_delta_max_abs": ppo_delta,
            "combined_gradient_delta_max_abs": combined_delta,
            "combined_delta_minus_ppo_delta_max_abs_error": composition_error,
            "predictor_gradients_bit_exact": predictor_gradients_exact,
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
            "jax_devices": [str(device) for device in jax.devices()],
        },
        "sources": {
            "contract_lf_sha256": lf_sha256(CONTRACT),
            "v23_result_lf_sha256": lf_sha256(V23_RESULT),
            "v22_training_lf_sha256": lf_sha256(V22_TRAINING),
            "mechanics_lf_sha256": lf_sha256(MECHANICS),
            "runner_lf_sha256": lf_sha256(Path(__file__)),
        },
        "authority": {
            "robot_clearance": False,
            "training_authorized": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "manual_mass_com_inertia_measurements_required": False,
            "pass_authorizes_only": (
                "a separate one-update symmetric-failure CPU-proof preregistration"
            ),
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(result["status"])
    for name in failed_checks:
        print(f"FAILED={name}")
    return 0 if not failed_checks else 1


if __name__ == "__main__":
    raise SystemExit(main())
