#!/usr/bin/env python3
"""Run the frozen Winner-v86 residual pitch-output diagnostic on CPU."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import types
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

import build_winner_v85_integrated_support_gate_preregistration as v85_builder  # noqa: E402
import build_winner_v86_residual_pitch_causal_preregistration as builder  # noqa: E402
import run_winner_v81_pitch_action_head_continuation as v81  # noqa: E402


PREREGISTRATION = ANALYSIS / "winner_v86_residual_pitch_causal_preregistration.json"
V85_RESULT = ANALYSIS / "winner_v85_integrated_support_gate_result.json"
V84_RESULT = ANALYSIS / "winner_v84_negative_gradient_pitch_head_continuation_result.json"
V84_PREREGISTRATION = (
    ANALYSIS / "winner_v84_negative_gradient_pitch_head_continuation_preregistration.json"
)
FULL_PREREGISTRATION = ANALYSIS / "winner_v12_full_calibrator_training_preregistration.json"
DOMAIN = ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
ARMS = builder.ARMS


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_preregistration(value: Mapping[str, Any]) -> None:
    frozen = value.get("frozen_source", {})
    if (
        value.get("schema_version") != "winner_v86.residual_pitch_causal_preregistration.v1"
        or value.get("status")
        != "PREREGISTERED_WINNER_V86_RESIDUAL_PITCH_CAUSAL_DIAGNOSTIC"
        or value.get("decision")
        != "AUTHORIZE_ONE_READ_ONLY_12_PAIR_FOUR_ARM_DIAGNOSTIC_ONLY"
        or frozen.get("v85_result_sha256") != builder.V85_RESULT_SHA256
        or frozen.get("failure_pair_count") != 12
        or frozen.get("arms") != list(ARMS)
        or frozen.get("diagnostic_cells") != 48
        or value.get("execution_now")
        != {
            "diagnostic_cells": 0,
            "optimizer_updates": 0,
            "locomotion_training_steps": 0,
            "robot_or_rdk_access": 0,
        }
    ):
        raise ValueError("Winner-v86 preregistration identity changed")
    sources = value.get("sources")
    if not isinstance(sources, Mapping) or not sources:
        raise ValueError("Winner-v86 source manifest absent")
    for name, item in sources.items():
        if (
            set(item) != {"hash_mode", "path", "sha256"}
            or item["hash_mode"] != "lf"
            or builder.lf_sha256(ROOT / item["path"]) != item["sha256"]
        ):
            raise ValueError(f"Winner-v86 source changed: {name}")
    if builder.canonical_sha256(sources) != value.get("source_manifest_sha256"):
        raise ValueError("Winner-v86 source manifest changed")


def configured_v85() -> tuple[Any, Any, Any]:
    import run_winner_v12_calibrator_cpu_smoke as smoke
    import run_winner_v12_calibrator_support_gate as gate
    import winner_v12_calibrator_training as training
    import winner_v21_predictor_preserving_joint_support as v21
    import winner_v22_normalized_predictor_v2 as v22v2
    import winner_v22_normalized_support_gate as normalized_support

    source, _ = v85_builder.transformed_source()
    module = types.ModuleType("winner_v86_reviewed_v85_gate")
    module.__file__ = str(ROOT / "tools/run_winner_v85_integrated_support_gate.py")
    exec(compile(source, module.__file__, "exec"), module.__dict__)
    module.smoke = smoke
    module.training = training
    module.v21 = v21
    module.v22v2 = v22v2
    module.normalized_support = normalized_support
    module._TRAINING = json.loads(V84_RESULT.read_text(encoding="utf-8"))
    module._TRAINING_PREREG = json.loads(V84_PREREGISTRATION.read_text(encoding="utf-8"))
    return smoke, gate, module


def formal_cell_map(checkpoint: Mapping[str, Any]) -> dict[tuple[str, str], Any]:
    cells = checkpoint["core_model_plant_cells"] + checkpoint["sensor_transport_plant_cells"]
    result = {(row["configuration_id"], row["plant"]): row for row in cells}
    if len(result) != len(cells):
        raise ValueError("Winner-v86 formal cell population contains duplicates")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--training-work-root", type=Path, required=True)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--canonical-fit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--offline-cpu-only", action="store_true")
    parser.add_argument("--causal-diagnostic-authorized", action="store_true")
    args = parser.parse_args()
    if not args.offline_cpu_only or not args.causal_diagnostic_authorized:
        raise PermissionError(
            "Winner-v86 requires --offline-cpu-only --causal-diagnostic-authorized"
        )
    if args.output.exists():
        raise FileExistsError("refusing to overwrite Winner-v86 evidence")

    import jax
    import mujoco
    import onnxruntime as ort
    import run_winner_v48_static_teacher_causal_diagnostic as v48

    if jax.default_backend() != "cpu" or any(
        device.platform != "cpu" for device in jax.devices()
    ):
        raise ValueError("Winner-v86 requires CPU-only JAX")
    preregistration = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    validate_preregistration(preregistration)
    formal = json.loads(V85_RESULT.read_text(encoding="utf-8"))
    if (
        sha256(V85_RESULT) != builder.V85_RESULT_SHA256
        or formal.get("status") != "HOLD_WINNER_V85_INTEGRATED_SUPPORT_GATE"
        or formal.get("selected_checkpoint") is not None
    ):
        raise ValueError("Winner-v86 formal source changed")
    smoke, gate, v85 = configured_v85()
    full_design = json.loads(FULL_PREREGISTRATION.read_text(encoding="utf-8"))
    calibrator_design = gate.load_calibrator_design(full_design)
    domain = json.loads(DOMAIN.read_text(encoding="utf-8"))
    matrix = domain["evaluation_matrix"]
    configurations = (
        matrix["fixed_anchors"] + matrix["discovery_samples"] + matrix["heldout_samples"]
    )
    by_id = {row["id"]: row for row in configurations}
    failure_pairs = preregistration["frozen_source"]["failure_pairs"]
    v80 = v81.v80_module()
    teacher_table = v80.complete_teacher_table()
    if any(
        row["configuration_id"] not in by_id
        or row["configuration_id"] not in teacher_table
        for row in failure_pairs
    ):
        raise ValueError("Winner-v86 frozen configuration is absent")
    scene = args.playground_root / smoke.SCENE_RELATIVE
    if not scene.is_file():
        raise FileNotFoundError(scene)
    if smoke.git_output(args.playground_root, "rev-parse", "HEAD") != smoke.CONTROL_COMMIT:
        raise ValueError("Winner-v86 Playground commit changed")
    smoke.validate_playground_tree(args.playground_root)
    if smoke.sha256(args.canonical_fit) != smoke.P30_FIT_LF_SHA256:
        raise ValueError("Winner-v86 canonical P30 fit changed")
    observer_type = smoke.load_runtime_observer(args.canonical_fit)
    options = ort.SessionOptions()
    options.intra_op_num_threads = 1
    options.inter_op_num_threads = 1
    options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL

    checkpoint_cache: dict[str, dict[str, Any]] = {}
    rows: list[dict[str, Any]] = []
    classifications: list[dict[str, Any]] = []
    for pair in failure_pairs:
        label = pair["checkpoint_label"]
        if label not in checkpoint_cache:
            checkpoint_path, graph_path = v85.checkpoint_paths(args.training_work_root, label)
            snapshot = v85.load_snapshot_for_reviewed_gate(checkpoint_path)
            v85.validate_snapshot_for_reviewed_gate(snapshot)
            session = ort.InferenceSession(
                str(graph_path), sess_options=options, providers=["CPUExecutionProvider"]
            )
            formal_checkpoint = next(
                row for row in formal["checkpoint_results"] if row["label"] == label
            )
            checkpoint_cache[label] = {
                "checkpoint_path": checkpoint_path,
                "graph_path": graph_path,
                "snapshot": snapshot,
                "session": session,
                "formal_cells": formal_cell_map(formal_checkpoint),
                "predictor": formal_checkpoint["heldout_prediction"],
            }
        cached = checkpoint_cache[label]
        snapshot = cached["snapshot"]
        configuration_id = pair["configuration_id"]
        plant = pair["plant"]
        raw_teacher = teacher_table[configuration_id]
        base_kwargs = {
            "mujoco": mujoco,
            "scene": scene,
            "configuration": by_id[configuration_id],
            "plant": plant,
            "calibrator_design": calibrator_design,
            "observer_type": observer_type,
            "canonical_fit": args.canonical_fit,
            "parameters": snapshot["parameters"],
            "target_mean": np.asarray(snapshot["target_mean"], dtype=np.float32),
            "target_std": np.asarray(snapshot["target_std"], dtype=np.float32),
        }
        graph_cell = gate.run_cell(session=cached["session"], **base_kwargs)
        formal_cell = cached["formal_cells"][(configuration_id, plant)]
        exact = gate.public_cell(graph_cell) == formal_cell
        if builder.canonical_sha256(formal_cell) != pair["formal_cell_sha256"]:
            raise ValueError("Winner-v86 frozen formal-cell digest changed")
        arms: dict[str, Any] = {"graph": v48.compact_cell(graph_cell)}
        for arm in ARMS[1:]:
            intervention = v48.InterventionSession(
                cached["session"],
                raw_teacher=raw_teacher,
                mode=arm,
                bounded_action=smoke.bounded_action_numpy,
            )
            arms[arm] = v48.compact_cell(gate.run_cell(session=intervention, **base_kwargs))
        classification = v48.classify_failed_pair(arms)
        classifications.append(
            {
                "checkpoint_label": label,
                "configuration_id": configuration_id,
                "plant": plant,
                "classification": classification,
            }
        )
        alignment = v48.action_alignment(
            graph_cell["_arrays"]["actions"], raw_teacher, smoke.bounded_action_numpy
        )
        post_rows = alignment["per_tick"][1:]
        alignment["first_tick_pitch_rms"] = alignment["per_tick"][0]["pitch_rms"]
        alignment["post_first_tick_pitch_rms_mean"] = (
            float(np.mean([row["pitch_rms"] for row in post_rows])) if post_rows else 0.0
        )
        rows.append(
            {
                "checkpoint_label": label,
                "checkpoint_update": pair["checkpoint_update"],
                "configuration_id": configuration_id,
                "plant": plant,
                "formal_graph_cell_bit_exact": exact,
                "raw_teacher_sha256": v48.array_sha256(raw_teacher),
                "action_alignment": alignment,
                "arms": arms,
            }
        )
    support_counts = {
        arm: sum(row["arms"][arm]["support_pass"] for row in rows) for arm in ARMS
    }
    classification_names = (
        "teacher_insufficient",
        "pitch_output_causal",
        "nonpitch_output_causal",
        "either_single_intervention_rescues",
        "pitch_nonpitch_interaction",
    )
    classification_counts = {
        name: sum(row["classification"] == name for row in classifications)
        for name in classification_names
    }
    all_cells = [cell for row in rows for cell in row["arms"].values()]
    checks = {
        "all_12_graph_cells_bit_exact_to_v85": all(
            row["formal_graph_cell_bit_exact"] for row in rows
        ),
        "all_12_source_graph_cells_fail": support_counts["graph"] == 0,
        "exact_48_cells": len(all_cells) == 48 and len(rows) == 12,
        "all_previous_action_chains_exact": all(
            cell["previous_action_chain_exact"] for cell in all_cells
        ),
        "all_jax_onnx_hidden_errors_at_most_1e_7": all(
            cell["maximum_jax_onnx_hidden_error"] <= 1.0e-7 for cell in all_cells
        ),
        "all_values_finite": all(
            math.isfinite(cell["maximum_jax_onnx_hidden_error"]) for cell in all_cells
        ),
    }
    failed_checks = sorted(name for name, passed in checks.items() if not passed)
    if failed_checks:
        raise ValueError(f"Winner-v86 diagnostic invalid: {failed_checks}")
    result = {
        "schema_version": "winner_v86.residual_pitch_causal_result.v1",
        "status": "PASS_WINNER_V86_RESIDUAL_PITCH_CAUSAL_DIAGNOSTIC",
        "decision": "SELECT_NEXT_MECHANISM_FROM_FROZEN_RESIDUAL_CLASSIFICATION_ONLY",
        "checks": {key: bool(value) for key, value in checks.items()},
        "failed_checks": [],
        "findings": {
            "support_pass_counts": support_counts,
            "classification_counts": classification_counts,
            "classification_rows": classifications,
            "first_tick_pitch_rms_mean": float(
                np.mean([row["action_alignment"]["first_tick_pitch_rms"] for row in rows])
            ),
            "post_first_tick_pitch_rms_mean": float(
                np.mean(
                    [
                        row["action_alignment"]["post_first_tick_pitch_rms_mean"]
                        for row in rows
                    ]
                )
            ),
            "predictor_failure_by_checkpoint": {
                label: checkpoint_cache[label]["predictor"] for label in ("half", "final")
            },
        },
        "cells": rows,
        "execution": {
            "diagnostic_cells": len(all_cells),
            "optimizer_updates": 0,
            "locomotion_training_steps": 0,
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
    print(f"support_counts={support_counts}")
    print(f"classification_counts={classification_counts}")
    print(f"sha256={sha256(args.output)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
