#!/usr/bin/env python3
"""Freeze the Winner-v24 baseline-anchored zero-update CPU contract."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v24_baseline_anchored_cpu_contract.json"
MARKDOWN = ANALYSIS / "WINNER_V24_BASELINE_ANCHORED_CPU_CONTRACT_20260722.md"
ATTRIBUTION = ANALYSIS / "winner_v24_gae_one_ulp_attribution.json"
V22_TRAINING = ANALYSIS / "winner_v22_normalized_predictor_training_result.json"
SOURCES = {
    "builder": Path("tools/build_winner_v24_baseline_anchored_cpu_contract.py"),
    "runner": Path("tools/run_winner_v24_baseline_anchored_cpu_contract.py"),
    "mechanics_v2": Path("patches/winner_v24_symmetric_support_failure_v2.py"),
    "mechanics_v2_tests": Path("tests/test_winner_v24_symmetric_support_failure_v2.py"),
    "runner_tests": Path("tests/test_winner_v24_baseline_anchored_cpu_contract.py"),
    "preregistration_tests": Path("tests/test_winner_v24_baseline_anchored_cpu_preregistration.py"),
    "importer": Path("tools/import_winner_v24_baseline_anchored_cpu_result.py"),
    "importer_tests": Path("tests/test_winner_v24_baseline_anchored_cpu_import.py"),
    "workflow": Path(".github/workflows/winner-v24-baseline-anchored-cpu-contract.yml"),
    "one_ulp_attribution": Path("outputs/analysis/winner_v24_gae_one_ulp_attribution.json"),
    "one_ulp_attribution_builder": Path("tools/build_winner_v24_gae_one_ulp_attribution.py"),
    "one_ulp_attribution_tests": Path("tests/test_winner_v24_gae_one_ulp_attribution.py"),
    "prior_cpu_result": Path("outputs/analysis/winner_v24_symmetric_failure_cpu_result.json"),
    "prior_cpu_importer": Path("tools/import_winner_v24_symmetric_failure_cpu_result.py"),
    "prior_cpu_runner": Path("tools/run_winner_v24_symmetric_failure_cpu_contract.py"),
    "prior_mechanics": Path("patches/winner_v24_symmetric_support_failure.py"),
    "v23_result": Path("outputs/analysis/winner_v23_negative_x_response_use_diagnostic_result.json"),
    "v22_training_result": Path("outputs/analysis/winner_v22_normalized_predictor_training_result.json"),
    "v22_normalized_predictor": Path("patches/winner_v22_normalized_predictor.py"),
    "v22_gradient_composition": Path("patches/winner_v22_normalized_predictor_v2.py"),
    "v21_predictor_preserving": Path("patches/winner_v21_predictor_preserving_joint_support.py"),
    "v20_recurrent_support": Path("patches/winner_v20_joint_recurrent_support.py"),
    "v15_pitch_margin": Path("patches/winner_v15_pitch_margin_support.py"),
    "base_training": Path("patches/winner_v12_calibrator_training.py"),
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
        raise FileExistsError("refusing to overwrite Winner-v24 baseline contract")
    attribution = json.loads(ATTRIBUTION.read_text(encoding="utf-8"))
    training = json.loads(V22_TRAINING.read_text(encoding="utf-8"))
    if (
        attribution.get("status") != "PASS_WINNER_V24_GAE_ONE_ULP_ATTRIBUTION"
        or attribution.get("decision")
        != "AUTHORIZE_BASELINE_ANCHORED_SYMMETRIC_FAILURE_CPU_CONTRACT_ONLY"
        or attribution.get("failed_checks") != []
        or attribution.get("prospective_correction", {}).get("threshold_relaxed")
        is not False
        or attribution.get("prospective_correction", {}).get("old_result_rewritten")
        is not False
        or training.get("status")
        != "PASS_WINNER_V22_NORMALIZED_PREDICTOR_TRAINING_ARTIFACT"
        or training.get("failed_checks") != []
    ):
        raise ValueError("Winner-v24 baseline source evidence changed")
    final_snapshot = training["snapshot_manifest"][99]
    if final_snapshot.get("completed_updates") != 100:
        raise ValueError("Winner-v24 baseline source checkpoint changed")
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
        "combined_delta_tolerance": 2.0e-6,
        "failure_selector": "terminal.checks.roll_pitch is false",
        "modified_batch_keys": ["advantages", "returns", "rewards"],
        "reads_hidden_configuration": False,
        "roll_pitch_failure_penalty": -250.0,
        "settled_success_bonus": 250.0,
        "source_rollout_update_index": 100,
    }
    payload = {
        "schema_version": "winner_v24.baseline_anchored_cpu_contract.v1",
        "status": "FROZEN_WINNER_V24_BASELINE_ANCHORED_CPU_CONTRACT",
        "decision": "AUTHORIZE_ONE_ZERO_UPDATE_BASELINE_ANCHORED_OBJECTIVE_PROOF_ONLY",
        "causal_hypothesis": (
            "Winner-v22 already encodes and uses the early response, but roll/pitch "
            "failure has zero terminal reward while settled success receives +250. "
            "Applying the equal-and-opposite failure delta to the recorded baseline "
            "should alter support-control PPO gradients without touching the predictor, "
            "rollout, action, observation, or physics contract."
        ),
        "attribution_boundary": {
            "old_result_rewritten": False,
            "old_threshold_relaxed": False,
            "baseline_gae_replayed": False,
            "reason": (
                "the sole prior miss was exactly one float32 ULP at 250 while its "
                "advantage replay and every causal/locality check passed"
            ),
        },
        "source_checkpoint": {
            "repository_attribution": training["repository_attribution"],
            "label": "final",
            "snapshot": final_snapshot,
        },
        "objective": objective,
        "required_checks": [
            "exact final Winner-v22 snapshot and exact 80-episode population",
            "exact one-ULP attribution authority, rollout, action boundary, and pitch reward",
            "recorded baseline arrays are authoritative and default-off is bit-exact",
            "both roll/pitch failures and settled successes are present",
            "enabled mode changes only rewards, returns, and advantages",
            "exactly -250 is applied only at observed roll/pitch terminals",
            "the analytic terminal delta and advantage renormalization are exact",
            "normalized predictor loss and gradients remain bit-exact",
            "PPO action-head and recurrent gradients both change",
            "combined-gradient delta equals PPO-gradient delta within 2e-6",
            "all values finite and parameters unchanged with zero optimizer updates",
        ],
        "execution_now": {
            "rollout_episode_slots": 0,
            "optimizer_updates": 0,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "future_execution": {
            "rollout_episode_slots": 80,
            "optimizer_updates": 0,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "robot_clearance": False,
            "training_authorized": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "manual_mass_com_inertia_measurements_required": False,
            "pass_authorizes_only": (
                "a separate one-update baseline-anchored CPU-proof preregistration"
            ),
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
                "# Winner-v24 baseline-anchored CPU contract",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                "- Baseline anchor: `recorded returns + rederived values`",
                "- New observed roll/pitch terminal delta: `-250`",
                "- Baseline GAE reconstruction / old threshold relaxation: `no / no`",
                "- Policy inputs / rollout actions / physics changes: `0 / 0 / 0`",
                "- Optimizer / formal support / locomotion / robot: `0 / 0 / 0 / 0`",
                "- Manual mass/COM measurements: `not required`",
                "",
                "A pass authorizes only a separately preregistered one-update CPU proof.",
                "It does not authorize training, checkpoint selection, or robot access.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
