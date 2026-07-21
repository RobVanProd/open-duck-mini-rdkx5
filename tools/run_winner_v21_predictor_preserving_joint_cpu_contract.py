#!/usr/bin/env python3
"""Run the zero-update Winner-v21 predictor-preserving gradient contract."""

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

CONTRACT = ANALYSIS / "winner_v21_predictor_preserving_joint_cpu_contract.json"
ATTRIBUTION = ANALYSIS / "winner_v20_joint_recurrent_support_failure_attribution.json"
STAGE1_RESULT = ANALYSIS / "winner_v13_normalized_response_stage1_v2_result.json"
FULL_PREREG = ANALYSIS / "winner_v12_full_calibrator_training_preregistration.json"
DOMAIN = ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
SNAPSHOT_SHA256 = "8c1392c738eddfb098e61c1a6ae2f863eda883e1eba6ac546aef695da6f163af"
SNAPSHOT_BYTES = 189027


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


def tree_equal(left: Mapping[str, Any], right: Mapping[str, Any]) -> bool:
    return set(left) == set(right) and all(
        np.array_equal(np.asarray(left[key]), np.asarray(right[key])) for key in left
    )


def arrays_equal(
    left: Mapping[str, np.ndarray], right: Mapping[str, np.ndarray], names: set[str]
) -> bool:
    return all(
        np.array_equal(np.asarray(left[name]), np.asarray(right[name])) for name in names
    )


def max_abs(tree: Mapping[str, Any]) -> dict[str, float]:
    return {
        key: float(np.max(np.abs(np.asarray(value)))) for key, value in tree.items()
    }


