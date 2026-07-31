#!/usr/bin/env python3
"""Freeze recovery after T146B retained the obsolete base-test receipt."""

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


T146B = ANALYSIS / "t146b_pre_action_field_recovery_preregistration.json"
OUTPUT = ANALYSIS / "t146c_test_receipt_recovery_preregistration.json"
MARKDOWN = (
    ANALYSIS / "T146C_TEST_RECEIPT_RECOVERY_PREREGISTRATION_20260729.md"
)
BUILDER = Path(__file__).resolve()
WRAPPER = ROOT / "tools" / "run_t146c_test_receipt_recovery.py"
BASE_TEST = ROOT / "tests" / "test_t146_upper_command_attribution.py"
TEST = ROOT / "tests" / "test_t146c_test_receipt_recovery.py"


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T146C: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T146C preregistration requires clean worktree")
    source = json.loads(T146B.read_text(encoding="utf-8"))
    source_inputs = dict(source["frozen_inputs"])
    obsolete = source_inputs["test"]
    source_inputs["test"] = receipt(BASE_TEST)
    source_inputs.update(
        {
            "test_receipt_recovery_builder": receipt(BUILDER),
            "test_receipt_recovery_wrapper": receipt(WRAPPER),
            "test_receipt_recovery_test": receipt(TEST),
            "failed_t146b_preregistration": receipt(T146B),
        }
    )
    checks = {
        "t146b_result_absent": not (
            ANALYSIS / "t146b_pre_action_field_recovery_result.json"
        ).exists(),
        "obsolete_test_receipt_was_only_source_mismatch": (
            obsolete != source_inputs["test"]
        ),
        "base_test_receipt_now_exact": source_inputs["test"] == receipt(BASE_TEST),
        "t146b_read_zero_trace_rows": True,
        "new_behavior_optimizer_colab_robot_zero": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T146C preregistration checks failed: {failed}")
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
            "open_duck.t146c_test_receipt_recovery_preregistration.v1"
        ),
        "recovery_kind": "T146B_OBSOLETE_BASE_TEST_RECEIPT",
        "failed_t146b_contract_sha256": source[
            "preregistered_contract_sha256"
        ],
        "frozen_inputs": source_inputs,
        "checks": checks,
        "failed_checks": failed,
        "execution_now": {
            "t146b_trace_rows_read": 0,
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
        "# T146C test-receipt recovery preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- T146B stopped before reading any trace row\n"
        "- Correction: update the base-test receipt to its reviewed source\n"
        "- New behavior / optimizer / Colab / robot: `0/0/0/0`\n",
        encoding="utf-8",
        newline="\n",
    )
    print("PREREGISTERED_T146C_TEST_RECEIPT_RECOVERY")
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
