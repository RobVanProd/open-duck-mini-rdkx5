#!/usr/bin/env python3
"""Run the frozen zero-update CPU contract for the Winner-v12 full trainer."""

from __future__ import annotations

from collections import Counter
import copy
import json
import os
from pathlib import Path
import sys
from typing import Any, Mapping

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
PATCHES = ROOT / "patches"
TOOLS = ROOT / "tools"
sys.path.insert(0, str(PATCHES))
sys.path.insert(0, str(TOOLS))

import run_winner_v12_calibrator_cpu_smoke as smoke  # noqa: E402
import run_winner_v12_full_calibrator_training as runner  # noqa: E402
import winner_v12_calibrator_training as training  # noqa: E402


DEFAULT_CONTRACT = (
    ROOT / "outputs/analysis/winner_v12_full_calibrator_training_cpu_contract.json"
)
DEFAULT_OUTPUT = (
    ROOT
    / "outputs/analysis/winner_v12_full_calibrator_training_cpu_contract_result.json"
)


def validate_contract(contract: Mapping[str, Any]) -> None:
    if (
        contract.get("status")
        != "PASS_WINNER_V12_FULL_CALIBRATOR_TRAINING_CPU_CONTRACT_FROZEN"
    ):
        raise ValueError("full-training CPU contract is not frozen")
    if (
        contract.get("decision")
        != "AUTHORIZE_ONE_ZERO_UPDATE_FULL_TRAINING_CPU_CONTRACT_RUN_ONLY"
    ):
        raise ValueError("full-training CPU contract authority changed")
    if contract.get("failed_checks") != [] or not all(contract["checks"].values()):
        raise ValueError("full-training CPU contract has failed checks")
    for item in contract["sources"].values():
        path = ROOT / item["path"]
        observed = (
            smoke.lf_sha256(path) if item["hash_mode"] == "lf" else smoke.sha256(path)
        )
        if observed != item["sha256"]:
            raise ValueError(f"full-training CPU source hash changed: {item['path']}")


def zero_optimizer(parameters: Mapping[str, Any], count: int) -> dict[str, Any]:
    return {
        "count": np.asarray(count, dtype=np.int32),
        "m": {
            key: np.zeros_like(np.asarray(value)) for key, value in parameters.items()
        },
        "v": {
            key: np.zeros_like(np.asarray(value)) for key, value in parameters.items()
        },
    }


def synthetic_metrics(
    stage1_count: int,
    stage2_count: int,
    target_mean: np.ndarray,
    target_std: np.ndarray,
) -> list[dict[str, Any]]:
    rows = []
    for stage, count in (("stage1", stage1_count), ("stage2", stage2_count)):
        for update in range(1, count + 1):
            row = {
                "stage": stage,
                "update": update,
                "loss": 0.0,
                "sampled_count": 1,
                "valid_transition_count": 1,
                "episode_receipts_sha256": f"{update + (0 if stage == 'stage1' else 100):064x}",
                "completed_episodes": 0,
            }
            if stage == "stage1":
                row["frozen_target_mean_sha256"] = smoke.array_sha256(target_mean)
                row["frozen_target_std_sha256"] = smoke.array_sha256(target_std)
            else:
                row["action_boundary"] = {
                    "attempted_samples": 1,
                    "realized_equals_numpy_bit_exact": True,
                    "numpy_equals_jax_bit_exact": True,
                    "maximum_realized_numpy_error": 0.0,
                    "maximum_numpy_jax_error": 0.0,
                }
            rows.append(row)
    return rows


def refresh_snapshot_integrity(snapshot: dict[str, Any]) -> None:
    metadata = snapshot["metadata"]
    metadata["state_payload_sha256"] = runner.array_manifest_sha256(
        runner._numeric_state_arrays(
            snapshot["parameters"],
            snapshot["optimizer"],
            snapshot["target_mean"],
            snapshot["target_std"],
        )
    )
    metadata.pop("metadata_payload_sha256", None)
    metadata["metadata_payload_sha256"] = smoke.canonical_sha256(metadata)


