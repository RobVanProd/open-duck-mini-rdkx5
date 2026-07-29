#!/usr/bin/env python3
"""Freeze the read-only recovery of T136's x=0 coordinate assertion."""

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


T136 = ANALYSIS / "t136_static_calibration_router_result.json"
T135B = (
    ANALYSIS
    / "t135b_interrupted_calibration_context_router_recovery_result.json"
)
OUTPUT = ANALYSIS / "t136b_x0_coordinate_recovery_preregistration.json"
MARKDOWN = (
    ANALYSIS / "T136B_X0_COORDINATE_RECOVERY_PREREGISTRATION_20260729.md"
)
BUILDER = Path(__file__).resolve()
RUNNER = ROOT / "tools" / "run_t136b_x0_coordinate_recovery.py"
TEST = ROOT / "tests" / "test_t136b_x0_coordinate_recovery.py"
SOURCE_ROOT = Path(
    "D:/CodexArtifacts/open-duck-policy/t131_t129_deployments_v1"
)
TRANSFORMED_ROOT = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t136_t129_static_calibration_router_v1"
)
STEPS = ("0", "1003520", "2007040")


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T136B: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T136B preregistration requires clean worktree")
    t136 = json.loads(T136.read_text(encoding="utf-8"))
    source = {
        step: SOURCE_ROOT / step / "deployment" / "action_margin.onnx"
        for step in STEPS
    }
    transformed = {
        step: TRANSFORMED_ROOT / step / "static_calibration_router.onnx"
        for step in STEPS
    }
    frozen_inputs = {
        "builder": BUILDER,
        "runner": RUNNER,
        "test": TEST,
        "t136_result": T136,
        "t135b_result": T135B,
    }
    other_checks = {
        name: passed
        for name, passed in t136["checks"].items()
        if name != "all_x0_paths_exact_zero"
    }
    checks = {
        "t136_single_assertion_hold": (
            t136["status"] == "HOLD_T136_STATIC_CALIBRATION_ROUTER_TRANSFORM"
            and t136["failed_checks"] == ["all_x0_paths_exact_zero"]
            and all(other_checks.values())
        ),
        "source_and_transformed_graphs_present": all(
            path.is_file() for path in (*source.values(), *transformed.values())
        ),
        "frozen_inputs_present": all(
            path.is_file() for path in frozen_inputs.values()
        ),
        "recovery_is_read_only": True,
        "no_behavior_training_colab_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T136B preregistration checks failed: {failed}")
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t136b_x0_coordinate_recovery_"
            "preregistration.v1"
        ),
        "status": "PREREGISTERED_T136B_X0_COORDINATE_RECOVERY",
        "question": (
            "Does every T136 graph preserve every frozen T131 output "
            "bit-exactly at x=0 in the external support-action coordinate "
            "domain for all four calibration contexts?"
        ),
        "source_graphs": {
            step: receipt(path) for step, path in source.items()
        },
        "transformed_graphs": {
            step: receipt(path) for step, path in transformed.items()
        },
        "frozen_inputs": {
            name: receipt(path) for name, path in frozen_inputs.items()
        },
        "checks": checks,
        "failed_checks": failed,
        "decision_rule": {
            "pass_decision": (
                "RECOVER_T136_AND_EARN_T137_STATIC_ROUTER_NOMINAL_"
                "MATRIX_PREREGISTRATION_ONLY"
            ),
            "fail_decision": "CLOSE_STATIC_CALIBRATION_ROUTER_TRANSFORM",
        },
        "execution_now": {
            "x0_cpu_samples": 0,
            "formal_behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "one_read_only_cpu_recovery": True,
            "nominal_matrix_preregistration": False,
            "behavior_evaluation": False,
            "negative_matrix": False,
            "training": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    value["preregistered_contract_sha256"] = canonical_sha256(value)
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T136B x=0 coordinate recovery preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Compare all three T136 graphs to T131 at x=0 bit-for-bit\n"
        "- Correct coordinate: external support action, not policy zero\n"
        "- Behavior / optimizer / Colab / robot: `0/0/0/0`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
