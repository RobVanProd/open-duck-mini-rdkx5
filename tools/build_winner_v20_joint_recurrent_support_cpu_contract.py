#!/usr/bin/env python3
"""Freeze one Winner-v20 joint recurrent PPO proof update."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v20_joint_recurrent_support_cpu_contract.json"
MARKDOWN = ANALYSIS / "WINNER_V20_JOINT_RECURRENT_SUPPORT_CPU_CONTRACT_20260721.md"
ATTRIBUTION = ANALYSIS / "winner_v20_joint_recurrent_support_attribution.json"
STAGE1_RESULT = ANALYSIS / "winner_v13_normalized_response_stage1_v2_result.json"
SOURCES = {
    "builder": Path("tools/build_winner_v20_joint_recurrent_support_cpu_contract.py"),
    "runner": Path("tools/run_winner_v20_joint_recurrent_support_cpu_contract.py"),
    "environment_builder": Path("tools/prepare_winner_v15_cpu_environment.py"),
    "mechanics": Path("patches/winner_v20_joint_recurrent_support.py"),
    "mechanics_tests": Path("tests/test_winner_v20_joint_recurrent_support.py"),
    "contract_tests": Path(
        "tests/test_winner_v20_joint_recurrent_support_cpu_contract.py"
    ),
    "workflow": Path(
        ".github/workflows/winner-v20-joint-recurrent-support-cpu-contract.yml"
    ),
    "attribution": Path(
        "outputs/analysis/winner_v20_joint_recurrent_support_attribution.json"
    ),
    "attribution_builder": Path(
        "tools/build_winner_v20_joint_recurrent_support_attribution.py"
    ),
    "attribution_tests": Path(
        "tests/test_winner_v20_joint_recurrent_support_attribution.py"
    ),
    "winner_v15_objective": Path("patches/winner_v15_pitch_margin_support.py"),
    "winner_v15_training_result": Path(
        "outputs/analysis/winner_v15_pitch_margin_support_training_result.json"
    ),
    "winner_v15_hold": Path(
        "outputs/analysis/winner_v15_pitch_margin_support_hold_attribution.json"
    ),
    "winner_v19_hold": Path(
        "outputs/analysis/winner_v19_imu_ankle_feedback_magnitude_hold_attribution.json"
    ),
    "stage1_result": Path(
        "outputs/analysis/winner_v13_normalized_response_stage1_v2_result.json"
    ),
    "v12_training_primitives": Path("patches/winner_v12_calibrator_training.py"),
    "deployable_network": Path("patches/winner_v12_decomposed_backend_networks.py"),
    "cpu_smoke": Path("tools/run_winner_v12_calibrator_cpu_smoke.py"),
    "full_training_runner": Path("tools/run_winner_v12_full_calibrator_training.py"),
    "full_training_preregistration": Path(
        "outputs/analysis/winner_v12_full_calibrator_training_preregistration.json"
    ),
    "calibrator_design": Path(
        "outputs/analysis/winner_v12_calibrator_training_preregistration.json"
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
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite CPU contract: {path}")
    attribution = json.loads(ATTRIBUTION.read_text(encoding="utf-8"))
    stage1 = json.loads(STAGE1_RESULT.read_text(encoding="utf-8"))
    final_snapshot = stage1.get("snapshot_manifest", [{}])[-1]
    if (
        attribution.get("status")
        != "PASS_WINNER_V20_JOINT_RECURRENT_SUPPORT_ATTRIBUTION"
        or attribution.get("decision")
        != "PREREGISTER_ONE_JOINT_RECURRENT_PPO_CPU_CONTRACT"
        or attribution.get("execution", {}).get("optimizer_updates") != 0
        or attribution.get("authority", {}).get("joint_recurrent_training_authorized")
        is not False
        or stage1.get("status") != "PASS_WINNER_V13_NORMALIZED_RESPONSE_STAGE1"
        or stage1.get("failed_checks") != []
        or final_snapshot.get("sha256")
        != "8c1392c738eddfb098e61c1a6ae2f863eda883e1eba6ac546aef695da6f163af"
        or final_snapshot.get("bytes") != 189027
    ):
        raise ValueError("Winner-v20 CPU source evidence changed")
    sources = {
        name: {
            "path": str(path).replace("\\", "/"),
            "hash_mode": "lf",
            "sha256": lf_sha256(ROOT / path),
        }
        for name, path in SOURCES.items()
    }
    payload = {
        "schema_version": "winner_v20.joint_recurrent_support_cpu_contract.v1",
        "status": "FROZEN_WINNER_V20_JOINT_RECURRENT_SUPPORT_CPU_CONTRACT",
        "decision": "AUTHORIZE_ONE_JOINT_RECURRENT_PPO_PROOF_UPDATE_ONLY",
        "source_artifact": {
            "github_run_id": 29822834921,
            "github_run_attempt": 1,
            "github_run_head_sha": "0b1dac9ea47a93861f72fa5dd393134f36d6db02",
            "github_artifact_id": 8492593761,
            "github_artifact_name": "winner-v13-normalized-response-stage1-v2-29822834921",
            "artifact_zip_sha256": (
                "b3ff19186ef39e8a72f9e43095d373840fb0b1562a2f7bed83a74c9f10cf6680"
            ),
            "snapshot_member": (
                "winner-v13-normalized-response-stage1-v2-work/snapshots/"
                "snapshot_stage1_update_100.npz"
            ),
            "snapshot_sha256": final_snapshot["sha256"],
            "snapshot_bytes": final_snapshot["bytes"],
        },
        "single_change": {
            "reference": "Winner-v15 action-head-only PPO proof from the same snapshot",
            "enabled": (
                "recompute hidden[80,250,64] from observations[80,250,115] and "
                "previous_actions[80,250,14] inside the PPO gradient"
            ),
            "newly_trainable_existing_leaves": [
                "obs_weight",
                "previous_action_weight",
                "hidden_weight",
                "hidden_bias",
            ],
            "still_trainable_winner_v15_leaves": [
                "action_weight",
                "action_bias",
                "training_only_log_std",
                "training_only_value_weight",
                "training_only_value_bias",
            ],
            "bit_exact_frozen_auxiliary_leaves": [
                "auxiliary_hidden_weight",
                "auxiliary_action_weight",
                "auxiliary_bias",
            ],
            "new_parameters": 0,
            "onnx_abi_change": False,
            "reward_change_from_winner_v15": False,
            "population_seed_horizon_action_bound_change": False,
            "post_policy_wrapper": False,
        },
        "frozen_cpu_proof": {
            "optimizer_updates": 1,
            "population": "exact 40 training configurations x 2 hidden plants",
            "ticks": 250,
            "rollout_update_index": 0,
            "training_root_seed": 120120,
            "learning_rate": 0.0001,
            "source_hidden_replay_tolerance": 1.0e-6,
            "requirements": [
                "Winner-v20 rollout equals Winner-v15 reward/action/mask/episode data bit-exactly",
                "complete observation capture reconstructs the reviewed ONNX chain",
                "full-BPTT source hidden replay error is at most 1e-6",
                "all nine selected gradients are finite and nonzero",
                "all nine selected leaves change after one Adam update",
                "three auxiliary predictor leaves remain bit-exact",
                "snapshot and optimizer read back exactly",
                "115/14/64 ONNX ABI, graph bounds, and previous-action chain remain exact",
            ],
        },
        "pass_rule": (
            "Every proof check passes. A pass authorizes only a separate preregistration "
            "for one 100-update causal A/B arm; it does not authorize that training now."
        ),
        "execution_now": {
            "optimizer_updates": 0,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "robot_clearance": False,
            "joint_recurrent_training_authorized": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "pass_authorizes_only": (
                "a separate joint-recurrent 100-update training preregistration"
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
                "# Winner-v20 joint recurrent support CPU contract",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                "- Source: identical Winner-v13 Stage-1 update-100 snapshot",
                "- Proof updates / support cells / robot: `1 / 0 / 0`",
                "",
                "This freezes a one-variable mechanics proof. The existing recurrent",
                "core is differentiated through the complete 250-tick observation and",
                "previous-action sequence. There are no new parameters, reward changes,",
                "wrappers, or ABI changes. A pass authorizes only a separate training",
                "preregistration.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
