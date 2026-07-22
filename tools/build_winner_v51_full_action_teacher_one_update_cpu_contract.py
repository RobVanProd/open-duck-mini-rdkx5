#!/usr/bin/env python3
"""Freeze one Winner-v51 full-action-teacher optimizer update on CPU."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v51_full_action_teacher_one_update_cpu_contract.json"
MARKDOWN = ANALYSIS / "WINNER_V51_FULL_ACTION_TEACHER_ONE_UPDATE_CPU_CONTRACT_20260722.md"
V50_CONTRACT = ANALYSIS / "winner_v50_full_action_teacher_source_gradient_contract.json"
V50C_RESULT = ANALYSIS / "winner_v50c_gradient_backward_error_attribution_result.json"
V50C_RESULT_SHA256 = "ce3bbe554b9497b744f792e1e4b53986cc3c48efe582bff5ac23e6e51d2883d3"
FULL_ACTION_TEACHER_SCALE = 136.35153198242188
SOURCES = {
    "builder": Path("tools/build_winner_v51_full_action_teacher_one_update_cpu_contract.py"),
    "runner": Path("tools/run_winner_v51_full_action_teacher_one_update_cpu_proof.py"),
    "tests": Path("tests/test_winner_v51_full_action_teacher_one_update_cpu_proof.py"),
    "winner_v50_contract": Path("outputs/analysis/winner_v50_full_action_teacher_source_gradient_contract.json"),
    "winner_v50_result": Path("outputs/analysis/winner_v50_full_action_teacher_source_gradient_result.json"),
    "winner_v50_runner": Path("tools/run_winner_v50_full_action_teacher_source_gradient_contract.py"),
    "winner_v50c_result": Path("outputs/analysis/winner_v50c_gradient_backward_error_attribution_result.json"),
    "winner_v49_teacher": Path("patches/winner_v49_full_action_static_target_teacher.py"),
    "winner_v46_result": Path("outputs/analysis/winner_v46_static_target_teacher_training_result.json"),
    "winner_v46_preregistration": Path("outputs/analysis/winner_v46_static_target_teacher_training_preregistration.json"),
    "winner_v22_result": Path("outputs/analysis/winner_v22_normalized_predictor_training_result.json"),
    "backend_networks": Path("patches/winner_v12_decomposed_backend_networks.py"),
    "training_mechanics": Path("patches/winner_v12_calibrator_training.py"),
    "joint_mechanics": Path("patches/winner_v21_predictor_preserving_joint_support.py"),
    "snapshot_mechanics": Path("patches/winner_v21_predictor_preserving_joint_support_v2.py"),
    "prefix_anchor": Path("patches/winner_v29_prefix_right_pitch_anchor.py"),
    "cpu_smoke": Path("tools/run_winner_v12_calibrator_cpu_smoke.py"),
    "canonical_p30_fit": Path("outputs/analysis/fixed_target_p30_actuator_fit_20260712.json"),
}


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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite Winner-v51 contract: {path}")

    v50_contract = json.loads(V50_CONTRACT.read_text(encoding="utf-8"))
    v50c = json.loads(V50C_RESULT.read_text(encoding="utf-8"))
    if (
        sha256(V50C_RESULT) != V50C_RESULT_SHA256
        or v50c.get("status")
        != "PASS_WINNER_V50C_GRADIENT_BACKWARD_ERROR_ATTRIBUTION"
        or v50c.get("decision")
        != "AUTHORIZE_FULL_ACTION_TEACHER_ONE_UPDATE_CPU_PREREGISTRATION_ONLY"
        or v50c.get("execution", {}).get("optimizer_updates") != 0
        or v50_contract.get("source_selection", {}).get("selected_update") != 352
    ):
        raise ValueError("Winner-v50c did not authorize Winner-v51")

    sources = {
        name: {"path": path.as_posix(), "hash_mode": "lf", "sha256": lf_sha256(ROOT / path)}
        for name, path in SOURCES.items()
    }
    value = {
        "schema_version": "winner_v51.full_action_teacher_one_update_cpu_contract.v1",
        "status": "PREREGISTERED_WINNER_V51_FULL_ACTION_TEACHER_ONE_UPDATE_CPU_PROOF",
        "decision": "AUTHORIZE_EXACT_ONE_FULL_ACTION_TEACHER_OPTIMIZER_UPDATE_ONLY",
        "question": (
            "Does exactly one Adam update from the terminal Winner-v46 state, using "
            "the frozen full-14D teacher replacement, preserve the complete stateful "
            "policy contract while reducing same-batch full-action teacher MSE?"
        ),
        "objective": {
            "source_checkpoint": {"label": "winner_v46_final", "update": 352},
            "teacher_checkpoint": {"label": "winner_v22_final", "update": 100},
            "rollout_update_index": 352,
            "result_optimizer_count": 353,
            "episode_slots": 80,
            "ticks_per_slot": 250,
            "teacher_configuration_ids": v50_contract["objective"]["teacher_configuration_ids"],
            "heldout_teacher_configuration_ids_excluded": v50_contract["objective"]["heldout_teacher_configuration_ids_excluded"],
            "teacher_configuration_rows": 22,
            "teacher_action_indices": list(range(14)),
            "teacher_scale": FULL_ACTION_TEACHER_SCALE,
            "predictor_scale": 380.9135437011719,
            "prefix_anchor_scale": 197.3112030029297,
            "baseline": "unchanged Winner-v46 PPO plus normalized predictor plus prefix anchor",
            "combined_gradient": "baseline composed gradient plus frozen-scale full-14D teacher gradient",
            "optimizer": "restore exact Winner-v46 Adam count 352 and execute one update to 353",
            "post_update_gate": "same frozen-batch full-action teacher MSE must be finite and strictly lower",
            "no_action_replacement": True,
            "deployable_abi": {
                "inputs": [["obs", [1, 115]], ["previous_action", [1, 14]], ["h_in", [1, 64]]],
                "outputs": [["calibration_actions", [1, 14]], ["previous_action_out", [1, 14]], ["h_out", [1, 64]]],
            },
        },
        "pass_checks": [
            "bind exact Winner-v46 final snapshot/graph, Winner-v22 teacher, and V50c pass",
            "restore source parameters and Adam state exactly at count 352",
            "recompute the exact 80-slot update-352 V50 rollout and full-action gradient",
            "apply exactly the algebraic float32 teacher scale 136.35153198242188",
            "exclude all heldout labels and supervise all 14 actions on exactly 22 plant rows",
            "execute exactly one Adam update to count 353",
            "strictly reduce same-batch full-action teacher MSE",
            "change all trainable leaves while preserving every frozen parameter leaf",
            "save and read back the complete parameter and optimizer state exactly",
            "export one candidate graph with the unchanged stateful hard-bounded 115/14/64 ABI",
            "exclude teacher and training-only state from the candidate graph",
            "execute zero support cells, continuation updates, and robot access",
        ],
        "execution_now": {
            "rollout_episode_slots": 0,
            "scheduled_rollout_ticks": 0,
            "optimizer_updates": 0,
            "formal_support_cells": 0,
            "continuation_training_updates": 0,
            "candidate_graph_exports": 0,
            "robot_or_rdk_access": 0,
        },
        "execution_future": {
            "rollout_episode_slots": 80,
            "scheduled_rollout_ticks": 20_000,
            "optimizer_updates": 1,
            "formal_support_cells": 0,
            "continuation_training_updates": 0,
            "candidate_graph_exports": 1,
            "robot_or_rdk_access": 0,
        },
        "artifact_inputs": v50_contract["artifact_inputs"],
        "frozen_v50c_result": {
            "path": V50C_RESULT.relative_to(ROOT).as_posix(),
            "bytes": V50C_RESULT.stat().st_size,
            "sha256": sha256(V50C_RESULT),
        },
        "sources": sources,
        "source_manifest_sha256": canonical_sha256(sources),
        "authority": {
            "robot_clearance": False,
            "continuation_training_authorized": False,
            "one_update_authorized_by_this_preregistration": True,
            "runtime_implementation_authorized": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "pass_authorizes_only": "one separately frozen bounded full-action continuation preregistration",
        },
    }
    args.output.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown.write_text(
        "\n".join(
            [
                "# Winner-v51 full-action teacher one-update CPU contract",
                "",
                f"- Status: `{value['status']}`",
                f"- Decision: `{value['decision']}`",
                "- Optimizer count: `352 -> 353`",
                f"- Full-action teacher scale: `{FULL_ACTION_TEACHER_SCALE}`",
                "- Formal support / continuation / robot: `0 / 0 / 0`",
                "",
                value["question"],
                "",
                "This authorizes one CPU update only. A pass can authorize only a",
                "separately preregistered bounded continuation; it cannot select a",
                "deployment checkpoint or grant robot clearance.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(value["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
