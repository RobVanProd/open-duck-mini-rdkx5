#!/usr/bin/env python3
"""Freeze the sole Winner-v46 bounded static-target-teacher training arm."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v46_static_target_teacher_training_preregistration.json"
MARKDOWN = ANALYSIS / "WINNER_V46_STATIC_TARGET_TEACHER_TRAINING_PREREGISTRATION_20260722.md"
V45_RESULT = ANALYSIS / "winner_v45_static_target_teacher_one_update_cpu_result.json"
V22_RESULT = ANALYSIS / "winner_v22_normalized_predictor_training_result.json"
SOURCES = {
    "builder": Path("tools/build_winner_v46_static_target_teacher_training_preregistration.py"),
    "runner": Path("tools/run_winner_v46_static_target_teacher_training.py"),
    "workflow": Path(".github/workflows/winner-v46-static-target-teacher-training.yml"),
    "runner_tests": Path("tests/test_winner_v46_static_target_teacher_training.py"),
    "preregistration_tests": Path("tests/test_winner_v46_static_target_teacher_training_preregistration.py"),
    "importer": Path("tools/import_winner_v46_static_target_teacher_training.py"),
    "importer_tests": Path("tests/test_winner_v46_static_target_teacher_training_import.py"),
    "environment_builder": Path("tools/prepare_winner_v15_cpu_environment.py"),
    "cpu_smoke": Path("tools/run_winner_v12_calibrator_cpu_smoke.py"),
    "full_training_runner": Path("tools/run_winner_v12_full_calibrator_training.py"),
    "v22_gate_runner": Path("tools/run_winner_v22_normalized_predictor_support_gate.py"),
    "v24_contract_common": Path("tools/run_winner_v24_symmetric_failure_cpu_contract.py"),
    "v44_teacher_batch": Path("tools/run_winner_v44_static_target_teacher_source_gradient_contract.py"),
    "base_training": Path("patches/winner_v12_calibrator_training.py"),
    "network_export": Path("patches/winner_v12_decomposed_backend_networks.py"),
    "pitch_margin": Path("patches/winner_v15_pitch_margin_support.py"),
    "recurrent_support": Path("patches/winner_v20_joint_recurrent_support.py"),
    "joint_support": Path("patches/winner_v21_predictor_preserving_joint_support.py"),
    "snapshot_mechanics": Path("patches/winner_v21_predictor_preserving_joint_support_v2.py"),
    "normalized_predictor": Path("patches/winner_v22_normalized_predictor.py"),
    "gradient_composition": Path("patches/winner_v22_normalized_predictor_v2.py"),
    "transition": Path("patches/winner_v24_symmetric_support_failure.py"),
    "transition_v2": Path("patches/winner_v24_symmetric_support_failure_v2.py"),
    "transition_v3": Path("patches/winner_v24_symmetric_support_failure_v3.py"),
    "prefix_anchor": Path("patches/winner_v29_prefix_right_pitch_anchor.py"),
    "static_target_teacher": Path("patches/winner_v43_static_target_teacher.py"),
    "v42_teacher_table": Path("outputs/analysis/winner_v42_static_target_teacher_table_result.json"),
    "v45_contract": Path("outputs/analysis/winner_v45_static_target_teacher_one_update_cpu_contract.json"),
    "v45_result": Path("outputs/analysis/winner_v45_static_target_teacher_one_update_cpu_result.json"),
    "v22_result": Path("outputs/analysis/winner_v22_normalized_predictor_training_result.json"),
    "full_training_preregistration": Path("outputs/analysis/winner_v12_full_calibrator_training_preregistration.json"),
    "domain": Path("outputs/analysis/winner_v3_variable_configuration_replacement_preregistration.json"),
    "calibrator_preregistration": Path("outputs/analysis/winner_v12_calibrator_training_preregistration.json"),
    "runtime_observer": Path("artifacts/runtime_handoff/rdkx5_native_20260719/observer/winner_v2_contract.py"),
    "canonical_p30_fit": Path("outputs/analysis/fixed_target_p30_actuator_fit_20260712.json"),
}


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    if args.output.exists() or args.markdown.exists():
        raise FileExistsError("refusing to overwrite Winner-v46 preregistration")
    v45 = json.loads(V45_RESULT.read_text(encoding="utf-8"))
    v22 = json.loads(V22_RESULT.read_text(encoding="utf-8"))
    if (
        v45.get("status") != "PASS_WINNER_V45_STATIC_TARGET_TEACHER_ONE_UPDATE_CPU_PROOF"
        or v45.get("decision") != "AUTHORIZE_STATIC_TARGET_TEACHER_TRAINING_PREREGISTRATION_ONLY"
        or v45.get("failed_checks") != []
        or v45.get("snapshot", {}).get("completed_updates") != 252
        or v45.get("repository_attribution", {}).get("github_run_attempt") != 1
        or v22.get("status") != "PASS_WINNER_V22_NORMALIZED_PREDICTOR_TRAINING_ARTIFACT"
        or v22.get("failed_checks") != []
    ):
        raise ValueError("Winner-v46 source evidence does not authorize training")
    sources = {
        name: {"path": path.as_posix(), "hash_mode": "lf", "sha256": lf_sha256(ROOT / path)}
        for name, path in SOURCES.items()
    }
    value = {
        "schema_version": "winner_v46.static_target_teacher_training_preregistration.v1",
        "status": "PREREGISTERED_WINNER_V46_STATIC_TARGET_TEACHER_TRAINING",
        "decision": "AUTHORIZE_ONE_100_UPDATE_STATIC_TARGET_TEACHER_ARM_ONLY",
        "causal_hypothesis": (
            "Winner-v42 proved a shared two-plant static support target for every failure "
            "configuration; V43/V44 isolated a training-only six-pitch gradient and its "
            "sole scale; V45 proved one exact update reduces same-batch teacher error while "
            "preserving the deployable graph. One inherited-length continuation now tests persistence."
        ),
        "source_checkpoint": {
            "completed_updates": 252,
            "optimizer_count": 252,
            "snapshot": v45["snapshot"],
            "graph": v45["graph"],
            "repository_attribution": v45["repository_attribution"],
        },
        "teacher_checkpoint": {
            "completed_updates": 100,
            "optimizer_count": 100,
            "snapshot": v22["snapshot_manifest"][99],
            "graph": v22["persistent_checkpoints"][1]["graph"],
            "repository_attribution": v22["repository_attribution"],
        },
        "frozen_training": {
            "source_completed_updates": 252,
            "source_optimizer_count": 252,
            "continuation_optimizer_updates": 100,
            "final_optimizer_count": 352,
            "environments_per_update": 80,
            "ticks_per_environment": 250,
            "scheduled_episode_slots": 2_000_000,
            "training_root_seed": 120120,
            "learning_rate": 0.0001,
            "predictor_scale": 380.9135437011719,
            "prefix_anchor_scale": 197.3112030029297,
            "static_target_teacher_scale": 58.436370849609375,
            "rollout_update_indices": [252, 351],
            "persistent_snapshots": "atomic digest-protected readback after every update",
            "persistent_checkpoints": {"half": 302, "final": 352},
            "duration_source": "inherit Winner-v32 100-update half/final persistence design without search",
            "coefficient_or_length_search": False,
        },
        "objective": {
            "ppo": "unchanged Winner-v32 recurrent PPO objective and failure transition shaping",
            "predictor": "unchanged normalized successor predictor at scale 380.9135437011719",
            "prefix_anchor": "unchanged Winner-v32 prefix right-pitch anchor at scale 197.3112030029297",
            "static_target_teacher": {
                "table": "exact imported Winner-v42 selected shared two-plant targets",
                "configuration_ids": v45["objective"]["teacher_configuration_ids"],
                "heldout_ids_excluded": v45["objective"]["heldout_teacher_configuration_ids_excluded"],
                "configuration_plant_rows": 22,
                "action_indices": [2, 3, 4, 11, 12, 13],
                "target": "stop-gradient graph-bounded static target relative to realized previous action",
                "candidate": "deterministic graph-authoritative bounded recurrent mean",
                "loss": "pitch-mask mean squared error",
                "scale": 58.436370849609375,
                "action_replacement": False,
                "actor_input_added": False,
            },
            "combined_gradient": "existing Winner-v32 gradient plus exact frozen-scale static-target-teacher gradient",
        },
        "stop_rules": [
            "stop if source snapshot, graph, Adam state, or teacher snapshot differs",
            "stop if any environment, population, receipt, action boundary, reward, mask, or transition differs",
            "stop if a heldout configuration receives a teacher label",
            "stop unless every update selects exactly 22 configuration/plant rows and only six pitch indices",
            "stop if teacher gradients affect value, log-std, or predictor leaves",
            "stop if hidden replay exceeds 1e-6 or successor masks disagree",
            "stop if any combined gradient, parameter delta, loss, metric, snapshot, or ONNX contract is invalid",
            "do not run or inspect the formal support gate in this workflow",
            "do not select a checkpoint from training losses or intermediate behavior",
        ],
        "post_training_selection": {
            "authorized_now": False,
            "checkpoint_rule": "both checkpoints remain evidence until one separately frozen support and context gate classifies both",
            "pass_authorizes_only": "a separately preregistered half/final support and context gate",
        },
        "execution_now": {
            "optimizer_updates": 0, "formal_support_cells": 0,
            "locomotion_steps": 0, "robot_or_rdk_access": 0,
        },
        "authority": {
            "robot_clearance": False,
            "training_authorized": True,
            "formal_support_gate_authorized": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "pass_authorizes_only": "a separate static-target-teacher support gate preregistration",
        },
        "sources": sources,
        "source_manifest_sha256": canonical_sha256(sources),
    }
    args.output.write_text(json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.markdown.write_text("\n".join([
        "# Winner-v46 static-target teacher training preregistration", "",
        f"- Status: `{value['status']}`", f"- Decision: `{value['decision']}`",
        "- Source / half / final optimizer count: `252 / 302 / 352`",
        "- Continuation: `100 updates`, `80 x 250` scheduled ticks per update",
        "- Predictor / prefix / teacher scales: `380.9135437011719 / 197.3112030029297 / 58.436370849609375`",
        "- Formal support / robot: `0 / 0`", "", value["causal_hypothesis"], "",
        "No checkpoint is selected from training metrics. A passing artifact authorizes",
        "only a separately frozen half/final support and context gate.", "",
    ]), encoding="utf-8")
    print(value["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

