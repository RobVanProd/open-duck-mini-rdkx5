#!/usr/bin/env python3
"""Preregister one Winner-v24 baseline-anchored 100-update CPU arm."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v24_baseline_anchored_training_preregistration.json"
MARKDOWN = ANALYSIS / "WINNER_V24_BASELINE_ANCHORED_TRAINING_PREREGISTRATION_20260722.md"
ONE_UPDATE = ANALYSIS / "winner_v24_baseline_anchored_one_update_cpu_result_v2.json"
V22_TRAINING = ANALYSIS / "winner_v22_normalized_predictor_training_result.json"
SOURCES = {
    "builder": Path("tools/build_winner_v24_baseline_anchored_training_preregistration.py"),
    "runner": Path("tools/run_winner_v24_baseline_anchored_training.py"),
    "workflow": Path(".github/workflows/winner-v24-baseline-anchored-training.yml"),
    "runner_tests": Path("tests/test_winner_v24_baseline_anchored_training.py"),
    "preregistration_tests": Path("tests/test_winner_v24_baseline_anchored_training_preregistration.py"),
    "importer": Path("tools/import_winner_v24_baseline_anchored_training.py"),
    "importer_tests": Path("tests/test_winner_v24_baseline_anchored_training_import.py"),
    "one_update_result": Path("outputs/analysis/winner_v24_baseline_anchored_one_update_cpu_result_v2.json"),
    "one_update_corrected_importer": Path("tools/import_winner_v24_baseline_anchored_one_update_result_v2.py"),
    "one_update_path_correction": Path("outputs/analysis/winner_v24_one_update_importer_path_correction.json"),
    "one_update_contract": Path("outputs/analysis/winner_v24_baseline_anchored_one_update_cpu_contract.json"),
    "zero_update_result": Path("outputs/analysis/winner_v24_baseline_anchored_cpu_result_v2.json"),
    "mechanics_v2": Path("patches/winner_v24_symmetric_support_failure_v2.py"),
    "mechanics_v2_tests": Path("tests/test_winner_v24_symmetric_support_failure_v2.py"),
    "mechanics_v3": Path("patches/winner_v24_symmetric_support_failure_v3.py"),
    "mechanics_v3_tests": Path("tests/test_winner_v24_symmetric_support_failure_v3.py"),
    "prior_mechanics": Path("patches/winner_v24_symmetric_support_failure.py"),
    "v22_training_result": Path("outputs/analysis/winner_v22_normalized_predictor_training_result.json"),
    "v22_training_importer": Path("tools/import_winner_v22_normalized_predictor_training.py"),
    "v22_normalized_predictor": Path("patches/winner_v22_normalized_predictor.py"),
    "v22_gradient_composition": Path("patches/winner_v22_normalized_predictor_v2.py"),
    "v21_predictor_preserving": Path("patches/winner_v21_predictor_preserving_joint_support.py"),
    "v21_snapshot": Path("patches/winner_v21_predictor_preserving_joint_support_v2.py"),
    "v20_recurrent_support": Path("patches/winner_v20_joint_recurrent_support.py"),
    "v15_pitch_margin": Path("patches/winner_v15_pitch_margin_support.py"),
    "base_training": Path("patches/winner_v12_calibrator_training.py"),
    "network_export": Path("patches/winner_v12_decomposed_backend_networks.py"),
    "environment_builder": Path("tools/prepare_winner_v15_cpu_environment.py"),
    "full_training_preregistration": Path("outputs/analysis/winner_v12_full_calibrator_training_preregistration.json"),
    "domain": Path("outputs/analysis/winner_v3_variable_configuration_replacement_preregistration.json"),
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
        raise FileExistsError("refusing to overwrite Winner-v24 training preregistration")
    proof = json.loads(ONE_UPDATE.read_text(encoding="utf-8"))
    training = json.loads(V22_TRAINING.read_text(encoding="utf-8"))
    if (
        proof.get("status")
        != "PASS_WINNER_V24_BASELINE_ANCHORED_ONE_UPDATE_CPU_PROOF"
        or proof.get("decision")
        != "AUTHORIZE_SEPARATE_BASELINE_ANCHORED_TRAINING_PREREGISTRATION_ONLY"
        or proof.get("failed_checks") != []
        or proof.get("optimization", {}).get("optimizer_count_before") != 100
        or proof.get("optimization", {}).get("optimizer_count_after") != 101
        or proof.get("repository_attribution", {}).get("github_run_id") != 29881265608
        or proof.get("repository_attribution", {}).get("github_run_attempt") != 1
        or training.get("status")
        != "PASS_WINNER_V22_NORMALIZED_PREDICTOR_TRAINING_ARTIFACT"
        or training.get("failed_checks") != []
    ):
        raise ValueError("Winner-v24 training source evidence changed")
    final_snapshot = training["snapshot_manifest"][99]
    if final_snapshot.get("completed_updates") != 100:
        raise ValueError("Winner-v24 training source checkpoint changed")
    sources = {
        name: {
            "path": str(path).replace("\\", "/"),
            "hash_mode": "lf",
            "sha256": lf_sha256(ROOT / path),
        }
        for name, path in SOURCES.items()
    }
    objective = {
        "anchor": "recorded baseline returns and rederived values",
        "advantage_operation": (
            "add only the analytically propagated -250 terminal reward delta, "
            "then renormalize sampled advantages"
        ),
        "baseline_gae_reconstruction": False,
        "failure_selector": "terminal.checks.roll_pitch is false",
        "modified_batch_keys": ["advantages", "returns", "rewards"],
        "reads_hidden_configuration": False,
        "roll_pitch_failure_penalty": -250.0,
        "settled_success_bonus": 250.0,
        "zero_failure_behavior": "bit-exact batch no-op",
    }
    payload = {
        "schema_version": "winner_v24.baseline_anchored_training_preregistration.v1",
        "status": "PREREGISTERED_WINNER_V24_BASELINE_ANCHORED_TRAINING",
        "decision": "AUTHORIZE_ONE_100_UPDATE_BASELINE_ANCHORED_ARM_ONLY",
        "causal_hypothesis": (
            "Winner-v23 proved response state is present and used, while Winner-v24 "
            "proved the equal-and-opposite observed roll/pitch terminal delta reaches "
            "the policy/recurrent gradient and composes through a real continuation "
            "step. One fixed continuation now tests whether that support-control "
            "objective resolves the negative-X boundary failures."
        ),
        "single_change": {
            "reference": "Winner-v22 final normalized-predictor checkpoint",
            "change": "observed roll/pitch terminal reward 0 to -250",
            "settled_success_bonus_unchanged": 250.0,
            "predictor_loss_and_scale_unchanged": True,
            "observation_action_onnx_physics_population_seed_horizon_unchanged": True,
            "coefficient_or_length_search": False,
            "flat_transport_equation_used": False,
        },
        "source_checkpoint": {
            "repository_attribution": training["repository_attribution"],
            "label": "final",
            "snapshot": final_snapshot,
            "completed_updates": 100,
            "optimizer_count": 100,
        },
        "objective": objective,
        "frozen_training": {
            "source_completed_updates": 100,
            "source_optimizer_count": 100,
            "continuation_optimizer_updates": 100,
            "final_optimizer_count": 200,
            "rollout_update_indices": [100, 199],
            "environments_per_update": 80,
            "ticks_per_environment": 250,
            "scheduled_episode_slots": 2_000_000,
            "training_root_seed": 120120,
            "learning_rate": 0.0001,
            "predictor_scale": 380.9135437011719,
            "predictor_scale_evaluations": 0,
            "persistent_snapshots": "atomic digest-protected readback after every update",
            "persistent_checkpoints": {"half": 150, "final": 200},
        },
        "stop_rules": [
            "stop if source snapshot or optimizer count differs",
            "stop if any action boundary, reward, mask, population, or episode receipt differs",
            "if failures are present require exact analytic delta; if absent require a bit-exact zero-failure no-op",
            "stop if hidden replay exceeds 1e-6 or successor masks disagree",
            "stop if any of twelve gradients or parameter deltas is zero/nonfinite",
            "stop if any snapshot or ONNX contract fails",
            "do not run or inspect the formal support gate in this workflow",
            "do not select a checkpoint from training metrics",
        ],
        "post_training_selection": {
            "authorized_now": False,
            "pass_authorizes_only": (
                "a separately preregistered baseline-anchored support gate over both half and final checkpoints"
            ),
            "checkpoint_rule": (
                "both checkpoints remain evidence until the unchanged support/context gate classifies them"
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
            "formal_support_gate_authorized": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "manual_mass_com_inertia_measurements_required": False,
            "pass_authorizes_only": "a separate baseline-anchored support gate preregistration",
        },
        "sources": sources,
        "source_manifest_sha256": canonical_sha256(sources),
    }
    args.output.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown.write_text(
        "\n".join(
            [
                "# Winner-v24 baseline-anchored training preregistration",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                "- Source / final optimizer count: `100 / 200`",
                "- Continuation updates / checkpoints: `100 / 150,200`",
                "- New terminal failure reward: `-250`",
                "- Coefficient / length / predictor-scale searches: `0 / 0 / 0`",
                "- Formal support / locomotion / robot: `0 / 0 / 0`",
                "- Flat-transport equation: `not used`",
                "- Manual mass/COM measurements: `not required`",
                "",
                "This workflow trains one fixed offline arm and exports half/final evidence.",
                "It does not evaluate support, select a checkpoint, or access the robot.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
