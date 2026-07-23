#!/usr/bin/env python3
"""Run the frozen Winner-v95 precision-truncated response readout contract."""

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

import build_winner_v95_precision_truncated_readout_preregistration as builder  # noqa: E402
import run_winner_v94_stable_response_readout as v94  # noqa: E402


PREREGISTRATION = ANALYSIS / "winner_v95_precision_truncated_readout_preregistration.json"
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
        != "winner_v95.precision_truncated_readout_preregistration.v1"
        or value.get("status")
        != "PREREGISTERED_WINNER_V95_PRECISION_TRUNCATED_READOUT"
        or source.get("snapshot_sha256") != builder.SNAPSHOT_SHA256
        or source.get("onnx_sha256") != builder.ONNX_SHA256
        or source.get("universal_target_candidate") != 536
        or source.get("universal_target_action") != list(builder.ACTION)
        or split.get("fit_configurations") != 40
        or split.get("heldout_configurations") != 16
        or split.get("fit_transitions") != 19920
        or split.get("heldout_transitions") != 7968
        or split.get("heldout_data_used_during_fit_or_rank_selection") is not False
        or readout.get("feature_order") != ["h_out[0:64]", "bias"]
        or readout.get("feature_dimension") != 65
        or readout.get("target_dimension") != 50
        or readout.get("float32_epsilon") != builder.FLOAT32_EPSILON
        or readout.get("condition_limit") != builder.CONDITION_LIMIT
        or readout.get("relative_singular_value_cutoff")
        != builder.RELATIVE_SINGULAR_VALUE_CUTOFF
        or readout.get("condition_number_times_float32_epsilon_at_most")
        != builder.AMPLIFICATION_LIMIT
        or readout.get("heldout_float64_vs_float32_max_abs_at_most")
        != builder.PREDICTION_DELTA_LIMIT
        or readout.get("regularization") is not None
        or readout.get("hyperparameter_rank_or_feature_search") is not False
        or readout.get("recurrent_parameters_changed") is not False
        or readout.get("policy_action_parameters_changed") is not False
        or readout.get("flat_transport_feature_enabled") is not False
        or value.get("execution_now")
        != {
            "source_trace_cells": 0,
            "svd_fits": 0,
            "optimizer_updates": 0,
            "snapshot_or_onnx_writes": 0,
            "robot_or_rdk_access": 0,
        }
    ):
        raise ValueError("Winner-v95 preregistration identity changed")
    sources = value.get("sources")
    if not isinstance(sources, Mapping) or not sources:
        raise ValueError("Winner-v95 source manifest absent")
    for name, item in sources.items():
        if (
            set(item) != {"hash_mode", "path", "sha256"}
            or item["hash_mode"] != "lf"
            or builder.lf_sha256(ROOT / item["path"]) != item["sha256"]
        ):
            raise ValueError(f"Winner-v95 source changed: {name}")
    if builder.canonical_sha256(sources) != value.get("source_manifest_sha256"):
        raise ValueError("Winner-v95 source manifest changed")


