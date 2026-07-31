#!/usr/bin/env python3
"""Preregister the one earned T170 eight-stratum head continuation."""

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
CPU_RESULT = (
    ANALYSIS / "t169_eight_stratum_head_continuation_cpu_result.json"
)
DIAGNOSTIC_RESULT = ANALYSIS / "t169b_cpu_diagnostic_validity_result.json"
T100C_VALIDATION = ANALYSIS / "t100c_recovered_training_validation.json"
DRIVER = ROOT / "tools/colab_t170_eight_stratum_head_continuation.py"
BASE_DRIVER = ROOT / "tools/colab_t78_endpoint_joint_adapter_continuation.py"
PLAYGROUND = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t100c_original_driver_wrapper_package_v1/"
    "t100c_original_driver_wrapper_bundle/playground"
)
SOURCE = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t100c_colab_extracted_20260728/"
    "t78_endpoint_joint_adapter_continuation/training/"
    "2026_07_29_024350_2007040"
)
STEP_ZERO = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t100c_colab_extracted_20260728/"
    "t78_endpoint_joint_adapter_continuation/training/"
    "2026_07_29_024350_2007040.onnx"
)
REFERENCE = ANALYSIS / "ground_up_projected_reference_feature_table.npz"
GATE = ANALYSIS / "t98_hidden_gate_asset.json"
OUTPUT = (
    ANALYSIS / "t170_eight_stratum_head_hosted_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "T170_EIGHT_STRATUM_HEAD_HOSTED_PREREGISTRATION_20260729.md"
)


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T170: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T170 preregistration requires clean worktree")
    cpu = json.loads(CPU_RESULT.read_text(encoding="utf-8"))
    diagnostic = json.loads(
        DIAGNOSTIC_RESULT.read_text(encoding="utf-8")
    )
    t100c = json.loads(T100C_VALIDATION.read_text(encoding="utf-8"))
    t100c_final = next(
        item
        for item in t100c["exports"]["checkpoints"]
        if item["step"] == 2_007_040
    )
    inventory = source_inventory(PLAYGROUND)
    input_hashes = {
        "driver": sha256(DRIVER),
        "base_driver": sha256(BASE_DRIVER),
        "cpu_result": sha256(CPU_RESULT),
        "diagnostic_result": sha256(DIAGNOSTIC_RESULT),
        "source_checkpoint": directory_sha256(SOURCE),
        "reference_features": sha256(REFERENCE),
        "expected_step_zero_raw": sha256(STEP_ZERO),
        "hidden_gate_static_asset": sha256(GATE),
        "playground_inventory": canonical_sha256(inventory),
    }
    checks = {
        "cpu_execution_scope_and_leaf_isolation_exact": (
            cpu["status"]
            == "HOLD_T169_EIGHT_STRATUM_HEAD_CONTINUATION_CPU_CONTRACT"
            and set(cpu["failed_checks"])
            == {
                "eight_stratum_model_contract_exact",
                "postupdate_random_action_binding",
            }
            and cpu["checks"]["only_nominal_expert_actor_changed"]
            and cpu["checks"]["normalizer_bit_exact"]
            and cpu["checks"]["step_zero_raw_onnx_byte_exact"]
            and cpu["execution"]["optimizer_steps"] == 1024
        ),
        "diagnostic_false_negatives_closed_exactly": (
            diagnostic["status"]
            == "PASS_T169B_CPU_DIAGNOSTIC_VALIDITY_AUDIT"
            and diagnostic["failed_checks"] == []
            and diagnostic["decision"]
            == (
                "EARN_T170_EIGHT_STRATUM_HEAD_HOSTED_CONTINUATION_"
                "PREREGISTRATION_ONLY"
            )
            and diagnostic["endpoint_representation"][
                "float32_bit_exact"
            ]
            and diagnostic["protected_trace_binding"][
                "final_changed_fraction"
            ]
            == 0.875
        ),
        "source_is_exact_t100c_final": (
            t100c["status"] == "PASS_T100C_RECOVERED_TRAINING_VALIDATION"
            and t100c["failed_checks"] == []
            and Path(t100c_final["path"]).resolve() == SOURCE.resolve()
            and t100c_final["directory_sha256"]
            == directory_sha256(SOURCE)
        ),
        "source_and_assets_present": all(
            path.exists()
            for path in (
                DRIVER,
                BASE_DRIVER,
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
        raise RuntimeError(f"T170 preregistration checks failed: {failed}")
    basis: dict[str, Any] = {
        "schema_version": (
            "open_duck.t170_eight_stratum_head_hosted_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T170_EIGHT_STRATUM_HEAD_HOSTED_CONTINUATION"
        ),
        "decision": "AUTHORIZE_ONE_HASH_FROZEN_T170_L4_CONTINUATION",
        "repository_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "question": (
            "Does continued maturation of the exact T100C-final conditional "
            "head through its unchanged eight-stratum curriculum produce "
            "two persistent checkpoints for the complete R2 matrix?"
        ),
        "causal_basis": {
            "t168": (
                "one nominal adapter pair exactly explains the Y-negative "
                "half/final gap on all 8,152 protected rows"
            ),
            "t169_t169b": (
                "the 1,024-step continuation restored exactly, changed only "
                "that pair and critic, preserved the normalizer/mature actor, "
                "and bound the update on in-distribution traces"
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
            "endpoint_names": [
                "broad_random",
                "nominal",
                "torso_com_x_neg",
                "torso_com_x_pos",
                "torso_com_y_neg",
                "torso_com_y_pos",
                "torso_com_z_neg",
                "torso_com_z_pos",
            ],
            "source": "exact_T100C_final",
            "actor_trainable_groups": ["negative_adapter_location"],
            "critic_trainable": True,
            "normalizer_frozen": True,
            "mature_actor_frozen": True,
            "forward_path": "fixed_live_hidden_gate_plus_negative_adapter",
            "reward_change": False,
            "optimizer_change": False,
            "command_support_change": False,
            "network_capacity_change": False,
            "policy_abi_change": False,
            "retry": False,
            "same_run_resume": False,
            "gpu": "L4",
            "maximum_wall_seconds": 21_600,
        },
        "post_training": {
            "recover_and_hash_all_three_exports": True,
            "validate_tree_and_raw_onnx_before_behavior": True,
            "compose_existing_t164_x_positive_command_repairs": True,
            "evaluate_both_new_checkpoints": True,
            "targeted_y_negative_matrix_first": True,
            "full_frozen_r2_from_condition_1_if_targeted_green": True,
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
        "# T170 eight-stratum head hosted preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Source: exact T100C final checkpoint\n"
        "- Run: one L4, 2,007,040 steps, no retry/resume\n"
        "- Population: broad, nominal, ±X, ±Y, ±Z; 32 envs each\n"
        "- Trainable actor: existing conditional adapter pair only\n"
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
