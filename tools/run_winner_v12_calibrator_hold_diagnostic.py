#!/usr/bin/env python3
"""Diagnose the frozen Winner-v12 calibrator HOLD without training or selection."""

from __future__ import annotations

import argparse
from collections.abc import Mapping, Sequence
import json
import math
import os
from pathlib import Path
import sys
from typing import Any

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
PATCHES = ROOT / "patches"
TOOLS = ROOT / "tools"
ANALYSIS = ROOT / "outputs/analysis"
sys.path.insert(0, str(PATCHES))
sys.path.insert(0, str(TOOLS))

PREREGISTRATION = ANALYSIS / "winner_v12_calibrator_hold_diagnostic_preregistration.json"
FORMAL_RESULT = ANALYSIS / "winner_v12_calibrator_support_gate_result.json"
FULL_TRAINING_PREREGISTRATION = (
    ANALYSIS / "winner_v12_full_calibrator_training_preregistration.json"
)
DOMAIN = (
    ANALYSIS
    / "winner_v3_variable_configuration_replacement_preregistration.json"
)
CHECKPOINTS = (("half", 50), ("final", 100))
TICKS = 250
EXPECTED_AUXILIARY_INDICES = np.asarray(
    list(range(0, 6)) + list(range(13, 41)) + list(range(83, 99)),
    dtype=np.int64,
)
CONTACT_AUXILIARY_INDICES = np.asarray([48, 49], dtype=np.int64)
NONCONTACT_AUXILIARY_INDICES = np.arange(48, dtype=np.int64)


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
        raise ValueError("diagnostic source manifest is absent")
    for name, item in sources.items():
        if not isinstance(item, dict) or set(item) != {"hash_mode", "path", "sha256"}:
            raise ValueError(f"diagnostic source record changed: {name}")
        path = ROOT / item["path"]
        if item["hash_mode"] != "lf" or lf_sha256(path) != item["sha256"]:
            raise ValueError(f"diagnostic source changed: {name}")
    if canonical_sha256(sources) != preregistration.get("source_manifest_sha256"):
        raise ValueError("diagnostic source-manifest digest changed")


def auxiliary_group(auxiliary_index: int) -> str:
    if 0 <= auxiliary_index < 6:
        return "imu"
    if 6 <= auxiliary_index < 20:
        return "joint_position"
    if 20 <= auxiliary_index < 34:
        return "joint_velocity"
    if 34 <= auxiliary_index < 48:
        return "applied_target"
    if 48 <= auxiliary_index < 50:
        return "foot_contact"
    raise ValueError("auxiliary index is outside the frozen 50-D target")


def prediction_cell_statistics(
    *,
    observations: np.ndarray,
    predictions: np.ndarray,
    target_mean: np.ndarray,
    target_std: np.ndarray,
) -> dict[str, Any]:
    observations = np.asarray(observations, dtype=np.float32)
    predictions = np.asarray(predictions, dtype=np.float32)
    target_mean = np.asarray(target_mean, dtype=np.float32)
    target_std = np.asarray(target_std, dtype=np.float32)
    if observations.ndim != 2 or observations.shape[1] != 115:
        raise ValueError("diagnostic observations violate the 115-D contract")
    if predictions.ndim != 2 or predictions.shape[1] != 50:
        raise ValueError("diagnostic predictions violate the 50-D contract")
    if observations.shape[0] != predictions.shape[0] or observations.shape[0] < 2:
        raise ValueError("diagnostic adjacent-state population is invalid")
    if target_mean.shape != (50,) or target_std.shape != (50,):
        raise ValueError("diagnostic normalization violates the 50-D contract")
    if not (
        np.all(np.isfinite(observations))
        and np.all(np.isfinite(predictions))
        and np.all(np.isfinite(target_mean))
        and np.all(np.isfinite(target_std))
        and np.all(target_std > 0.0)
    ):
        raise ValueError("diagnostic predictor inputs are nonfinite or unscaled")

    # The frozen runner retained each pre-transition observation and prediction.
    # Adjacent retained observations therefore recover every target except the
    # final target of a full-duration cell; failed cells lose no valid target.
    target = observations[1:, EXPECTED_AUXILIARY_INDICES]
    prediction = predictions[:-1]
    learned_sq = np.square(
        (prediction.astype(np.float64) - target.astype(np.float64))
        / target_std.astype(np.float64)
    )
    baseline_sq = np.square(
        (target_mean.astype(np.float64) - target.astype(np.float64))
        / target_std.astype(np.float64)
    )
    contact_prediction = prediction[:, CONTACT_AUXILIARY_INDICES].astype(np.float64)
    contact_target = target[:, CONTACT_AUXILIARY_INDICES].astype(np.float64)
    return {
        "adjacent_transition_count": int(target.shape[0]),
        "learned_normalized_mse_per_dimension": np.mean(learned_sq, axis=0).tolist(),
        "constant_normalized_mse_per_dimension": np.mean(baseline_sq, axis=0).tolist(),
        "contact_prediction_sum": float(np.sum(contact_prediction)),
        "contact_prediction_count": int(contact_prediction.size),
        "contact_prediction_min": float(np.min(contact_prediction)),
        "contact_prediction_max": float(np.max(contact_prediction)),
        "contact_targets_exactly_one": bool(np.all(contact_target == 1.0)),
    }


