#!/usr/bin/env python3
"""Preregister one T113 always-on expert hosted continuation."""

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
CPU_RESULT = ANALYSIS / "t112b_cpu_recovery_result.json"
CPU_PREREG = ANALYSIS / "t112b_cpu_recovery_preregistration.json"
T100C_VALIDATION = ANALYSIS / "t100c_recovered_training_validation.json"
DRIVER = ROOT / "tools" / "colab_t113_always_on_trainthrough.py"
BASE_DRIVER = ROOT / "tools" / "colab_t78_endpoint_joint_adapter_continuation.py"
PLAYGROUND = Path(
    "D:/CodexProjects/Open_Duck_Playground-t112-always-on-expert-v1"
)
SOURCE = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t100c_colab_extracted_20260728/"
    "t78_endpoint_joint_adapter_continuation/training/"
    "2026_07_29_023820_1003520"
)
STEP_ZERO = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t112_always_on_trainthrough_cpu_v1/"
    "t100c_half_expected_always_on.onnx"
)
REFERENCE = ANALYSIS / "ground_up_projected_reference_feature_table.npz"
GATE = ANALYSIS / "t98_hidden_gate_asset.json"
OUTPUT = ANALYSIS / "t113_always_on_trainthrough_hosted_preregistration.json"
MARKDOWN = ANALYSIS / "T113_ALWAYS_ON_TRAINTHROUGH_HOSTED_PREREGISTRATION_20260729.md"


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T113 prereg: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("formal T113 preregistration requires clean worktree")

    cpu = json.loads(CPU_RESULT.read_text(encoding="utf-8"))
    cpu_prereg = json.loads(CPU_PREREG.read_text(encoding="utf-8"))
    t100c = json.loads(T100C_VALIDATION.read_text(encoding="utf-8"))
    t100c_half = next(
        item
        for item in t100c["exports"]["checkpoints"]
        if item["step"] == 1_003_520
    )
    inventory = source_inventory(PLAYGROUND)
    input_hashes = {
        "driver": sha256(DRIVER),
        "base_driver": sha256(BASE_DRIVER),
        "cpu_result": sha256(CPU_RESULT),
        "source_checkpoint": directory_sha256(SOURCE),
        "reference_features": sha256(REFERENCE),
        "expected_step_zero_raw": sha256(STEP_ZERO),
        "hidden_gate_static_asset": sha256(GATE),
        "playground_inventory": canonical_sha256(inventory),
    }
    checks = {
        "cpu_contract_passed_exactly": (
            cpu["status"] == "PASS_T112B_READ_ONLY_CPU_RECOVERY"
            and cpu["failed_checks"] == []
            and cpu["decision"]
            == "EARN_T113_ALWAYS_ON_TRAINTHROUGH_HOSTED_PREREGISTRATION_ONLY"
            and cpu["execution"]["additional_optimizer_steps"] == 0
        ),
        "source_is_exact_t100c_half": (
            t100c["status"] == "PASS_T100C_RECOVERED_TRAINING_VALIDATION"
            and t100c["failed_checks"] == []
            and Path(t100c_half["path"]).resolve() == SOURCE.resolve()
            and t100c_half["directory_sha256"] == directory_sha256(SOURCE)
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
        "cpu_step_zero_expected_graph_exact": (
            sha256(STEP_ZERO)
            == cpu_prereg["assets"]["expected_always_on_graph"]["sha256"]
            and Path(
                cpu_prereg["assets"]["expected_always_on_graph"]["path"]
            ).resolve()
            == STEP_ZERO.resolve()
        ),
        "no_reward_randomizer_optimizer_command_abi_change": True,
        "one_run_no_retry_or_same_run_resume": True,
        "both_checkpoint_persistence_required": True,
        "no_behavior_hosted_or_robot_execution_now": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T113 preregistration checks failed: {failed}")

    basis: dict[str, Any] = {
        "schema_version": "open_duck.t113_always_on_trainthrough_hosted_preregistration.v1",
        "status": (
            "PREREGISTERED_T113_ALWAYS_ON_TRAINTHROUGH_HOSTED_CONTINUATION"
        ),
        "decision": "AUTHORIZE_ONE_HASH_FROZEN_T113_L4_CONTINUATION",
        "repository_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "question": (
            "Does training the existing negative expert always-on across the "
            "unchanged eight endpoint strata produce two persistent "
            "checkpoints that retain nominal gait and close negative COM?"
        ),
        "causal_basis": {
            "routing_family_closed": (
                "hard 9/16, sigmoid 4/16, and posthoc always-on 6/16 close "
                "post-training routing transforms"
            ),
            "cpu_contract": (
                "all 72 trace rows changed after one update while mature "
                "actor, recurrent hidden output, and normalizer stayed exact"
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
            "source": "exact_T100C_half",
            "actor_trainable_groups": ["negative_adapter_location"],
            "critic_trainable": True,
            "normalizer_frozen": True,
            "forward_path": "negative_adapter_location_always_on",
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
                "# T113 always-on train-through hosted preregistration",
                "",
                f"- Status: `{value['status']}`",
                "- Source: exact T100C half checkpoint",
                "- Run: one L4, 2,007,040 steps, no retry/resume",
                "- Exports: 0 / 1,003,520 / 2,007,040",
                "- Trainable actor: negative expert only; critic trainable",
                "- Mature actor / normalizer: frozen",
                "- Both new checkpoints must pass; no selection",
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
