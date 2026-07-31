#!/usr/bin/env python3
"""Preregister one no-retry T62 midpoint gait-transfer continuation."""

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

from colab_t62_midpoint_gait_transfer_continuation import (  # noqa: E402
    EXPECTED_MIDPOINT_EXPORTS,
    EXPECTED_TRANSFER_EXPORTS,
    MAX_WALL_SECONDS,
    MIDPOINT_STEPS,
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


T61_RESULT = ANALYSIS / "t61_midpoint_gait_transfer_cpu_result.json"
T61_PREREG = (
    ANALYSIS / "t61_midpoint_gait_transfer_cpu_preregistration.json"
)
REFERENCE = ANALYSIS / "ground_up_projected_reference_feature_table.npz"
DRIVER = ROOT / "tools" / "colab_t62_midpoint_gait_transfer_continuation.py"
BUILDER = Path(__file__).resolve()
TEST = (
    ROOT / "tests" / "test_t62_midpoint_gait_transfer_hosted_contract.py"
)
OUTPUT = (
    ANALYSIS
    / "t62_midpoint_gait_transfer_hosted_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "T62_MIDPOINT_GAIT_TRANSFER_HOSTED_PREREGISTRATION_20260728.md"
)


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T62: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"],
        cwd=ROOT,
        text=True,
    ).strip():
        raise RuntimeError("T62 preregistration requires a clean worktree")

    t61 = json.loads(T61_RESULT.read_text(encoding="utf-8"))
    t61_prereg = json.loads(T61_PREREG.read_text(encoding="utf-8"))
    source = Path(
        t61_prereg["assets"]["t56_balance_final_checkpoint"]["path"]
    ).resolve()
    playground = Path(t61_prereg["playground"]["path"]).resolve()
    inventory = source_inventory(playground)
    input_hashes = {
        "driver": sha256(DRIVER),
        "cpu_result": sha256(T61_RESULT),
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
    midpoint_command = runner_command(stage="midpoint", **dummy)
    transfer_command = runner_command(stage="transfer", **dummy)
    checks = {
        "t61_cpu_passed_and_earned_only_hosted_preregistration": (
            t61["status"]
            == "PASS_T61_MIDPOINT_GAIT_TRANSFER_CPU_CONTRACT"
            and t61["decision"]
            == "EARN_T62_MIDPOINT_GAIT_TRANSFER_HOSTED_PREREGISTRATION"
            and t61["failed_checks"] == []
            and t61["checks"]["midpoint_source_restore_exact"]
            and t61["checks"]["midpoint_step_zero_onnx_byte_exact_source"]
            and t61["checks"]["default_off_trajectory_bit_exact"]
            and t61["checks"]["all_deployment_contracts_green"]
            and not t61["authority"]["hosted_training"]
        ),
        "source_balance_checkpoint_exact": (
            source.is_dir()
            and input_hashes["source_checkpoint"]
            == t61_prereg["assets"][
                "t56_balance_final_checkpoint"
            ]["sha256"]
        ),
        "playground_inventory_exact_t61": (
            {
                path: item["sha256"]
                for path, item in inventory.items()
                if path.endswith(".py")
            }
            == t61_prereg["playground"]["python_inventory"]
        ),
        "midpoint_stage_one_standard_interval_exact": (
            MIDPOINT_STEPS == 1_003_520
            and EXPECTED_MIDPOINT_EXPORTS == [0, 1_003_520]
            and midpoint_command[
                midpoint_command.index("--num_timesteps") + 1
            ]
            == "1003520"
            and midpoint_command[
                midpoint_command.index("--ppo_num_evals") + 1
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
            "--winner_t61_midpoint_transfer_stage" in midpoint_command
            and "--winner_t55_transfer_stage" not in midpoint_command
            and "--winner_t55_transfer_stage" in transfer_command
            and "--winner_t61_midpoint_transfer_stage"
            not in transfer_command
        ),
        "all_frozen_training_constants_preserved": (
            SOURCE_VELOCITY_LIMITS in midpoint_command
            and SOURCE_VELOCITY_LIMITS in transfer_command
            and "--winner_t31_action_margin_trainthrough"
            in midpoint_command
            and "--winner_t31_action_margin_trainthrough"
            in transfer_command
            and "--winner_t19_support_trainthrough" in midpoint_command
            and "--winner_t19_support_trainthrough" in transfer_command
        ),
        "one_session_no_retry_no_sweep": True,
        "behavior_hosted_robot_execution_zero": True,
    }
    checks = {name: bool(passed) for name, passed in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    basis: dict[str, Any] = {
        "schema_version": (
            "open_duck.t62_midpoint_gait_transfer_hosted_"
            "preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T62_MIDPOINT_GAIT_TRANSFER_HOSTED_CONTINUATION"
            if not failed
            else "HOLD_T62_MIDPOINT_GAIT_TRANSFER_HOSTED_PREREGISTRATION"
        ),
        "decision": (
            "AUTHORIZE_ONE_HASH_FROZEN_T62_L4_CONTINUATION_WITHOUT_RETRY"
        ),
        "question": (
            "Does inserting one fixed midpoint locomotion interval before "
            "the full gait transfer remove T56's half-checkpoint "
            "consolidation gap while preserving its final gait?"
        ),
        "evidence_basis": {
            "t59_half": "0/6 moving cells green",
            "t59_final": "8/8 cells green",
            "t60_classification": "ABRUPT_TRANSFER_CONSOLIDATION_GAP",
            "t61_cpu_restore_update_export_passed": True,
            "midpoint_weight": 0.5,
            "midpoint_weight_derivation": (
                "arithmetic midpoint of closed 0 and 1 endpoints"
            ),
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
            "source": "exact_recovered_T56_balance_final_checkpoint",
            "architecture": "reference_residual_recurrent_adapter",
            "recurrent_hidden_size": 64,
            "midpoint_stage": {
                "timesteps": MIDPOINT_STEPS,
                "exports": EXPECTED_MIDPOINT_EXPORTS,
                "reward": (
                    "support plus fixed 0.5 complete locomotion reward"
                ),
            },
            "transfer_stage": {
                "restore": "exact midpoint-stage final checkpoint",
                "timesteps": TRANSFER_STEPS,
                "exports": EXPECTED_TRANSFER_EXPORTS,
                "reward": (
                    "complete frozen locomotion reward plus bilateral "
                    "single-support balance reward"
                ),
            },
            "total_timesteps": MIDPOINT_STEPS + TRANSFER_STEPS,
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
            "t61_result_sha256": sha256(T61_RESULT),
            "t61_preregistration_sha256": sha256(T61_PREREG),
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
                "# T62 midpoint gait-transfer hosted preregistration",
                "",
                f"- Status: `{value['status']}`",
                "- Source: recovered T56 balance-final checkpoint",
                "- Midpoint: `1,003,520 steps; exports 0/final`",
                "- Full transfer: `2,007,040 steps; exports 0/half/final`",
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
