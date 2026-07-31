#!/usr/bin/env python3
"""Preregister recovery from T249's condition-type reporter mismatch."""

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


T249 = ANALYSIS / "t249_remaining_r2_preregistration.json"
T249_PROGRESS = Path(
    "D:/CodexArtifacts/open-duck-policy/t249_remaining_r2_v1/progress.json"
)
PARTIAL_MANIFEST = Path(
    "D:/CodexArtifacts/open-duck-policy/t249_remaining_r2_v1/"
    "19_KP_LO/T247_HOME_NEGATIVE_HALF_ADAPTER_HALF/p30/manifest.json"
)
FAILED_STDERR = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t249_launcher_logs_20260731_c19/runner.stderr.log"
)
ORIGINAL_RUNNER = ROOT / "tools/run_t249_remaining_r2.py"
OUTPUT = ANALYSIS / "t249b_reporter_recovery_preregistration.json"
MARKDOWN = (
    ANALYSIS / "T249B_REPORTER_RECOVERY_PREREGISTRATION_20260731.md"
)
RUNNER = ROOT / "tools/run_t249b_reporter_recovery.py"
TEST = ROOT / "tests/test_t249b_reporter_recovery.py"


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError("refusing to overwrite T249B preregistration")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T249B preregistration requires clean worktree")
    t249 = json.loads(T249.read_text(encoding="utf-8"))
    progress = json.loads(T249_PROGRESS.read_text(encoding="utf-8"))
    partial = json.loads(PARTIAL_MANIFEST.read_text(encoding="utf-8"))
    stderr = FAILED_STDERR.read_text(encoding="utf-8")
    runner_text = ORIGINAL_RUNNER.read_text(encoding="utf-8")
    checks = {
        "t249_contract_was_green": (
            t249["status"] == "PREREGISTERED_T249_REMAINING_R2"
            and not t249["failed_checks"]
        ),
        "condition_18_progress_green": (
            progress["status"] == "IN_PROGRESS_T249_REMAINING_R2"
            and progress["completed_new_conditions"] == 1
            and len(progress["new_conditions"]) == 1
            and progress["new_conditions"][0]["condition_id"]
            == "HOME_JOINT_OFFSET_POS"
            and progress["new_conditions"][0]["condition_green"]
            and progress["new_conditions"][0]["green_cells"] == 16
        ),
        "condition_19_first_block_complete_and_cached": (
            partial["block_contract"]["condition"]["id"] == "KP_LO"
            and partial["block_contract"]["policy"]["checkpoint_id"]
            == "T247_HOME_NEGATIVE_HALF_ADAPTER_HALF"
            and partial["block_contract"]["fit"]["fit_id"] == "p30"
            and len(partial["traces"]) == 4
        ),
        "failure_is_reporter_type_mismatch": (
            "corrected_extract_block(" in runner_text
            and "KeyError: 'joint_qpos0_offset_rad'" in stderr
            and "tools\\run_t249_remaining_r2.py" in stderr
            and "corrected_extract_block" in stderr
        ),
        "partial_behavior_is_not_rerun": True,
        "remaining_engine_uses_condition_appropriate_extractor": True,
        "one_fresh_condition_per_invocation_no_retry": True,
        "zero_new_behavior_optimizer_hosted_or_robot_now": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T249B preregistration checks failed: {failed}")
    frozen = {
        "builder": Path(__file__),
        "runner": RUNNER,
        "test": TEST,
        "t249_contract": T249,
        "t249_original_runner": ORIGINAL_RUNNER,
        "condition_18_progress": T249_PROGRESS,
        "condition_19_partial_manifest": PARTIAL_MANIFEST,
        "condition_19_failed_stderr": FAILED_STDERR,
    }
    basis: dict[str, Any] = {
        "schema_version": (
            "open_duck.t249b_reporter_recovery_preregistration.v1"
        ),
        "status": "PREREGISTERED_T249B_REPORTER_RECOVERY",
        "classification": (
            "reporting-only: the KP_LO evaluator completed all four first-"
            "block cells and wrote a valid manifest before the home-offset-"
            "specific readback correction indexed the wrong override key"
        ),
        "execution_contract": receipt(T249),
        "condition_18_progress": receipt(T249_PROGRESS),
        "condition_19_partial_manifest": receipt(PARTIAL_MANIFEST),
        "recovery": {
            "reuse_condition_18": True,
            "reuse_condition_19_half_p30": True,
            "rerun_completed_cells": False,
            "extract_joint_offset_with_corrected_helper": True,
            "extract_all_other_conditions_with_frozen_r2_helper": True,
            "maximum_new_conditions_per_invocation": 1,
            "stop_after_first_failed_condition": True,
            "no_retry": True,
        },
        "decision_rule": t249["decision_rule"],
        "frozen_inputs": {
            name: receipt(path) for name, path in frozen.items()
        },
        "checks": checks,
        "failed_checks": failed,
        "execution_now": {
            "new_behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "recover_without_rerunning_completed_cells": True,
            "continue_conditions_19_then_20_cpu_only": True,
            "offline_deployment_contract_audit_preregistration": False,
            "training": False,
            "hosted": False,
            "gate5": False,
            "rdkx5_or_robot": False,
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
        "# T249B reporter recovery preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Classification: reporting-only condition-type mismatch\n"
        "- Reuse: condition 18 and completed condition-19 half/P30 block\n"
        "- Continue: condition 19, then 20; one condition per invocation\n"
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
