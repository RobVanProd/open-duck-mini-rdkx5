#!/usr/bin/env python3
"""Freeze the read-only expert-bank causality audit."""

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


T102 = ANALYSIS / "t102_t100c_nominal_matrix_result.json"
T103 = ANALYSIS / "t103_t100c_negative_endpoint_result.json"
T132 = ANALYSIS / "t132b_interrupted_nominal_recovery_result.json"
T135B = (
    ANALYSIS
    / "t135b_interrupted_calibration_context_router_recovery_result.json"
)
T137 = ANALYSIS / "t137_static_router_nominal_result.json"
OUTPUT = ANALYSIS / "t138_expert_bank_causality_preregistration.json"
MARKDOWN = (
    ANALYSIS / "T138_EXPERT_BANK_CAUSALITY_PREREGISTRATION_20260729.md"
)
BUILDER = Path(__file__).resolve()
RUNNER = ROOT / "tools" / "run_t138_expert_bank_causality_audit.py"
TEST = ROOT / "tests" / "test_t138_expert_bank_causality.py"
NOMINAL_ROOT = Path(
    "D:/CodexArtifacts/open-duck-policy/t101_t100c_postexport_v1"
)
NEGATIVE_ROOT = Path(
    "D:/CodexArtifacts/open-duck-policy/t131_t129_deployments_v1"
)
STEPS = ("1003520", "2007040")


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T138: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T138 preregistration requires clean worktree")
    t137 = json.loads(T137.read_text(encoding="utf-8"))
    t135b = json.loads(T135B.read_text(encoding="utf-8"))
    nominal = {
        step: NOMINAL_ROOT / step / "action_margin.onnx"
        for step in STEPS
    }
    negative = {
        step: NEGATIVE_ROOT / step / "deployment" / "action_margin.onnx"
        for step in STEPS
    }
    frozen_inputs = {
        "builder": BUILDER,
        "runner": RUNNER,
        "test": TEST,
        "t102_nominal": T102,
        "t103_negative": T103,
        "t132_nominal": T132,
        "t135b_context": T135B,
        "t137_nominal": T137,
    }
    checks = {
        "t137_closes_always_off_router": (
            t137["status"] == "HOLD_T137_STATIC_ROUTER_NOMINAL_MATRIX"
            and t137["condition"]["green_cells"] == 14
            and t137["decision"] == "CLOSE_STATIC_ROUTER_ZERO_TRAINING_REPAIR"
        ),
        "calibration_context_separation_green": (
            t135b["status"]
            == "PASS_T135B_INTERRUPTED_CALIBRATION_CONTEXT_ROUTER_RECOVERY"
            and t135b["failed_checks"] == []
        ),
        "paired_graphs_present": all(
            path.is_file() for path in (*nominal.values(), *negative.values())
        ),
        "frozen_inputs_present": all(
            path.is_file() for path in frozen_inputs.values()
        ),
        "read_only_no_behavior_training_colab_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T138 preregistration checks failed: {failed}")
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t138_expert_bank_causality_"
            "preregistration.v1"
        ),
        "status": "PREREGISTERED_T138_EXPERT_BANK_CAUSALITY_AUDIT",
        "question": (
            "Do T137 and the paired graph identities prove that "
            "calibration context should select T100C versus T129 expert "
            "parameters while the original hidden-state gate remains?"
        ),
        "nominal_graphs": {
            step: receipt(path) for step, path in nominal.items()
        },
        "negative_graphs": {
            step: receipt(path) for step, path in negative.items()
        },
        "frozen_inputs": {
            name: receipt(path) for name, path in frozen_inputs.items()
        },
        "checks": checks,
        "failed_checks": failed,
        "decision_rule": {
            "pass_decision": (
                "EARN_T139_CONTEXT_SELECTED_EXPERT_BANK_TRANSFORM_"
                "PREREGISTRATION_ONLY"
            ),
            "fail_decision": "CLOSE_CONTEXT_SELECTED_EXPERT_BANK",
        },
        "execution_now": {
            "onnx_pairs_compared": 0,
            "formal_behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "one_read_only_cpu_audit": True,
            "expert_bank_transform_preregistration": False,
            "behavior_evaluation": False,
            "training": False,
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
        "# T138 expert-bank causality preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Compare two checkpoint graph pairs and frozen behavior evidence\n"
        "- No graph transform or behavior run in this audit\n"
        "- Optimizer / Colab / robot: `0/0/0`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
