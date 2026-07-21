#!/usr/bin/env python3
"""Run the one preregistered Winner-v20 joint recurrent training arm."""

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

PREREGISTRATION = (
    ANALYSIS / "winner_v20_joint_recurrent_support_training_preregistration.json"
)
CPU_RESULT = ANALYSIS / "winner_v20_joint_recurrent_support_cpu_v2_result.json"
STAGE1_RESULT = ANALYSIS / "winner_v13_normalized_response_stage1_v2_result.json"
FULL_PREREG = ANALYSIS / "winner_v12_full_calibrator_training_preregistration.json"
DOMAIN = ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
STAGE1_SNAPSHOT_SHA256 = (
    "8c1392c738eddfb098e61c1a6ae2f863eda883e1eba6ac546aef695da6f163af"
)
STAGE1_SNAPSHOT_BYTES = 189027
UPDATES = 100
HALF_UPDATE = 50


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


def validate_source_manifest(value: Mapping[str, Any]) -> None:
    sources = value.get("sources")
    if not isinstance(sources, dict) or not sources:
        raise ValueError("Winner-v20 training source manifest is absent")
    for name, item in sources.items():
        path = ROOT / item["path"]
        if (
            set(item) != {"hash_mode", "path", "sha256"}
            or item["hash_mode"] != "lf"
            or lf_sha256(path) != item["sha256"]
        ):
            raise ValueError(f"Winner-v20 training source changed: {name}")
    if canonical_sha256(sources) != value.get("source_manifest_sha256"):
        raise ValueError("Winner-v20 training source-manifest digest changed")


def validate_preregistration(value: Mapping[str, Any]) -> None:
    if (
        value.get("schema_version")
        != "winner_v20.joint_recurrent_support_training_preregistration.v1"
        or value.get("status")
        != "PREREGISTERED_WINNER_V20_JOINT_RECURRENT_SUPPORT_TRAINING"
        or value.get("decision")
        != "AUTHORIZE_ONE_100_UPDATE_JOINT_RECURRENT_CAUSAL_AB_ONLY"
        or value.get("execution_now")
        != {
            "optimizer_updates": 0,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        }
    ):
        raise ValueError("Winner-v20 training preregistration changed")
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
        "objective": "one_sided_negative_pitch_margin",
        "pitch_boundary_rad": 0.35,
        "objective_scale": None,
        "failure_transition_reward": 0.0,
        "settled_terminal_bonus": 250.0,
        "trainable_leaves": [
            "obs_weight",
            "previous_action_weight",
            "hidden_weight",
            "hidden_bias",
            "action_weight",
            "action_bias",
            "training_only_log_std",
            "training_only_value_weight",
            "training_only_value_bias",
        ],
        "bit_exact_frozen_leaves": [
            "auxiliary_hidden_weight",
            "auxiliary_action_weight",
            "auxiliary_bias",
        ],
        "hidden_replay_population": "valid_mask == 1 sampled ticks only",
        "hidden_replay_max_abs_error": 1.0e-6,
        "persistent_snapshots": "atomic readback-verified snapshot after every update",
        "persistent_checkpoints": {"half": 50, "final": 100},
    }:
        raise ValueError("Winner-v20 training constants changed")
    validate_source_manifest(value)


