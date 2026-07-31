#!/usr/bin/env python3
"""Run the frozen V54 residual-teacher causal diagnostic on CPU."""

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

PREREGISTRATION = ANALYSIS / "winner_v54_residual_teacher_causal_preregistration.json"
V53_RESULT = ANALYSIS / "winner_v53_full_action_teacher_support_gate_result.json"
V52_RESULT = ANALYSIS / "winner_v52_full_action_teacher_training_result.json"
V52_PREREGISTRATION = ANALYSIS / "winner_v52_full_action_teacher_training_preregistration.json"
V42_RESULT = ANALYSIS / "winner_v42_static_target_teacher_table_result.json"
FULL_TRAINING_PREREGISTRATION = ANALYSIS / "winner_v12_full_calibrator_training_preregistration.json"
DOMAIN = ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
ARMS = ("graph", "full_teacher", "pitch_teacher", "nonpitch_zero")


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


def validate_preregistration(value: Mapping[str, Any]) -> None:
    if (
        value.get("schema_version")
        != "winner_v54.residual_teacher_causal_preregistration.v1"
        or value.get("status")
        != "PREREGISTERED_WINNER_V54_RESIDUAL_TEACHER_CAUSAL_DIAGNOSTIC"
        or value.get("decision")
        != "AUTHORIZE_ONE_READ_ONLY_48_CELL_CPU_DIAGNOSTIC_ONLY"
        or value.get("frozen_source", {}).get("configuration_ids")
        != [
            "COM_X_NEG",
            "COM_CORNER_01",
            "COM_CORNER_03",
            "DISCOVERY_03",
            "HELDOUT_04",
            "HELDOUT_09",
        ]
        or value.get("frozen_execution")
        != {
            "checkpoint_count": 1,
            "configuration_count": 6,
            "plant_count": 2,
            "arm_count": 4,
            "diagnostic_cells": 48,
            "ticks_per_cell": 250,
            "formal_graph_cells_must_match_v53_bit_exact": True,
            "optimizer_updates": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        }
        or value.get("execution_now")
        != {
            "diagnostic_cells": 0,
            "optimizer_updates": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        }
    ):
        raise ValueError("Winner-v54 preregistration identity changed")
    sources = value.get("sources")
    if not isinstance(sources, dict) or not sources:
        raise ValueError("Winner-v54 source manifest is absent")
    for name, item in sources.items():
        if (
            set(item) != {"hash_mode", "path", "sha256"}
            or item["hash_mode"] != "lf"
            or lf_sha256(ROOT / item["path"]) != item["sha256"]
        ):
            raise ValueError(f"Winner-v54 source changed: {name}")
    if canonical_sha256(sources) != value.get("source_manifest_sha256"):
        raise ValueError("Winner-v54 source manifest changed")


def configure_v53_modules() -> tuple[Any, ...]:
    import run_winner_v12_calibrator_cpu_smoke as smoke
    import run_winner_v12_calibrator_support_gate as gate
    import run_winner_v53_full_action_teacher_support_gate as v53
    import winner_v12_calibrator_training as training
    import winner_v21_predictor_preserving_joint_support as v21
    import winner_v22_normalized_predictor_v2 as v22v2
    import winner_v22_normalized_support_gate as normalized_support

    v53.smoke = smoke
    v53.training = training
    v53.v21 = v21
    v53.v22v2 = v22v2
    v53.normalized_support = normalized_support
    v53._TRAINING = json.loads(V52_RESULT.read_text(encoding="utf-8"))
    v53._TRAINING_PREREG = json.loads(V52_PREREGISTRATION.read_text(encoding="utf-8"))
    return smoke, gate, v53


