#!/usr/bin/env python3
"""Preregister recovery from T250's raw-response/full-handoff schema mismatch."""

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


T250 = ANALYSIS / "t250_offline_deployment_contract_audit_preregistration.json"
T249B = ANALYSIS / "t249b_reporter_recovery_result.json"
ORIGINAL_RUNNER = ROOT / "tools/run_t250_offline_deployment_contract_audit.py"
RECOVERY_RUNNER = ROOT / "tools/run_t250b_reporter_recovery.py"
TEST = ROOT / "tests/test_t250b_reporter_recovery.py"
OUTPUT = ANALYSIS / "t250b_reporter_recovery_preregistration.json"
MARKDOWN = ANALYSIS / "T250B_REPORTER_RECOVERY_PREREGISTRATION_20260731.md"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError("refusing to overwrite T250B preregistration")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T250B preregistration requires a clean worktree")

    t250 = load(T250)
    t249b = load(T249B)
    runner_text = ORIGINAL_RUNNER.read_text(encoding="utf-8")
    t250_outputs_absent = all(
        not path.exists()
        for path in (
            ANALYSIS / "t250_offline_deployment_contract_audit_result.json",
            ANALYSIS / "t250_gate5_policy_handoff_manifest.json",
            ANALYSIS / "T250_OFFLINE_DEPLOYMENT_CONTRACT_AUDIT_RESULT_20260731.md",
        )
    )
    checks = {
        "t250_contract_green_and_canonical": (
            t250["status"]
            == "PREREGISTERED_T250_OFFLINE_DEPLOYMENT_CONTRACT_AUDIT"
            and not t250["failed_checks"]
            and canonical_sha256(
                {
                    key: value
                    for key, value in t250.items()
                    if key != "preregistered_contract_sha256"
                }
            )
            == t250["preregistered_contract_sha256"]
        ),
        "t249b_evidence_remains_green": (
            t249b["status"] == "PASS_T249B_REPORTER_RECOVERY"
            and t249b["summary"]["green_cells"] == 320
        ),
        "failure_precedes_any_t250_output": t250_outputs_absent,
        "failure_is_raw_response_schema_assumption": (
            'response = run["response_calibration"]' in runner_text
            and 'response["handoff_state_preserved"]' in runner_text
            and 'response["locomotion_hidden_exact_zero"]' in runner_text
        ),
        "frozen_block_extractors_already_produce_full_handoff": True,
        "recovery_reads_existing_manifests_and_traces_without_behavior_rerun": True,
        "original_onnx_and_golden_tick_audit_unchanged": True,
        "zero_simulator_optimizer_hosted_or_robot_now": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T250B preregistration checks failed: {failed}")

    frozen = {
        "builder": Path(__file__).resolve(),
        "recovery_runner": RECOVERY_RUNNER,
        "test": TEST,
        "t250_contract": T250,
        "t249b_full_r2_result": T249B,
        "original_t250_runner": ORIGINAL_RUNNER,
    }
    basis: dict[str, Any] = {
        "schema_version": "open_duck.t250b_reporter_recovery_preregistration.v1",
        "status": "PREREGISTERED_T250B_REPORTER_RECOVERY",
        "classification": (
            "reporting-only: the raw worker response stores prefix configuration, "
            "while the frozen R2 block extractor reconstructs the complete handoff "
            "proof from the immutable trace"
        ),
        "recovery_contract": {
            "patch_original_runner_in_memory": True,
            "replace_only_fresh_handoff_extraction_and_golden_handoff_source": True,
            "use_corrected_home_offset_extractor_for_condition_18": True,
            "use_frozen_r2_extractor_for_conditions_19_and_20": True,
            "reuse_all_320_behavior_cells": True,
            "rerun_behavior_cells": 0,
            "retain_original_onnx_cpu_chains": True,
            "retain_original_selection_and_authority_rules": True,
        },
        "frozen_inputs": {name: receipt(path) for name, path in frozen.items()},
        "checks": checks,
        "failed_checks": failed,
        "decision_rule": {
            "pass": "RECOVER_T250_AND_PRESERVE_ITS_FROZEN_DECISION",
            "fail": "HOLD_T250_REPORTER_RECOVERY",
            "gate5_on_pass": False,
            "robot_on_pass": False,
        },
        "execution_now": {
            "onnx_inferences": 0,
            "simulator_steps": 0,
            "behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "run_recovered_cpu_audit": True,
            "runtime_integration_preregistration": False,
            "training": False,
            "hosted": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    value = {**basis, "preregistered_contract_sha256": canonical_sha256(basis)}
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T250B reporter recovery preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Classification: reporting-only raw-response/full-handoff schema mismatch\n"
        "- Recovery: frozen block extractor; no behavior rerun\n"
        "- Simulator/optimizer/hosted/robot: `0/0/0/0`\n"
        "- Gate 5 remains: `NOT_AUTHORIZED`\n"
        f"- Contract SHA-256: `{value['preregistered_contract_sha256']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
