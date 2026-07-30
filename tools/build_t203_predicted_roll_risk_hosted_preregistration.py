#!/usr/bin/env python3
"""Preregister T203's one earned predicted-roll-risk continuation."""

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
CPU_RESULT = ANALYSIS / "t202_predicted_roll_risk_cpu_result.json"
RECOVERY_RESULT = ANALYSIS / "t202b_metric_namespace_recovery_result.json"
T171 = ANALYSIS / "t171_t170_recovered_training_validation.json"
DRIVER = ROOT / "tools/colab_t203_predicted_roll_risk_continuation.py"
BASE_T170 = ROOT / "tools/colab_t170_eight_stratum_head_continuation.py"
BASE_T78 = ROOT / "tools/colab_t78_endpoint_joint_adapter_continuation.py"
T32_DRIVER = (
    ROOT / "tools/colab_t32_action_margin_trainthrough_continuation.py"
)
HELPER = ROOT / "tools/colab_winner_v114_linear_torque_continuation.py"
PLAYGROUND = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t202_predicted_roll_risk_cpu_source_v1"
)
TRAINING = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t170_colab_recovery_20260729/extracted/"
    "t170_eight_stratum_head_continuation/training"
)
SOURCE = TRAINING / "2026_07_30_003907_1003520"
STEP_ZERO = TRAINING / "2026_07_30_003907_1003520.onnx"
REFERENCE = ANALYSIS / "ground_up_projected_reference_feature_table.npz"
GATE = ANALYSIS / "t98_hidden_gate_asset.json"
OUTPUT = ANALYSIS / "t203_predicted_roll_risk_hosted_preregistration.json"
MARKDOWN = (
    ANALYSIS / "T203_PREDICTED_ROLL_RISK_HOSTED_PREREGISTRATION_20260730.md"
)


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T203: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T203 preregistration requires clean worktree")
    cpu = json.loads(CPU_RESULT.read_text(encoding="utf-8"))
    recovery = json.loads(RECOVERY_RESULT.read_text(encoding="utf-8"))
    t171 = json.loads(T171.read_text(encoding="utf-8"))
    t171_half = next(
        item
        for item in t171["exports"]["checkpoints"]
        if item["step"] == 1_003_520
    )
    inventory = source_inventory(PLAYGROUND)
    input_hashes = {
        "driver": sha256(DRIVER),
        "base_t170_driver": sha256(BASE_T170),
        "base_t78_driver": sha256(BASE_T78),
        "t32_driver": sha256(T32_DRIVER),
        "helper": sha256(HELPER),
        "cpu_result": sha256(CPU_RESULT),
        "recovery_result": sha256(RECOVERY_RESULT),
        "t171_validation": sha256(T171),
        "source_checkpoint": directory_sha256(SOURCE),
        "reference_features": sha256(REFERENCE),
        "expected_step_zero_raw": sha256(STEP_ZERO),
        "hidden_gate_static_asset": sha256(GATE),
        "playground_inventory": canonical_sha256(inventory),
    }
    substantive = {
        name: passed
        for name, passed in cpu["checks"].items()
        if name != "training_roll_risk_metrics_finite"
    }
    checks = {
        "t202_substantive_cpu_contract_green": (
            cpu["status"] == "HOLD_T202_PREDICTED_ROLL_RISK_CPU_CONTRACT"
            and cpu["failed_checks"]
            == ["training_roll_risk_metrics_finite"]
            and all(substantive.values())
            and cpu["execution"]["optimizer_steps"] == 1024
            and cpu["execution"]["formal_behavior_cells"] == 0
        ),
        "t202b_metric_recovery_green_and_earned_exactly": (
            recovery["status"]
            == "PASS_T202B_METRIC_NAMESPACE_RECOVERY"
            and recovery["failed_checks"] == []
            and recovery["decision"]
            == (
                "EARN_T203_PREDICTED_ROLL_RISK_HOSTED_"
                "PREREGISTRATION_ONLY"
            )
            and recovery["execution"]["optimizer_steps"] == 0
        ),
        "source_is_exact_t170_half": (
            t171["status"]
            == "PASS_T171_T170_RECOVERED_TRAINING_VALIDATION"
            and t171["failed_checks"] == []
            and Path(t171_half["path"]).resolve() == SOURCE.resolve()
            and t171_half["directory_sha256"]
            == directory_sha256(SOURCE)
            and sha256(STEP_ZERO)
            == next(
                item["sha256"]
                for item in t171["exports"]["onnx"]
                if item["step"] == 1_003_520
            )
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
        raise RuntimeError(f"T203 preregistration checks failed: {failed}")
    basis: dict[str, Any] = {
        "schema_version": (
            "open_duck.t203_predicted_roll_risk_hosted_"
            "preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T203_PREDICTED_ROLL_RISK_HOSTED_CONTINUATION"
        ),
        "decision": "AUTHORIZE_ONE_HASH_FROZEN_T203_L4_CONTINUATION",
        "repository_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "question": (
            "Does one exact T170-half continuation with the pass-derived "
            "predicted-roll-risk objective produce two persistent "
            "checkpoints that pass nominal and frozen robustness gates?"
        ),
        "causal_basis": {
            "known_failures": (
                "T170 final and T194 half each end in sharp roll collapse"
            ),
            "source_transfer": (
                "T201B separates both failures from all 18 passing traces "
                "with one fixed signal and threshold"
            ),
            "training_contract": (
                "T202 proves exact default-off behavior, outside-clip cost, "
                "protected restore, intended update scope, and unchanged ABI"
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
            "source": "exact_T170_half",
            "risk": "abs(roll + 0.08 * roll_rate)",
            "passing_envelope_rad": 0.3541802655745987,
            "scale": 0.8017763166551805,
            "scale_derivation": (
                "one 0.4 alive tick averaged over both failures' 45 "
                "violating rows and 22.450151776859293 squared integral"
            ),
            "cost_placement": "outside_existing_positive_reward_clip",
            "support_objective": False,
            "actor_trainable_groups": ["negative_adapter_location"],
            "critic_trainable": True,
            "normalizer_frozen": True,
            "mature_actor_frozen": True,
            "optimizer_change_from_t170": False,
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
            "recover_and_hash_all_three_exports": True,
            "validate_tree_raw_onnx_and_roll_metrics_before_behavior": True,
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
        "# T203 predicted-roll-risk hosted preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Source: exact protected T170 half checkpoint\n"
        "- Run: one L4, 2,007,040 steps, no retry/resume\n"
        "- Objective: fixed predicted-roll squared excess outside clip\n"
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
