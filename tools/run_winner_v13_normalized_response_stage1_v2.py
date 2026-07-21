#!/usr/bin/env python3
"""Run the fresh Winner-v13 Stage-1 with the corrected same-input checker."""

from __future__ import annotations

import json
import math
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
PATCHES = ROOT / "patches"
ANALYSIS = ROOT / "outputs/analysis"
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(PATCHES))

import run_winner_v13_normalized_response_stage1 as base  # noqa: E402


PREREGISTRATION = (
    ANALYSIS / "winner_v13_normalized_response_stage1_v2_preregistration.json"
)
CHECKER_RESULT = ANALYSIS / "winner_v13_stage1_checker_v2_cpu_result.json"
CHECKPOINT_CHECKS = [
    "exact_32_heldout_cells",
    "heldout_repeat_bit_exact",
    "learned_prediction_beats_constant_per_plant",
    "all_16_plant_contexts_separate",
    "checker_same_input_all_outputs_at_most_1e_7",
    "checker_previous_action_out_equals_action_bit_exact",
    "checker_nonzero_bounded_action_observed",
    "checker_zero_previous_action_exact_zero",
    "deployable_onnx_abi_exact",
    "deployable_onnx_training_only_tensors_absent",
    "deployable_onnx_chain_at_most_1e_7",
]


