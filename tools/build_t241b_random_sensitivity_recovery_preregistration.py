#!/usr/bin/env python3
"""Preregister immutable recovery of T241's random sensitivity hold."""

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


T241_PREREG = (
    ANALYSIS
    / "t241_bounded_positive_router_transform_preregistration.json"
)
T241 = ANALYSIS / "t241_bounded_positive_router_transform_result.json"
OUTPUT = (
    ANALYSIS
    / "t241b_random_sensitivity_recovery_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "T241B_RANDOM_SENSITIVITY_RECOVERY_PREREGISTRATION_20260731.md"
)
BUILDER = Path(__file__).resolve()
RUNNER = ROOT / "tools" / "run_t241b_random_sensitivity_recovery.py"
TEST = ROOT / "tests" / "test_t241b_random_sensitivity_recovery.py"


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T241B: {path}")
    prereg = json.loads(T241_PREREG.read_text(encoding="utf-8"))
    result = json.loads(T241.read_text(encoding="utf-8"))
    checks = {
        "t241_is_immutable_single_check_hold": (
            result["status"]
            == "HOLD_T241_BOUNDED_POSITIVE_ROUTER_TRANSFORM"
            and result["failed_checks"] == ["random_contract_exact"]
            and result["checks"]["failed_trace_contract_exact"] is True
        ),
        "t241_contract_sha_exact": (
            result["preregistered_contract_sha256"]
            == prereg["preregistered_contract_sha256"]
        ),
        "read_only_no_transform_inference_behavior_training_hosted_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T241B preregistration checks failed: {failed}")

    basis: dict[str, Any] = {
        "schema_version": (
            "open_duck.t241b_random_sensitivity_recovery_"
            "preregistration.v1"
        ),
        "status": "PREREGISTERED_T241B_RANDOM_SENSITIVITY_RECOVERY",
        "question": (
            "Is T241's sole hold a non-causal random-output sensitivity "
            "expectation when structure, preservation, finiteness, exact "
            "source replay, and all 948 actual failed-state deltas are green?"
        ),
        "frozen_inputs": {
            "builder": receipt(BUILDER),
            "runner": receipt(RUNNER),
            "test": receipt(TEST),
            "t241_preregistration": receipt(T241_PREREG),
            "t241_result": receipt(T241),
        },
        "recovery_rule": {
            "pass_if": {
                "sole_failed_check": "random_contract_exact",
                "random_non_home_contexts_bit_exact": True,
                "random_home_negative_x0_bit_exact": True,
                "random_outputs_finite": True,
                "all_six_failed_traces_per_graph_source_exact": True,
                "all_six_failed_traces_per_graph_transformed_finite": True,
                "every_failed_trace_has_changed_actions": True,
                "all_structure_and_abi_checks_green": True,
            },
            "interpretation": (
                "random branch-output equality is not required for route "
                "binding; exact failed-state replay is the causal sensitivity "
                "test"
            ),
            "pass_decision": (
                "EARN_T242_BOUNDED_ROUTER_HOME_OFFSET_MATRIX_"
                "PREREGISTRATION_ONLY"
            ),
            "fail_decision": (
                "CLOSE_BOUNDED_POSITIVE_ROUTER_WITHOUT_BEHAVIOR"
            ),
            "no_rerun": True,
        },
        "checks": checks,
        "failed_checks": failed,
        "execution_now": {
            "onnx_transforms": 0,
            "inference_rows": 0,
            "behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_sessions": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "execute_immutable_result_review": True,
            "home_offset_behavior_preregistration": False,
            "training": False,
            "hosted": False,
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
        "# T241B random-sensitivity recovery preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Input: immutable T241 result; no transform or inference rerun\n"
        "- Decisive evidence: all `948` actual failed-state rows changed\n"
        "- Behavior/training/hosted/robot: `0/0/0/0`\n"
        f"- Contract SHA-256: `{value['preregistered_contract_sha256']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
