#!/usr/bin/env python3
"""Run the frozen Winner-v48 teacher/action causal diagnostic on CPU."""

from __future__ import annotations

import argparse
from collections.abc import Callable, Mapping, Sequence
import hashlib
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
TOOLS = ROOT / "tools"
PATCHES = ROOT / "patches"
ANALYSIS = ROOT / "outputs/analysis"
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(PATCHES))

PREREGISTRATION = (
    ANALYSIS / "winner_v48_static_teacher_causal_diagnostic_preregistration.json"
)
V47B_RESULT = (
    ANALYSIS / "winner_v47b_support_gate_execution_correction_result.json"
)
V46_RESULT = ANALYSIS / "winner_v46_static_target_teacher_training_result.json"
V46_PREREGISTRATION = (
    ANALYSIS / "winner_v46_static_target_teacher_training_preregistration.json"
)
V42_RESULT = ANALYSIS / "winner_v42_static_target_teacher_table_result.json"
FULL_TRAINING_PREREGISTRATION = (
    ANALYSIS / "winner_v12_full_calibrator_training_preregistration.json"
)
DOMAIN = ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
PITCH_INDICES = np.asarray([2, 3, 4, 11, 12, 13], dtype=np.int64)
NONPITCH_INDICES = np.asarray([0, 1, 5, 6, 7, 8, 9, 10], dtype=np.int64)
ARMS = ("graph", "full_teacher", "pitch_teacher", "nonpitch_zero")
CHECKPOINTS = (("half", 302), ("final", 352))


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def validate_source_manifest(preregistration: Mapping[str, Any]) -> None:
    sources = preregistration.get("sources")
    if not isinstance(sources, Mapping) or not sources:
        raise ValueError("Winner-v48 source manifest is absent")
    for name, item in sources.items():
        if set(item) != {"hash_mode", "path", "sha256"}:
            raise ValueError(f"Winner-v48 source record changed: {name}")
        if item["hash_mode"] != "lf" or lf_sha256(ROOT / item["path"]) != item["sha256"]:
            raise ValueError(f"Winner-v48 source changed: {name}")
    if canonical_sha256(sources) != preregistration.get("source_manifest_sha256"):
        raise ValueError("Winner-v48 source-manifest digest changed")


class InterventionSession:
    """Replace selected graph actions while retaining its response-state output."""

    def __init__(
        self,
        session: Any,
        *,
        raw_teacher: np.ndarray,
        mode: str,
        bounded_action: Callable[[np.ndarray, np.ndarray], np.ndarray],
    ) -> None:
        if mode not in ARMS[1:]:
            raise ValueError(f"unsupported Winner-v48 intervention: {mode}")
        teacher = np.asarray(raw_teacher, dtype=np.float32)
        if teacher.shape != (14,) or not np.all(np.isfinite(teacher)):
            raise ValueError("Winner-v48 teacher target is invalid")
        self.session = session
        self.raw_teacher = teacher.copy()
        self.mode = mode
        self.bounded_action = bounded_action

    def run(
        self, output_names: Sequence[str], inputs: Mapping[str, np.ndarray]
    ) -> list[np.ndarray]:
        outputs = self.session.run(output_names, dict(inputs))
        actor = np.asarray(outputs[0], dtype=np.float32)
        previous = np.asarray(inputs["previous_action"], dtype=np.float32)
        if actor.shape != (1, 14) or previous.shape != (1, 14):
            raise ValueError("Winner-v48 intervention ABI changed")
        raw = actor[0].copy()
        if self.mode == "full_teacher":
            raw[:] = self.raw_teacher
        elif self.mode == "pitch_teacher":
            raw[PITCH_INDICES] = self.raw_teacher[PITCH_INDICES]
        elif self.mode == "nonpitch_zero":
            raw[NONPITCH_INDICES] = 0.0
        applied = self.bounded_action(raw, previous[0])[None, :]
        return [
            applied,
            applied.copy(),
            np.asarray(outputs[2], dtype=np.float32),
        ]


def subset_statistics(error: np.ndarray, indices: np.ndarray) -> dict[str, float]:
    selected = np.asarray(error, dtype=np.float64)[:, indices]
    return {
        "mean_abs": float(np.mean(np.abs(selected))),
        "rms": float(np.sqrt(np.mean(np.square(selected)))),
        "maximum_abs": float(np.max(np.abs(selected))),
    }