def truncated_svd_fit(
    design: np.ndarray, targets: np.ndarray
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    u, singular_values, vt = np.linalg.svd(design, full_matrices=False)
    retained = singular_values >= (
        singular_values[0] * builder.RELATIVE_SINGULAR_VALUE_CUTOFF
    )
    if not np.any(retained):
        raise ValueError("Winner-v95 precision rule retained no singular direction")
    coefficients = (
        (vt[retained].T / singular_values[retained])
        @ (u[:, retained].T @ targets)
    )
    return coefficients, singular_values, retained


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--training-work-root", type=Path, required=True)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--canonical-fit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--offline-cpu-only", action="store_true")
    parser.add_argument("--formal-contract-authorized", action="store_true")
    args = parser.parse_args()
    if not args.offline_cpu_only or not args.formal_contract_authorized:
        raise PermissionError(
            "Winner-v95 requires --offline-cpu-only --formal-contract-authorized"
        )
    if args.output.exists():
        raise FileExistsError("refusing to overwrite Winner-v95 evidence")

    import jax
    import mujoco
    import onnxruntime as ort
    import run_winner_v48_static_teacher_causal_diagnostic as v48

    if jax.default_backend() != "cpu" or any(
        device.platform != "cpu" for device in jax.devices()
    ):
        raise ValueError("Winner-v95 requires CPU-only JAX")
    preregistration = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    validate_preregistration(preregistration)
    smoke, gate, v22_gate = v94.v93.v92.configure_v22_gate()
    if smoke.git_output(args.playground_root, "rev-parse", "HEAD") != smoke.CONTROL_COMMIT:
        raise ValueError("Winner-v95 Playground commit changed")
    smoke.validate_playground_tree(args.playground_root)
    if smoke.sha256(args.canonical_fit) != smoke.P30_FIT_LF_SHA256:
        raise ValueError("Winner-v95 canonical P30 fit changed")
    full_design = json.loads(FULL_PREREGISTRATION.read_text(encoding="utf-8"))
    calibrator_design = gate.load_calibrator_design(full_design)
    matrix = json.loads(DOMAIN.read_text(encoding="utf-8"))["evaluation_matrix"]
    fit_configurations = matrix["fixed_anchors"] + matrix["discovery_samples"]
    heldout_configurations = matrix["heldout_samples"]
    if len(fit_configurations) != 40 or len(heldout_configurations) != 16:
        raise ValueError("Winner-v95 configuration split changed")
    scene = args.playground_root / smoke.SCENE_RELATIVE
    observer_type = smoke.load_runtime_observer(args.canonical_fit)
    checkpoint_path, graph_path = v22_gate.checkpoint_paths(
        args.training_work_root, "final"
    )
    if (
        sha256(checkpoint_path) != builder.SNAPSHOT_SHA256
        or sha256(graph_path) != builder.ONNX_SHA256
    ):
        raise ValueError("Winner-v95 source artifact changed")
    snapshot = v22_gate.load_snapshot_for_reviewed_gate(checkpoint_path)
    v22_gate.validate_snapshot_for_reviewed_gate(snapshot)
    target_mean = np.asarray(snapshot["target_mean"], dtype=np.float32)
    target_std = np.asarray(snapshot["target_std"], dtype=np.float32)
    options = ort.SessionOptions()
    options.intra_op_num_threads = 1
    options.inter_op_num_threads = 1
    options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
    base_session = ort.InferenceSession(
        str(graph_path), sess_options=options, providers=["CPUExecutionProvider"]
    )
    session = v48.InterventionSession(
        base_session,
        raw_teacher=np.asarray(builder.ACTION, dtype=np.float32),
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
        "parameters": snapshot["parameters"],
        "target_mean": target_mean,
        "target_std": target_std,
    }
    fit_cells: list[dict[str, Any]] = []
    heldout_cells: list[dict[str, Any]] = []
    for destination, configurations in (
        (fit_cells, fit_configurations),
        (heldout_cells, heldout_configurations),
    ):
        for configuration in configurations:
            for plant in smoke.PLANTS:
                destination.append(
                    gate.run_cell(
                        configuration=configuration,
                        plant=plant,
                        **base_kwargs,
                    )
                )
    auxiliary_indices = gate.training.AUXILIARY_INDICES
    fit_features = []
    fit_targets = []
    for cell in fit_cells:
        features, target, _ = v94.stable_arrays(
            cell, target_mean, target_std, auxiliary_indices
        )
        fit_features.append(features)
        fit_targets.append(target)
    design64 = np.concatenate(fit_features, axis=0).astype(np.float64)
    targets64 = np.concatenate(fit_targets, axis=0).astype(np.float64)
    coefficients64, singular_values, retained = truncated_svd_fit(design64, targets64)
    coefficients32 = coefficients64.astype(np.float32)
    retained_values = singular_values[retained]
    retained_condition = float(retained_values[0] / retained_values[-1])
    amplification = retained_condition * builder.FLOAT32_EPSILON
    heldout_rows = []
    maximum_precision_delta = 0.0
    for cell in heldout_cells:
        features, target, frozen = v94.stable_arrays(
            cell, target_mean, target_std, auxiliary_indices
        )
        prediction64 = features.astype(np.float64) @ coefficients64
        prediction32 = features @ coefficients32
        maximum_precision_delta = max(
            maximum_precision_delta,
            float(np.max(np.abs(prediction64 - prediction32.astype(np.float64)))),
        )
        heldout_rows.append(
            {
                "configuration_id": cell["configuration_id"],
                "plant": cell["plant"],
                "transition_count": 249,
                "fitted_float32_normalized_prediction_mse": v94.v93.mse(
                    prediction32, target
                ),
                "frozen_predictor_normalized_prediction_mse": v94.v93.mse(
                    frozen, target
                ),
                "constant_normalized_prediction_mse": v94.v93.mse(
                    np.zeros_like(target), target
                ),
            }
        )
    heldout_by_plant = {}
    for plant in smoke.PLANTS:
        rows = [row for row in heldout_rows if row["plant"] == plant]
        fitted = float(
            np.mean(
                [row["fitted_float32_normalized_prediction_mse"] for row in rows]
            )
        )
        frozen = float(
            np.mean([row["frozen_predictor_normalized_prediction_mse"] for row in rows])
        )
        constant = float(
            np.mean([row["constant_normalized_prediction_mse"] for row in rows])
        )
        heldout_by_plant[plant] = {
            "configuration_count": len(rows),
            "transition_count": sum(row["transition_count"] for row in rows),
            "fitted_float32_normalized_prediction_mse": fitted,
            "frozen_predictor_normalized_prediction_mse": frozen,
            "constant_normalized_prediction_mse": constant,
            "fitted_strictly_below_frozen": fitted < frozen,
            "fitted_strictly_below_constant": fitted < constant,
        }
    action_weight = np.zeros((14, 50), dtype=np.float32)
    hidden_weight = coefficients32[:64]
    bias = coefficients32[64]
    all_cells = fit_cells + heldout_cells
    checks = {
        "exact_112_source_trace_cells": len(all_cells) == 112,
        "all_source_trace_cells_pass_support": all(
            cell["support_pass"] for cell in all_cells
        ),
        "exact_fit_and_heldout_transition_counts": design64.shape == (19920, 65)
        and targets64.shape == (19920, 50)
        and sum(row["transition_count"] for row in heldout_rows) == 7968,
        "precision_rule_retains_at_least_one_direction": int(np.sum(retained)) > 0,
        "retained_condition_amplification_at_most_1e_minus_3": (
            amplification <= builder.AMPLIFICATION_LIMIT
        ),
        "heldout_float64_float32_delta_at_most_1e_minus_4": (
            maximum_precision_delta <= builder.PREDICTION_DELTA_LIMIT
        ),
        "float32_readout_finite": bool(np.all(np.isfinite(coefficients32)))
        and math.isfinite(retained_condition)
        and math.isfinite(maximum_precision_delta),
        "action_weight_is_exact_zero": bool(
            np.array_equal(action_weight, np.zeros_like(action_weight))
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
        "schema_version": "winner_v95.precision_truncated_readout_result.v1",
        "status": (
            "PASS_WINNER_V95_PRECISION_TRUNCATED_READOUT"
            if passed
            else "HOLD_WINNER_V95_PRECISION_TRUNCATED_READOUT"
        ),
        "decision": (
            "PREREGISTER_RESPONSE_CONDITIONED_LOCOMOTION_CPU_CONTRACT"
            if passed
            else "DO_NOT_SELECT_PRECISION_TRUNCATED_READOUT"
        ),
        "checks": {name: bool(value) for name, value in checks.items()},
        "failed_checks": failed_checks,
        "fit": {
            "fit_configuration_count": len(fit_configurations),
            "fit_cell_count": len(fit_cells),
            "fit_transition_count": int(design64.shape[0]),
            "feature_dimension": int(design64.shape[1]),
            "target_dimension": int(targets64.shape[1]),
            "original_rank": int(np.linalg.matrix_rank(design64)),
            "retained_rank": int(np.sum(retained)),
            "retained_mask": retained.astype(bool).tolist(),
            "singular_values": singular_values.astype(float).tolist(),
            "retained_condition_number": retained_condition,
            "condition_number_times_float32_epsilon": amplification,
            "relative_singular_value_cutoff": builder.RELATIVE_SINGULAR_VALUE_CUTOFF,
            "heldout_float64_float32_maximum_abs": maximum_precision_delta,
            "coefficient_maximum_abs": float(np.max(np.abs(coefficients32))),
            "combined_coefficient_sha256": gate.array_sha256(coefficients32),
        },
        "readout": {
            "auxiliary_hidden_weight": hidden_weight.astype(float).tolist(),
            "auxiliary_action_weight": action_weight.astype(float).tolist(),
            "auxiliary_bias": bias.astype(float).tolist(),
            "auxiliary_hidden_weight_sha256": gate.array_sha256(hidden_weight),
            "auxiliary_action_weight_sha256": gate.array_sha256(action_weight),
            "auxiliary_bias_sha256": gate.array_sha256(bias),
        },
        "heldout_by_plant": heldout_by_plant,
        "heldout_cells": heldout_rows,
        "source_trace_cells": [
            v94.v93.compact_cell(gate, cell) for cell in all_cells
        ],
        "normalization": {
            "target_mean_sha256": gate.array_sha256(target_mean),
            "target_std_sha256": gate.array_sha256(target_std),
        },
        "execution": {
            "source_trace_cells": len(all_cells),
            "svd_fits": 1,
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
    print(
        f"rank={int(np.sum(retained))} condition={retained_condition} "
        f"amplification={amplification}"
    )
    print(f"precision_delta={maximum_precision_delta}")
    print(f"heldout={heldout_by_plant}")
    print(f"sha256={sha256(args.output)}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
