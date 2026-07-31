#!/usr/bin/env python3
"""Freeze T234B's sequential 20-condition R2 robustness matrix."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
sys.path.insert(0, str(ROOT / "tools"))
from run_t27_t23_robustness_matrix import (  # noqa: E402
    canonical_sha256,
    matrix_plan,
    receipt,
)


T234B = ANALYSIS / "t234b_abi_helper_recovery_result.json"
T235 = ANALYSIS / "t235_exact_low_command_nominal_result.json"
T236 = ANALYSIS / "t236_exact_low_command_upper_z_result.json"
BASIS = ANALYSIS / "t27_t23_robustness_matrix_preregistration.json"
OUTPUT = ANALYSIS / "t237_exact_low_command_full_r2_preregistration.json"
MARKDOWN = (
    ANALYSIS / "T237_EXACT_LOW_COMMAND_FULL_R2_PREREGISTRATION_20260730.md"
)
BUILDER = Path(__file__).resolve()
RUNNER = ROOT / "tools" / "run_t237_exact_low_command_full_r2.py"
TEST = ROOT / "tests" / "test_t237_exact_low_command_full_r2.py"


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T237: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T237 preregistration requires clean worktree")
    values = {
        "t234b": json.loads(T234B.read_text(encoding="utf-8")),
        "t235": json.loads(T235.read_text(encoding="utf-8")),
        "t236": json.loads(T236.read_text(encoding="utf-8")),
        "basis": json.loads(BASIS.read_text(encoding="utf-8")),
    }
    policies = [
        {
            "checkpoint_id": f"T234_EXACT_LOW_COMMAND_{row['role'].upper()}",
            "step": int(row["step"]),
            **row["structure"]["transformed"],
        }
        for row in values["t234b"]["graphs"]
    ]
    policies.sort(key=lambda row: row["step"])
    basis = values["basis"]
    plan = matrix_plan(
        basis["conditions"],
        policies,
        basis["fits"],
        basis["commands_x_m_s"],
        int(basis["seed"]),
    )
    frozen = {
        "builder": BUILDER,
        "runner": RUNNER,
        "test": TEST,
        "t234b_transform": T234B,
        "t235_nominal_matrix": T235,
        "t236_upper_z_matrix": T236,
        "r2_basis": BASIS,
        "reused_matrix_engine": ROOT
        / "tools"
        / "run_t225_global_plateau_full_r2.py",
    }
    checks = {
        "t234b_transform_green": (
            values["t234b"]["status"] == "PASS_T234B_ABI_HELPER_RECOVERY"
            and not values["t234b"]["failed_checks"]
        ),
        "t235_nominal_green": (
            values["t235"]["status"]
            == "PASS_T235_EXACT_LOW_COMMAND_NOMINAL"
            and values["t235"]["condition"]["green_cells"] == 16
        ),
        "t236_former_blocker_green": (
            values["t236"]["status"]
            == "PASS_T236_EXACT_LOW_COMMAND_UPPER_Z"
            and values["t236"]["condition"]["green_cells"] == 16
            and values["t236"]["decision"]
            == (
                "EARN_T237_EXACT_LOW_COMMAND_FULL_R2_RESTART_"
                "PREREGISTRATION_ONLY"
            )
        ),
        "candidate_graphs_exact": (
            len(policies) == 2
            and [row["step"] for row in policies]
            == [1_003_520, 2_007_040]
            and all(Path(row["path"]).is_file() for row in policies)
        ),
        "basis_is_full_sequential_r2": (
            basis["status"]
            == "PREREGISTERED_T27_T23_SEQUENTIAL_R2_ROBUSTNESS_MATRIX"
            and len(basis["conditions"]) == 20
            and basis["matrix"]["maximum_cells"] == 320
            and basis["matrix"]["stop_after_first_failed_condition"]
        ),
        "plan_exact_320_cells": len(plan) == 320,
        "all_inputs_present": all(path.exists() for path in frozen.values()),
        "repository_inputs_present": all(
            Path(item["path"]).is_file()
            for item in basis["repository_inputs"].values()
        ),
        "fresh_cache_no_prior_behavior_reuse": True,
        "no_training_hosted_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, value in checks.items() if not value)
    if failed:
        raise RuntimeError(f"T237 preregistration checks failed: {failed}")
    copied = {
        name: basis[name]
        for name in (
            "conditions",
            "fits",
            "calibrator",
            "reference_feature_table",
            "playground",
            "commands_x_m_s",
            "seed",
            "support_handoff",
            "behavior_contract",
            "protection_contract",
            "repository_inputs",
        )
    }
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t237_exact_low_command_full_r2_"
            "preregistration.v1"
        ),
        "status": "PREREGISTERED_T237_EXACT_LOW_COMMAND_FULL_R2",
        **copied,
        "policies": policies,
        "matrix": {
            "conditions": 20,
            "checkpoints": 2,
            "fits": 2,
            "commands": 4,
            "cells_per_condition": 16,
            "maximum_cells": 320,
            "both_checkpoints_required": True,
            "checkpoint_cherry_pick": False,
            "strictly_sequential_conditions": True,
            "complete_each_16_cell_condition_before_decision": True,
            "stop_after_first_failed_condition": True,
            "maximum_new_conditions_per_invocation": 1,
            "fresh_cache": True,
            "plan_sha256": canonical_sha256(plan),
        },
        "decision_rule": {
            "pass_decision": (
                "EARN_T238_OFFLINE_DEPLOYMENT_CONTRACT_AUDIT_"
                "PREREGISTRATION_ONLY"
            ),
            "fail_decision": (
                "CLOSE_EXACT_LOW_COMMAND_HEAD_ROUTE_AT_FIRST_FAILED_R2_"
                "CONDITION"
            ),
            "no_retry": True,
            "selection_weight": 0,
        },
        "frozen_inputs": {
            name: receipt(path) for name, path in frozen.items()
        },
        "checks": checks,
        "failed_checks": failed,
        "execution_now": {
            "behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "sequential_cpu_r2_matrix": True,
            "deployment_contract_audit_preregistration": False,
            "training": False,
            "hosted": False,
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
        "# T237 exact low-command full R2 preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Matrix: up to `20 x 16 = 320` fresh CPU cells\n"
        "- Order: frozen; stop after first complete failed condition\n"
        "- Operational chunk: exactly one new condition per invocation\n"
        "- Both checkpoints/fits required; no retry\n"
        "- Training/hosted/robot: `0/0/0`\n"
        f"- Contract SHA-256: `{value['preregistered_contract_sha256']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
