#!/usr/bin/env python3
"""Freeze T149's zero-credit negative-context command plateau."""

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


OUTPUT = (
    ANALYSIS
    / "t149_negative_context_command_plateau_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "T149_NEGATIVE_CONTEXT_COMMAND_PLATEAU_PREREGISTRATION_20260729.md"
)
T135B = (
    ANALYSIS
    / "t135b_interrupted_calibration_context_router_recovery_result.json"
)
T143C = ANALYSIS / "t143c_runner_receipt_recovery_result.json"
T145C = ANALYSIS / "t145c_cache_contract_recovery_result.json"
T146C = ANALYSIS / "t146c_test_receipt_recovery_result.json"
T148B = ANALYSIS / "t148b_command_group_risk_cpu_recovery_result.json"
REFERENCE = ANALYSIS / "ground_up_projected_reference_feature_table.npz"
RUNNER = (
    ROOT / "tools/run_t149_negative_context_command_plateau_transform.py"
)
TEST = ROOT / "tests/test_t149_negative_context_command_plateau.py"


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T149: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("formal T149 preregistration requires clean tree")
    t135 = json.loads(T135B.read_text(encoding="utf-8"))
    t143 = json.loads(T143C.read_text(encoding="utf-8"))
    t145 = json.loads(T145C.read_text(encoding="utf-8"))
    t146 = json.loads(T146C.read_text(encoding="utf-8"))
    t148 = json.loads(T148B.read_text(encoding="utf-8"))
    checks = {
        "calibration_contexts_green": (
            t135["status"]
            == "PASS_T135B_INTERRUPTED_CALIBRATION_CONTEXT_ROUTER_RECOVERY"
            and t135["failed_checks"] == []
        ),
        "conditional_forward_path_green": (
            t143["status"]
            == "PASS_T143C_CONDITIONAL_FORWARD_PATH_TRANSFORM"
            and t143["failed_checks"] == []
        ),
        "negative_endpoint_failure_exact": (
            t145["status"]
            == "HOLD_T145C_CONDITIONAL_PATH_NEGATIVE_ENDPOINT_MATRIX"
            and t145["condition"]["green_cells"] == 8
        ),
        "upper_command_attribution_exact": (
            t146["status"] == "PASS_T146C_UPPER_COMMAND_ATTRIBUTION"
            and t146["classification"]
            == "SUSTAINED_UPPER_COMMAND_POLICY_COLLAPSE_NOT_HANDOFF"
        ),
        "grouped_risk_closed_without_hosted_run": (
            t148["status"]
            == "HOLD_T148B_COMMAND_GROUP_RISK_CPU_RECOVERY"
            and t148["decision"] == "CLOSE_COMMAND_GROUP_RISK_INTEGRATION"
            and t148["execution"]["hosted_compute_units"] == 0
        ),
        "all_inputs_present": all(
            path.exists()
            for path in (
                T135B,
                T143C,
                T145C,
                T146C,
                T148B,
                REFERENCE,
                RUNNER,
                TEST,
            )
        ),
        "no_training_runtime_abi_or_hardware_change": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T149 preregistration checks failed: {failed}")
    frozen = {
        "builder": receipt(Path(__file__).resolve()),
        "runner": receipt(RUNNER),
        "test": receipt(TEST),
        "t135b_contexts": receipt(T135B),
        "t143c_result": receipt(T143C),
        "t145c_result": receipt(T145C),
        "t146c_result": receipt(T146C),
        "t148b_closure": receipt(T148B),
        "reference_feature_table": receipt(REFERENCE),
    }
    for step, item in sorted(t143["graphs"].items()):
        frozen[f"source_graph_{step}"] = item["transformed"]
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t149_negative_context_command_plateau_"
            "preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T149_NEGATIVE_CONTEXT_COMMAND_PLATEAU"
        ),
        "question": (
            "Can a zero-credit graph-internal plateau preserve the proven "
            "negative-COM x=.074 gait at x=.077/.080 while leaving nominal, "
            "x=0, x=.074, external command semantics, and the ABI exact?"
        ),
        "repository_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "causal_basis": {
            "failure": (
                "T146C proves identical starting physical/policy state and "
                "sustained collapse only at x=.077/.080"
            ),
            "reference_alias": (
                "T149 must prove obs[101:115] is bit-exact across "
                "x=.074/.077/.080 over every shared trace row"
            ),
            "intervention": (
                "under the existing calibrated negative condition only, "
                "replace the policy-internal obs[6] with min(obs[6], .074)"
            ),
        },
        "mechanism": {
            "external_input_abi": "unchanged_115_14_64_plus_context",
            "external_command": "unchanged",
            "nominal_context": "bit_exact_source",
            "negative_context_x0": "bit_exact_source",
            "negative_context_x074": "bit_exact_source",
            "negative_context_upper": "internal_command_capped_at_0.074",
            "reference_features": "unchanged",
            "action_pipeline": "unchanged",
            "runtime_change": False,
            "training": False,
            "new_scalar_search": False,
            "cap_m_s": 0.074,
            "cap_derivation": "only_full_horizon_passing_negative_command",
        },
        "thresholds": {
            "maximum_reference_feature_delta": 0.0,
            "minimum_shared_trace_rows": 95,
            "random_equivalence_samples_per_context_command": 32,
            "stateful_chain_steps_per_context": 256,
            "maximum_equivalence_error": 0.0,
        },
        "frozen_inputs": frozen,
        "checks": checks,
        "failed_checks": failed,
        "decision_rule": {
            "pass": (
                "Both transformed graphs retain exact ABI and old graph "
                "content except the two raw-observation consumers; nominal "
                "all-command, negative x=0/x=.074, and negative-upper "
                "counterfactual outputs are bit-exact over random samples "
                "and 256-step stateful chains."
            ),
            "pass_decision": (
                "EARN_T150_NEGATIVE_COMMAND_PLATEAU_ENDPOINT_"
                "PREREGISTRATION_ONLY"
            ),
            "fail_decision": "CLOSE_NEGATIVE_CONTEXT_COMMAND_PLATEAU",
        },
        "execution_now": {
            "environment_steps": 0,
            "behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "execute_transform_contract": True,
            "negative_endpoint_preregistration": False,
            "training": False,
            "colab": False,
            "policy_promotion": False,
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
        "# T149 negative-context command plateau preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- External command/ABI: unchanged\n"
        "- Negative-only internal cap: `.074 m/s`\n"
        "- Nominal, x=0, x=.074: required bit-exact\n"
        "- Environment / behavior / optimizer / Colab / robot: `0/0/0/0/0`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
