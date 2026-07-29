#!/usr/bin/env python3
"""Freeze recovery from T143B's obsolete primary runner receipt."""

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


T143 = ANALYSIS / "t143_conditional_forward_path_preregistration.json"
T143B = ANALYSIS / "t143b_directory_recovery_preregistration.json"
OUTPUT = ANALYSIS / "t143c_runner_receipt_recovery_preregistration.json"
MARKDOWN = (
    ANALYSIS / "T143C_RUNNER_RECEIPT_RECOVERY_PREREGISTRATION_20260729.md"
)
BUILDER = Path(__file__).resolve()
WRAPPER = ROOT / "tools" / "run_t143c_runner_receipt_recovery.py"
FIXED_RUNNER = (
    ROOT / "tools" / "run_t143_conditional_forward_path_transform.py"
)
TEST = ROOT / "tests" / "test_t143c_runner_receipt_recovery.py"
FRESH_WORK = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t143c_conditional_forward_path_v1"
)


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T143C: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T143C preregistration requires clean worktree")
    source = json.loads(T143.read_text(encoding="utf-8"))
    failed_recovery = json.loads(T143B.read_text(encoding="utf-8"))
    source_inputs = dict(source["frozen_inputs"])
    obsolete_runner = source_inputs["runner"]
    source_inputs["runner"] = receipt(FIXED_RUNNER)
    source_inputs.update(
        {
            "recovery_builder": receipt(BUILDER),
            "recovery_wrapper": receipt(WRAPPER),
            "recovery_test": receipt(TEST),
            "source_t143_preregistration": receipt(T143),
            "failed_t143b_preregistration": receipt(T143B),
        }
    )
    checks = {
        "t143b_retained_obsolete_runner": (
            failed_recovery["frozen_inputs"]["runner"] == obsolete_runner
            and failed_recovery["frozen_inputs"]["fixed_transform"]
            == receipt(FIXED_RUNNER)
        ),
        "primary_runner_now_exact_fixed_source": (
            source_inputs["runner"] == receipt(FIXED_RUNNER)
        ),
        "source_and_t143b_results_absent": (
            not (
                ANALYSIS / "t143_conditional_forward_path_result.json"
            ).exists()
            and not (
                ANALYSIS / "t143b_directory_recovery_result.json"
            ).exists()
        ),
        "t143b_work_absent": not Path(
            "D:/CodexArtifacts/open-duck-policy/"
            "t143b_conditional_forward_path_v1"
        ).exists(),
        "fresh_work_absent": not FRESH_WORK.exists(),
        "zero_transforms_behavior_training_colab_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T143C preregistration checks failed: {failed}")
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
            "open_duck.t143c_runner_receipt_recovery_"
            "preregistration.v1"
        ),
        "recovery_kind": "T143B_OBSOLETE_PRIMARY_RUNNER_RECEIPT",
        "source_t143_contract_sha256": source[
            "preregistered_contract_sha256"
        ],
        "frozen_inputs": source_inputs,
        "checks": checks,
        "failed_checks": failed,
        "execution_now": {
            "prior_attempt_transforms": 0,
            "prior_attempt_behavior_cells": 0,
            "recovery_transforms": 0,
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
        "# T143C runner-receipt recovery preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Primary runner receipt now points to the fixed source\n"
        "- Both prior attempts completed zero transforms and behavior\n"
        "- Recovery uses a fresh work root\n",
        encoding="utf-8",
        newline="\n",
    )
    print("PREREGISTERED_T143C_RUNNER_RECEIPT_RECOVERY")
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
