#!/usr/bin/env python3
"""Freeze the zero-update Winner-v21 predictor-preserving CPU contract."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v21_predictor_preserving_joint_cpu_contract.json"
MARKDOWN = ANALYSIS / "WINNER_V21_PREDICTOR_PRESERVING_JOINT_CPU_CONTRACT_20260721.md"
ATTRIBUTION = ANALYSIS / "winner_v20_joint_recurrent_support_failure_attribution.json"
STAGE1_RESULT = ANALYSIS / "winner_v13_normalized_response_stage1_v2_result.json"
SOURCES = {
    "builder": Path("tools/build_winner_v21_predictor_preserving_joint_cpu_contract.py"),
    "runner": Path("tools/run_winner_v21_predictor_preserving_joint_cpu_contract.py"),
    "mechanics": Path("patches/winner_v21_predictor_preserving_joint_support.py"),
    "mechanics_tests": Path("tests/test_winner_v21_predictor_preserving_joint_support.py"),
    "contract_tests": Path("tests/test_winner_v21_predictor_preserving_joint_cpu_contract.py"),
    "workflow": Path(".github/workflows/winner-v21-predictor-preserving-joint-cpu-contract.yml"),
    "result_importer": Path("tools/import_winner_v21_predictor_preserving_joint_cpu_result.py"),
    "result_importer_tests": Path("tests/test_winner_v21_predictor_preserving_joint_cpu_import.py"),
    "failure_attribution": Path(
        "outputs/analysis/winner_v20_joint_recurrent_support_failure_attribution.json"
    ),
    "failure_attribution_builder": Path(
        "tools/build_winner_v20_joint_recurrent_support_failure_attribution.py"
    ),
    "stage1_result": Path("outputs/analysis/winner_v13_normalized_response_stage1_v2_result.json"),
    "winner_v20_mechanics": Path("patches/winner_v20_joint_recurrent_support.py"),
    "winner_v15_objective": Path("patches/winner_v15_pitch_margin_support.py"),
    "training_primitives": Path("patches/winner_v12_calibrator_training.py"),
    "environment_builder": Path("tools/prepare_winner_v15_cpu_environment.py"),
    "cpu_smoke": Path("tools/run_winner_v12_calibrator_cpu_smoke.py"),
    "full_training_runner": Path("tools/run_winner_v12_full_calibrator_training.py"),
    "full_training_preregistration": Path(
        "outputs/analysis/winner_v12_full_calibrator_training_preregistration.json"
    ),
    "variable_configuration_domain": Path(
        "outputs/analysis/winner_v3_variable_configuration_replacement_preregistration.json"
    ),
    "runtime_observer": Path(
        "artifacts/runtime_handoff/rdkx5_native_20260719/observer/winner_v2_contract.py"
    ),
    "canonical_p30_fit": Path(
        "outputs/analysis/fixed_target_p30_actuator_fit_20260712.json"
    ),
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
        raise FileExistsError("refusing to overwrite Winner-v21 CPU contract")
    attribution = json.loads(ATTRIBUTION.read_text(encoding="utf-8"))
    stage1 = json.loads(STAGE1_RESULT.read_text(encoding="utf-8"))
    final_snapshot = stage1["snapshot_manifest"][-1]
    if (
        attribution.get("status") != "PASS_WINNER_V20_SUPPORT_FAILURE_ATTRIBUTION"
        or attribution.get("decision")
        != "AUTHORIZE_PREDICTOR_PRESERVING_JOINT_OBJECTIVE_CPU_CONTRACT_ONLY"
        or attribution.get("authority", {}).get("optimizer_updates_authorized_now")
        != 0
        or attribution.get("findings", {}).get("flat_transport_equation_selected")
        is not False
        or stage1.get("status") != "PASS_WINNER_V13_NORMALIZED_RESPONSE_STAGE1"
        or stage1.get("failed_checks") != []
        or final_snapshot.get("sha256")
        != "8c1392c738eddfb098e61c1a6ae2f863eda883e1eba6ac546aef695da6f163af"
        or final_snapshot.get("bytes") != 189027
    ):
        raise ValueError("Winner-v21 CPU-contract source evidence changed")
    sources = {
        name: {
            "path": str(path).replace("\\", "/"),
            "hash_mode": "lf",
            "sha256": lf_sha256(ROOT / path),
        }
        for name, path in SOURCES.items()
    }
    payload = {
        "schema_version": "winner_v21.predictor_preserving_joint_cpu_contract.v1",
        "status": "FROZEN_WINNER_V21_PREDICTOR_PRESERVING_JOINT_CPU_CONTRACT",
        "decision": "AUTHORIZE_EXACT_ZERO_UPDATE_GRADIENT_BALANCE_PROOF_ONLY",
        "source_artifact": {
            "github_run_id": 29822834921,
            "github_run_attempt": 1,
            "github_run_head_sha": "0b1dac9ea47a93861f72fa5dd393134f36d6db02",
            "github_artifact_id": 8492593761,
            "github_artifact_name": "winner-v13-normalized-response-stage1-v2-29822834921",
            "artifact_zip_sha256": "b3ff19186ef39e8a72f9e43095d373840fb0b1562a2f7bed83a74c9f10cf6680",
            "snapshot_member": (
                "winner-v13-normalized-response-stage1-v2-work/snapshots/"
                "snapshot_stage1_update_100.npz"
            ),
            "snapshot_sha256": final_snapshot["sha256"],
            "snapshot_bytes": final_snapshot["bytes"],
        },
        "single_change": {
            "reference": "Winner-v20 joint recurrent support from the identical Stage-1 source",
            "newly_trainable_existing_leaves": [
                "auxiliary_hidden_weight",
                "auxiliary_action_weight",
                "auxiliary_bias",
            ],
            "unchanged_winner_v20_trainable_leaves": [
                "obs_weight",
                "previous_action_weight",
                "hidden_weight",
                "hidden_bias",
                "action_weight",
                "action_bias",
                "training_only_log_std",
                "training_only_value_weight",
                "training_only_value_bias",
            ],
            "new_parameters": 0,
            "onnx_abi_change": False,
            "rollout_reward_population_seed_horizon_action_bound_change": False,
            "flat_transport_equation_used": False,
        },
        "objective": {
            "ppo": "exact Winner-v20 one-sided negative-pitch-margin PPO loss",
            "predictor": (
                "existing normalized next-response squared error on valid transitions "
                "with an in-batch stored successor; complete-episode tick 249 is excluded"
            ),
            "balance_reference": {
                "ppo": "global RMS over action_weight and action_bias gradients",
                "predictor": (
                    "global RMS over auxiliary_hidden_weight, auxiliary_action_weight, "
                    "and auxiliary_bias gradients"
                ),
            },
            "predictor_scale_formula": "ppo_action_head_gradient_rms / predictor_head_gradient_rms",
            "scale_evaluations": 1,
            "scale_sweep": False,
            "behavior_selection": False,
        },
        "frozen_cpu_proof": {
            "optimizer_updates": 0,
            "population": "exact 40 training configurations x 2 hidden plants",
            "ticks": 250,
            "rollout_update_index": 0,
            "training_root_seed": 120120,
            "requirements": [
                "Winner-v21 rollout equals Winner-v15 reward/action/mask/episode data bit-exactly",
                "sampled-tick recurrent replay error is at most 1e-6",
                "stored-successor target mask is exact and nonempty",
                "PPO gradients open only the five Winner-v20 PPO-only leaves at source",
                "predictor gradients open all four recurrent and all three auxiliary leaves and no PPO-only leaves",
                "the single balance scale is finite and strictly positive",
                "the combined gradient equals PPO plus scaled predictor within 1e-6",
                "all twelve combined gradients are finite and nonzero",
                "all source parameters remain bit-exact and optimizer updates remain zero",
            ],
        },
        "pass_rule": (
            "Every proof check passes. A pass freezes the one measured scale and "
            "authorizes only a separately preregistered two-update CPU proof."
        ),
        "execution_now": {
            "optimizer_updates": 0,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "robot_clearance": False,
            "winner_v21_training_authorized": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "manual_mass_com_inertia_measurements_required": False,
            "pass_authorizes_only": (
                "a separate two-update predictor-preserving CPU proof preregistration"
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
                "# Winner-v21 predictor-preserving joint CPU contract",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                "- Source: identical Winner-v13 Stage-1 update-100 snapshot",
                "- Optimizer updates / support cells / robot access: `0 / 0 / 0`",
                "- Candidate scale evaluations: `1`; sweeps: `0`",
                "- Flat-transport equation: `not used`",
                "",
                "The proof measures PPO and next-response gradients separately, freezes",
                "one head-gradient RMS ratio, and requires all twelve combined gradients",
                "to open without changing a parameter. A pass authorizes only a separate",
                "two-update CPU proof, not support training or locomotion.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
