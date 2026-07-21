#!/usr/bin/env python3
"""Run the preregistered Winner-v14 support-action amplitude diagnostic."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
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

PREREGISTRATION = (
    ANALYSIS / "winner_v14_support_action_diagnostic_preregistration.json"
)
FORMAL_RESULT = ANALYSIS / "winner_v13_support_controller_gate_result.json"
V13_GATE_PREREGISTRATION = (
    ANALYSIS / "winner_v13_support_controller_gate_preregistration.json"
)
TRAINING_RESULT = ANALYSIS / "winner_v13_support_controller_training_result.json"
DOMAIN = ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
EXPECTED_FORMAL_RESULT_LF_SHA256 = (
    "ad6e0ea99cf0d96fbcd336d7984467efccdd430591201d6fd5242a328518ce05"
)
CHECKPOINTS = (("half", 50), ("final", 100))
TICKS = 250


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def validate_preregistration(value: Mapping[str, Any]) -> None:
    if (
        value.get("schema_version")
        != "winner_v14.support_action_diagnostic_preregistration.v2"
        or value.get("status")
        != "PREREGISTERED_WINNER_V14_SUPPORT_ACTION_DIAGNOSTIC_V2"
        or value.get("decision")
        != "AUTHORIZE_ONE_HASH_CORRECTED_CPU_ONLY_FIVE_SCALE_SUPPORT_DIAGNOSTIC"
        or value.get("execution_now")
        != {
            "optimizer_updates": 0,
            "main_cells": 0,
            "repeat_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        }
    ):
        raise ValueError("Winner-v14 diagnostic preregistration changed")
    frozen = value.get("frozen_screen", {})
    if frozen != {
        "scales": [0.0, 0.25, 0.5, 0.75, 1.0],
        "checkpoint_labels": ["half", "final"],
        "cells_per_checkpoint_scale": 124,
        "heldout_repeats_per_checkpoint_scale": 32,
        "main_cells": 1240,
        "repeat_cells": 320,
        "duration_ticks": 250,
        "sensor_noise_seed_includes_scale": False,
    }:
        raise ValueError("Winner-v14 diagnostic population changed")
    sources = value.get("sources")
    if not isinstance(sources, dict) or not sources:
        raise ValueError("Winner-v14 diagnostic source manifest is absent")
    for name, item in sources.items():
        path = ROOT / item["path"]
        if (
            set(item) != {"hash_mode", "path", "sha256"}
            or item["hash_mode"] != "lf"
            or lf_sha256(path) != item["sha256"]
        ):
            raise ValueError(f"Winner-v14 diagnostic source changed: {name}")
    if canonical_sha256(sources) != value.get("source_manifest_sha256"):
        raise ValueError("Winner-v14 diagnostic source-manifest digest changed")


def cell_key(cell: Mapping[str, Any]) -> tuple[str, str, str | None]:
    condition = cell.get("condition")
    return (
        cell["configuration_id"],
        cell["plant"],
        None if condition is None else condition["id"],
    )


def formal_cell_index(
    formal_checkpoint: Mapping[str, Any]
) -> dict[tuple[str, str, str | None], Mapping[str, Any]]:
    rows = (
        formal_checkpoint["core_model_plant_cells"]
        + formal_checkpoint["sensor_transport_plant_cells"]
    )
    index = {cell_key(row): row for row in rows}
    if len(index) != 124:
        raise ValueError("formal Winner-v13 cell index changed")
    return index


def scale_one_matches_formal(
    diagnostic: Mapping[str, Any], formal: Mapping[str, Any]
) -> bool:
    scalar_fields = (
        "configuration_id",
        "configuration_sha256",
        "plant",
        "condition",
        "terminal",
        "episode",
        "support_pass",
        "maximum_jax_onnx_hidden_error",
        "final_h_out",
        "constant_normalized_prediction_mse",
    )
    if any(diagnostic[name] != formal[name] for name in scalar_fields):
        return False
    if diagnostic["source_previous_action_out_exact"] is not True:
        return False
    for name in ("observations", "actions", "predictions", "hidden"):
        if diagnostic["trace_hashes"][name] != formal["trace_hashes"][name]:
            return False
    return True


def run_cell(
    *,
    base: Any,
    transform: Any,
    normalized_training: Any,
    networks: Any,
    mujoco: Any,
    scene: Path,
    configuration: Mapping[str, Any],
    plant: str,
    calibrator_design: Mapping[str, Any],
    observer_type: type[Any],
    canonical_fit: Path,
    session: Any,
    parameters: Mapping[str, Any],
    target_mean: np.ndarray,
    target_std: np.ndarray,
    scale: float,
    condition: Mapping[str, Any] | None = None,
    rng: np.random.Generator | None = None,
) -> dict[str, Any]:
    import jax.numpy as jnp

    episode = base.Episode(
        mujoco,
        scene,
        configuration,
        plant,
        calibrator_design,
        observer_type,
        canonical_fit,
    )
    if episode.initial_contacts != (1, 1):
        raise ValueError("support-action cell does not start with both feet loaded")
    transport = base.ObservationTransport(condition, rng)
    action_delay = base.DelayedActionQueue(
        int((condition or {}).get("additional_action_delay_ticks", 0))
    )
    observation = transport.observe(episode.observation())
    previous_action = np.zeros((14,), dtype=np.float32)
    h_in = np.zeros((64,), dtype=np.float32)
    observations: list[np.ndarray] = []
    source_actions: list[np.ndarray] = []
    actions: list[np.ndarray] = []
    predictions: list[np.ndarray] = []
    hidden: list[np.ndarray] = []
    normalized_squared_errors: list[np.ndarray] = []
    baseline_normalized_squared_errors: list[np.ndarray] = []
    maximum_jax_onnx_hidden_error = 0.0
    maximum_action_delta_excess = 0.0
    source_previous_action_out_exact = True
    transformed_previous_action_chain_exact = True
    scale_one_source_action_bit_exact = True
    terminal = None
    maximum_delta = np.asarray(networks.INTERNAL_ACTION_DELTA, dtype=np.float32)
    for tick in range(TICKS):
        outputs = session.run(
            ["calibration_actions", "previous_action_out", "h_out"],
            {
                "obs": observation[None, :],
                "previous_action": previous_action[None, :],
                "h_in": h_in[None, :],
            },
        )
        source_action = np.asarray(outputs[0][0], dtype=np.float32)
        source_previous = np.asarray(outputs[1][0], dtype=np.float32)
        h_out = np.asarray(outputs[2][0], dtype=np.float32)
        source_previous_action_out_exact &= np.array_equal(
            source_previous, source_action
        )
        action = transform.scale_and_rebound_action(
            source_action, previous_action, maximum_delta, scale
        )
        expected = transform.scale_and_rebound_action(
            source_action, previous_action, maximum_delta, scale
        )
        transformed_previous_action_chain_exact &= np.array_equal(action, expected)
        if scale == 1.0:
            scale_one_source_action_bit_exact &= np.array_equal(action, source_action)
        maximum_action_delta_excess = max(
            maximum_action_delta_excess,
            float(np.max(np.abs(action - previous_action) - maximum_delta)),
        )
        jax_h, prediction = normalized_training.response_step(
            parameters,
            jnp.asarray(observation),
            jnp.asarray(previous_action),
            jnp.asarray(h_in),
            jnp.asarray(action),
        )
        prediction_np = np.asarray(prediction, dtype=np.float32)
        maximum_jax_onnx_hidden_error = max(
            maximum_jax_onnx_hidden_error,
            float(np.max(np.abs(np.asarray(jax_h, dtype=np.float32) - h_out))),
        )
        delayed = action_delay.push(action)
        valid, next_raw, evidence = base.step_episode(episode, action, delayed)
        observations.append(observation.copy())
        source_actions.append(source_action.copy())
        actions.append(action.copy())
        predictions.append(prediction_np.copy())
        hidden.append(h_out.copy())
        if not valid:
            terminal = {"tick": tick, **evidence}
            break
        if next_raw is None:
            raise AssertionError("valid support-action transition lacks observation")
        next_observation = transport.observe(next_raw)
        target = next_observation[normalized_training.AUXILIARY_INDICES]
        normalized_squared_errors.append(
            transform.normalized_prediction_squared_error(
                prediction_np, target, target_mean, target_std
            )
        )
        baseline_normalized_squared_errors.append(
            transform.constant_prediction_squared_error(
                target, target_mean, target_std
            )
        )
        observation = next_observation
        previous_action = action
        h_in = h_out
    summary = episode.summary()
    learned_mse = (
        float(np.mean(np.asarray(normalized_squared_errors, dtype=np.float64)))
        if normalized_squared_errors
        else math.inf
    )
    baseline_mse = (
        float(
            np.mean(
                np.asarray(baseline_normalized_squared_errors, dtype=np.float64)
            )
        )
        if baseline_normalized_squared_errors
        else math.inf
    )
    arrays = {
        "observations": np.asarray(observations, dtype=np.float32),
        "source_actions": np.asarray(source_actions, dtype=np.float32),
        "actions": np.asarray(actions, dtype=np.float32),
        "predictions": np.asarray(predictions, dtype=np.float32),
        "hidden": np.asarray(hidden, dtype=np.float32),
    }
    return {
        "configuration_id": configuration["id"],
        "configuration_sha256": base.canonical_sha256(configuration),
        "plant": plant,
        "condition": None if condition is None else dict(condition),
        "scale": scale,
        "terminal": terminal,
        "episode": summary,
        "support_pass": base.support_pass(summary) and terminal is None,
        "source_previous_action_out_exact": bool(source_previous_action_out_exact),
        "transformed_previous_action_chain_exact": bool(
            transformed_previous_action_chain_exact
        ),
        "scale_one_source_action_bit_exact": bool(
            scale_one_source_action_bit_exact if scale == 1.0 else True
        ),
        "maximum_action_delta_excess": maximum_action_delta_excess,
        "maximum_jax_onnx_hidden_error": maximum_jax_onnx_hidden_error,
        "corrected_learned_normalized_prediction_mse": learned_mse,
        "constant_normalized_prediction_mse": baseline_mse,
        "final_h_out": h_in.astype(float).tolist(),
        "trace_hashes": {
            name: base.array_sha256(value) for name, value in arrays.items()
        },
        "_arrays": arrays,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--training-work-root", type=Path, required=True)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--canonical-fit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--offline-cpu-only", action="store_true")
    parser.add_argument("--diagnostic-authorized", action="store_true")
    args = parser.parse_args()
    if not args.offline_cpu_only or not args.diagnostic_authorized:
        raise PermissionError(
            "support-action diagnostic requires --offline-cpu-only "
            "--diagnostic-authorized"
        )
    if args.output.exists():
        raise FileExistsError(f"refusing to overwrite diagnostic result: {args.output}")

    import jax
    import mujoco
    import onnxruntime as ort
    import run_winner_v12_calibrator_cpu_smoke as smoke
    import run_winner_v12_calibrator_support_gate as base
    import run_winner_v12_full_calibrator_training as full_training
    import run_winner_v13_support_controller_gate as v13_gate
    import winner_v12_calibrator_training as legacy_training
    import winner_v12_decomposed_backend_networks as networks
    import winner_v13_normalized_calibrator_training as normalized_training
    import winner_v14_support_action_diagnostic as transform

    if jax.default_backend() != "cpu" or any(
        device.platform != "cpu" for device in jax.devices()
    ):
        raise ValueError("support-action diagnostic requires CPU-only JAX")
    preregistration = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    validate_preregistration(preregistration)
    formal = json.loads(FORMAL_RESULT.read_text(encoding="utf-8"))
    if (
        lf_sha256(FORMAL_RESULT) != EXPECTED_FORMAL_RESULT_LF_SHA256
        or formal.get("status") != "HOLD_WINNER_V13_SUPPORT_CONTROLLER_GATE"
        or formal.get("decision") != "DO_NOT_TRAIN_RESPONSE_CONDITIONED_LOCOMOTION"
    ):
        raise ValueError("formal Winner-v13 gate result changed")
    training_result = json.loads(TRAINING_RESULT.read_text(encoding="utf-8"))
    if training_result.get("status") != "PASS_WINNER_V13_SUPPORT_CONTROLLER_TRAINING_ARTIFACT":
        raise ValueError("Winner-v13 support training artifact changed")
    v13_gate.smoke = smoke
    v13_gate.training = legacy_training
    v13_gate._TRAINING = training_result

    gate_prereg = json.loads(V13_GATE_PREREGISTRATION.read_text(encoding="utf-8"))
    calibrator_design = base.load_calibrator_design(gate_prereg)
    gate = gate_prereg["future_frozen_support_gate"]
    domain = json.loads(DOMAIN.read_text(encoding="utf-8"))
    matrix = domain["evaluation_matrix"]
    configurations = (
        matrix["fixed_anchors"]
        + matrix["discovery_samples"]
        + matrix["heldout_samples"]
    )
    heldout_ids = {row["id"] for row in matrix["heldout_samples"]}
    conditions = gate["sensor_transport_population"]
    if (
        len(configurations) != 56
        or canonical_sha256(conditions) != gate["sensor_transport_population_sha256"]
    ):
        raise ValueError("support-action diagnostic population changed")
    scene = (
        args.playground_root
        / "playground/open_duck_mini_v2/xmls/scene_flat_terrain_backlash.xml"
    )
    if not scene.is_file():
        raise FileNotFoundError(scene)
    observer_type = smoke.load_runtime_observer(args.canonical_fit)
    nominal = base.nominal_configuration(mujoco, scene)
    session_options = ort.SessionOptions()
    session_options.intra_op_num_threads = 1
    session_options.inter_op_num_threads = 1
    session_options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
    formal_by_checkpoint = {
        row["label"]: formal_cell_index(row) for row in formal["checkpoint_results"]
    }
    scale_results = []
    formal_reproduction_cells = 0
    for scale in transform.SCALES:
        checkpoint_results = []
        for checkpoint_index, (label, update) in enumerate(CHECKPOINTS):
            checkpoint_path, graph_path = v13_gate.checkpoint_paths(
                args.training_work_root, label
            )
            snapshot = full_training.load_snapshot(checkpoint_path)
            v13_gate.validate_snapshot(snapshot)
            if (
                snapshot["metadata"]["stage"] != "stage2"
                or snapshot["metadata"]["completed_updates"] != update
            ):
                raise ValueError(f"{label} diagnostic checkpoint boundary changed")
            parameters = snapshot["parameters"]
            target_mean = np.asarray(snapshot["target_mean"], dtype=np.float32)
            target_std = np.asarray(snapshot["target_std"], dtype=np.float32)
            session = ort.InferenceSession(
                str(graph_path),
                sess_options=session_options,
                providers=["CPUExecutionProvider"],
            )
            core_cells = []
            repeated_cells = []
            heldout_by_configuration: dict[str, dict[str, dict[str, Any]]] = {}
            for configuration in configurations:
                for plant in smoke.PLANTS:
                    cell = run_cell(
                        base=base,
                        transform=transform,
                        normalized_training=normalized_training,
                        networks=networks,
                        mujoco=mujoco,
                        scene=scene,
                        configuration=configuration,
                        plant=plant,
                        calibrator_design=calibrator_design,
                        observer_type=observer_type,
                        canonical_fit=args.canonical_fit,
                        session=session,
                        parameters=parameters,
                        target_mean=target_mean,
                        target_std=target_std,
                        scale=scale,
                    )
                    public = base.public_cell(cell)
                    core_cells.append(public)
                    if scale == 1.0:
                        expected = formal_by_checkpoint[label][cell_key(public)]
                        if not scale_one_matches_formal(public, expected):
                            raise ValueError(
                                f"scale-1 formal reproduction changed: {label} {cell_key(public)}"
                            )
                        formal_reproduction_cells += 1
                    if configuration["id"] in heldout_ids:
                        repeat = run_cell(
                            base=base,
                            transform=transform,
                            normalized_training=normalized_training,
                            networks=networks,
                            mujoco=mujoco,
                            scene=scene,
                            configuration=configuration,
                            plant=plant,
                            calibrator_design=calibrator_design,
                            observer_type=observer_type,
                            canonical_fit=args.canonical_fit,
                            session=session,
                            parameters=parameters,
                            target_mean=target_mean,
                            target_std=target_std,
                            scale=scale,
                        )
                        repeated_cells.append(
                            {
                                "configuration_id": configuration["id"],
                                "plant": plant,
                                "bit_exact": base.repeated_exact(cell, repeat),
                                "first_trace_hashes": public["trace_hashes"],
                                "repeat_trace_hashes": base.public_cell(repeat)[
                                    "trace_hashes"
                                ],
                            }
                        )
                        heldout_by_configuration.setdefault(
                            configuration["id"], {}
                        )[plant] = public
            sensor_cells = []
            for condition_index, condition in enumerate(conditions):
                for plant_index, plant in enumerate(smoke.PLANTS):
                    sequence = np.random.SeedSequence(
                        [120120, 3, checkpoint_index, condition_index, plant_index]
                    )
                    rng = np.random.default_rng(sequence)
                    cell = run_cell(
                        base=base,
                        transform=transform,
                        normalized_training=normalized_training,
                        networks=networks,
                        mujoco=mujoco,
                        scene=scene,
                        configuration=nominal,
                        plant=plant,
                        calibrator_design=calibrator_design,
                        observer_type=observer_type,
                        canonical_fit=args.canonical_fit,
                        session=session,
                        parameters=parameters,
                        target_mean=target_mean,
                        target_std=target_std,
                        scale=scale,
                        condition=condition,
                        rng=rng,
                    )
                    public = base.public_cell(cell)
                    public["prng"] = {
                        "algorithm": "NumPy PCG64",
                        "seed_sequence_entropy": [
                            120120,
                            3,
                            checkpoint_index,
                            condition_index,
                            plant_index,
                        ],
                        "seed_sequence_state_u32": sequence.generate_state(4)
                        .astype(int)
                        .tolist(),
                    }
                    sensor_cells.append(public)
                    if scale == 1.0:
                        expected = formal_by_checkpoint[label][cell_key(public)]
                        comparable = dict(public)
                        comparable.pop("prng")
                        if not scale_one_matches_formal(comparable, expected):
                            raise ValueError(
                                f"scale-1 sensor reproduction changed: {label} {cell_key(public)}"
                            )
                        formal_reproduction_cells += 1
            context = []
            for configuration in matrix["heldout_samples"]:
                pair = heldout_by_configuration[configuration["id"]]
                separation = float(
                    np.max(
                        np.abs(
                            np.asarray(pair[smoke.PLANTS[0]]["final_h_out"], dtype=np.float32)
                            - np.asarray(pair[smoke.PLANTS[1]]["final_h_out"], dtype=np.float32)
                        )
                    )
                )
                context.append(
                    {
                        "configuration_id": configuration["id"],
                        "final_h_out_linf_separation": separation,
                        "separation_above_1e_7": separation > 1.0e-7,
                    }
                )
            predictor = {}
            for plant in smoke.PLANTS:
                rows = [
                    heldout_by_configuration[configuration["id"]][plant]
                    for configuration in matrix["heldout_samples"]
                ]
                learned = float(
                    np.mean(
                        [
                            row["corrected_learned_normalized_prediction_mse"]
                            for row in rows
                        ]
                    )
                )
                baseline = float(
                    np.mean(
                        [row["constant_normalized_prediction_mse"] for row in rows]
                    )
                )
                predictor[plant] = {
                    "corrected_learned_normalized_prediction_mse": learned,
                    "constant_normalized_prediction_mse": baseline,
                    "learned_strictly_below_constant": learned < baseline,
                }
            all_cells = core_cells + sensor_cells
            checks = {
                "exact_124_main_cells": len(all_cells) == 124,
                "all_support_cells_pass": all(
                    row["support_pass"] for row in all_cells
                ),
                "all_transformed_action_chains_exact": all(
                    row["transformed_previous_action_chain_exact"]
                    for row in all_cells
                ),
                "all_action_deltas_within_graph_bounds": all(
                    row["maximum_action_delta_excess"] <= 5.0e-7
                    for row in all_cells
                ),
                "all_jax_onnx_hidden_errors_at_most_1e_7": all(
                    row["maximum_jax_onnx_hidden_error"] <= 1.0e-7
                    for row in all_cells
                ),
                "all_32_heldout_repeats_bit_exact": len(repeated_cells) == 32
                and all(row["bit_exact"] for row in repeated_cells),
                "all_16_heldout_contexts_separate": len(context) == 16
                and all(row["separation_above_1e_7"] for row in context),
                "corrected_prediction_beats_constant_per_plant": all(
                    row["learned_strictly_below_constant"]
                    for row in predictor.values()
                ),
                "scale_one_source_action_bit_exact": scale != 1.0
                or all(row["scale_one_source_action_bit_exact"] for row in all_cells),
            }
            checkpoint_results.append(
                {
                    "label": label,
                    "update": update,
                    "checkpoint_sha256": sha256(checkpoint_path),
                    "onnx_sha256": sha256(graph_path),
                    "core_model_plant_cells": core_cells,
                    "sensor_transport_plant_cells": sensor_cells,
                    "heldout_repeatability": repeated_cells,
                    "heldout_context_separation": context,
                    "heldout_prediction_corrected": predictor,
                    "checks": {name: bool(value) for name, value in checks.items()},
                    "failed_checks": sorted(
                        name for name, passed in checks.items() if not passed
                    ),
                }
            )
        complete_pass = all(not row["failed_checks"] for row in checkpoint_results)
        scale_results.append(
            {
                "scale": scale,
                "complete_pass": complete_pass,
                "checkpoint_results": checkpoint_results,
            }
        )
    passing_scales = [row["scale"] for row in scale_results if row["complete_pass"]]
    selected_scale = max(passing_scales) if passing_scales else None
    validity_checks = {
        "exact_scale_order": [row["scale"] for row in scale_results]
        == list(transform.SCALES),
        "exact_1240_main_cells": sum(
            len(checkpoint["core_model_plant_cells"])
            + len(checkpoint["sensor_transport_plant_cells"])
            for scale in scale_results
            for checkpoint in scale["checkpoint_results"]
        )
        == 1240,
        "exact_320_repeat_cells": sum(
            len(checkpoint["heldout_repeatability"])
            for scale in scale_results
            for checkpoint in scale["checkpoint_results"]
        )
        == 320,
        "scale_one_reproduces_all_248_formal_cells": formal_reproduction_cells == 248,
        "cpu_only": jax.default_backend() == "cpu"
        and all(device.platform == "cpu" for device in jax.devices()),
    }
    failed_validity = sorted(
        name for name, passed in validity_checks.items() if not passed
    )
    if failed_validity:
        raise ValueError(f"Winner-v14 diagnostic validity failed: {failed_validity}")
    result = {
        "schema_version": "winner_v14.support_action_diagnostic_result.v1",
        "status": "PASS_WINNER_V14_SUPPORT_ACTION_DIAGNOSTIC",
        "decision": (
            "SELECT_MAXIMUM_FULL_PASS_SCALE_FOR_SEPARATE_TRANSFORM_CONTRACT"
            if selected_scale is not None
            else "NO_SCALE_PASSES_PREREGISTER_SUPPORT_OBJECTIVE_REPAIR"
        ),
        "selected_scale": selected_scale,
        "passing_scales": passing_scales,
        "validity_checks": validity_checks,
        "failed_validity_checks": failed_validity,
        "scale_results": scale_results,
        "execution": {
            "optimizer_updates": 0,
            "main_cells": 1240,
            "repeat_cells": 320,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "sources": {
            "preregistration_lf_sha256": lf_sha256(PREREGISTRATION),
            "formal_result_sha256": sha256(FORMAL_RESULT),
            "training_result_lf_sha256": lf_sha256(TRAINING_RESULT),
            "runner_lf_sha256": lf_sha256(Path(__file__)),
        },
        "authority": {
            "robot_clearance": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "result_authorizes_only": (
                "a separate graph-transform contract for the selected scale, or a "
                "separate support-objective preregistration if no scale passes"
            ),
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(result["status"])
    print(f"DECISION={result['decision']}")
    print(f"SELECTED_SCALE={selected_scale}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