def aggregate_prediction_statistics(
    cells: Sequence[Mapping[str, Any]],
    *,
    target_std: np.ndarray,
) -> dict[str, Any]:
    if not cells:
        raise ValueError("diagnostic predictor aggregate is empty")
    learned = np.asarray(
        [row["learned_normalized_mse_per_dimension"] for row in cells],
        dtype=np.float64,
    )
    baseline = np.asarray(
        [row["constant_normalized_mse_per_dimension"] for row in cells],
        dtype=np.float64,
    )
    if learned.shape[1:] != (50,) or baseline.shape != learned.shape:
        raise ValueError("diagnostic per-dimension predictor schema changed")
    learned_per_dimension = np.mean(learned, axis=0)
    baseline_per_dimension = np.mean(baseline, axis=0)
    learned_total = float(np.sum(learned_per_dimension))
    contact_total = float(np.sum(learned_per_dimension[CONTACT_AUXILIARY_INDICES]))
    count = sum(int(row["contact_prediction_count"]) for row in cells)
    if count <= 0:
        raise ValueError("diagnostic contact prediction population is empty")
    per_dimension = []
    for auxiliary_index, observation_index in enumerate(EXPECTED_AUXILIARY_INDICES):
        per_dimension.append(
            {
                "auxiliary_index": auxiliary_index,
                "observation_index": int(observation_index),
                "group": auxiliary_group(auxiliary_index),
                "target_std": float(target_std[auxiliary_index]),
                "learned_normalized_mse": float(learned_per_dimension[auxiliary_index]),
                "constant_normalized_mse": float(baseline_per_dimension[auxiliary_index]),
            }
        )
    return {
        "cell_count": len(cells),
        "adjacent_transition_count": sum(
            int(row["adjacent_transition_count"]) for row in cells
        ),
        "all_contact_targets_exactly_one": all(
            row["contact_targets_exactly_one"] for row in cells
        ),
        "contact_target_std_exactly_1e_6": bool(
            np.array_equal(
                np.asarray(target_std, dtype=np.float32)[CONTACT_AUXILIARY_INDICES],
                np.full((2,), np.float32(1.0e-6), dtype=np.float32),
            )
        ),
        "learned_normalized_mse_all_50": float(np.mean(learned_per_dimension)),
        "constant_normalized_mse_all_50": float(np.mean(baseline_per_dimension)),
        "learned_normalized_mse_noncontact_48": float(
            np.mean(learned_per_dimension[NONCONTACT_AUXILIARY_INDICES])
        ),
        "constant_normalized_mse_noncontact_48": float(
            np.mean(baseline_per_dimension[NONCONTACT_AUXILIARY_INDICES])
        ),
        "learned_noncontact_strictly_below_constant": bool(
            np.mean(learned_per_dimension[NONCONTACT_AUXILIARY_INDICES])
            < np.mean(baseline_per_dimension[NONCONTACT_AUXILIARY_INDICES])
        ),
        "contact_fraction_of_learned_normalized_sse": (
            contact_total / learned_total if learned_total > 0.0 else math.nan
        ),
        "contact_fraction_at_least_0_99": bool(
            learned_total > 0.0 and contact_total / learned_total >= 0.99
        ),
        "contact_prediction_mean": sum(
            float(row["contact_prediction_sum"]) for row in cells
        )
        / count,
        "contact_prediction_min": min(
            float(row["contact_prediction_min"]) for row in cells
        ),
        "contact_prediction_max": max(
            float(row["contact_prediction_max"]) for row in cells
        ),
        "per_dimension": per_dimension,
    }


