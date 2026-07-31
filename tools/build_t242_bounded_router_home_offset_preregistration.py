#!/usr/bin/env python3
"""Preregister T241's targeted negative-home-offset behavior matrix."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from run_t136_static_calibration_router_transform import (
    ANALYSIS,
    ROOT,
    canonical_sha256,
    receipt,
)


T237_PREREG = (
    ANALYSIS / "t237_exact_low_command_full_r2_preregistration.json"
)
T241 = ANALYSIS / "t241_bounded_positive_router_transform_result.json"
T241B = ANALYSIS / "t241b_random_sensitivity_recovery_result.json"
OUTPUT = (
    ANALYSIS / "t242_bounded_router_home_offset_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "T242_BOUNDED_ROUTER_HOME_OFFSET_PREREGISTRATION_20260731.md"
)
BUILDER = Path(__file__).resolve()
RUNNER = ROOT / "tools" / "run_t242_bounded_router_home_offset.py"
TEST = ROOT / "tests" / "test_t242_bounded_router_home_offset.py"


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T242: {path}")
    basis = json.loads(T237_PREREG.read_text(encoding="utf-8"))
    t241 = json.loads(T241.read_text(encoding="utf-8"))
    t241b = json.loads(T241B.read_text(encoding="utf-8"))
    condition = next(
        row
        for row in basis["conditions"]
        if row["id"] == "HOME_JOINT_OFFSET_NEG"
    )
    policies = [
        {
            "checkpoint_id": f"T241_BOUNDED_ROUTER_{row['role'].upper()}",
            "step": int(row["step"]),
            **row["structure"]["transformed"],
        }
        for row in t241["graphs"]
    ]
    policies.sort(key=lambda row: row["step"])
    checks = {
        "t241b_earns_targeted_matrix_only": (
            t241b["status"]
            == "PASS_T241B_RANDOM_SENSITIVITY_REPORTING_RECOVERY"
            and t241b["decision"]
            == "EARN_T242_BOUNDED_ROUTER_HOME_OFFSET_MATRIX_PREREGISTRATION_ONLY"
            and all(t241b["checks"].values())
        ),
        "two_transformed_policies_present": (
            len(policies) == 2
            and [row["step"] for row in policies]
            == [1_003_520, 2_007_040]
            and all(Path(row["path"]).is_file() for row in policies)
        ),
        "condition_is_exact_t237_blocker": (
            condition["condition_index"] == 17
            and condition["override"]
            == {"joint_qpos0_offset_rad": -0.03}
        ),
        "matrix_contract_unchanged": (
            basis["commands_x_m_s"] == [0.0, 0.074, 0.077, 0.08]
            and basis["support_handoff"]["unscored_calibration_ticks"] == 250
            and basis["support_handoff"]["unscored_home_return_ticks"] == 0
            and basis["support_handoff"][
                "preserve_final_support_action_as_previous_action"
            ]
            is True
            and basis["support_handoff"][
                "preserve_applied_target_observer_state"
            ]
            is True
        ),
        "both_checkpoints_fresh_cache_no_retry": True,
        "no_training_hosted_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T242 preregistration checks failed: {failed}")
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
    value_basis: dict[str, Any] = {
        "schema_version": (
            "open_duck.t242_bounded_router_home_offset_"
            "preregistration.v1"
        ),
        "status": "PREREGISTERED_T242_BOUNDED_ROUTER_HOME_OFFSET",
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
        "readback_correction": {
            "scope": "joint_qpos0_offset_rad only",
            "legacy_failure": (
                "expected scalar -0.03 compared strictly against evaluator "
                "14-vector [-0.03]*14"
            ),
            "correct_check": (
                "key exact; reported value/offset are fourteen -0.03 values; "
                "before/after are length fourteen; each delta is -0.03 "
                "within float64 1e-12"
            ),
            "selection_weight": 0,
            "behavior_gates_unchanged": True,
        },
        "decision_rule": {
            "pass_decision": (
                "EARN_T243_BOUNDED_ROUTER_PRESERVATION_"
                "PREREGISTRATION_ONLY"
            ),
            "fail_decision": "CLOSE_BOUNDED_POSITIVE_ROUTER",
            "no_retry": True,
            "selection_weight": 0,
        },
        "frozen_inputs": {
            "builder": receipt(BUILDER),
            "runner": receipt(RUNNER),
            "test": receipt(TEST),
            "t237_preregistration": receipt(T237_PREREG),
            "t241_result": receipt(T241),
            "t241b_recovery": receipt(T241B),
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
            "one_cpu_home_offset_matrix": True,
            "preservation_preregistration": False,
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
        "# T242 bounded-router home-offset preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Condition: uniform joint qpos0 offset `-0.03 rad`\n"
        "- Matrix: `2 checkpoints x 2 fits x 4 commands = 16`\n"
        "- Behavior/protection/handoff gates unchanged; readback correction "
        "is reporting-only\n"
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