def formal_cell_map(checkpoint: Mapping[str, Any]) -> dict[tuple[str, str], Any]:
    cells = checkpoint["core_model_plant_cells"]
    result = {(row["configuration_id"], row["plant"]): row for row in cells}
    if len(result) != len(cells):
        raise ValueError("Winner-v54 formal cell population contains duplicates")
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--training-work-root", type=Path, required=True)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--canonical-fit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--markdown", type=Path)
    parser.add_argument("--offline-cpu-only", action="store_true")
    parser.add_argument("--causal-diagnostic-authorized", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if not args.offline_cpu_only or not args.causal_diagnostic_authorized:
        raise PermissionError(
            "Winner-v54 requires --offline-cpu-only --causal-diagnostic-authorized"
        )
    if args.output.exists():
        raise FileExistsError(f"refusing to overwrite Winner-v54 result: {args.output}")
    markdown = args.markdown or args.output.with_suffix(".md")
    if markdown.exists():
        raise FileExistsError(f"refusing to overwrite Winner-v54 summary: {markdown}")

    import jax
    import mujoco
    import onnxruntime as ort
    import run_winner_v48_static_teacher_causal_diagnostic as v48
    import winner_v43_static_target_teacher as v43

    if jax.default_backend() != "cpu" or any(
        device.platform != "cpu" for device in jax.devices()
    ):
        raise ValueError("Winner-v54 requires CPU-only JAX")
    preregistration = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    validate_preregistration(preregistration)
    formal = json.loads(V53_RESULT.read_text(encoding="utf-8"))
    if (
        formal.get("status") != "HOLD_WINNER_V53_FULL_ACTION_TEACHER_SUPPORT_GATE"
        or formal.get("selected_checkpoint") is not None
        or sha256(V53_RESULT) != preregistration["frozen_source"]["v53_result_sha256"]
    ):
        raise ValueError("Winner-v54 formal source changed")
    smoke, gate, v53 = configure_v53_modules()
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
    configuration_ids = preregistration["frozen_source"]["configuration_ids"]
    teacher_table = v43.load_teacher_table(
        json.loads(V42_RESULT.read_text(encoding="utf-8"))
    )
    if set(configuration_ids) - set(by_id) or set(configuration_ids) - set(teacher_table):
        raise ValueError("Winner-v54 frozen configuration is absent")
    scene = args.playground_root / smoke.SCENE_RELATIVE
    if not scene.is_file():
        raise FileNotFoundError(scene)
    if smoke.git_output(args.playground_root, "rev-parse", "HEAD") != smoke.CONTROL_COMMIT:
        raise ValueError("Winner-v54 Playground commit changed")
    smoke.validate_playground_tree(args.playground_root)
    if smoke.sha256(args.canonical_fit) != smoke.P30_FIT_LF_SHA256:
        raise ValueError("Winner-v54 canonical P30 fit changed")
    observer_type = smoke.load_runtime_observer(args.canonical_fit)
    options = ort.SessionOptions()
    options.intra_op_num_threads = 1
    options.inter_op_num_threads = 1
    options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL

    checkpoint_path, graph_path = v53.checkpoint_paths(args.training_work_root, "final")
    snapshot = v53.load_snapshot_for_reviewed_gate(checkpoint_path)
    v53.validate_snapshot_for_reviewed_gate(snapshot)
    if snapshot["metadata"]["completed_updates"] != 453:
        raise ValueError("Winner-v54 checkpoint boundary changed")
    session = ort.InferenceSession(
        str(graph_path), sess_options=options, providers=["CPUExecutionProvider"]
    )
    target_mean = np.asarray(snapshot["target_mean"], dtype=np.float32)
    target_std = np.asarray(snapshot["target_std"], dtype=np.float32)
    formal_checkpoint = next(
        row for row in formal["checkpoint_results"] if row["label"] == "final"
    )
    formal_cells = formal_cell_map(formal_checkpoint)
    rows = []
    classifications = []
    for configuration_id in configuration_ids:
        configuration = by_id[configuration_id]
        raw_teacher = teacher_table[configuration_id]
        for plant in smoke.PLANTS:
            base_kwargs = {
                "mujoco": mujoco,
                "scene": scene,
                "configuration": configuration,
                "plant": plant,
                "calibrator_design": calibrator_design,
                "observer_type": observer_type,
                "canonical_fit": args.canonical_fit,
                "parameters": snapshot["parameters"],
                "target_mean": target_mean,
                "target_std": target_std,
            }
            graph_cell = gate.run_cell(session=session, **base_kwargs)
            exact = gate.public_cell(graph_cell) == formal_cells[(configuration_id, plant)]
            arms: dict[str, Any] = {"graph": v48.compact_cell(graph_cell)}
            for arm in ARMS[1:]:
                intervention = v48.InterventionSession(
                    session,
                    raw_teacher=raw_teacher,
                    mode=arm,
                    bounded_action=smoke.bounded_action_numpy,
                )
                arms[arm] = v48.compact_cell(
                    gate.run_cell(session=intervention, **base_kwargs)
                )
            classification = v48.classify_failed_pair(arms)
            classifications.append(
                {
                    "configuration_id": configuration_id,
                    "plant": plant,
                    "classification": classification,
                }
            )
            rows.append(
                {
                    "configuration_id": configuration_id,
                    "plant": plant,
                    "formal_graph_cell_bit_exact": exact,
                    "raw_teacher_sha256": v48.array_sha256(raw_teacher),
                    "action_alignment": v48.action_alignment(
                        graph_cell["_arrays"]["actions"],
                        raw_teacher,
                        smoke.bounded_action_numpy,
                    ),
                    "arms": arms,
                }
            )
    support_counts = {
        arm: sum(row["arms"][arm]["support_pass"] for row in rows)
        for arm in ARMS
    }
    classification_counts = {
        name: sum(row["classification"] == name for row in classifications)
        for name in (
            "teacher_insufficient",
            "pitch_output_causal",
            "nonpitch_output_causal",
            "either_single_intervention_rescues",
            "pitch_nonpitch_interaction",
        )
    }
    all_arm_cells = [cell for row in rows for cell in row["arms"].values()]
    checks = {
        "exact_48_cells": len(all_arm_cells) == 48,
        "exact_12_cells_per_arm": all(
            sum(arm in row["arms"] for row in rows) == 12 for arm in ARMS
        ),
        "all_12_graph_cells_bit_exact_to_v53": all(
            row["formal_graph_cell_bit_exact"] for row in rows
        ),
        "exact_12_failed_pair_classifications": len(classifications) == 12,
        "all_previous_action_chains_exact": all(
            cell["previous_action_chain_exact"] for cell in all_arm_cells
        ),
        "all_jax_onnx_hidden_errors_at_most_1e_7": all(
            cell["maximum_jax_onnx_hidden_error"] <= 1.0e-7
            for cell in all_arm_cells
        ),
        "all_values_finite": all(
            math.isfinite(cell["maximum_jax_onnx_hidden_error"])
            for cell in all_arm_cells
        ),
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    valid = not failed
    result = {
        "schema_version": "winner_v54.residual_teacher_causal_result.v1",
        "status": (
            "PASS_WINNER_V54_RESIDUAL_TEACHER_CAUSAL_DIAGNOSTIC"
            if valid
            else "INVALID_WINNER_V54_RESIDUAL_TEACHER_CAUSAL_DIAGNOSTIC"
        ),
        "decision": (
            "SELECT_NEXT_MECHANISM_FROM_FROZEN_RESIDUAL_CLASSIFICATION_ONLY"
            if valid
            else "DO_NOT_SELECT_NEXT_POLICY_MECHANISM"
        ),
        "checks": checks,
        "failed_checks": failed,
        "findings": {
            "support_pass_counts": support_counts,
            "full_teacher_all_12_pass": support_counts["full_teacher"] == 12,
            "classification_counts": classification_counts,
            "classification_rows": classifications,
        },
        "checkpoint": {
            "label": "final",
            "update": 453,
            "checkpoint_sha256": smoke.sha256(checkpoint_path),
            "onnx_sha256": smoke.sha256(graph_path),
            "cells": rows,
        },
        "sources": {
            "preregistration_lf_sha256": lf_sha256(PREREGISTRATION),
            "v53_result_sha256": sha256(V53_RESULT),
            "runner_lf_sha256": lf_sha256(Path(__file__)),
            "v48_intervention_runner_lf_sha256": lf_sha256(
                ROOT / "tools/run_winner_v48_static_teacher_causal_diagnostic.py"
            ),
        },
        "execution": {
            "diagnostic_cells": len(all_arm_cells),
            "optimizer_updates": 0,
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
    markdown.write_text(
        "\n".join(
            [
                "# Winner-v54 residual-teacher causal result",
                "",
                f"- Status: `{result['status']}`",
                f"- Decision: `{result['decision']}`",
                f"- Arm support: `{json.dumps(support_counts, sort_keys=True)}`",
                f"- Classification: `{json.dumps(classification_counts, sort_keys=True)}`",
                "- Optimizer / locomotion / robot: `0 / 0 / 0`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(result["status"])
    print(json.dumps(result["findings"], sort_keys=True))
    return 0 if valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