def action_statistics(actions: np.ndarray) -> dict[str, Any]:
    values = np.asarray(actions, dtype=np.float32)
    if values.ndim != 2 or values.shape[1] != 14 or values.shape[0] < 1:
        raise ValueError("diagnostic actions violate the 14-D contract")
    if not np.all(np.isfinite(values)):
        raise ValueError("diagnostic actions are nonfinite")
    previous = np.vstack([np.zeros((1, 14), dtype=np.float32), values[:-1]])
    return {
        "tick_count": int(values.shape[0]),
        "all_zero": bool(np.array_equal(values, np.zeros_like(values))),
        "peak_abs_by_joint": np.max(np.abs(values), axis=0).astype(float).tolist(),
        "rms_by_joint": np.sqrt(np.mean(np.square(values), axis=0)).astype(float).tolist(),
        "peak_abs_step_by_joint": np.max(np.abs(values - previous), axis=0)
        .astype(float)
        .tolist(),
    }


class ZeroActionSession:
    """Retain the frozen graph's response state while forcing diagnostic home hold."""

    def __init__(self, session: Any) -> None:
        self.session = session

    def run(self, output_names: Sequence[str], inputs: Mapping[str, np.ndarray]):
        outputs = self.session.run(output_names, dict(inputs))
        action = np.zeros_like(np.asarray(outputs[0], dtype=np.float32))
        return [action, action.copy(), np.asarray(outputs[2], dtype=np.float32)]


def failed_configuration_ids(formal_result: Mapping[str, Any]) -> list[str]:
    values = {
        cell["configuration_id"]
        for checkpoint in formal_result["checkpoint_results"]
        for cell in checkpoint["core_model_plant_cells"]
        if cell["support_pass"] is False
    }
    return sorted(values)


def formal_cell_map(
    checkpoint: Mapping[str, Any],
) -> dict[tuple[str, str], Mapping[str, Any]]:
    cells = checkpoint["core_model_plant_cells"]
    result = {(row["configuration_id"], row["plant"]): row for row in cells}
    if len(result) != len(cells):
        raise ValueError("formal support result contains duplicate cells")
    return result


def outcome_matches_formal(
    diagnostic: Mapping[str, Any], formal: Mapping[str, Any]
) -> bool:
    diagnostic_terminal = diagnostic.get("terminal")
    formal_terminal = formal.get("terminal")
    return bool(
        diagnostic.get("support_pass") is formal.get("support_pass")
        and (None if diagnostic_terminal is None else diagnostic_terminal.get("tick"))
        == (None if formal_terminal is None else formal_terminal.get("tick"))
        and diagnostic.get("episode", {}).get("valid_ticks")
        == formal.get("episode", {}).get("valid_ticks")
    )