def assert_raises(function, expected: type[BaseException]) -> bool:
    try:
        function()
    except expected:
        return True
    return False


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--canonical-fit", type=Path, required=True)
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    if args.work_root.exists():
        raise FileExistsError(
            f"CPU contract work root already exists: {args.work_root}"
        )
    if args.output.exists():
        raise FileExistsError(f"CPU contract result already exists: {args.output}")
    args.work_root.mkdir(parents=True)

    contract = json.loads(args.contract.read_text(encoding="utf-8"))
    validate_contract(contract)
    software = smoke.validate_software_versions(contract)
    preregistration = runner.load_preregistration()
    if smoke.sha256(args.canonical_fit) != smoke.P30_FIT_LF_SHA256:
        raise ValueError("canonical LF P30 fit hash changed")
    if (
        smoke.git_output(args.playground_root, "rev-parse", "HEAD")
        != smoke.CONTROL_COMMIT
    ):
        raise ValueError("Playground commit changed")
    playground = smoke.validate_playground_tree(args.playground_root)
    scene = args.playground_root / smoke.SCENE_RELATIVE
    if smoke.sha256(scene) != smoke.SCENE_SHA256:
        raise ValueError("Playground scene changed")

    import jax
    import jax.numpy as jnp
    import mujoco

    if jax.default_backend() != "cpu" or any(
        device.platform != "cpu" for device in jax.devices()
    ):
        raise ValueError("formal full-training contract requires CPU-only JAX")
    design = json.loads(smoke.CALIBRATOR_PREREG.read_text(encoding="utf-8"))
    domain = json.loads(runner.DOMAIN.read_text(encoding="utf-8"))
    population = runner.training_population(preregistration, domain)
    heldout = set(preregistration["population"]["heldout_configuration_ids"])
    observer_type = smoke.load_runtime_observer(args.canonical_fit)
    parameters = training.initialize_training_parameters(seed=runner.PARAMETER_SEED)
    initial_tree_hash = smoke.tree_sha256(parameters)
    if initial_tree_hash != preregistration["parameter_initialization"]["tree_sha256"]:
        raise ValueError("initial parameter tree hash changed")
    stage1_optimizer = training.adam_initialize(training.stage1_parameters(parameters))
    stage2_optimizer = training.adam_initialize(training.stage2_parameters(parameters))
    optimizer_calls = 0
    original_adam_step = training.adam_step

    def forbidden_adam_step(*_args, **_kwargs):
        nonlocal optimizer_calls
        optimizer_calls += 1
        raise AssertionError("CPU contract may not execute an optimizer update")

    training.adam_step = forbidden_adam_step
    try:
        stage1_batch, stage1_episodes, stage1_evidence = runner.stage1_rollout(
            mujoco,
            scene,
            population,
            design,
            observer_type,
            args.canonical_fit,
            0,
        )
        normalization = stage1_evidence.pop("normalization")
        stage1_receipt_hash = runner.validate_episode_receipts(
            stage1_episodes, population, stage=1, update_index=0
        )
        target_mean = np.asarray(normalization["mean"], dtype=np.float32)
        target_std = np.asarray(normalization["std"], dtype=np.float32)
        valid_targets = stage1_batch["targets"][
            stage1_batch["valid_mask"].astype(bool)
        ].astype(np.float64)
        recomputed_mean64 = np.mean(valid_targets, axis=0, dtype=np.float64)
        recomputed_empirical_std64 = np.std(
            valid_targets, axis=0, dtype=np.float64, ddof=0
        )
        recomputed_std64 = np.maximum(recomputed_empirical_std64, 1.0e-6)
        normalizer_recomputed_exact = (
            normalization["valid_rows"] == int(valid_targets.shape[0])
            and normalization["heldout_rows"] == 0
            and normalization["mean_float64_sha256"]
            == smoke.array_sha256(recomputed_mean64)
            and normalization["empirical_std_float64_sha256"]
            == smoke.array_sha256(recomputed_empirical_std64)
            and normalization["floored_std_float64_sha256"]
            == smoke.array_sha256(recomputed_std64)
            and np.array_equal(target_mean, recomputed_mean64.astype(np.float32))
            and np.array_equal(target_std, recomputed_std64.astype(np.float32))
        )
        stage1_loss, stage1_gradients = jax.value_and_grad(training.stage1_loss)(
            training.stage1_parameters(parameters),
            {key: jnp.asarray(value) for key, value in stage1_batch.items()},
            jnp.asarray(target_mean),
            jnp.asarray(target_std),
        )
        stage2_batch, stage2_episodes, observation_bank = runner.stage2_rollout(
            mujoco,
            scene,
            population,
            design,
            observer_type,
            args.canonical_fit,
            parameters,
            0,
        )
        stage2_receipt_hash = runner.validate_episode_receipts(
            stage2_episodes, population, stage=2, update_index=0
        )
        runner.validate_stage2_masks(stage2_batch, stage2_episodes)
        action_boundary = runner.stage2_action_boundary_evidence(stage2_batch)
        runner.validate_log_std(training.stage2_parameters(parameters))

        def objective(value):
            return training.stage2_ppo_loss(
                value,
                {key: jnp.asarray(item) for key, item in stage2_batch.items()},
                clip_epsilon=training.PPO_CLIP_EPSILON,
                value_coefficient=training.PPO_VALUE_COEFFICIENT,
                entropy_coefficient=training.PPO_ENTROPY_COEFFICIENT,
            )

        (stage2_loss, stage2_loss_metrics), stage2_gradients = jax.value_and_grad(
            objective, has_aux=True
        )(training.stage2_parameters(parameters))
    finally:
        training.adam_step = original_adam_step

    malformed_batch = {
        key: np.asarray(value).copy() for key, value in stage2_batch.items()
    }
    malformed_environment = next(
        index
        for index, row in enumerate(malformed_batch["valid_mask"])
        if int(np.sum(row)) >= 2
    )
    malformed_batch["valid_mask"][malformed_environment, 0] = np.float32(0.5)
    malformed_batch["valid_mask"][malformed_environment, 1] = np.float32(1.5)
    fractional_mask_rejected = assert_raises(
        lambda: runner.validate_stage2_masks(malformed_batch, stage2_episodes),
        ValueError,
    )
    malformed_action_batch = {
        key: np.asarray(value).copy() for key, value in stage2_batch.items()
    }
    first_active = tuple(np.argwhere(malformed_action_batch["valid_mask"] > 0)[0])
    malformed_action_batch["realized_actions"][first_active][0] += np.float32(0.125)
    malformed_action_evidence = runner.stage2_action_boundary_evidence(
        malformed_action_batch
    )

    stub_result = args.work_root / "cpu_contract_authority_stub.json"
    stub_result.write_text('{"contract_test_only":true}\n', encoding="utf-8")
    original_cpu_result = runner.CPU_RESULT
    runner.CPU_RESULT = stub_result
    persistence_root = args.work_root / "persistence"
    persistence_root.mkdir()
    try:
        synthetic_claim = {
            "logical_run_id": "winner-v12-full-calibrator-seed-120120",
            "resolved_work_root": str(persistence_root.resolve()),
            "repository_relative_claim_path": str(
                runner.PREREGISTRATION.relative_to(ROOT)
            ).replace("\\", "/"),
        }
        claim_receipt = runner.consume_or_validate_claim(
            synthetic_claim, persistence_root, fresh=True
        )
        claim_repeat_exact = (
            runner.consume_or_validate_claim(
                synthetic_claim, persistence_root, fresh=False
            )
            == claim_receipt
        )
        second_fresh_root_rejected = assert_raises(
            lambda: runner.claim_receipt_payload(
                synthetic_claim, args.work_root / "different-fresh-root"
            ),
            ValueError,
        )
        stage1_parameters = training.stage1_parameters(parameters)
        stage1_metrics = synthetic_metrics(100, 0, target_mean, target_std)
        runner.persist_update(
            persistence_root,
            stage="stage1",
            completed_updates=100,
            parameters=parameters,
            optimizer=zero_optimizer(stage1_parameters, 100),
            metrics=stage1_metrics,
            sampled_count=100,
            valid_count=100,
            target_mean=target_mean,
            target_std=target_std,
            frozen_stage1_tree_sha256=None,
        )
        stage1_final = runner.ensure_stage1_final_checkpoint(persistence_root)
        frozen_stage1_hash = smoke.tree_sha256(stage1_parameters)
        runner.persist_update(
            persistence_root,
            stage="stage2",
            completed_updates=0,
            parameters=parameters,
            optimizer=zero_optimizer(training.stage2_parameters(parameters), 0),
            metrics=stage1_metrics,
            sampled_count=100,
            valid_count=100,
            target_mean=target_mean,
            target_std=target_std,
            frozen_stage1_tree_sha256=frozen_stage1_hash,
        )
        stage2_zero = persistence_root / "snapshots/snapshot_stage2_update_000.npz"
        newest_transition = runner.newest_committed_snapshot(persistence_root)
        transition_order_exact = newest_transition.resolve() == stage2_zero.resolve()

        pending_paths = [
            persistence_root / "snapshots/snapshot_stage2_update_001.npz.pending.npz",
            persistence_root / "winner_v12_calibrator_half.onnx.pending.onnx",
            persistence_root / "winner_v12_calibrator_half_receipt.json.pending",
            persistence_root / f"{runner.SNAPSHOT_NAME}.pending",
        ]
        for index, path in enumerate(pending_paths):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(f"uncommitted-{index}".encode())
        recovery = runner.quarantine_uncommitted_pending(persistence_root)
        pending_recovery_exact = recovery is not None and len(recovery["entries"]) == 4
        if any(path.exists() for path in pending_paths):
            raise ValueError("uncommitted pending artifact survived quarantine")

        stage2_history = synthetic_metrics(100, 50, target_mean, target_std)
        runner.persist_update(
            persistence_root,
            stage="stage2",
            completed_updates=50,
            parameters=parameters,
            optimizer=zero_optimizer(training.stage2_parameters(parameters), 50),
            metrics=stage2_history,
            sampled_count=150,
            valid_count=150,
            target_mean=target_mean,
            target_std=target_std,
            frozen_stage1_tree_sha256=frozen_stage1_hash,
        )
        half = runner.ensure_persistent_artifact(persistence_root, "half", 50)
        newest = runner.newest_committed_snapshot(persistence_root)
        older_resume_rejected = newest.resolve() != stage2_zero.resolve()
        latest = persistence_root / runner.SNAPSHOT_NAME
        latest.write_bytes(b"stale-latest-pointer")
        runner.replace_latest_snapshot(newest, latest)
        stale_latest_repaired = smoke.sha256(latest) == smoke.sha256(newest)

        clean_snapshot = runner.load_snapshot(newest)
        numerically_tampered = copy.deepcopy(clean_snapshot)
        numerically_tampered["parameters"]["obs_weight"][0, 0] += np.float32(0.25)
        self_hash_rejects_tamper = assert_raises(
            lambda: runner.validate_resume(numerically_tampered), ValueError
        )
        lineage_tampered = copy.deepcopy(clean_snapshot)
        lineage_tampered["parameters"]["obs_weight"][0, 0] += np.float32(0.25)
        lineage_tampered["metadata"]["frozen_stage1_tree_sha256"] = smoke.tree_sha256(
            training.stage1_parameters(lineage_tampered["parameters"])
        )
        refresh_snapshot_integrity(lineage_tampered)
        runner.validate_resume(lineage_tampered)
        independent_lineage_rejects_tamper = assert_raises(
            lambda: runner.validate_stage2_lineage(lineage_tampered, persistence_root),
            ValueError,
        )
        normalization_tampered = copy.deepcopy(clean_snapshot)
        normalization_tampered["target_mean"][0] += np.float32(0.25)
        changed_mean_hash = smoke.array_sha256(normalization_tampered["target_mean"])
        for row in normalization_tampered["metadata"]["metrics"]:
            if row["stage"] == "stage1":
                row["frozen_target_mean_sha256"] = changed_mean_hash
        refresh_snapshot_integrity(normalization_tampered)
        runner.validate_resume(normalization_tampered)
        independent_normalizer_lineage_rejects_tamper = assert_raises(
            lambda: runner.validate_stage2_lineage(
                normalization_tampered, persistence_root
            ),
            ValueError,
        )
    finally:
        runner.CPU_RESULT = original_cpu_result

    stage1_valid = int(np.sum(stage1_batch["valid_mask"]))
    stage1_attempted = sum(
        int(row["episode"]["valid_ticks"]) + (1 if row["terminal"] else 0)
        for row in stage1_episodes
    )
    stage2_sampled = int(np.sum(stage2_batch["valid_mask"]))
    stage2_valid = int(np.sum(stage2_batch["valid_transition_mask"]))
    population_ids = [row["id"] for row in population]
    plants = Counter(row["plant"] for row in stage1_episodes)
    checks = {
        "software_versions_exact": software["exact"],
        "cpu_only_jax": jax.default_backend() == "cpu"
        and all(device.platform == "cpu" for device in jax.devices()),
        "playground_tree_exact": bool(playground),
        "initial_parameter_tree_exact": initial_tree_hash
        == "2b8cbc46517c1e6b073c7b93a9fe4c1b50e66e1ee7be514371bafd2b050e0127",
        "fresh_adam_counts_zero": int(np.asarray(stage1_optimizer["count"])) == 0
        and int(np.asarray(stage2_optimizer["count"])) == 0,
        "full_population_exact": len(population) == 80
        and population_ids[::2]
        == preregistration["population"]["training_configuration_ids"]
        and population_ids[1::2]
        == preregistration["population"]["training_configuration_ids"],
        "heldout_excluded": not heldout.intersection(population_ids),
        "plants_balanced": plants
        == Counter({smoke.PLANTS[0]: 40, smoke.PLANTS[1]: 40}),
        "stage1_receipts_exact": len(stage1_receipt_hash) == 64,
        "stage2_receipts_exact": len(stage2_receipt_hash) == 64,
        "stage1_fixed_p30_slot_exact": bool(
            stage1_evidence["fixed_p30_observer_slot_exact"]
        ),
        "stage1_action_chain_exact": bool(
            stage1_evidence["realized_action_chain_exact"]
        ),
        "stage1_normalizer_independently_recomputed_exact": normalizer_recomputed_exact,
        "stage1_full_shape": stage1_batch["valid_mask"].shape == (80, 250),
        "stage2_full_shape": stage2_batch["valid_mask"].shape == (80, 250),
        "sample_accounting_valid": 0 < stage1_valid <= stage1_attempted <= 20_000
        and 0 < stage2_valid <= stage2_sampled <= 20_000,
        "stage1_objective_and_gradients_finite": training.finite_tree(
            {"loss": stage1_loss, "gradients": stage1_gradients}
        ),
        "stage2_objective_and_gradients_finite": training.finite_tree(
            {
                "loss": stage2_loss,
                "metrics": stage2_loss_metrics,
                "gradients": stage2_gradients,
            }
        ),
        "optimizer_updates_zero": optimizer_calls == 0,
        "stage2_terminal_masks_exact": True,
        "fractional_terminal_mask_rejected": fractional_mask_rejected,
        "full_rollout_action_boundary_exact": action_boundary["attempted_samples"]
        == stage2_sampled
        and action_boundary["realized_equals_numpy_bit_exact"]
        and action_boundary["numpy_equals_jax_bit_exact"]
        and action_boundary["maximum_realized_numpy_error"] == 0.0
        and action_boundary["maximum_numpy_jax_error"] == 0.0,
        "malformed_realized_action_rejected": not malformed_action_evidence[
            "realized_equals_numpy_bit_exact"
        ],
        "observation_bank_nonzero_finite": observation_bank.shape == (250, 115)
        and np.count_nonzero(observation_bank) > 0
        and np.all(np.isfinite(observation_bank)),
        "snapshot_transition_order_exact": transition_order_exact,
        "pending_recovery_exact": pending_recovery_exact,
        "logical_run_claim_repeat_exact": claim_repeat_exact,
        "second_fresh_root_claim_rejected": second_fresh_root_rejected,
        "older_resume_rejected": older_resume_rejected,
        "stale_latest_repaired": stale_latest_repaired,
        "snapshot_self_hash_rejects_tamper": self_hash_rejects_tamper,
        "independent_stage1_lineage_rejects_tamper": independent_lineage_rejects_tamper,
        "independent_normalizer_lineage_rejects_tamper": independent_normalizer_lineage_rejects_tamper,
        "stage1_final_checkpoint_exact": bool(stage1_final),
        "nonzero_onnx_chain_passes": half["onnx_observation_bank"]["nonzero_values"] > 0
        and half["graph"]["jax_onnx_at_most_1e_7"]
        and half["graph"]["previous_action_out_equals_action_bit_exact"],
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    result = {
        "schema_version": "winner_v12.full_calibrator_training_cpu_contract_result.v1",
        "status": (
            "PASS_WINNER_V12_FULL_CALIBRATOR_TRAINING_CPU_CONTRACT"
            if not failed
            else "HOLD_WINNER_V12_FULL_CALIBRATOR_TRAINING_CPU_CONTRACT"
        ),
        "decision": (
            "AUTHORIZE_ONE_WINNER_V12_FULL_CALIBRATOR_TRAINING_RUN_ONLY"
            if not failed
            else "DO_NOT_RUN_FULL_CALIBRATOR_TRAINING"
        ),
        "contract_lf_sha256": smoke.lf_sha256(args.contract),
        "environment": {
            "software_versions": software,
            "jax_devices": [str(device) for device in jax.devices()],
        },
        "execution": {
            "optimizer_updates": optimizer_calls,
            "formal_support_cells": 0,
            "locomotion_training_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "rollouts": {
            "stage1": {
                "environments": 80,
                "scheduled_tick_slots": 20_000,
                "attempted_transition_samples": stage1_attempted,
                "valid_transitions": stage1_valid,
                "receipt_sha256": stage1_receipt_hash,
            },
            "stage2": {
                "environments": 80,
                "scheduled_tick_slots": 20_000,
                "attempted_transition_samples": stage2_sampled,
                "valid_transitions": stage2_valid,
                "receipt_sha256": stage2_receipt_hash,
            },
        },
        "persistence_contract": {
            "stage1_final": stage1_final,
            "half": half,
            "recovery": recovery,
            "newest_snapshot": {
                "path": str(newest),
                "sha256": smoke.sha256(newest),
            },
        },
        "checks": checks,
        "failed_checks": failed,
        "authority": {
            "full_calibrator_training_executed": False,
            "formal_support_gate_executed": False,
            "locomotion_training_or_behavior_executed": False,
            "robot_clearance": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "pass_authorizes_only": "one frozen seed-120120 full calibrator training run",
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    pending_output = args.output.with_name(args.output.name + ".pending")
    if pending_output.exists():
        raise FileExistsError(pending_output)
    pending_output.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    pending_output.replace(args.output)
    print(
        json.dumps(
            {
                "status": result["status"],
                "result_sha256": smoke.sha256(args.output),
                "failed_checks": failed,
            },
            sort_keys=True,
        )
    )
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
