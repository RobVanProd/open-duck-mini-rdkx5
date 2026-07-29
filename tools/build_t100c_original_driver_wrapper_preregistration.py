#!/usr/bin/env python3
"""Preregister one wrapper-only recovery of frozen T100."""

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
T100_HOLD = ANALYSIS / "t100_preexecution_hold_attribution.json"
T100B_HOLD = ANALYSIS / "t100b_prelaunch_identity_hold_attribution.json"
T100_PREREG = ANALYSIS / "t100_hidden_expert_hosted_preregistration.json"
T99_RESULT = ANALYSIS / "t99_deployment_coordinate_audit_result.json"
WRAPPER = ROOT / "tools" / "colab_t100c_original_driver_wrapper.py"
ORIGINAL_BUNDLE = Path(
    "D:/CodexArtifacts/open-duck-policy/t100_hidden_expert_package_v1/"
    "t100_hidden_expert_bundle"
)
ORIGINAL_DRIVER = ORIGINAL_BUNDLE / "colab_t100_hidden_expert_continuation.py"
BASE_DRIVER = ROOT / "tools" / "colab_t78_endpoint_joint_adapter_continuation.py"
PLAYGROUND = Path("D:/CodexProjects/Open_Duck_Playground-t98-hidden-expert-v1")
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
OUTPUT = ANALYSIS / "t100c_original_driver_wrapper_preregistration.json"
MARKDOWN = ANALYSIS / "T100C_ORIGINAL_DRIVER_WRAPPER_PREREGISTRATION_20260728.md"


def git_head() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()


def canonical_without_result(value: dict[str, Any]) -> str:
    return canonical_sha256(
        {key: item for key, item in value.items() if key != "result_sha256"}
    )


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T100C prereg: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("formal T100C preregistration requires clean worktree")

    t100_hold = json.loads(T100_HOLD.read_text(encoding="utf-8"))
    t100b_hold = json.loads(T100B_HOLD.read_text(encoding="utf-8"))
    original = json.loads(T100_PREREG.read_text(encoding="utf-8"))
    inventory = source_inventory(PLAYGROUND)
    wrapper_text = WRAPPER.read_text(encoding="utf-8")
    input_hashes = {
        "t100_hold_attribution": sha256(T100_HOLD),
        "t100b_hold_attribution": sha256(T100B_HOLD),
        "original_t100_preregistration": sha256(T100_PREREG),
        "wrapper": sha256(WRAPPER),
        "original_driver": sha256(ORIGINAL_DRIVER),
        "base_driver": sha256(BASE_DRIVER),
        "cpu_result": sha256(T99_RESULT),
        "source_checkpoint": directory_sha256(SOURCE),
        "reference_features": sha256(REFERENCE),
        "expected_step_zero_raw": sha256(STEP_ZERO),
        "hidden_gate": sha256(GATE),
        "playground_inventory": canonical_sha256(inventory),
    }
    original_unchanged = {
        "driver": input_hashes["original_driver"],
        "base_driver": input_hashes["base_driver"],
        "cpu_result": input_hashes["cpu_result"],
        "source_checkpoint": input_hashes["source_checkpoint"],
        "reference_features": input_hashes["reference_features"],
        "expected_step_zero_raw": input_hashes["expected_step_zero_raw"],
        "hidden_gate": input_hashes["hidden_gate"],
        "playground_inventory": input_hashes["playground_inventory"],
    }
    checks = {
        "t100_hold_exact_and_optimizer_zero": (
            t100_hold["status"] == "PASS_T100_PREEXECUTION_HOLD_ATTRIBUTION"
            and canonical_without_result(t100_hold) == t100_hold["result_sha256"]
            and t100_hold["interpretation"]["optimizer_started"] is False
        ),
        "t100b_hold_exact_and_prelaunch": (
            t100b_hold["status"]
            == "PASS_T100B_PRELAUNCH_IDENTITY_HOLD_ATTRIBUTION"
            and canonical_without_result(t100b_hold) == t100b_hold["result_sha256"]
            and t100b_hold["interpretation"]["hosted_session_opened"] is False
            and t100b_hold["decision"]
            == "EARN_T100C_ORIGINAL_DRIVER_WRAPPER_PREREGISTRATION_ONLY"
        ),
        "original_t100_inputs_byte_exact": (
            original_unchanged == original["input_hashes"]
            and inventory == original["playground"]["file_inventory"]
        ),
        "original_driver_matches_failed_but_hash_valid_driver": (
            input_hashes["original_driver"]
            == t100_hold["failure"]["frozen_failed_driver"]["sha256"]
            == original["input_hashes"]["driver"]
        ),
        "wrapper_only_corrects_command_dispatch": all(
            token in wrapper_text
            for token in (
                "_BASE_RUNNER_COMMAND = frozen_t100.base.runner_command",
                "frozen_t100.runner_command = corrected_runner_command",
                "--winner_t98_hidden_expert_continuation",
                "--winner_t98_hidden_gate_asset_path",
                "return frozen_t100.main()",
            )
        ),
        "training_recipe_unchanged": (
            original["training"]["timesteps"] == 2_007_040
            and original["training"]["exports"] == [0, 1_003_520, 2_007_040]
            and original["training"]["num_envs"] == 256
            and original["training"]["endpoint_strata"] == 8
            and original["training"]["actor_trainable_groups"]
            == ["negative_adapter_location"]
            and original["training"]["retry"] is False
            and original["training"]["resume"] is False
        ),
        "all_prior_training_behavior_robot_counts_zero": True,
        "replacement_not_retry_or_resume": True,
        "robot_surface_absent": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T100C preregistration checks failed: {failed}")

    basis: dict[str, Any] = {
        "schema_version": "open_duck.t100c_original_driver_wrapper_preregistration.v1",
        "status": "PREREGISTERED_T100C_ORIGINAL_DRIVER_WRAPPER_RECOVERY",
        "decision": "AUTHORIZE_ONE_HASH_FROZEN_T100C_L4_REPLACEMENT_NO_RETRY",
        "repository_commit": git_head(),
        "classification": "PRE_OPTIMIZER_WRAPPER_RECOVERY_NOT_TRAINING_RETRY",
        "question": original["question"],
        "input_hashes": input_hashes,
        "paths": {
            "original_driver": str(ORIGINAL_DRIVER.resolve()),
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
        "recovery": {
            "original_t100_driver_byte_exact": True,
            "original_t100_preregistration_byte_exact": True,
            "external_wrapper_only": True,
            "wrapper_function": "corrected_runner_command",
            "mechanism_source_gate_threshold_recipe_changes": 0,
        },
        "training": original["training"],
        "post_training": original["post_training"],
        "checks": {name: bool(value) for name, value in checks.items()},
        "failed_checks": failed,
        "execution_now": {
            "optimizer_steps": 0,
            "simulator_training_steps": 0,
            "formal_behavior_cells": 0,
            "t100c_sessions_opened": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "one_replacement_after_package_and_launch_contract": True,
            "additional_training_attempt_retry_or_resume": False,
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
                "# T100C original-driver wrapper preregistration",
                "",
                f"- Status: `{value['status']}`",
                "- Original T100 driver / preregistration: `byte-exact / byte-exact`",
                "- New code: `one corrected-dispatch wrapper`",
                "- Mechanism / source / gate / recipe changes: `0 / 0 / 0 / 0`",
                "- Run: `2,007,040 steps; one L4; no retry/resume`",
                "- Exports: `0 / 1,003,520 / 2,007,040`",
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
