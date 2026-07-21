#!/usr/bin/env python3
"""Bind the corrected-coordinate reviewed support gate to Winner-v22 checkpoints."""

from __future__ import annotations

import argparse
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

PREREGISTRATION = ANALYSIS / "winner_v22_normalized_predictor_support_gate_preregistration.json"
TRAINING_RESULT = ANALYSIS / "winner_v22_normalized_predictor_training_result.json"
TRAINING_PREREGISTRATION = ANALYSIS / "winner_v22_normalized_predictor_training_preregistration.json"
TRAINING_RUNNER = ROOT / "tools/run_winner_v22_normalized_predictor_training.py"
BASE_GATE_RUNNER = ROOT / "tools/run_winner_v12_calibrator_support_gate.py"
STAGE1_SNAPSHOT_SHA256 = "8c1392c738eddfb098e61c1a6ae2f863eda883e1eba6ac546aef695da6f163af"
SNAPSHOT_SCHEMA = "winner_v21.predictor_preserving_snapshot.v1"
_TRAINING: dict[str, Any] | None = None
reviewed_gate: Any = None
smoke: Any = None
training: Any = None
v21: Any = None
v22v2: Any = None
normalized_support: Any = None


def _validate_snapshot(snapshot: Mapping[str, Any], *, expected_stage: str) -> None:
    if smoke is None or training is None or v21 is None:
        raise AssertionError("Winner-v22 gate dependencies were not loaded")
    if set(snapshot) != {"parameters", "optimizer", "metadata", "target_mean", "target_std"}:
        raise ValueError("Winner-v22 checkpoint state schema changed")
    metadata = snapshot["metadata"]
    update = metadata.get("completed_updates")
    if (
        metadata.get("schema_version") != SNAPSHOT_SCHEMA
        or metadata.get("stage") != expected_stage
        or update not in {50, 100}
        or metadata.get("root_seed") != 120120
        or metadata.get("learning_rate") != 0.0001
        or metadata.get("predictor_scale") != 380.9135437011719
        or metadata.get("predictor_formula")
        != "prediction_normalized - normalized_next_response"
        or metadata.get("source_stage1_snapshot_sha256") != STAGE1_SNAPSHOT_SHA256
        or metadata.get("preregistration_lf_sha256")
        != smoke.lf_sha256(TRAINING_PREREGISTRATION)
        or metadata.get("runner_lf_sha256") != smoke.lf_sha256(TRAINING_RUNNER)
        or metadata.get("formal_support_cells") != 0
        or metadata.get("locomotion_steps") != 0
        or metadata.get("robot_or_rdk_access") != 0
        or type(metadata.get("cumulative_sampled_count")) is not int
        or metadata["cumulative_sampled_count"] <= 0
        or type(metadata.get("cumulative_valid_transition_count")) is not int
        or not 0 < metadata["cumulative_valid_transition_count"]
        <= metadata["cumulative_sampled_count"]
        or type(metadata.get("cumulative_stored_successor_count")) is not int
        or not 0 < metadata["cumulative_stored_successor_count"]
        <= metadata["cumulative_sampled_count"]
        or int(np.asarray(snapshot["optimizer"]["count"])) != update
        or set(snapshot["optimizer"]["m"]) != set(v21.JOINT_TRAINABLE_KEYS)
        or set(snapshot["optimizer"]["v"]) != set(v21.JOINT_TRAINABLE_KEYS)
        or set(v21.joint_trainable_parameters(snapshot["parameters"]))
        != set(v21.JOINT_TRAINABLE_KEYS)
    ):
        raise ValueError("Winner-v22 checkpoint metadata changed")
    for name in ("target_mean", "target_std"):
        value = np.asarray(snapshot[name])
        if (
            value.shape != (50,)
            or value.dtype != np.dtype(np.float32)
            or not bool(np.all(np.isfinite(value)))
        ):
            raise ValueError(f"Winner-v22 {name} schema changed")
    if bool(np.any(np.asarray(snapshot["target_std"]) <= 0.0)):
        raise ValueError("Winner-v22 target_std is not strictly positive")
    for tree in (
        snapshot["parameters"],
        snapshot["optimizer"]["m"],
        snapshot["optimizer"]["v"],
    ):
        if not all(bool(np.all(np.isfinite(np.asarray(value)))) for value in tree.values()):
            raise ValueError("Winner-v22 checkpoint contains nonfinite arrays")


def load_snapshot_for_reviewed_gate(path: Path) -> dict[str, Any]:
    if v22v2 is None or normalized_support is None:
        raise AssertionError("Winner-v22 mechanics were not loaded")
    exact = v22v2.load_snapshot(path)
    _validate_snapshot(exact, expected_stage="normalized_predictor_joint_stage2")
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
    if _TRAINING is None or smoke is None:
        raise AssertionError("Winner-v22 training result was not loaded")
    mapping = {"half": 50, "final": 100}
    if label not in mapping:
        raise ValueError(f"unknown Winner-v22 checkpoint: {label}")
    update = mapping[label]
    snapshot = work_root / "snapshots" / f"snapshot_normalized_predictor_update_{update:03d}.npz"
    graph = work_root / "graphs" / f"winner_v22_{label}.onnx"
    snapshot_receipt = _TRAINING["snapshot_manifest"][update - 1]
    graph_receipt = next(
        row["graph"]
        for row in _TRAINING["persistent_checkpoints"]
        if row["label"] == label and row["update"] == update
    )
    for path, receipt in ((snapshot, snapshot_receipt), (graph, graph_receipt)):
        if (
            not path.is_file()
            or smoke.sha256(path) != receipt["sha256"]
            or path.stat().st_size != receipt["bytes"]
        ):
            raise ValueError(f"Winner-v22 {label} artifact bytes changed: {path.name}")
    return snapshot, graph


