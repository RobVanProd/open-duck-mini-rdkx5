#!/usr/bin/env python3
"""Run the one frozen 100-update Winner-v24 baseline-anchored CPU arm."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
import time
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

PREREGISTRATION = ANALYSIS / "winner_v24_baseline_anchored_training_preregistration.json"
ONE_UPDATE_RESULT = ANALYSIS / "winner_v24_baseline_anchored_one_update_cpu_result_v2.json"
V22_TRAINING = ANALYSIS / "winner_v22_normalized_predictor_training_result.json"
FULL_PREREG = ANALYSIS / "winner_v12_full_calibrator_training_preregistration.json"
DOMAIN = ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
UPDATES = 100
SOURCE_COMPLETED_UPDATES = 100
HALF_COMPLETED_UPDATES = 150
FINAL_COMPLETED_UPDATES = 200


def validate_preregistration(value: Mapping[str, Any], common: Any) -> None:
    if (
        value.get("schema_version")
        != "winner_v24.baseline_anchored_training_preregistration.v1"
        or value.get("status")
        != "PREREGISTERED_WINNER_V24_BASELINE_ANCHORED_TRAINING"
        or value.get("decision")
        != "AUTHORIZE_ONE_100_UPDATE_BASELINE_ANCHORED_ARM_ONLY"
        or value.get("execution_now")
        != {
            "optimizer_updates": 0,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        }
    ):
        raise ValueError("Winner-v24 training preregistration changed")
    frozen = value.get("frozen_training", {})
    if (
        frozen.get("source_completed_updates") != 100
        or frozen.get("source_optimizer_count") != 100
        or frozen.get("continuation_optimizer_updates") != 100
        or frozen.get("final_optimizer_count") != 200
        or frozen.get("environments_per_update") != 80
        or frozen.get("ticks_per_environment") != 250
        or frozen.get("scheduled_episode_slots") != 2_000_000
        or frozen.get("training_root_seed") != 120120
        or frozen.get("learning_rate") != 0.0001
        or frozen.get("predictor_scale") != 380.9135437011719
        or frozen.get("persistent_checkpoints")
        != {"half": 150, "final": 200}
    ):
        raise ValueError("Winner-v24 training constants changed")
    sources = value.get("sources")
    if not isinstance(sources, dict) or not sources:
        raise ValueError("Winner-v24 training sources are absent")
    for name, item in sources.items():
        path = ROOT / item["path"]
        if (
            set(item) != {"hash_mode", "path", "sha256"}
            or item["hash_mode"] != "lf"
            or common.lf_sha256(path) != item["sha256"]
        ):
            raise ValueError(f"Winner-v24 training source changed: {name}")
    if common.canonical_sha256(sources) != value.get("source_manifest_sha256"):
        raise ValueError("Winner-v24 training source manifest changed")


def graph_receipt(
    *, smoke: Any, networks: Any, training: Any,
    parameters: Mapping[str, Any], observations: np.ndarray,
    path: Path, label: str, completed_updates: int, common: Any,
) -> dict[str, Any]:
    networks.export_calibrator_onnx(training.deployable_parameters(parameters), path)
    contract = smoke.onnx_contract(path, parameters, observations)
    if not all(
        contract[name]
        for name in (
            "abi_exact", "training_only_tensors_absent", "jax_onnx_at_most_1e_7",
            "previous_action_out_equals_action_bit_exact",
        )
    ):
        raise ValueError(f"Winner-v24 {label} graph contract failed")
    return {
        "label": label,
        "completed_updates": completed_updates,
        "path": str(path),
        "sha256": common.sha256(path),
        "bytes": path.stat().st_size,
        "contract": contract,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--canonical-fit", type=Path, required=True)
    parser.add_argument("--final-snapshot", type=Path, required=True)
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--offline-cpu-only", action="store_true")
    parser.add_argument("--baseline-anchored-training-authorized", action="store_true")
    args = parser.parse_args()
    if not args.offline_cpu_only or not args.baseline_anchored_training_authorized:
        raise PermissionError(
            "Winner-v24 training requires --offline-cpu-only "
            "--baseline-anchored-training-authorized"
        )
    if args.work_root.exists() or args.output.exists():
        raise FileExistsError("refusing to overwrite Winner-v24 training evidence")

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
    import winner_v24_symmetric_support_failure_v3 as v24v3

    if jax.default_backend() != "cpu" or any(
        device.platform != "cpu" for device in jax.devices()
    ):
        raise ValueError("Winner-v24 training requires CPU-only JAX")
    preregistration = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    validate_preregistration(preregistration, common)
    one_update = json.loads(ONE_UPDATE_RESULT.read_text(encoding="utf-8"))
    training_result = json.loads(V22_TRAINING.read_text(encoding="utf-8"))
    if (
        one_update.get("status")
        != "PASS_WINNER_V24_BASELINE_ANCHORED_ONE_UPDATE_CPU_PROOF"
        or one_update.get("decision")
        != "AUTHORIZE_SEPARATE_BASELINE_ANCHORED_TRAINING_PREREGISTRATION_ONLY"
        or one_update.get("failed_checks") != []
        or one_update.get("execution", {}).get("optimizer_updates") != 1
        or training_result.get("status")
        != "PASS_WINNER_V22_NORMALIZED_PREDICTOR_TRAINING_ARTIFACT"
        or training_result.get("failed_checks") != []
    ):
        raise ValueError("Winner-v24 training source evidence changed")
    final_receipt = training_result["snapshot_manifest"][99]
    if (
        final_receipt.get("completed_updates") != 100
        or common.sha256(args.final_snapshot) != final_receipt.get("sha256")
        or args.final_snapshot.stat().st_size != final_receipt.get("bytes")
    ):
        raise ValueError("Winner-v24 training source snapshot changed")

    expected_versions = dict(
        json.loads(FULL_PREREG.read_text(encoding="utf-8"))[
            "implementation_contract_environment"
        ]
    )
    if expected_versions.pop("platform") != "CPU only" or not smoke.validate_software_versions(
        {"software_versions": expected_versions}
    )["exact"]:
        raise ValueError("Winner-v24 training environment changed")
    if smoke.sha256(args.canonical_fit) != smoke.P30_FIT_LF_SHA256:
        raise ValueError("Winner-v24 training P30 fit changed")
    if smoke.git_output(args.playground_root, "rev-parse", "HEAD") != smoke.CONTROL_COMMIT:
        raise ValueError("Winner-v24 training Playground source changed")
    smoke.validate_playground_tree(args.playground_root)
    scene = args.playground_root / smoke.SCENE_RELATIVE
    if smoke.sha256(scene) != smoke.SCENE_SHA256:
        raise ValueError("Winner-v24 training scene changed")

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
        raise ValueError("Winner-v24 training restore boundary changed")
    parameters = restored["parameters"]
    source_trainable = v21.joint_trainable_parameters(parameters)
    optimizer = restored["optimizer"]
    target_mean = jnp.asarray(restored["target_mean"], dtype=jnp.float32)
    target_std = jnp.asarray(restored["target_std"], dtype=jnp.float32)
    population = full.training_population(
        json.loads(FULL_PREREG.read_text(encoding="utf-8")),
        json.loads(DOMAIN.read_text(encoding="utf-8")),
    )
    if len(population) != 80:
        raise ValueError("Winner-v24 training population changed")
    design = json.loads(smoke.CALIBRATOR_PREREG.read_text(encoding="utf-8"))
    observer_type = smoke.load_runtime_observer(args.canonical_fit)
    metrics: list[dict[str, Any]] = []
    snapshots: list[dict[str, Any]] = []
    checkpoints: list[dict[str, Any]] = []
    sampled_total = valid_total = 0
    start = time.monotonic()
    args.work_root.mkdir(parents=True, exist_ok=False)
    (args.work_root / "snapshots").mkdir()
    (args.work_root / "graphs").mkdir()

    def ppo_objective(values_tree: Mapping[str, Any], data: Mapping[str, Any]):
        return v20.joint_recurrent_ppo_loss(
            values_tree, data,
            clip_epsilon=training.PPO_CLIP_EPSILON,
            value_coefficient=training.PPO_VALUE_COEFFICIENT,
            entropy_coefficient=training.PPO_ENTROPY_COEFFICIENT,
        )

    def predictor_objective(values_tree: Mapping[str, Any], data: Mapping[str, Any]):
        return v22.normalized_predictor_loss(values_tree, data, target_mean, target_std)

    ppo_grad = jax.value_and_grad(ppo_objective, has_aux=True)
    predictor_grad = jax.value_and_grad(predictor_objective, has_aux=True)
    for local_index in range(UPDATES):
        rollout_update_index = SOURCE_COMPLETED_UPDATES + local_index
        completed_updates = rollout_update_index + 1
        batch_np, episodes, observations = v20.stage2_rollout(
            smoke=smoke, full=full, training=training, mujoco=mujoco,
            scene=scene, population=population, preregistration=design,
            observer_type=observer_type, canonical_fit=args.canonical_fit,
            parameters=parameters, update_index=rollout_update_index,
        )
        full.validate_stage2_masks(batch_np, episodes)
        episode_hash = full.validate_episode_receipts(
            episodes, population, stage=2, update_index=rollout_update_index
        )
        boundary = full.stage2_action_boundary_evidence(batch_np)
        reward = v15.reward_evidence(batch_np)
        _, values = training.stage2_mean_value(
            parameters, jnp.asarray(batch_np["hidden"], dtype=jnp.float32)
        )
        objective_batch_np, objective_evidence = v24v3.apply_training_objective(
            batch_np, episodes, np.asarray(values, dtype=np.float32),
            gamma=training.PPO_GAMMA, gae_lambda=training.PPO_GAE_LAMBDA,
        )
        changed_keys = sorted(
            key for key in batch_np
            if not np.array_equal(np.asarray(batch_np[key]), objective_batch_np[key])
        )
        failure_mask = v24.roll_pitch_failure_mask(
            episodes, shape=np.asarray(batch_np["rewards"]).shape
        )
        if not (
            boundary["realized_equals_numpy_bit_exact"]
            and boundary["numpy_equals_jax_bit_exact"]
            and reward["reward_formula_bit_exact"]
            and (
                (
                    int(np.sum(failure_mask)) > 0
                    and changed_keys == list(v24v2.MODIFIED_BATCH_KEYS)
                    and objective_evidence["analytical_terminal_delta_nonzero_count"]
                    > int(np.sum(failure_mask))
                    and objective_evidence["zero_failure_bit_exact_noop"] is False
                )
                or (
                    int(np.sum(failure_mask)) == 0
                    and changed_keys == []
                    and objective_evidence["analytical_terminal_delta_nonzero_count"] == 0
                    and objective_evidence["zero_failure_bit_exact_noop"] is True
                )
            )
        ):
            raise ValueError(f"Winner-v24 transition changed at {completed_updates}")
        batch = {key: jnp.asarray(value) for key, value in objective_batch_np.items()}
        before = v21.joint_trainable_parameters(parameters)
        (ppo_loss, ppo_metrics), ppo_gradients = ppo_grad(before, batch)
        (predictor_loss, predictor_metrics), predictor_gradients = predictor_grad(
            before, batch
        )
        gradients = v22v2.compose_gradients(ppo_gradients, predictor_gradients)
        combined_loss = ppo_loss + jnp.asarray(v22v2.FROZEN_PREDICTOR_SCALE) * predictor_loss
        expected_stored = int(
            np.sum(
                batch_np["valid_transition_mask"][:, :-1]
                * batch_np["valid_mask"][:, 1:]
            )
        )
        if (
            float(ppo_metrics["sampled_hidden_replay_max_abs_error"]) > 1.0e-6
            or int(predictor_metrics["stored_successor_transition_count"])
            != expected_stored
            or expected_stored <= 0
        ):
            raise ValueError(f"Winner-v24 replay changed at {completed_updates}")
        after, optimizer = training.adam_step(
            before, gradients, optimizer,
            learning_rate=training.STAGE2_LEARNING_RATE,
            beta1=training.ADAM_BETA1, beta2=training.ADAM_BETA2,
            epsilon=training.ADAM_EPSILON,
        )
        after = training.clamp_stage2_parameters(after)
        full.validate_log_std(after)
        deltas = v20.leaf_max_abs_delta(before, after)
        gradient_max = common.tree_max_abs(gradients)
        if not all(value > 0.0 for value in gradient_max.values()) or not all(
            value > 0.0 for value in deltas.values()
        ):
            raise ValueError(f"Winner-v24 closed a leaf at {completed_updates}")
        parameters = v21.merge_joint_trainable(parameters, after)
        if (
            int(np.asarray(optimizer["count"])) != completed_updates
            or not training.finite_tree(
                {
                    "ppo_loss": ppo_loss, "ppo_metrics": ppo_metrics,
                    "predictor_loss": predictor_loss,
                    "predictor_metrics": predictor_metrics,
                    "combined_loss": combined_loss, "gradients": gradients,
                    "parameters": parameters, "optimizer": optimizer,
                }
            )
        ):
            raise FloatingPointError(f"Winner-v24 update {completed_updates} invalid")
        sampled = int(np.sum(batch_np["valid_mask"]))
        valid = int(np.sum(batch_np["valid_transition_mask"]))
        sampled_total += sampled
        valid_total += valid
        metrics.append(
            {
                "local_update": local_index + 1,
                "rollout_update_index": rollout_update_index,
                "completed_updates": completed_updates,
                "optimizer_count": int(np.asarray(optimizer["count"])),
                "episode_receipts_sha256": episode_hash,
                "sampled_count": sampled,
                "valid_transition_count": valid,
                "stored_successor_transition_count": expected_stored,
                "roll_pitch_failure_count": int(np.sum(failure_mask)),
                "settled_success_count": sum(
                    item.get("terminal_success_bonus_applied") is True
                    for item in episodes
                ),
                "ppo_loss": float(ppo_loss),
                "normalized_predictor_loss": float(predictor_loss),
                "combined_loss": float(combined_loss),
                "sampled_hidden_replay_max_abs_error": float(
                    ppo_metrics["sampled_hidden_replay_max_abs_error"]
                ),
                "combined_gradient_max_abs": gradient_max,
                "leaf_max_abs_delta": deltas,
                "objective_evidence": objective_evidence,
                "action_boundary_exact": True,
                "pitch_margin_reward_exact": True,
            }
        )
        snapshot_path = (
            args.work_root / "snapshots"
            / f"snapshot_baseline_anchored_update_{completed_updates:03d}.npz"
        )
        receipt = v22v2.save_snapshot(
            snapshot_path, parameters, optimizer,
            {
                "stage": "baseline_anchored_symmetric_failure_joint_stage2",
                "completed_updates": completed_updates,
                "source_completed_updates": SOURCE_COMPLETED_UPDATES,
                "source_snapshot_sha256": final_receipt["sha256"],
                "objective": preregistration["objective"],
                "root_seed": 120120,
                "learning_rate": float(training.STAGE2_LEARNING_RATE),
                "predictor_scale": float(v22v2.FROZEN_PREDICTOR_SCALE),
                "formal_support_cells": 0,
                "locomotion_steps": 0,
                "robot_or_rdk_access": 0,
            },
            restored["target_mean"], restored["target_std"],
        )
        loaded = v22v2.load_snapshot(snapshot_path)
        if not (
            common.tree_equal(parameters, loaded["parameters"])
            and np.array_equal(
                np.asarray(optimizer["count"]),
                np.asarray(loaded["optimizer"]["count"]),
            )
            and common.tree_equal(optimizer["m"], loaded["optimizer"]["m"])
            and common.tree_equal(optimizer["v"], loaded["optimizer"]["v"])
            and np.array_equal(restored["target_mean"], loaded["target_mean"])
            and np.array_equal(restored["target_std"], loaded["target_std"])
        ):
            raise ValueError(f"Winner-v24 snapshot changed at {completed_updates}")
        snapshots.append({"completed_updates": completed_updates, **receipt})
        if completed_updates in {HALF_COMPLETED_UPDATES, FINAL_COMPLETED_UPDATES}:
            label = "half" if completed_updates == HALF_COMPLETED_UPDATES else "final"
            graph = graph_receipt(
                smoke=smoke, networks=networks, training=training,
                parameters=parameters, observations=observations,
                path=args.work_root / "graphs" / f"winner_v24_{label}.onnx",
                label=label, completed_updates=completed_updates, common=common,
            )
            checkpoints.append(
                {
                    "label": label,
                    "completed_updates": completed_updates,
                    "snapshot": receipt,
                    "graph": graph,
                }
            )

    cumulative = v20.leaf_max_abs_delta(
        source_trainable, v21.joint_trainable_parameters(parameters)
    )
    checks = {
        "source_snapshot_and_optimizer_count_100_exact": True,
        "exact_100_continuation_updates": len(metrics) == 100
        and [row["completed_updates"] for row in metrics] == list(range(101, 201)),
        "all_100_episode_receipts_exact": all(
            bool(row["episode_receipts_sha256"]) for row in metrics
        ),
        "all_100_action_boundaries_exact": all(
            row["action_boundary_exact"] for row in metrics
        ),
        "all_100_pitch_margin_rewards_exact": all(
            row["pitch_margin_reward_exact"] for row in metrics
        ),
        "all_100_objective_failure_or_zero_failure_noop_contracts_exact": all(
            (
                row["roll_pitch_failure_count"] > 0
                and row["objective_evidence"]["analytical_terminal_delta_nonzero_count"]
                > row["roll_pitch_failure_count"]
                and row["objective_evidence"]["zero_failure_bit_exact_noop"] is False
            )
            or (
                row["roll_pitch_failure_count"] == 0
                and row["objective_evidence"]["analytical_terminal_delta_nonzero_count"] == 0
                and row["objective_evidence"]["zero_failure_bit_exact_noop"] is True
            )
            for row in metrics
        ),
        "all_100_hidden_replays_at_most_1e_6": all(
            row["sampled_hidden_replay_max_abs_error"] <= 1.0e-6
            for row in metrics
        ),
        "all_100_stored_successor_masks_nonempty": all(
            row["stored_successor_transition_count"] > 0 for row in metrics
        ),
        "all_100_updates_all_12_gradients_and_deltas_nonzero": all(
            all(value > 0.0 for value in row["combined_gradient_max_abs"].values())
            and all(value > 0.0 for value in row["leaf_max_abs_delta"].values())
            for row in metrics
        ),
        "all_12_leaves_changed_cumulatively": all(
            value > 0.0 for value in cumulative.values()
        ),
        "exact_100_atomic_snapshots": len(snapshots) == 100
        and [row["completed_updates"] for row in snapshots] == list(range(101, 201)),
        "optimizer_count_200_exact": int(np.asarray(optimizer["count"])) == 200,
        "half_and_final_graphs_present": [
            (row["label"], row["completed_updates"]) for row in checkpoints
        ]
        == [("half", 150), ("final", 200)],
        "all_updates_finite": True,
        "formal_support_cells_zero": True,
        "locomotion_steps_zero": True,
        "robot_or_rdk_access_zero": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    result = {
        "schema_version": "winner_v24.baseline_anchored_training_result.v1",
        "status": (
            "PASS_WINNER_V24_BASELINE_ANCHORED_TRAINING_ARTIFACT"
            if not failed else "HOLD_WINNER_V24_BASELINE_ANCHORED_TRAINING_ARTIFACT"
        ),
        "decision": (
            "AUTHORIZE_SEPARATE_BASELINE_ANCHORED_SUPPORT_GATE_PREREGISTRATION_ONLY"
            if not failed else "DO_NOT_EVALUATE_WINNER_V24_BASELINE_ANCHORED_POLICY"
        ),
        "checks": checks,
        "failed_checks": failed,
        "source_snapshot": {
            "sha256": final_receipt["sha256"], "bytes": final_receipt["bytes"],
            "completed_updates": 100, "optimizer_count": 100,
        },
        "objective": preregistration["objective"],
        "metrics": metrics,
        "snapshot_manifest": snapshots,
        "persistent_checkpoints": checkpoints,
        "cumulative_leaf_max_abs_delta": cumulative,
        "elapsed_seconds": time.monotonic() - start,
        "execution": {
            "optimizer_updates": 100,
            "scheduled_episode_slots": 2_000_000,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "environment": {
            "jax_backend": jax.default_backend(),
            "jax_devices": [str(device) for device in jax.devices()],
        },
        "sources": {
            "preregistration_lf_sha256": common.lf_sha256(PREREGISTRATION),
            "one_update_result_lf_sha256": common.lf_sha256(ONE_UPDATE_RESULT),
            "v22_training_lf_sha256": common.lf_sha256(V22_TRAINING),
            "runner_lf_sha256": common.lf_sha256(Path(__file__)),
        },
        "authority": {
            "robot_clearance": False,
            "training_executed": True,
            "formal_support_gate_executed": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "manual_mass_com_inertia_measurements_required": False,
            "pass_authorizes_only": (
                "a separate frozen baseline-anchored support gate preregistration"
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
