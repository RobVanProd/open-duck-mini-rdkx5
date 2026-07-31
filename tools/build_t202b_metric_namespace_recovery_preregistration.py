#!/usr/bin/env python3
"""Preregister T202B's read-only metric-namespace recovery."""

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


T202_PREREG = ANALYSIS / "t202_predicted_roll_risk_cpu_preregistration.json"
T202_RESULT = ANALYSIS / "t202_predicted_roll_risk_cpu_result.json"
OUTPUT = ANALYSIS / "t202b_metric_namespace_recovery_preregistration.json"
MARKDOWN = (
    ANALYSIS / "T202B_METRIC_NAMESPACE_RECOVERY_PREREGISTRATION_20260730.md"
)
BUILDER = Path(__file__).resolve()
RUNNER = ROOT / "tools" / "run_t202b_metric_namespace_recovery.py"
TEST = ROOT / "tests" / "test_t202b_metric_namespace_recovery.py"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T202B: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T202B preregistration requires clean worktree")
    prereg = load(T202_PREREG)
    result = load(T202_RESULT)
    event_path = Path(result["training"]["event_file"]["path"])
    checks = {
        "t202_held_on_exact_single_metric_check": (
            result["status"]
            == "HOLD_T202_PREDICTED_ROLL_RISK_CPU_CONTRACT"
            and result["failed_checks"]
            == ["training_roll_risk_metrics_finite"]
            and sum(not value for value in result["checks"].values()) == 1
        ),
        "all_mechanism_checks_green": all(
            value
            for name, value in result["checks"].items()
            if name != "training_roll_risk_metrics_finite"
        ),
        "t202_preregistration_identity_matches": (
            result["preregistered_contract_sha256"]
            == prereg["preregistered_contract_sha256"]
        ),
        "event_file_exists": event_path.is_file(),
        "read_only_no_simulator_optimizer_hosted_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T202B preregistration checks failed: {failed}")
    basis: dict[str, Any] = {
        "schema_version": (
            "open_duck.t202b_metric_namespace_recovery_"
            "preregistration.v1"
        ),
        "status": "PREREGISTERED_T202B_METRIC_NAMESPACE_RECOVERY",
        "question": (
            "Did T202 hold solely because non-cost state diagnostics were "
            "emitted under eval/episode_t202/... instead of the anticipated "
            "eval/episode_reward/t202/... namespace?"
        ),
        "frozen_inputs": {
            "builder": receipt(BUILDER),
            "runner": receipt(RUNNER),
            "test": receipt(TEST),
            "t202_preregistration": receipt(T202_PREREG),
            "t202_result": receipt(T202_RESULT),
            "event_file": result["training"]["event_file"],
        },
        "expected_tags": {
            "cost": "eval/episode_cost/t202_predicted_roll_risk",
            "risk": "eval/episode_t202/predicted_roll_risk_rad",
            "excess": "eval/episode_t202/roll_risk_excess_rad",
            "original": "eval/episode_t202/original_clipped_reward",
        },
        "anticipated_but_absent_tags": [
            "eval/episode_reward/t202/predicted_roll_risk_rad",
            "eval/episode_reward/t202/roll_risk_excess_rad",
        ],
        "decision_rule": {
            "reporting_only": (
                "all four actual tags exist with exactly two finite events; "
                "cost and excess are positive; every non-reporting T202 "
                "check remains green"
            ),
            "reporting_only_decision": (
                "EARN_T203_PREDICTED_ROLL_RISK_HOSTED_"
                "PREREGISTRATION_ONLY"
            ),
            "otherwise": (
                "CLOSE_T202_PREDICTED_ROLL_RISK_AND_RETURN_TO_"
                "MECHANISM_SELECTION"
            ),
        },
        "checks": checks,
        "failed_checks": failed,
        "execution_now": {
            "event_files_read": 0,
            "simulator_transitions": 0,
            "optimizer_steps": 0,
            "behavior_cells": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "execute_read_only_recovery": True,
            "hosted_preregistration": False,
            "hosted_training": False,
            "behavior": False,
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
        "# T202B metric-namespace recovery preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Input: immutable T202 event file; no simulator or optimizer\n"
        "- Classification: reporting-only only if all four frozen actual "
        "tags contain two finite events and positive cost/excess\n"
        "- Simulator/optimizer/behavior/hosted/robot: `0/0/0/0/0`\n"
        f"- Contract SHA-256: `{value['preregistered_contract_sha256']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