def validate_preregistration(value: Mapping[str, Any]) -> None:
    if smoke is None or reviewed_gate is None:
        raise AssertionError("Winner-v22 gate dependencies were not loaded")
    if (
        value.get("schema_version")
        != "winner_v22.normalized_predictor_support_gate_preregistration.v1"
        or value.get("status")
        != "PREREGISTERED_WINNER_V22_NORMALIZED_PREDICTOR_SUPPORT_GATE"
        or value.get("decision")
        != "AUTHORIZE_ONE_FROZEN_CORRECTED_COORDINATE_248_CELL_GATE_ONLY"
        or value.get("execution_now")
        != {
            "formal_support_cells": 0,
            "heldout_repeat_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        }
    ):
        raise ValueError("Winner-v22 gate preregistration changed")
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
        raise ValueError("Winner-v22 gate dimensions changed")
    sources = value.get("sources")
    if not isinstance(sources, dict) or not sources:
        raise ValueError("Winner-v22 gate sources are absent")
    for name, item in sources.items():
        path = ROOT / item["path"]
        if (
            set(item) != {"hash_mode", "path", "sha256"}
            or item["hash_mode"] != "lf"
            or smoke.lf_sha256(path) != item["sha256"]
        ):
            raise ValueError(f"Winner-v22 gate source changed: {name}")
    if reviewed_gate.canonical_sha256(sources) != value.get("source_manifest_sha256"):
        raise ValueError("Winner-v22 gate source manifest changed")


def main() -> int:
    global reviewed_gate, smoke, training, v21, v22v2, normalized_support, _TRAINING
    import run_winner_v12_calibrator_support_gate as reviewed_gate_module
    import run_winner_v12_calibrator_cpu_smoke as smoke_module
    import winner_v12_calibrator_training as training_module
    import winner_v21_predictor_preserving_joint_support as v21_module
    import winner_v22_normalized_predictor_v2 as v22v2_module
    import winner_v22_normalized_support_gate as normalized_support_module

    reviewed_gate = reviewed_gate_module
    smoke = smoke_module
    training = training_module
    v21 = v21_module
    v22v2 = v22v2_module
    normalized_support = normalized_support_module
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--training-work-root", type=Path, required=True)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--canonical-fit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--offline-cpu-only", action="store_true")
    parser.add_argument("--formal-gate-authorized", action="store_true")
    args = parser.parse_args()
    if not args.offline_cpu_only or not args.formal_gate_authorized:
        raise PermissionError("support gate requires --offline-cpu-only --formal-gate-authorized")
    if args.output.exists():
        raise FileExistsError(f"refusing to overwrite support-gate result: {args.output}")
    preregistration = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    validate_preregistration(preregistration)
    training_result = json.loads(TRAINING_RESULT.read_text(encoding="utf-8"))
    if (
        training_result.get("status")
        != "PASS_WINNER_V22_NORMALIZED_PREDICTOR_TRAINING_ARTIFACT"
        or training_result.get("decision")
        != "AUTHORIZE_SEPARATE_CORRECTED_SUPPORT_GATE_PREREGISTRATION_ONLY"
        or training_result.get("failed_checks") != []
        or training_result.get("execution", {}).get("formal_support_cells") != 0
    ):
        raise ValueError("Winner-v22 training does not authorize the gate")
    _TRAINING = training_result
    pending = args.output.with_name(args.output.name + ".reviewed-v12.pending")
    if pending.exists():
        raise FileExistsError(pending)
    reviewed_gate.PREREGISTRATION = PREREGISTRATION
    reviewed_gate.checkpoint_paths = checkpoint_paths
    reviewed_gate.full_training.load_snapshot = load_snapshot_for_reviewed_gate
    reviewed_gate.full_training.validate_resume = validate_snapshot_for_reviewed_gate
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
        reviewed_rc = reviewed_gate.main()
    finally:
        sys.argv = original_argv
    reviewed = json.loads(pending.read_text(encoding="utf-8"))
    pending.unlink()
    passed = reviewed_rc == 0 and reviewed.get("failed_checks") == []
    reviewed["schema_version"] = "winner_v22.normalized_predictor_support_gate_result.v1"
    reviewed["status"] = (
        "PASS_WINNER_V22_NORMALIZED_PREDICTOR_SUPPORT_GATE"
        if passed
        else "HOLD_WINNER_V22_NORMALIZED_PREDICTOR_SUPPORT_GATE"
    )
    reviewed["decision"] = (
        "AUTHORIZE_RESPONSE_CONDITIONED_LOCOMOTION_PREREGISTRATION_ONLY"
        if passed
        else "DO_NOT_TRAIN_RESPONSE_CONDITIONED_LOCOMOTION"
    )
    reviewed["sources"] = {
        "preregistration_lf_sha256": smoke.lf_sha256(PREREGISTRATION),
        "training_result_lf_sha256": smoke.lf_sha256(TRAINING_RESULT),
        "training_preregistration_lf_sha256": smoke.lf_sha256(TRAINING_PREREGISTRATION),
        "training_runner_lf_sha256": smoke.lf_sha256(TRAINING_RUNNER),
        "base_gate_runner_lf_sha256": smoke.lf_sha256(BASE_GATE_RUNNER),
        "gate_runner_lf_sha256": smoke.lf_sha256(Path(__file__)),
    }
    reviewed["authority"] = {
        "pass_authorizes_only": "a separate response-conditioned locomotion-training preregistration",
        "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
        "robot_clearance": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(reviewed, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(reviewed["status"])
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
