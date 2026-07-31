#!/usr/bin/env python3
"""Run the frozen two-update Winner-v22 normalized-predictor CPU proof."""

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

CONTRACT = ANALYSIS / "winner_v22_normalized_predictor_two_update_cpu_contract.json"
ZERO_UPDATE = ANALYSIS / "winner_v22_normalized_predictor_cpu_result.json"
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
        value.get("schema_version")
        != "winner_v22.normalized_predictor_two_update_cpu_contract.v1"
        or value.get("status")
        != "FROZEN_WINNER_V22_NORMALIZED_PREDICTOR_TWO_UPDATE_CPU_CONTRACT"
        or value.get("decision")
        != "AUTHORIZE_EXACT_TWO_UPDATE_NORMALIZED_PREDICTOR_PROOF_ONLY"
        or value.get("execution_now")
        != {
            "optimizer_updates": 0,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        }
    ):
        raise ValueError("Winner-v22 two-update contract changed")
    sources = value.get("sources")
    if not isinstance(sources, dict) or not sources:
        raise ValueError("Winner-v22 two-update sources are absent")
    for name, item in sources.items():
        path = ROOT / item["path"]
        if (
            set(item) != {"hash_mode", "path", "sha256"}
            or item["hash_mode"] != "lf"
            or lf_sha256(path) != item["sha256"]
        ):
            raise ValueError(f"Winner-v22 two-update source changed: {name}")
    if canonical_sha256(sources) != value.get("source_manifest_sha256"):
        raise ValueError("Winner-v22 two-update source-manifest digest changed")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--canonical-fit", type=Path, required=True)
    parser.add_argument("--stage1-final-snapshot", type=Path, required=True)
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--offline-cpu-only", action="store_true")
    parser.add_argument("--two-update-normalized-predictor-proof-authorized", action="store_true")
    args = parser.parse_args()
    if not args.offline_cpu_only or not args.two_update_normalized_predictor_proof_authorized:
        raise PermissionError(
            "Winner-v22 two-update proof requires --offline-cpu-only "
            "--two-update-normalized-predictor-proof-authorized"
        )
    if args.work_root.exists() or args.output.exists():
        raise FileExistsError("refusing to overwrite Winner-v22 two-update evidence")

    import jax
    import jax.numpy as jnp
    import mujoco
    import run_winner_v12_calibrator_cpu_smoke as smoke
    import run_winner_v12_full_calibrator_training as full
    import winner_v12_calibrator_training as training
    import winner_v12_decomposed_backend_networks as networks
    import winner_v15_pitch_margin_support as v15
    import winner_v20_joint_recurrent_support as v20
    import winner_v21_predictor_preserving_joint_support as v21
    import winner_v22_normalized_predictor as v22
    import winner_v22_normalized_predictor_v2 as v22v2

    if jax.default_backend() != "cpu" or any(
        device.platform != "cpu" for device in jax.devices()
    ):
        raise ValueError("Winner-v22 two-update proof requires CPU-only JAX")
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    validate_contract(contract)
    zero_update = json.loads(ZERO_UPDATE.read_text(encoding="utf-8"))
    stage1_result = json.loads(STAGE1_RESULT.read_text(encoding="utf-8"))
    if (
        zero_update.get("status") != "PASS_WINNER_V22_NORMALIZED_PREDICTOR_CPU_CONTRACT"
        or zero_update.get("failed_checks") != []
        or zero_update.get("objective", {}).get("balance", {}).get("predictor_scale")
        != float(v22v2.FROZEN_PREDICTOR_SCALE)
        or zero_update.get("execution", {}).get("optimizer_updates") != 0
        or stage1_result.get("status") != "PASS_WINNER_V13_NORMALIZED_RESPONSE_STAGE1"
        or stage1_result.get("failed_checks") != []
        or sha256(args.stage1_final_snapshot) != SNAPSHOT_SHA256
        or args.stage1_final_snapshot.stat().st_size != SNAPSHOT_BYTES
    ):
        raise ValueError("Winner-v22 two-update source evidence changed")
    restored = full.load_snapshot(args.stage1_final_snapshot)
    if (
        restored["metadata"].get("schema_version")
        != "winner_v13.normalized_response_stage1_snapshot.v1"
        or restored["metadata"].get("completed_updates") != 100
        or restored["metadata"].get("robot_or_rdk_access") != 0
    ):
        raise ValueError("Winner-v22 two-update source snapshot changed")

    expected_versions = dict(
        json.loads(FULL_PREREG.read_text(encoding="utf-8"))[
            "implementation_contract_environment"
        ]
    )
    if expected_versions.pop("platform") != "CPU only" or not smoke.validate_software_versions(
        {"software_versions": expected_versions}
    )["exact"]:
        raise ValueError("Winner-v22 two-update software environment changed")
    if smoke.sha256(args.canonical_fit) != smoke.P30_FIT_LF_SHA256:
        raise ValueError("Winner-v22 two-update P30 fit changed")
    if smoke.git_output(args.playground_root, "rev-parse", "HEAD") != smoke.CONTROL_COMMIT:
        raise ValueError("Winner-v22 two-update Playground source changed")
    smoke.validate_playground_tree(args.playground_root)
    scene = args.playground_root / smoke.SCENE_RELATIVE
    if smoke.sha256(scene) != smoke.SCENE_SHA256:
        raise ValueError("Winner-v22 two-update scene changed")

    full_prereg = json.loads(FULL_PREREG.read_text(encoding="utf-8"))
    domain = json.loads(DOMAIN.read_text(encoding="utf-8"))
    design = json.loads(smoke.CALIBRATOR_PREREG.read_text(encoding="utf-8"))
    population = full.training_population(full_prereg, domain)
    if len(population) != 80:
        raise ValueError("Winner-v22 two-update population changed")
    observer_type = smoke.load_runtime_observer(args.canonical_fit)
    source_parameters = restored["parameters"]
    parameters = source_parameters
    target_mean = jnp.asarray(restored["target_mean"], dtype=jnp.float32)
    target_std = jnp.asarray(restored["target_std"], dtype=jnp.float32)
    optimizer = training.adam_initialize(v21.joint_trainable_parameters(parameters))
    rollout_reports: list[dict[str, Any]] = []
    optimization_reports: list[dict[str, Any]] = []
    chain_observations: np.ndarray | None = None
    for update_index in range(2):
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
            update_index=update_index,
        )
        full.validate_stage2_masks(batch_np, episodes)
        episode_hash = full.validate_episode_receipts(
            episodes, population, stage=2, update_index=update_index
        )
        reward = v15.reward_evidence(batch_np)
        boundary = full.stage2_action_boundary_evidence(batch_np)
        batch = {key: jnp.asarray(value) for key, value in batch_np.items()}
        trainable_before = v21.joint_trainable_parameters(parameters)

        def ppo_objective(values: Mapping[str, Any], data: Mapping[str, Any]):
            return v20.joint_recurrent_ppo_loss(
                values,
                data,
                clip_epsilon=training.PPO_CLIP_EPSILON,
                value_coefficient=training.PPO_VALUE_COEFFICIENT,
                entropy_coefficient=training.PPO_ENTROPY_COEFFICIENT,
            )

        def predictor_objective(values: Mapping[str, Any], data: Mapping[str, Any]):
            return v22.normalized_predictor_loss(values, data, target_mean, target_std)

        (ppo_loss, ppo_metrics), ppo_gradients = jax.value_and_grad(
            ppo_objective, has_aux=True
        )(trainable_before, batch)
        (predictor_loss, predictor_metrics), predictor_gradients = jax.value_and_grad(
            predictor_objective, has_aux=True
        )(trainable_before, batch)
        gradients = v22v2.compose_gradients(ppo_gradients, predictor_gradients)
        combined_loss = ppo_loss + jnp.asarray(v22v2.FROZEN_PREDICTOR_SCALE) * predictor_loss
        trainable_after, optimizer = training.adam_step(
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
        parameters = v21.merge_joint_trainable(parameters, trainable_after)
        stored_count = int(
            np.sum(
                batch_np["valid_transition_mask"][:, :-1]
                * batch_np["valid_mask"][:, 1:]
            )
        )
        rollout_reports.append(
            {
                "update": update_index + 1,
                "episode_receipts_sha256": episode_hash,
                "sampled_count": int(np.sum(batch_np["valid_mask"])),
                "valid_transition_count": int(np.sum(batch_np["valid_transition_mask"])),
                "stored_successor_transition_count": stored_count,
                "stored_successor_mask_exact": int(
                    predictor_metrics["stored_successor_transition_count"]
                )
                == stored_count,
                "reward_formula_exact_and_nonzero": reward["reward_formula_bit_exact"]
                and reward["nonzero_penalty_count"] > 0,
                "action_boundary_exact": boundary["realized_equals_numpy_bit_exact"]
                and boundary["numpy_equals_jax_bit_exact"],
                "sampled_hidden_replay_max_abs_error": float(
                    ppo_metrics["sampled_hidden_replay_max_abs_error"]
                ),
            }
        )
        optimization_reports.append(
            {
                "update": update_index + 1,
                "ppo_loss": float(ppo_loss),
                "corrected_predictor_loss": float(predictor_loss),
                "combined_loss": float(combined_loss),
                "combined_gradient_max_abs": max_abs(gradients),
                "leaf_max_abs_delta": v20.leaf_max_abs_delta(
                    trainable_before, trainable_after
                ),
            }
        )
        if not training.finite_tree(
            {
                "ppo_loss": ppo_loss,
                "ppo_metrics": ppo_metrics,
                "predictor_loss": predictor_loss,
                "predictor_metrics": predictor_metrics,
                "gradients": gradients,
                "parameters": parameters,
                "optimizer": optimizer,
            }
        ):
            raise FloatingPointError(f"Winner-v22 update {update_index + 1} is nonfinite")

    if chain_observations is None:
        raise ValueError("Winner-v22 proof has no ONNX observations")
    cumulative = v20.leaf_max_abs_delta(
        v21.joint_trainable_parameters(source_parameters),
        v21.joint_trainable_parameters(parameters),
    )
    args.work_root.mkdir(parents=True, exist_ok=False)
    graph = args.work_root / "winner_v22_normalized_predictor_update_002.onnx"
    networks.export_calibrator_onnx(training.deployable_parameters(parameters), graph)
    graph_contract = smoke.onnx_contract(graph, parameters, chain_observations)
    snapshot = args.work_root / "winner_v22_normalized_predictor_update_002.npz"
    snapshot_receipt = v22v2.save_snapshot(
        snapshot,
        parameters,
        optimizer,
        {
            "stage": "normalized_predictor_joint_stage2",
            "completed_updates": 2,
            "source_stage1_snapshot_sha256": SNAPSHOT_SHA256,
            "predictor_scale": float(v22v2.FROZEN_PREDICTOR_SCALE),
            "predictor_formula": "prediction_normalized - normalized_next_response",
            "trainable_leaves": list(v21.JOINT_TRAINABLE_KEYS),
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        restored["target_mean"],
        restored["target_std"],
    )
    loaded = v22v2.load_snapshot(snapshot)
    checks = {
        "source_stage1_snapshot_exact": True,
        "both_exact_80_episode_populations": len(rollout_reports) == 2,
        "both_episode_receipts_exact": all(
            bool(row["episode_receipts_sha256"]) for row in rollout_reports
        ),
        "both_action_boundaries_exact": all(
            row["action_boundary_exact"] for row in rollout_reports
        ),
        "both_reward_formulas_exact_and_nonzero": all(
            row["reward_formula_exact_and_nonzero"] for row in rollout_reports
        ),
        "both_sampled_hidden_replays_at_most_1e_6": all(
            row["sampled_hidden_replay_max_abs_error"] <= 1.0e-6
            for row in rollout_reports
        ),
        "both_stored_successor_masks_exact": all(
            row["stored_successor_mask_exact"]
            and row["stored_successor_transition_count"] > 0
            for row in rollout_reports
        ),
        "frozen_corrected_predictor_scale_exact": float(
            v22v2.FROZEN_PREDICTOR_SCALE
        )
        == 380.9135437011719,
        "both_corrected_predictor_losses_finite_positive": all(
            np.isfinite(row["corrected_predictor_loss"])
            and row["corrected_predictor_loss"] > 0.0
            for row in optimization_reports
        ),
        "both_updates_all_12_gradients_and_deltas_nonzero": all(
            all(value > 0.0 for value in row["combined_gradient_max_abs"].values())
            and all(value > 0.0 for value in row["leaf_max_abs_delta"].values())
            for row in optimization_reports
        ),
        "cumulative_all_12_leaves_changed": all(value > 0.0 for value in cumulative.values()),
        "two_adam_updates_exact": int(np.asarray(optimizer["count"])) == 2,
        "snapshot_readback_exact": tree_equal(parameters, loaded["parameters"])
        and np.array_equal(np.asarray(optimizer["count"]), np.asarray(loaded["optimizer"]["count"]))
        and tree_equal(optimizer["m"], loaded["optimizer"]["m"])
        and tree_equal(optimizer["v"], loaded["optimizer"]["v"]),
        "onnx_abi_exact": graph_contract["abi_exact"],
        "onnx_training_only_tensors_absent": graph_contract["training_only_tensors_absent"],
        "onnx_jax_chain_at_most_1e_7": graph_contract["jax_onnx_at_most_1e_7"],
        "onnx_previous_action_chain_exact": graph_contract[
            "previous_action_out_equals_action_bit_exact"
        ],
        "formal_support_locomotion_robot_zero": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    result = {
        "schema_version": "winner_v22.normalized_predictor_two_update_cpu_result.v1",
        "status": (
            "PASS_WINNER_V22_NORMALIZED_PREDICTOR_TWO_UPDATE_CPU_PROOF"
            if not failed
            else "HOLD_WINNER_V22_NORMALIZED_PREDICTOR_TWO_UPDATE_CPU_PROOF"
        ),
        "decision": (
            "AUTHORIZE_SEPARATE_100_UPDATE_NORMALIZED_PREDICTOR_TRAINING_PREREGISTRATION_ONLY"
            if not failed
            else "DO_NOT_TRAIN_WINNER_V22"
        ),
        "checks": {name: bool(value) for name, value in checks.items()},
        "failed_checks": failed,
        "source_snapshot": {"sha256": SNAPSHOT_SHA256, "bytes": SNAPSHOT_BYTES},
        "predictor_scale": float(v22v2.FROZEN_PREDICTOR_SCALE),
        "rollouts": rollout_reports,
        "optimization": {
            "updates": optimization_reports,
            "cumulative_leaf_max_abs_delta": cumulative,
            "trainable_leaves": list(v21.JOINT_TRAINABLE_KEYS),
            "gradient_composition": "explicit g_ppo + frozen_scale * corrected_g_predictor",
        },
        "graph": {
            "path": str(graph),
            "sha256": sha256(graph),
            "bytes": graph.stat().st_size,
            "contract": graph_contract,
        },
        "snapshot": snapshot_receipt,
        "execution": {
            "optimizer_updates": 2,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "sources": {
            "contract_lf_sha256": lf_sha256(CONTRACT),
            "zero_update_lf_sha256": lf_sha256(ZERO_UPDATE),
            "runner_lf_sha256": lf_sha256(Path(__file__)),
        },
        "authority": {
            "robot_clearance": False,
            "training_executed": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "pass_authorizes_only": (
                "a separate frozen 100-update normalized-predictor training preregistration"
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