def public_support_summary(cell: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "support_pass": bool(cell["support_pass"]),
        "terminal": cell["terminal"],
        "episode": cell["episode"],
        "action_statistics": action_statistics(cell["_arrays"]["actions"]),
        "trace_hashes": cell["trace_hashes"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--training-work-root", type=Path, required=True)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--canonical-fit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--offline-cpu-only", action="store_true")
    parser.add_argument("--hold-diagnostic-authorized", action="store_true")
    args = parser.parse_args()
    if not args.offline_cpu_only or not args.hold_diagnostic_authorized:
        raise PermissionError(
            "HOLD diagnostic requires --offline-cpu-only "
            "--hold-diagnostic-authorized"
        )
    if args.output.exists():
        raise FileExistsError(f"refusing to overwrite HOLD diagnostic: {args.output}")

    import jax
    import mujoco
    import onnxruntime as ort
    import run_winner_v12_calibrator_cpu_smoke as smoke
    import run_winner_v12_calibrator_support_gate as gate
    import run_winner_v12_full_calibrator_training as full_training
    import winner_v12_calibrator_training as training

    if jax.default_backend() != "cpu" or any(
        device.platform != "cpu" for device in jax.devices()
    ):
        raise ValueError("HOLD diagnostic requires CPU-only JAX")
    if not np.array_equal(training.AUXILIARY_INDICES, EXPECTED_AUXILIARY_INDICES):
        raise ValueError("HOLD diagnostic auxiliary target indices changed")

    preregistration = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    if (
        preregistration.get("status")
        != "PREREGISTERED_WINNER_V12_CALIBRATOR_HOLD_DIAGNOSTIC"
        or preregistration.get("decision")
        != "AUTHORIZE_ONE_READ_ONLY_OFFLINE_HOLD_DIAGNOSTIC"
        or preregistration.get("execution_now")
        != {
            "diagnostic_cells": 0,
            "training_steps": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        }
    ):
        raise ValueError("HOLD diagnostic preregistration changed")
    validate_source_manifest(preregistration)

    formal_result = json.loads(FORMAL_RESULT.read_text(encoding="utf-8"))
    if (
        formal_result.get("status") != "HOLD_WINNER_V12_CALIBRATOR_SUPPORT_GATE"
        or formal_result.get("decision") != "DO_NOT_TRAIN_RESPONSE_CONDITIONED_LOCOMOTION"
        or formal_result.get("execution", {}).get("formal_support_cells") != 248
    ):
        raise ValueError("formal Winner-v12 HOLD evidence changed")
    expected_failed = preregistration["frozen_population"]["failed_configuration_ids"]
    if failed_configuration_ids(formal_result) != sorted(expected_failed):
        raise ValueError("formal Winner-v12 failed configuration population changed")

    full_preregistration = json.loads(
        FULL_TRAINING_PREREGISTRATION.read_text(encoding="utf-8")
    )
    calibrator_design = gate.load_calibrator_design(full_preregistration)
    domain = json.loads(DOMAIN.read_text(encoding="utf-8"))
    matrix = domain["evaluation_matrix"]
    configurations = (
        matrix["fixed_anchors"] + matrix["discovery_samples"] + matrix["heldout_samples"]
    )
    by_id = {row["id"]: row for row in configurations}
    heldout_ids = [row["id"] for row in matrix["heldout_samples"]]
    if heldout_ids != preregistration["frozen_population"]["heldout_configuration_ids"]:
        raise ValueError("HOLD diagnostic heldout population changed")
    graph_ids = preregistration["frozen_population"]["graph_configuration_ids"]
    if graph_ids != list(dict.fromkeys([*expected_failed, *heldout_ids])):
        raise ValueError("HOLD diagnostic graph population changed")
    if set(graph_ids) - set(by_id):
        raise ValueError("HOLD diagnostic configuration is absent from domain")

    scene = (
        args.playground_root
        / "playground/open_duck_mini_v2/xmls/scene_flat_terrain_backlash.xml"
    )
    if not scene.is_file():
        raise FileNotFoundError(scene)
    observer_type = smoke.load_runtime_observer(args.canonical_fit)
    options = ort.SessionOptions()
    options.intra_op_num_threads = 1
    options.inter_op_num_threads = 1
    options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL

    checkpoint_results = []
    for label, update in CHECKPOINTS:
        checkpoint_path, graph_path = gate.checkpoint_paths(args.training_work_root, label)
        snapshot = full_training.load_snapshot(checkpoint_path)
        full_training.validate_resume(snapshot)
        if (
            snapshot["metadata"]["stage"] != "stage2"
            or snapshot["metadata"]["completed_updates"] != update
        ):
            raise ValueError(f"{label} checkpoint boundary changed")
        target_mean = np.asarray(snapshot["target_mean"], dtype=np.float32)
        target_std = np.asarray(snapshot["target_std"], dtype=np.float32)
        session = ort.InferenceSession(
            str(graph_path), sess_options=options, providers=["CPUExecutionProvider"]
        )
        zero_session = ZeroActionSession(session)
        formal_checkpoint = next(
            row for row in formal_result["checkpoint_results"] if row["label"] == label
        )
        formal_cells = formal_cell_map(formal_checkpoint)
        graph_cells = []
        prediction_by_plant: dict[str, list[Mapping[str, Any]]] = {
            plant: [] for plant in smoke.PLANTS
        }
        for configuration_id in graph_ids:
            configuration = by_id[configuration_id]
            for plant in smoke.PLANTS:
                cell = gate.run_cell(
                    mujoco=mujoco,
                    scene=scene,
                    configuration=configuration,
                    plant=plant,
                    calibrator_design=calibrator_design,
                    observer_type=observer_type,
                    canonical_fit=args.canonical_fit,
                    session=session,
                    parameters=snapshot["parameters"],
                    target_mean=target_mean,
                    target_std=target_std,
                )
                matches = outcome_matches_formal(cell, formal_cells[(configuration_id, plant)])
                graph_cells.append(
                    {
                        "configuration_id": configuration_id,
                        "plant": plant,
                        "formal_outcome_match": matches,
                        **public_support_summary(cell),
                    }
                )
                if configuration_id in heldout_ids:
                    prediction_by_plant[plant].append(
                        prediction_cell_statistics(
                            observations=cell["_arrays"]["observations"],
                            predictions=cell["_arrays"]["predictions"],
                            target_mean=target_mean,
                            target_std=target_std,
                        )
                    )

        zero_action_cells = []
        for configuration_id in expected_failed:
            configuration = by_id[configuration_id]
            for plant in smoke.PLANTS:
                cell = gate.run_cell(
                    mujoco=mujoco,
                    scene=scene,
                    configuration=configuration,
                    plant=plant,
                    calibrator_design=calibrator_design,
                    observer_type=observer_type,
                    canonical_fit=args.canonical_fit,
                    session=zero_session,
                    parameters=snapshot["parameters"],
                    target_mean=target_mean,
                    target_std=target_std,
                )
                public = public_support_summary(cell)
                if not public["action_statistics"]["all_zero"]:
                    raise ValueError("diagnostic zero-action cell emitted a nonzero action")
                zero_action_cells.append(
                    {
                        "configuration_id": configuration_id,
                        "plant": plant,
                        **public,
                    }
                )

        predictor = {
            plant: aggregate_prediction_statistics(
                prediction_by_plant[plant], target_std=target_std
            )
            for plant in smoke.PLANTS
        }
        graph_failed = {
            (row["configuration_id"], row["plant"])
            for row in graph_cells
            if row["configuration_id"] in expected_failed and not row["support_pass"]
        }
        zero_passed = {
            (row["configuration_id"], row["plant"])
            for row in zero_action_cells
            if row["support_pass"]
        }
        expected_pairs = {
            (configuration_id, plant)
            for configuration_id in expected_failed
            for plant in smoke.PLANTS
        }
        classifications = {
            "graph_fail_zero_pass": sorted(
                [list(pair) for pair in graph_failed & zero_passed]
            ),
            "graph_fail_zero_fail": sorted(
                [list(pair) for pair in graph_failed - zero_passed]
            ),
            "graph_pass_zero_pass": sorted(
                [list(pair) for pair in (expected_pairs - graph_failed) & zero_passed]
            ),
            "graph_pass_zero_fail": sorted(
                [list(pair) for pair in (expected_pairs - graph_failed) - zero_passed]
            ),
        }
        checkpoint_results.append(
            {
                "label": label,
                "update": update,
                "checkpoint_sha256": gate.sha256(checkpoint_path),
                "onnx_sha256": gate.sha256(graph_path),
                "graph_cells": graph_cells,
                "zero_action_cells": zero_action_cells,
                "predictor_by_plant": predictor,
                "support_classification": classifications,
                "checks": {
                    "all_graph_outcomes_match_formal": all(
                        row["formal_outcome_match"] for row in graph_cells
                    ),
                    "all_zero_action_cells_exactly_zero": all(
                        row["action_statistics"]["all_zero"] for row in zero_action_cells
                    ),
                    "predictor_contact_targets_exactly_one": all(
                        row["all_contact_targets_exactly_one"]
                        for row in predictor.values()
                    ),
                    "predictor_contact_std_exactly_1e_6": all(
                        row["contact_target_std_exactly_1e_6"]
                        for row in predictor.values()
                    ),
                },
            }
        )

    all_predictor_rows = [
        row
        for checkpoint in checkpoint_results
        for row in checkpoint["predictor_by_plant"].values()
    ]
    graph_fail_zero_pass_count = sum(
        len(checkpoint["support_classification"]["graph_fail_zero_pass"])
        for checkpoint in checkpoint_results
    )
    graph_fail_zero_fail_count = sum(
        len(checkpoint["support_classification"]["graph_fail_zero_fail"])
        for checkpoint in checkpoint_results
    )
    checks = {
        "both_checkpoints_evaluated": [row["label"] for row in checkpoint_results]
        == ["half", "final"],
        "all_graph_outcomes_match_formal": all(
            checkpoint["checks"]["all_graph_outcomes_match_formal"]
            for checkpoint in checkpoint_results
        ),
        "all_zero_action_cells_exactly_zero": all(
            checkpoint["checks"]["all_zero_action_cells_exactly_zero"]
            for checkpoint in checkpoint_results
        ),
        "contact_floor_conditions_confirmed": all(
            row["all_contact_targets_exactly_one"]
            and row["contact_target_std_exactly_1e_6"]
            for row in all_predictor_rows
        ),
    }
    failed_checks = sorted(name for name, passed in checks.items() if not passed)
    result = {
        "schema_version": "winner_v12.calibrator_hold_diagnostic_result.v1",
        "status": (
            "PASS_WINNER_V12_CALIBRATOR_HOLD_DIAGNOSTIC"
            if not failed_checks
            else "INVALID_WINNER_V12_CALIBRATOR_HOLD_DIAGNOSTIC"
        ),
        "decision": "DIAGNOSTIC_ONLY_DO_NOT_TRAIN_OR_DEPLOY",
        "checks": checks,
        "failed_checks": failed_checks,
        "findings": {
            "contact_floor_dominates_all_predictor_aggregates": all(
                row["contact_fraction_at_least_0_99"] for row in all_predictor_rows
            ),
            "noncontact_predictor_beats_constant_all_aggregates": all(
                row["learned_noncontact_strictly_below_constant"]
                for row in all_predictor_rows
            ),
            "graph_fail_zero_pass_count": graph_fail_zero_pass_count,
            "graph_fail_zero_fail_count": graph_fail_zero_fail_count,
            "all_formal_failed_pairs_pass_with_zero_action": (
                graph_fail_zero_pass_count == 30 and graph_fail_zero_fail_count == 0
            ),
        },
        "checkpoint_results": checkpoint_results,
        "sources": {
            "preregistration_lf_sha256": lf_sha256(PREREGISTRATION),
            "formal_result_lf_sha256": lf_sha256(FORMAL_RESULT),
            "diagnostic_runner_lf_sha256": lf_sha256(Path(__file__)),
        },
        "execution": {
            "graph_diagnostic_cells": sum(
                len(row["graph_cells"]) for row in checkpoint_results
            ),
            "zero_action_diagnostic_cells": sum(
                len(row["zero_action_cells"]) for row in checkpoint_results
            ),
            "training_steps": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "robot_clearance": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "result_authorizes": "causal diagnosis and a separate prospective mechanism preregistration only",
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(result["status"])
    print(json.dumps(result["findings"], sort_keys=True))
    return 0 if not failed_checks else 1


if __name__ == "__main__":
    raise SystemExit(main())
