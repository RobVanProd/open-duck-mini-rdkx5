#!/usr/bin/env python3
"""Run one exact CPU update with the Winner-v15 pitch-margin objective."""

from __future__ import annotations

import argparse
import hashlib
import json
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

CONTRACT = ANALYSIS / "winner_v15_pitch_margin_cpu_contract.json"
ATTRIBUTION = ANALYSIS / "winner_v15_pitch_margin_objective_attribution.json"
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


def validate_source_manifest(contract: Mapping[str, Any]) -> None:
    sources = contract.get("sources")
    if not isinstance(sources, dict) or not sources:
        raise ValueError("Winner-v15 pitch-margin CPU source manifest is absent")
    for name, item in sources.items():
        path = ROOT / item["path"]
        if (
            set(item) != {"hash_mode", "path", "sha256"}
            or item["hash_mode"] != "lf"
            or lf_sha256(path) != item["sha256"]
        ):
            raise ValueError(f"Winner-v15 pitch-margin CPU source changed: {name}")
    if canonical_sha256(sources) != contract.get("source_manifest_sha256"):
        raise ValueError("Winner-v15 pitch-margin CPU source-manifest digest changed")


def arrays_equal(
    left: Mapping[str, np.ndarray],
    right: Mapping[str, np.ndarray],
    names: set[str],
) -> bool:
    return all(np.array_equal(np.asarray(left[name]), np.asarray(right[name])) for name in names)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--canonical-fit", type=Path, required=True)
    parser.add_argument("--stage1-final-snapshot", type=Path, required=True)
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--offline-cpu-only", action="store_true")
    parser.add_argument("--one-update-pitch-margin-contract-authorized", action="store_true")
    args = parser.parse_args()
    if not args.offline_cpu_only or not args.one_update_pitch_margin_contract_authorized:
        raise PermissionError(
            "pitch-margin CPU contract requires --offline-cpu-only "
            "--one-update-pitch-margin-contract-authorized"
        )
    if args.work_root.exists() or args.output.exists():
        raise FileExistsError("refusing to overwrite pitch-margin CPU evidence")

    import jax
    import jax.numpy as jnp
    import mujoco
    import run_winner_v12_calibrator_cpu_smoke as smoke
    import run_winner_v12_full_calibrator_training as full
    import winner_v12_calibrator_training as training
    import winner_v12_decomposed_backend_networks as networks
    import winner_v15_pitch_margin_support as pitch_margin

    if jax.default_backend() != "cpu" or any(
        device.platform != "cpu" for device in jax.devices()
    ):
        raise ValueError("Winner-v15 pitch-margin contract requires CPU-only JAX")
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    if (
        contract.get("schema_version") != "winner_v15.pitch_margin_cpu_contract.v1"
        or contract.get("status") != "FROZEN_WINNER_V15_PITCH_MARGIN_CPU_CONTRACT"
        or contract.get("decision")
        != "AUTHORIZE_ONE_RESTORED_PITCH_MARGIN_STAGE2_UPDATE_ONLY"
        or contract.get("execution_now")
        != {
            "stage2_optimizer_updates": 0,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        }
    ):
        raise ValueError("Winner-v15 pitch-margin CPU contract changed")
    validate_source_manifest(contract)
    attribution = json.loads(ATTRIBUTION.read_text(encoding="utf-8"))
    if (
        attribution.get("status")
        != "PASS_WINNER_V15_PITCH_MARGIN_OBJECTIVE_ATTRIBUTION"
        or attribution.get("decision")
        != "PREREGISTER_ONE_SIDED_NEGATIVE_PITCH_MARGIN_CPU_CONTRACT"
    ):
        raise ValueError("Winner-v15 objective attribution changed")
    stage1_result = json.loads(STAGE1_RESULT.read_text(encoding="utf-8"))
    if (
        stage1_result.get("status") != "PASS_WINNER_V13_NORMALIZED_RESPONSE_STAGE1"
        or stage1_result.get("failed_checks") != []
        or stage1_result.get("snapshot_manifest", [{}])[-1].get("sha256")
        != SNAPSHOT_SHA256
    ):
        raise ValueError("Winner-v13 Stage-1 source changed")
    if (
        sha256(args.stage1_final_snapshot) != SNAPSHOT_SHA256
        or args.stage1_final_snapshot.stat().st_size != SNAPSHOT_BYTES
    ):
        raise ValueError("Winner-v13 Stage-1 snapshot bytes changed")
    restored = full.load_snapshot(args.stage1_final_snapshot)
    metadata = restored["metadata"]
    if (
        metadata.get("schema_version")
        != "winner_v13.normalized_response_stage1_snapshot.v1"
        or metadata.get("stage") != "stage1"
        or metadata.get("completed_updates") != 100
        or int(np.asarray(restored["optimizer"]["count"])) != 100
        or metadata.get("robot_or_rdk_access") != 0
    ):
        raise ValueError("Winner-v13 Stage-1 snapshot metadata changed")
    expected_versions = dict(
        json.loads(FULL_PREREG.read_text(encoding="utf-8"))[
            "implementation_contract_environment"
        ]
    )
    if expected_versions.pop("platform") != "CPU only":
        raise ValueError("Winner-v15 pitch-margin platform changed")
    if not smoke.validate_software_versions(
        {"software_versions": expected_versions}
    )["exact"]:
        raise ValueError("Winner-v15 pitch-margin software versions changed")
    if smoke.sha256(args.canonical_fit) != smoke.P30_FIT_LF_SHA256:
        raise ValueError("canonical P30 fit changed")
    if smoke.git_output(args.playground_root, "rev-parse", "HEAD") != smoke.CONTROL_COMMIT:
        raise ValueError("Playground source commit changed")
    smoke.validate_playground_tree(args.playground_root)
    scene = args.playground_root / smoke.SCENE_RELATIVE
    if smoke.sha256(scene) != smoke.SCENE_SHA256:
        raise ValueError("Winner-v15 pitch-margin scene changed")

    full_prereg = json.loads(FULL_PREREG.read_text(encoding="utf-8"))
    domain = json.loads(DOMAIN.read_text(encoding="utf-8"))
    design = json.loads(smoke.CALIBRATOR_PREREG.read_text(encoding="utf-8"))
    population = full.training_population(full_prereg, domain)
    if len(population) != 80:
        raise ValueError("Winner-v15 pitch-margin population changed")
    observer_type = smoke.load_runtime_observer(args.canonical_fit)
    parameters = restored["parameters"]
    stage1_before = training.stage1_parameters(parameters)
    stage2_before = training.stage2_parameters(parameters)
    optimizer = training.adam_initialize(stage2_before)

    base_batch, base_episodes, base_observations = full.stage2_rollout(
        mujoco,
        scene,
        population,
        design,
        observer_type,
        args.canonical_fit,
        parameters,
        0,
    )
    off_batch, off_episodes, off_observations = pitch_margin.stage2_rollout(
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
        enabled=False,
    )
    enabled_batch, enabled_episodes, enabled_observations = pitch_margin.stage2_rollout(
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
    full.validate_stage2_masks(base_batch, base_episodes)
    full.validate_stage2_masks(off_batch, off_episodes)
    full.validate_stage2_masks(enabled_batch, enabled_episodes)
    episode_hash = full.validate_episode_receipts(
        enabled_episodes, population, stage=2, update_index=0
    )
    base_keys = set(base_batch)
    default_off_exact = (
        arrays_equal(base_batch, off_batch, base_keys)
        and base_episodes == off_episodes
        and np.array_equal(base_observations, off_observations)
    )
    transition_keys = base_keys - {"returns", "advantages"}
    enabled_transition_exact = (
        arrays_equal(base_batch, enabled_batch, transition_keys)
        and base_episodes == enabled_episodes
        and np.array_equal(base_observations, enabled_observations)
    )
    objective_changes_learning_targets = (
        not np.array_equal(base_batch["returns"], enabled_batch["returns"])
        and not np.array_equal(base_batch["advantages"], enabled_batch["advantages"])
    )
    off_valid = np.asarray(off_batch["valid_transition_mask"], dtype=bool)
    off_expected_rewards = off_valid.astype(np.float32)
    for environment, receipt in enumerate(off_episodes):
        if receipt["terminal_success_bonus_applied"]:
            off_expected_rewards[environment, smoke.SMOKE_TICKS - 1] += np.float32(
                smoke.TERMINAL_BONUS
            )
    default_off_reward_exact = np.array_equal(
        off_batch["rewards"], off_expected_rewards
    ) and np.array_equal(
        off_batch["applied_negative_pitch_penalty"],
        np.zeros_like(off_batch["applied_negative_pitch_penalty"]),
    )
    reward_proof = pitch_margin.reward_evidence(enabled_batch)
    action_boundary = full.stage2_action_boundary_evidence(enabled_batch)
    if not (
        action_boundary["realized_equals_numpy_bit_exact"]
        and action_boundary["numpy_equals_jax_bit_exact"]
    ):
        raise ValueError("Winner-v15 pitch-margin action boundary changed")

    batch = {key: jnp.asarray(value) for key, value in enabled_batch.items()}

    def objective(values: Mapping[str, Any], data: Mapping[str, Any]):
        return training.stage2_ppo_loss(
            values,
            data,
            clip_epsilon=training.PPO_CLIP_EPSILON,
            value_coefficient=training.PPO_VALUE_COEFFICIENT,
            entropy_coefficient=training.PPO_ENTROPY_COEFFICIENT,
        )

    (loss, loss_metrics), gradients = jax.value_and_grad(
        objective, has_aux=True
    )(stage2_before, batch)
    stage2_after, optimizer_after = training.adam_step(
        stage2_before,
        gradients,
        optimizer,
        learning_rate=training.STAGE2_LEARNING_RATE,
        beta1=training.ADAM_BETA1,
        beta2=training.ADAM_BETA2,
        epsilon=training.ADAM_EPSILON,
    )
    stage2_after = training.clamp_stage2_parameters(stage2_after)
    full.validate_log_std(stage2_after)
    parameters_after = training.merge_stage2(parameters, stage2_after)
    stage1_after = training.stage1_parameters(parameters_after)
    stage2_deltas = training.leaf_max_abs_delta(stage2_before, stage2_after)
    gradient_max = {
        key: float(np.max(np.abs(np.asarray(value))))
        for key, value in gradients.items()
    }
    args.work_root.mkdir(parents=True, exist_ok=False)
    graph = args.work_root / "winner_v15_pitch_margin_update_001.onnx"
    networks.export_calibrator_onnx(training.deployable_parameters(parameters_after), graph)
    graph_contract = smoke.onnx_contract(graph, parameters_after, enabled_observations)
    snapshot = args.work_root / "winner_v15_pitch_margin_update_001.npz"
    snapshot_receipt = full.save_snapshot(
        snapshot,
        parameters_after,
        optimizer_after,
        {
            "schema_version": "winner_v15.pitch_margin_cpu_snapshot.v1",
            "stage": "stage2",
            "completed_updates": 1,
            "source_stage1_snapshot_sha256": SNAPSHOT_SHA256,
            "objective": "one_sided_negative_pitch_margin",
            "objective_boundary_rad": 0.35,
            "metrics": [],
            "cumulative_sampled_count": int(np.sum(enabled_batch["valid_mask"])),
            "cumulative_valid_transition_count": int(
                np.sum(enabled_batch["valid_transition_mask"])
            ),
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        restored["target_mean"],
        restored["target_std"],
    )
    loaded_after = full.load_snapshot(snapshot)
    checks = {
        "source_stage1_snapshot_exact": True,
        "exact_80_episode_population": len(enabled_episodes) == 80,
        "default_off_batch_episode_observation_bit_exact": default_off_exact,
        "default_off_reward_bit_exact": default_off_reward_exact,
        "enabled_transition_action_episode_observation_bit_exact": enabled_transition_exact,
        "enabled_changes_only_returns_and_advantages": objective_changes_learning_targets,
        "enabled_reward_formula_bit_exact": reward_proof["reward_formula_bit_exact"],
        "enabled_penalty_formula_bit_exact": reward_proof["penalty_formula_bit_exact"],
        "enabled_penalty_nonzero": reward_proof["nonzero_penalty_count"] > 0,
        "enabled_reward_and_penalty_bounded": reward_proof["all_rewards_nonnegative"]
        and reward_proof["all_penalties_in_unit_interval"]
        and reward_proof["only_zero_or_settled_bonus"],
        "stage2_masks_exact": True,
        "action_boundary_exact": True,
        "all_stage2_gradients_nonzero": all(value > 0.0 for value in gradient_max.values()),
        "one_adam_update_exact": int(np.asarray(optimizer_after["count"])) == 1,
        "stage1_tree_bit_exact_frozen": tree_equal(stage1_before, stage1_after),
        "all_stage2_leaves_changed": all(value > 0.0 for value in stage2_deltas.values()),
        "all_values_finite": training.finite_tree(
            {
                "loss": loss,
                "loss_metrics": loss_metrics,
                "gradients": gradients,
                "parameters": parameters_after,
                "optimizer": optimizer_after,
            }
        ),
        "snapshot_readback_exact": tree_equal(
            parameters_after, loaded_after["parameters"]
        )
        and np.array_equal(
            np.asarray(optimizer_after["count"]),
            np.asarray(loaded_after["optimizer"]["count"]),
        )
        and tree_equal(optimizer_after["m"], loaded_after["optimizer"]["m"])
        and tree_equal(optimizer_after["v"], loaded_after["optimizer"]["v"]),
        "onnx_abi_exact": graph_contract["abi_exact"],
        "onnx_training_only_tensors_absent": graph_contract[
            "training_only_tensors_absent"
        ],
        "onnx_jax_chain_at_most_1e_7": graph_contract["jax_onnx_at_most_1e_7"],
        "onnx_previous_action_chain_exact": graph_contract[
            "previous_action_out_equals_action_bit_exact"
        ],
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    result = {
        "schema_version": "winner_v15.pitch_margin_cpu_result.v1",
        "status": (
            "PASS_WINNER_V15_PITCH_MARGIN_CPU_CONTRACT"
            if not failed
            else "HOLD_WINNER_V15_PITCH_MARGIN_CPU_CONTRACT"
        ),
        "decision": (
            "AUTHORIZE_PITCH_MARGIN_SUPPORT_TRAINING_PREREGISTRATION_ONLY"
            if not failed
            else "DO_NOT_TRAIN_PITCH_MARGIN_SUPPORT_CONTROLLER"
        ),
        "checks": checks,
        "failed_checks": failed,
        "proof": {
            "source_snapshot_sha256": SNAPSHOT_SHA256,
            "source_snapshot_bytes": SNAPSHOT_BYTES,
            "episode_receipts_sha256": episode_hash,
            "sampled_count": int(np.sum(enabled_batch["valid_mask"])),
            "valid_transition_count": int(
                np.sum(enabled_batch["valid_transition_mask"])
            ),
            "reward": reward_proof,
            "loss": float(loss),
            "loss_metrics": {key: float(value) for key, value in loss_metrics.items()},
            "gradient_max_abs": gradient_max,
            "stage2_leaf_max_abs_delta": stage2_deltas,
            "action_boundary": action_boundary,
            "graph_contract": graph_contract,
            "snapshot": snapshot_receipt,
        },
        "execution": {
            "stage2_optimizer_updates": 1,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "sources": {
            "contract_lf_sha256": lf_sha256(CONTRACT),
            "attribution_lf_sha256": lf_sha256(ATTRIBUTION),
            "stage1_result_lf_sha256": lf_sha256(STAGE1_RESULT),
            "runner_lf_sha256": lf_sha256(Path(__file__)),
        },
        "authority": {
            "robot_clearance": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "pass_authorizes_only": "a separate pitch-margin support-training preregistration",
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
