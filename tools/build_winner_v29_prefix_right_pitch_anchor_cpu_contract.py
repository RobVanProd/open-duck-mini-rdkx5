#!/usr/bin/env python3
"""Freeze one Winner-v29 early right-pitch prefix-anchor CPU contract."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PATCHES = ROOT / "patches"
ANALYSIS = ROOT / "outputs/analysis"
sys.path.insert(0, str(PATCHES))

import winner_v29_prefix_right_pitch_anchor as v29  # noqa: E402


OUTPUT = ANALYSIS / "winner_v29_prefix_right_pitch_anchor_cpu_contract.json"
MARKDOWN = ANALYSIS / "WINNER_V29_PREFIX_RIGHT_PITCH_ANCHOR_CPU_CONTRACT_20260722.md"
V28_RESULT = ANALYSIS / "winner_v28_prefix_joint_group_causal_screen_result.json"
V28_PREREG = ANALYSIS / "winner_v28_prefix_joint_group_causal_screen_preregistration.json"
SOURCES = {
    "builder": Path("tools/build_winner_v29_prefix_right_pitch_anchor_cpu_contract.py"),
    "objective": Path("patches/winner_v29_prefix_right_pitch_anchor.py"),
    "objective_tests": Path("tests/test_winner_v29_prefix_right_pitch_anchor.py"),
    "runner": Path("tools/run_winner_v29_prefix_right_pitch_anchor_cpu_contract.py"),
    "runner_tests": Path("tests/test_winner_v29_prefix_right_pitch_anchor_cpu_contract.py"),
    "preregistration_tests": Path("tests/test_winner_v29_prefix_right_pitch_anchor_cpu_preregistration.py"),
    "result_importer": Path("tools/import_winner_v29_prefix_right_pitch_anchor_cpu_result.py"),
    "result_importer_tests": Path("tests/test_winner_v29_prefix_right_pitch_anchor_cpu_import.py"),
    "workflow": Path(".github/workflows/winner-v29-prefix-right-pitch-anchor-cpu-contract.yml"),
    "winner_v28_preregistration": Path("outputs/analysis/winner_v28_prefix_joint_group_causal_screen_preregistration.json"),
    "winner_v28_result": Path("outputs/analysis/winner_v28_prefix_joint_group_causal_screen_result.json"),
    "winner_v28_runner": Path("tools/run_winner_v28_prefix_joint_group_causal_screen.py"),
    "winner_v22_training_result": Path("outputs/analysis/winner_v22_normalized_predictor_training_result.json"),
    "winner_v24_training_result": Path("outputs/analysis/winner_v24_baseline_anchored_training_result.json"),
    "winner_v24_support_result": Path("outputs/analysis/winner_v24_baseline_anchored_support_gate_result.json"),
    "winner_v12_full_preregistration": Path("outputs/analysis/winner_v12_full_calibrator_training_preregistration.json"),
    "configuration_domain": Path("outputs/analysis/winner_v3_variable_configuration_replacement_preregistration.json"),
    "calibrator_design": Path("outputs/analysis/winner_v12_calibrator_training_preregistration.json"),
    "cpu_smoke": Path("tools/run_winner_v12_calibrator_cpu_smoke.py"),
    "full_training": Path("tools/run_winner_v12_full_calibrator_training.py"),
    "v22_support_gate": Path("tools/run_winner_v22_normalized_predictor_support_gate.py"),
    "v24_common": Path("tools/run_winner_v24_symmetric_failure_cpu_contract.py"),
    "v25_graph_helpers": Path("tools/run_winner_v25_directional_support_control_diagnostic.py"),
    "training_mechanics": Path("patches/winner_v12_calibrator_training.py"),
    "pitch_margin_mechanics": Path("patches/winner_v15_pitch_margin_support.py"),
    "recurrent_mechanics": Path("patches/winner_v20_joint_recurrent_support.py"),
    "joint_predictor_mechanics": Path("patches/winner_v21_predictor_preserving_joint_support.py"),
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
        raise FileExistsError("refusing to overwrite Winner-v29 contract")
    v28 = json.loads(V28_RESULT.read_text(encoding="utf-8"))
    v28_prereg = json.loads(V28_PREREG.read_text(encoding="utf-8"))
    if (
        v28.get("status") != "PASS_WINNER_V28_PREFIX_JOINT_GROUP_CAUSAL_SCREEN"
        or v28.get("classification") != "SINGLE_PREFIX_JOINT_GROUP_CAUSAL_LOCALIZATION"
        or v28.get("selected_group") != "RIGHT_PITCH_CHAIN"
        or v28.get("decision")
        != "AUTHORIZE_SELECTED_PREFIX_GROUP_OBJECTIVE_CPU_CONTRACT_PREREGISTRATION_ONLY"
        or v28.get("failed_checks") != []
        or v28.get("execution")
        != {
            "prefix_arms": 240,
            "source_recovery_rollouts": 480,
            "optimizer_updates": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        }
    ):
        raise ValueError("Winner-v28 did not authorize Winner-v29 contract")
    sources = {
        name: {
            "path": path.as_posix(),
            "hash_mode": "lf",
            "sha256": lf_sha256(ROOT / path),
        }
        for name, path in SOURCES.items()
    }
    value = {
        "schema_version": "winner_v29.prefix_right_pitch_anchor_cpu_contract.v1",
        "status": "PREREGISTERED_WINNER_V29_PREFIX_RIGHT_PITCH_ANCHOR_CPU_CONTRACT",
        "decision": "AUTHORIZE_ONE_ZERO_UPDATE_PREFIX_RIGHT_PITCH_ANCHOR_CPU_PROOF_ONLY",
        "question": (
            "Can the exact V28 right-pitch-chain ticks-0-7 intervention be represented as "
            "a finite, localized, default-off-exact differentiable objective before any "
            "optimizer update is allowed?"
        ),
        "objective": {
            "candidate_checkpoint": {"label": "winner_v24_final", "update": 200},
            "source_checkpoint": {"label": "winner_v22_final", "update": 100},
            "rollout_update_index": 200,
            "selected_training_configuration_ids": list(
                v29.SELECTED_TRAINING_CONFIGURATION_IDS
            ),
            "selected_episode_slots": v29.EXPECTED_SELECTED_EPISODES,
            "prefix_ticks": list(range(v29.PREFIX_TICKS)),
            "action_indices": list(v29.RIGHT_PITCH_ACTION_INDICES),
            "action_labels": ["right_hip_pitch", "right_knee", "right_ankle"],
            "selected_elements": v29.EXPECTED_ANCHOR_ELEMENTS,
            "candidate_action": (
                "deterministic graph-authoritative bounded mean action recomputed with "
                "Winner-v24 final on its rollout observations and realized previous actions"
            ),
            "source_action": (
                "stop-gradient deterministic graph-authoritative bounded mean action from "
                "Winner-v22 final on the same candidate observations and realized previous "
                "actions with its own shadow recurrent hidden state"
            ),
            "raw_loss": "mean squared candidate-minus-source action over selected elements",
            "baseline": (
                "unchanged Winner-v24 baseline-anchored PPO gradient plus frozen Winner-v22 "
                "normalized-predictor gradient at scale 380.9135437011719"
            ),
            "scale_rule": (
                "once on the exact zero-update batch, set anchor scale to baseline-gradient "
                "RMS divided by raw-anchor-gradient RMS over recurrent-core plus action-head "
                "leaves; freeze the resulting scalar for any later one-update preregistration"
            ),
            "gradient_balance_keys": list(v29.ANCHOR_GRADIENT_KEYS),
            "default_off": "bit-exact unchanged Winner-v24 gradient and all transition arrays",
            "no_action_replacement": True,
        },
        "pass_checks": [
            "bind exact Winner-v22 source and Winner-v24 final snapshot/ONNX bytes",
            "reproduce the exact update-200 80-slot CPU rollout and V24 baseline objective",
            "select exactly 16 two-plant negative-X training slots, ticks 0-7, indices 11-13",
            "match source and candidate JAX actions/hidden states to ONNX within 1e-7",
            "prove finite nonzero raw anchor loss and gradients on all six policy leaves",
            "prove exact zero anchor gradient on value, log-std, and predictor leaves",
            "derive one finite positive gradient-RMS balance scale without tuning",
            "prove default-off gradients and every transition array are bit-exact",
            "prove enabled gradient composition within 4e-6 and execute no update",
        ],
        "decision_tree": {
            "pass": "AUTHORIZE_SEPARATE_ONE_UPDATE_PREFIX_RIGHT_PITCH_ANCHOR_CPU_PROOF_PREREGISTRATION_ONLY",
            "hold": "DO_NOT_RUN_OPTIMIZER_UPDATE",
        },
        "execution_now": {
            "rollout_episode_slots": 0,
            "optimizer_updates": 0,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "artifact_inputs": v28_prereg["artifact_inputs"],
        "sources": sources,
        "source_manifest_sha256": canonical_sha256(sources),
        "authority": {
            "robot_clearance": False,
            "training_authorized": False,
            "one_update_authorized": False,
            "runtime_implementation_authorized": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "pass_authorizes_only": (
                "one separately preregistered CPU-only one-update proof using the exact "
                "recorded anchor scale"
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
                "# Winner-v29 prefix right-pitch anchor CPU contract",
                "",
                f"- Status: `{value['status']}`",
                f"- Decision: `{value['decision']}`",
                "- Candidate/source: `Winner-v24 final@200 / Winner-v22 final@100`",
                "- Selected mechanism: `ticks 0-7, action indices 11-13`",
                "- Selected training cells: `16 episodes / 384 action elements`",
                "- Optimizer / support / locomotion / robot: `0 / 0 / 0 / 0`",
                "",
                value["question"],
                "",
                "The proof calibrates one analytic gradient-RMS scale but executes no update.",
                "A pass can authorize only a separately frozen one-update CPU proof.",
                "It cannot authorize training, checkpoint selection, runtime work, or robot access.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(value["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
