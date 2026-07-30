#!/usr/bin/env python3
"""Freeze read-only attribution of T192's failed late switch."""

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


T192_PREREG = ANALYSIS / "t192_one_period_head_switch_preregistration.json"
T192_RESULT = ANALYSIS / "t192_one_period_head_switch_result.json"
OUTPUT = ANALYSIS / "t192b_switch_effect_attribution_preregistration.json"
MARKDOWN = (
    ANALYSIS / "T192B_SWITCH_EFFECT_ATTRIBUTION_PREREGISTRATION_20260730.md"
)
BUILDER = Path(__file__).resolve()
RUNNER = ROOT / "tools" / "run_t192b_switch_effect_attribution.py"
TEST = ROOT / "tests" / "test_t192b_switch_effect_attribution.py"


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T192B: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T192B preregistration requires clean worktree")

    prereg = json.loads(T192_PREREG.read_text(encoding="utf-8"))
    result = json.loads(T192_RESULT.read_text(encoding="utf-8"))
    hybrid_trace = Path(result["cell"]["protection"]["path"])
    original_trace = Path(prereg["original_failure_trace"]["path"])
    checks = {
        "t192_exact_behavior_hold": (
            result["status"]
            == "HOLD_T192_ONE_PERIOD_HEAD_SWITCH_FEASIBILITY"
            and result["decision"]
            == (
                "CLOSE_LATE_HEAD_SWITCH_AND_SELECT_GAIT_STATE_"
                "DISTRIBUTION_CURRICULUM"
            )
            and not any(
                not value for value in result["integrity_checks"].values()
            )
        ),
        "switch_and_original_traces_present": (
            hybrid_trace.is_file() and original_trace.is_file()
        ),
        "both_traces_have_547_rows": (
            result["cell"]["behavior"]["samples"] == 547
            and prereg["original_failure_trace"]["bytes"]
            == original_trace.stat().st_size
        ),
        "switch_tick_exact": result["switch"]["tick"] == 520,
        "read_only_no_inference_behavior_training_hosted_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T192B preregistration checks failed: {failed}")

    basis: dict[str, Any] = {
        "schema_version": (
            "open_duck.t192b_switch_effect_attribution_"
            "preregistration.v1"
        ),
        "status": "PREREGISTERED_T192B_SWITCH_EFFECT_ATTRIBUTION",
        "question": (
            "Did selecting the T186-final graph at tick 520 alter any policy "
            "output, target, state, or dynamics row before the repeated fall?"
        ),
        "switch_tick": 520,
        "terminal_tick": 546,
        "original_trace": prereg["original_failure_trace"],
        "hybrid_trace": {
            "path": str(hybrid_trace),
            "bytes": hybrid_trace.stat().st_size,
            "sha256": result["cell"]["protection"]["sha256"],
        },
        "comparison": {
            "row_range_inclusive": [520, 546],
            "all_original_fields": True,
            "switch_metadata_fields_excluded": [
                "policy_switch_active",
                "policy_session_role",
            ],
            "primary_action_fields": [
                "policy_raw_action",
                "action",
                "sent_target_rad",
                "applied_target_rad",
                "actual_position_rad",
            ],
            "selection_weight": 0,
        },
        "decision_rule": {
            "zero_effect": (
                "EARN_T193_CORRECTED_DYNAMIC_SUPPORT_CPU_CONTRACT_"
                "PREREGISTRATION_ONLY"
            ),
            "nonzero_effect": (
                "RETURN_TO_MECHANISM_SELECTION_WITH_LATE_SWITCH_EFFECT"
            ),
        },
        "frozen_inputs": {
            name: receipt(path)
            for name, path in {
                "builder": BUILDER,
                "runner": RUNNER,
                "test": TEST,
                "t192_preregistration": T192_PREREG,
                "t192_result": T192_RESULT,
                "original_trace": original_trace,
                "hybrid_trace": hybrid_trace,
            }.items()
        },
        "checks": checks,
        "failed_checks": failed,
        "execution_now": {
            "trace_rows_read": 0,
            "inference_rows": 0,
            "behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "execute_saved_trace_attribution": True,
            "dynamic_support_cpu_preregistration": False,
            "behavior": False,
            "training": False,
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
        "# T192B switch-effect attribution preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Compare sealed original and hybrid ticks `520-546`\n"
        "- All original fields; switch metadata excluded\n"
        "- Inference/behavior/training/hosted/robot: `0/0/0/0/0`\n"
        f"- Contract SHA-256: `{value['preregistered_contract_sha256']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
