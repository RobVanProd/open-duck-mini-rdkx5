#!/usr/bin/env python3
"""Train and gate only the Winner-v13 normalized-response encoder."""

from __future__ import annotations

import argparse
from contextlib import contextmanager
import json
import math
import os
from pathlib import Path
import sys
import time
from typing import Any, Mapping, Sequence

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
PATCHES = ROOT / "patches"
TOOLS = ROOT / "tools"
ANALYSIS = ROOT / "outputs/analysis"
sys.path.insert(0, str(PATCHES))
sys.path.insert(0, str(TOOLS))

PREREGISTRATION = ANALYSIS / "winner_v13_normalized_response_stage1_preregistration.json"
CPU_RESULT = ANALYSIS / "winner_v13_normalized_response_cpu_contract_result.json"
FULL_PREREGISTRATION = (
    ANALYSIS / "winner_v12_full_calibrator_training_preregistration.json"
)
DOMAIN = ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
UPDATES = 100
TICKS = 250
CHECKPOINTS = {50: "half", 100: "final"}
PARAMETER_SEED = 60720
EVALUATION_ROOT_SEED = 131313
RUN_CHECKS = [
    "exact_100_optimizer_updates",
    "exact_100_immutable_snapshots",
    "half_and_final_evaluated",
    "both_checkpoints_pass_heldout_gate",
    "action_head_bit_exact",
]
CHECKPOINT_CHECKS = [
    "exact_32_heldout_cells",
    "heldout_repeat_bit_exact",
    "learned_prediction_beats_constant_per_plant",
    "all_16_plant_contexts_separate",
    "checker_onnx_action_exact_zero",
    "checker_onnx_hidden_at_most_1e_7",
    "deployable_onnx_abi_exact",
    "deployable_onnx_training_only_tensors_absent",
    "deployable_onnx_chain_at_most_1e_7",
]


def lf_sha256(path: Path) -> str:
    import hashlib

    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical_sha256(value: Any) -> str:
    import hashlib

    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def validate_source_manifest(preregistration: Mapping[str, Any]) -> None:
    sources = preregistration.get("sources")
    if not isinstance(sources, dict) or not sources:
        raise ValueError("Winner-v13 Stage-1 source manifest is absent")
    for name, item in sources.items():
        path = ROOT / item["path"]
        if (
            set(item) != {"hash_mode", "path", "sha256"}
            or item["hash_mode"] != "lf"
            or lf_sha256(path) != item["sha256"]
        ):
            raise ValueError(f"Winner-v13 Stage-1 source changed: {name}")
    if canonical_sha256(sources) != preregistration.get("source_manifest_sha256"):
        raise ValueError("Winner-v13 Stage-1 source-manifest digest changed")


def validate_preregistration(preregistration: Mapping[str, Any]) -> None:
    training = preregistration.get("frozen_training", {})
    gate = preregistration.get("heldout_gate", {})
    if (
        preregistration.get("status")
        != "PREREGISTERED_WINNER_V13_NORMALIZED_RESPONSE_STAGE1"
        or preregistration.get("decision")
        != "AUTHORIZE_ONE_100_UPDATE_STAGE1_RUN_ONLY"
        or training.get("stage") != "response encoder only"
        or training.get("optimizer_updates") != UPDATES
        or training.get("environments_per_update") != 80
        or training.get("ticks_per_environment") != TICKS
        or training.get("training_episode_slots") != 2_000_000
        or training.get("parameter_seed") != PARAMETER_SEED
        or training.get("training_root_seed") != 120120
        or training.get("persistent_checkpoints") != {"half": 50, "final": 100}
        or gate.get("population")
        != "exact 16 HELDOUT configurations x P30/P31_34"
        or gate.get("checkpoints") != ["half", "final"]
        or gate.get("ticks_per_cell") != TICKS
        or gate.get("cells") != 64
        or gate.get("deterministic_repeat_cells") != 64
        or gate.get("root_seed") != EVALUATION_ROOT_SEED
        or gate.get("required_per_checkpoint_checks") != CHECKPOINT_CHECKS
        or preregistration.get("required_run_checks") != RUN_CHECKS
        or preregistration.get("execution_now")
        != {
            "stage1_optimizer_updates": 0,
            "stage2_optimizer_updates": 0,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        }
        or preregistration.get("authority", {}).get("robot_clearance") is not False
    ):
        raise ValueError("Winner-v13 Stage-1 preregistration changed")
    validate_source_manifest(preregistration)


