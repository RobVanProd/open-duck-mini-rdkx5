#!/usr/bin/env python3
"""Freeze the zero-update Winner-v24 symmetric support-failure CPU contract."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v24_symmetric_failure_cpu_contract.json"
MARKDOWN = ANALYSIS / "WINNER_V24_SYMMETRIC_FAILURE_CPU_CONTRACT_20260721.md"
V23_RESULT = ANALYSIS / "winner_v23_negative_x_response_use_diagnostic_result.json"
V22_TRAINING = ANALYSIS / "winner_v22_normalized_predictor_training_result.json"
SOURCES = {
    "builder": Path("tools/build_winner_v24_symmetric_failure_cpu_contract.py"),
    "runner": Path("tools/run_winner_v24_symmetric_failure_cpu_contract.py"),
    "mechanics": Path("patches/winner_v24_symmetric_support_failure.py"),
    "mechanics_tests": Path("tests/test_winner_v24_symmetric_support_failure.py"),
    "runner_tests": Path("tests/test_winner_v24_symmetric_failure_cpu_contract.py"),
    "preregistration_tests": Path("tests/test_winner_v24_symmetric_failure_cpu_preregistration.py"),
    "importer": Path("tools/import_winner_v24_symmetric_failure_cpu_result.py"),
    "importer_tests": Path("tests/test_winner_v24_symmetric_failure_cpu_import.py"),
    "workflow": Path(".github/workflows/winner-v24-symmetric-failure-cpu-contract.yml"),
    "v23_result": Path("outputs/analysis/winner_v23_negative_x_response_use_diagnostic_result.json"),
    "v23_importer": Path("tools/import_winner_v23_negative_x_response_use_diagnostic.py"),
    "v22_training_result": Path("outputs/analysis/winner_v22_normalized_predictor_training_result.json"),
    "v22_normalized_predictor": Path("patches/winner_v22_normalized_predictor.py"),
    "v22_gradient_composition": Path("patches/winner_v22_normalized_predictor_v2.py"),
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
        raise FileExistsError("refusing to overwrite Winner-v24 CPU contract")
    v23 = json.loads(V23_RESULT.read_text(encoding="utf-8"))
    training = json.loads(V22_TRAINING.read_text(encoding="utf-8"))
    if (
        v23.get("status") != "PASS_WINNER_V23_NEGATIVE_X_RESPONSE_USE_DIAGNOSTIC"
        or v23.get("classification")
        != "RESPONSE_STATE_PRESENT_AND_USED_SUPPORT_CONTROL_INADEQUATE"
        or v23.get("decision")
        != "AUTHORIZE_NEGATIVE_X_SUPPORT_CONTROL_OBJECTIVE_CPU_CONTRACT_ONLY"
        or v23.get("failed_checks") != []
        or training.get("status")
        != "PASS_WINNER_V22_NORMALIZED_PREDICTOR_TRAINING_ARTIFACT"
        or training.get("failed_checks") != []
    ):
        raise ValueError("Winner-v24 source evidence changed")
    final_snapshot = training["snapshot_manifest"][99]
    if final_snapshot.get("completed_updates") != 100:
        raise ValueError("Winner-v24 source checkpoint changed")
    sources = {
        name: {
            "path": str(path).replace("\\", "/"),
            "hash_mode": "lf",
            "sha256": lf_sha256(ROOT / path),
        }
        for name, path in SOURCES.items()
    }
    payload = {
        "schema_version": "winner_v24.symmetric_failure_cpu_contract.v1",
        "status": "FROZEN_WINNER_V24_SYMMETRIC_FAILURE_CPU_CONTRACT",
        "decision": "AUTHORIZE_ONE_ZERO_UPDATE_SYMMETRIC_FAILURE_OBJECTIVE_PROOF_ONLY",
        "causal_hypothesis": (
            "Winner-v22 already encodes and uses the response, but its support objective "
            "gives +250 to settled success and zero at a roll/pitch boundary. A symmetric "
            "-250 observed-terminal penalty should change the context-conditioned policy "
            "gradient without changing rollouts, predictor semantics, or policy inputs."
        ),
        "source_checkpoint": {
            "repository_attribution": training["repository_attribution"],
            "label": "final",
            "snapshot": final_snapshot,
        },
        "objective": {
            "source_rollout_update_index": 100,
            "settled_success_bonus": 250.0,
            "roll_pitch_failure_penalty": -250.0,
            "penalty_basis": "equal magnitude and opposite sign to the existing settled terminal bonus",
            "failure_selector": "terminal.checks.roll_pitch is false",
            "reads_hidden_configuration": False,
            "changes_rollout_or_policy_action": False,
            "modified_batch_keys": ["advantages", "returns", "rewards"],
            "combined_delta_tolerance": 2.0e-6,
            "combined_delta_tolerance_basis": "above the previously measured 1.430511474609375e-6 float32 explicit-composition roundoff",
            "coefficient_search": False,
        },
        "required_checks": [
            "exact final Winner-v22 snapshot and exact 80-episode population",
            "baseline rollout, action boundary, pitch reward, and GAE replay are exact",
            "default-off batch is bit-exact",
            "both roll/pitch failures and settled successes are present",
            "enabled mode changes only rewards, returns, and advantages",
            "exactly -250 is applied only at observed roll/pitch terminals",
            "normalized predictor loss and gradients remain bit-exact",
            "PPO action-head and recurrent gradients both change",
            "combined-gradient delta equals the PPO-gradient delta within 2e-6",
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
            "pass_authorizes_only": "a separate one-update symmetric-failure CPU-proof preregistration",
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
                "# Winner-v24 symmetric support-failure CPU contract",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                "- Existing settled terminal bonus: `+250`",
                "- New observed roll/pitch terminal penalty: `-250`",
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
