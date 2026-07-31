#!/usr/bin/env python3
"""Run the frozen Winner-v92 universal-target response-observer CPU gate."""

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

import build_winner_v92_universal_target_response_observer_preregistration as builder  # noqa: E402


PREREGISTRATION = (
    ANALYSIS / "winner_v92_universal_target_response_observer_preregistration.json"
)
FULL_PREREGISTRATION = ANALYSIS / "winner_v12_full_calibrator_training_preregistration.json"
DOMAIN = ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
V22_TRAINING_RESULT = ANALYSIS / "winner_v22_normalized_predictor_training_result.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_preregistration(value: Mapping[str, Any]) -> None:
    observer = value.get("source_observer", {})
    target = value.get("frozen_target", {})
    gate = value.get("gate", {})
    if (
        value.get("schema_version")
        != "winner_v92.universal_target_response_observer_preregistration.v1"
        or value.get("status")
        != "PREREGISTERED_WINNER_V92_UNIVERSAL_TARGET_RESPONSE_OBSERVER"
        or observer.get("label") != "final"
        or observer.get("update") != 100
        or observer.get("snapshot_sha256") != builder.SNAPSHOT_SHA256
        or observer.get("onnx_sha256") != builder.ONNX_SHA256
        or target.get("candidate_index") != 536
        or target.get("expanded_raw_action") != list(builder.ACTION)
        or gate.get("formal_support_cells") != 124
        or gate.get("heldout_repeat_cells") != 32
        or gate.get("duration_ticks") != 250
        or gate.get("sensor_prng_checkpoint_index") != 1
        or gate.get("checkpoint_or_candidate_selection_from_new_result") is not False
        or gate.get("flat_transport_feature_enabled") is not False
        or value.get("execution_now")
        != {
            "formal_support_cells": 0,
            "heldout_repeat_cells": 0,
            "optimizer_updates": 0,
            "snapshot_or_onnx_writes": 0,
            "robot_or_rdk_access": 0,
        }
    ):
        raise ValueError("Winner-v92 preregistration identity changed")
    sources = value.get("sources")
    if not isinstance(sources, Mapping) or not sources:
        raise ValueError("Winner-v92 source manifest absent")
    for name, item in sources.items():
        if (
            set(item) != {"hash_mode", "path", "sha256"}
            or item["hash_mode"] != "lf"
            or builder.lf_sha256(ROOT / item["path"]) != item["sha256"]
        ):
            raise ValueError(f"Winner-v92 source changed: {name}")
    if builder.canonical_sha256(sources) != value.get("source_manifest_sha256"):
        raise ValueError("Winner-v92 source manifest changed")


def configure_v22_gate() -> tuple[Any, Any, Any]:
    import run_winner_v12_calibrator_cpu_smoke as smoke
    import run_winner_v12_calibrator_support_gate as gate
    import winner_v12_calibrator_training as training
    import winner_v21_predictor_preserving_joint_support as v21
    import winner_v22_normalized_predictor_v2 as v22v2
    import winner_v22_normalized_support_gate as normalized_support
    import run_winner_v22_normalized_predictor_support_gate as v22_gate

    training_result = json.loads(V22_TRAINING_RESULT.read_text(encoding="utf-8"))
    if (
        sha256(V22_TRAINING_RESULT) != builder.V22_TRAINING_RESULT_SHA256
        or training_result.get("status")
        != "PASS_WINNER_V22_NORMALIZED_PREDICTOR_TRAINING_ARTIFACT"
        or training_result.get("failed_checks") != []
    ):
        raise ValueError("Winner-v22 training result changed")
    v22_gate.reviewed_gate = gate
    v22_gate.smoke = smoke
    v22_gate.training = training
    v22_gate.v21 = v21
    v22_gate.v22v2 = v22v2
    v22_gate.normalized_support = normalized_support
    v22_gate._TRAINING = training_result
    return smoke, gate, v22_gate


