#!/usr/bin/env python3
"""Preregister T247's final three-condition R2 preservation screen."""

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


T237_PREREG = ANALYSIS / "t237_exact_low_command_full_r2_preregistration.json"
T237_RESULT = ANALYSIS / "t237_exact_low_command_full_r2_result.json"
T241 = ANALYSIS / "t241_bounded_positive_router_transform_result.json"
T243B = ANALYSIS / "t243b_abi_helper_recovery_result.json"
T243C = ANALYSIS / "t243c_random_sensitivity_recovery_result.json"
T247 = ANALYSIS / "t247_home_negative_half_adapter_route_result.json"
T247B = ANALYSIS / "t247b_reporting_recovery_result.json"
T248 = ANALYSIS / "t248_home_negative_half_adapter_matrix_result.json"
OUTPUT = ANALYSIS / "t249_remaining_r2_preregistration.json"
MARKDOWN = ANALYSIS / "T249_REMAINING_R2_PREREGISTRATION_20260731.md"
RUNNER = ROOT / "tools/run_t249_remaining_r2.py"
TEST = ROOT / "tests/test_t249_remaining_r2.py"


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError("refusing to overwrite T249 preregistration")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T249 preregistration requires clean worktree")
    values = {
        "t237_prereg": json.loads(T237_PREREG.read_text(encoding="utf-8")),
        "t237_result": json.loads(T237_RESULT.read_text(encoding="utf-8")),
        "t241": json.loads(T241.read_text(encoding="utf-8")),
        "t243b": json.loads(T243B.read_text(encoding="utf-8")),
        "t243c": json.loads(T243C.read_text(encoding="utf-8")),
        "t247": json.loads(T247.read_text(encoding="utf-8")),
        "t247b": json.loads(T247B.read_text(encoding="utf-8")),
        "t248": json.loads(T248.read_text(encoding="utf-8")),
    }
    basis = values["t237_prereg"]
    policies = [
        {
            "checkpoint_id": (
                f"T247_HOME_NEGATIVE_HALF_ADAPTER_{row['role'].upper()}"
            ),
            "step": int(row["step"]),
            **row["structure"]["transformed"],
        }
        for row in values["t247"]["graphs"]
    ]
    policies.sort(key=lambda row: row["step"])
    reused_conditions = values["t237_result"]["conditions"][:16]
    remaining_conditions = basis["conditions"][17:]
    t241_non_home_exact = all(
        row["random_inference"]["all_non_home_negative_exact"]
        for row in values["t241"]["graphs"]
    )
    t243_non_target_exact = all(
        row["inference"]["all_non_targets_exact_source"]
        for row in values["t243b"]["graphs"]
    )
    t247_non_tail_exact = all(
        row["inference"]["all_non_tail_exact_source"]
        for row in values["t247"]["graphs"]
    )
    checks = {
        "condition_17_green_16_of_16": (
            values["t248"]["status"]
            == "PASS_T248_HOME_NEGATIVE_HALF_ADAPTER_MATRIX"
            and values["t248"]["condition"]["condition_green"]
            and values["t248"]["condition"]["green_cells"] == 16
            and values["t248"]["decision"]
            == (
                "EARN_T249_HOME_NEGATIVE_REPAIR_FULL_R2_"
                "PRESERVATION_PREREGISTRATION_ONLY"
            )
        ),
        "conditions_1_through_16_green": (
            len(reused_conditions) == 16
            and [row["condition_index"] for row in reused_conditions]
            == list(range(1, 17))
            and all(
                row["condition_green"] and row["green_cells"] == 16
                for row in reused_conditions
            )
        ),
        "t241_non_home_routes_exact_t237_source": t241_non_home_exact,
        "t243_non_target_routes_exact_t241_source": t243_non_target_exact,
        "t243_reporting_recovery_green": (
            values["t243c"]["status"]
            == "PASS_T243C_RANDOM_SENSITIVITY_REPORTING_RECOVERY"
            and all(values["t243c"]["checks"].values())
        ),
        "t247_non_tail_routes_exact_t243_source": t247_non_tail_exact,
        "t247_reporting_recovery_green": (
            values["t247b"]["status"] == "PASS_T247B_REPORTING_RECOVERY"
            and all(values["t247b"]["checks"].values())
        ),
        "remaining_conditions_exact_and_ordered": (
            [row["condition_index"] for row in remaining_conditions]
            == [18, 19, 20]
            and [row["id"] for row in remaining_conditions]
            == ["HOME_JOINT_OFFSET_POS", "KP_LO", "KP_HI"]
        ),
        "two_candidate_graphs_present": (
            len(policies) == 2
            and [row["step"] for row in policies]
            == [1_003_520, 2_007_040]
            and all(Path(row["path"]).is_file() for row in policies)
        ),
        "one_fresh_condition_per_invocation_no_retry": True,
        "zero_behavior_optimizer_hosted_or_robot_now": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T249 preregistration checks failed: {failed}")
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
    frozen = {
        "builder": Path(__file__),
        "runner": RUNNER,
        "test": TEST,
        "t237_preregistration": T237_PREREG,
        "t237_result": T237_RESULT,
        "t241_transform": T241,
        "t243b_transform": T243B,
        "t243c_recovery": T243C,
        "t247_transform": T247,
        "t247b_recovery": T247B,
        "t248_condition_17": T248,
    }
    value_basis: dict[str, Any] = {
        "schema_version": "open_duck.t249_remaining_r2_preregistration.v1",
        "status": "PREREGISTERED_T249_REMAINING_R2",
        "question": (
            "After inheriting exact green evidence for conditions 1-17, "
            "does the T247 candidate pass conditions 18-20 sequentially?"
        ),
        **copied,
        "policies": policies,
        "remaining_conditions": remaining_conditions,
        "reused_evidence": {
            "conditions_1_through_16": receipt(T237_RESULT),
            "condition_17": receipt(T248),
            "reused_conditions": 17,
            "reused_cells": 272,
            "rerun": False,
        },
        "matrix": {
            "conditions_total": 20,
            "conditions_reused": 17,
            "conditions_new_maximum": 3,
            "cells_total": 320,
            "cells_reused": 272,
            "cells_new_maximum": 48,
            "cells_per_condition": 16,
            "both_checkpoints_required": True,
            "both_fits_required": True,
            "complete_condition_before_decision": True,
            "strict_condition_order": [18, 19, 20],
            "maximum_new_conditions_per_invocation": 1,
            "stop_after_first_failed_condition": True,
            "no_retry": True,
        },
        "decision_rule": {
            "pass": (
                "EARN_T250_OFFLINE_DEPLOYMENT_CONTRACT_AUDIT_"
                "PREREGISTRATION_ONLY"
            ),
            "fail": "CLOSE_HOME_NEGATIVE_HALF_ADAPTER_ROUTE_AT_R2_FAILURE",
            "selection_weight": 0,
            "no_retry": True,
        },
        "frozen_inputs": {
            name: receipt(path) for name, path in frozen.items()
        },
        "checks": checks,
        "failed_checks": failed,
        "execution_now": {
            "behavior_cells_reused": 0,
            "new_behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "reuse_conditions_1_through_17": True,
            "run_conditions_18_through_20_cpu_only": True,
            "offline_deployment_contract_audit_preregistration": False,
            "training": False,
            "hosted": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    value = {
        **value_basis,
        "preregistered_contract_sha256": canonical_sha256(value_basis),
    }
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T249 remaining R2 preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Conditions already green: `1-17` (`272` cells)\n"
        "- Remaining: `18 HOME_JOINT_OFFSET_POS`, `19 KP_LO`, `20 KP_HI`\n"
        "- Execute: one complete 16-cell condition per invocation\n"
        "- Stop after first failed condition; no retry\n"
        "- Optimizer/hosted/robot: `0/0/0`\n"
        f"- Contract SHA-256: `{value['preregistered_contract_sha256']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
