#!/usr/bin/env python3
"""Train only the Winner-v13 support controller from the frozen Stage-1 snapshot."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
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

PREREGISTRATION = ANALYSIS / "winner_v13_support_controller_training_preregistration.json"
CPU_RESULT = ANALYSIS / "winner_v13_support_controller_cpu_result.json"
STAGE1_RESULT = ANALYSIS / "winner_v13_normalized_response_stage1_v2_result.json"
FULL_PREREG = ANALYSIS / "winner_v12_full_calibrator_training_preregistration.json"
DOMAIN = ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
STAGE1_SNAPSHOT_SHA256 = "8c1392c738eddfb098e61c1a6ae2f863eda883e1eba6ac546aef695da6f163af"
STAGE1_SNAPSHOT_BYTES = 189027
UPDATES = 100
PERSISTENT = {50: "half", 100: "final"}


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


def validate_source_manifest(preregistration: Mapping[str, Any]) -> None:
    sources = preregistration.get("sources")
    if not isinstance(sources, dict) or not sources:
        raise ValueError("Winner-v13 support training source manifest is absent")
    for name, item in sources.items():
        path = ROOT / item["path"]
        if (
            set(item) != {"hash_mode", "path", "sha256"}
            or item["hash_mode"] != "lf"
            or lf_sha256(path) != item["sha256"]
        ):
            raise ValueError(f"Winner-v13 support training source changed: {name}")
    if canonical_sha256(sources) != preregistration.get("source_manifest_sha256"):
        raise ValueError("Winner-v13 support training source-manifest digest changed")


def validate_preregistration(value: Mapping[str, Any]) -> None:
    if (
        value.get("schema_version")
        != "winner_v13.support_controller_training_preregistration.v1"
        or value.get("status")
        != "PREREGISTERED_WINNER_V13_SUPPORT_CONTROLLER_TRAINING"
        or value.get("decision")
        != "AUTHORIZE_ONE_100_UPDATE_SUPPORT_CONTROLLER_RUN_ONLY"
        or value.get("execution_now")
        != {
            "stage2_optimizer_updates": 0,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        }
    ):
        raise ValueError("Winner-v13 support training preregistration changed")
    frozen = value.get("frozen_training", {})
    if frozen != {
        "source_stage1_snapshot_sha256": STAGE1_SNAPSHOT_SHA256,
        "source_stage1_snapshot_bytes": STAGE1_SNAPSHOT_BYTES,
        "optimizer_updates": 100,
        "environments_per_update": 80,
        "ticks_per_environment": 250,
        "scheduled_episode_slots": 2_000_000,
        "training_root_seed": 120120,
        "learning_rate": 0.0001,
        "trainable_leaves": [
            "action_bias",
            "action_weight",
            "training_only_log_std",
            "training_only_value_bias",
            "training_only_value_weight",
        ],
        "frozen_leaves": [
            "obs_weight",
            "previous_action_weight",
            "hidden_weight",
            "hidden_bias",
            "auxiliary_hidden_weight",
            "auxiliary_action_weight",
            "auxiliary_bias",
        ],
        "persistent_snapshots": "atomic readback-verified snapshot after every update",
        "persistent_checkpoints": {"half": 50, "final": 100},
    }:
        raise ValueError("Winner-v13 support training constants changed")
    validate_source_manifest(value)


def graph_receipt(
    smoke: Any,
    networks: Any,
    training: Any,
    parameters: Mapping[str, Any],
    observations: np.ndarray,
    work_root: Path,
    label: str,
    update: int,
) -> dict[str, Any]:
    graph = work_root / "graphs" / f"winner_v13_support_controller_{label}.onnx"
    graph.parent.mkdir(parents=True, exist_ok=True)
    networks.export_calibrator_onnx(training.deployable_parameters(parameters), graph)
    contract = smoke.onnx_contract(graph, parameters, observations)
    required = (
        "abi_exact",
        "all_initializers_finite",
        "all_chain_outputs_finite",
        "training_only_tensors_absent",
        "jax_onnx_at_most_1e_7",
        "previous_action_out_equals_action_bit_exact",
    )
    if not all(contract[name] for name in required):
        raise ValueError(f"Winner-v13 support {label} ONNX contract failed")
    return {"label": label, "update": update, "graph": contract}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--canonical-fit", type=Path, required=True)
    parser.add_argument("--stage1-final-snapshot", type=Path, required=True)
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--offline-cpu-only", action="store_true")
    parser.add_argument("--support-controller-training-authorized", action="store_true")
    args = parser.parse_args()
    if not args.offline_cpu_only or not args.support_controller_training_authorized:
        raise PermissionError(
            "support training requires --offline-cpu-only "
            "--support-controller-training-authorized"
        )
    if args.work_root.exists() or args.output.exists():
        raise FileExistsError("refusing to overwrite support-controller evidence")

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
        raise ValueError("Winner-v13 support training requires CPU-only JAX")
    preregistration = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    validate_preregistration(preregistration)
    cpu_result = json.loads(CPU_RESULT.read_text(encoding="utf-8"))
    if (
        cpu_result.get("status")
        != "PASS_WINNER_V13_SUPPORT_CONTROLLER_CPU_CONTRACT"
        or cpu_result.get("decision")
        != "AUTHORIZE_SUPPORT_CONTROLLER_TRAINING_PREREGISTRATION_ONLY"
        or cpu_result.get("failed_checks") != []
        or cpu_result.get("execution", {}).get("stage2_optimizer_updates") != 1
    ):
        raise ValueError("Winner-v13 support CPU result changed")
    stage1_result = json.loads(STAGE1_RESULT.read_text(encoding="utf-8"))
    if (
        stage1_result.get("status")
        != "PASS_WINNER_V13_NORMALIZED_RESPONSE_STAGE1"
        or stage1_result.get("failed_checks") != []
    ):
        raise ValueError("Winner-v13 Stage-1 result changed")
    if (
        sha256(args.stage1_final_snapshot) != STAGE1_SNAPSHOT_SHA256
        or args.stage1_final_snapshot.stat().st_size != STAGE1_SNAPSHOT_BYTES
    ):
        raise ValueError("Winner-v13 Stage-1 source snapshot changed")
    restored = full.load_snapshot(args.stage1_final_snapshot)
    source_metadata = restored["metadata"]
    if (
        source_metadata.get("schema_version")
        != "winner_v13.normalized_response_stage1_snapshot.v1"
        or source_metadata.get("stage") != "stage1"
        or source_metadata.get("completed_updates") != 100
        or int(np.asarray(restored["optimizer"]["count"])) != 100
        or source_metadata.get("robot_or_rdk_access") != 0
    ):
        raise ValueError("Winner-v13 Stage-1 source metadata changed")

    expected_versions = dict(
        json.loads(FULL_PREREG.read_text(encoding="utf-8"))[
            "implementation_contract_environment"
        ]
    )
    if expected_versions.pop("platform") != "CPU only":
        raise ValueError("Winner-v13 support platform changed")
    software = smoke.validate_software_versions(
        {"software_versions": expected_versions}
    )
    if not software["exact"]:
        raise ValueError("Winner-v13 support software versions changed")
    if smoke.sha256(args.canonical_fit) != smoke.P30_FIT_LF_SHA256:
        raise ValueError("canonical P30 fit changed")
    if smoke.git_output(args.playground_root, "rev-parse", "HEAD") != smoke.CONTROL_COMMIT:
        raise ValueError("Playground source commit changed")
    smoke.validate_playground_tree(args.playground_root)
    scene = args.playground_root / smoke.SCENE_RELATIVE
    if smoke.sha256(scene) != smoke.SCENE_SHA256:
        raise ValueError("Winner-v13 support scene changed")

    full_prereg = json.loads(FULL_PREREG.read_text(encoding="utf-8"))
    domain = json.loads(DOMAIN.read_text(encoding="utf-8"))
    design = json.loads(smoke.CALIBRATOR_PREREG.read_text(encoding="utf-8"))
    population = full.training_population(full_prereg, domain)
    if len(population) != 80:
        raise ValueError("Winner-v13 support population changed")
    observer_type = smoke.load_runtime_observer(args.canonical_fit)
    parameters = restored["parameters"]
    source_stage1 = training.stage1_parameters(parameters)
    frozen_stage1_hash = smoke.tree_sha256(source_stage1)
    initial_stage2 = training.stage2_parameters(parameters)
    optimizer = training.adam_initialize(initial_stage2)
    target_mean = restored["target_mean"]
    target_std = restored["target_std"]
    metrics: list[dict[str, Any]] = []
    snapshots: list[dict[str, Any]] = []
    checkpoints: list[dict[str, Any]] = []
    sampled_count = 0
    valid_count = 0
    start = time.monotonic()

    def objective(values: Mapping[str, Any], batch: Mapping[str, Any]):
        return training.stage2_ppo_loss(
            values,
            batch,
            clip_epsilon=training.PPO_CLIP_EPSILON,
            value_coefficient=training.PPO_VALUE_COEFFICIENT,
            entropy_coefficient=training.PPO_ENTROPY_COEFFICIENT,
        )

    objective_grad = jax.value_and_grad(objective, has_aux=True)
    args.work_root.mkdir(parents=True, exist_ok=False)
    for update_index in range(UPDATES):
        batch_np, episodes, observations = full.stage2_rollout(
            mujoco,
            scene,
            population,
            design,
            observer_type,
            args.canonical_fit,
            parameters,
            update_index,
        )
        episode_hash = full.validate_episode_receipts(
            episodes, population, stage=2, update_index=update_index
        )
        full.validate_stage2_masks(batch_np, episodes)
        boundary = full.stage2_action_boundary_evidence(batch_np)
        if not (
            boundary["realized_equals_numpy_bit_exact"]
            and boundary["numpy_equals_jax_bit_exact"]
        ):
            raise ValueError(f"support action boundary changed at {update_index + 1}")
        if not training.finite_tree({"batch": batch_np, "observations": observations}):
            raise FloatingPointError(f"nonfinite support rollout {update_index + 1}")
        batch = {key: jnp.asarray(value) for key, value in batch_np.items()}
        stage2_before = training.stage2_parameters(parameters)
        (loss, loss_metrics), gradients = objective_grad(stage2_before, batch)
        stage2_after, optimizer = training.adam_step(
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
        parameters = training.merge_stage2(parameters, stage2_after)
        if not tree_equal(source_stage1, training.stage1_parameters(parameters)):
            raise ValueError(f"Stage-2 changed frozen Stage-1 at {update_index + 1}")
        if not training.finite_tree(
            {
                "loss": loss,
                "loss_metrics": loss_metrics,
                "gradients": gradients,
                "parameters": parameters,
                "optimizer": optimizer,
            }
        ):
            raise FloatingPointError(f"nonfinite support update {update_index + 1}")
        sampled = int(np.sum(batch_np["valid_mask"]))
        valid = int(np.sum(batch_np["valid_transition_mask"]))
        if sampled < valid or valid <= 0:
            raise ValueError(f"invalid support sample count at {update_index + 1}")
        sampled_count += sampled
        valid_count += valid
        gradient_max = {
            key: float(np.max(np.abs(np.asarray(value))))
            for key, value in gradients.items()
        }
        metrics.append(
            {
                "update": update_index + 1,
                "loss": float(loss),
                "sampled_count": sampled,
                "valid_transition_count": valid,
                "completed_episodes": sum(
                    row["episode"]["valid_ticks"] == 250 for row in episodes
                ),
                "episode_receipts_sha256": episode_hash,
                "gradient_max_abs": gradient_max,
                "action_boundary": boundary,
                **{key: float(value) for key, value in loss_metrics.items()},
            }
        )
        metadata = {
            "schema_version": "winner_v13.support_controller_training_snapshot.v1",
            "stage": "stage2",
            "completed_updates": update_index + 1,
            "root_seed": 120120,
            "learning_rate": float(training.STAGE2_LEARNING_RATE),
            "source_stage1_snapshot_sha256": STAGE1_SNAPSHOT_SHA256,
            "preregistration_lf_sha256": lf_sha256(PREREGISTRATION),
            "runner_lf_sha256": lf_sha256(Path(__file__)),
            "frozen_stage1_tree_sha256": frozen_stage1_hash,
            "metrics": metrics,
            "cumulative_sampled_count": sampled_count,
            "cumulative_valid_transition_count": valid_count,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        }
        snapshot_path = (
            args.work_root
            / "snapshots"
            / f"snapshot_stage2_update_{update_index + 1:03d}.npz"
        )
        receipt = full.save_snapshot(
            snapshot_path,
            parameters,
            optimizer,
            metadata,
            target_mean,
            target_std,
        )
        loaded = full.load_snapshot(snapshot_path)
        if not (
            tree_equal(parameters, loaded["parameters"])
            and tree_equal(optimizer["m"], loaded["optimizer"]["m"])
            and tree_equal(optimizer["v"], loaded["optimizer"]["v"])
            and np.array_equal(optimizer["count"], loaded["optimizer"]["count"])
            and loaded["metadata"]["completed_updates"] == update_index + 1
        ):
            raise ValueError(f"support snapshot readback failed at {update_index + 1}")
        snapshots.append(receipt)
        if update_index + 1 in PERSISTENT:
            checkpoints.append(
                graph_receipt(
                    smoke,
                    networks,
                    training,
                    parameters,
                    observations,
                    args.work_root,
                    PERSISTENT[update_index + 1],
                    update_index + 1,
                )
            )

    final_stage2 = training.stage2_parameters(parameters)
    deltas = training.leaf_max_abs_delta(initial_stage2, final_stage2)
    checks = {
        "exact_100_stage2_updates": len(metrics) == 100
        and int(np.asarray(optimizer["count"])) == 100,
        "exact_100_atomic_snapshots": len(snapshots) == 100,
        "half_and_final_graphs_present": [row["label"] for row in checkpoints]
        == ["half", "final"],
        "stage1_tree_bit_exact_frozen": tree_equal(
            source_stage1, training.stage1_parameters(parameters)
        ),
        "all_stage2_leaves_changed": all(value > 0.0 for value in deltas.values()),
        "all_updates_finite": training.finite_tree(
            {"parameters": parameters, "optimizer": optimizer}
        )
        and all(
            math.isfinite(float(row[name]))
            for row in metrics
            for name in (
                "loss",
                "entropy",
                "policy_loss",
                "ratio_max",
                "ratio_min",
                "value_loss",
            )
        )
        and all(
            math.isfinite(float(value))
            for row in metrics
            for value in row["gradient_max_abs"].values()
        ),
        "all_action_boundaries_exact": all(
            row["action_boundary"]["realized_equals_numpy_bit_exact"]
            and row["action_boundary"]["numpy_equals_jax_bit_exact"]
            for row in metrics
        ),
        "formal_support_cells_zero": True,
        "locomotion_steps_zero": True,
        "robot_or_rdk_access_zero": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    result = {
        "schema_version": "winner_v13.support_controller_training_result.v1",
        "status": (
            "PASS_WINNER_V13_SUPPORT_CONTROLLER_TRAINING_ARTIFACT"
            if not failed
            else "HOLD_WINNER_V13_SUPPORT_CONTROLLER_TRAINING_ARTIFACT"
        ),
        "decision": (
            "AUTHORIZE_SEPARATE_124_CELL_SUPPORT_GATE_PREREGISTRATION_ONLY"
            if not failed
            else "DO_NOT_EVALUATE_SUPPORT_CONTROLLER"
        ),
        "checks": checks,
        "failed_checks": failed,
        "environment": {
            "software_versions": software,
            "jax_devices": [str(device) for device in jax.devices()],
        },
        "source_stage1_snapshot": {
            "sha256": STAGE1_SNAPSHOT_SHA256,
            "bytes": STAGE1_SNAPSHOT_BYTES,
            "frozen_stage1_tree_sha256": frozen_stage1_hash,
        },
        "execution": {
            "stage2_optimizer_updates": 100,
            "scheduled_episode_slots": 2_000_000,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "population": {
            "environments_per_update": len(population),
            "cumulative_sampled_count": sampled_count,
            "cumulative_valid_transition_count": valid_count,
        },
        "metrics": metrics,
        "stage2_leaf_max_abs_delta": deltas,
        "snapshot_manifest": snapshots,
        "persistent_checkpoints": checkpoints,
        "elapsed_seconds": time.monotonic() - start,
        "sources": {
            "preregistration_lf_sha256": lf_sha256(PREREGISTRATION),
            "cpu_result_lf_sha256": lf_sha256(CPU_RESULT),
            "stage1_result_lf_sha256": lf_sha256(STAGE1_RESULT),
            "runner_lf_sha256": lf_sha256(Path(__file__)),
        },
        "authority": {
            "formal_support_gate_executed": False,
            "locomotion_executed": False,
            "robot_clearance": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "pass_authorizes_only": "a separately frozen 124-cell support/context gate",
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
