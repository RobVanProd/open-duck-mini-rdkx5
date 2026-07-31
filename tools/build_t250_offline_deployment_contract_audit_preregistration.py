#!/usr/bin/env python3
"""Preregister the offline deployment-contract audit for the green T249B policy."""

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


T249B = ANALYSIS / "t249b_reporter_recovery_result.json"
T249 = ANALYSIS / "t249_remaining_r2_preregistration.json"
T247 = ANALYSIS / "t247_home_negative_half_adapter_route_result.json"
T247B = ANALYSIS / "t247b_reporting_recovery_result.json"
T8_AMENDMENT = ANALYSIS / "t8_state_coherent_handoff_abi_amendment.json"
T8_RESULT = ANALYSIS / "t8_state_coherent_handoff_result.json"
BUILDER = Path(__file__).resolve()
RUNNER = ROOT / "tools/run_t250_offline_deployment_contract_audit.py"
TEST = ROOT / "tests/test_t250_offline_deployment_contract_audit.py"
OUTPUT = ANALYSIS / "t250_offline_deployment_contract_audit_preregistration.json"
MARKDOWN = ANALYSIS / "T250_OFFLINE_DEPLOYMENT_CONTRACT_AUDIT_PREREGISTRATION_20260731.md"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError("refusing to overwrite T250 preregistration")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T250 preregistration requires a clean worktree")

    t249b = load(T249B)
    t249 = load(T249)
    t247 = load(T247)
    t247b = load(T247B)
    t8 = load(T8_RESULT)
    policies = sorted(t249["policies"], key=lambda row: int(row["step"]))
    selected = policies[-1]
    witness = policies[0]

    checks = {
        "t249b_full_r2_green": (
            t249b["status"] == "PASS_T249B_REPORTER_RECOVERY"
            and t249b["summary"]["all_twenty_conditions_green"]
            and t249b["summary"]["completed_conditions"] == 20
            and t249b["summary"]["green_cells"] == 320
        ),
        "t249b_earned_only_this_audit": (
            t249b["decision"]
            == "EARN_T250_OFFLINE_DEPLOYMENT_CONTRACT_AUDIT_PREREGISTRATION_ONLY"
            and not t249b["authority"]["gate5"]
            and not t249b["authority"]["rdkx5_or_robot"]
        ),
        "t247_structural_recovery_green": (
            t247["checks"]["stateful_abi_exact"]
            and t247["checks"]["onnx_checker_passes"]
            and t247b["status"] == "PASS_T247B_REPORTING_RECOVERY"
            and not t247b["failed_checks"]
        ),
        "state_coherent_handoff_contract_preexists": (
            t8["summary"]["all_handoff_contracts_pass"]
            and t8["expected_cells"] == 16
            and t8["completed_cells"] == 16
        ),
        "exact_two_checkpoint_population": len(policies) == 2,
        "checkpoint_spacing_frozen": (
            int(witness["step"]) == 1_003_520
            and int(selected["step"]) == 2_007_040
        ),
        "terminal_checkpoint_selected_without_metric_ranking": (
            selected["checkpoint_id"]
            == "T247_HOME_NEGATIVE_HALF_ADAPTER_FINAL"
            and witness["checkpoint_id"]
            == "T247_HOME_NEGATIVE_HALF_ADAPTER_HALF"
        ),
        "audit_is_cpu_read_only": True,
        "no_training_hosted_behavior_or_robot_now": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T250 preregistration checks failed: {failed}")

    frozen = {
        "builder": BUILDER,
        "runner": RUNNER,
        "test": TEST,
        "t249b_full_r2_result": T249B,
        "t249_execution_contract": T249,
        "t247_transform_result": T247,
        "t247_reporting_recovery": T247B,
        "t8_handoff_abi_amendment": T8_AMENDMENT,
        "t8_handoff_result": T8_RESULT,
    }
    basis: dict[str, Any] = {
        "schema_version": "open_duck.t250_offline_deployment_contract_audit_preregistration.v1",
        "status": "PREREGISTERED_T250_OFFLINE_DEPLOYMENT_CONTRACT_AUDIT",
        "question": (
            "Does the terminal green T247 graph have a complete, hash-frozen, "
            "CPU-executable deployment contract whose two-stage handoff exactly "
            "matches the 320/320 offline evaluator?"
        ),
        "selection_rule": {
            "deployment_checkpoint": "maximum preregistered continuation step",
            "selected_checkpoint_id": selected["checkpoint_id"],
            "selected_step": int(selected["step"]),
            "selected_sha256": selected["sha256"],
            "persistence_witness_checkpoint_id": witness["checkpoint_id"],
            "persistence_witness_step": int(witness["step"]),
            "persistence_witness_sha256": witness["sha256"],
            "behavior_metric_ranking_or_cherry_pick": False,
        },
        "audit_contract": {
            "verify_all_20_conditions_and_320_cells_green": True,
            "verify_all_recorded_handoff_checks_green": True,
            "verify_policy_and_calibrator_hashes_and_exact_abis": True,
            "run_onnx_checker_and_cpu_only_recurrent_chains": True,
            "verify_one_frozen_first_locomotion_tick_field_by_field": True,
            "freeze_observation_action_and_two_stage_handoff_semantics": True,
            "identify_p30_as_the_fixed_runtime_observer": True,
            "identify_p31_34_as_robustness_evidence_not_runtime_routing": True,
            "copy_or_modify_policy_binaries": False,
            "simulator_or_behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "pass_rule": (
            "Every frozen evidence, ABI, ONNX, CPU-chain, handoff, golden-tick, "
            "selection, and authority check passes."
        ),
        "decision_rule": {
            "pass": "EARN_VERSIONED_RDKX5_STATE_COHERENT_INTEGRATION_PREREGISTRATION_ONLY",
            "fail": "HOLD_POLICY_DEPLOYMENT_CONTRACT_AND_RETURN_TO_AUDIT",
            "gate5_on_pass": False,
            "robot_on_pass": False,
            "training_on_pass": False,
        },
        "frozen_inputs": {name: receipt(path) for name, path in frozen.items()},
        "checks": checks,
        "failed_checks": failed,
        "execution_now": {
            "onnx_inferences": 0,
            "simulator_steps": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "offline_cpu_audit": True,
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
        "# T250 offline deployment-contract audit preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Selected terminal checkpoint: `{selected['checkpoint_id']}`\n"
        f"- Persistence witness: `{witness['checkpoint_id']}`\n"
        "- Execution: CPU-only ONNX/read-only evidence audit\n"
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
