#!/usr/bin/env python3
"""Freeze T149B's sequential 20-condition R2 revalidation."""

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


T150 = ANALYSIS / "t150_negative_command_plateau_endpoint_result.json"
T149B = ANALYSIS / "t149b_negative_context_command_plateau_result.json"
BASIS = ANALYSIS / "t27_t23_robustness_matrix_preregistration.json"
OUTPUT = ANALYSIS / "t151_command_plateau_full_r2_preregistration.json"
MARKDOWN = (
    ANALYSIS / "T151_COMMAND_PLATEAU_FULL_R2_PREREGISTRATION_20260729.md"
)
BUILDER = Path(__file__).resolve()
RUNNER = ROOT / "tools/run_t151_command_plateau_full_r2.py"
TEST = ROOT / "tests/test_t151_command_plateau_full_r2.py"


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T151: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T151 preregistration requires clean worktree")
    t150 = json.loads(T150.read_text(encoding="utf-8"))
    t149 = json.loads(T149B.read_text(encoding="utf-8"))
    basis = json.loads(BASIS.read_text(encoding="utf-8"))
    policies = [
        {
            "checkpoint_id": f"T149B_NEGATIVE_PLATEAU_{label}",
            "step": int(step),
            **t149["transforms"][step]["transformed"],
        }
        for label, step in (("HALF", "1003520"), ("FINAL", "2007040"))
    ]
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
        "t149b_transform": T149B,
        "t150_negative_endpoint": T150,
        "r2_basis": BASIS,
    }
    checks = {
        "t150_negative_endpoint_green": (
            t150["status"]
            == "PASS_T150_NEGATIVE_COMMAND_PLATEAU_ENDPOINT"
            and t150["condition"]["green_cells"] == 16
            and t150["decision"]
            == "EARN_T151_COMMAND_PLATEAU_FULL_R2_PREREGISTRATION_ONLY"
        ),
        "t149b_graphs_exact": all(
            {key: policy[key] for key in ("path", "bytes", "sha256")}
            == t149["transforms"][str(policy["step"])]["transformed"]
            for policy in policies
        ),
        "basis_is_full_sequential_r2": (
            basis["status"]
            == "PREREGISTERED_T27_T23_SEQUENTIAL_R2_ROBUSTNESS_MATRIX"
            and len(basis["conditions"]) == 20
            and basis["matrix"]["maximum_cells"] == 320
            and basis["matrix"]["stop_after_first_failed_condition"]
        ),
        "plan_exact_320_cells": len(plan) == 320,
        "all_inputs_present": all(
            path.exists() for path in frozen.values()
        ),
        "repository_inputs_present": all(
            Path(item["path"]).is_file()
            for item in basis["repository_inputs"].values()
        ),
        "no_training_colab_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T151 preregistration checks failed: {failed}")
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
            "open_duck.t151_command_plateau_full_r2_"
            "preregistration.v1"
        ),
        "status": "PREREGISTERED_T151_COMMAND_PLATEAU_FULL_R2",
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
            "plan_sha256": canonical_sha256(plan),
        },
        "decision_rule": {
            "pass_decision": (
                "EARN_T152_OFFLINE_DEPLOYMENT_CONTRACT_AUDIT_"
                "PREREGISTRATION_ONLY"
            ),
            "fail_decision": (
                "CLOSE_COMMAND_PLATEAU_AT_FIRST_FAILED_R2_CONDITION"
            ),
            "no_retry": True,
            "training_selection_weight": 0,
        },
        "frozen_inputs": {name: receipt(path) for name, path in frozen.items()},
        "checks": checks,
        "failed_checks": failed,
        "authority": {
            "sequential_cpu_r2_matrix": True,
            "deployment_contract_audit_preregistration": False,
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
        "# T151 command-plateau full R2 preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Matrix: up to `20 × 16 = 320` CPU cells\n"
        "- Order: frozen; stop after first complete failed condition\n"
        "- Operational chunk: exactly one new condition per invocation\n"
        "- Both checkpoints and fits required; no retry\n"
        "- Training / Colab / robot: `0/0/0`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
