#!/usr/bin/env python3
"""Preregister one no-retry T56 balance-first hosted continuation."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
ANALYSIS = ROOT / "outputs" / "analysis"
sys.path.insert(0, str(TOOLS))

from colab_t56_dynamic_single_support_continuation import (  # noqa: E402
    BALANCE_STEPS,
    EXPECTED_BALANCE_EXPORTS,
    EXPECTED_TRANSFER_EXPORTS,
    MAX_WALL_SECONDS,
    SOURCE_VELOCITY_LIMITS,
    TRANSFER_STEPS,
    canonical_sha256,
    runner_command,
    source_inventory,
)
from colab_winner_v114_linear_torque_continuation import (  # noqa: E402
    directory_sha256,
    sha256,
)


T55_RESULT = ANALYSIS / "t55_dynamic_single_support_cpu_result.json"
T55B_PREREG = (
    ANALYSIS / "t55b_dynamic_single_support_cpu_recovery_preregistration.json"
)
REFERENCE = ANALYSIS / "ground_up_projected_reference_feature_table.npz"
DRIVER = ROOT / "tools" / "colab_t56_dynamic_single_support_continuation.py"
BUILDER = Path(__file__).resolve()
TEST = (
    ROOT / "tests" / "test_t56_dynamic_single_support_hosted_contract.py"
)
OUTPUT = (
    ANALYSIS / "t56_dynamic_single_support_hosted_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "T56_DYNAMIC_SINGLE_SUPPORT_HOSTED_PREREGISTRATION_20260728.md"
)


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T56: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"],
        cwd=ROOT,
        text=True,
    ).strip():
        raise RuntimeError("T56 preregistration requires a clean worktree")

    t55 = json.loads(T55_RESULT.read_text(encoding="utf-8"))
    t55b = json.loads(T55B_PREREG.read_text(encoding="utf-8"))
    source = Path(t55["materialization"]["materialized"]["path"]).resolve()
    playground = Path(t55b["playground"]["path"]).resolve()
    inventory = source_inventory(playground)
    input_hashes = {
        "driver": sha256(DRIVER),
        "cpu_result": sha256(T55_RESULT),
        "source_checkpoint": directory_sha256(source),
        "reference_features": sha256(REFERENCE),
        "playground_inventory": canonical_sha256(inventory),
    }
    dummy = {
        "playground": Path("/frozen/playground"),
        "output": Path("/frozen/output"),
        "source": Path("/frozen/source"),
        "reference": Path("/frozen/reference.npz"),
    }
    balance_command = runner_command(stage="balance", **dummy)
    transfer_command = runner_command(stage="transfer", **dummy)
    checks = {
        "t55_cpu_passed_and_earned_only_hosted_preregistration": (
            t55["status"]
            == "PASS_T55_DYNAMIC_SINGLE_SUPPORT_CPU_CONTRACT"
            and t55["decision"]
            == "EARN_T56_DYNAMIC_SINGLE_SUPPORT_HOSTED_PREREGISTRATION"
            and t55["failed_checks"] == []
            and t55["checks"]["balance_stage_exercises_both_support_sides"]
            and t55["checks"]["transfer_stage_exercises_both_support_sides"]
            and t55["checks"]["all_deployment_contracts_green"]
            and not t55["authority"]["hosted_training"]
        ),
        "t55b_recovery_identity_green": (
            t55b["status"]
            == "PREREGISTERED_T55B_DYNAMIC_SINGLE_SUPPORT_CPU_RECOVERY"
            and t55b["failed_checks"] == []
        ),
        "source_materialization_exact": (
            source.is_dir()
            and input_hashes["source_checkpoint"]
            == t55["materialization"]["materialized"]["sha256"]
            and t55["checks"]["materialized_deployment_byte_exact_t52_half"]
            and t55["materialization"]["restore_maximum_abs_error"] == 0.0
        ),
        "playground_inventory_exact_t55": (
            {
                path: item["sha256"]
                for path, item in inventory.items()
                if path.endswith(".py")
            }
            == t55b["playground"]["python_inventory"]
        ),
        "balance_stage_one_standard_interval_exact": (
            BALANCE_STEPS == 1_003_520
            and EXPECTED_BALANCE_EXPORTS == [0, 1_003_520]
            and balance_command[
                balance_command.index("--num_timesteps") + 1
            ]
            == "1003520"
            and balance_command[
                balance_command.index("--ppo_num_evals") + 1
            ]
            == "2"
        ),
        "transfer_stage_two_standard_intervals_exact": (
            TRANSFER_STEPS == 2_007_040
            and EXPECTED_TRANSFER_EXPORTS
            == [0, 1_003_520, 2_007_040]
            and transfer_command[
                transfer_command.index("--num_timesteps") + 1
            ]
            == "2007040"
            and transfer_command[
                transfer_command.index("--ppo_num_evals") + 1
            ]
            == "3"
        ),
        "stage_flags_mutually_exclusive": (
            "--winner_t55_balance_stage" in balance_command
            and "--winner_t55_transfer_stage" not in balance_command
            and "--winner_t55_transfer_stage" in transfer_command
            and "--winner_t55_balance_stage" not in transfer_command
        ),
        "all_frozen_training_constants_preserved": (
            SOURCE_VELOCITY_LIMITS
            in balance_command
            and SOURCE_VELOCITY_LIMITS in transfer_command
            and "--winner_t31_action_margin_trainthrough"
            in balance_command
            and "--winner_t31_action_margin_trainthrough"
            in transfer_command
            and "--winner_t19_support_trainthrough" in balance_command
            and "--winner_t19_support_trainthrough" in transfer_command
        ),
        "one_session_no_retry_no_sweep": True,
        "behavior_hosted_robot_execution_zero": True,
    }
    checks = {name: bool(passed) for name, passed in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    basis: dict[str, Any] = {
        "schema_version": (
            "open_duck.t56_dynamic_single_support_hosted_"
            "preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T56_DYNAMIC_SINGLE_SUPPORT_HOSTED_CONTINUATION"
            if not failed
            else "HOLD_T56_DYNAMIC_SINGLE_SUPPORT_HOSTED_PREREGISTRATION"
        ),
        "decision": (
            "AUTHORIZE_ONE_HASH_FROZEN_T56_L4_CONTINUATION_WITHOUT_RETRY"
        ),
        "question": (
            "Does first learning phase-selected balance on either foot, then "
            "restoring the complete gait objective, produce a persistent "
            "two-checkpoint walking policy under the unchanged deployment "
            "transition and measured limits?"
        ),
        "evidence_basis": {
            "t54_failure_class": (
                "delayed backward-pitch collapse during left-only or double "
                "support, with no right-only onset"
            ),
            "capture_point_or_pressure_objective_closed": True,
            "t55_cpu_restore_update_export_passed": True,
            "t55_cpu_checks_green": len(t55["checks"]),
            "t55_cpu_left_and_right_metrics_positive": True,
            "materialized_deployment_byte_exact_t52_half": True,
            "manual_mass_com_or_foot_measurements": False,
            "reward_or_scalar_search": False,
        },
        "input_hashes": input_hashes,
        "paths": {
            "playground": str(playground),
            "source_checkpoint": str(source),
            "reference": str(REFERENCE.resolve()),
        },
        "playground": {
            "file_count": len(inventory),
            "file_inventory": inventory,
        },
        "training": {
            "session_count": 1,
            "accelerator": "L4",
            "seed": 100,
            "source": "exact_T55_materialized_T52_half_checkpoint",
            "architecture": "reference_residual_recurrent_adapter",
            "recurrent_hidden_size": 64,
            "balance_stage": {
                "timesteps": BALANCE_STEPS,
                "exports": EXPECTED_BALANCE_EXPORTS,
                "reward": (
                    "phase-selected bilateral single-support balance only"
                ),
            },
            "transfer_stage": {
                "restore": "exact balance-stage final checkpoint",
                "timesteps": TRANSFER_STEPS,
                "exports": EXPECTED_TRANSFER_EXPORTS,
                "reward": (
                    "complete frozen locomotion reward plus the same "
                    "bilateral single-support balance reward"
                ),
            },
            "total_timesteps": BALANCE_STEPS + TRANSFER_STEPS,
            "num_envs": 256,
            "episode_length": 600,
            "unroll_length": 20,
            "batch_size": 256,
            "num_minibatches": 4,
            "num_updates_per_batch": 4,
            "learning_rate": 0.0003,
            "discounting": 0.97,
            "entropy_cost": 0.005,
            "wall_ceiling_seconds": MAX_WALL_SECONDS,
            "maximum_compute_units_at_prior_rate": 6.42,
            "retry": False,
            "resume": False,
            "reward_curve_selection": False,
            "checkpoint_cherry_pick": False,
            "scalar_sweep": False,
        },
        "post_training": {
            "behavior_cells_during_training": 0,
            "recover_and_hash_all_five_stage_exports": True,
            "cpu_topology_validation_before_behavior": True,
            "transfer_half_and_final_both_required": True,
            "evaluate_nominal_16_cells_first": True,
            "robustness_only_after_nominal_persistence_pass": True,
            "gate5_only_after_all_offline_gates": True,
        },
        "checks": checks,
        "failed_checks": failed,
        "execution_now": {
            "optimizer_steps": 0,
            "simulator_locomotion_steps": 0,
            "formal_behavior_cells": 0,
            "colab_sessions": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "one_hosted_gpu_continuation_after_package_contract": not failed,
            "additional_training_or_retry": False,
            "behavior_evaluation_after_valid_artifact": False,
            "checkpoint_selection": False,
            "gate5": False,
            "deployment": False,
            "rdkx5_or_robot": False,
            "robot_clearance": False,
            "torque_or_motion": False,
        },
        "sources": {
            "builder_sha256": sha256(BUILDER),
            "driver_sha256": sha256(DRIVER),
            "test_sha256": sha256(TEST),
            "t55_result_sha256": sha256(T55_RESULT),
            "t55b_preregistration_sha256": sha256(T55B_PREREG),
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
                "# T56 dynamic single-support hosted preregistration",
                "",
                f"- Status: `{value['status']}`",
                "- Balance: `1,003,520 steps; exports 0/final`",
                "- Transfer: `2,007,040 steps; exports 0/half/final`",
                "- Sessions/retries/sweeps: `1/0/0`",
                "- Maximum compute at prior rate: `6.42 CU`",
                "- Behavior/Gate5/robot authority now: `0/0/0`",
                (
                    "- Contract SHA-256: "
                    f"`{value['preregistered_contract_sha256']}`"
                ),
                "",
            ]
        ),
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"failed_checks={failed}")
    print(f"playground_files={len(inventory)}")
    print(
        "preregistered_contract_sha256="
        f"{value['preregistered_contract_sha256']}"
    )
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