def trees_equal(left: Mapping[str, Any], right: Mapping[str, Any]) -> bool:
    return set(left) == set(right) and all(
        np.array_equal(np.asarray(left[key]), np.asarray(right[key])) for key in left
    )


def optimizer_equal(left: Mapping[str, Any], right: Mapping[str, Any]) -> bool:
    return bool(
        np.array_equal(np.asarray(left["count"]), np.asarray(right["count"]))
        and trees_equal(left["m"], right["m"])
        and trees_equal(left["v"], right["v"])
    )


def snapshot_metadata(
    *,
    completed_updates: int,
    metrics: Sequence[Mapping[str, Any]],
    sampled_count: int,
    valid_count: int,
) -> dict[str, Any]:
    return {
        "schema_version": "winner_v13.normalized_response_stage1_snapshot.v1",
        "stage": "stage1",
        "completed_updates": completed_updates,
        "objective": "normalized-coordinate next-response MSE",
        "parameter_seed": PARAMETER_SEED,
        "training_root_seed": 120120,
        "metrics": list(metrics),
        "cumulative_sampled_count": sampled_count,
        "cumulative_valid_transition_count": valid_count,
        "full_training_updates": 0,
        "formal_support_cells": 0,
        "locomotion_steps": 0,
        "robot_or_rdk_access": 0,
        "preregistration_lf_sha256": lf_sha256(PREREGISTRATION),
    }


def save_and_verify_snapshot(
    *,
    full: Any,
    path: Path,
    parameters: Mapping[str, Any],
    optimizer: Mapping[str, Any],
    metadata: Mapping[str, Any],
    target_mean: np.ndarray,
    target_std: np.ndarray,
) -> dict[str, Any]:
    receipt = full.save_snapshot(
        path, parameters, optimizer, metadata, target_mean, target_std
    )
    loaded = full.load_snapshot(path)
    if (
        not trees_equal(parameters, loaded["parameters"])
        or not optimizer_equal(optimizer, loaded["optimizer"])
        or not np.array_equal(target_mean, loaded["target_mean"])
        or not np.array_equal(target_std, loaded["target_std"])
        or loaded["metadata"].get("completed_updates")
        != metadata["completed_updates"]
        or loaded["metadata"].get("schema_version")
        != "winner_v13.normalized_response_stage1_snapshot.v1"
    ):
        raise ValueError("Winner-v13 Stage-1 snapshot readback changed")
    return receipt


def heldout_population(domain: Mapping[str, Any]) -> list[dict[str, Any]]:
    configurations = domain["evaluation_matrix"]["heldout_samples"]
    if [row["id"] for row in configurations] != [
        f"HELDOUT_{index:02d}" for index in range(16)
    ]:
        raise ValueError("Winner-v13 heldout configuration population changed")
    return [dict(configuration) for row in configurations for configuration in (row, row)]


def evaluation_prng(
    checkpoint_index: int, environment: int
) -> tuple[np.random.Generator, dict[str, Any]]:
    entropy = [EVALUATION_ROOT_SEED, checkpoint_index, environment]
    sequence = np.random.SeedSequence(entropy)
    return np.random.Generator(np.random.PCG64(sequence)), {
        "algorithm": "NumPy PCG64",
        "seed_sequence_entropy": entropy,
        "seed_sequence_state_u32": sequence.generate_state(4).astype(int).tolist(),
    }


@contextmanager
def heldout_rollout_context(smoke: Any, checkpoint_index: int):
    old_count = smoke.SMOKE_ENVIRONMENTS
    old_ticks = smoke.SMOKE_TICKS
    old_prng = smoke.prng_for

    def bound_prng(stage: int, environment: int):
        if stage != 1:
            raise ValueError("Winner-v13 heldout rollout stage changed")
        return evaluation_prng(checkpoint_index, environment)

    smoke.SMOKE_ENVIRONMENTS = 32
    smoke.SMOKE_TICKS = TICKS
    smoke.prng_for = bound_prng
    try:
        yield
    finally:
        smoke.SMOKE_ENVIRONMENTS = old_count
        smoke.SMOKE_TICKS = old_ticks
        smoke.prng_for = old_prng


def run_heldout_rollout(
    *,
    smoke: Any,
    mujoco: Any,
    scene: Path,
    population: Sequence[Mapping[str, Any]],
    design: Mapping[str, Any],
    observer_type: type[Any],
    canonical_fit: Path,
    checkpoint_index: int,
):
    with heldout_rollout_context(smoke, checkpoint_index):
        return smoke.stage1_rollout(
            mujoco, scene, population, design, observer_type, canonical_fit
        )