def public_cell(gate: Any, cell: Mapping[str, Any]) -> dict[str, Any]:
    return gate.public_cell(cell)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--training-work-root", type=Path, required=True)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--canonical-fit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--offline-cpu-only", action="store_true")
    parser.add_argument("--formal-gate-authorized", action="store_true")
    args = parser.parse_args()
    if not args.offline_cpu_only or not args.formal_gate_authorized:
        raise PermissionError(
            "Winner-v92 requires --offline-cpu-only --formal-gate-authorized"
        )
    if args.output.exists():
        raise FileExistsError("refusing to overwrite Winner-v92 evidence")

    import jax
    import mujoco
    import onnxruntime as ort
    import run_winner_v48_static_teacher_causal_diagnostic as v48
    import winner_v43_static_target_teacher as v43

    if jax.default_backend() != "cpu" or any(
        device.platform != "cpu" for device in jax.devices()
    ):
        raise ValueError("Winner-v92 requires CPU-only JAX")
    preregistration = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    validate_preregistration(preregistration)
    smoke, gate, v22_gate = configure_v22_gate()
    if smoke.git_output(args.playground_root, "rev-parse", "HEAD") != smoke.CONTROL_COMMIT:
        raise ValueError("Winner-v92 Playground commit changed")
    smoke.validate_playground_tree(args.playground_root)
    if smoke.sha256(args.canonical_fit) != smoke.P30_FIT_LF_SHA256:
        raise ValueError("Winner-v92 canonical P30 fit changed")
    full_design = json.loads(FULL_PREREGISTRATION.read_text(encoding="utf-8"))
    calibrator_design = gate.load_calibrator_design(full_design)
    domain = json.loads(DOMAIN.read_text(encoding="utf-8"))
    matrix = domain["evaluation_matrix"]
    configurations = (
        matrix["fixed_anchors"] + matrix["discovery_samples"] + matrix["heldout_samples"]
    )
    heldout_ids = {row["id"] for row in matrix["heldout_samples"]}
    conditions = full_design["future_frozen_support_gate"][
        "sensor_transport_population"
    ]
    if len(configurations) != 56 or len(heldout_ids) != 16 or len(conditions) != 6:
        raise ValueError("Winner-v92 formal population changed")
    scene = args.playground_root / smoke.SCENE_RELATIVE
    observer_type = smoke.load_runtime_observer(args.canonical_fit)
    nominal = gate.nominal_configuration(mujoco, scene)
    checkpoint_path, graph_path = v22_gate.checkpoint_paths(
        args.training_work_root, "final"
    )
    if (
        sha256(checkpoint_path) != builder.SNAPSHOT_SHA256
        or sha256(graph_path) != builder.ONNX_SHA256
    ):
        raise ValueError("Winner-v92 selected observer artifact changed")
    snapshot = v22_gate.load_snapshot_for_reviewed_gate(checkpoint_path)
    v22_gate.validate_snapshot_for_reviewed_gate(snapshot)
    if int(np.asarray(snapshot["optimizer"]["count"])) != 100:
        raise ValueError("Winner-v92 selected observer update changed")
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
    raw_target = v43.expand_coordinates((0.5, 0.25, 0.25))
    if raw_target.tolist() != list(builder.ACTION):
        raise ValueError("Winner-v92 target expansion changed")
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
    core_cells: list[dict[str, Any]] = []
    repeated_cells: list[dict[str, Any]] = []
    heldout_by_configuration: dict[str, dict[str, dict[str, Any]]] = {}
    maximum_target_error = 0.0
    for configuration in configurations:
        for plant in smoke.PLANTS:
            cell = gate.run_cell(configuration=configuration, plant=plant, **base_kwargs)
            alignment = v48.action_alignment(
                cell["_arrays"]["actions"], raw_target, smoke.bounded_action_numpy
            )
            maximum_target_error = max(
                maximum_target_error, float(alignment["all"]["maximum_abs"])
            )
            core_cells.append(public_cell(gate, cell))
            if configuration["id"] in heldout_ids:
                repeat = gate.run_cell(
                    configuration=configuration, plant=plant, **base_kwargs
                )
                repeated_cells.append(
                    {
                        "configuration_id": configuration["id"],
                        "plant": plant,
                        "bit_exact": gate.repeated_exact(cell, repeat),
                        "first_trace_hashes": cell["trace_hashes"],
                        "repeat_trace_hashes": repeat["trace_hashes"],
                    }
                )
                heldout_by_configuration.setdefault(configuration["id"], {})[
                    plant
                ] = cell
    sensor_cells: list[dict[str, Any]] = []
    for condition_index, condition in enumerate(conditions):
        for plant_index, plant in enumerate(smoke.PLANTS):
            sequence = np.random.SeedSequence(
                [120120, 3, 1, condition_index, plant_index]
            )
            rng = np.random.Generator(np.random.PCG64(sequence))
            cell = gate.run_cell(
                configuration=nominal,
                plant=plant,
                condition=condition,
                rng=rng,
                **base_kwargs,
            )
            alignment = v48.action_alignment(
                cell["_arrays"]["actions"], raw_target, smoke.bounded_action_numpy
            )
            maximum_target_error = max(
                maximum_target_error, float(alignment["all"]["maximum_abs"])
            )
            public = public_cell(gate, cell)
            public["prng"] = {
                "algorithm": "NumPy PCG64",
                "seed_sequence_entropy": [120120, 3, 1, condition_index, plant_index],
                "seed_sequence_state_u32": sequence.generate_state(4)
                .astype(int)
                .tolist(),
            }
            sensor_cells.append(public)
    context = []
    for configuration in matrix["heldout_samples"]:
        pair = heldout_by_configuration[configuration["id"]]
        left = pair[smoke.PLANTS[0]]
        right = pair[smoke.PLANTS[1]]
        separation = float(
            np.max(
                np.abs(
                    np.asarray(left["final_h_out"], dtype=np.float32)
                    - np.asarray(right["final_h_out"], dtype=np.float32)
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
    prediction_by_plant = {}
    for plant in smoke.PLANTS:
        rows = [
            heldout_by_configuration[configuration["id"]][plant]
            for configuration in matrix["heldout_samples"]
        ]
        learned = float(
            np.mean([row["learned_normalized_prediction_mse"] for row in rows])
        )
        constant = float(
            np.mean([row["constant_normalized_prediction_mse"] for row in rows])
        )
        prediction_by_plant[plant] = {
            "learned_normalized_prediction_mse": learned,
            "constant_normalized_prediction_mse": constant,
            "learned_strictly_below_constant": learned < constant,
        }
    all_cells = core_cells + sensor_cells
    checks = {
        "exact_124_formal_cells": len(all_cells) == 124,
        "all_124_support_cells_pass": all(row["support_pass"] for row in all_cells),
        "all_previous_action_chains_exact": all(
            row["previous_action_chain_exact"] for row in all_cells
        ),
        "all_jax_onnx_hidden_errors_at_most_1e_7": all(
            row["maximum_jax_onnx_hidden_error"] <= 1.0e-7 for row in all_cells
        ),
        "all_requested_actions_match_bounded_universal_target": (
            maximum_target_error == 0.0
        ),
        "all_32_heldout_repeats_bit_exact": len(repeated_cells) == 32
        and all(row["bit_exact"] for row in repeated_cells),
        "all_16_heldout_contexts_separate": len(context) == 16
        and all(row["separation_above_1e_7"] for row in context),
        "learned_prediction_beats_constant_per_plant": all(
            row["learned_strictly_below_constant"]
            for row in prediction_by_plant.values()
        ),
        "all_values_finite": all(
            math.isfinite(row["maximum_jax_onnx_hidden_error"]) for row in all_cells
        )
        and all(
            math.isfinite(value)
            for row in prediction_by_plant.values()
            for value in (
                row["learned_normalized_prediction_mse"],
                row["constant_normalized_prediction_mse"],
            )
        ),
    }
    failed_checks = sorted(name for name, passed in checks.items() if not passed)
    failed_cells = [
        {
            "configuration_id": row["configuration_id"],
            "plant": row["plant"],
            "condition": row["condition"],
            "terminal": row["terminal"],
        }
        for row in all_cells
        if not row["support_pass"]
    ]
    passed = not failed_checks
    result = {
        "schema_version": "winner_v92.universal_target_response_observer_result.v1",
        "status": (
            "PASS_WINNER_V92_UNIVERSAL_TARGET_RESPONSE_OBSERVER"
            if passed
            else "HOLD_WINNER_V92_UNIVERSAL_TARGET_RESPONSE_OBSERVER"
        ),
        "decision": (
            "PREREGISTER_RESPONSE_CONDITIONED_LOCOMOTION_CPU_CONTRACT"
            if passed
            else "DO_NOT_USE_UNIVERSAL_TARGET_RESPONSE_OBSERVER"
        ),
        "source_observer": preregistration["source_observer"],
        "frozen_target": preregistration["frozen_target"],
        "checks": {name: bool(value) for name, value in checks.items()},
        "failed_checks": failed_checks,
        "failed_cells": failed_cells,
        "maximum_bounded_target_action_error": maximum_target_error,
        "heldout_prediction": prediction_by_plant,
        "heldout_context_separation": context,
        "heldout_repeatability": repeated_cells,
        "core_model_plant_cells": core_cells,
        "sensor_transport_plant_cells": sensor_cells,
        "execution": {
            "formal_support_cells": len(all_cells),
            "heldout_repeat_cells": len(repeated_cells),
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
    print(f"failed_cells={len(failed_cells)}")
    print(f"sha256={sha256(args.output)}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
