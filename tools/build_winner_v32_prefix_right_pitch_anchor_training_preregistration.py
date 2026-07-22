#!/usr/bin/env python3
"""Freeze the sole Winner-v32 bounded prefix-anchor training arm."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v32_prefix_right_pitch_anchor_training_preregistration.json"
MARKDOWN = ANALYSIS / "WINNER_V32_PREFIX_RIGHT_PITCH_ANCHOR_TRAINING_PREREGISTRATION_20260722.md"
V31_RESULT = ANALYSIS / "winner_v31_cross_worker_replay_attribution_result.json"
V30_HOLD = ANALYSIS / "winner_v30_prefix_right_pitch_anchor_one_update_cpu_hold_result.json"
V29_RESULT = ANALYSIS / "winner_v29_prefix_right_pitch_anchor_cpu_result.json"
V24_TRAINING = ANALYSIS / "winner_v24_baseline_anchored_training_result.json"
V24_PREREG = ANALYSIS / "winner_v24_baseline_anchored_training_preregistration.json"
V22_TRAINING = ANALYSIS / "winner_v22_normalized_predictor_training_result.json"
SOURCES = {
    "builder": Path("tools/build_winner_v32_prefix_right_pitch_anchor_training_preregistration.py"),
    "runner": Path("tools/run_winner_v32_prefix_right_pitch_anchor_training.py"),
    "workflow": Path(".github/workflows/winner-v32-prefix-right-pitch-anchor-training.yml"),
    "runner_tests": Path("tests/test_winner_v32_prefix_right_pitch_anchor_training.py"),
    "preregistration_tests": Path("tests/test_winner_v32_prefix_right_pitch_anchor_training_preregistration.py"),
    "importer": Path("tools/import_winner_v32_prefix_right_pitch_anchor_training.py"),
    "importer_tests": Path("tests/test_winner_v32_prefix_right_pitch_anchor_training_import.py"),
    "environment_builder": Path("tools/prepare_winner_v15_cpu_environment.py"),
    "cpu_smoke": Path("tools/run_winner_v12_calibrator_cpu_smoke.py"),
    "full_training_runner": Path("tools/run_winner_v12_full_calibrator_training.py"),
    "v22_gate_runner": Path("tools/run_winner_v22_normalized_predictor_support_gate.py"),
    "v24_contract_common": Path("tools/run_winner_v24_symmetric_failure_cpu_contract.py"),
    "base_training": Path("patches/winner_v12_calibrator_training.py"),
    "network_export": Path("patches/winner_v12_decomposed_backend_networks.py"),
    "v15_pitch_margin": Path("patches/winner_v15_pitch_margin_support.py"),
    "v20_recurrent_support": Path("patches/winner_v20_joint_recurrent_support.py"),
    "v21_predictor_preserving": Path("patches/winner_v21_predictor_preserving_joint_support.py"),
    "v22_normalized_predictor": Path("patches/winner_v22_normalized_predictor.py"),
    "v22_gradient_composition": Path("patches/winner_v22_normalized_predictor_v2.py"),
    "v24_transition": Path("patches/winner_v24_symmetric_support_failure.py"),
    "v24_transition_v2": Path("patches/winner_v24_symmetric_support_failure_v2.py"),
    "v24_transition_v3": Path("patches/winner_v24_symmetric_support_failure_v3.py"),
    "v29_anchor": Path("patches/winner_v29_prefix_right_pitch_anchor.py"),
    "v29_anchor_tests": Path("tests/test_winner_v29_prefix_right_pitch_anchor.py"),
    "runtime_observer": Path("artifacts/runtime_handoff/rdkx5_native_20260719/observer/winner_v2_contract.py"),
    "canonical_p30_fit": Path("outputs/analysis/fixed_target_p30_actuator_fit_20260712.json"),
    "calibrator_preregistration": Path("outputs/analysis/winner_v12_calibrator_training_preregistration.json"),
    "full_training_preregistration": Path("outputs/analysis/winner_v12_full_calibrator_training_preregistration.json"),
    "domain": Path("outputs/analysis/winner_v3_variable_configuration_replacement_preregistration.json"),
    "v22_training_result": Path("outputs/analysis/winner_v22_normalized_predictor_training_result.json"),
    "v24_training_preregistration": Path("outputs/analysis/winner_v24_baseline_anchored_training_preregistration.json"),
    "v24_training_result": Path("outputs/analysis/winner_v24_baseline_anchored_training_result.json"),
    "v29_result": Path("outputs/analysis/winner_v29_prefix_right_pitch_anchor_cpu_result.json"),
    "v30_hold_result": Path("outputs/analysis/winner_v30_prefix_right_pitch_anchor_one_update_cpu_hold_result.json"),
    "v31_attribution_result": Path("outputs/analysis/winner_v31_cross_worker_replay_attribution_result.json"),
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
        raise FileExistsError("refusing to overwrite Winner-v32 preregistration")
    v31 = json.loads(V31_RESULT.read_text(encoding="utf-8"))
    v30 = json.loads(V30_HOLD.read_text(encoding="utf-8"))
    v29 = json.loads(V29_RESULT.read_text(encoding="utf-8"))
    v24 = json.loads(V24_TRAINING.read_text(encoding="utf-8"))
    v24_prereg = json.loads(V24_PREREG.read_text(encoding="utf-8"))
    v22 = json.loads(V22_TRAINING.read_text(encoding="utf-8"))
    if (
        v31.get("status") != "PASS_WINNER_V31_CROSS_WORKER_REPLAY_ATTRIBUTION"
        or v31.get("classification") != "CROSS_WORKER_FLOAT_REPLAY_ONLY"
        or v31.get("decision")
        != "AUTHORIZE_PREFIX_RIGHT_PITCH_ANCHOR_TRAINING_PREREGISTRATION_USING_PRESERVED_COUNT_201_ARTIFACT_ONLY"
        or v31.get("failed_checks") != []
        or v30.get("status")
        != "HOLD_WINNER_V30_PREFIX_RIGHT_PITCH_ANCHOR_ONE_UPDATE_CPU_PROOF"
        or v30.get("snapshot", {}).get("completed_updates") != 201
        or v30.get("repository_attribution", {}).get("github_run_attempt") != 1
        or v29.get("status")
        != "PASS_WINNER_V29_PREFIX_RIGHT_PITCH_ANCHOR_CPU_CONTRACT"
        or v29.get("failed_checks") != []
        or v24.get("status")
        != "PASS_WINNER_V24_BASELINE_ANCHORED_TRAINING_ARTIFACT"
        or v24.get("failed_checks") != []
        or v22.get("status")
        != "PASS_WINNER_V22_NORMALIZED_PREDICTOR_TRAINING_ARTIFACT"
        or v22.get("failed_checks") != []
    ):
        raise ValueError("Winner-v32 source evidence does not authorize training")
    if (
        v29["objective_evidence"]["balance"]["anchor_scale"]
        != 197.3112030029297
        or v29["rollout_evidence"]["selected_elements"] != 384
    ):
        raise ValueError("Winner-v32 anchor contract changed")
    sources = {
        name: {
            "path": path.as_posix(),
            "hash_mode": "lf",
            "sha256": lf_sha256(ROOT / path),
        }
        for name, path in SOURCES.items()
    }
    source_attribution = v30["repository_attribution"]
    teacher_attribution = v22["repository_attribution"]
    value = {
        "schema_version": "winner_v32.prefix_right_pitch_anchor_training_preregistration.v1",
        "status": "PREREGISTERED_WINNER_V32_PREFIX_RIGHT_PITCH_ANCHOR_TRAINING",
        "decision": "AUTHORIZE_ONE_100_UPDATE_PREFIX_RIGHT_PITCH_ANCHOR_ARM_ONLY",
        "causal_hypothesis": (
            "Winner-v27 localized negative-X failure to ticks 4-8, Winner-v28 "
            "isolated the right pitch chain, Winner-v29 proved the exact anchor "
            "gradient, Winner-v30 reduced same-batch anchor error in one update, "
            "and Winner-v31 proved its two HOLD checks were only bounded cross-worker "
            "float replay. One unchanged continuation now tests persistence."
        ),
        "source_checkpoint": {
            "completed_updates": 201,
            "optimizer_count": 201,
            "snapshot": v30["snapshot"],
            "graph": v30["graph"],
            "repository_attribution": source_attribution,
        },
        "teacher_checkpoint": {
            "completed_updates": 100,
            "optimizer_count": 100,
            "snapshot": v22["snapshot_manifest"][99],
            "graph": v22["persistent_checkpoints"][1]["graph"],
            "repository_attribution": teacher_attribution,
        },
        "frozen_training": {
            "source_completed_updates": 201,
            "source_optimizer_count": 201,
            "continuation_optimizer_updates": 100,
            "final_optimizer_count": 301,
            "environments_per_update": 80,
            "ticks_per_environment": 250,
            "scheduled_episode_slots": 2_000_000,
            "training_root_seed": 120120,
            "learning_rate": 0.0001,
            "predictor_scale": 380.9135437011719,
            "anchor_scale": 197.3112030029297,
            "rollout_update_indices": [201, 300],
            "persistent_snapshots": "atomic digest-protected readback after every update",
            "persistent_checkpoints": {"half": 251, "final": 301},
            "coefficient_or_length_search": False,
        },
        "objective": {
            "baseline_transition_objective": v24_prereg["objective"],
            "ppo": "unchanged Winner-v24 recurrent PPO objective",
            "predictor": (
                "unchanged Winner-v22 normalized successor predictor at exact scale "
                "380.9135437011719"
            ),
            "prefix_anchor": {
                "teacher": "frozen Winner-v22 final update-100 trainable policy leaves",
                "teacher_state": (
                    "own recurrent shadow state evaluated on each candidate observation "
                    "and realized previous-action history"
                ),
                "candidate_action": "deterministic graph-authoritative bounded mean action",
                "teacher_action": "stop-gradient deterministic graph-authoritative bounded mean action",
                "loss": "raw mean squared action error over the selected elements",
                "selected_training_configuration_ids": [
                    "COM_X_NEG",
                    "COM_CORNER_00",
                    "COM_CORNER_01",
                    "COM_CORNER_02",
                    "COM_CORNER_03",
                    "DISCOVERY_03",
                    "DISCOVERY_09",
                    "DISCOVERY_10",
                ],
                "prefix_ticks": list(range(8)),
                "action_indices": [11, 12, 13],
                "selected_elements_per_update": 384,
                "scale": 197.3112030029297,
                "scale_source": "sole Winner-v29 same-leaf gradient-RMS balance",
                "action_replacement": False,
            },
            "combined_gradient": (
                "Winner-v24 PPO plus Winner-v22 predictor gradient plus exact "
                "197.3112030029297 times the Winner-v29 prefix-anchor gradient"
            ),
        },
        "stop_rules": [
            "stop if the preserved count-201 snapshot, Adam state, or teacher differs",
            "stop if any environment, population, receipt, action boundary, reward, mask, or V24 transition differs",
            "stop unless every update selects exactly 384 valid prefix-anchor elements",
            "stop unless anchor gradients are nonzero on exactly the six recurrent/action leaves and zero on all other leaves",
            "stop if hidden replay exceeds 1e-6 or successor masks disagree",
            "stop if any combined gradient, parameter delta, loss, metric, snapshot, or ONNX contract is invalid",
            "do not run or inspect the formal support gate in this workflow",
            "do not select a checkpoint from training losses or intermediate behavior",
        ],
        "post_training_selection": {
            "authorized_now": False,
            "checkpoint_rule": (
                "both checkpoints remain evidence until one separately frozen support "
                "and context gate classifies both"
            ),
            "pass_authorizes_only": (
                "a separately preregistered prefix right-pitch anchor support gate "
                "over both half and final checkpoints"
            ),
        },
        "execution_now": {
            "optimizer_updates": 0,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "robot_clearance": False,
            "training_authorized": True,
            "formal_support_gate_authorized": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "pass_authorizes_only": (
                "a separate prefix right-pitch anchor support gate preregistration"
            ),
        },
        "sources": sources,
        "source_manifest_sha256": canonical_sha256(sources),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown.write_text(
        "\n".join(
            [
                "# Winner-v32 prefix right-pitch anchor training preregistration",
                "",
                f"- Status: `{value['status']}`",
                f"- Decision: `{value['decision']}`",
                "- Source / half / final optimizer count: `201 / 251 / 301`",
                "- Continuation: `100 updates`, `80 x 250` scheduled slots per update",
                "- Predictor / prefix-anchor scales: `380.9135437011719 / 197.3112030029297`",
                "- Formal support / locomotion / robot in training: `0 / 0 / 0`",
                "",
                value["causal_hypothesis"],
                "",
                "No checkpoint is selected from training metrics. A passing artifact",
                "authorizes only a separately frozen half/final support gate.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(value["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
