#!/usr/bin/env python3
"""Freeze one Winner-v45 static-target-teacher optimizer update on CPU."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v45_static_target_teacher_one_update_cpu_contract.json"
MARKDOWN = ANALYSIS / "WINNER_V45_STATIC_TARGET_TEACHER_ONE_UPDATE_CPU_CONTRACT_20260722.md"
V44_CONTRACT = ANALYSIS / "winner_v44_static_target_teacher_source_gradient_contract.json"
V44_RESULT = ANALYSIS / "winner_v44_static_target_teacher_source_gradient_result.json"
FROZEN_TEACHER_SCALE = 58.436370849609375
SOURCES = {
    "builder": Path("tools/build_winner_v45_static_target_teacher_one_update_cpu_contract.py"),
    "runner": Path("tools/run_winner_v45_static_target_teacher_one_update_cpu_proof.py"),
    "runner_tests": Path("tests/test_winner_v45_static_target_teacher_one_update_cpu_proof.py"),
    "preregistration_tests": Path("tests/test_winner_v45_static_target_teacher_one_update_cpu_preregistration.py"),
    "result_importer": Path("tools/import_winner_v45_static_target_teacher_one_update_cpu_result.py"),
    "result_importer_tests": Path("tests/test_winner_v45_static_target_teacher_one_update_cpu_import.py"),
    "workflow": Path(".github/workflows/winner-v45-static-target-teacher-one-update-cpu.yml"),
    "winner_v44_contract": Path("outputs/analysis/winner_v44_static_target_teacher_source_gradient_contract.json"),
    "winner_v44_result": Path("outputs/analysis/winner_v44_static_target_teacher_source_gradient_result.json"),
    "winner_v44_runner": Path("tools/run_winner_v44_static_target_teacher_source_gradient_contract.py"),
    "winner_v43_teacher": Path("patches/winner_v43_static_target_teacher.py"),
    "winner_v42_result": Path("outputs/analysis/winner_v42_static_target_teacher_table_result.json"),
    "winner_v32_result": Path("outputs/analysis/winner_v32_prefix_right_pitch_anchor_training_result.json"),
    "winner_v32_preregistration": Path("outputs/analysis/winner_v32_prefix_right_pitch_anchor_training_preregistration.json"),
    "winner_v22_result": Path("outputs/analysis/winner_v22_normalized_predictor_training_result.json"),
    "winner_v12_full_preregistration": Path("outputs/analysis/winner_v12_full_calibrator_training_preregistration.json"),
    "configuration_domain": Path("outputs/analysis/winner_v3_variable_configuration_replacement_preregistration.json"),
    "calibrator_design": Path("outputs/analysis/winner_v12_calibrator_training_preregistration.json"),
    "cpu_smoke": Path("tools/run_winner_v12_calibrator_cpu_smoke.py"),
    "full_training": Path("tools/run_winner_v12_full_calibrator_training.py"),
    "v22_support_gate": Path("tools/run_winner_v22_normalized_predictor_support_gate.py"),
    "v33_support_gate": Path("tools/run_winner_v33_prefix_right_pitch_anchor_support_gate.py"),
    "v24_common": Path("tools/run_winner_v24_symmetric_failure_cpu_contract.py"),
    "training_mechanics": Path("patches/winner_v12_calibrator_training.py"),
    "backend_networks": Path("patches/winner_v12_decomposed_backend_networks.py"),
    "pitch_margin_mechanics": Path("patches/winner_v15_pitch_margin_support.py"),
    "recurrent_mechanics": Path("patches/winner_v20_joint_recurrent_support.py"),
    "joint_mechanics": Path("patches/winner_v21_predictor_preserving_joint_support.py"),
    "snapshot_mechanics": Path("patches/winner_v21_predictor_preserving_joint_support_v2.py"),
    "normalized_predictor": Path("patches/winner_v22_normalized_predictor.py"),
    "gradient_composition": Path("patches/winner_v22_normalized_predictor_v2.py"),
    "failure_mechanics": Path("patches/winner_v24_symmetric_support_failure.py"),
    "baseline_objective": Path("patches/winner_v24_symmetric_support_failure_v2.py"),
    "training_objective": Path("patches/winner_v24_symmetric_support_failure_v3.py"),
    "prefix_anchor": Path("patches/winner_v29_prefix_right_pitch_anchor.py"),
    "environment_preparation": Path("tools/prepare_winner_v15_cpu_environment.py"),
    "runtime_observer": Path("artifacts/runtime_handoff/rdkx5_native_20260719/observer/winner_v2_contract.py"),
    "canonical_p30_fit": Path("outputs/analysis/fixed_target_p30_actuator_fit_20260712.json"),
}


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    if args.output.exists() or args.markdown.exists():
        raise FileExistsError("refusing to overwrite Winner-v45 contract")
    v44_contract = json.loads(V44_CONTRACT.read_text(encoding="utf-8"))
    v44 = json.loads(V44_RESULT.read_text(encoding="utf-8"))
    if (
        v44.get("status") != "PASS_WINNER_V44_STATIC_TARGET_TEACHER_SOURCE_GRADIENT_CONTRACT"
        or v44.get("decision")
        != "AUTHORIZE_ONE_UPDATE_STATIC_TARGET_TEACHER_CPU_PROOF_PREREGISTRATION_ONLY"
        or v44.get("failed_checks") != []
        or float(v44["objective_evidence"]["teacher_scale"]) != FROZEN_TEACHER_SCALE
        or v44.get("execution", {}).get("optimizer_updates") != 0
    ):
        raise ValueError("Winner-v44 did not authorize Winner-v45")
    sources = {
        name: {"path": path.as_posix(), "hash_mode": "lf", "sha256": lf_sha256(ROOT / path)}
        for name, path in SOURCES.items()
    }
    value = {
        "schema_version": "winner_v45.static_target_teacher_one_update_cpu_contract.v1",
        "status": "PREREGISTERED_WINNER_V45_STATIC_TARGET_TEACHER_ONE_UPDATE_CPU_PROOF",
        "decision": "AUTHORIZE_EXACT_ONE_STATIC_TARGET_TEACHER_OPTIMIZER_UPDATE_ONLY",
        "question": (
            "Does exactly one Adam update from Winner-v32 half, using the frozen "
            "Winner-v44 training-only teacher gradient and scale, preserve the complete "
            "deployable contract while reducing same-batch teacher MSE?"
        ),
        "objective": {
            "source_checkpoint": {"label": "winner_v32_half", "update": 251},
            "teacher_checkpoint": {"label": "winner_v22_final", "update": 100},
            "rollout_update_index": 251,
            "result_optimizer_count": 252,
            "episode_slots": 80,
            "ticks_per_slot": 250,
            "teacher_configuration_ids": v44_contract["objective"]["teacher_configuration_ids"],
            "heldout_teacher_configuration_ids_excluded": v44_contract["objective"]["heldout_teacher_configuration_ids_excluded"],
            "teacher_configuration_rows": 22,
            "teacher_action_indices": [2, 3, 4, 11, 12, 13],
            "teacher_scale": FROZEN_TEACHER_SCALE,
            "predictor_scale": 380.9135437011719,
            "prefix_anchor_scale": 197.3112030029297,
            "baseline": "unchanged Winner-v32 PPO plus normalized predictor plus prefix anchor",
            "combined_gradient": "baseline gradient plus frozen-scale Winner-v43 static-target teacher gradient",
            "optimizer": "restore exact Winner-v32 Adam count 251 and execute one update to 252",
            "post_update_gate": "same frozen-batch teacher MSE must be finite and strictly lower after the update",
            "no_action_replacement": True,
            "deployable_abi": {
                "inputs": [["obs", [1, 115]], ["previous_action", [1, 14]], ["h_in", [1, 64]]],
                "outputs": [["calibration_actions", [1, 14]], ["previous_action_out", [1, 14]], ["h_out", [1, 64]]],
            },
        },
        "pass_checks": [
            "bind exact Winner-v32 half snapshot and graph plus Winner-v22 teacher snapshot",
            "restore the exact source parameters and Adam state at count 251",
            "reproduce the frozen 80-slot update-251 objective dimensions without requiring cross-worker byte hashes",
            "apply exactly the recorded float32 teacher scale 58.436370849609375",
            "exclude all heldout teacher labels and supervise only six pitch indices",
            "execute exactly one Adam update to count 252",
            "strictly reduce same-batch teacher MSE",
            "change all twelve trainable leaves while preserving every frozen parameter leaf",
            "save and read back the complete snapshot and optimizer exactly",
            "export the unchanged stateful hard-bounded 115/14/64 ONNX ABI",
            "exclude teacher, configuration-table, and training-only state from the deployable graph",
            "execute zero formal support cells, continuation training, and robot access",
        ],
        "execution_now": {
            "rollout_episode_slots": 0,
            "scheduled_rollout_ticks": 0,
            "optimizer_updates": 0,
            "formal_support_cells": 0,
            "continuation_training_updates": 0,
            "deployable_graph_exports": 0,
            "robot_or_rdk_access": 0,
        },
        "execution_future": {
            "rollout_episode_slots": 80,
            "scheduled_rollout_ticks": 20000,
            "optimizer_updates": 1,
            "formal_support_cells": 0,
            "continuation_training_updates": 0,
            "deployable_graph_exports": 1,
            "robot_or_rdk_access": 0,
        },
        "artifact_inputs": v44_contract["artifact_inputs"],
        "frozen_v44_evidence": {
            "source_identity": v44["source_identity"],
            "rollout_evidence": v44["rollout_evidence"],
            "objective_evidence": v44["objective_evidence"],
        },
        "sources": sources,
        "source_manifest_sha256": canonical_sha256(sources),
        "authority": {
            "robot_clearance": False,
            "continuation_training_authorized": False,
            "one_update_authorized_by_this_preregistration": True,
            "runtime_implementation_authorized": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "pass_authorizes_only": "one separately frozen bounded static-target-teacher continuation preregistration",
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.markdown.write_text("\n".join([
        "# Winner-v45 static-target teacher one-update CPU contract", "",
        f"- Status: `{value['status']}`", f"- Decision: `{value['decision']}`",
        "- Optimizer count: `251 -> 252`", f"- Frozen teacher scale: `{FROZEN_TEACHER_SCALE}`",
        "- Formal support / continuation training / robot: `0 / 0 / 0`", "",
        value["question"], "",
        "This authorizes one CPU update only. A pass can authorize only a separately",
        "preregistered bounded continuation; it cannot select a checkpoint or grant robot clearance.", "",
    ]), encoding="utf-8")
    print(value["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
