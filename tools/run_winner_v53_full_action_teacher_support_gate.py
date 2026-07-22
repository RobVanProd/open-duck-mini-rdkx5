#!/usr/bin/env python3
"""Run the frozen 248-cell support gate on Winner-v52 half/final artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
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

PREREGISTRATION = ANALYSIS / "winner_v53_full_action_teacher_support_gate_preregistration.json"
TRAINING_RESULT = ANALYSIS / "winner_v52_full_action_teacher_training_result.json"
TRAINING_PREREGISTRATION = ANALYSIS / "winner_v52_full_action_teacher_training_preregistration.json"
BASE_GATE_PREREGISTRATION = ANALYSIS / "winner_v12_full_calibrator_training_preregistration.json"
BASE_GATE_RUNNER = ROOT / "tools/run_winner_v12_calibrator_support_gate.py"
SNAPSHOT_SCHEMA = "winner_v21.predictor_preserving_snapshot.v1"
CHECKPOINTS = (("half", 403), ("final", 453))

_TRAINING: dict[str, Any] | None = None
_TRAINING_PREREG: dict[str, Any] | None = None
smoke: Any = None
training: Any = None
v21: Any = None
v22v2: Any = None
normalized_support: Any = None


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


def _validate_snapshot(snapshot: Mapping[str, Any], *, expected_stage: str) -> None:
    if smoke is None or training is None or v21 is None:
        raise AssertionError("Winner-v53 snapshot dependencies were not loaded")
    if _TRAINING is None or _TRAINING_PREREG is None:
        raise AssertionError("Winner-v53 training evidence was not loaded")
    if set(snapshot) != {"parameters", "optimizer", "metadata", "target_mean", "target_std"}:
        raise ValueError("Winner-v53 checkpoint state schema changed")
    metadata = snapshot["metadata"]
    update = metadata.get("completed_updates")
    if (
        metadata.get("schema_version") != SNAPSHOT_SCHEMA
        or metadata.get("stage") != expected_stage
        or update not in {403, 453}
        or metadata.get("source_completed_updates") != 353
        or metadata.get("source_snapshot_sha256")
        != _TRAINING["source_snapshot"]["sha256"]
        or metadata.get("teacher_snapshot_sha256")
        != _TRAINING["teacher_snapshot"]["sha256"]
        or metadata.get("objective") != _TRAINING_PREREG["objective"]
        or metadata.get("root_seed") != 120120
        or metadata.get("learning_rate") != 0.0001
        or metadata.get("predictor_scale") != 380.9135437011719
        or metadata.get("prefix_anchor_scale") != 197.3112030029297
        or metadata.get("full_action_teacher_scale") != 136.35153198242188
        or metadata.get("formal_support_cells") != 0
        or metadata.get("locomotion_steps") != 0
        or metadata.get("robot_or_rdk_access") != 0
        or int(np.asarray(snapshot["optimizer"]["count"])) != update
        or set(snapshot["optimizer"]["m"]) != set(v21.JOINT_TRAINABLE_KEYS)
        or set(snapshot["optimizer"]["v"]) != set(v21.JOINT_TRAINABLE_KEYS)
        or set(v21.joint_trainable_parameters(snapshot["parameters"]))
        != set(v21.JOINT_TRAINABLE_KEYS)
    ):
        raise ValueError("Winner-v53 checkpoint metadata changed")
    for name in ("target_mean", "target_std"):
        value = np.asarray(snapshot[name])
        if (
            value.shape != (50,)
            or value.dtype != np.dtype(np.float32)
            or not np.all(np.isfinite(value))
        ):
            raise ValueError(f"Winner-v53 {name} schema changed")
    if np.any(np.asarray(snapshot["target_std"]) <= 0.0):
        raise ValueError("Winner-v53 target_std is not positive")
    for tree in (
        snapshot["parameters"],
        snapshot["optimizer"]["m"],
        snapshot["optimizer"]["v"],
    ):
        if not all(np.all(np.isfinite(np.asarray(value))) for value in tree.values()):
            raise ValueError("Winner-v53 checkpoint contains nonfinite arrays")


def load_snapshot_for_reviewed_gate(path: Path) -> dict[str, Any]:
    if v22v2 is None or normalized_support is None:
        raise AssertionError("Winner-v53 checkpoint mechanics were not loaded")
    exact = v22v2.load_snapshot(path)
    _validate_snapshot(
        exact, expected_stage="full_action_static_target_teacher_joint_stage2"
    )
    adapted = dict(exact)
    adapted["metadata"] = dict(exact["metadata"])
    adapted["metadata"]["stage"] = "stage2"
    adapted["parameters"] = normalized_support.raw_coordinate_predictor_parameters(
        exact["parameters"], exact["target_mean"], exact["target_std"]
    )
    return adapted


def validate_snapshot_for_reviewed_gate(snapshot: Mapping[str, Any]) -> None:
    _validate_snapshot(snapshot, expected_stage="stage2")


def checkpoint_paths(work_root: Path, label: str) -> tuple[Path, Path]:
    if _TRAINING is None:
        raise AssertionError("Winner-v53 training result was not loaded")
    mapping = {"half": 403, "final": 453}
    if label not in mapping:
        raise ValueError(f"unknown Winner-v53 checkpoint: {label}")
    update = mapping[label]
    snapshot = (
        work_root
        / "snapshots"
        / f"snapshot_full_action_teacher_update_{update:03d}.npz"
    )
    graph = work_root / "graphs" / f"winner_v52_{label}.onnx"
    snapshot_receipt = next(
        row for row in _TRAINING["snapshot_manifest"]
        if row["completed_updates"] == update
    )
    graph_receipt = next(
        row["graph"] for row in _TRAINING["persistent_checkpoints"]
        if row["label"] == label and row["completed_updates"] == update
    )
    for path, receipt in ((snapshot, snapshot_receipt), (graph, graph_receipt)):
        if (
            not path.is_file()
            or sha256(path) != receipt["sha256"]
            or path.stat().st_size != receipt["bytes"]
        ):
            raise ValueError(f"Winner-v53 {label} artifact bytes changed: {path.name}")
    return snapshot, graph


def validate_preregistration(value: Mapping[str, Any]) -> None:
    if _TRAINING is None:
        raise AssertionError("Winner-v53 training result was not loaded")
    if (
        value.get("schema_version")
        != "winner_v53.full_action_teacher_support_gate_preregistration.v1"
        or value.get("status")
        != "PREREGISTERED_WINNER_V53_FULL_ACTION_TEACHER_SUPPORT_GATE"
        or value.get("decision")
        != "AUTHORIZE_ONE_FROZEN_WINNER_V53_248_CELL_GATE_ONLY"
        or value.get("execution_now")
        != {
            "formal_support_cells": 0,
            "heldout_repeat_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        }
        or value.get("pass_rule")
        != {
            "all_124_main_cells_at_both_checkpoints": True,
            "all_32_heldout_repeats_at_both_checkpoints": True,
            "all_16_heldout_contexts_separate_at_both_checkpoints": True,
            "learned_prediction_beats_constant_per_plant": True,
            "closest_checkpoint_selection": False,
        }
        or value.get("selection_rule")
        != {
            "selected_only_if_every_pass_rule_is_true_at_both_checkpoints": True,
            "selected_checkpoint_if_pass": "final",
            "selected_update_if_pass": 453,
            "selection_basis": "fixed terminal endpoint after half/final persistence",
            "metric_ranking_or_closest_result": False,
            "no_selection_if_hold": True,
        }
    ):
        raise ValueError("Winner-v53 preregistration identity changed")
    gate = value.get("future_frozen_support_gate", {})
    if (
        gate.get("cells_per_checkpoint") != 124
        or gate.get("checkpoint_labels") != ["half", "final"]
        or gate.get("duration_ticks") != 250
        or gate.get("all_cells_at_both_checkpoints_must_pass") is not True
        or gate.get("selection_by_closest_result") is not False
        or gate.get("predictor_scoring", {}).get("head_output_coordinates")
        != "normalized"
        or gate.get("predictor_scoring", {}).get(
            "physical_support_population_thresholds_seeds_unchanged"
        )
        is not True
    ):
        raise ValueError("Winner-v53 gate dimensions changed")
    bound = value.get("training_artifact", {})
    expected = {
        "source_snapshot": _TRAINING["source_snapshot"],
        "source_graph": _TRAINING["source_graph"],
        "teacher_snapshot": _TRAINING["teacher_snapshot"],
        "objective": _TRAINING["objective"],
    }
    if any(bound.get(name) != item for name, item in expected.items()):
        raise ValueError("Winner-v53 training binding changed")
    if (
        bound.get("result", {}).get("sha256") != sha256(TRAINING_RESULT)
        or bound.get("result", {}).get("bytes") != TRAINING_RESULT.stat().st_size
    ):
        raise ValueError("Winner-v53 training-result receipt changed")
    sources = value.get("sources")
    if not isinstance(sources, dict):
        raise ValueError("Winner-v53 source manifest is absent")
    for name, item in sources.items():
        if (
            set(item) != {"hash_mode", "path", "sha256"}
            or item["hash_mode"] != "lf"
            or lf_sha256(ROOT / item["path"]) != item["sha256"]
        ):
            raise ValueError(f"Winner-v53 source changed: {name}")
    if canonical_sha256(sources) != value.get("source_manifest_sha256"):
        raise ValueError("Winner-v53 source manifest changed")


def finalize_result(reviewed: Mapping[str, Any], return_code: int) -> dict[str, Any]:
    if _TRAINING is None:
        raise AssertionError("Winner-v53 training result was not loaded")
    rows = reviewed.get("checkpoint_results")
    if (
        not isinstance(rows, list)
        or [(row.get("label"), row.get("update")) for row in rows]
        != list(CHECKPOINTS)
    ):
        raise ValueError("Winner-v53 checkpoint result population changed")
    passed = return_code == 0 and reviewed.get("failed_checks") == []
    final_row = rows[1]
    selected = None
    if passed:
        selected = {
            "label": "final",
            "completed_updates": 453,
            "snapshot_sha256": final_row["checkpoint_sha256"],
            "onnx_sha256": final_row["onnx_sha256"],
            "snapshot": _TRAINING["persistent_checkpoints"][1]["snapshot"],
            "graph": _TRAINING["persistent_checkpoints"][1]["graph"],
        }
    result = dict(reviewed)
    result["schema_version"] = (
        "winner_v53.full_action_teacher_support_gate_result.v1"
    )
    result["status"] = (
        "PASS_WINNER_V53_FULL_ACTION_TEACHER_SUPPORT_GATE"
        if passed
        else "HOLD_WINNER_V53_FULL_ACTION_TEACHER_SUPPORT_GATE"
    )
    result["decision"] = (
        "SELECT_WINNER_V52_FINAL_FOR_OFFLINE_RUNTIME_FREEZE_ONLY"
        if passed
        else "DO_NOT_SELECT_WINNER_V52_DEPLOYMENT_POLICY"
    )
    result["selected_checkpoint"] = selected
    result["selection_rule"] = {
        "selected_only_if_every_pass_rule_is_true_at_both_checkpoints": True,
        "selected_checkpoint_if_pass": "final",
        "selected_update_if_pass": 453,
        "selection_basis": "fixed terminal endpoint after half/final persistence",
        "metric_ranking_or_closest_result": False,
        "no_selection_if_hold": True,
    }
    result["reviewed_v12_sources"] = result.pop("sources")
    result["sources"] = {
        "preregistration_lf_sha256": lf_sha256(PREREGISTRATION),
        "training_result_sha256": sha256(TRAINING_RESULT),
        "training_preregistration_lf_sha256": lf_sha256(TRAINING_PREREGISTRATION),
        "base_gate_preregistration_lf_sha256": lf_sha256(
            BASE_GATE_PREREGISTRATION
        ),
        "base_gate_runner_lf_sha256": lf_sha256(BASE_GATE_RUNNER),
        "gate_runner_lf_sha256": lf_sha256(Path(__file__)),
    }
    result["authority"] = {
        "robot_clearance": passed,
        "robot_clearance_scope": (
            "selected policy is eligible only for separately authorized suspended Gate 5 "
            "after frozen-asset and no-servo runtime preflight"
            if passed
            else "none"
        ),
        "execution_authorized_by_this_result": False,
        "grounded_walking_authorized": False,
        "rdkx5_robot_serial_gpio_i2c_torque_motion_in_this_gate": False,
    }
    return result


def validate_result(value: Mapping[str, Any]) -> None:
    rows = value.get("checkpoint_results")
    if not isinstance(rows, list) or len(rows) != 2:
        raise ValueError("Winner-v53 result checkpoints changed")
    checks = value.get("checks")
    expected_checks = {
        "both_checkpoints_evaluated": [row["label"] for row in rows]
        == ["half", "final"],
        "all_248_main_cells_pass": all(not row["failed_checks"] for row in rows),
        "formal_cell_count_exact": sum(
            len(row["core_model_plant_cells"])
            + len(row["sensor_transport_plant_cells"])
            for row in rows
        )
        == 248,
    }
    failed = sorted(name for name, passed in expected_checks.items() if not passed)
    passed = not failed
    if (
        checks != expected_checks
        or value.get("failed_checks") != failed
        or value.get("execution")
        != {
            "formal_support_cells": 248,
            "heldout_repeat_cells": 64,
            "locomotion_training_steps": 0,
            "robot_or_rdk_access": 0,
        }
        or value.get("status")
        != (
            "PASS_WINNER_V53_FULL_ACTION_TEACHER_SUPPORT_GATE"
            if passed
            else "HOLD_WINNER_V53_FULL_ACTION_TEACHER_SUPPORT_GATE"
        )
        or (value.get("selected_checkpoint") is not None) is not passed
        or value.get("authority", {}).get("robot_clearance") is not passed
        or value.get("authority", {}).get("execution_authorized_by_this_result")
        is not False
    ):
        raise ValueError("Winner-v53 result decision changed")
    if passed:
        selected = value["selected_checkpoint"]
        if (
            selected.get("label") != "final"
            or selected.get("completed_updates") != 453
            or selected.get("onnx_sha256") != rows[1]["onnx_sha256"]
            or selected.get("snapshot_sha256") != rows[1]["checkpoint_sha256"]
        ):
            raise ValueError("Winner-v53 fixed endpoint selection changed")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--training-work-root", type=Path, required=True)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--canonical-fit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--offline-cpu-only", action="store_true")
    parser.add_argument("--formal-gate-authorized", action="store_true")
    return parser


def main() -> int:
    global _TRAINING, _TRAINING_PREREG, smoke, training, v21, v22v2
    global normalized_support
    import run_winner_v12_calibrator_cpu_smoke as smoke_module
    import run_winner_v12_calibrator_support_gate as base_gate
    import winner_v12_calibrator_training as training_module
    import winner_v21_predictor_preserving_joint_support as v21_module
    import winner_v22_normalized_predictor_v2 as v22v2_module
    import winner_v22_normalized_support_gate as normalized_support_module

    smoke = smoke_module
    training = training_module
    v21 = v21_module
    v22v2 = v22v2_module
    normalized_support = normalized_support_module
    args = build_parser().parse_args()
    if not args.offline_cpu_only or not args.formal_gate_authorized:
        raise PermissionError(
            "Winner-v53 requires --offline-cpu-only --formal-gate-authorized"
        )
    if args.output.exists():
        raise FileExistsError(f"refusing to overwrite Winner-v53 result: {args.output}")
    _TRAINING = json.loads(TRAINING_RESULT.read_text(encoding="utf-8"))
    _TRAINING_PREREG = json.loads(
        TRAINING_PREREGISTRATION.read_text(encoding="utf-8")
    )
    if (
        _TRAINING.get("status")
        != "PASS_WINNER_V52_FULL_ACTION_TEACHER_TRAINING_ARTIFACT"
        or _TRAINING.get("decision")
        != "AUTHORIZE_FULL_ACTION_TEACHER_SUPPORT_GATE_PREREGISTRATION_ONLY"
        or _TRAINING.get("failed_checks") != []
        or _TRAINING.get("execution", {}).get("formal_support_cells") != 0
    ):
        raise ValueError("Winner-v52 does not authorize the gate")
    preregistration = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    validate_preregistration(preregistration)

    pending = args.output.with_name(args.output.name + ".reviewed-v12.pending")
    if pending.exists():
        raise FileExistsError(pending)
    original = {
        "preregistration": base_gate.PREREGISTRATION,
        "checkpoints": base_gate.CHECKPOINTS,
        "checkpoint_paths": base_gate.checkpoint_paths,
        "load_snapshot": base_gate.full_training.load_snapshot,
        "validate_resume": base_gate.full_training.validate_resume,
        "load_calibrator_design": base_gate.load_calibrator_design,
    }

    def corrected_design_loader(
        _gate_preregistration: Mapping[str, Any],
    ) -> dict[str, Any]:
        reviewed = json.loads(
            BASE_GATE_PREREGISTRATION.read_text(encoding="utf-8")
        )
        return original["load_calibrator_design"](reviewed)

    base_gate.PREREGISTRATION = PREREGISTRATION
    base_gate.CHECKPOINTS = CHECKPOINTS
    base_gate.checkpoint_paths = checkpoint_paths
    base_gate.full_training.load_snapshot = load_snapshot_for_reviewed_gate
    base_gate.full_training.validate_resume = validate_snapshot_for_reviewed_gate
    base_gate.load_calibrator_design = corrected_design_loader
    original_argv = sys.argv
    try:
        sys.argv = [
            str(BASE_GATE_RUNNER),
            "--training-work-root",
            str(args.training_work_root),
            "--playground-root",
            str(args.playground_root),
            "--canonical-fit",
            str(args.canonical_fit),
            "--output",
            str(pending),
            "--offline-cpu-only",
            "--formal-gate-authorized",
        ]
        return_code = base_gate.main()
    finally:
        sys.argv = original_argv
        base_gate.PREREGISTRATION = original["preregistration"]
        base_gate.CHECKPOINTS = original["checkpoints"]
        base_gate.checkpoint_paths = original["checkpoint_paths"]
        base_gate.full_training.load_snapshot = original["load_snapshot"]
        base_gate.full_training.validate_resume = original["validate_resume"]
        base_gate.load_calibrator_design = original["load_calibrator_design"]
    reviewed = json.loads(pending.read_text(encoding="utf-8"))
    pending.unlink()
    result = finalize_result(reviewed, return_code)
    validate_result(result)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(result["status"])
    return 0 if not result["failed_checks"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