def graph_receipt(
    *,
    smoke: Any,
    networks: Any,
    training: Any,
    parameters: Mapping[str, Any],
    observations: np.ndarray,
    path: Path,
    label: str,
    update: int,
) -> dict[str, Any]:
    networks.export_calibrator_onnx(training.deployable_parameters(parameters), path)
    contract = smoke.onnx_contract(path, parameters, observations)
    required = (
        "abi_exact",
        "training_only_tensors_absent",
        "jax_onnx_at_most_1e_7",
        "previous_action_out_equals_action_bit_exact",
    )
    if not all(contract[name] for name in required):
        raise ValueError(f"Winner-v20 {label} graph contract failed")
    return {
        "label": label,
        "update": update,
        "path": str(path),
        "sha256": sha256(path),
        "bytes": path.stat().st_size,
        "contract": contract,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--canonical-fit", type=Path, required=True)
    parser.add_argument("--stage1-final-snapshot", type=Path, required=True)
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--offline-cpu-only", action="store_true")
    parser.add_argument("--joint-recurrent-support-training-authorized", action="store_true")
    args = parser.parse_args()
    if not args.offline_cpu_only or not args.joint_recurrent_support_training_authorized:
        raise PermissionError(
            "Winner-v20 training requires --offline-cpu-only "
            "--joint-recurrent-support-training-authorized"
        )
    if args.work_root.exists() or args.output.exists():
        raise FileExistsError("refusing to overwrite Winner-v20 training evidence")

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
        raise ValueError("Winner-v20 training requires CPU-only JAX")
    preregistration = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    validate_preregistration(preregistration)
    cpu_result = json.loads(CPU_RESULT.read_text(encoding="utf-8"))
    if (
        cpu_result.get("status")
        != "PASS_WINNER_V20_JOINT_RECURRENT_SUPPORT_CPU_CONTRACT"
        or cpu_result.get("decision")
        != "AUTHORIZE_SEPARATE_JOINT_RECURRENT_100_UPDATE_PREREGISTRATION_ONLY"
        or cpu_result.get("failed_checks") != []
        or not all(cpu_result.get("checks", {}).values())
        or cpu_result.get("execution", {}).get("optimizer_updates") != 2
        or cpu_result.get("authority", {}).get("joint_recurrent_training_executed")
        is not False
    ):
        raise ValueError("Winner-v20 passing CPU result changed")
    stage1_result = json.loads(STAGE1_RESULT.read_text(encoding="utf-8"))
    if (
        stage1_result.get("status") != "PASS_WINNER_V13_NORMALIZED_RESPONSE_STAGE1"
        or stage1_result.get("failed_checks") != []
        or sha256(args.stage1_final_snapshot) != STAGE1_SNAPSHOT_SHA256
        or args.stage1_final_snapshot.stat().st_size != STAGE1_SNAPSHOT_BYTES
    ):
        raise ValueError("Winner-v20 Stage-1 source changed")
    restored = full.load_snapshot(args.stage1_final_snapshot)
    if (
        restored["metadata"].get("schema_version")
        != "winner_v13.normalized_response_stage1_snapshot.v1"
        or restored["metadata"].get("stage") != "stage1"
        or restored["metadata"].get("completed_updates") != 100
        or int(np.asarray(restored["optimizer"]["count"])) != 100
        or restored["metadata"].get("robot_or_rdk_access") != 0
    ):
        raise ValueError("Winner-v20 Stage-1 metadata changed")
    expected_versions = dict(
        json.loads(FULL_PREREG.read_text(encoding="utf-8"))[
            "implementation_contract_environment"
        ]
    )
    if expected_versions.pop("platform") != "CPU only" or not smoke.validate_software_versions(
        {"software_versions": expected_versions}
    )["exact"]:
        raise ValueError("Winner-v20 training environment changed")
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
        raise ValueError("Winner-v20 training population changed")
    observer_type = smoke.load_runtime_observer(args.canonical_fit)
    parameters = restored["parameters"]
    source_joint = v20.joint_trainable_parameters(parameters)
    source_auxiliary = v20.frozen_auxiliary_parameters(parameters)
    optimizer = training.adam_initialize(source_joint)
    metrics: list[dict[str, Any]] = []
    snapshots: list[dict[str, Any]] = []
    checkpoints: list[dict[str, Any]] = []
    sampled_count = 0
    valid_count = 0
    start = time.monotonic()
    args.work_root.mkdir(parents=True, exist_ok=False)
    (args.work_root / "snapshots").mkdir()
    (args.work_root / "graphs").mkdir()

    def objective(values: Mapping[str, Any], data: Mapping[str, Any]):
        return v20.joint_recurrent_ppo_loss(
            values,
            data,
            clip_epsilon=training.PPO_CLIP_EPSILON,
            value_coefficient=training.PPO_VALUE_COEFFICIENT,
            entropy_coefficient=training.PPO_ENTROPY_COEFFICIENT,
        )

    objective_grad = jax.value_and_grad(objective, has_aux=True)
    recurrent = set(v20.RECURRENT_CORE_KEYS)
    for update_index in range(UPDATES):
        batch_np, episodes, observations = v20.stage2_rollout(
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
        boundary = full.stage2_action_boundary_evidence(batch_np)
        reward = v15.reward_evidence(batch_np)
        if not (
            boundary["realized_equals_numpy_bit_exact"]
            and boundary["numpy_equals_jax_bit_exact"]
            and reward["reward_formula_bit_exact"]
            and reward["penalty_formula_bit_exact"]
            and reward["only_zero_or_settled_bonus"]
            and reward["nonzero_penalty_count"] > 0
        ):
            raise ValueError(f"Winner-v20 transition changed at {update_index + 1}")
        batch = {key: jnp.asarray(value) for key, value in batch_np.items()}
        trainable_before = v20.joint_trainable_parameters(parameters)
        (loss, loss_metrics), gradients = objective_grad(trainable_before, batch)
        replay_error = float(loss_metrics["sampled_hidden_replay_max_abs_error"])
        if replay_error > 1.0e-6:
            raise ValueError(f"Winner-v20 hidden replay changed at {update_index + 1}")
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
        deltas = v20.leaf_max_abs_delta(trainable_before, trainable_after)
        gradient_max = {
            key: float(np.max(np.abs(np.asarray(value))))
            for key, value in gradients.items()
        }
        if update_index == 0:
            if not (
                all(gradient_max[name] == 0.0 for name in recurrent)
                and all(deltas[name] == 0.0 for name in recurrent)
                and all(
                    value > 0.0
                    for name, value in gradient_max.items()
                    if name not in recurrent
                )
                and all(
                    value > 0.0
                    for name, value in deltas.items()
                    if name not in recurrent
                )
            ):
                raise ValueError("Winner-v20 update-1 chain-rule gate changed")
        if update_index == 1 and not (
            all(value > 0.0 for value in gradient_max.values())
            and all(value > 0.0 for value in deltas.values())
        ):
            raise ValueError("Winner-v20 update-2 recurrent opening changed")
        parameters = v20.merge_joint_trainable(parameters, trainable_after)
        if not tree_equal(
            source_auxiliary, v20.frozen_auxiliary_parameters(parameters)
        ):
            raise ValueError(f"Winner-v20 changed auxiliary leaves at {update_index + 1}")
        if not training.finite_tree(
            {
                "loss": loss,
                "loss_metrics": loss_metrics,
                "gradients": gradients,
                "parameters": parameters,
                "optimizer": optimizer,
            }
        ):
            raise FloatingPointError(f"Winner-v20 update {update_index + 1} is nonfinite")
        sampled = int(np.sum(batch_np["valid_mask"]))
        valid = int(np.sum(batch_np["valid_transition_mask"]))
        sampled_count += sampled
        valid_count += valid
        metrics.append(
            {
                "update": update_index + 1,
                "loss": float(loss),
                "loss_metrics": {
                    key: float(value) for key, value in loss_metrics.items()
                },
                "sampled_count": sampled,
                "valid_transition_count": valid,
                "episode_receipts_sha256": episode_hash,
                "gradient_max_abs": gradient_max,
                "leaf_max_abs_delta": deltas,
                "action_boundary": boundary,
                "pitch_margin_reward": reward,
            }
        )
        snapshot_path = (
            args.work_root
            / "snapshots"
            / f"snapshot_joint_recurrent_update_{update_index + 1:03d}.npz"
        )
        snapshot_receipt = full.save_snapshot(
            snapshot_path,
            parameters,
            optimizer,
            {
                "schema_version": (
                    "winner_v20.joint_recurrent_support_training_snapshot.v1"
                ),
                "stage": "joint_recurrent_stage2",
                "completed_updates": update_index + 1,
                "root_seed": 120120,
                "learning_rate": float(training.STAGE2_LEARNING_RATE),
                "objective": "one_sided_negative_pitch_margin",
                "pitch_boundary_rad": 0.35,
                "source_stage1_snapshot_sha256": STAGE1_SNAPSHOT_SHA256,
                "preregistration_lf_sha256": lf_sha256(PREREGISTRATION),
                "runner_lf_sha256": lf_sha256(Path(__file__)),
                "cumulative_sampled_count": sampled_count,
                "cumulative_valid_transition_count": valid_count,
                "formal_support_cells": 0,
                "locomotion_steps": 0,
                "robot_or_rdk_access": 0,
            },
            restored["target_mean"],
            restored["target_std"],
        )
        loaded = v20.load_joint_snapshot(
            snapshot_path,
            expected_schema_version=(
                "winner_v20.joint_recurrent_support_training_snapshot.v1"
            ),
        )
        if not (
            tree_equal(parameters, loaded["parameters"])
            and np.array_equal(
                np.asarray(optimizer["count"]),
                np.asarray(loaded["optimizer"]["count"]),
            )
            and tree_equal(optimizer["m"], loaded["optimizer"]["m"])
            and tree_equal(optimizer["v"], loaded["optimizer"]["v"])
        ):
            raise ValueError(f"Winner-v20 snapshot changed at {update_index + 1}")
        snapshots.append({"update": update_index + 1, **snapshot_receipt})
        if update_index + 1 in {HALF_UPDATE, UPDATES}:
            label = "half" if update_index + 1 == HALF_UPDATE else "final"
            graph_path = args.work_root / "graphs" / f"winner_v20_{label}.onnx"
            graph = graph_receipt(
                smoke=smoke,
                networks=networks,
                training=training,
                parameters=parameters,
                observations=observations,
                path=graph_path,
                label=label,
                update=update_index + 1,
            )
            checkpoints.append(
                {
                    "label": label,
                    "update": update_index + 1,
                    "snapshot": snapshot_receipt,
                    "graph": graph,
                }
            )

    cumulative_deltas = v20.leaf_max_abs_delta(
        source_joint, v20.joint_trainable_parameters(parameters)
    )
    checks = {
        "exact_100_joint_updates": int(np.asarray(optimizer["count"])) == 100,
        "exact_100_atomic_snapshots": len(snapshots) == 100
        and all(row["bit_exact_readback"] for row in snapshots),
        "half_and_final_graphs_present": [row["label"] for row in checkpoints]
        == ["half", "final"],
        "all_updates_finite": all(
            math.isfinite(row["loss"])
            and all(math.isfinite(value) for value in row["gradient_max_abs"].values())
            and all(math.isfinite(value) for value in row["leaf_max_abs_delta"].values())
            for row in metrics
        ),
        "all_sampled_hidden_replays_at_most_1e_6": all(
            row["loss_metrics"]["sampled_hidden_replay_max_abs_error"] <= 1.0e-6
            for row in metrics
        ),
        "all_action_boundaries_exact": all(
            row["action_boundary"]["realized_equals_numpy_bit_exact"]
            and row["action_boundary"]["numpy_equals_jax_bit_exact"]
            for row in metrics
        ),
        "all_pitch_margin_rewards_exact": all(
            row["pitch_margin_reward"]["reward_formula_bit_exact"]
            and row["pitch_margin_reward"]["penalty_formula_bit_exact"]
            and row["pitch_margin_reward"]["only_zero_or_settled_bonus"]
            for row in metrics
        ),
        "pitch_margin_signal_nonzero_every_update": all(
            row["pitch_margin_reward"]["nonzero_penalty_count"] > 0
            for row in metrics
        ),
        "update_1_chain_rule_gate_exact": all(
            metrics[0]["gradient_max_abs"][name] == 0.0
            and metrics[0]["leaf_max_abs_delta"][name] == 0.0
            for name in recurrent
        ),
        "update_2_recurrent_opening_exact": all(
            metrics[1]["gradient_max_abs"][name] > 0.0
            and metrics[1]["leaf_max_abs_delta"][name] > 0.0
            for name in recurrent
        ),
        "all_joint_leaves_changed_cumulatively": all(
            value > 0.0 for value in cumulative_deltas.values()
        ),
        "auxiliary_predictor_bit_exact_frozen": tree_equal(
            source_auxiliary, v20.frozen_auxiliary_parameters(parameters)
        ),
        "formal_support_cells_zero": True,
        "locomotion_steps_zero": True,
        "robot_or_rdk_access_zero": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    result = {
        "schema_version": "winner_v20.joint_recurrent_support_training_result.v1",
        "status": (
            "PASS_WINNER_V20_JOINT_RECURRENT_SUPPORT_TRAINING_ARTIFACT"
            if not failed
            else "HOLD_WINNER_V20_JOINT_RECURRENT_SUPPORT_TRAINING_ARTIFACT"
        ),
        "decision": (
            "AUTHORIZE_SEPARATE_UNCHANGED_124_CELL_SUPPORT_GATE_PREREGISTRATION_ONLY"
            if not failed
            else "DO_NOT_EVALUATE_WINNER_V20_JOINT_RECURRENT_CONTROLLER"
        ),
        "checks": checks,
        "failed_checks": failed,
        "environment": {
            "software_versions": expected_versions,
            "jax_devices": [str(device) for device in jax.devices()],
        },
        "source_stage1_snapshot": {
            "sha256": STAGE1_SNAPSHOT_SHA256,
            "bytes": STAGE1_SNAPSHOT_BYTES,
        },
        "execution": {
            "optimizer_updates": 100,
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
        "joint_leaf_max_abs_delta": cumulative_deltas,
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
            "pass_authorizes_only": (
                "a separately frozen unchanged 124-cell support/context gate"
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
