#!/usr/bin/env python3
"""Preregister one T100B replacement after T100's pre-optimizer hold."""

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
ATTRIBUTION = ANALYSIS / "t100_preexecution_hold_attribution.json"
T100_PREREG = ANALYSIS / "t100_hidden_expert_hosted_preregistration.json"
T99_RESULT = ANALYSIS / "t99_deployment_coordinate_audit_result.json"
DRIVER = ROOT / "tools" / "colab_t100_hidden_expert_continuation.py"
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
OUTPUT = ANALYSIS / "t100b_preexecution_recovery_preregistration.json"
MARKDOWN = ANALYSIS / "T100B_PREEXECUTION_RECOVERY_PREREGISTRATION_20260728.md"


def git_head() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()


def without_result_sha(value: dict[str, Any]) -> dict[str, Any]:
    return {key: item for key, item in value.items() if key != "result_sha256"}


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T100B prereg: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("formal T100B preregistration requires clean worktree")

    attribution = json.loads(ATTRIBUTION.read_text(encoding="utf-8"))
    t100 = json.loads(T100_PREREG.read_text(encoding="utf-8"))
    t99 = json.loads(T99_RESULT.read_text(encoding="utf-8"))
    inventory = source_inventory(PLAYGROUND)
    old_driver = Path(
        attribution["failure"]["frozen_failed_driver"]["path"]
    ).read_text(encoding="utf-8")
    fixed_driver = DRIVER.read_text(encoding="utf-8")
    expected_fixed = old_driver.replace(
        "EXPECTED_STEPS = [0, 1_003_520, 2_007_040]\n",
        "EXPECTED_STEPS = [0, 1_003_520, 2_007_040]\n"
        "_BASE_RUNNER_COMMAND = base.runner_command\n",
        1,
    ).replace(
        "command = base.runner_command(playground, output, source, reference)",
        "command = _BASE_RUNNER_COMMAND(playground, output, source, reference)",
        1,
    )
    input_hashes = {
        "attribution": sha256(ATTRIBUTION),
        "original_t100_preregistration": sha256(T100_PREREG),
        "driver": sha256(DRIVER),
        "base_driver": sha256(BASE_DRIVER),
        "cpu_result": sha256(T99_RESULT),
        "source_checkpoint": directory_sha256(SOURCE),
        "reference_features": sha256(REFERENCE),
        "expected_step_zero_raw": sha256(STEP_ZERO),
        "hidden_gate": sha256(GATE),
        "playground_inventory": canonical_sha256(inventory),
    }
    unchanged_keys = (
        "base_driver",
        "cpu_result",
        "source_checkpoint",
        "reference_features",
        "expected_step_zero_raw",
        "hidden_gate",
        "playground_inventory",
    )
    checks = {
        "attribution_identity_exact": (
            attribution["status"] == "PASS_T100_PREEXECUTION_HOLD_ATTRIBUTION"
            and attribution["failed_checks"] == []
            and attribution["decision"]
            == "EARN_ONE_T100B_PREEXECUTION_RECOVERY_PREREGISTRATION_ONLY"
            and canonical_sha256(without_result_sha(attribution))
            == attribution["result_sha256"]
        ),
        "optimizer_and_simulator_never_started": (
            attribution["interpretation"]["optimizer_started"] is False
            and attribution["interpretation"]["simulator_training_started"] is False
            and attribution["interpretation"]["hosted_training_attempt_consumed"]
            is False
        ),
        "driver_fix_exactly_dispatch_capture": fixed_driver == expected_fixed,
        "old_and_fixed_driver_hashes_match_attribution": (
            t100["input_hashes"]["driver"]
            == attribution["failure"]["frozen_failed_driver"]["sha256"]
            and input_hashes["driver"]
            == attribution["failure"]["fixed_driver"]["sha256"]
        ),
        "all_non_driver_inputs_unchanged": all(
            input_hashes[key] == t100["input_hashes"][key]
            for key in unchanged_keys
        ),
        "training_recipe_unchanged": (
            t100["training"]["timesteps"] == 2_007_040
            and t100["training"]["exports"] == [0, 1_003_520, 2_007_040]
            and t100["training"]["num_envs"] == 256
            and t100["training"]["endpoint_strata"] == 8
            and t100["training"]["actor_trainable_groups"]
            == ["negative_adapter_location"]
            and t100["training"]["retry"] is False
            and t100["training"]["resume"] is False
        ),
        "t99_deployment_coordinate_contract_still_green": (
            t99["status"] == "PASS_T99_DEPLOYMENT_COORDINATE_AUDIT"
            and t99["failed_checks"] == []
        ),
        "replacement_not_retry_or_resume": True,
        "robot_surface_absent": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T100B preregistration checks failed: {failed}")

    basis: dict[str, Any] = {
        "schema_version": "open_duck.t100b_preexecution_recovery_preregistration.v1",
        "status": "PREREGISTERED_T100B_PREEXECUTION_RECOVERY",
        "decision": "AUTHORIZE_ONE_HASH_FROZEN_T100B_L4_REPLACEMENT_NO_RETRY",
        "repository_commit": git_head(),
        "classification": "PRE_OPTIMIZER_REPLACEMENT_NOT_TRAINING_RETRY",
        "question": t100["question"],
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
        "allowed_change": {
            "file": str(DRIVER.resolve()),
            "description": (
                "capture base.runner_command before wrapper replacement and "
                "invoke that captured function"
            ),
            "line_additions": 2,
            "line_deletions": 1,
            "mechanism_change": False,
            "training_recipe_change": False,
            "gate_or_threshold_change": False,
        },
        "training": t100["training"],
        "post_training": t100["post_training"],
        "checks": {name: bool(value) for name, value in checks.items()},
        "failed_checks": failed,
        "execution_now": {
            "optimizer_steps": 0,
            "simulator_training_steps": 0,
            "formal_behavior_cells": 0,
            "replacement_sessions_opened": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "one_replacement_after_package_and_launch_contract": True,
            "additional_training_attempt_or_retry": False,
            "resume": False,
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
                "# T100B pre-execution recovery preregistration",
                "",
                f"- Status: `{value['status']}`",
                "- Classification: `replacement after zero optimizer work`",
                "- Allowed change: `capture and call the original command builder`",
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