def validate_source_manifest(contract: Mapping[str, Any]) -> None:
    sources = contract.get("sources")
    if not isinstance(sources, dict) or not sources:
        raise ValueError("Winner-v21 CPU source manifest is absent")
    for name, item in sources.items():
        path = ROOT / item["path"]
        if (
            set(item) != {"hash_mode", "path", "sha256"}
            or item["hash_mode"] != "lf"
            or lf_sha256(path) != item["sha256"]
        ):
            raise ValueError(f"Winner-v21 CPU source changed: {name}")
    if canonical_sha256(sources) != contract.get("source_manifest_sha256"):
        raise ValueError("Winner-v21 CPU source-manifest digest changed")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--canonical-fit", type=Path, required=True)
    parser.add_argument("--stage1-final-snapshot", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--offline-cpu-only", action="store_true")
    parser.add_argument(
        "--zero-update-predictor-preserving-contract-authorized", action="store_true"
    )
    args = parser.parse_args()
    if (
        not args.offline_cpu_only
        or not args.zero_update_predictor_preserving_contract_authorized
    ):
        raise PermissionError(
            "Winner-v21 CPU contract requires --offline-cpu-only "
            "--zero-update-predictor-preserving-contract-authorized"
        )
    if args.output.exists():
        raise FileExistsError("refusing to overwrite Winner-v21 CPU evidence")

    import jax
    import jax.numpy as jnp
    import mujoco
    import run_winner_v12_calibrator_cpu_smoke as smoke
    import run_winner_v12_full_calibrator_training as full
    import winner_v12_calibrator_training as training
    import winner_v15_pitch_margin_support as v15
    import winner_v20_joint_recurrent_support as v20
    import winner_v21_predictor_preserving_joint_support as v21

    if jax.default_backend() != "cpu" or any(
        device.platform != "cpu" for device in jax.devices()
    ):
        raise ValueError("Winner-v21 contract requires CPU-only JAX")
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    if (
        contract.get("schema_version")
        != "winner_v21.predictor_preserving_joint_cpu_contract.v1"
        or contract.get("status")
        != "FROZEN_WINNER_V21_PREDICTOR_PRESERVING_JOINT_CPU_CONTRACT"
        or contract.get("decision")
        != "AUTHORIZE_EXACT_ZERO_UPDATE_GRADIENT_BALANCE_PROOF_ONLY"
        or contract.get("execution_now")
        != {
            "optimizer_updates": 0,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        }
    ):
        raise ValueError("Winner-v21 CPU contract changed")
    validate_source_manifest(contract)
    attribution = json.loads(ATTRIBUTION.read_text(encoding="utf-8"))
    if (
        attribution.get("status") != "PASS_WINNER_V20_SUPPORT_FAILURE_ATTRIBUTION"
        or attribution.get("decision")
        != "AUTHORIZE_PREDICTOR_PRESERVING_JOINT_OBJECTIVE_CPU_CONTRACT_ONLY"
        or attribution.get("authority", {}).get("optimizer_updates_authorized_now")
        != 0
    ):
        raise ValueError("Winner-v21 source attribution changed")
    stage1_result = json.loads(STAGE1_RESULT.read_text(encoding="utf-8"))
    if (
        stage1_result.get("status") != "PASS_WINNER_V13_NORMALIZED_RESPONSE_STAGE1"
        or stage1_result.get("failed_checks") != []
        or sha256(args.stage1_final_snapshot) != SNAPSHOT_SHA256
        or args.stage1_final_snapshot.stat().st_size != SNAPSHOT_BYTES
    ):
        raise ValueError("Winner-v21 Stage-1 source changed")
    restored = full.load_snapshot(args.stage1_final_snapshot)
    if (
        restored["metadata"].get("schema_version")
        != "winner_v13.normalized_response_stage1_snapshot.v1"
        or restored["metadata"].get("completed_updates") != 100
        or restored["metadata"].get("robot_or_rdk_access") != 0
    ):
        raise ValueError("Winner-v21 source snapshot metadata changed")

    expected_versions = dict(
        json.loads(FULL_PREREG.read_text(encoding="utf-8"))[
            "implementation_contract_environment"
        ]
    )
    if expected_versions.pop("platform") != "CPU only" or not smoke.validate_software_versions(
        {"software_versions": expected_versions}
    )["exact"]:
        raise ValueError("Winner-v21 software environment changed")
    if smoke.sha256(args.canonical_fit) != smoke.P30_FIT_LF_SHA256:
        raise ValueError("Winner-v21 canonical P30 fit changed")
    if smoke.git_output(args.playground_root, "rev-parse", "HEAD") != smoke.CONTROL_COMMIT:
        raise ValueError("Winner-v21 Playground source changed")
    smoke.validate_playground_tree(args.playground_root)
    scene = args.playground_root / smoke.SCENE_RELATIVE
    if smoke.sha256(scene) != smoke.SCENE_SHA256:
        raise ValueError("Winner-v21 scene changed")

    full_prereg = json.loads(FULL_PREREG.read_text(encoding="utf-8"))
    domain = json.loads(DOMAIN.read_text(encoding="utf-8"))
    design = json.loads(smoke.CALIBRATOR_PREREG.read_text(encoding="utf-8"))
    population = full.training_population(full_prereg, domain)
    if len(population) != 80:
        raise ValueError("Winner-v21 population changed")
    observer_type = smoke.load_runtime_observer(args.canonical_fit)
    parameters = restored["parameters"]
    source_parameters = {
        key: np.asarray(value).copy() for key, value in parameters.items()
    }
    v15_batch, v15_episodes, v15_chain = v15.stage2_rollout(
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
        update_index=0,
        enabled=True,
    )
    batch_np, episodes, chain_observations = v20.stage2_rollout(
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
        update_index=0,
    )
    full.validate_stage2_masks(batch_np, episodes)
    episode_hash = full.validate_episode_receipts(
        episodes, population, stage=2, update_index=0
    )
    transition_keys = set(v15_batch)
    rollout_exact = (
        arrays_equal(v15_batch, batch_np, transition_keys)
        and episodes == v15_episodes
        and np.array_equal(chain_observations, v15_chain)
    )
    reward = v15.reward_evidence(batch_np)
    boundary = full.stage2_action_boundary_evidence(batch_np)
    batch = {key: jnp.asarray(value) for key, value in batch_np.items()}
    trainable = v21.joint_trainable_parameters(parameters)
    target_std = jnp.asarray(restored["target_std"], dtype=jnp.float32)

    def ppo_objective(values: Mapping[str, Any], data: Mapping[str, Any]):
        return v20.joint_recurrent_ppo_loss(
            values,
            data,
            clip_epsilon=training.PPO_CLIP_EPSILON,
            value_coefficient=training.PPO_VALUE_COEFFICIENT,
            entropy_coefficient=training.PPO_ENTROPY_COEFFICIENT,
        )

    def predictor_objective(values: Mapping[str, Any], data: Mapping[str, Any]):
        return v21.predictor_loss(values, data, target_std)

    (ppo_loss, ppo_metrics), ppo_gradients = jax.value_and_grad(
        ppo_objective, has_aux=True
    )(trainable, batch)
    (prediction_loss, prediction_metrics), prediction_gradients = jax.value_and_grad(
        predictor_objective, has_aux=True
    )(trainable, batch)
    predictor_scale, scale_receipt = v21.gradient_balance_scale(
        ppo_gradients, prediction_gradients
    )

    def joint_objective(values: Mapping[str, Any], data: Mapping[str, Any]):
        return v21.combined_loss(
            values,
            data,
            target_std,
            jnp.asarray(predictor_scale),
            clip_epsilon=training.PPO_CLIP_EPSILON,
            value_coefficient=training.PPO_VALUE_COEFFICIENT,
            entropy_coefficient=training.PPO_ENTROPY_COEFFICIENT,
        )

    (combined_loss, combined_metrics), combined_gradients = jax.value_and_grad(
        joint_objective, has_aux=True
    )(trainable, batch)
    expected_gradients = {
        key: ppo_gradients[key]
        + jnp.asarray(predictor_scale) * prediction_gradients[key]
        for key in v21.JOINT_TRAINABLE_KEYS
    }
    combination_error = max(
        float(
            np.max(
                np.abs(
                    np.asarray(combined_gradients[key])
                    - np.asarray(expected_gradients[key])
                )
            )
        )
        for key in v21.JOINT_TRAINABLE_KEYS
    )
    ppo_max = max_abs(ppo_gradients)
    prediction_max = max_abs(prediction_gradients)
    combined_max = max_abs(combined_gradients)
    stored_count = int(np.sum(batch_np["valid_transition_mask"][:, :-1] * batch_np["valid_mask"][:, 1:]))
    checks = {
        "source_stage1_snapshot_exact": True,
        "exact_80_episode_population": len(episodes) == 80,
        "winner_v15_rollout_bit_exact": rollout_exact,
        "episode_receipts_exact": bool(episode_hash),
        "action_boundary_exact": boundary["realized_equals_numpy_bit_exact"]
        and boundary["numpy_equals_jax_bit_exact"],
        "reward_formula_exact_and_nonzero": reward["reward_formula_bit_exact"]
        and reward["nonzero_penalty_count"] > 0,
        "sampled_hidden_replay_at_most_1e_6": float(
            ppo_metrics["sampled_hidden_replay_max_abs_error"]
        )
        <= 1.0e-6,
        "stored_successor_mask_exact": int(
            prediction_metrics["stored_successor_transition_count"]
        )
        == stored_count
        and stored_count > 0,
        "ppo_gradient_partition_exact": all(
            ppo_max[name] == 0.0 for name in (*v21.RECURRENT_KEYS, *v21.PREDICTOR_KEYS)
        )
        and all(ppo_max[name] > 0.0 for name in v21.PPO_ONLY_KEYS),
        "predictor_gradient_partition_exact": all(
            prediction_max[name] > 0.0
            for name in (*v21.RECURRENT_KEYS, *v21.PREDICTOR_KEYS)
        )
        and all(prediction_max[name] == 0.0 for name in v21.PPO_ONLY_KEYS),
        "gradient_balance_scale_finite_positive": math.isfinite(
            float(predictor_scale)
        )
        and float(predictor_scale) > 0.0,
        "combined_all_12_gradients_nonzero": all(
            combined_max[name] > 0.0 for name in v21.JOINT_TRAINABLE_KEYS
        ),
        "combined_gradient_is_exact_sum_at_most_1e_6": combination_error <= 1.0e-6,
        "all_losses_gradients_and_metrics_finite": training.finite_tree(
            {
                "ppo_loss": ppo_loss,
                "ppo_metrics": ppo_metrics,
                "prediction_loss": prediction_loss,
                "prediction_metrics": prediction_metrics,
                "combined_loss": combined_loss,
                "combined_metrics": combined_metrics,
                "ppo_gradients": ppo_gradients,
                "prediction_gradients": prediction_gradients,
                "combined_gradients": combined_gradients,
            }
        ),
        "parameters_bit_exact_unchanged": tree_equal(source_parameters, parameters),
        "optimizer_updates_zero": True,
        "formal_support_locomotion_robot_zero": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    result = {
        "schema_version": "winner_v21.predictor_preserving_joint_cpu_result.v1",
        "status": (
            "PASS_WINNER_V21_PREDICTOR_PRESERVING_JOINT_CPU_CONTRACT"
            if not failed
            else "HOLD_WINNER_V21_PREDICTOR_PRESERVING_JOINT_CPU_CONTRACT"
        ),
        "decision": (
            "AUTHORIZE_SEPARATE_TWO_UPDATE_PREDICTOR_PRESERVING_PROOF_PREREGISTRATION_ONLY"
            if not failed
            else "DO_NOT_UPDATE_OR_TRAIN_WINNER_V21"
        ),
        "checks": {name: bool(value) for name, value in checks.items()},
        "failed_checks": failed,
        "environment": {
            "software_versions": expected_versions,
            "jax_devices": [str(device) for device in jax.devices()],
        },
        "source_snapshot": {"sha256": SNAPSHOT_SHA256, "bytes": SNAPSHOT_BYTES},
        "rollout": {
            "episode_receipts_sha256": episode_hash,
            "sampled_count": int(np.sum(batch_np["valid_mask"])),
            "valid_transition_count": int(
                np.sum(batch_np["valid_transition_mask"])
            ),
            "stored_successor_transition_count": stored_count,
            "winner_v15_transition_exact": rollout_exact,
            "reward": reward,
            "action_boundary_exact": bool(checks["action_boundary_exact"]),
            "sampled_hidden_replay_max_abs_error": float(
                ppo_metrics["sampled_hidden_replay_max_abs_error"]
            ),
        },
        "objective": {
            "ppo_loss": float(ppo_loss),
            "predictor_loss": float(prediction_loss),
            "combined_loss": float(combined_loss),
            "balance": scale_receipt,
            "combined_gradient_max_abs_error_from_sum": combination_error,
            "ppo_gradient_max_abs": ppo_max,
            "predictor_gradient_max_abs": prediction_max,
            "combined_gradient_max_abs": combined_max,
            "trainable_leaves": list(v21.JOINT_TRAINABLE_KEYS),
        },
        "execution": {
            "optimizer_updates": 0,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "sources": {
            "contract_lf_sha256": lf_sha256(CONTRACT),
            "attribution_lf_sha256": lf_sha256(ATTRIBUTION),
            "runner_lf_sha256": lf_sha256(Path(__file__)),
        },
        "authority": {
            "robot_clearance": False,
            "training_executed": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "pass_authorizes_only": (
                "a separate frozen two-update predictor-preserving CPU proof"
            ),
        },
    }
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
