#!/usr/bin/env python3
"""Freeze nominal evidence reuse for T143C's exact T100C branch."""

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


T143C = ANALYSIS / "t143c_runner_receipt_recovery_result.json"
T102 = ANALYSIS / "t102_t100c_nominal_matrix_result.json"
T102_PREREG = ANALYSIS / "t102_t100c_nominal_matrix_preregistration.json"
OUTPUT = ANALYSIS / "t144_nominal_identity_reuse_preregistration.json"
MARKDOWN = ANALYSIS / "T144_NOMINAL_IDENTITY_REUSE_PREREGISTRATION_20260729.md"
BUILDER = Path(__file__).resolve()
RUNNER = ROOT / "tools" / "run_t144_nominal_identity_reuse.py"
TEST = ROOT / "tests" / "test_t144_nominal_identity_reuse.py"


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T144: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T144 preregistration requires clean worktree")
    t143c = json.loads(T143C.read_text(encoding="utf-8"))
    t102 = json.loads(T102.read_text(encoding="utf-8"))
    frozen = {
        "builder": BUILDER,
        "runner": RUNNER,
        "test": TEST,
        "t143c_result": T143C,
        "t102_result": T102,
        "t102_prereg": T102_PREREG,
    }
    checks = {
        "t143c_transform_green": (
            t143c["status"] == "PASS_T143C_CONDITIONAL_FORWARD_PATH_TRANSFORM"
            and t143c["failed_checks"] == []
            and t143c["decision"]
            == "EARN_T144_CONDITIONAL_PATH_NOMINAL_IDENTITY_REUSE_"
            "PREREGISTRATION_ONLY"
        ),
        "t102_nominal_green": (
            t102["status"] == "PASS_T102_T100C_NOMINAL_MATRIX"
            and t102["condition"]["green_cells"] == 16
        ),
        "frozen_inputs_present": all(path.is_file() for path in frozen.values()),
        "no_new_behavior_training_colab_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T144 preregistration checks failed: {failed}")
    value: dict[str, Any] = {
        "schema_version": "open_duck.t144_nominal_identity_reuse_preregistration.v1",
        "status": "PREREGISTERED_T144_NOMINAL_IDENTITY_REUSE",
        "question": (
            "Can the frozen T102 16/16 nominal matrix be inherited because "
            "T143C selects exact T100C outputs for both nominal contexts?"
        ),
        "frozen_inputs": {name: receipt(path) for name, path in frozen.items()},
        "checks": checks,
        "failed_checks": failed,
        "decision_rule": {
            "pass_decision": (
                "EARN_T145_CONDITIONAL_PATH_NEGATIVE_ENDPOINT_"
                "PREREGISTRATION_ONLY"
            ),
            "fail_decision": "REQUIRE_FRESH_NOMINAL_MATRIX",
        },
        "execution_now": {
            "inherited_behavior_cells": 0,
            "new_behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "one_cpu_identity_reuse_audit": True,
            "negative_endpoint_preregistration": False,
            "training": False,
            "colab": False,
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
        "# T144 nominal identity reuse preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- T143C nominal outputs must be exact T100C\n"
        "- Source T102 matrix: `16/16 green`\n"
        "- New behavior / optimizer / Colab / robot: `0/0/0/0`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