def action_alignment(
    actions: np.ndarray,
    raw_teacher: np.ndarray,
    bounded_action: Callable[[np.ndarray, np.ndarray], np.ndarray],
) -> dict[str, Any]:
    values = np.asarray(actions, dtype=np.float32)
    teacher = np.asarray(raw_teacher, dtype=np.float32)
    if values.ndim != 2 or values.shape[1] != 14 or values.shape[0] < 1:
        raise ValueError("Winner-v48 action trace shape changed")
    if teacher.shape != (14,) or not np.all(np.isfinite(values)):
        raise ValueError("Winner-v48 action alignment input changed")
    previous = np.vstack(
        [np.zeros((1, 14), dtype=np.float32), values[:-1]]
    )
    bounded_teacher = np.asarray(
        [bounded_action(teacher, row) for row in previous], dtype=np.float32
    )
    error = values - bounded_teacher
    per_tick = []
    for tick, row in enumerate(error.astype(np.float64)):
        pitch = row[PITCH_INDICES]
        nonpitch = row[NONPITCH_INDICES]
        per_tick.append(
            {
                "tick": tick,
                "pitch_rms": float(np.sqrt(np.mean(np.square(pitch)))),
                "pitch_maximum_abs": float(np.max(np.abs(pitch))),
                "nonpitch_rms": float(np.sqrt(np.mean(np.square(nonpitch)))),
                "nonpitch_maximum_abs": float(np.max(np.abs(nonpitch))),
            }
        )
    return {
        "tick_count": int(values.shape[0]),
        "actor_action_trace_sha256": array_sha256(values),
        "bounded_teacher_trace_sha256": array_sha256(bounded_teacher),
        "pitch": subset_statistics(error, PITCH_INDICES),
        "nonpitch": subset_statistics(error, NONPITCH_INDICES),
        "all": subset_statistics(error, np.arange(14, dtype=np.int64)),
        "per_tick": per_tick,
    }


def array_sha256(value: Any) -> str:
    array = np.ascontiguousarray(np.asarray(value))
    digest = hashlib.sha256()
    digest.update(str(array.dtype).encode())
    digest.update(json.dumps(list(array.shape), separators=(",", ":")).encode())
    digest.update(array.tobytes())
    return digest.hexdigest()


def compact_cell(cell: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "support_pass": bool(cell["support_pass"]),
        "terminal": cell["terminal"],
        "episode": cell["episode"],
        "previous_action_chain_exact": bool(cell["previous_action_chain_exact"]),
        "maximum_jax_onnx_hidden_error": float(
            cell["maximum_jax_onnx_hidden_error"]
        ),
        "trace_hashes": cell["trace_hashes"],
    }


def classify_failed_pair(arms: Mapping[str, Mapping[str, Any]]) -> str:
    full = bool(arms["full_teacher"]["support_pass"])
    pitch = bool(arms["pitch_teacher"]["support_pass"])
    nonpitch = bool(arms["nonpitch_zero"]["support_pass"])
    if not full:
        return "teacher_insufficient"
    if pitch and nonpitch:
        return "either_single_intervention_rescues"
    if pitch:
        return "pitch_output_causal"
    if nonpitch:
        return "nonpitch_output_causal"
    return "pitch_nonpitch_interaction"


def formal_cell_map(checkpoint: Mapping[str, Any]) -> dict[tuple[str, str], Any]:
    cells = checkpoint["core_model_plant_cells"]
    result = {(row["configuration_id"], row["plant"]): row for row in cells}
    if len(result) != len(cells):
        raise ValueError("Winner-v48 formal cell population contains duplicates")
    return result


