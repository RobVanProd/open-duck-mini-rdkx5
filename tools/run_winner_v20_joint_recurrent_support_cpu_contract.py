#!/usr/bin/env python3
"""Run one exact CPU update of the Winner-v20 joint recurrent support arm."""

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

CONTRACT = ANALYSIS / "winner_v20_joint_recurrent_support_cpu_contract.json"
ATTRIBUTION = ANALYSIS / "winner_v20_joint_recurrent_support_attribution.json"
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
    return all(np.array_equal(np.asarray(left[name]), np.asarray(right[name])) for name in names)


def validate_source_manifest(contract: Mapping[str, Any]) -> None:
    sources = contract.get("sources")
    if not isinstance(sources, dict) or not sources:
        raise ValueError("Winner-v20 CPU source manifest is absent")
    for name, item in sources.items():
        path = ROOT / item["path"]
        if (
            set(item) != {"hash_mode", "path", "sha256"}
            or item["hash_mode"] != "lf"
            or lf_sha256(path) != item["sha256"]
        ):
            raise ValueError(f"Winner-v20 CPU source changed: {name}")
    if canonical_sha256(sources) != contract.get("source_manifest_sha256"):
        raise ValueError("Winner-v20 CPU source-manifest digest changed")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--canonical-fit", type=Path, required=True)
    parser.add_argument("--stage1-final-snapshot", type=Path, required=True)
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--offline-cpu-only", action="store_true")
    parser.add_argument("--one-update-joint-recurrent-contract-authorized", action="store_true")
    args = parser.parse_args()
    if not args.offline_cpu_only or not args.one_update_joint_recurrent_contract_authorized:
        raise PermissionError(
            "Winner-v20 CPU contract requires --offline-cpu-only "
            "--one-update-joint-recurrent-contract-authorized"
        )
    if args.work_root.exists() or args.output.exists():
        raise FileExistsError("refusing to overwrite Winner-v20 CPU evidence")

    import jax
    import jax.numpy as jnp
    import mujoco
    import run_winner_v12_calibrator_cpu_smoke as smoke
    import run_winner_v12_full_calibrator_training as full
    import winner_v12_calibrator_training as training
    import winner_v12_decomposed_backend_networks as networks
    import winner_v15_pitch_margin_support as v15
    import winner_v20_joint_recurrent_support as v20

    if jax.default_backend() != "cpu" or any(
        device.platform != "cpu" for device in jax.devices()
    ):
        raise ValueError("Winner-v20 contract requires CPU-only JAX")
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    if (
        contract.get("schema_version")
        != "winner_v20.joint_recurrent_support_cpu_contract.v1"
        or contract.get("status")
        != "FROZEN_WINNER_V20_JOINT_RECURRENT_SUPPORT_CPU_CONTRACT"
        or contract.get("decision")
        != "AUTHORIZE_ONE_JOINT_RECURRENT_PPO_PROOF_UPDATE_ONLY"
        or contract.get("execution_now")
        != {
            "optimizer_updates": 0,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        }
    ):
        raise ValueError("Winner-v20 CPU contract changed")
    validate_source_manifest(contract)
    attribution = json.loads(ATTRIBUTION.read_text(encoding="utf-8"))
    if (
        attribution.get("status")
        != "PASS_WINNER_V20_JOINT_RECURRENT_SUPPORT_ATTRIBUTION"
        or attribution.get("decision")
        != "PREREGISTER_ONE_JOINT_RECURRENT_PPO_CPU_CONTRACT"
    ):
        raise ValueError("Winner-v20 source attribution changed")
    stage1_result = json.loads(STAGE1_RESULT.read_text(encoding="utf-8"))
    if (
        stage1_result.get("status") != "PASS_WINNER_V13_NORMALIZED_RESPONSE_STAGE1"
        or stage1_result.get("failed_checks") != []
        or sha256(args.stage1_final_snapshot) != SNAPSHOT_SHA256
        or args.stage1_final_snapshot.stat().st_size != SNAPSHOT_BYTES
    ):
        raise ValueError("Winner-v20 Stage-1 source changed")
    restored = full.load_snapshot(args.stage1_final_snapshot)
    if (
        restored["metadata"].get("schema_version")
        != "winner_v13.normalized_response_stage1_snapshot.v1"
        or restored["metadata"].get("completed_updates") != 100
        or restored["metadata"].get("robot_or_rdk_access") != 0
    ):
        raise ValueError("Winner-v20 source snapshot metadata changed")

    expected_versions = dict(
        json.loads(FULL_PREREG.read_text(encoding="utf-8"))[
            "implementation_contract_environment"
        ]
    )
    if expected_versions.pop("platform") != "CPU only" or not smoke.validate_software_versions(
        {"software_versions": expected_versions}
    )["exact"]:
        raise ValueError("Winner-v20 software environment changed")
    if smoke.sha256(args.canonical_fit) != smoke.P30_FIT_LF_SHA256:
        raise ValueError("Winner-v20 canonical P30 fit changed")
    if smoke.git_output(args.playground_root, "rev-parse", "HEAD") != smoke.CONTROL_COMMIT:
        raise ValueError("Winner-v20 Playground source changed")
    smoke.validate_playground_tree(args.playground_root)
    scene = args.playground_root / smoke.SCENE_RELATIVE
    if smoke.sha256(scene) != smoke.SCENE_SHA256:
        raise ValueError("Winner-v20 scene changed")

    full_prereg = json.loads(FULL_PREREG.read_text(encoding="utf-8"))
    domain = json.loads(DOMAIN.read_text(encoding="utf-8"))
    design = json.loads(smoke.CALIBRATOR_PREREG.read_text(encoding="utf-8"))
    population = full.training_population(full_prereg, domain)
    if len(population) != 80:
        raise ValueError("Winner-v20 population changed")
    observer_type = smoke.load_runtime_observer(args.canonical_fit)
    parameters = restored["parameters"]
    auxiliary_before = v20.frozen_auxiliary_parameters(parameters)
    trainable_before = v20.joint_trainable_parameters(parameters)
    optimizer = training.adam_initialize(trainable_before)

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
    observations_masked = np.asarray(batch_np["observations"])[
        np.asarray(batch_np["valid_mask"], dtype=bool)
    ]
    observation_capture_exact = np.array_equal(
        observations_masked[: smoke.SMOKE_TICKS], chain_observations
    )
    reward = v15.reward_evidence(batch_np)
    boundary = full.stage2_action_boundary_evidence(batch_np)
    batch = {key: jnp.asarray(value) for key, value in batch_np.items()}

    def objective(values: Mapping[str, Any], data: Mapping[str, Any]):
        return v20.joint_recurrent_ppo_loss(
            values,
            data,
            clip_epsilon=training.PPO_CLIP_EPSILON,
            value_coefficient=training.PPO_VALUE_COEFFICIENT,
            entropy_coefficient=training.PPO_ENTROPY_COEFFICIENT,
        )

    (loss, loss_metrics), gradients = jax.value_and_grad(
        objective, has_aux=True
    )(trainable_before, batch)
    trainable_after, optimizer_after = training.adam_step(
        trainable_before,
        gradients,
        optimizer,
        learning_rate=training.STAGE2_LEARNING_RATE,
        beta1=training.ADAM_BETA1,
        beta2=training.ADAM_BETA2,
        epsilon=training.ADAM_EPSILON,
    )
    trainable_after = training.clamp_stage2_parameters(trainable_after)
    full.validate_log_std(trainable_after)
    parameters_after = v20.merge_joint_trainable(parameters, trainable_after)
    auxiliary_after = v20.frozen_auxiliary_parameters(parameters_after)
    deltas = v20.leaf_max_abs_delta(trainable_before, trainable_after)
    gradient_max = {
        key: float(np.max(np.abs(np.asarray(value)))) for key, value in gradients.items()
    }

    args.work_root.mkdir(parents=True, exist_ok=False)
    graph = args.work_root / "winner_v20_joint_recurrent_update_001.onnx"
    networks.export_calibrator_onnx(training.deployable_parameters(parameters_after), graph)
    graph_contract = smoke.onnx_contract(graph, parameters_after, chain_observations)
    snapshot = args.work_root / "winner_v20_joint_recurrent_update_001.npz"
    snapshot_receipt = full.save_snapshot(
        snapshot,
        parameters_after,
        optimizer_after,
        {
            "schema_version": "winner_v20.joint_recurrent_support_cpu_snapshot.v1",
            "stage": "joint_recurrent_stage2",
            "completed_updates": 1,
            "source_stage1_snapshot_sha256": SNAPSHOT_SHA256,
            "objective": "one_sided_negative_pitch_margin",
            "trainable_leaves": list(v20.JOINT_TRAINABLE_KEYS),
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        restored["target_mean"],
        restored["target_std"],
    )
    loaded = full.load_snapshot(snapshot)
    hidden_replay_error = float(loss_metrics["source_hidden_replay_max_abs_error"])
    checks = {
        "source_stage1_snapshot_exact": True,
        "exact_80_episode_population": len(episodes) == 80,
        "winner_v15_rollout_reward_action_masks_bit_exact": rollout_exact,
        "complete_observation_capture_exact": observation_capture_exact,
        "episode_receipts_exact": bool(episode_hash),
        "reward_formula_bit_exact": reward["reward_formula_bit_exact"]
        and reward["penalty_formula_bit_exact"],
        "reward_signal_nonzero": reward["nonzero_penalty_count"] > 0,
        "action_boundary_exact": boundary["realized_equals_numpy_bit_exact"]
        and boundary["numpy_equals_jax_bit_exact"],
        "source_hidden_replay_at_most_1e_6": hidden_replay_error <= 1.0e-6,
        "all_joint_gradients_nonzero": all(value > 0.0 for value in gradient_max.values()),
        "all_joint_leaves_changed": all(value > 0.0 for value in deltas.values()),
        "auxiliary_predictor_bit_exact_frozen": tree_equal(
            auxiliary_before, auxiliary_after
        ),
        "one_adam_update_exact": int(np.asarray(optimizer_after["count"])) == 1,
        "all_values_finite": training.finite_tree(
            {
                "loss": loss,
                "loss_metrics": loss_metrics,
                "gradients": gradients,
                "parameters": parameters_after,
                "optimizer": optimizer_after,
            }
        ),
        "snapshot_readback_exact": tree_equal(parameters_after, loaded["parameters"])
        and np.array_equal(
            np.asarray(optimizer_after["count"]), np.asarray(loaded["optimizer"]["count"])
        )
        and tree_equal(optimizer_after["m"], loaded["optimizer"]["m"])
        and tree_equal(optimizer_after["v"], loaded["optimizer"]["v"]),
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
        "schema_version": "winner_v20.joint_recurrent_support_cpu_result.v1",
        "status": (
            "PASS_WINNER_V20_JOINT_RECURRENT_SUPPORT_CPU_CONTRACT"
            if not failed
            else "HOLD_WINNER_V20_JOINT_RECURRENT_SUPPORT_CPU_CONTRACT"
        ),
        "decision": (
            "AUTHORIZE_SEPARATE_JOINT_RECURRENT_100_UPDATE_PREREGISTRATION_ONLY"
            if not failed
            else "DO_NOT_TRAIN_JOINT_RECURRENT_SUPPORT_ARM"
        ),
        "checks": checks,
        "failed_checks": failed,
        "environment": {
            "software_versions": expected_versions,
            "jax_devices": [str(device) for device in jax.devices()],
        },
        "source_snapshot": {"sha256": SNAPSHOT_SHA256, "bytes": SNAPSHOT_BYTES},
        "rollout": {
            "episode_receipts_sha256": episode_hash,
            "sampled_count": int(np.sum(batch_np["valid_mask"])),
            "valid_transition_count": int(np.sum(batch_np["valid_transition_mask"])),
            "reward": reward,
            "source_hidden_replay_max_abs_error": hidden_replay_error,
        },
        "optimization": {
            "loss": float(loss),
            "loss_metrics": {key: float(value) for key, value in loss_metrics.items()},
            "gradient_max_abs": gradient_max,
            "leaf_max_abs_delta": deltas,
            "trainable_leaves": list(v20.JOINT_TRAINABLE_KEYS),
            "frozen_auxiliary_leaves": list(v20.FROZEN_AUXILIARY_KEYS),
        },
        "graph": {
            "path": str(graph),
            "sha256": sha256(graph),
            "bytes": graph.stat().st_size,
            "contract": graph_contract,
        },
        "snapshot": snapshot_receipt,
        "execution": {
            "optimizer_updates": 1,
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
            "joint_recurrent_training_executed": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "pass_authorizes_only": (
                "a separate frozen 100-update joint-recurrent training preregistration"
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
