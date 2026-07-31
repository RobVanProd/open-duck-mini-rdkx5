#!/usr/bin/env python3
"""Run the frozen Winner-v62 residual-teacher diagnostic on CPU."""

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

PREREGISTRATION = ANALYSIS / "winner_v62_residual_teacher_causal_preregistration.json"
V61_RESULT = ANALYSIS / "winner_v61_integrated_support_gate_result.json"
V60_RESULT = ANALYSIS / "winner_v60_integrated_numeric_guard_training_result.json"
V60_PREREGISTRATION = ANALYSIS / "winner_v60_integrated_numeric_guard_training_preregistration.json"
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
        != "winner_v62.residual_teacher_causal_preregistration.v1"
        or value.get("status")
        != "PREREGISTERED_WINNER_V62_RESIDUAL_TEACHER_CAUSAL_DIAGNOSTIC"
        or value.get("decision")
        != "AUTHORIZE_ONE_READ_ONLY_52_CELL_CPU_DIAGNOSTIC_ONLY"
        or len(value.get("frozen_source", {}).get("failure_pairs", [])) != 13
        or value.get("frozen_execution")
        != {
            "checkpoint_count": 1,
            "failed_pair_count": 13,
            "arm_count": 4,
            "diagnostic_cells": 52,
            "ticks_per_cell": 250,
            "formal_graph_cells_must_match_v61_bit_exact": True,
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
        raise ValueError("Winner-v62 preregistration identity changed")
    sources = value.get("sources")
    if not isinstance(sources, dict) or not sources:
        raise ValueError("Winner-v62 source manifest is absent")
    for name, item in sources.items():
        if (
            set(item) != {"hash_mode", "path", "sha256"}
            or item["hash_mode"] != "lf"
            or lf_sha256(ROOT / item["path"]) != item["sha256"]
        ):
            raise ValueError(f"Winner-v62 source changed: {name}")
    if canonical_sha256(sources) != value.get("source_manifest_sha256"):
        raise ValueError("Winner-v62 source manifest changed")


def configure_v61_modules() -> tuple[Any, ...]:
    import build_winner_v61_integrated_support_gate_preregistration as v61_builder
    import run_winner_v12_calibrator_cpu_smoke as smoke
    import run_winner_v12_calibrator_support_gate as gate
    import winner_v12_calibrator_training as training
    import winner_v21_predictor_preserving_joint_support as v21
    import winner_v22_normalized_predictor_v2 as v22v2
    import winner_v22_normalized_support_gate as normalized_support

    source, _ = v61_builder.transformed_source()
    v61 = types.ModuleType("winner_v61_reviewed_gate")
    v61.__file__ = str(ROOT / "tools/run_winner_v61_integrated_support_gate.py")
    exec(compile(source, v61.__file__, "exec"), v61.__dict__)
    v61.smoke = smoke
    v61.training = training
    v61.v21 = v21
    v61.v22v2 = v22v2
    v61.normalized_support = normalized_support
    v61._TRAINING = json.loads(V60_RESULT.read_text(encoding="utf-8"))
    v61._TRAINING_PREREG = json.loads(V60_PREREGISTRATION.read_text(encoding="utf-8"))
    return smoke, gate, v61


def formal_cell_map(checkpoint: Mapping[str, Any]) -> dict[tuple[str, str], Any]:
    cells = checkpoint["core_model_plant_cells"]
    result = {(row["configuration_id"], row["plant"]): row for row in cells}
    if len(result) != len(cells):
        raise ValueError("Winner-v62 formal cell population contains duplicates")
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
            "Winner-v62 requires --offline-cpu-only --causal-diagnostic-authorized"
        )
    if args.output.exists():
        raise FileExistsError(f"refusing to overwrite Winner-v62 result: {args.output}")
    markdown = args.markdown or args.output.with_suffix(".md")
    if markdown.exists():
        raise FileExistsError(f"refusing to overwrite Winner-v62 summary: {markdown}")

    import jax
    import mujoco
    import onnxruntime as ort
    import run_winner_v48_static_teacher_causal_diagnostic as v48
    import winner_v43_static_target_teacher as v43

    if jax.default_backend() != "cpu" or any(
        device.platform != "cpu" for device in jax.devices()
    ):
        raise ValueError("Winner-v62 requires CPU-only JAX")
    preregistration = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    validate_preregistration(preregistration)
    formal = json.loads(V61_RESULT.read_text(encoding="utf-8"))
    if (
        formal.get("status") != "HOLD_WINNER_V61_INTEGRATED_SUPPORT_GATE"
        or formal.get("selected_checkpoint") is not None
        or sha256(V61_RESULT) != preregistration["frozen_source"]["v61_result_sha256"]
    ):
        raise ValueError("Winner-v62 formal source changed")
    smoke, gate, v61 = configure_v61_modules()
    full_preregistration = json.loads(FULL_TRAINING_PREREGISTRATION.read_text(encoding="utf-8"))
    calibrator_design = gate.load_calibrator_design(full_preregistration)
    domain = json.loads(DOMAIN.read_text(encoding="utf-8"))
    matrix = domain["evaluation_matrix"]
    configurations = matrix["fixed_anchors"] + matrix["discovery_samples"] + matrix["heldout_samples"]
    by_id = {row["id"]: row for row in configurations}
    failure_pairs = preregistration["frozen_source"]["failure_pairs"]
    teacher_table = v43.load_teacher_table(json.loads(V42_RESULT.read_text(encoding="utf-8")))
    if any(row["configuration_id"] not in by_id or row["configuration_id"] not in teacher_table for row in failure_pairs):
        raise ValueError("Winner-v62 frozen configuration is absent")
    scene = args.playground_root / smoke.SCENE_RELATIVE
    if not scene.is_file():
        raise FileNotFoundError(scene)
    if smoke.git_output(args.playground_root, "rev-parse", "HEAD") != smoke.CONTROL_COMMIT:
        raise ValueError("Winner-v62 Playground commit changed")
    smoke.validate_playground_tree(args.playground_root)
    if smoke.sha256(args.canonical_fit) != smoke.P30_FIT_LF_SHA256:
        raise ValueError("Winner-v62 canonical P30 fit changed")
    observer_type = smoke.load_runtime_observer(args.canonical_fit)
    options = ort.SessionOptions()
    options.intra_op_num_threads = 1
    options.inter_op_num_threads = 1
    options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL

    checkpoint_path, graph_path = v61.checkpoint_paths(args.training_work_root, "final")
    snapshot = v61.load_snapshot_for_reviewed_gate(checkpoint_path)
    v61.validate_snapshot_for_reviewed_gate(snapshot)
    if snapshot["metadata"]["completed_updates"] != 554:
        raise ValueError("Winner-v62 checkpoint boundary changed")
    session = ort.InferenceSession(str(graph_path), sess_options=options, providers=["CPUExecutionProvider"])
    target_mean = np.asarray(snapshot["target_mean"], dtype=np.float32)
    target_std = np.asarray(snapshot["target_std"], dtype=np.float32)
    formal_checkpoint = next(row for row in formal["checkpoint_results"] if row["label"] == "final")
    formal_cells = formal_cell_map(formal_checkpoint)
    rows = []
    classifications = []
    for pair in failure_pairs:
        configuration_id = pair["configuration_id"]
        plant = pair["plant"]
        configuration = by_id[configuration_id]
        raw_teacher = teacher_table[configuration_id]
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
            arms[arm] = v48.compact_cell(gate.run_cell(session=intervention, **base_kwargs))
        classification = v48.classify_failed_pair(arms)
        classifications.append(
            {
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
        alignment["post_first_tick_pitch_rms_mean"] = float(
            np.mean([row["pitch_rms"] for row in post_rows])
        ) if post_rows else 0.0
        rows.append(
            {
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
    all_arm_cells = [cell for row in rows for cell in row["arms"].values()]
    checks = {
        "exact_52_cells": len(all_arm_cells) == 52,
        "exact_13_cells_per_arm": all(
            sum(arm in row["arms"] for row in rows) == 13 for arm in ARMS
        ),
        "all_13_graph_cells_bit_exact_to_v61": all(
            row["formal_graph_cell_bit_exact"] for row in rows
        ),
        "all_13_source_graph_cells_fail": support_counts["graph"] == 0,
        "exact_13_failed_pair_classifications": len(classifications) == 13,
        "all_previous_action_chains_exact": all(
            cell["previous_action_chain_exact"] for cell in all_arm_cells
        ),
        "all_jax_onnx_hidden_errors_at_most_1e_7": all(
            cell["maximum_jax_onnx_hidden_error"] <= 1.0e-7 for cell in all_arm_cells
        ),
        "all_values_finite": all(
            math.isfinite(cell["maximum_jax_onnx_hidden_error"])
            for cell in all_arm_cells
        ),
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    valid = not failed
    result = {
        "schema_version": "winner_v62.residual_teacher_causal_result.v1",
        "status": (
            "PASS_WINNER_V62_RESIDUAL_TEACHER_CAUSAL_DIAGNOSTIC"
            if valid
            else "INVALID_WINNER_V62_RESIDUAL_TEACHER_CAUSAL_DIAGNOSTIC"
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
            "full_teacher_all_13_pass": support_counts["full_teacher"] == 13,
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
        },
        "checkpoint": {
            "label": "final",
            "update": 554,
            "checkpoint_sha256": smoke.sha256(checkpoint_path),
            "onnx_sha256": smoke.sha256(graph_path),
            "cells": rows,
        },
        "sources": {
            "preregistration_lf_sha256": lf_sha256(PREREGISTRATION),
            "v61_result_sha256": sha256(V61_RESULT),
            "runner_lf_sha256": lf_sha256(Path(__file__)),
            "intervention_runner_lf_sha256": lf_sha256(
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
            "result_authorizes": (
                "causal diagnosis and a separate prospective mechanism preregistration only"
            ),
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
                "# Winner-v62 residual-teacher causal result",
                "",
                f"- Status: `{result['status']}`",
                f"- Decision: `{result['decision']}`",
                f"- Arm support: `{json.dumps(support_counts, sort_keys=True)}`",
                f"- Classification: `{json.dumps(classification_counts, sort_keys=True)}`",
                f"- First/post-first pitch RMS means: `{result['findings']['first_tick_pitch_rms_mean']} / {result['findings']['post_first_tick_pitch_rms_mean']}`",
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
