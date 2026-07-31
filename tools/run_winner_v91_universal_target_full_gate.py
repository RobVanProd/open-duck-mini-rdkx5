#!/usr/bin/env python3
"""Run the frozen Winner-v91 124-cell universal-target CPU gate."""

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

import build_winner_v91_universal_target_full_gate_preregistration as builder  # noqa: E402
import run_winner_v86_residual_pitch_causal as v86  # noqa: E402


PREREGISTRATION = ANALYSIS / "winner_v91_universal_target_full_gate_preregistration.json"
FULL_PREREGISTRATION = ANALYSIS / "winner_v12_full_calibrator_training_preregistration.json"
DOMAIN = ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_preregistration(value: Mapping[str, Any]) -> None:
    target = value.get("frozen_target", {})
    gate = value.get("gate", {})
    if (
        value.get("schema_version")
        != "winner_v91.universal_target_full_gate_preregistration.v1"
        or value.get("status") != "PREREGISTERED_WINNER_V91_UNIVERSAL_TARGET_FULL_GATE"
        or target.get("candidate_index") != 536
        or target.get("mirrored_coordinates") != [0.5, 0.25, 0.25]
        or target.get("expanded_raw_action") != list(builder.ACTION)
        or gate.get("core_model_plant_cells") != 112
        or gate.get("sensor_transport_plant_cells") != 12
        or gate.get("formal_cells") != 124
        or gate.get("duration_ticks") != 250
        or gate.get("predictor_or_context_selection") is not False
        or value.get("execution_now")
        != {
            "formal_support_cells": 0,
            "optimizer_updates": 0,
            "snapshot_or_onnx_writes": 0,
            "robot_or_rdk_access": 0,
        }
    ):
        raise ValueError("Winner-v91 preregistration identity changed")
    sources = value.get("sources")
    if not isinstance(sources, Mapping) or not sources:
        raise ValueError("Winner-v91 source manifest absent")
    for name, item in sources.items():
        if (
            set(item) != {"hash_mode", "path", "sha256"}
            or item["hash_mode"] != "lf"
            or builder.lf_sha256(ROOT / item["path"]) != item["sha256"]
        ):
            raise ValueError(f"Winner-v91 source changed: {name}")
    if builder.canonical_sha256(sources) != value.get("source_manifest_sha256"):
        raise ValueError("Winner-v91 source manifest changed")


