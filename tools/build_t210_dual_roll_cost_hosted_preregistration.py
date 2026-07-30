#!/usr/bin/env python3
"""Preregister T210's one earned dual roll-cost continuation."""

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
CPU_RESULT = ANALYSIS / "t209_dual_roll_cost_cpu_result.json"
T204 = ANALYSIS / "t204_t203_recovered_training_validation.json"
T208 = ANALYSIS / "t208_t203_persistence_autopsy_result.json"
DRIVER = ROOT / "tools/colab_t210_dual_roll_cost_continuation.py"
BASE_T170 = ROOT / "tools/colab_t170_eight_stratum_head_continuation.py"
BASE_T78 = ROOT / "tools/colab_t78_endpoint_joint_adapter_continuation.py"
T32_DRIVER = (
    ROOT / "tools/colab_t32_action_margin_trainthrough_continuation.py"
)
HELPER = ROOT / "tools/colab_winner_v114_linear_torque_continuation.py"
PLAYGROUND = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t209_dual_roll_cost_cpu_source_v3"
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
OUTPUT = ANALYSIS / "t210_dual_roll_cost_hosted_preregistration.json"
MARKDOWN = ANALYSIS / "T210_DUAL_ROLL_COST_HOSTED_PREREGISTRATION_20260730.md"


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T210: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T210 preregistration requires clean worktree")
    cpu = json.loads(CPU_RESULT.read_text(encoding="utf-8"))
    t204 = json.loads(T204.read_text(encoding="utf-8"))
    t208 = json.loads(T208.read_text(encoding="utf-8"))
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
        "t208_selection": sha256(T208),
        "source_checkpoint": directory_sha256(SOURCE),
        "reference_features": sha256(REFERENCE),
        "expected_step_zero_raw": sha256(STEP_ZERO),
        "hidden_gate_static_asset": sha256(GATE),
        "playground_inventory": canonical_sha256(inventory),
    }
    checks = {
        "t209_cpu_contract_green_and_earned_exactly": (
            cpu["status"] == "PASS_T209_DUAL_ROLL_COST_CPU_CONTRACT"
            and cpu["failed_checks"] == []
            and all(cpu["checks"].values())
            and cpu["decision"]
            == "EARN_T210_DUAL_ROLL_COST_HOSTED_PREREGISTRATION_ONLY"
            and cpu["execution"]["optimizer_steps"] == 1024
            and cpu["execution"]["formal_behavior_cells"] == 0
        ),
        "t208_selects_dense_dual_roll_cost": (
            t208["status"] == "PASS_T208_T203_PERSISTENCE_AUTOPSY"
            and t208["failed_checks"] == []
            and t208["classification"]
            == "ROLL_SIGNAL_RETAINED_FIXED_PRICE_LOST_PERSISTENCE"
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
            ]
            == "b749d956c4651e5a9037b542e946fcc81425915c17495e1b68ee27f4a7435615"
            and inventory[
                "playground/common/winner_v127_constrained_ppo_losses.py"
            ]
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
        raise RuntimeError(f"T210 preregistration checks failed: {failed}")
    basis: dict[str, Any] = {
        "schema_version": (
            "open_duck.t210_dual_roll_cost_hosted_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T210_DUAL_ROLL_COST_HOSTED_CONTINUATION"
        ),
        "decision": "AUTHORIZE_ONE_HASH_FROZEN_T210_L4_CONTINUATION",
        "repository_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "question": (
            "Does one exact T203-half continuation with a separate dense "
            "roll-cost critic and derived dual price preserve gait while "
            "preventing the fixed-price final-checkpoint regression?"
        ),
        "causal_basis": {
            "failure": (
                "T203 passed nominal 16/16 but failed one final-checkpoint "
                "targeted Y-negative cell"
            ),
            "signal": (
                "T208 replay detected the sole failure 47 ticks early and "
                "all 15 passing targeted traces had zero exceedance rows"
            ),
            "fixed_price_diagnosis": (
                "T203 delayed but did not remove the failure and its hosted "
                "cost regressed from half to final"
            ),
            "training_contract": (
                "T209 proves exact cost/reward separation, pure V127 "
                "Lagrangian wiring, protected restore/update scope, dual "
                "law, and unchanged ONNX ABI"
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
            "risk": "abs(roll + 0.08 * roll_rate)",
            "passing_envelope_rad": 0.3541802655745987,
            "cost": "unscaled_squared_excess",
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
        "# T210 dual roll-cost hosted preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Source: exact T203 half checkpoint\n"
        "- Run: one L4, 2,007,040 steps, no retry/resume\n"
        "- Constraint: separate dense roll-cost critic and derived dual\n"
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
