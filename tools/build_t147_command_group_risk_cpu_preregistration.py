#!/usr/bin/env python3
"""Freeze the parameter-free command-group risk CPU contract."""

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


T146C = ANALYSIS / "t146c_test_receipt_recovery_result.json"
OUTPUT = ANALYSIS / "t147_command_group_risk_cpu_preregistration.json"
MARKDOWN = (
    ANALYSIS / "T147_COMMAND_GROUP_RISK_CPU_PREREGISTRATION_20260729.md"
)
BUILDER = Path(__file__).resolve()
RUNNER = ROOT / "tools" / "run_t147_command_group_risk_cpu_contract.py"
CORE = ROOT / "tools" / "t147_command_group_risk.py"
TEST = ROOT / "tests" / "test_t147_command_group_risk.py"


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T147: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T147 preregistration requires clean worktree")
    t146c = json.loads(T146C.read_text(encoding="utf-8"))
    frozen = {
        "builder": BUILDER,
        "runner": RUNNER,
        "core": CORE,
        "test": TEST,
        "t146c_result": T146C,
    }
    checks = {
        "t146c_earns_group_risk_only": (
            t146c["status"] == "PASS_T146C_UPPER_COMMAND_ATTRIBUTION"
            and t146c["classification"]
            == "SUSTAINED_UPPER_COMMAND_POLICY_COLLAPSE_NOT_HANDOFF"
            and t146c["decision"]
            == "EARN_T147_COMMAND_GROUP_RISK_CPU_CONTRACT_"
            "PREREGISTRATION_ONLY"
        ),
        "frozen_inputs_present": all(path.is_file() for path in frozen.values()),
        "no_behavior_optimizer_colab_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T147 preregistration checks failed: {failed}")
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t147_command_group_risk_cpu_preregistration.v1"
        ),
        "status": "PREREGISTERED_T147_COMMAND_GROUP_RISK_CPU_CONTRACT",
        "question": (
            "Can a parameter-free worst-group PPO actor loss make one of "
            "x=.074/.077/.080 authoritative instead of averaging its failure "
            "into the full batch?"
        ),
        "mechanism": {
            "anchors_x_m_s": [0.074, 0.077, 0.08],
            "boundaries_x_m_s": [0.0755, 0.0785],
            "group_surrogate": (
                "-mean(min(rho*A, clip(rho)*A) | command group)"
            ),
            "actor_policy_loss": "max(group_surrogate[0:3])",
            "advantage_normalization": "unchanged frozen global rule",
            "critic_entropy_optimizer": "unchanged",
            "new_scalar_hyperparameters": 0,
            "policy_abi_change": False,
            "deployment_graph_change": False,
        },
        "contract": {
            "anchor_group_ids": [0, 1, 2],
            "all_groups_required_in_each_minibatch": True,
            "worst_group_only_has_nonzero_actor_gradient_when_unique": True,
            "permutation_invariant": True,
            "standard_loss_differs_on_known_averaging_failure": True,
            "cpu_jit_and_grad_finite": True,
        },
        "frozen_inputs": {name: receipt(path) for name, path in frozen.items()},
        "checks": checks,
        "failed_checks": failed,
        "decision_rule": {
            "pass_decision": (
                "EARN_T148_COMMAND_GROUP_RISK_ONE_UPDATE_"
                "PREREGISTRATION_ONLY"
            ),
            "fail_decision": "CLOSE_COMMAND_GROUP_RISK_OBJECTIVE",
        },
        "execution_now": {
            "synthetic_rows": 0,
            "environment_steps": 0,
            "optimizer_steps": 0,
            "behavior_cells": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "one_synthetic_cpu_contract": True,
            "integrated_one_update_preregistration": False,
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
        "# T147 command-group risk CPU preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Actor loss: worst of the .074/.077/.080 group surrogates\n"
        "- Critic, entropy, optimizer, normalizer, and ABI: unchanged\n"
        "- New scalar hyperparameters: `0`\n"
        "- Behavior / optimizer / Colab / robot: `0/0/0/0`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
