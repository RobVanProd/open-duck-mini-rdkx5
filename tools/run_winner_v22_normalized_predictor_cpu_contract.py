#!/usr/bin/env python3
"""Run the zero-update Winner-v22 normalized-predictor CPU contract."""

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

CONTRACT = ANALYSIS / "winner_v22_normalized_predictor_cpu_contract.json"
ATTRIBUTION = ANALYSIS / "winner_v21_normalized_semantics_attribution.json"
TRAINING_RESULT = ANALYSIS / "winner_v21_predictor_preserving_training_result.json"
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


def max_abs(tree: Mapping[str, Any]) -> dict[str, float]:
    return {
        key: float(np.max(np.abs(np.asarray(value)))) for key, value in tree.items()
    }


def validate_contract(value: Mapping[str, Any]) -> None:
    if (
        value.get("schema_version") != "winner_v22.normalized_predictor_cpu_contract.v1"
        or value.get("status") != "FROZEN_WINNER_V22_NORMALIZED_PREDICTOR_CPU_CONTRACT"
        or value.get("decision") != "AUTHORIZE_ONE_ZERO_UPDATE_NORMALIZED_SEMANTICS_PROOF_ONLY"
        or value.get("execution_now")
        != {
            "optimizer_updates": 0,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        }
    ):
        raise ValueError("Winner-v22 CPU contract changed")
    sources = value.get("sources")
    if not isinstance(sources, dict) or not sources:
        raise ValueError("Winner-v22 source manifest is absent")
    for name, item in sources.items():
        path = ROOT / item["path"]
        if (
            set(item) != {"hash_mode", "path", "sha256"}
            or item["hash_mode"] != "lf"
            or lf_sha256(path) != item["sha256"]
        ):
            raise ValueError(f"Winner-v22 source changed: {name}")
    if canonical_sha256(sources) != value.get("source_manifest_sha256"):
        raise ValueError("Winner-v22 source-manifest digest changed")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--canonical-fit", type=Path, required=True)
    parser.add_argument("--stage1-final-snapshot", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--offline-cpu-only", action="store_true")
    parser.add_argument("--zero-update-normalized-semantics-proof-authorized", action="store_true")
    args = parser.parse_args()
    if not args.offline_cpu_only or not args.zero_update_normalized_semantics_proof_authorized:
        raise PermissionError(
            "Winner-v22 contract requires --offline-cpu-only "
            "--zero-update-normalized-semantics-proof-authorized"
        )
    if args.output.exists():
        raise FileExistsError("refusing to overwrite Winner-v22 CPU evidence")

    import jax
    import jax.numpy as jnp
    import mujoco
    import run_winner_v12_calibrator_cpu_smoke as smoke
    import run_winner_v12_full_calibrator_training as full
    import winner_v12_calibrator_training as training
    import winner_v15_pitch_margin_support as v15
    import winner_v20_joint_recurrent_support as v20
    import winner_v21_predictor_preserving_joint_support as v21
    import winner_v22_normalized_predictor as v22

    if jax.default_backend() != "cpu" or any(
        device.platform != "cpu" for device in jax.devices()
    ):
        raise ValueError("Winner-v22 requires CPU-only JAX")
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    validate_contract(contract)
    attribution = json.loads(ATTRIBUTION.read_text(encoding="utf-8"))
    completed_v21 = json.loads(TRAINING_RESULT.read_text(encoding="utf-8"))
    stage1_result = json.loads(STAGE1_RESULT.read_text(encoding="utf-8"))
    if (
        attribution.get("status") != "PASS_WINNER_V21_NORMALIZED_SEMANTICS_ATTRIBUTION"
        or attribution.get("decision") != "AUTHORIZE_CORRECT_NORMALIZED_PREDICTOR_CPU_CONTRACT_ONLY"
        or attribution.get("authority", {}).get("optimizer_updates_authorized_now") != 0
        or completed_v21.get("status")
        != "PASS_WINNER_V21_PREDICTOR_PRESERVING_TRAINING_ARTIFACT"
        or stage1_result.get("status") != "PASS_WINNER_V13_NORMALIZED_RESPONSE_STAGE1"
        or stage1_result.get("failed_checks") != []
        or sha256(args.stage1_final_snapshot) != SNAPSHOT_SHA256
        or args.stage1_final_snapshot.stat().st_size != SNAPSHOT_BYTES
    ):
        raise ValueError("Winner-v22 source evidence changed")
    restored = full.load_snapshot(args.stage1_final_snapshot)
    if (
        restored["metadata"].get("schema_version")
        != "winner_v13.normalized_response_stage1_snapshot.v1"
        or restored["metadata"].get("completed_updates") != 100
        or restored["metadata"].get("robot_or_rdk_access") != 0
    ):
        raise ValueError("Winner-v22 source snapshot changed")

    expected_versions = dict(
        json.loads(FULL_PREREG.read_text(encoding="utf-8"))[
            "implementation_contract_environment"
        ]
    )
    if expected_versions.pop("platform") != "CPU only" or not smoke.validate_software_versions(
        {"software_versions": expected_versions}
    )["exact"]:
        raise ValueError("Winner-v22 software environment changed")
    if smoke.sha256(args.canonical_fit) != smoke.P30_FIT_LF_SHA256:
        raise ValueError("Winner-v22 canonical P30 fit changed")
    if smoke.git_output(args.playground_root, "rev-parse", "HEAD") != smoke.CONTROL_COMMIT:
        raise ValueError("Winner-v22 Playground source changed")
    smoke.validate_playground_tree(args.playground_root)
    scene = args.playground_root / smoke.SCENE_RELATIVE
    if smoke.sha256(scene) != smoke.SCENE_SHA256:
        raise ValueError("Winner-v22 scene changed")

    full_prereg = json.loads(FULL_PREREG.read_text(encoding="utf-8"))
    domain = json.loads(DOMAIN.read_text(encoding="utf-8"))
    design = json.loads(smoke.CALIBRATOR_PREREG.read_text(encoding="utf-8"))
    population = full.training_population(full_prereg, domain)
    if len(population) != 80:
        raise ValueError("Winner-v22 population changed")
    observer_type = smoke.load_runtime_observer(args.canonical_fit)
    parameters = restored["parameters"]
    source_parameters = {key: np.asarray(value).copy() for key, value in parameters.items()}
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
        update_index=0,
    )
    full.validate_stage2_masks(batch_np, episodes)
    episode_hash = full.validate_episode_receipts(
        episodes, population, stage=2, update_index=0
    )
    boundary = full.stage2_action_boundary_evidence(batch_np)
    reward = v15.reward_evidence(batch_np)
    batch = {key: jnp.asarray(value) for key, value in batch_np.items()}
    trainable = v21.joint_trainable_parameters(parameters)
    target_mean = jnp.asarray(restored["target_mean"], dtype=jnp.float32)
    target_std = jnp.asarray(restored["target_std"], dtype=jnp.float32)

    def ppo_objective(values: Mapping[str, Any], data: Mapping[str, Any]):
        return v20.joint_recurrent_ppo_loss(
            values,
            data,
            clip_epsilon=training.PPO_CLIP_EPSILON,
            value_coefficient=training.PPO_VALUE_COEFFICIENT,
            entropy_coefficient=training.PPO_ENTROPY_COEFFICIENT,
        )

    def corrected_objective(values: Mapping[str, Any], data: Mapping[str, Any]):
        return v22.normalized_predictor_loss(values, data, target_mean, target_std)

    def old_objective(values: Mapping[str, Any], data: Mapping[str, Any]):
        return v21.predictor_loss(values, data, target_std)

    (ppo_loss, ppo_metrics), ppo_gradients = jax.value_and_grad(
        ppo_objective, has_aux=True
    )(trainable, batch)
    (corrected_loss, corrected_metrics), corrected_gradients = jax.value_and_grad(
        corrected_objective, has_aux=True
    )(trainable, batch)
    old_loss, old_metrics = old_objective(trainable, batch)
    scale, scale_receipt = v21.gradient_balance_scale(
        ppo_gradients, corrected_gradients
    )
    combined_gradients = {
        key: ppo_gradients[key] + jnp.asarray(scale) * corrected_gradients[key]
        for key in v21.JOINT_TRAINABLE_KEYS
    }

    observations = np.asarray(batch_np["observations"], dtype=np.float32)
    previous = np.asarray(batch_np["previous_actions"], dtype=np.float32)
    realized = np.asarray(batch_np["realized_actions"], dtype=np.float32)
    hidden = np.asarray(
        v20.recurrent_hidden_trajectory(
            trainable, jnp.asarray(observations), jnp.asarray(previous)
        ),
        dtype=np.float32,
    )
    prediction = (
        hidden @ np.asarray(trainable["auxiliary_hidden_weight"])
        + realized @ np.asarray(trainable["auxiliary_action_weight"])
        + np.asarray(trainable["auxiliary_bias"])
    )[:, :-1]
    target_raw = observations[:, 1:, training.AUXILIARY_INDICES]
    independent_sq = v22.normalized_prediction_squared_error(
        prediction,
        target_raw,
        np.asarray(restored["target_mean"]),
        np.asarray(restored["target_std"]),
    )
    mask = (
        np.asarray(batch_np["valid_transition_mask"], dtype=np.float64)[:, :-1]
        * np.asarray(batch_np["valid_mask"], dtype=np.float64)[:, 1:]
    )[..., None]
    independent_loss = float(
        np.sum(independent_sq * mask)
        / max(float(np.sum(mask) * len(training.AUXILIARY_INDICES)), 1.0)
    )
    stored_count = int(np.sum(mask))
    corrected_value = float(corrected_loss)
    old_value = float(old_loss)
    old_reference = float(completed_v21["metrics"][0]["predictor_loss"])
    corrected_error = abs(corrected_value - independent_loss)
    corrected_tolerance = max(1.0e-5, abs(independent_loss) * 1.0e-6)
    corrected_max = max_abs(corrected_gradients)
    ppo_max = max_abs(ppo_gradients)
    combined_max = max_abs(combined_gradients)
    contact_mean = np.asarray(restored["target_mean"], dtype=np.float64)[48:50]
    contact_std = np.asarray(restored["target_std"], dtype=np.float64)[48:50]
    contact_prediction = np.zeros((2,), dtype=np.float64)
    corrected_contact = v22.normalized_prediction_squared_error(
        contact_prediction, contact_mean, contact_mean, contact_std
    )
    old_contact = np.square((contact_prediction - contact_mean) / contact_std)
    checks = {
        "source_stage1_snapshot_exact": True,
        "exact_80_episode_population": len(episodes) == 80,
        "episode_receipts_exact": bool(episode_hash),
        "action_boundary_exact": boundary["realized_equals_numpy_bit_exact"]
        and boundary["numpy_equals_jax_bit_exact"],
        "reward_formula_exact_and_nonzero": reward["reward_formula_bit_exact"]
        and reward["nonzero_penalty_count"] > 0,
        "stored_successor_mask_exact": int(
            corrected_metrics["stored_successor_transition_count"]
        )
        == stored_count
        and stored_count > 0,
        "corrected_jax_matches_independent_numpy": corrected_error
        <= corrected_tolerance,
        "old_formula_reproduces_completed_update1": old_value == old_reference,
        "corrected_loss_finite_positive": math.isfinite(corrected_value)
        and corrected_value > 0.0,
        "corrected_loss_below_old_by_six_orders": corrected_value * 1.0e6
        < old_value,
        "constant_contact_target_is_zero_error_only_under_correct_semantics": bool(
            np.array_equal(corrected_contact, np.zeros((2,), dtype=np.float64))
            and np.all(old_contact > 1.0e10)
        ),
        "corrected_predictor_gradient_partition_exact": all(
            corrected_max[name] > 0.0
            for name in (*v21.RECURRENT_KEYS, *v21.PREDICTOR_KEYS)
        )
        and all(corrected_max[name] == 0.0 for name in v21.PPO_ONLY_KEYS),
        "ppo_gradient_partition_exact": all(
            ppo_max[name] == 0.0
            for name in (*v21.RECURRENT_KEYS, *v21.PREDICTOR_KEYS)
        )
        and all(ppo_max[name] > 0.0 for name in v21.PPO_ONLY_KEYS),
        "single_balance_scale_finite_positive": math.isfinite(float(scale))
        and float(scale) > 0.0,
        "combined_all_12_gradients_nonzero": all(
            combined_max[name] > 0.0 for name in v21.JOINT_TRAINABLE_KEYS
        ),
        "all_losses_gradients_and_metrics_finite": training.finite_tree(
            {
                "ppo_loss": ppo_loss,
                "ppo_metrics": ppo_metrics,
                "corrected_loss": corrected_loss,
                "corrected_metrics": corrected_metrics,
                "old_loss": old_loss,
                "old_metrics": old_metrics,
                "ppo_gradients": ppo_gradients,
                "corrected_gradients": corrected_gradients,
                "combined_gradients": combined_gradients,
            }
        ),
        "parameters_bit_exact_unchanged": tree_equal(source_parameters, parameters),
        "optimizer_updates_zero": True,
        "formal_support_locomotion_robot_zero": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    result = {
        "schema_version": "winner_v22.normalized_predictor_cpu_result.v1",
        "status": (
            "PASS_WINNER_V22_NORMALIZED_PREDICTOR_CPU_CONTRACT"
            if not failed
            else "HOLD_WINNER_V22_NORMALIZED_PREDICTOR_CPU_CONTRACT"
        ),
        "decision": (
            "AUTHORIZE_SEPARATE_TWO_UPDATE_NORMALIZED_PREDICTOR_PROOF_PREREGISTRATION_ONLY"
            if not failed
            else "DO_NOT_UPDATE_OR_TRAIN_WINNER_V22"
        ),
        "checks": {name: bool(value) for name, value in checks.items()},
        "failed_checks": failed,
        "source_snapshot": {"sha256": SNAPSHOT_SHA256, "bytes": SNAPSHOT_BYTES},
        "rollout": {
            "episode_receipts_sha256": episode_hash,
            "sampled_count": int(np.sum(batch_np["valid_mask"])),
            "valid_transition_count": int(np.sum(batch_np["valid_transition_mask"])),
            "stored_successor_transition_count": stored_count,
        },
        "objective": {
            "formula": "prediction_normalized - ((next_response_raw - target_mean) / target_std)",
            "ppo_loss": float(ppo_loss),
            "corrected_predictor_loss": corrected_value,
            "independent_numpy_loss": independent_loss,
            "corrected_numpy_jax_abs_error": corrected_error,
            "old_raw_coordinate_loss": old_value,
            "old_completed_update1_reference": old_reference,
            "old_to_corrected_ratio": old_value / corrected_value,
            "balance": scale_receipt,
            "corrected_gradient_max_abs": corrected_max,
            "combined_gradient_max_abs": combined_max,
            "contact_mean": contact_mean.tolist(),
            "contact_std": contact_std.tolist(),
            "corrected_contact_error": corrected_contact.tolist(),
            "old_contact_error": old_contact.tolist(),
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
                "a separate frozen two-update normalized-predictor CPU proof"
            ),
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(result["status"])
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
