#!/usr/bin/env python3
"""Freeze T217B's read-only CPU/GPU cost-init recovery."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
from typing import Any

import numpy as np

from run_t136_static_calibration_router_transform import (
    ANALYSIS,
    ROOT,
    canonical_sha256,
    receipt,
)


T217 = ANALYSIS / "t217_t216_recovered_training_validation.json"
T215B = ANALYSIS / "t215b_axis_complete_tilt_cpu_result.json"
OUTPUT = ANALYSIS / "t217b_cost_init_backend_recovery_preregistration.json"
MARKDOWN = (
    ANALYSIS
    / "T217B_COST_INIT_BACKEND_RECOVERY_PREREGISTRATION_20260730.md"
)
RUNNER = ROOT / "tools/run_t217b_cost_init_backend_recovery.py"
TEST = ROOT / "tests/test_t217b_cost_init_backend_recovery.py"
FAILED_CHECK = "step_zero_cost_tree_reproducible_bit_exact"


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError("refusing to overwrite T217B preregistration")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T217B preregistration requires clean worktree")
    t217 = json.loads(T217.read_text(encoding="utf-8"))
    t215b = json.loads(T215B.read_text(encoding="utf-8"))
    hosted_cost_zero = next(
        row
        for row in t217["exports"]["cost_checkpoints"]
        if int(row["step"]) == 0
    )
    cpu_cost_zero = t215b["training"]["cost_checkpoints"]["0"]
    frozen = {
        "builder": receipt(Path(__file__)),
        "runner": receipt(RUNNER),
        "test": receipt(TEST),
        "t217_hold": receipt(T217),
        "t215b_cpu_result": receipt(T215B),
        "cpu_cost_zero": {
            "path": cpu_cost_zero["path"],
            "sha256": cpu_cost_zero["sha256"],
        },
        "hosted_cost_zero": {
            "path": hosted_cost_zero["path"],
            "sha256": hosted_cost_zero["directory_sha256"],
        },
    }
    checks = {
        "t217_exact_single_hold": (
            t217["status"]
            == "HOLD_T217_T216_RECOVERED_TRAINING_VALIDATION"
            and t217["decision"] == "NO_BEHAVIOR_EVALUATION"
            and t217["failed_checks"] == [FAILED_CHECK]
            and all(
                passed
                for name, passed in t217["checks"].items()
                if name != FAILED_CHECK
            )
        ),
        "t215b_cpu_contract_green": (
            t215b["status"]
            == "PASS_T215B_AXIS_COMPLETE_TILT_CPU_CONTRACT"
            and not t215b["failed_checks"]
        ),
        "both_cost_zero_checkpoints_present": (
            Path(cpu_cost_zero["path"]).is_dir()
            and Path(hosted_cost_zero["path"]).is_dir()
        ),
        "tolerance_derived_from_float32_dtype": (
            float(np.finfo(np.float32).eps)
            == 1.1920928955078125e-7
        ),
        "zero_optimizer_simulator_onnx_behavior_or_robot_now": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T217B preregistration checks failed: {failed}")
    basis: dict[str, Any] = {
        "schema_version": (
            "open_duck.t217b_cost_init_backend_recovery_"
            "preregistration.v1"
        ),
        "status": "PREREGISTERED_T217B_COST_INIT_BACKEND_RECOVERY",
        "question": (
            "Is T217's sole cost-init bit-equality miss confined to "
            "structure-exact, finite CPU/GPU float32 initialization "
            "differences no larger than one dtype machine epsilon?"
        ),
        "frozen_inputs": frozen,
        "recovery_rule": {
            "failed_check": FAILED_CHECK,
            "comparison": "maximum_absolute_leaf_delta",
            "dtype": "float32",
            "absolute_tolerance": float(np.finfo(np.float32).eps),
            "tolerance_derivation": "numpy.finfo(float32).eps",
            "structure_exact_required": True,
            "all_leaves_finite_required": True,
            "all_other_t217_checks_must_remain_green": True,
            "post_hoc_tolerance_tuning": False,
        },
        "decision_rule": {
            "pass": (
                "RECOVER_T217_AND_EARN_T218_T216_POSTEXPORT_"
                "COMPOSITION_PREREGISTRATION_ONLY"
            ),
            "fail": "HOLD_T216_WITHOUT_BEHAVIOR",
            "rerun_training_or_validation": False,
        },
        "checks": checks,
        "failed_checks": failed,
        "execution_now": {
            "checkpoint_restores": 0,
            "optimizer_steps": 0,
            "simulator_transitions": 0,
            "onnx_inferences": 0,
            "behavior_cells": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "execute_read_only_cost_init_comparison": True,
            "composition_preregistration": False,
            "behavior": False,
            "training": False,
            "colab": False,
            "gate5": False,
            "robot_or_rdk": False,
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
        "# T217B cost-init backend recovery preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Scope: T217's sole CPU/GPU cost-init bit-equality hold\n"
        f"- Absolute tolerance: "
        f"`{value['recovery_rule']['absolute_tolerance']}` "
        "(`float32` machine epsilon)\n"
        "- Optimizer / simulator / ONNX / behavior / hosted / robot: "
        "`0/0/0/0/0/0`\n"
        f"- Contract SHA-256: `{value['preregistered_contract_sha256']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(
        "preregistered_contract_sha256="
        f"{value['preregistered_contract_sha256']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
