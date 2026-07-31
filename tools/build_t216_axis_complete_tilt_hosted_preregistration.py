#!/usr/bin/env python3
"""Preregister T216's one earned axis-complete tilt continuation."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from colab_t32_action_margin_trainthrough_continuation import (
    canonical_sha256,
    source_inventory,
)
from colab_winner_v114_linear_torque_continuation import (
    directory_sha256,
    sha256,
)


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
CPU_RESULT = ANALYSIS / "t215b_axis_complete_tilt_cpu_result.json"
T204 = ANALYSIS / "t204_t203_recovered_training_validation.json"
T214B = (
    ANALYSIS / "t214b_axis_complete_tilt_source_transfer_result.json"
)
DRIVER = ROOT / "tools/colab_t216_axis_complete_tilt_continuation.py"
BASE_T170 = ROOT / "tools/colab_t170_eight_stratum_head_continuation.py"
BASE_T78 = ROOT / "tools/colab_t78_endpoint_joint_adapter_continuation.py"
T32_DRIVER = (
    ROOT / "tools/colab_t32_action_margin_trainthrough_continuation.py"
)
HELPER = ROOT / "tools/colab_winner_v114_linear_torque_continuation.py"
PLAYGROUND = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t215b_axis_complete_tilt_cpu_source_v1"
)
TRAINING = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t203_colab_recovery_20260730/extracted/"
    "t203_predicted_roll_risk_continuation/training"
)
SOURCE = TRAINING / "2026_07_30_125443_1003520"
STEP_ZERO = TRAINING / "2026_07_30_125443_1003520.onnx"
REFERENCE = ANALYSIS / "ground_up_projected_reference_feature_table.npz"
GATE = ANALYSIS / "t98_hidden_gate_asset.json"
OUTPUT = ANALYSIS / "t216_axis_complete_tilt_hosted_preregistration.json"
MARKDOWN = ANALYSIS / "T216_AXIS_COMPLETE_TILT_HOSTED_PREREGISTRATION_20260730.md"


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T216: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T216 preregistration requires clean worktree")
    cpu = json.loads(CPU_RESULT.read_text(encoding="utf-8"))
    t204 = json.loads(T204.read_text(encoding="utf-8"))
    t214b = json.loads(T214B.read_text(encoding="utf-8"))
    t204_half = next(
        item
        for item in t204["exports"]["checkpoints"]
        if int(item["step"]) == 1_003_520
    )
    t204_half_onnx = next(
        item
        for item in t204["exports"]["onnx"]
        if int(item["step"]) == 1_003_520
    )
    inventory = source_inventory(PLAYGROUND)
    input_hashes = {
        "driver": sha256(DRIVER),
        "base_t170_driver": sha256(BASE_T170),
        "base_t78_driver": sha256(BASE_T78),
        "t32_driver": sha256(T32_DRIVER),
        "helper": sha256(HELPER),
        "cpu_result": sha256(CPU_RESULT),
        "t204_validation": sha256(T204),
        "t214b_selection": sha256(T214B),
        "source_checkpoint": directory_sha256(SOURCE),
        "reference_features": sha256(REFERENCE),
        "expected_step_zero_raw": sha256(STEP_ZERO),
        "hidden_gate_static_asset": sha256(GATE),
        "playground_inventory": canonical_sha256(inventory),
    }
    checks = {
        "t215b_cpu_contract_green_and_earned_exactly": (
            cpu["status"] == "PASS_T215B_AXIS_COMPLETE_TILT_CPU_CONTRACT"
            and cpu["failed_checks"] == []
            and all(cpu["checks"].values())
            and cpu["decision"]
            == "EARN_T216_AXIS_COMPLETE_TILT_HOSTED_PREREGISTRATION_ONLY"
            and cpu["execution"]["optimizer_steps"] == 1024
            and cpu["execution"]["formal_behavior_cells"] == 0
        ),
        "t214b_selects_axis_complete_tilt_box": (
            t214b["status"]
            == "PASS_T214B_AXIS_COMPLETE_TILT_SOURCE_TRANSFER"
            and t214b["failed_checks"] == []
            and all(t214b["checks"].values())
            and t214b["decision"]
            == (
                "EARN_T215B_AXIS_COMPLETE_TILT_DUAL_CPU_CONTRACT_"
                "PREREGISTRATION_ONLY"
            )
            and t214b["classification"]
            == "AXIS_COMPLETE_TILT_BOX_UNIFIES_ROLL_AND_PITCH_FALLS"
            and t214b["dominant_failure_axes"] == ["pitch", "roll"]
        ),
        "source_is_exact_green_t203_half": (
            t204["status"]
            == "PASS_T204_T203_RECOVERED_TRAINING_VALIDATION"
            and Path(t204_half["path"]).resolve() == SOURCE.resolve()
            and t204_half["directory_sha256"]
            == directory_sha256(SOURCE)
            and t204_half_onnx["sha256"] == sha256(STEP_ZERO)
        ),
        "pure_v127_lagrangian_engine_frozen": (
            inventory[
                "playground/common/winner_v127_constrained_ppo_train.py"
            ]["sha256"]
            == "b749d956c4651e5a9037b542e946fcc81425915c17495e1b68ee27f4a7435615"
            and inventory[
                "playground/common/winner_v127_constrained_ppo_losses.py"
            ]["sha256"]
            == "996e292f76a4071f2c3117b0f1dacd9b1a3bf9e31d6d97128ce2f054f9bc6ff1"
        ),
        "all_inputs_present": all(
            path.exists()
            for path in (
                DRIVER,
                BASE_T170,
                BASE_T78,
                T32_DRIVER,
                HELPER,
                CPU_RESULT,
                T204,
                T214B,
                PLAYGROUND,
                SOURCE,
                STEP_ZERO,
                REFERENCE,
                GATE,
            )
        ),
        "one_run_no_retry_or_same_run_resume": True,
        "both_checkpoint_persistence_required": True,
        "no_behavior_hosted_or_robot_execution_now": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T216 preregistration checks failed: {failed}")
    basis: dict[str, Any] = {
        "schema_version": (
            "open_duck.t216_axis_complete_tilt_hosted_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T216_AXIS_COMPLETE_TILT_HOSTED_CONTINUATION"
        ),
        "decision": "AUTHORIZE_ONE_HASH_FROZEN_T216_L4_CONTINUATION",
        "repository_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "question": (
            "Does one exact T203-half continuation with a separate dense "
            "axis-complete predicted-tilt cost critic and derived dual price "
            "preserve gait while preventing both observed roll- and "
            "pitch-dominant fall modes?"
        ),
        "causal_basis": {
            "failure": (
                "T210's roll-only dual continuation failed one nominal "
                "final-checkpoint P30 x=0.080 cell through a pitch-dominant "
                "contact-loss collapse"
            ),
            "signal": (
                "T214B found zero box exceedance in all 33 passing traces "
                "and early exceedance in all three cross-family falls, with "
                "both pitch- and roll-dominant failures represented"
            ),
            "axis_completeness": (
                "the selected score is the maximum of independently "
                "normalized 80 ms predicted roll and pitch risks; repeating "
                "single-support curricula is closed by T56, T186, and T194"
            ),
            "training_contract": (
                "T215B proves exact cost/reward separation, pure V127 "
                "Lagrangian wiring, protected restore/update scope, dual "
                "law, both-axis environment readback, and unchanged ONNX ABI"
            ),
            "hosted_run_earned": True,
        },
        "input_hashes": input_hashes,
        "paths": {
            "playground": str(PLAYGROUND.resolve()),
            "source_checkpoint": str(SOURCE.resolve()),
            "expected_step_zero_raw": str(STEP_ZERO.resolve()),
            "reference": str(REFERENCE.resolve()),
            "hidden_gate_static_asset": str(GATE.resolve()),
        },
        "playground": {
            "file_count": len(inventory),
            "file_inventory": inventory,
        },
        "training": {
            "timesteps": 2_007_040,
            "exports": [0, 1_003_520, 2_007_040],
            "num_envs": 256,
            "body_configuration_strata": 8,
            "environments_per_stratum": 32,
            "source": "exact_T203_half",
            "prediction_horizon_s": 0.08,
            "score": (
                "max(abs(roll+0.08*roll_rate)/0.3541802655745987,"
                "abs(pitch+0.08*pitch_rate)/0.2379576557426921)"
            ),
            "passing_envelope_rad": {
                "roll": 0.3541802655745987,
                "pitch": 0.2379576557426921,
            },
            "cost": "square(max(0,score-1))",
            "reward_channel": "unchanged_original_clipped_reward",
            "cost_channel": "separate_unclipped_training_only",
            "cost_critic": "separate",
            "cost_discount": 1.0,
            "actor_advantage": "(A_R-lambda*A_C)/(1+lambda)",
            "dual_initial_lambda": 0.0,
            "dual_eta": "1/(ceil(K/4)*J_C0)",
            "legacy_constraint_reward_penalties": 0.0,
            "actor_trainable_groups": ["negative_adapter_location"],
            "reward_critic_trainable": True,
            "cost_critic_trainable": True,
            "normalizer_frozen": True,
            "mature_actor_frozen": True,
            "command_support_change": False,
            "network_capacity_change": False,
            "policy_abi_change": False,
            "deployment_graph_change": False,
            "retry": False,
            "same_run_resume": False,
            "gpu": "L4",
            "maximum_wall_seconds": 21_600,
        },
        "post_training": {
            "recover_and_hash_policy_cost_aux_and_onnx_exports": True,
            "validate_tree_raw_onnx_cost_and_dual_before_behavior": True,
            "compose_existing_t164_deployment_repairs": True,
            "evaluate_both_new_checkpoints": True,
            "nominal_then_targeted_y_negative_first": True,
            "full_frozen_robustness_only_if_targeted_green": True,
            "both_checkpoint_persistence_required": True,
            "positive_finite_tilt_cost_required_before_behavior": True,
            "positive_finite_dual_eta_and_lambda_required_before_behavior": True,
            "final_lambda_not_below_half_required": True,
            "checkpoint_selection_or_cherry_pick": False,
            "gate5_remains_closed": True,
        },
        "checks": checks,
        "failed_checks": failed,
        "execution_now": {
            "optimizer_steps": 0,
            "formal_behavior_cells": 0,
            "hosted_sessions_opened": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "package_and_launch_contract": True,
            "one_hash_exact_l4_run_after_package_green": True,
            "retry_or_same_run_resume": False,
            "behavior_evaluation_after_valid_artifact": False,
            "checkpoint_selection": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    value = {
        **basis,
        "preregistered_contract_sha256": canonical_sha256(basis),
    }
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T216 axis-complete tilt hosted preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Source: exact T203 half checkpoint\n"
        "- Run: one L4, 2,007,040 steps, no retry/resume\n"
        "- Constraint: separate dense axis-complete predicted-tilt cost "
        "critic and derived dual\n"
        "- Trainable actor: existing negative adapter pair only\n"
        "- Both new checkpoints must pass; no selection\n"
        f"- Contract SHA-256: `{value['preregistered_contract_sha256']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
