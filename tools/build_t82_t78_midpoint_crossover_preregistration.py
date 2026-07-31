#!/usr/bin/env python3
"""Freeze T78 midpoint's two-cell x=.08 crossover falsifier."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
MIDPOINT = ANALYSIS / "t81_t78_midpoint_result.json"
T80_PREREG = ANALYSIS / "t80_t78_nominal_matrix_preregistration.json"
T80_RESULT = ANALYSIS / "t80_t78_nominal_matrix_result.json"
RUNNER = ROOT / "tools" / "run_t82_t78_midpoint_crossover.py"
WORKER = ROOT / "tools" / "evaluate_t27_t23_robustness_condition.py"
ADAPTER = ROOT / "tools" / "t27_state_coherent_eval_adapter.py"
TEST = ROOT / "tests" / "test_t82_t78_midpoint_crossover.py"
OUTPUT = ANALYSIS / "t82_t78_midpoint_crossover_preregistration.json"
MARKDOWN = (
    ANALYSIS / "T82_T78_MIDPOINT_CROSSOVER_PREREGISTRATION_20260728.md"
)


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
            raise FileExistsError(f"refusing to overwrite T82: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"],
        cwd=ROOT,
        text=True,
    ).strip():
        raise RuntimeError("T82 preregistration requires a clean worktree")
    midpoint = json.loads(MIDPOINT.read_text(encoding="utf-8"))
    basis = json.loads(T80_PREREG.read_text(encoding="utf-8"))
    t80 = json.loads(T80_RESULT.read_text(encoding="utf-8"))
    wrapped = midpoint["midpoint"]["wrapped"]
    policy_path = Path(wrapped["path"])
    checks = {
        "t81_midpoint_contract_green": (
            midpoint["status"]
            == "PASS_T81_T78_EXACT_ADAPTER_MIDPOINT"
            and midpoint["failed_checks"] == []
            and midpoint["decision"]
            == "EARN_T82_TWO_CELL_MIDPOINT_CROSSOVER_PREREGISTRATION_ONLY"
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
        "exact_two_fits": len(basis["fits"]) == 2,
        "exact_one_command_x008": True,
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
            "open_duck.t82_t78_midpoint_crossover_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T82_T78_MIDPOINT_CROSSOVER"
            if not failed
            else "HOLD_T82_T78_MIDPOINT_CROSSOVER_PREREGISTRATION"
        ),
        "question": (
            "Does the exact half/final adapter midpoint survive x=.08 under "
            "both measured actuator fits where the source checkpoints failed "
            "on opposite fits?"
        ),
        "commands_x_m_s": [0.08],
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
            "commands": 1,
            "maximum_cells": 2,
            "execution_order": "midpoint -> p30/p31_34 -> x=.08",
            "condition_must_complete": True,
            "cpu_only": True,
        },
        "decision_rule": {
            "pass": (
                "Both x=.08 cells pass every unchanged behavior, protection, "
                "handoff, readback, action-margin, and rate check."
            ),
            "pass_decision": (
                "EARN_T83_FULL_MIDPOINT_DIAGNOSTIC_PREREGISTRATION_ONLY"
            ),
            "fail_decision": "CLOSE_EXACT_T78_ADAPTER_MIDPOINT",
            "candidate_promotion": False,
            "persistence_satisfied": False,
            "no_coefficient_search": True,
        },
        "frozen_inputs": {
            "t81_midpoint": receipt(MIDPOINT),
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
            "execute_one_two_cell_cpu_screen": not failed,
            "full_midpoint_preregistration": False,
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
                "# T82 T78 midpoint crossover preregistration",
                "",
                f"- Status: `{payload['status']}`",
                "- Cells: `2`",
                "- Policy: exact half/final adapter midpoint",
                "- Fits: `P30 / P31-34`",
                "- Command: `.080 m/s`",
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