def batch_exact(left: Mapping[str, np.ndarray], right: Mapping[str, np.ndarray]) -> bool:
    return set(left) == set(right) and all(
        np.array_equal(np.asarray(left[key]), np.asarray(right[key])) for key in left
    )


def episode_receipts_exact(
    left: Sequence[Mapping[str, Any]], right: Sequence[Mapping[str, Any]]
) -> bool:
    return canonical_sha256(left) == canonical_sha256(right)


def evaluate_checkpoint(
    *,
    label: str,
    checkpoint_index: int,
    parameters: Mapping[str, Any],
    graph: Path,
    target_mean: np.ndarray,
    target_std: np.ndarray,
    smoke: Any,
    v13: Any,
    mujoco: Any,
    scene: Path,
    population: Sequence[Mapping[str, Any]],
    design: Mapping[str, Any],
    observer_type: type[Any],
    canonical_fit: Path,
) -> dict[str, Any]:
    import jax.numpy as jnp
    import onnxruntime as ort

    batch, episodes, evidence = run_heldout_rollout(
        smoke=smoke,
        mujoco=mujoco,
        scene=scene,
        population=population,
        design=design,
        observer_type=observer_type,
        canonical_fit=canonical_fit,
        checkpoint_index=checkpoint_index,
    )
    repeat_batch, repeat_episodes, repeat_evidence = run_heldout_rollout(
        smoke=smoke,
        mujoco=mujoco,
        scene=scene,
        population=population,
        design=design,
        observer_type=observer_type,
        canonical_fit=canonical_fit,
        checkpoint_index=checkpoint_index,
    )
    evidence.pop("normalization")
    repeat_evidence.pop("normalization")
    repeated_exact = bool(
        batch_exact(batch, repeat_batch)
        and episode_receipts_exact(episodes, repeat_episodes)
        and evidence == repeat_evidence
    )
    observations = np.asarray(batch["observations"], dtype=np.float32)
    previous_actions = np.asarray(batch["previous_actions"], dtype=np.float32)
    realized_actions = np.asarray(batch["realized_actions"], dtype=np.float32)
    targets = np.asarray(batch["targets"], dtype=np.float32)
    mask = np.asarray(batch["valid_mask"], dtype=bool)
    _, hidden_jax, prediction_jax = v13.stage1_predictions(
        v13.stage1_parameters(parameters),
        jnp.asarray(observations),
        jnp.asarray(previous_actions),
        jnp.asarray(realized_actions),
    )
    hidden = np.asarray(hidden_jax, dtype=np.float32)
    prediction = np.asarray(prediction_jax, dtype=np.float32)
    target_normalized = (
        targets.astype(np.float64) - target_mean.astype(np.float64)
    ) / target_std.astype(np.float64)
    learned_sq = np.square(prediction.astype(np.float64) - target_normalized)
    baseline_sq = np.square(target_normalized)
    predictor_by_plant = {}
    for plant_index, plant in enumerate(smoke.PLANTS):
        rows = np.arange(plant_index, 32, 2)
        plant_mask = mask[rows]
        learned = learned_sq[rows][plant_mask]
        baseline = baseline_sq[rows][plant_mask]
        if learned.shape[0] == 0 or learned.shape != baseline.shape:
            raise ValueError("Winner-v13 heldout predictor population is empty")
        predictor_by_plant[plant] = {
            "valid_transition_count": int(learned.shape[0]),
            "learned_normalized_mse_all_50": float(np.mean(learned)),
            "constant_normalized_mse_all_50": float(np.mean(baseline)),
            "learned_strictly_below_constant": bool(
                np.mean(learned) < np.mean(baseline)
            ),
            "learned_normalized_mse_noncontact_48": float(
                np.mean(learned[:, :48])
            ),
            "constant_normalized_mse_noncontact_48": float(
                np.mean(baseline[:, :48])
            ),
            "contact_normalized_mse": float(np.mean(learned[:, 48:50])),
        }

    contexts = []
    for configuration_index in range(16):
        indices = (configuration_index * 2, configuration_index * 2 + 1)
        values = []
        for environment in indices:
            valid_ticks = int(np.sum(mask[environment]))
            if valid_ticks <= 0:
                raise ValueError("Winner-v13 heldout context has no valid tick")
            values.append(hidden[environment, valid_ticks - 1])
        separation = float(np.max(np.abs(values[0] - values[1])))
        contexts.append(
            {
                "configuration_id": population[indices[0]]["id"],
                "final_valid_h_out_linf_plant_separation": separation,
                "separation_above_1e_7": separation > 1.0e-7,
            }
        )

    session = ort.InferenceSession(str(graph), providers=["CPUExecutionProvider"])
    maximum_onnx_hidden_error = 0.0
    graph_action_zero = True
    checked_ticks = 0
    for environment in range(32):
        h_in = np.zeros((1, 64), dtype=np.float32)
        for tick in range(int(np.sum(mask[environment]))):
            output = session.run(
                ["calibration_actions", "previous_action_out", "h_out"],
                {
                    "obs": observations[environment, tick][None, :],
                    "previous_action": previous_actions[environment, tick][None, :],
                    "h_in": h_in,
                },
            )
            graph_action_zero &= np.array_equal(
                output[0], np.zeros((1, 14), dtype=np.float32)
            ) and np.array_equal(output[1], output[0])
            maximum_onnx_hidden_error = max(
                maximum_onnx_hidden_error,
                float(np.max(np.abs(output[2][0] - hidden[environment, tick]))),
            )
            h_in = np.asarray(output[2], dtype=np.float32)
            checked_ticks += 1
    graph_contract = smoke.onnx_contract(
        graph, parameters, observations[mask][:256]
    )
    checks = {
        "exact_32_heldout_cells": len(episodes) == 32,
        "heldout_repeat_bit_exact": repeated_exact,
        "learned_prediction_beats_constant_per_plant": all(
            row["learned_strictly_below_constant"]
            for row in predictor_by_plant.values()
        ),
        "all_16_plant_contexts_separate": len(contexts) == 16
        and all(row["separation_above_1e_7"] for row in contexts),
        "checker_onnx_action_exact_zero": bool(graph_action_zero),
        "checker_onnx_hidden_at_most_1e_7": maximum_onnx_hidden_error <= 1.0e-7,
        "deployable_onnx_abi_exact": graph_contract["abi_exact"],
        "deployable_onnx_training_only_tensors_absent": graph_contract[
            "training_only_tensors_absent"
        ],
        "deployable_onnx_chain_at_most_1e_7": graph_contract[
            "jax_onnx_at_most_1e_7"
        ],
    }
    return {
        "label": label,
        "predictor_by_plant": predictor_by_plant,
        "context_separation": contexts,
        "heldout_episode_receipts_sha256": canonical_sha256(episodes),
        "heldout_repeat_episode_receipts_sha256": canonical_sha256(repeat_episodes),
        "heldout_batch_sha256": canonical_sha256(
            {key: smoke.array_sha256(value) for key, value in sorted(batch.items())}
        ),
        "heldout_repeat_batch_sha256": canonical_sha256(
            {
                key: smoke.array_sha256(value)
                for key, value in sorted(repeat_batch.items())
            }
        ),
        "checker_onnx_hidden_ticks": checked_ticks,
        "checker_onnx_hidden_max_abs_error": maximum_onnx_hidden_error,
        "graph_contract": graph_contract,
        "checks": checks,
        "failed_checks": sorted(name for name, passed in checks.items() if not passed),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--canonical-fit", type=Path, required=True)
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--offline-cpu-only", action="store_true")
    parser.add_argument("--stage1-training-authorized", action="store_true")
    args = parser.parse_args()
    if not args.offline_cpu_only or not args.stage1_training_authorized:
        raise PermissionError(
            "Winner-v13 Stage-1 requires --offline-cpu-only "
            "--stage1-training-authorized"
        )
    if args.output.exists() or args.work_root.exists():
        raise FileExistsError("refusing to overwrite Winner-v13 Stage-1 evidence")

    import jax
    import jax.numpy as jnp
    import mujoco
    import run_winner_v12_calibrator_cpu_smoke as smoke
    import run_winner_v12_full_calibrator_training as full
    import winner_v12_decomposed_backend_networks as networks
    import winner_v13_normalized_calibrator_training as v13

    if jax.default_backend() != "cpu" or any(
        device.platform != "cpu" for device in jax.devices()
    ):
        raise ValueError("Winner-v13 Stage-1 requires CPU-only JAX")
    preregistration = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    validate_preregistration(preregistration)
    cpu_result = json.loads(CPU_RESULT.read_text(encoding="utf-8"))
    if (
        cpu_result.get("status")
        != "PASS_WINNER_V13_NORMALIZED_RESPONSE_CPU_CONTRACT"
        or cpu_result.get("decision")
        != "AUTHORIZE_NORMALIZED_RESPONSE_STAGE1_PREREGISTRATION_ONLY"
        or cpu_result.get("execution", {}).get("full_training_updates") != 0
    ):
        raise ValueError("Winner-v13 CPU result did not authorize Stage-1")

    full_preregistration = json.loads(FULL_PREREGISTRATION.read_text(encoding="utf-8"))
    design = json.loads(smoke.CALIBRATOR_PREREG.read_text(encoding="utf-8"))
    domain = json.loads(DOMAIN.read_text(encoding="utf-8"))
    training_population = full.training_population(full_preregistration, domain)
    evaluation_population = heldout_population(domain)
    observer_type = smoke.load_runtime_observer(args.canonical_fit)
    scene = (
        args.playground_root
        / "playground/open_duck_mini_v2/xmls/scene_flat_terrain_backlash.xml"
    )
    if not scene.is_file():
        raise FileNotFoundError(scene)
    args.work_root.mkdir(parents=True, exist_ok=False)
    snapshot_root = args.work_root / "snapshots"
    graph_root = args.work_root / "graphs"
    graph_root.mkdir(parents=True, exist_ok=False)

    parameters = v13.initialize_training_parameters(seed=PARAMETER_SEED)
    initial_action = {
        key: np.asarray(parameters[key]).copy() for key in v13.DEPLOYABLE_ACTION_KEYS
    }
    optimizer = v13.adam_initialize(v13.stage1_parameters(parameters))
    loss_grad = jax.value_and_grad(v13.stage1_loss)
    target_mean: np.ndarray | None = None
    target_std: np.ndarray | None = None
    metrics = []
    snapshots = []
    checkpoint_state: dict[str, dict[str, Any]] = {}
    sampled_count = 0
    valid_count = 0
    start = time.monotonic()
    for update_index in range(UPDATES):
        batch_np, episodes, evidence = full.stage1_rollout(
            mujoco,
            scene,
            training_population,
            design,
            observer_type,
            args.canonical_fit,
            update_index,
        )
        normalization = evidence.pop("normalization")
        normalization_mean, normalization_std = full.validate_stage1_normalization(
            normalization, batch_np
        )
        if update_index == 0:
            target_mean = normalization_mean
            target_std = normalization_std
        if target_mean is None or target_std is None:
            raise AssertionError("Winner-v13 training normalization is absent")
        if not evidence.get("realized_action_chain_exact") or not evidence.get(
            "fixed_p30_observer_slot_exact"
        ):
            raise ValueError("Winner-v13 Stage-1 rollout contract changed")
        episode_hash = full.validate_episode_receipts(
            episodes,
            training_population,
            stage=1,
            update_index=update_index,
        )
        batch = {key: jnp.asarray(value) for key, value in batch_np.items()}
        trainable = v13.stage1_parameters(parameters)
        loss, gradients = loss_grad(
            trainable,
            batch,
            jnp.asarray(target_mean),
            jnp.asarray(target_std),
        )
        trainable, optimizer = v13.adam_step(
            trainable,
            gradients,
            optimizer,
            learning_rate=v13.STAGE1_LEARNING_RATE,
            beta1=v13.ADAM_BETA1,
            beta2=v13.ADAM_BETA2,
            epsilon=v13.ADAM_EPSILON,
        )
        parameters = v13.merge_stage1(parameters, trainable)
        if not v13.finite_tree(
            {
                "loss": loss,
                "gradients": gradients,
                "parameters": parameters,
                "optimizer": optimizer,
            }
        ):
            raise FloatingPointError(f"Winner-v13 Stage-1 update {update_index} is nonfinite")
        if any(
            not np.array_equal(np.asarray(parameters[key]), initial_action[key])
            for key in v13.DEPLOYABLE_ACTION_KEYS
        ):
            raise ValueError("Winner-v13 Stage-1 changed the action head")
        valid = int(np.sum(batch_np["valid_mask"]))
        sampled = sum(
            int(row["episode"]["valid_ticks"])
            + (1 if row["terminal"] is not None else 0)
            for row in episodes
        )
        if valid <= 0 or sampled < valid or sampled > 80 * TICKS:
            raise ValueError("Winner-v13 Stage-1 sample accounting changed")
        sampled_count += sampled
        valid_count += valid
        metrics.append(
            {
                "update": update_index + 1,
                "loss": float(loss),
                "sampled_count": sampled,
                "valid_transition_count": valid,
                "completed_episodes": sum(
                    row["episode"]["valid_ticks"] == TICKS for row in episodes
                ),
                "episode_receipts_sha256": episode_hash,
            }
        )
        snapshot_path = snapshot_root / f"snapshot_stage1_update_{update_index + 1:03d}.npz"
        snapshot = save_and_verify_snapshot(
            full=full,
            path=snapshot_path,
            parameters=parameters,
            optimizer=optimizer,
            metadata=snapshot_metadata(
                completed_updates=update_index + 1,
                metrics=metrics,
                sampled_count=sampled_count,
                valid_count=valid_count,
            ),
            target_mean=target_mean,
            target_std=target_std,
        )
        snapshots.append(snapshot)
        if update_index + 1 in CHECKPOINTS:
            label = CHECKPOINTS[update_index + 1]
            graph = graph_root / f"winner_v13_normalized_response_{label}.onnx"
            networks.export_calibrator_onnx(v13.deployable_parameters(parameters), graph)
            checkpoint_state[label] = {
                "update": update_index + 1,
                "parameters": {key: np.asarray(value).copy() for key, value in parameters.items()},
                "snapshot": snapshot,
                "graph": graph,
            }

    if set(checkpoint_state) != {"half", "final"}:
        raise ValueError("Winner-v13 Stage-1 checkpoint set is incomplete")
    checkpoint_results = []
    for checkpoint_index, label in enumerate(("half", "final")):
        state = checkpoint_state[label]
        evaluation = evaluate_checkpoint(
            label=label,
            checkpoint_index=checkpoint_index,
            parameters=state["parameters"],
            graph=state["graph"],
            target_mean=target_mean,
            target_std=target_std,
            smoke=smoke,
            v13=v13,
            mujoco=mujoco,
            scene=scene,
            population=evaluation_population,
            design=design,
            observer_type=observer_type,
            canonical_fit=args.canonical_fit,
        )
        checkpoint_results.append(
            {
                **evaluation,
                "update": state["update"],
                "snapshot": state["snapshot"],
            }
        )

    checks = {
        "exact_100_optimizer_updates": int(np.asarray(optimizer["count"])) == 100,
        "exact_100_immutable_snapshots": len(snapshots) == 100,
        "half_and_final_evaluated": [row["label"] for row in checkpoint_results]
        == ["half", "final"],
        "both_checkpoints_pass_heldout_gate": all(
            not row["failed_checks"] for row in checkpoint_results
        ),
        "action_head_bit_exact": all(
            np.array_equal(np.asarray(parameters[key]), initial_action[key])
            for key in v13.DEPLOYABLE_ACTION_KEYS
        ),
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    result = {
        "schema_version": "winner_v13.normalized_response_stage1_result.v1",
        "status": (
            "PASS_WINNER_V13_NORMALIZED_RESPONSE_STAGE1"
            if not failed
            else "HOLD_WINNER_V13_NORMALIZED_RESPONSE_STAGE1"
        ),
        "decision": (
            "AUTHORIZE_SUPPORT_CONTROLLER_PREREGISTRATION_ONLY"
            if not failed
            else "DO_NOT_TRAIN_SUPPORT_CONTROLLER"
        ),
        "checks": checks,
        "failed_checks": failed,
        "metrics": metrics,
        "checkpoint_results": checkpoint_results,
        "normalization": {
            "target_mean_sha256": smoke.array_sha256(target_mean),
            "target_std_sha256": smoke.array_sha256(target_std),
            "contact_mean": target_mean[48:50].astype(float).tolist(),
            "contact_std": target_std[48:50].astype(float).tolist(),
        },
        "snapshot_manifest": snapshots,
        "execution": {
            "stage1_optimizer_updates": 100,
            "stage2_optimizer_updates": 0,
            "training_episode_slots": 80 * TICKS * 100,
            "heldout_evaluation_cells": 64,
            "heldout_repeat_cells": 64,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "sources": {
            "preregistration_lf_sha256": lf_sha256(PREREGISTRATION),
            "cpu_result_lf_sha256": lf_sha256(CPU_RESULT),
            "runner_lf_sha256": lf_sha256(Path(__file__)),
            "v13_primitives_lf_sha256": lf_sha256(
                PATCHES / "winner_v13_normalized_calibrator_training.py"
            ),
        },
        "elapsed_seconds": time.monotonic() - start,
        "authority": {
            "robot_clearance": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "pass_authorizes_only": "a separate automatic support-controller preregistration",
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
