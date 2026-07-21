#!/usr/bin/env python3
"""Run one restored-snapshot Winner-v13 support-controller CPU update."""

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

CONTRACT = ANALYSIS / "winner_v13_support_controller_cpu_contract.json"
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
        raise ValueError("Winner-v13 support CPU source manifest is absent")
    for name, item in sources.items():
        path = ROOT / item["path"]
        if (
            set(item) != {"hash_mode", "path", "sha256"}
            or item["hash_mode"] != "lf"
            or lf_sha256(path) != item["sha256"]
        ):
            raise ValueError(f"Winner-v13 support CPU source changed: {name}")
    if canonical_sha256(sources) != contract.get("source_manifest_sha256"):
        raise ValueError("Winner-v13 support CPU source-manifest digest changed")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--canonical-fit", type=Path, required=True)
    parser.add_argument("--stage1-final-snapshot", type=Path, required=True)
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--offline-cpu-only", action="store_true")
    parser.add_argument("--one-update-support-contract-authorized", action="store_true")
    args = parser.parse_args()
    if not args.offline_cpu_only or not args.one_update_support_contract_authorized:
        raise PermissionError(
            "support CPU contract requires --offline-cpu-only "
            "--one-update-support-contract-authorized"
        )
    if args.work_root.exists() or args.output.exists():
        raise FileExistsError("refusing to overwrite support CPU evidence")

    import jax
    import jax.numpy as jnp
    import mujoco
    import run_winner_v12_calibrator_cpu_smoke as smoke
    import run_winner_v12_full_calibrator_training as full
    import winner_v12_calibrator_training as training
    import winner_v12_decomposed_backend_networks as networks

    if jax.default_backend() != "cpu" or any(
        device.platform != "cpu" for device in jax.devices()
    ):
        raise ValueError("Winner-v13 support CPU contract requires CPU-only JAX")
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    if (
        contract.get("status") != "FROZEN_WINNER_V13_SUPPORT_CONTROLLER_CPU_CONTRACT"
        or contract.get("decision") != "AUTHORIZE_ONE_RESTORED_STAGE2_UPDATE_ONLY"
        or contract.get("execution_now")
        != {
            "stage2_optimizer_updates": 0,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        }
    ):
        raise ValueError("Winner-v13 support CPU contract changed")
    validate_source_manifest(contract)
    stage1_result = json.loads(STAGE1_RESULT.read_text(encoding="utf-8"))
    if (
        stage1_result.get("status")
        != "PASS_WINNER_V13_NORMALIZED_RESPONSE_STAGE1"
        or stage1_result.get("decision")
        != "AUTHORIZE_SUPPORT_CONTROLLER_PREREGISTRATION_ONLY"
        or stage1_result.get("failed_checks") != []
        or stage1_result.get("execution", {}).get("stage2_optimizer_updates") != 0
        or stage1_result.get("snapshot_manifest", [{}])[-1].get("sha256")
        != SNAPSHOT_SHA256
    ):
        raise ValueError("Winner-v13 Stage-1 result changed")
    if (
        sha256(args.stage1_final_snapshot) != SNAPSHOT_SHA256
        or args.stage1_final_snapshot.stat().st_size != SNAPSHOT_BYTES
    ):
        raise ValueError("Winner-v13 Stage-1 final snapshot bytes changed")
    restored = full.load_snapshot(args.stage1_final_snapshot)
    metadata = restored["metadata"]
    if (
        metadata.get("schema_version")
        != "winner_v13.normalized_response_stage1_snapshot.v1"
        or metadata.get("stage") != "stage1"
        or metadata.get("completed_updates") != 100
        or int(np.asarray(restored["optimizer"]["count"])) != 100
        or metadata.get("full_training_updates") != 0
        or metadata.get("robot_or_rdk_access") != 0
    ):
        raise ValueError("Winner-v13 Stage-1 snapshot metadata changed")

    full_prereg = json.loads(FULL_PREREG.read_text(encoding="utf-8"))
    domain = json.loads(DOMAIN.read_text(encoding="utf-8"))
    design = json.loads(smoke.CALIBRATOR_PREREG.read_text(encoding="utf-8"))
    population = full.training_population(full_prereg, domain)
    observer_type = smoke.load_runtime_observer(args.canonical_fit)
    scene = (
        args.playground_root
        / "playground/open_duck_mini_v2/xmls/scene_flat_terrain_backlash.xml"
    )
    if not scene.is_file():
        raise FileNotFoundError(scene)
    parameters = restored["parameters"]
    stage1_before = training.stage1_parameters(parameters)
    stage2_before = training.stage2_parameters(parameters)
    optimizer = training.adam_initialize(stage2_before)
    batch_np, episodes, observations = full.stage2_rollout(
        mujoco,
        scene,
        population,
        design,
        observer_type,
        args.canonical_fit,
        parameters,
        0,
    )
    episode_hash = full.validate_episode_receipts(
        episodes, population, stage=2, update_index=0
    )
    full.validate_stage2_masks(batch_np, episodes)
    action_boundary = full.stage2_action_boundary_evidence(batch_np)
    if not (
        action_boundary["realized_equals_numpy_bit_exact"]
        and action_boundary["numpy_equals_jax_bit_exact"]
    ):
        raise ValueError("Winner-v13 support action boundary changed")
    batch = {key: jnp.asarray(value) for key, value in batch_np.items()}

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
    graph = args.work_root / "winner_v13_support_controller_one_update.onnx"
    networks.export_calibrator_onnx(training.deployable_parameters(parameters_after), graph)
    graph_contract = smoke.onnx_contract(graph, parameters_after, observations)
    snapshot = args.work_root / "winner_v13_support_controller_update_001.npz"
    snapshot_receipt = full.save_snapshot(
        snapshot,
        parameters_after,
        optimizer_after,
        {
            "schema_version": "winner_v13.support_controller_cpu_snapshot.v1",
            "stage": "stage2",
            "completed_updates": 1,
            "source_stage1_snapshot_sha256": SNAPSHOT_SHA256,
            "metrics": [],
            "cumulative_sampled_count": int(np.sum(batch_np["valid_mask"])),
            "cumulative_valid_transition_count": int(
                np.sum(batch_np["valid_transition_mask"])
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
        "source_stage1_result_passed": True,
        "source_snapshot_hash_and_bytes_exact": True,
        "source_snapshot_stage1_update_100_exact": True,
        "exact_80_episode_population": len(episodes) == 80,
        "valid_transition_count_nonzero": int(
            np.sum(batch_np["valid_transition_mask"])
        )
        > 0,
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
        "schema_version": "winner_v13.support_controller_cpu_result.v1",
        "status": (
            "PASS_WINNER_V13_SUPPORT_CONTROLLER_CPU_CONTRACT"
            if not failed
            else "HOLD_WINNER_V13_SUPPORT_CONTROLLER_CPU_CONTRACT"
        ),
        "decision": (
            "AUTHORIZE_SUPPORT_CONTROLLER_TRAINING_PREREGISTRATION_ONLY"
            if not failed
            else "DO_NOT_TRAIN_SUPPORT_CONTROLLER"
        ),
        "checks": checks,
        "failed_checks": failed,
        "proof": {
            "source_snapshot_sha256": SNAPSHOT_SHA256,
            "source_snapshot_bytes": SNAPSHOT_BYTES,
            "episode_receipts_sha256": episode_hash,
            "sampled_count": int(np.sum(batch_np["valid_mask"])),
            "valid_transition_count": int(
                np.sum(batch_np["valid_transition_mask"])
            ),
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
            "stage1_result_lf_sha256": lf_sha256(STAGE1_RESULT),
            "runner_lf_sha256": lf_sha256(Path(__file__)),
        },
        "authority": {
            "robot_clearance": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "pass_authorizes_only": "a separate support-controller training preregistration",
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
