#!/usr/bin/env python3
"""Freeze the Winner-v30 one-update prefix-anchor CPU proof."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v30_prefix_right_pitch_anchor_one_update_cpu_contract.json"
MARKDOWN = ANALYSIS / "WINNER_V30_PREFIX_RIGHT_PITCH_ANCHOR_ONE_UPDATE_CPU_CONTRACT_20260722.md"
V29_RESULT = ANALYSIS / "winner_v29_prefix_right_pitch_anchor_cpu_result.json"
V29_CONTRACT = ANALYSIS / "winner_v29_prefix_right_pitch_anchor_cpu_contract.json"
SOURCES = {
    "builder": Path("tools/build_winner_v30_prefix_right_pitch_anchor_one_update_cpu_contract.py"),
    "runner": Path("tools/run_winner_v30_prefix_right_pitch_anchor_one_update_cpu_proof.py"),
    "runner_tests": Path("tests/test_winner_v30_prefix_right_pitch_anchor_one_update_cpu_proof.py"),
    "preregistration_tests": Path("tests/test_winner_v30_prefix_right_pitch_anchor_one_update_cpu_preregistration.py"),
    "result_importer": Path("tools/import_winner_v30_prefix_right_pitch_anchor_one_update_cpu_result.py"),
    "result_importer_tests": Path("tests/test_winner_v30_prefix_right_pitch_anchor_one_update_cpu_import.py"),
    "workflow": Path(".github/workflows/winner-v30-prefix-right-pitch-anchor-one-update-cpu-proof.yml"),
    "winner_v29_contract": Path("outputs/analysis/winner_v29_prefix_right_pitch_anchor_cpu_contract.json"),
    "winner_v29_result": Path("outputs/analysis/winner_v29_prefix_right_pitch_anchor_cpu_result.json"),
    "winner_v29_objective": Path("patches/winner_v29_prefix_right_pitch_anchor.py"),
    "winner_v29_objective_tests": Path("tests/test_winner_v29_prefix_right_pitch_anchor.py"),
    "winner_v29_runner": Path("tools/run_winner_v29_prefix_right_pitch_anchor_cpu_contract.py"),
    "winner_v22_training_result": Path("outputs/analysis/winner_v22_normalized_predictor_training_result.json"),
    "winner_v24_training_result": Path("outputs/analysis/winner_v24_baseline_anchored_training_result.json"),
    "winner_v12_full_preregistration": Path("outputs/analysis/winner_v12_full_calibrator_training_preregistration.json"),
    "configuration_domain": Path("outputs/analysis/winner_v3_variable_configuration_replacement_preregistration.json"),
    "calibrator_design": Path("outputs/analysis/winner_v12_calibrator_training_preregistration.json"),
    "cpu_smoke": Path("tools/run_winner_v12_calibrator_cpu_smoke.py"),
    "full_training": Path("tools/run_winner_v12_full_calibrator_training.py"),
    "v22_support_gate": Path("tools/run_winner_v22_normalized_predictor_support_gate.py"),
    "v24_common": Path("tools/run_winner_v24_symmetric_failure_cpu_contract.py"),
    "training_mechanics": Path("patches/winner_v12_calibrator_training.py"),
    "backend_networks": Path("patches/winner_v12_decomposed_backend_networks.py"),
    "pitch_margin_mechanics": Path("patches/winner_v15_pitch_margin_support.py"),
    "recurrent_mechanics": Path("patches/winner_v20_joint_recurrent_support.py"),
    "joint_predictor_mechanics": Path("patches/winner_v21_predictor_preserving_joint_support.py"),
    "snapshot_mechanics": Path("patches/winner_v21_predictor_preserving_joint_support_v2.py"),
    "normalized_predictor_mechanics": Path("patches/winner_v22_normalized_predictor.py"),
    "gradient_composition_mechanics": Path("patches/winner_v22_normalized_predictor_v2.py"),
    "v24_failure_mechanics": Path("patches/winner_v24_symmetric_support_failure.py"),
    "v24_baseline_objective": Path("patches/winner_v24_symmetric_support_failure_v2.py"),
    "v24_training_objective": Path("patches/winner_v24_symmetric_support_failure_v3.py"),
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
        raise FileExistsError("refusing to overwrite Winner-v30 contract")
    zero = json.loads(V29_RESULT.read_text(encoding="utf-8"))
    prior = json.loads(V29_CONTRACT.read_text(encoding="utf-8"))
    if (
        zero.get("status")
        != "PASS_WINNER_V29_PREFIX_RIGHT_PITCH_ANCHOR_CPU_CONTRACT"
        or zero.get("decision")
        != "AUTHORIZE_SEPARATE_ONE_UPDATE_PREFIX_RIGHT_PITCH_ANCHOR_CPU_PROOF_PREREGISTRATION_ONLY"
        or zero.get("failed_checks") != []
        or zero.get("execution")
        != {
            "rollout_episode_slots": 80,
            "optimizer_updates": 0,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        }
        or zero["objective_evidence"].get("anchor_scale") != 197.3112030029297
    ):
        raise ValueError("Winner-v29 did not authorize Winner-v30")
    sources = {
        name: {
            "path": path.as_posix(),
            "hash_mode": "lf",
            "sha256": lf_sha256(ROOT / path),
        }
        for name, path in SOURCES.items()
    }
    value = {
        "schema_version": "winner_v30.prefix_right_pitch_anchor_one_update_cpu_contract.v1",
        "status": "PREREGISTERED_WINNER_V30_PREFIX_RIGHT_PITCH_ANCHOR_ONE_UPDATE_CPU_PROOF",
        "decision": "AUTHORIZE_EXACT_ONE_PREFIX_RIGHT_PITCH_ANCHOR_OPTIMIZER_UPDATE_ONLY",
        "question": (
            "Does exactly one Adam update from Winner-v24 final, using the frozen "
            "Winner-v29 prefix-anchor gradient and scale, preserve the complete software "
            "contract while reducing the selected same-batch anchor MSE?"
        ),
        "objective": {
            "candidate_checkpoint": {"label": "winner_v24_final", "update": 200},
            "teacher_checkpoint": {"label": "winner_v22_final", "update": 100},
            "rollout_update_index": 200,
            "selected_training_configuration_ids": prior["objective"][
                "selected_training_configuration_ids"
            ],
            "prefix_ticks": list(range(8)),
            "action_indices": [11, 12, 13],
            "selected_elements": 384,
            "anchor_scale": 197.3112030029297,
            "baseline": (
                "unchanged Winner-v24 baseline-anchored PPO gradient plus frozen Winner-v22 "
                "normalized-predictor gradient at scale 380.9135437011719"
            ),
            "combined_gradient": (
                "baseline combined gradient plus 197.3112030029297 times the frozen "
                "Winner-v29 prefix-anchor gradient"
            ),
            "optimizer": "restore exact Winner-v24 Adam count 200 and execute one update to 201",
            "post_update_gate": (
                "on the identical frozen batch, selected raw anchor MSE must be finite and "
                "strictly lower after the update"
            ),
            "no_action_replacement": True,
        },
        "pass_checks": [
            "reproduce the exact Winner-v29 update-200 batch, loss, gradients, and scale",
            "restore the exact Winner-v24 final parameters and Adam state at count 200",
            "execute exactly one Adam update to count 201",
            "keep all twelve combined gradients nonzero and change all twelve leaves",
            "strictly reduce selected same-batch anchor MSE without another rollout",
            "save and read back the complete snapshot and optimizer exactly",
            "export a stateful hard-bounded ONNX graph with the unchanged 115/14/64 ABI",
            "execute zero formal support cells, locomotion steps, and robot access",
        ],
        "execution_now": {
            "rollout_episode_slots": 0,
            "optimizer_updates": 0,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "execution_future": {
            "rollout_episode_slots": 80,
            "optimizer_updates": 1,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "artifact_inputs": prior["artifact_inputs"],
        "sources": sources,
        "source_manifest_sha256": canonical_sha256(sources),
        "authority": {
            "robot_clearance": False,
            "training_authorized": False,
            "one_update_authorized_by_this_preregistration": True,
            "runtime_implementation_authorized": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "pass_authorizes_only": (
                "one separately frozen prefix right-pitch anchor training preregistration"
            ),
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown.write_text(
        "\n".join(
            [
                "# Winner-v30 prefix right-pitch anchor one-update CPU contract",
                "",
                f"- Status: `{value['status']}`",
                f"- Decision: `{value['decision']}`",
                "- Source optimizer count: `200`",
                "- Authorized optimizer count: `201`",
                "- Frozen anchor scale: `197.3112030029297`",
                "- Formal support / locomotion / robot: `0 / 0 / 0`",
                "",
                value["question"],
                "",
                "This contract authorizes one update only. A pass can authorize only a",
                "separately preregistered bounded training continuation; it cannot authorize",
                "checkpoint selection, deployment, runtime work, Gate 5, or robot access.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(value["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
