#!/usr/bin/env python3
"""Preregister one T120 joint soft-router hosted continuation."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from colab_t32_action_margin_trainthrough_continuation import (  # noqa: E402
    canonical_sha256,
    source_inventory,
)
from colab_winner_v114_linear_torque_continuation import (  # noqa: E402
    directory_sha256,
    sha256,
)


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
CPU_RESULT = ANALYSIS / "t119_joint_soft_router_cpu_result.json"
RECOVERY = ANALYSIS / "t119b_random_binding_recovery_result.json"
DRIVER = ROOT / "tools" / "colab_t120_joint_soft_router_trainthrough.py"
BASE_DRIVER = ROOT / "tools" / "colab_t78_endpoint_joint_adapter_continuation.py"
PLAYGROUND = Path(
    "D:/CodexProjects/Open_Duck_Playground-t119-joint-soft-router-v1"
)
SOURCE = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t119_joint_soft_router_assets_v2/expanded_checkpoint"
)
STEP_ZERO = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t119_joint_soft_router_assets_v2/t119_step_zero.onnx"
)
REFERENCE = ANALYSIS / "ground_up_projected_reference_feature_table.npz"
GATE = ANALYSIS / "t98_hidden_gate_asset.json"
OUTPUT = ANALYSIS / "t120_joint_soft_router_hosted_preregistration.json"
MARKDOWN = (
    ANALYSIS / "T120_JOINT_SOFT_ROUTER_HOSTED_PREREGISTRATION_20260729.md"
)


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T120 prereg: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("formal T120 preregistration requires clean tree")

    cpu = json.loads(CPU_RESULT.read_text(encoding="utf-8"))
    recovery = json.loads(RECOVERY.read_text(encoding="utf-8"))
    inventory = source_inventory(PLAYGROUND)
    input_hashes = {
        "driver": sha256(DRIVER),
        "base_driver": sha256(BASE_DRIVER),
        "cpu_result": sha256(CPU_RESULT),
        "recovery_result": sha256(RECOVERY),
        "source_checkpoint": directory_sha256(SOURCE),
        "reference_features": sha256(REFERENCE),
        "expected_step_zero_raw": sha256(STEP_ZERO),
        "hidden_gate_static_asset": sha256(GATE),
        "playground_inventory": canonical_sha256(inventory),
    }
    checks = {
        "cpu_contract_recovered_exactly": (
            cpu["status"] == "HOLD_T119_JOINT_SOFT_ROUTER_CPU_CONTRACT"
            and cpu["failed_checks"] == ["random_action_and_router_binding"]
            and recovery["status"]
            == "PASS_T119B_READ_ONLY_BINDING_RECOVERY"
            and recovery["failed_checks"] == []
            and recovery["decision"]
            == (
                "RECOVER_T119_CPU_CONTRACT_AND_EARN_T120_HOSTED_"
                "PREREGISTRATION_ONLY"
            )
            and recovery["execution"]["optimizer_steps"] == 0
        ),
        "primary_trace_bindings_green": (
            cpu["checks"]["nominal_population_action_and_router_binding"]
            and cpu["checks"][
                "negative_population_action_and_router_binding"
            ]
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
        "step_zero_matches_cpu_contract": (
            sha256(STEP_ZERO)
            == cpu["training"]["graphs"]["0"]["receipt"]["sha256"]
        ),
        "no_reward_randomizer_optimizer_command_abi_change": True,
        "one_run_no_retry_or_same_run_resume": True,
        "both_checkpoint_persistence_required": True,
        "no_behavior_hosted_or_robot_execution_now": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T120 preregistration checks failed: {failed}")

    basis: dict[str, Any] = {
        "schema_version": (
            "open_duck.t120_joint_soft_router_hosted_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T120_JOINT_SOFT_ROUTER_HOSTED_CONTINUATION"
        ),
        "decision": "AUTHORIZE_ONE_HASH_FROZEN_T120_L4_CONTINUATION",
        "repository_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "question": (
            "Does jointly training the continuous router and negative-COM "
            "expert through the unchanged eight endpoint strata produce two "
            "persistent checkpoints that retain nominal gait and close the "
            "negative-COM endpoint?"
        ),
        "causal_basis": {
            "t118": (
                "failed moving cells span both supports and gait phase; "
                "simple support or phase masks are rejected"
            ),
            "cpu_contract": (
                "all 72 real trace rows bind learned router and action "
                "changes while mature actor and normalizer remain exact"
            ),
            "t119b": (
                "the sole auxiliary hold was caused by 100% out-of-support, "
                "100% tanh-saturated random inputs"
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
            "endpoint_strata": 8,
            "strata_population_per_batch": 32,
            "source": "exact_T100C_half_expanded_zero_router_deltas",
            "actor_trainable_groups": [
                "negative_adapter_location",
                "soft_router_coefficient_delta",
                "soft_router_intercept_delta",
            ],
            "critic_trainable": True,
            "normalizer_frozen": True,
            "forward_path": "sigmoid_soft_router_times_negative_expert",
            "reward_change": False,
            "randomizer_change": False,
            "optimizer_change": False,
            "command_support_change": False,
            "policy_abi_change": False,
            "retry": False,
            "same_run_resume": False,
            "gpu": "L4",
            "maximum_wall_seconds": 21_600,
        },
        "post_training": {
            "recover_and_hash_all_three_exports": True,
            "validate_tree_and_raw_onnx_before_behavior": True,
            "evaluate_both_new_checkpoints": True,
            "nominal_matrix_first": True,
            "negative_com_matrix_second_if_nominal_green": True,
            "full_frozen_robustness_only_if_both_green": True,
            "both_checkpoint_persistence_required": True,
            "checkpoint_selection_or_cherry_pick": False,
            "gate5_remains_closed": True,
        },
        "checks": {name: bool(value) for name, value in checks.items()},
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
        "\n".join(
            [
                "# T120 joint soft-router hosted preregistration",
                "",
                f"- Status: `{value['status']}`",
                "- Source: exact T100C half plus zero router deltas",
                "- Run: one L4, 2,007,040 steps, no retry/resume",
                "- Exports: 0 / 1,003,520 / 2,007,040",
                "- Trainable: negative expert + two router deltas + critic",
                "- Mature actor / normalizer: frozen",
                "- Both new checkpoints must pass; no selection",
                f"- Contract SHA-256: "
                f"`{value['preregistered_contract_sha256']}`",
                "",
            ]
        ),
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
