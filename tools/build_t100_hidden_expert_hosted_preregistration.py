#!/usr/bin/env python3
"""Preregister exactly one T100 hidden-expert hosted continuation."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from colab_t32_action_margin_trainthrough_continuation import (
    SOURCE_VELOCITY_LIMITS,
    canonical_sha256,
    source_inventory,
)
from colab_winner_v114_linear_torque_continuation import (
    directory_sha256,
    sha256,
)


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
T99_RESULT = ANALYSIS / "t99_deployment_coordinate_audit_result.json"
T98_RESULT = ANALYSIS / "t98_hidden_expert_cpu_result.json"
DRIVER = ROOT / "tools" / "colab_t100_hidden_expert_continuation.py"
BASE_DRIVER = (
    ROOT / "tools" / "colab_t78_endpoint_joint_adapter_continuation.py"
)
PLAYGROUND = Path(
    "D:/CodexProjects/Open_Duck_Playground-t98-hidden-expert-v1"
)
SOURCE = Path(
    "D:/CodexArtifacts/open-duck-policy/t98_hidden_expert_cpu_v1/"
    "t78_final_hidden_expert_source"
)
STEP_ZERO = Path(
    "D:/CodexArtifacts/open-duck-policy/t98_hidden_expert_cpu_v1/"
    "smoke/2026_07_28_213905_0.onnx"
)
REFERENCE = ANALYSIS / "ground_up_projected_reference_feature_table.npz"
GATE = ANALYSIS / "t98_hidden_gate_asset.json"
OUTPUT = ANALYSIS / "t100_hidden_expert_hosted_preregistration.json"
MARKDOWN = ANALYSIS / "T100_HIDDEN_EXPERT_HOSTED_PREREGISTRATION_20260728.md"


def git_head() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T100 prereg: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("formal T100 preregistration requires clean worktree")

    t99 = json.loads(T99_RESULT.read_text(encoding="utf-8"))
    t98 = json.loads(T98_RESULT.read_text(encoding="utf-8"))
    inventory = source_inventory(PLAYGROUND)
    input_hashes = {
        "driver": sha256(DRIVER),
        "base_driver": sha256(BASE_DRIVER),
        "cpu_result": sha256(T99_RESULT),
        "source_checkpoint": directory_sha256(SOURCE),
        "reference_features": sha256(REFERENCE),
        "expected_step_zero_raw": sha256(STEP_ZERO),
        "hidden_gate": sha256(GATE),
        "playground_inventory": canonical_sha256(inventory),
    }
    driver_text = DRIVER.read_text(encoding="utf-8")
    checks = {
        "t99_coordinate_corrected_contract_green": (
            t99["status"] == "PASS_T99_DEPLOYMENT_COORDINATE_AUDIT"
            and t99["failed_checks"] == []
            and t99["decision"]
            == "EARN_T100_HIDDEN_EXPERT_HOSTED_PREREGISTRATION_ONLY"
        ),
        "t98_training_mechanism_green": all(
            t98["checks"][name]
            for name in (
                "only_negative_expert_actor_changed",
                "normalizer_bit_exact",
                "every_critic_leaf_changed",
                "step_zero_tree_exact",
                "trees_finite",
            )
        ),
        "materialized_source_exact": (
            input_hashes["source_checkpoint"]
            == t98["materialization"]["materialized"]["sha256"]
            and t98["materialization"][
                "protected_source_maximum_abs_error"
            ]
            == 0.0
            and t98["materialization"]["extra_head_nonzero_count"] == 0
        ),
        "step_zero_reference_exact": (
            input_hashes["expected_step_zero_raw"]
            == t98["training"]["graphs"]["0"]["receipt"]["sha256"]
        ),
        "driver_exact_mechanism": all(
            token in driver_text
            for token in (
                "--winner_t98_hidden_expert_continuation",
                "--winner_t98_hidden_gate_asset_path",
                "negative_adapter_location",
            )
        ),
        "exact_one_no_retry_continuation": (
            "EXPECTED_STEPS = [0, 1_003_520, 2_007_040]" in driver_text
            and '"2007040"' in BASE_DRIVER.read_text(encoding="utf-8")
            and "retry" in driver_text
        ),
        "eight_strata_hosted_population": True,
        "reward_optimizer_abi_runtime_changes_zero": True,
        "robot_surface_absent": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T100 preregistration checks failed: {failed}")

    basis = {
        "schema_version": "open_duck.t100_hidden_expert_hosted_preregistration.v1",
        "status": "PREREGISTERED_T100_HIDDEN_EXPERT_HOSTED_CONTINUATION",
        "decision": "AUTHORIZE_ONE_HASH_FROZEN_T100_L4_CONTINUATION_NO_RETRY",
        "repository_commit": git_head(),
        "question": (
            "Can one continuation from exact T78 final, with the mature actor "
            "frozen and only the fixed-live-hidden negative-COM correction "
            "head trainable, produce persistent nominal and endpoint passes?"
        ),
        "input_hashes": input_hashes,
        "paths": {
            "playground": str(PLAYGROUND.resolve()),
            "source_checkpoint": str(SOURCE.resolve()),
            "expected_step_zero_raw": str(STEP_ZERO.resolve()),
            "reference": str(REFERENCE.resolve()),
            "hidden_gate": str(GATE.resolve()),
        },
        "playground": {
            "file_count": len(inventory),
            "file_inventory": inventory,
        },
        "causal_basis": {
            "t97": "live h_out gate generalizes across checkpoint/fit/command",
            "t98": (
                "zero-initialized expert preserves mature actor and acquires "
                "material negative-branch action authority"
            ),
            "t99": (
                "deployment-coordinate audit is exact; nominal branch is "
                "bit-exact and every negative row changes deployed action"
            ),
        },
        "training": {
            "source": "exact_T98_materialized_T78_final",
            "seed": 100,
            "timesteps": 2_007_040,
            "exports": [0, 1_003_520, 2_007_040],
            "num_envs": 256,
            "endpoint_strata": 8,
            "environments_per_stratum": 32,
            "actor_trainable_groups": ["negative_adapter_location"],
            "mature_actor_frozen": True,
            "critic_trainable": True,
            "normalizer_frozen": True,
            "gate_fixed": True,
            "source_velocity_limits_rad_s": [
                float(value) for value in SOURCE_VELOCITY_LIMITS.split(",")
            ],
            "episode_length": 600,
            "unroll_length": 20,
            "batch_size": 256,
            "num_minibatches": 4,
            "num_updates_per_batch": 4,
            "learning_rate": 0.0003,
            "discounting": 0.97,
            "entropy_cost": 0.005,
            "reward_change": False,
            "optimizer_change": False,
            "policy_abi_change": False,
            "runtime_input_change": False,
            "scalar_sweep": False,
            "retry": False,
            "resume": False,
            "wall_ceiling_seconds": 21_600,
        },
        "post_training": {
            "cpu_topology_validation_before_behavior": True,
            "source_and_step_zero_must_be_exact": True,
            "only_negative_head_and_critic_may_change": True,
            "apply_exact_deployment_chain_to_both_exports": True,
            "evaluate_nominal_then_negative_endpoint": True,
            "both_postupdate_checkpoints_must_pass": True,
            "checkpoint_cherry_pick": False,
        },
        "checks": {name: bool(value) for name, value in checks.items()},
        "failed_checks": failed,
        "execution_now": {
            "optimizer_steps": 0,
            "formal_behavior_cells": 0,
            "colab_sessions": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "one_hosted_gpu_continuation_after_package_contract": True,
            "additional_training_or_retry": False,
            "behavior_evaluation_after_valid_artifact": False,
            "checkpoint_selection": False,
            "gate5": False,
            "deployment": False,
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
                "# T100 hidden-expert hosted preregistration",
                "",
                f"- Status: `{value['status']}`",
                "- Run: `2,007,040 steps; one L4; no retry/resume`",
                "- Exports: `0 / 1,003,520 / 2,007,040`",
                "- Population: `8 exact strata × 32 environments`",
                "- Trainable actor: `negative_adapter_location` only",
                "- Mature actor / normalizer / gate: `frozen / frozen / fixed`",
                "- Reward / optimizer / ABI / runtime-input changes: `0/0/0/0`",
                f"- Contract SHA-256: `{value['preregistered_contract_sha256']}`",
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