def configure_v47_modules() -> tuple[Any, ...]:
    import build_winner_v47_static_target_teacher_support_gate_preregistration as v47_builder
    import run_winner_v12_calibrator_cpu_smoke as smoke
    import run_winner_v12_calibrator_support_gate as gate
    import run_winner_v47_static_target_teacher_support_gate as v47
    import winner_v12_calibrator_training as training
    import winner_v21_predictor_preserving_joint_support as v21
    import winner_v22_normalized_predictor_v2 as v22v2
    import winner_v22_normalized_support_gate as normalized_support

    v47.reviewed_gate = gate
    v47.smoke = smoke
    v47.training = training
    v47.v21 = v21
    v47.v22v2 = v22v2
    v47.normalized_support = normalized_support
    v47.builder = v47_builder
    v47._TRAINING = json.loads(V46_RESULT.read_text(encoding="utf-8"))
    v47._TRAINING_PREREG = json.loads(
        V46_PREREGISTRATION.read_text(encoding="utf-8")
    )
    return smoke, gate, v47, training


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--training-work-root", type=Path, required=True)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--canonical-fit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--markdown", type=Path)
    parser.add_argument("--offline-cpu-only", action="store_true")
    parser.add_argument("--causal-diagnostic-authorized", action="store_true")
    args = parser.parse_args()
    if not args.offline_cpu_only or not args.causal_diagnostic_authorized:
        raise PermissionError(
            "Winner-v48 requires --offline-cpu-only --causal-diagnostic-authorized"
        )
    if args.output.exists():
        raise FileExistsError(f"refusing to overwrite Winner-v48 result: {args.output}")
    markdown = args.markdown or args.output.with_suffix(".md")
    if markdown.exists():
        raise FileExistsError(f"refusing to overwrite Winner-v48 summary: {markdown}")

    import jax
    import mujoco
    import onnxruntime as ort
    import winner_v43_static_target_teacher as v43

    if jax.default_backend() != "cpu" or any(
        device.platform != "cpu" for device in jax.devices()
    ):
        raise ValueError("Winner-v48 requires CPU-only JAX")
    preregistration = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    if (
        preregistration.get("status")
        != "PREREGISTERED_WINNER_V48_STATIC_TEACHER_CAUSAL_DIAGNOSTIC"
        or preregistration.get("decision")
        != "AUTHORIZE_ONE_READ_ONLY_CPU_CAUSAL_DIAGNOSTIC"
        or preregistration.get("frozen_population", {}).get("total_cells") != 128
        or preregistration.get("execution_now")
        != {
            "diagnostic_cells": 0,
            "optimizer_updates": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        }
    ):
        raise ValueError("Winner-v48 preregistration changed")
    validate_source_manifest(preregistration)

    formal = json.loads(V47B_RESULT.read_text(encoding="utf-8"))
    if (
        formal.get("status")
        != "HOLD_WINNER_V47B_SUPPORT_GATE_EXECUTION_CORRECTION"
        or formal.get("decision") != "DO_NOT_TRAIN_RESPONSE_CONDITIONED_LOCOMOTION"
    ):
        raise ValueError("Winner-v48 formal source changed")
    smoke, gate, v47, _ = configure_v47_modules()
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
    configuration_ids = preregistration["frozen_population"]["configuration_ids"]
    if set(configuration_ids) - set(by_id):
        raise ValueError("Winner-v48 configuration is absent from the frozen domain")
    teacher_table = v43.load_teacher_table(
        json.loads(V42_RESULT.read_text(encoding="utf-8"))
    )
    if set(configuration_ids) - set(teacher_table):
        raise ValueError("Winner-v48 configuration is absent from the teacher table")

    scene = args.playground_root / smoke.SCENE_RELATIVE
    if not scene.is_file():
        raise FileNotFoundError(scene)
    if smoke.git_output(args.playground_root, "rev-parse", "HEAD") != smoke.CONTROL_COMMIT:
        raise ValueError("Winner-v48 Playground commit changed")
    smoke.validate_playground_tree(args.playground_root)
    if smoke.sha256(args.canonical_fit) != smoke.P30_FIT_LF_SHA256:
        raise ValueError("Winner-v48 canonical P30 fit changed")
    observer_type = smoke.load_runtime_observer(args.canonical_fit)
    options = ort.SessionOptions()
    options.intra_op_num_threads = 1
    options.inter_op_num_threads = 1
    options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL

    checkpoint_results = []
    classifications: list[dict[str, Any]] = []
    for label, update in CHECKPOINTS:
        checkpoint_path, graph_path = v47.checkpoint_paths(
            args.training_work_root, label
        )
        snapshot = v47.load_snapshot_for_reviewed_gate(checkpoint_path)
        v47.validate_snapshot_for_reviewed_gate(snapshot)
        if snapshot["metadata"]["completed_updates"] != update:
            raise ValueError("Winner-v48 checkpoint boundary changed")
        session = ort.InferenceSession(
            str(graph_path), sess_options=options, providers=["CPUExecutionProvider"]
        )
        target_mean = np.asarray(snapshot["target_mean"], dtype=np.float32)
        target_std = np.asarray(snapshot["target_std"], dtype=np.float32)
        formal_checkpoint = next(
            row for row in formal["checkpoint_results"] if row["label"] == label
        )
        formal_cells = formal_cell_map(formal_checkpoint)
        rows = []
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
                graph_public = gate.public_cell(graph_cell)
                formal_public = formal_cells[(configuration_id, plant)]
                exact = graph_public == formal_public
                arm_results: dict[str, Any] = {
                    "graph": compact_cell(graph_cell)
                }
                for arm in ARMS[1:]:
                    intervention = InterventionSession(
                        session,
                        raw_teacher=raw_teacher,
                        mode=arm,
                        bounded_action=smoke.bounded_action_numpy,
                    )
                    arm_results[arm] = compact_cell(
                        gate.run_cell(session=intervention, **base_kwargs)
                    )
                row = {
                    "configuration_id": configuration_id,
                    "plant": plant,
                    "formal_graph_cell_bit_exact": exact,
                    "raw_teacher_sha256": array_sha256(raw_teacher),
                    "action_alignment": action_alignment(
                        graph_cell["_arrays"]["actions"],
                        raw_teacher,
                        smoke.bounded_action_numpy,
                    ),
                    "arms": arm_results,
                }
                rows.append(row)
                if not graph_cell["support_pass"]:
                    classifications.append(
                        {
                            "checkpoint": label,
                            "configuration_id": configuration_id,
                            "plant": plant,
                            "classification": classify_failed_pair(arm_results),
                        }
                    )
        support_counts = {
            arm: sum(row["arms"][arm]["support_pass"] for row in rows)
            for arm in ARMS
        }
        checkpoint_results.append(
            {
                "label": label,
                "update": update,
                "checkpoint_sha256": smoke.sha256(checkpoint_path),
                "onnx_sha256": smoke.sha256(graph_path),
                "cells": rows,
                "support_pass_counts": support_counts,
            }
        )

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
    all_rows = [row for checkpoint in checkpoint_results for row in checkpoint["cells"]]
    all_arm_cells = [
        cell
        for row in all_rows
        for cell in row["arms"].values()
    ]
    checks = {
        "exact_128_cells": len(all_arm_cells) == 128,
        "exact_32_cells_per_arm": all(
            sum(1 for row in all_rows if arm in row["arms"]) == 32
            for arm in ARMS
        ),
        "all_graph_cells_bit_exact_to_v47b": all(
            row["formal_graph_cell_bit_exact"] for row in all_rows
        ),
        "exact_28_formal_failed_pair_classifications": len(classifications) == 28,
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
    failed_checks = sorted(name for name, passed in checks.items() if not passed)
    full_teacher_pass_count = sum(
        row["arms"]["full_teacher"]["support_pass"] for row in all_rows
    )
    findings = {
        "full_teacher_support_pass_count": full_teacher_pass_count,
        "full_teacher_all_32_pass": full_teacher_pass_count == 32,
        "classification_counts": classification_counts,
        "classification_rows": classifications,
    }
    valid = not failed_checks
    result = {
        "schema_version": "winner_v48.static_teacher_causal_diagnostic_result.v1",
        "status": (
            "PASS_WINNER_V48_STATIC_TEACHER_CAUSAL_DIAGNOSTIC"
            if valid
            else "INVALID_WINNER_V48_STATIC_TEACHER_CAUSAL_DIAGNOSTIC"
        ),
        "decision": (
            "DIAGNOSTIC_ONLY_SELECT_NEXT_MECHANISM_FROM_FROZEN_CLASSIFICATION"
            if valid
            else "DO_NOT_SELECT_NEXT_POLICY_MECHANISM"
        ),
        "checks": checks,
        "failed_checks": failed_checks,
        "findings": findings,
        "checkpoint_results": checkpoint_results,
        "sources": {
            "preregistration_lf_sha256": lf_sha256(PREREGISTRATION),
            "v47b_result_lf_sha256": lf_sha256(V47B_RESULT),
            "runner_lf_sha256": lf_sha256(Path(__file__)),
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
                "# Winner-v48 static-teacher causal diagnostic result",
                "",
                f"- Status: `{result['status']}`",
                f"- Decision: `{result['decision']}`",
                f"- Full-teacher support: `{full_teacher_pass_count}/32`",
                f"- Formal failed-pair classifications: `{json.dumps(classification_counts, sort_keys=True)}`",
                "- Optimizer / locomotion / robot: `0 / 0 / 0`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(result["status"])
    print(json.dumps(findings, sort_keys=True))
    return 0 if valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
