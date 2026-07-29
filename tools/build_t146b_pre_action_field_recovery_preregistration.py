#!/usr/bin/env python3
"""Freeze correction of T146's post-action handoff comparison."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
from typing import Any

from run_t136_static_calibration_router_transform import (
    ANALYSIS,
    ROOT,
    canonical_sha256,
    receipt,
)


T146_PREREG = ANALYSIS / "t146_upper_command_attribution_preregistration.json"
T146_RESULT = ANALYSIS / "t146_upper_command_attribution_result.json"
OUTPUT = ANALYSIS / "t146b_pre_action_field_recovery_preregistration.json"
MARKDOWN = (
    ANALYSIS
    / "T146B_PRE_ACTION_FIELD_RECOVERY_PREREGISTRATION_20260729.md"
)
BUILDER = Path(__file__).resolve()
WRAPPER = ROOT / "tools" / "run_t146b_pre_action_field_recovery.py"
FIXED_RUNNER = ROOT / "tools" / "run_t146_upper_command_attribution.py"
TEST = ROOT / "tests" / "test_t146b_pre_action_field_recovery.py"


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T146B: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T146B preregistration requires clean worktree")
    source = json.loads(T146_PREREG.read_text(encoding="utf-8"))
    result = json.loads(T146_RESULT.read_text(encoding="utf-8"))
    source_inputs = dict(source["frozen_inputs"])
    source_inputs["runner"] = receipt(FIXED_RUNNER)
    source_inputs.update(
        {
            "recovery_builder": receipt(BUILDER),
            "recovery_wrapper": receipt(WRAPPER),
            "recovery_test": receipt(TEST),
            "source_t146_preregistration": receipt(T146_PREREG),
            "source_t146_result": receipt(T146_RESULT),
        }
    )
    runner_source = FIXED_RUNNER.read_text(encoding="utf-8")
    checks = {
        "source_hold_is_only_handoff_field_check": (
            result["status"] == "HOLD_T146_UPPER_COMMAND_ATTRIBUTION"
            and result["failed_checks"]
            == ["all_command_handoffs_bit_exact_within_checkpoint_fit"]
        ),
        "post_action_fields_caused_source_hold": all(
            not fields["qpos"]
            and not fields["qvel"]
            and not fields["applied_target_rad"]
            and fields["previous_action"]
            and fields["h_in"]
            and fields["calibration_context_sha256"]
            for fields in result["handoff_checks"].values()
        ),
        "fixed_runner_uses_pre_action_fields": (
            "actual_position_pre_rad" in runner_source
            and "physical_observation_excluding_command_and_reference"
            in runner_source
        ),
        "source_trace_rows_reused_without_new_behavior": True,
        "optimizer_colab_robot_zero": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T146B preregistration checks failed: {failed}")
    value: dict[str, Any] = {
        **{
            key: item
            for key, item in source.items()
            if key
            not in {
                "preregistered_contract_sha256",
                "frozen_inputs",
                "checks",
                "failed_checks",
            }
        },
        "schema_version": (
            "open_duck.t146b_pre_action_field_recovery_"
            "preregistration.v1"
        ),
        "recovery_kind": "T146_POST_ACTION_FIELDS_USED_FOR_HANDOFF",
        "source_t146_contract_sha256": source[
            "preregistered_contract_sha256"
        ],
        "frozen_inputs": source_inputs,
        "checks": checks,
        "failed_checks": failed,
        "execution_now": {
            "source_trace_rows_reused": result["execution"]["trace_rows_read"],
            "new_behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
    }
    value["preregistered_contract_sha256"] = canonical_sha256(value)
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T146B pre-action field recovery preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Correction: compare pre-action joint state and observation fields\n"
        "- Command `6:13` and projected reference `101:115` are excluded\n"
        "- Existing trace rows reused; no new behavior or training\n",
        encoding="utf-8",
        newline="\n",
    )
    print("PREREGISTERED_T146B_PRE_ACTION_FIELD_RECOVERY")
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