def validate_preregistration(preregistration: Mapping[str, Any]) -> None:
    training = preregistration.get("frozen_training", {})
    gate = preregistration.get("heldout_gate", {})
    if (
        preregistration.get("status")
        != "PREREGISTERED_WINNER_V13_NORMALIZED_RESPONSE_STAGE1_V2"
        or preregistration.get("decision")
        != "AUTHORIZE_ONE_FRESH_100_UPDATE_STAGE1_V2_RUN_ONLY"
        or training.get("stage") != "response encoder only"
        or training.get("optimizer_updates") != base.UPDATES
        or training.get("environments_per_update") != 80
        or training.get("ticks_per_environment") != base.TICKS
        or training.get("training_episode_slots") != 2_000_000
        or training.get("parameter_seed") != base.PARAMETER_SEED
        or training.get("training_root_seed") != 120120
        or training.get("learning_rate") != 0.0001
        or training.get("persistent_checkpoints") != {"half": 50, "final": 100}
        or gate.get("population")
        != "exact 16 HELDOUT configurations x P30/P31_34"
        or gate.get("checkpoints") != ["half", "final"]
        or gate.get("ticks_per_cell") != base.TICKS
        or gate.get("cells") != 64
        or gate.get("deterministic_repeat_cells") != 64
        or gate.get("root_seed") != base.EVALUATION_ROOT_SEED
        or gate.get("required_per_checkpoint_checks") != CHECKPOINT_CHECKS
        or preregistration.get("required_run_checks") != base.RUN_CHECKS
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
        raise ValueError("Winner-v13 Stage-1 v2 preregistration changed")
    checker = json.loads(CHECKER_RESULT.read_text(encoding="utf-8"))
    if (
        checker.get("status")
        != "PASS_WINNER_V13_STAGE1_CHECKER_V2_CPU_CONTRACT"
        or checker.get("decision")
        != "AUTHORIZE_FRESH_STAGE1_V2_PREREGISTRATION_ONLY"
        or checker.get("failed_checks") != []
        or checker.get("execution", {}).get("optimizer_updates") != 0
    ):
        raise ValueError("Winner-v13 checker-v2 result changed")
    base.validate_source_manifest(preregistration)


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
    import winner_v12_decomposed_backend_networks as networks

    batch, episodes, evidence = base.run_heldout_rollout(
        smoke=smoke,
        mujoco=mujoco,
        scene=scene,
        population=population,
        design=design,
        observer_type=observer_type,
        canonical_fit=canonical_fit,
        checkpoint_index=checkpoint_index,
    )
    repeat_batch, repeat_episodes, repeat_evidence = base.run_heldout_rollout(
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
        base.batch_exact(batch, repeat_batch)
        and base.episode_receipts_exact(episodes, repeat_episodes)
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
            raise ValueError("Winner-v13 v2 heldout predictor population is empty")
        predictor_by_plant[plant] = {
            "valid_transition_count": int(learned.shape[0]),
            "learned_normalized_mse_all_50": float(np.mean(learned)),
            "constant_normalized_mse_all_50": float(np.mean(baseline)),
            "learned_strictly_below_constant": bool(np.mean(learned) < np.mean(baseline)),
            "learned_normalized_mse_noncontact_48": float(np.mean(learned[:, :48])),
            "constant_normalized_mse_noncontact_48": float(np.mean(baseline[:, :48])),
            "contact_normalized_mse": float(np.mean(learned[:, 48:50])),
        }

    contexts = []
    for configuration_index in range(16):
        indices = (configuration_index * 2, configuration_index * 2 + 1)
        values = []
        for environment in indices:
            valid_ticks = int(np.sum(mask[environment]))
            if valid_ticks <= 0:
                raise ValueError("Winner-v13 v2 heldout context has no valid tick")
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
    maximum_same_input_errors = np.zeros(3, dtype=np.float64)
    state_equals_action = True
    nonzero_bounded_action_ticks = 0
    zero_previous_action_exact = True
    checked_ticks = 0
    deployable = v13.deployable_parameters(parameters)
    for environment in range(32):
        h_in = np.zeros((1, 64), dtype=np.float32)
        for tick in range(int(np.sum(mask[environment]))):
            observation = observations[environment, tick][None, :]
            previous = previous_actions[environment, tick][None, :]
            output = session.run(
                ["calibration_actions", "previous_action_out", "h_out"],
                {"obs": observation, "previous_action": previous, "h_in": h_in},
            )
            reference = networks.calibrator_step(
                deployable,
                jnp.asarray(observation),
                jnp.asarray(previous),
                jnp.asarray(h_in),
            )
            for index, (observed, expected) in enumerate(zip(output, reference)):
                maximum_same_input_errors[index] = max(
                    maximum_same_input_errors[index],
                    float(
                        np.max(
                            np.abs(observed - np.asarray(expected, dtype=np.float32))
                        )
                    ),
                )
            state_equals_action &= np.array_equal(output[0], output[1])
            nonzero_bounded_action_ticks += int(np.any(output[0] != 0.0))
            h_in = np.asarray(output[2], dtype=np.float32)
            checked_ticks += 1
        zero_output = session.run(
            ["calibration_actions", "previous_action_out"],
            {
                "obs": observations[environment, 0][None, :],
                "previous_action": np.zeros((1, 14), dtype=np.float32),
                "h_in": np.zeros((1, 64), dtype=np.float32),
            },
        )
        zero_previous_action_exact &= np.array_equal(
            zero_output[0], np.zeros((1, 14), dtype=np.float32)
        ) and np.array_equal(zero_output[1], zero_output[0])
    graph_contract = smoke.onnx_contract(graph, parameters, observations[mask][:256])
    checks = {
        "exact_32_heldout_cells": len(episodes) == 32,
        "heldout_repeat_bit_exact": repeated_exact,
        "learned_prediction_beats_constant_per_plant": all(
            row["learned_strictly_below_constant"]
            for row in predictor_by_plant.values()
        ),
        "all_16_plant_contexts_separate": len(contexts) == 16
        and all(row["separation_above_1e_7"] for row in contexts),
        "checker_same_input_all_outputs_at_most_1e_7": bool(
            np.max(maximum_same_input_errors) <= 1.0e-7
        ),
        "checker_previous_action_out_equals_action_bit_exact": bool(
            state_equals_action
        ),
        "checker_nonzero_bounded_action_observed": nonzero_bounded_action_ticks > 0,
        "checker_zero_previous_action_exact_zero": bool(zero_previous_action_exact),
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
        "heldout_episode_receipts_sha256": base.canonical_sha256(episodes),
        "heldout_repeat_episode_receipts_sha256": base.canonical_sha256(
            repeat_episodes
        ),
        "heldout_batch_sha256": base.canonical_sha256(
            {key: smoke.array_sha256(value) for key, value in sorted(batch.items())}
        ),
        "heldout_repeat_batch_sha256": base.canonical_sha256(
            {
                key: smoke.array_sha256(value)
                for key, value in sorted(repeat_batch.items())
            }
        ),
        "checker_onnx_ticks": checked_ticks,
        "checker_same_input_max_abs_errors": {
            "action": float(maximum_same_input_errors[0]),
            "previous_action_out": float(maximum_same_input_errors[1]),
            "hidden": float(maximum_same_input_errors[2]),
        },
        "checker_nonzero_bounded_action_ticks": nonzero_bounded_action_ticks,
        "graph_contract": graph_contract,
        "checks": checks,
        "failed_checks": sorted(name for name, passed in checks.items() if not passed),
    }


def main() -> int:
    base.PREREGISTRATION = PREREGISTRATION
    base.validate_preregistration = validate_preregistration
    base.evaluate_checkpoint = evaluate_checkpoint
    base.__file__ = str(Path(__file__).resolve())
    result_code = base.main()
    try:
        output_index = sys.argv.index("--output") + 1
        output = Path(sys.argv[output_index])
    except (ValueError, IndexError) as error:
        raise ValueError("Winner-v13 Stage-1 v2 output argument is absent") from error
    result = json.loads(output.read_text(encoding="utf-8"))
    result["schema_version"] = "winner_v13.normalized_response_stage1_result.v2"
    result["sources"]["checker_v2_cpu_result_lf_sha256"] = base.lf_sha256(
        CHECKER_RESULT
    )
    output.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return result_code


if __name__ == "__main__":
    raise SystemExit(main())
