#!/usr/bin/env python3
"""Freeze T234B's 16-cell upper-Z behavior matrix."""

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


T234B = ANALYSIS / "t234b_abi_helper_recovery_result.json"
T235 = ANALYSIS / "t235_exact_low_command_nominal_result.json"
BASIS = ANALYSIS / "t165_composed_full_r2_preregistration.json"
OUTPUT = ANALYSIS / "t236_exact_low_command_upper_z_preregistration.json"
MARKDOWN = (
    ANALYSIS / "T236_EXACT_LOW_COMMAND_UPPER_Z_PREREGISTRATION_20260730.md"
)
BUILDER = Path(__file__).resolve()
RUNNER = ROOT / "tools" / "run_t236_exact_low_command_upper_z.py"


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T236: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T236 preregistration requires clean worktree")
    t234b = json.loads(T234B.read_text(encoding="utf-8"))
    t235 = json.loads(T235.read_text(encoding="utf-8"))
    basis = json.loads(BASIS.read_text(encoding="utf-8"))
    policies = [
        {
            "checkpoint_id": f"T234_EXACT_LOW_COMMAND_{row['role'].upper()}",
            "step": int(row["step"]),
            **row["structure"]["transformed"],
        }
        for row in t234b["graphs"]
    ]
    policies.sort(key=lambda row: row["step"])
    condition = next(
        row for row in basis["conditions"] if row["id"] == "TORSO_COM_Z_POS"
    )
    checks = {
        "t235_nominal_green_exact": (
            t235["status"] == "PASS_T235_EXACT_LOW_COMMAND_NOMINAL"
            and t235["condition"]["green_cells"]
            == t235["condition"]["cells"]
            == 16
            and t235["decision"]
            == (
                "EARN_T236_EXACT_LOW_COMMAND_UPPER_Z_MATRIX_"
                "PREREGISTRATION_ONLY"
            )
        ),
        "two_transformed_policies_present": (
            len(policies) == 2
            and [row["step"] for row in policies]
            == [1_003_520, 2_007_040]
            and all(Path(row["path"]).is_file() for row in policies)
        ),
        "basis_is_green_frozen_matrix_contract": (
            basis["status"] == "PREREGISTERED_T165_COMPOSED_FULL_R2"
            and not basis["failed_checks"]
            and basis["commands_x_m_s"] == [0.0, 0.074, 0.077, 0.08]
        ),
        "condition_is_exact_failed_upper_z": (
            condition["condition_index"] == 12
            and condition["override"]
            == {"torso_com_offset_m": [0.0, 0.0, 0.05]}
        ),
        "both_checkpoints_required": True,
        "fresh_cache_required": True,
        "no_retry_training_hosted_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, value in checks.items() if not value)
    if failed:
        raise RuntimeError(f"T236 preregistration checks failed: {failed}")
    copied = {
        name: basis[name]
        for name in (
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
            "open_duck.t236_exact_low_command_upper_z_"
            "preregistration.v1"
        ),
        "status": "PREREGISTERED_T236_EXACT_LOW_COMMAND_UPPER_Z",
        **copied,
        "condition": condition,
        "policies": policies,
        "matrix": {
            "conditions": 1,
            "checkpoints": 2,
            "fits": 2,
            "commands": 4,
            "cells": 16,
            "both_checkpoints_required": True,
            "checkpoint_cherry_pick": False,
            "fresh_cache": True,
        },
        "decision_rule": {
            "pass_decision": (
                "EARN_T237_EXACT_LOW_COMMAND_FULL_R2_RESTART_"
                "PREREGISTRATION_ONLY"
            ),
            "fail_decision": "CLOSE_EXACT_LOW_COMMAND_HEAD_ROUTE",
            "no_retry": True,
            "selection_weight": 0,
        },
        "frozen_inputs": {
            name: receipt(path)
            for name, path in {
                "builder": BUILDER,
                "runner": RUNNER,
                "t234b_recovery": T234B,
                "t235_nominal": T235,
                "t165_matrix_basis": BASIS,
            }.items()
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
            "one_cpu_upper_z_matrix": True,
            "full_r2_restart_preregistration": False,
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
        "# T236 exact low-command upper-Z preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Condition: torso COM z=`+0.05 m` (the T225 blocker)\n"
        "- Matrix: `2 checkpoints x 2 fits x 4 commands = 16`\n"
        "- Fresh cache; both checkpoints mandatory; no retry\n"
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
