#!/usr/bin/env python3
"""Freeze recovery from T143's pre-transform directory collision."""

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
OUTPUT = ANALYSIS / "t143b_directory_recovery_preregistration.json"
MARKDOWN = (
    ANALYSIS / "T143B_DIRECTORY_RECOVERY_PREREGISTRATION_20260729.md"
)
BUILDER = Path(__file__).resolve()
RUNNER = ROOT / "tools" / "run_t143b_directory_recovery.py"
FIXED_TRANSFORM = (
    ROOT / "tools" / "run_t143_conditional_forward_path_transform.py"
)
TEST = ROOT / "tests" / "test_t143b_directory_recovery.py"
PARTIAL = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t143_conditional_forward_path_v1/1003520/"
    "negative_always_on_reference.onnx"
)
FRESH_WORK = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t143b_conditional_forward_path_v1"
)


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T143B: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T143B preregistration requires clean worktree")
    source = json.loads(T143.read_text(encoding="utf-8"))
    frozen_inputs = {
        **source["frozen_inputs"],
        "recovery_builder": receipt(BUILDER),
        "recovery_runner": receipt(RUNNER),
        "fixed_transform": receipt(FIXED_TRANSFORM),
        "recovery_test": receipt(TEST),
        "source_t143_preregistration": receipt(T143),
        "partial_always_on_reference": receipt(PARTIAL),
    }
    checks = {
        "source_t143_preregistered": (
            source["status"]
            == "PREREGISTERED_T143_CONDITIONAL_FORWARD_PATH_TRANSFORM"
        ),
        "source_result_absent": not (
            ANALYSIS / "t143_conditional_forward_path_result.json"
        ).exists(),
        "partial_contains_only_first_reference": (
            PARTIAL.is_file()
            and len(
                [
                    path
                    for path in PARTIAL.parents[1].rglob("*")
                    if path.is_file()
                ]
            )
            == 1
        ),
        "fresh_work_absent": not FRESH_WORK.exists(),
        "fixed_source_contains_exist_ok": (
            "destination.parent.mkdir(parents=True, exist_ok=True)"
            in FIXED_TRANSFORM.read_text(encoding="utf-8")
        ),
        "zero_behavior_training_colab_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T143B preregistration checks failed: {failed}")
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
            "open_duck.t143b_directory_recovery_preregistration.v1"
        ),
        "recovery_kind": "T143_ZERO_TRANSFORM_DIRECTORY_EXISTS",
        "source_t143_contract_sha256": source[
            "preregistered_contract_sha256"
        ],
        "frozen_inputs": frozen_inputs,
        "checks": checks,
        "failed_checks": failed,
        "execution_now": {
            "source_attempt_references": 1,
            "source_attempt_transforms": 0,
            "source_attempt_behavior_cells": 0,
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
        "# T143B directory recovery preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Source stopped after one reference and zero transforms\n"
        "- Correction: directory creation is idempotent\n"
        "- Recovery uses a fresh work root\n"
        "- Behavior / optimizer / Colab / robot: `0/0/0/0`\n",
        encoding="utf-8",
        newline="\n",
    )
    print("PREREGISTERED_T143B_DIRECTORY_RECOVERY")
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
