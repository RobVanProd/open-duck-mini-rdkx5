#!/usr/bin/env python3
"""Run the frozen Winner-v93 universal-response readout diagnostic."""

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

import build_winner_v93_universal_response_readout_preregistration as builder  # noqa: E402
import run_winner_v92_universal_target_response_observer as v92  # noqa: E402


PREREGISTRATION = ANALYSIS / "winner_v93_universal_response_readout_preregistration.json"
FULL_PREREGISTRATION = ANALYSIS / "winner_v12_full_calibrator_training_preregistration.json"
DOMAIN = ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_preregistration(value: Mapping[str, Any]) -> None:
    source = value.get("source", {})
    split = value.get("split", {})
    readout = value.get("readout", {})
    if (
        value.get("schema_version")
        != "winner_v93.universal_response_readout_preregistration.v1"
        or value.get("status")
        != "PREREGISTERED_WINNER_V93_UNIVERSAL_RESPONSE_READOUT"
        or source.get("snapshot_sha256") != builder.SNAPSHOT_SHA256
        or source.get("onnx_sha256") != builder.ONNX_SHA256
        or source.get("universal_target", {}).get("candidate_index") != 536
        or split.get("fit_configurations") != 40
        or split.get("heldout_configurations") != 16
        or split.get("fit_transitions") != 19920
        or split.get("heldout_transitions") != 7968
        or split.get("heldout_data_used_during_fit_or_selection") is not False
        or readout.get("feature_dimension") != 79
        or readout.get("target_dimension") != 50
        or readout.get("regularization") is not None
        or readout.get("hyperparameter_or_feature_search") is not False
        or readout.get("recurrent_parameters_changed") is not False
        or readout.get("policy_action_parameters_changed") is not False
        or readout.get("flat_transport_feature_enabled") is not False
        or value.get("execution_now")
        != {
            "source_trace_cells": 0,
            "least_squares_fits": 0,
            "optimizer_updates": 0,
            "snapshot_or_onnx_writes": 0,
            "robot_or_rdk_access": 0,
        }
    ):
        raise ValueError("Winner-v93 preregistration identity changed")
    sources = value.get("sources")
    if not isinstance(sources, Mapping) or not sources:
        raise ValueError("Winner-v93 source manifest absent")
    for name, item in sources.items():
        if (
            set(item) != {"hash_mode", "path", "sha256"}
            or item["hash_mode"] != "lf"
            or builder.lf_sha256(ROOT / item["path"]) != item["sha256"]
        ):
            raise ValueError(f"Winner-v93 source changed: {name}")
    if builder.canonical_sha256(sources) != value.get("source_manifest_sha256"):
        raise ValueError("Winner-v93 source manifest changed")


