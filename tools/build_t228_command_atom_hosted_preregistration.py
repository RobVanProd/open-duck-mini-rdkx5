#!/usr/bin/env python3
"""Preregister T228's one earned command-atom continuation."""

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
CPU_RESULT = ANALYSIS / "t227d_recovered_cpu_validation_result.json"
DRIVER = ROOT / "tools/colab_t228_command_atom_continuation.py"
BASE_T216 = ROOT / "tools/colab_t216_axis_complete_tilt_continuation.py"
PLAYGROUND = Path(
    "D:/CodexArtifacts/open-duck-policy/t227b_command_atom_cpu_source_v2"
)
TRAINING = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t216_colab_recovery_20260730/extracted/"
    "t216_axis_complete_tilt_continuation/training"
)
SOURCE = TRAINING / "2026_07_30_165259_2007040"
STEP_ZERO = TRAINING / "2026_07_30_165259_2007040.onnx"
REFERENCE = ANALYSIS / "ground_up_projected_reference_feature_table.npz"
GATE = ANALYSIS / "t98_hidden_gate_asset.json"
OUTPUT = ANALYSIS / "t228_command_atom_hosted_preregistration.json"
MARKDOWN = ANALYSIS / "T228_COMMAND_ATOM_HOSTED_PREREGISTRATION_20260730.md"


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T228: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T228 preregistration requires clean worktree")
    cpu = json.loads(CPU_RESULT.read_text(encoding="utf-8"))
    inventory = source_inventory(PLAYGROUND)
    input_hashes = {
        "driver": sha256(DRIVER),
        "base_t216_driver": sha256(BASE_T216),
        "cpu_result": sha256(CPU_RESULT),
        "source_checkpoint": directory_sha256(SOURCE),
        "reference_features": sha256(REFERENCE),
        "expected_step_zero_raw": sha256(STEP_ZERO),
        "hidden_gate_static_asset": sha256(GATE),
        "playground_inventory": canonical_sha256(inventory),
    }
    command_module = inventory[
        "playground/common/t227_command_atom_bank.py"
    ]
    checks = {
        "t227d_cpu_contract_green_and_earned_exactly": (
            cpu["status"] == "PASS_T227D_RECOVERED_CPU_VALIDATION"
            and cpu["failed_checks"] == []
            and all(cpu["checks"].values())
            and cpu["decision"]
            == (
                "EARN_T228_COMMAND_ATOM_HOSTED_CONTINUATION_"
                "PREREGISTRATION_ONLY"
            )
            and cpu["execution"]["formal_behavior_cells"] == 0
            and cpu["execution"]["hosted_compute_units"] == 0
        ),
        "source_is_exact_t216_final": (
            input_hashes["source_checkpoint"]
            == "d0e969cab98cbb8cf779792935c58058019c07d41a5e7ae0087136830ef21c0c"
            and input_hashes["expected_step_zero_raw"]
            == "2dd89adfc487da6ad41008bb2094b3e8d24c2fdff4ba233459df36879e2aa770"
        ),
        "command_atom_module_exact": (
            command_module["sha256"]
            == "e03b6ea7f9d3c7d52f2a69e472e01c9f8a63fd2c60361d4913ff8e05a42df00a"
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
                BASE_T216,
                CPU_RESULT,
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
        raise RuntimeError(f"T228 preregistration checks failed: {failed}")
    basis: dict[str, Any] = {
        "schema_version": (
            "open_duck.t228_command_atom_hosted_preregistration.v1"
        ),
        "status": "PREREGISTERED_T228_COMMAND_ATOM_HOSTED_CONTINUATION",
        "decision": "AUTHORIZE_ONE_HASH_FROZEN_T228_L4_CONTINUATION",
        "repository_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "question": (
            "Does one exact T216-final continuation over the proven "
            "8-configuration by 4-command Cartesian lattice preserve both "
            "checkpoints while repairing deterministic x=.074 support?"
        ),
        "causal_basis": {
            "failure": (
                "T225 passed 190/192 cells; only T216-half failed the "
                "torso-COM-z+.05 condition at exact x=.074 for both fits"
            ),
            "support_correction": (
                "T226B proved T216 already trained the exact COM endpoint, "
                "but no deterministic command atom was present"
            ),
            "cpu_contract": (
                "T227D proved the exact 32-cell Cartesian reset lattice, "
                "source restore, protected update scope, unchanged reward, "
                "cost, ABI, and deployment graph"
            ),
            "source_choice": (
                "T216 final is used because it already passes every upper-Z "
                "cell; both new exports remain mandatory"
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
            "configuration_strata": 8,
            "command_strata": 4,
            "cartesian_strata": 32,
            "environments_per_cartesian_stratum": 8,
            "command_groups": [
                "broad_continuous_[.074,.080)",
                "exact_.074",
                "exact_.077",
                "exact_.080",
            ],
            "source": "exact_T216_final",
            "reward_change": False,
            "cost_change": False,
            "axis_complete_tilt_dual_change": False,
            "actor_trainable_groups": ["negative_adapter_location"],
            "reward_critic_trainable": True,
            "cost_critic_trainable": True,
            "normalizer_frozen": True,
            "mature_actor_frozen": True,
            "x_zero_training": False,
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
            "compose_existing_deployment_repairs": True,
            "evaluate_both_new_checkpoints": True,
            "nominal_then_failed_torso_com_z_first": True,
            "full_frozen_r2_only_if_targeted_green": True,
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
        "# T228 command-atom hosted preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Source: exact T216 final checkpoint\n"
        "- Run: one L4, 2,007,040 steps, no retry/resume\n"
        "- Change: training population only, 8 configurations x 4 commands\n"
        "- Both new checkpoints must pass; no selection\n"
        f"- Contract SHA-256: `{value['preregistered_contract_sha256']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(
        "preregistered_contract_sha256="
        f"{value['preregistered_contract_sha256']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
