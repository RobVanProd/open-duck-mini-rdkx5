#!/usr/bin/env python3
"""Freeze the Winner-v24 baseline-anchored one-update CPU proof."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v24_baseline_anchored_one_update_cpu_contract.json"
MARKDOWN = ANALYSIS / "WINNER_V24_BASELINE_ANCHORED_ONE_UPDATE_CPU_CONTRACT_20260722.md"
ZERO_UPDATE = ANALYSIS / "winner_v24_baseline_anchored_cpu_result_v2.json"
V22_TRAINING = ANALYSIS / "winner_v22_normalized_predictor_training_result.json"
SOURCES = {
    "builder": Path("tools/build_winner_v24_baseline_anchored_one_update_cpu_contract.py"),
    "runner": Path("tools/run_winner_v24_baseline_anchored_one_update_cpu_proof.py"),
    "runner_tests": Path("tests/test_winner_v24_baseline_anchored_one_update_cpu_contract.py"),
    "preregistration_tests": Path("tests/test_winner_v24_baseline_anchored_one_update_cpu_preregistration.py"),
    "importer": Path("tools/import_winner_v24_baseline_anchored_one_update_result.py"),
    "importer_tests": Path("tests/test_winner_v24_baseline_anchored_one_update_cpu_import.py"),
    "workflow": Path(".github/workflows/winner-v24-baseline-anchored-one-update-cpu-proof.yml"),
    "zero_update_result": Path("outputs/analysis/winner_v24_baseline_anchored_cpu_result_v2.json"),
    "zero_update_corrected_importer": Path("tools/import_winner_v24_baseline_anchored_cpu_result_v2.py"),
    "zero_update_importer_correction": Path("outputs/analysis/winner_v24_baseline_importer_correction.json"),
    "zero_update_contract": Path("outputs/analysis/winner_v24_baseline_anchored_cpu_contract.json"),
    "mechanics_v2": Path("patches/winner_v24_symmetric_support_failure_v2.py"),
    "mechanics_v2_tests": Path("tests/test_winner_v24_symmetric_support_failure_v2.py"),
    "prior_mechanics": Path("patches/winner_v24_symmetric_support_failure.py"),
    "v22_training_result": Path("outputs/analysis/winner_v22_normalized_predictor_training_result.json"),
    "v22_training_runner": Path("tools/run_winner_v22_normalized_predictor_training.py"),
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
        raise FileExistsError("refusing to overwrite Winner-v24 one-update contract")
    zero_update = json.loads(ZERO_UPDATE.read_text(encoding="utf-8"))
    training = json.loads(V22_TRAINING.read_text(encoding="utf-8"))
    if (
        zero_update.get("status")
        != "PASS_WINNER_V24_BASELINE_ANCHORED_CPU_CONTRACT"
        or zero_update.get("decision")
        != "AUTHORIZE_SEPARATE_ONE_UPDATE_BASELINE_ANCHORED_CPU_PROOF_PREREGISTRATION_ONLY"
        or zero_update.get("failed_checks") != []
        or zero_update.get("repository_attribution", {}).get("github_run_id")
        != 29880437377
        or zero_update.get("repository_attribution", {}).get("github_run_attempt")
        != 1
        or training.get("status")
        != "PASS_WINNER_V22_NORMALIZED_PREDICTOR_TRAINING_ARTIFACT"
        or training.get("failed_checks") != []
    ):
        raise ValueError("Winner-v24 one-update source evidence changed")
    final_snapshot = training["snapshot_manifest"][99]
    if final_snapshot.get("completed_updates") != 100:
        raise ValueError("Winner-v24 one-update source checkpoint changed")
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
        "source_rollout_update_index": 100,
    }
    payload = {
        "schema_version": "winner_v24.baseline_anchored_one_update_cpu_contract.v1",
        "status": "FROZEN_WINNER_V24_BASELINE_ANCHORED_ONE_UPDATE_CPU_CONTRACT",
        "decision": "AUTHORIZE_EXACT_ONE_BASELINE_ANCHORED_OPTIMIZER_UPDATE_ONLY",
        "causal_hypothesis": (
            "The zero-update contract proves the symmetric terminal delta reaches the "
            "policy and recurrent gradients without disturbing the predictor. One exact "
            "continuation step from optimizer count 100 must now prove that the frozen "
            "objective, optimizer state, snapshot, and deployable ONNX compose correctly."
        ),
        "source_checkpoint": {
            "repository_attribution": training["repository_attribution"],
            "label": "final",
            "snapshot": final_snapshot,
            "completed_updates": 100,
            "optimizer_count": 100,
        },
        "objective": objective,
        "required_checks": [
            "exact imported zero-update pass and exact final Winner-v22 snapshot",
            "exact 80-episode update-100 rollout, masks, action boundary, and reward",
            "default-off bytes exact and objective changes only rewards/returns/advantages",
            "all twelve combined gradients are finite and nonzero",
            "one Adam step changes all twelve trainable leaves and count 100 becomes 101",
            "saved optimizer/parameter/normalizer state reads back exactly",
            "exported stateful ONNX preserves ABI, action chain, and JAX agreement",
            "formal support, locomotion, robot, and hardware access remain zero",
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
        "authority": {
            "robot_clearance": False,
            "training_authorized": False,
            "formal_support_gate_authorized": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "manual_mass_com_inertia_measurements_required": False,
            "pass_authorizes_only": "a separate frozen baseline-anchored training preregistration",
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
                "# Winner-v24 baseline-anchored one-update CPU contract",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                "- Source optimizer count: `100`",
                "- Authorized optimizer count after proof: `101`",
                "- Formal support / locomotion / robot: `0 / 0 / 0`",
                "- Manual mass/COM measurements: `not required`",
                "",
                "A pass authorizes only a separately frozen training preregistration.",
                "It does not itself authorize training, support evaluation, or robot access.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