def feature_target_arrays(
    cell: Mapping[str, Any],
    target_mean: np.ndarray,
    target_std: np.ndarray,
    auxiliary_indices: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    arrays = cell["_arrays"]
    observations = np.asarray(arrays["observations"], dtype=np.float32)
    actions = np.asarray(arrays["actions"], dtype=np.float32)
    hidden = np.asarray(arrays["hidden"], dtype=np.float32)
    predictions = np.asarray(arrays["predictions"], dtype=np.float32)
    if (
        observations.shape != (250, 115)
        or actions.shape != (250, 14)
        or hidden.shape != (250, 64)
        or predictions.shape != (250, 50)
    ):
        raise ValueError("Winner-v93 source trace shape changed")
    features = np.concatenate(
        (
            hidden[:-1],
            actions[:-1],
            np.ones((249, 1), dtype=np.float32),
        ),
        axis=1,
    )
    target_raw = observations[1:, auxiliary_indices]
    target_normalized = (target_raw - target_mean) / target_std
    current_normalized = (predictions[:-1] - target_mean) / target_std
    if (
        features.shape != (249, 79)
        or target_normalized.shape != (249, 50)
        or current_normalized.shape != (249, 50)
    ):
        raise ValueError("Winner-v93 feature/target shape changed")
    return features, target_normalized, current_normalized


def mse(prediction: np.ndarray, target: np.ndarray) -> float:
    return float(
        np.mean(
            np.square(
                np.asarray(prediction, dtype=np.float64)
                - np.asarray(target, dtype=np.float64)
            )
        )
    )


def compact_cell(gate: Any, cell: Mapping[str, Any]) -> dict[str, Any]:
    value = gate.public_cell(cell)
    value.pop("learned_normalized_prediction_mse", None)
    value.pop("constant_normalized_prediction_mse", None)
    value.pop("final_h_out", None)
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--training-work-root", type=Path, required=True)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--canonical-fit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--offline-cpu-only", action="store_true")
    parser.add_argument("--formal-diagnostic-authorized", action="store_true")
    args = parser.parse_args()
    if not args.offline_cpu_only or not args.formal_diagnostic_authorized:
        raise PermissionError(
            "Winner-v93 requires --offline-cpu-only --formal-diagnostic-authorized"
        )
    if args.output.exists():
        raise FileExistsError("refusing to overwrite Winner-v93 evidence")

    import jax
    import mujoco
    import onnxruntime as ort
    import run_winner_v48_static_teacher_causal_diagnostic as v48

    if jax.default_backend() != "cpu" or any(
        device.platform != "cpu" for device in jax.devices()
    ):
        raise ValueError("Winner-v93 requires CPU-only JAX")
    preregistration = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    validate_preregistration(preregistration)
    smoke, gate, v22_gate = v92.configure_v22_gate()
    if smoke.git_output(args.playground_root, "rev-parse", "HEAD") != smoke.CONTROL_COMMIT:
        raise ValueError("Winner-v93 Playground commit changed")
    smoke.validate_playground_tree(args.playground_root)
    if smoke.sha256(args.canonical_fit) != smoke.P30_FIT_LF_SHA256:
        raise ValueError("Winner-v93 canonical P30 fit changed")
    full_design = json.loads(FULL_PREREGISTRATION.read_text(encoding="utf-8"))
    calibrator_design = gate.load_calibrator_design(full_design)
    domain = json.loads(DOMAIN.read_text(encoding="utf-8"))
    matrix = domain["evaluation_matrix"]
    fit_configurations = matrix["fixed_anchors"] + matrix["discovery_samples"]
    heldout_configurations = matrix["heldout_samples"]
    if len(fit_configurations) != 40 or len(heldout_configurations) != 16:
        raise ValueError("Winner-v93 configuration split changed")
    scene = args.playground_root / smoke.SCENE_RELATIVE
    observer_type = smoke.load_runtime_observer(args.canonical_fit)
    checkpoint_path, graph_path = v22_gate.checkpoint_paths(
        args.training_work_root, "final"
    )
    if (
        sha256(checkpoint_path) != builder.SNAPSHOT_SHA256
        or sha256(graph_path) != builder.ONNX_SHA256
    ):
        raise ValueError("Winner-v93 source artifact changed")
    snapshot = v22_gate.load_snapshot_for_reviewed_gate(checkpoint_path)
    v22_gate.validate_snapshot_for_reviewed_gate(snapshot)
    parameters = snapshot["parameters"]
    target_mean = np.asarray(snapshot["target_mean"], dtype=np.float32)
    target_std = np.asarray(snapshot["target_std"], dtype=np.float32)
    options = ort.SessionOptions()
    options.intra_op_num_threads = 1
    options.inter_op_num_threads = 1
    options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
    base_session = ort.InferenceSession(
        str(graph_path), sess_options=options, providers=["CPUExecutionProvider"]
    )
    raw_target = np.asarray(
        preregistration["source"]["universal_target"]["expanded_raw_action"],
        dtype=np.float32,
    )
    session = v48.InterventionSession(
        base_session,
        raw_teacher=raw_target,
        mode="full_teacher",
        bounded_action=smoke.bounded_action_numpy,
    )
    base_kwargs = {
        "mujoco": mujoco,
        "scene": scene,
        "calibrator_design": calibrator_design,
        "observer_type": observer_type,
        "canonical_fit": args.canonical_fit,
        "session": session,
        "parameters": parameters,
        "target_mean": target_mean,
        "target_std": target_std,
    }
    fit_cells: list[dict[str, Any]] = []
    heldout_cells: list[dict[str, Any]] = []
    for split, configurations in (
        (fit_cells, fit_configurations),
        (heldout_cells, heldout_configurations),
    ):
        for configuration in configurations:
            for plant in smoke.PLANTS:
                split.append(
                    gate.run_cell(
                        configuration=configuration,
                        plant=plant,
                        **base_kwargs,
                    )
                )
    fit_features = []
    fit_targets = []
    for cell in fit_cells:
        features, targets, _ = feature_target_arrays(
            cell, target_mean, target_std, gate.training.AUXILIARY_INDICES
        )
        fit_features.append(features)
        fit_targets.append(targets)
    design = np.concatenate(fit_features, axis=0).astype(np.float64)
    targets = np.concatenate(fit_targets, axis=0).astype(np.float64)
    coefficients64, residuals, rank, singular_values = np.linalg.lstsq(
        design, targets, rcond=None
    )
    coefficients = coefficients64.astype(np.float32)
    fitted_training_mse = mse(design.astype(np.float32) @ coefficients, targets)
    heldout_rows = []
    for cell in heldout_cells:
        features, target, current = feature_target_arrays(
            cell, target_mean, target_std, gate.training.AUXILIARY_INDICES
        )
        fitted = features @ coefficients
        heldout_rows.append(
            {
                "configuration_id": cell["configuration_id"],
                "plant": cell["plant"],
                "transition_count": 249,
                "fitted_normalized_prediction_mse": mse(fitted, target),
                "frozen_predictor_normalized_prediction_mse": mse(current, target),
                "constant_normalized_prediction_mse": mse(
                    np.zeros_like(target), target
                ),
            }
        )
    heldout_by_plant = {}
    for plant in smoke.PLANTS:
        rows = [row for row in heldout_rows if row["plant"] == plant]
        fitted = float(np.mean([row["fitted_normalized_prediction_mse"] for row in rows]))
        frozen = float(
            np.mean([row["frozen_predictor_normalized_prediction_mse"] for row in rows])
        )
        constant = float(
            np.mean([row["constant_normalized_prediction_mse"] for row in rows])
        )
        heldout_by_plant[plant] = {
            "configuration_count": len(rows),
            "transition_count": sum(row["transition_count"] for row in rows),
            "fitted_normalized_prediction_mse": fitted,
            "frozen_predictor_normalized_prediction_mse": frozen,
            "constant_normalized_prediction_mse": constant,
            "fitted_strictly_below_frozen": fitted < frozen,
            "fitted_strictly_below_constant": fitted < constant,
        }
    all_cells = fit_cells + heldout_cells
    checks = {
        "exact_112_source_trace_cells": len(all_cells) == 112,
        "all_source_trace_cells_pass_support": all(
            cell["support_pass"] for cell in all_cells
        ),
        "exact_19920_fit_transitions": design.shape == (19920, 79)
        and targets.shape == (19920, 50),
        "exact_7968_heldout_transitions": sum(
            row["transition_count"] for row in heldout_rows
        )
        == 7968,
        "one_float32_readout_fit": coefficients.shape == (79, 50)
        and coefficients.dtype == np.dtype(np.float32),
        "readout_and_metrics_finite": bool(np.all(np.isfinite(coefficients)))
        and math.isfinite(fitted_training_mse)
        and all(
            math.isfinite(value)
            for row in heldout_by_plant.values()
            for value in (
                row["fitted_normalized_prediction_mse"],
                row["frozen_predictor_normalized_prediction_mse"],
                row["constant_normalized_prediction_mse"],
            )
        ),
        "fitted_readout_beats_frozen_predictor_per_plant": all(
            row["fitted_strictly_below_frozen"] for row in heldout_by_plant.values()
        ),
        "fitted_readout_beats_constant_per_plant": all(
            row["fitted_strictly_below_constant"] for row in heldout_by_plant.values()
        ),
    }
    failed_checks = sorted(name for name, passed in checks.items() if not passed)
    passed = not failed_checks
    result = {
        "schema_version": "winner_v93.universal_response_readout_result.v1",
        "status": (
            "PASS_WINNER_V93_UNIVERSAL_RESPONSE_READOUT"
            if passed
            else "HOLD_WINNER_V93_UNIVERSAL_RESPONSE_READOUT"
        ),
        "classification": (
            "FROZEN_RECURRENT_STATE_HAS_HELDOUT_LINEAR_RESPONSE_SIGNAL"
            if passed
            else "FROZEN_RECURRENT_STATE_LINEAR_RESPONSE_SIGNAL_INSUFFICIENT"
        ),
        "decision": (
            "PREREGISTER_UNIVERSAL_ACTION_OBSERVER_CPU_CONTRACT"
            if passed
            else "DO_NOT_REFIT_ONLY_THE_AUXILIARY_READOUT"
        ),
        "checks": {name: bool(value) for name, value in checks.items()},
        "failed_checks": failed_checks,
        "fit": {
            "fit_configuration_count": len(fit_configurations),
            "fit_cell_count": len(fit_cells),
            "fit_transition_count": int(design.shape[0]),
            "feature_dimension": int(design.shape[1]),
            "target_dimension": int(targets.shape[1]),
            "rank": int(rank),
            "singular_values": singular_values.astype(float).tolist(),
            "solver_residual_sum": float(np.sum(residuals, dtype=np.float64)),
            "fitted_training_mse": fitted_training_mse,
            "coefficient_maximum_abs": float(np.max(np.abs(coefficients))),
            "coefficient_sha256": gate.array_sha256(coefficients),
            "coefficients_float32": coefficients.astype(float).tolist(),
        },
        "heldout_by_plant": heldout_by_plant,
        "heldout_cells": heldout_rows,
        "source_trace_cells": [compact_cell(gate, cell) for cell in all_cells],
        "normalization": {
            "target_mean_sha256": gate.array_sha256(target_mean),
            "target_std_sha256": gate.array_sha256(target_std),
        },
        "execution": {
            "source_trace_cells": len(all_cells),
            "least_squares_fits": 1,
            "optimizer_updates": 0,
            "snapshot_or_onnx_writes": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": preregistration["authority"],
        "sources": preregistration["sources"],
        "source_manifest_sha256": preregistration["source_manifest_sha256"],
    }
    args.output.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(result["status"])
    print(f"failed_checks={failed_checks}")
    print(f"rank={rank}")
    print(f"heldout={heldout_by_plant}")
    print(f"sha256={sha256(args.output)}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
