#!/usr/bin/env python3
"""Freeze the expert-first negative-COM mechanism screen."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
T125_PREREG = ANALYSIS / "t125_expert_first_nominal_preregistration.json"
T125_RESULT = ANALYSIS / "t125_expert_first_nominal_result.json"
R2 = ANALYSIS / "t41_uniform_normalizer_r2_preregistration.json"
BUILDER = ROOT / "tools" / Path(__file__).name
RUNNER = ROOT / "tools" / "run_t126_expert_first_negative.py"
MATRIX = ROOT / "tools" / "run_t27_t23_robustness_matrix.py"
WORKER = ROOT / "tools" / "evaluate_t27_t23_robustness_condition.py"
ADAPTER = ROOT / "tools" / "t27_state_coherent_eval_adapter.py"
TEST = ROOT / "tests" / "test_t126_expert_first_negative.py"
OUTPUT = ANALYSIS / "t126_expert_first_negative_preregistration.json"
MARKDOWN = (
    ANALYSIS / "T126_EXPERT_FIRST_NEGATIVE_PREREGISTRATION_20260729.md"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def receipt(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def canonical_sha256(value: Any, ignored: str) -> str:
    payload = dict(value)
    payload.pop(ignored, None)
    return hashlib.sha256(
        json.dumps(
            payload,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--read-only-authorized", action="store_true")
    args = parser.parse_args()
    if not args.read_only_authorized:
        raise PermissionError("T126 preregistration requires authorization")
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T126: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T126 preregistration requires clean worktree")
    t125_prereg = json.loads(T125_PREREG.read_text(encoding="utf-8"))
    t125 = json.loads(T125_RESULT.read_text(encoding="utf-8"))
    r2 = json.loads(R2.read_text(encoding="utf-8"))
    condition = next(
        item for item in r2["conditions"] if item["condition_index"] == 7
    )
    sys.path.insert(0, str(ROOT / "tools"))
    try:
        from run_t27_t23_robustness_matrix import matrix_plan

        plan = matrix_plan(
            [condition],
            t125_prereg["policies"],
            t125_prereg["fits"],
            t125_prereg["commands_x_m_s"],
            int(t125_prereg["seed"]),
        )
    finally:
        sys.path.pop(0)
    inputs = {
        "builder": BUILDER,
        "runner": RUNNER,
        "matrix": MATRIX,
        "worker": WORKER,
        "adapter": ADAPTER,
        "test": TEST,
        "t125_preregistration": T125_PREREG,
        "t125_result": T125_RESULT,
        "r2": R2,
    }
    checks = {
        "t125_green": (
            t125["status"] == "PASS_T125_EXPERT_FIRST_NOMINAL_SCREEN"
            and t125["condition"]["green_cells"] == 16
        ),
        "condition_exact": (
            condition["id"] == "TORSO_COM_X_NEG"
            and condition["override"]["torso_com_offset_m"]
            == [-0.05, 0.0, 0.0]
        ),
        "sixteen_cells": len(plan) == 16,
        "inputs_present": all(path.is_file() for path in inputs.values()),
        "screen_is_not_candidate_promotion": True,
        "no_behavior_training_colab_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t126_expert_first_negative_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T126_EXPERT_FIRST_NEGATIVE_SCREEN"
            if not failed
            else "HOLD_T126_EXPERT_FIRST_NEGATIVE_PREREGISTRATION"
        ),
        "question": (
            "Does the expert-first factorial pair also preserve the exact "
            "negative-COM endpoint that motivated the router/expert mechanism?"
        ),
        "interpretation": t125_prereg["interpretation"],
        "condition": condition,
        "policies": t125_prereg["policies"],
        "fits": t125_prereg["fits"],
        "commands_x_m_s": t125_prereg["commands_x_m_s"],
        "seed": t125_prereg["seed"],
        "calibrator": t125_prereg["calibrator"],
        "reference_feature_table": t125_prereg[
            "reference_feature_table"
        ],
        "playground": t125_prereg["playground"],
        "support_handoff": t125_prereg["support_handoff"],
        "behavior_contract": t125_prereg["behavior_contract"],
        "protection_contract": t125_prereg["protection_contract"],
        "matrix": {
            "cells": 16,
            "plan_sha256": canonical_sha256({"plan": plan}, "unused"),
            "both_factorial_endpoints_required": True,
            "training_selection_weight": 0,
        },
        "decision_rule": {
            "pass_decision": (
                "EARN_T127_EXPERT_FIRST_STAGED_TRAINING_CPU_CONTRACT_ONLY"
            ),
            "fail_decision": "CLOSE_EXPERT_FIRST_STAGE_HYPOTHESIS",
            "no_hosted_training": True,
        },
        "repository_inputs": {
            name: receipt(path) for name, path in inputs.items()
        },
        "checks": checks,
        "failed_checks": failed,
        "authority": {
            "one_cpu_endpoint_screen": not failed,
            "staged_training_cpu_preregistration": False,
            "training": False,
            "colab": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    value["preregistered_contract_sha256"] = canonical_sha256(
        value, "preregistered_contract_sha256"
    )
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T126 expert-first negative-COM preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Matrix: exact `TORSO_COM_X_NEG`, 16 cells\n"
        "- This is a mechanism screen, not a candidate or checkpoint selection\n"
        "- Training / Colab / robot: `0 / 0 / 0`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"failed_checks={failed}")
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
