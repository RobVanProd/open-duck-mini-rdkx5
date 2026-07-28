#!/usr/bin/env python3
"""Freeze T78 midpoint's full eight-cell formal diagnostic."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
MIDPOINT = ANALYSIS / "t81_t78_midpoint_result.json"
INVALIDATION = ANALYSIS / "t82_t78_midpoint_crossover_invalidation.json"
T80_PREREG = ANALYSIS / "t80_t78_nominal_matrix_preregistration.json"
T80_RESULT = ANALYSIS / "t80_t78_nominal_matrix_result.json"
RUNNER = ROOT / "tools" / "run_t83_t78_midpoint_full_matrix.py"
WORKER = ROOT / "tools" / "evaluate_t27_t23_robustness_condition.py"
ADAPTER = ROOT / "tools" / "t27_state_coherent_eval_adapter.py"
TEST = ROOT / "tests" / "test_t83_t78_midpoint_full_matrix.py"
OUTPUT = ANALYSIS / "t83_t78_midpoint_full_preregistration.json"
MARKDOWN = ANALYSIS / "T83_T78_MIDPOINT_FULL_PREREGISTRATION_20260728.md"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: Any) -> str:
    payload = dict(value)
    payload.pop("preregistered_contract_sha256", None)
    return hashlib.sha256(
        json.dumps(
            payload,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def receipt(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T83: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"],
        cwd=ROOT,
        text=True,
    ).strip():
        raise RuntimeError("T83 preregistration requires a clean worktree")
    midpoint = json.loads(MIDPOINT.read_text(encoding="utf-8"))
    invalidation = json.loads(INVALIDATION.read_text(encoding="utf-8"))
    basis = json.loads(T80_PREREG.read_text(encoding="utf-8"))
    t80 = json.loads(T80_RESULT.read_text(encoding="utf-8"))
    wrapped = midpoint["midpoint"]["wrapped"]
    policy_path = Path(wrapped["path"])
    checks = {
        "t81_midpoint_contract_green": (
            midpoint["status"]
            == "PASS_T81_T78_EXACT_ADAPTER_MIDPOINT"
            and midpoint["failed_checks"] == []
        ),
        "t82_invalidated_before_behavior": (
            invalidation["status"]
            == "INVALIDATED_T82_PROTOCOL_BEFORE_BEHAVIOR"
            and invalidation["failed_checks"] == []
            and invalidation["execution"]["formal_behavior_cells"] == 0
            and invalidation["execution"]["simulator_trace_rows"] == 0
        ),
        "t80_exact_14_of_16_hold": (
            t80["status"] == "HOLD_T80_T78_NOMINAL_MATRIX"
            and t80["condition"]["green_cells"] == 14
            and t80["condition"]["cells"] == 16
        ),
        "midpoint_policy_exact": (
            policy_path.is_file()
            and sha256(policy_path) == wrapped["sha256"]
        ),
        "formal_full_command_set_unchanged": (
            basis["commands_x_m_s"] == [0.0, 0.074, 0.077, 0.08]
        ),
        "exact_two_fits": len(basis["fits"]) == 2,
        "runner_worker_adapter_test_present": all(
            path.is_file() for path in (RUNNER, WORKER, ADAPTER, TEST)
        ),
        "diagnostic_only_no_candidate_promotion": True,
        "training_colab_robot_and_gate5_zero": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, value in checks.items() if not value)
    policy = {
        "checkpoint_id": "T78_EXACT_ADAPTER_MIDPOINT_DIAGNOSTIC",
        "step": -1,
        **wrapped,
    }
    payload: dict[str, Any] = {
        "schema_version": (
            "open_duck.t83_t78_midpoint_full_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T83_T78_MIDPOINT_FULL_MATRIX"
            if not failed
            else "HOLD_T83_T78_MIDPOINT_FULL_PREREGISTRATION"
        ),
        "question": (
            "Does the exact half/final adapter midpoint pass all four "
            "commands under both measured actuator fits?"
        ),
        "commands_x_m_s": basis["commands_x_m_s"],
        "seed": basis["seed"],
        "conditions": basis["conditions"],
        "policies": [policy],
        "fits": basis["fits"],
        "calibrator": basis["calibrator"],
        "reference_feature_table": basis["reference_feature_table"],
        "playground": basis["playground"],
        "support_handoff": basis["support_handoff"],
        "behavior_contract": basis["behavior_contract"],
        "protection_contract": basis["protection_contract"],
        "repository_inputs": basis["repository_inputs"],
        "matrix": {
            "conditions": 1,
            "policies": 1,
            "fits": 2,
            "commands": 4,
            "maximum_cells": 8,
            "execution_order": (
                "midpoint -> p30/p31_34 -> 0/.074/.077/.080"
            ),
            "condition_must_complete": True,
            "cpu_only": True,
        },
        "decision_rule": {
            "pass": (
                "All eight cells pass every unchanged behavior, protection, "
                "handoff, readback, action-margin, and rate check."
            ),
            "pass_decision": (
                "EARN_T84_PERSISTENT_INTERPOLATION_MECHANISM_PREREGISTRATION_ONLY"
            ),
            "fail_decision": "CLOSE_EXACT_T78_ADAPTER_MIDPOINT",
            "candidate_promotion": False,
            "persistence_satisfied": False,
            "no_coefficient_search": True,
        },
        "frozen_inputs": {
            "t81_midpoint": receipt(MIDPOINT),
            "t82_invalidation": receipt(INVALIDATION),
            "t80_preregistration": receipt(T80_PREREG),
            "t80_result": receipt(T80_RESULT),
            "runner": receipt(RUNNER),
            "worker": receipt(WORKER),
            "adapter": receipt(ADAPTER),
            "test": receipt(TEST),
        },
        "checks": checks,
        "failed_checks": failed,
        "authority": {
            "execute_one_eight_cell_cpu_screen": not failed,
            "persistent_mechanism_preregistration": False,
            "training": False,
            "colab": False,
            "candidate_promotion": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    payload["preregistered_contract_sha256"] = canonical_sha256(payload)
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T83 T78 midpoint full-matrix preregistration",
                "",
                f"- Status: `{payload['status']}`",
                "- Cells: `8`",
                "- Policy: exact half/final adapter midpoint",
                "- Fits: `P30 / P31-34`",
                "- Commands: `0 / .074 / .077 / .080 m/s`",
                "- Candidate status: `diagnostic only; persistence unsatisfied`",
                "- Training/Colab/Gate5/robot: `0/0/0/0`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"failed_checks={failed}")
    print(
        "contract_sha256="
        f"{payload['preregistered_contract_sha256']}"
    )
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