def compact_cell(gate: Any, cell: Mapping[str, Any]) -> dict[str, Any]:
    public = gate.public_cell(cell)
    public.pop("learned_normalized_prediction_mse", None)
    public.pop("constant_normalized_prediction_mse", None)
    public.pop("final_h_out", None)
    return public


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
            "Winner-v91 requires --offline-cpu-only --formal-gate-authorized"
        )
    if args.output.exists():
        raise FileExistsError("refusing to overwrite Winner-v91 evidence")

    import jax
    import mujoco
    import onnxruntime as ort
    import run_winner_v48_static_teacher_causal_diagnostic as v48
    import winner_v43_static_target_teacher as v43

    if jax.default_backend() != "cpu" or any(
        device.platform != "cpu" for device in jax.devices()
    ):
        raise ValueError("Winner-v91 requires CPU-only JAX")
    preregistration = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    validate_preregistration(preregistration)
    smoke, gate, v85 = v86.configured_v85()
    if smoke.git_output(args.playground_root, "rev-parse", "HEAD") != smoke.CONTROL_COMMIT:
        raise ValueError("Winner-v91 Playground commit changed")
    smoke.validate_playground_tree(args.playground_root)
    if smoke.sha256(args.canonical_fit) != smoke.P30_FIT_LF_SHA256:
        raise ValueError("Winner-v91 canonical P30 fit changed")
    scene = args.playground_root / smoke.SCENE_RELATIVE
    observer_type = smoke.load_runtime_observer(args.canonical_fit)
    full_design = json.loads(FULL_PREREGISTRATION.read_text(encoding="utf-8"))
    calibrator_design = gate.load_calibrator_design(full_design)
    domain = json.loads(DOMAIN.read_text(encoding="utf-8"))
    matrix = domain["evaluation_matrix"]
    configurations = (
        matrix["fixed_anchors"] + matrix["discovery_samples"] + matrix["heldout_samples"]
    )
    conditions = full_design["future_frozen_support_gate"]["sensor_transport_population"]
    if len(configurations) != 56 or len(conditions) != 6:
        raise ValueError("Winner-v91 formal population changed")
    nominal = gate.nominal_configuration(mujoco, scene)
    checkpoint_path, graph_path = v85.checkpoint_paths(args.training_work_root, "half")
    snapshot = v85.load_snapshot_for_reviewed_gate(checkpoint_path)
    v85.validate_snapshot_for_reviewed_gate(snapshot)
    if int(np.asarray(snapshot["optimizer"]["count"])) != 705:
        raise ValueError("Winner-v91 instrumentation checkpoint changed")
    options = ort.SessionOptions()
    options.intra_op_num_threads = 1
    options.inter_op_num_threads = 1
    options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
    base_session = ort.InferenceSession(
        str(graph_path), sess_options=options, providers=["CPUExecutionProvider"]
    )
    raw_target = v43.expand_coordinates(builder.COORDINATES)
    if (
        raw_target.tolist() != list(builder.ACTION)
        or builder.array_sha256(raw_target)
        != preregistration["frozen_target"]["expanded_raw_action_sha256"]
    ):
        raise ValueError("Winner-v91 target expansion changed")
    session = v48.InterventionSession(
        base_session,
        raw_teacher=raw_target,
        mode="full_teacher",
        bounded_action=smoke.bounded_action_numpy,
    )
    parameters = snapshot["parameters"]
    target_mean = np.asarray(snapshot["target_mean"], dtype=np.float32)
    target_std = np.asarray(snapshot["target_std"], dtype=np.float32)
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
            core_cells.append(compact_cell(gate, cell))
    sensor_cells: list[dict[str, Any]] = []
    for condition_index, condition in enumerate(conditions):
        for plant_index, plant in enumerate(smoke.PLANTS):
            sequence = np.random.SeedSequence(
                [120120, 3, 0, condition_index, plant_index]
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
            public = compact_cell(gate, cell)
            public["prng"] = {
                "algorithm": "NumPy PCG64",
                "seed_sequence_entropy": [120120, 3, 0, condition_index, plant_index],
                "seed_sequence_state_u32": sequence.generate_state(4).astype(int).tolist(),
            }
            sensor_cells.append(public)
    all_cells = core_cells + sensor_cells
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
    checks = {
        "exact_112_core_cells": len(core_cells) == 112,
        "exact_12_sensor_transport_cells": len(sensor_cells) == 12,
        "all_124_support_cells_pass": len(all_cells) == 124
        and all(row["support_pass"] for row in all_cells),
        "all_previous_action_chains_exact": all(
            row["previous_action_chain_exact"] for row in all_cells
        ),
        "all_jax_onnx_hidden_errors_at_most_1e_7": all(
            row["maximum_jax_onnx_hidden_error"] <= 1.0e-7 for row in all_cells
        ),
        "all_requested_actions_match_bounded_universal_target": maximum_target_error == 0.0,
        "all_values_finite": all(
            math.isfinite(row["maximum_jax_onnx_hidden_error"]) for row in all_cells
        ),
    }
    failed_checks = sorted(name for name, passed in checks.items() if not passed)
    pass_gate = not failed_checks
    result = {
        "schema_version": "winner_v91.universal_target_full_gate_result.v1",
        "status": (
            "PASS_WINNER_V91_UNIVERSAL_TARGET_FULL_GATE"
            if pass_gate
            else "HOLD_WINNER_V91_UNIVERSAL_TARGET_FULL_GATE"
        ),
        "decision": (
            "PREREGISTER_UNIVERSAL_TARGET_POLICY_MECHANISM_CPU_CONTRACT"
            if pass_gate
            else "DO_NOT_USE_UNIVERSAL_TARGET_MECHANISM"
        ),
        "frozen_target": preregistration["frozen_target"],
        "instrumentation": {
            "checkpoint_label": "half",
            "checkpoint_update": 705,
            "checkpoint_sha256": sha256(checkpoint_path),
            "onnx_sha256": sha256(graph_path),
        },
        "checks": {key: bool(value) for key, value in checks.items()},
        "failed_checks": failed_checks,
        "failed_cells": failed_cells,
        "maximum_bounded_target_action_error": maximum_target_error,
        "core_model_plant_cells": core_cells,
        "sensor_transport_plant_cells": sensor_cells,
        "execution": {
            "formal_support_cells": len(all_cells),
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
