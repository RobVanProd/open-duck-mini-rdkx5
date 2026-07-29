#!/usr/bin/env python3
"""Freeze recovery after T135 completed exactly one calibration prefix."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
from typing import Any

from run_t135_calibration_context_router_screen import (
    ANALYSIS,
    WORK,
    canonical_sha256,
    context_sha256,
    receipt,
)
from run_t135b_interrupted_calibration_context_router_recovery import (
    load_context,
)


ROOT = Path(__file__).resolve().parents[1]
T135 = ANALYSIS / "t135_calibration_context_router_preregistration.json"
OUTPUT = (
    ANALYSIS
    / "t135b_interrupted_calibration_context_router_recovery_"
    "preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "T135B_INTERRUPTED_CALIBRATION_CONTEXT_ROUTER_RECOVERY_"
    "PREREGISTRATION_20260729.md"
)
RUNNER = (
    ROOT
    / "tools"
    / "run_t135b_interrupted_calibration_context_router_recovery.py"
)
BUILDER = Path(__file__).resolve()
TEST = (
    ROOT
    / "tests"
    / "test_t135b_interrupted_calibration_context_router_recovery.py"
)
TRACE = (
    WORK
    / "p30"
    / "nominal"
    / "traces"
    / "x0.074_seed167931544_calibration_context_diagnostic.jsonl"
)
EVALUATION = WORK / "p30" / "nominal" / "evaluation.json"
STDOUT = WORK / "p30" / "nominal" / "stdout.log"
POLICY = WORK / "calibration_context_diagnostic.onnx"


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T135B: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T135B preregistration requires clean worktree")
    t135 = json.loads(T135.read_text(encoding="utf-8"))
    context, trace_hash = load_context(TRACE)
    frozen_inputs = {
        "builder": BUILDER,
        "runner": RUNNER,
        "test": TEST,
        "source_t135_preregistration": T135,
        "evaluator": Path(t135["frozen_inputs"]["evaluator"]["path"]),
    }
    cached = {
        "diagnostic_policy": receipt(POLICY),
        "trace": receipt(TRACE),
        "evaluation": receipt(EVALUATION),
        "stdout": receipt(STDOUT),
    }
    checks = {
        "source_t135_preregistered": (
            t135["status"]
            == "PREREGISTERED_T135_CALIBRATION_CONTEXT_ROUTER_SCREEN"
        ),
        "source_t135_result_absent": not (
            ANALYSIS / "t135_calibration_context_router_result.json"
        ).exists(),
        "cached_context_shape_64": context.shape == (64,),
        "cached_context_matches_trace_hash": (
            context_sha256(context.reshape(1, 64)) == trace_hash
        ),
        "cached_context_matches_preregistered_hash": (
            trace_hash
            == t135["expected_context_hashes"]["p30"]["nominal"]
        ),
        "frozen_inputs_present": all(
            path.is_file() for path in frozen_inputs.values()
        ),
        "remaining_prefixes_exactly_three": True,
        "no_behavior_training_colab_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T135B preregistration checks failed: {failed}")
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t135b_interrupted_calibration_context_router_"
            "recovery_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T135B_INTERRUPTED_CALIBRATION_CONTEXT_"
            "ROUTER_RECOVERY"
        ),
        "source_t135_contract_sha256": t135[
            "preregistered_contract_sha256"
        ],
        "reason": (
            "The first prefix completed and matched its frozen hash; "
            "orchestration then read the hash from the summary instead of "
            "the trace row where the evaluator records it."
        ),
        "fits": t135["fits"],
        "populations": t135["populations"],
        "remaining_prefixes": [
            {"fit_id": "p30", "population": "com_x_negative"},
            {"fit_id": "p31_34", "population": "nominal"},
            {"fit_id": "p31_34", "population": "com_x_negative"},
        ],
        "expected_context_hashes": t135["expected_context_hashes"],
        "command_x_m_s": t135["command_x_m_s"],
        "seed": t135["seed"],
        "calibrator": t135["calibrator"],
        "reference_feature_table": t135["reference_feature_table"],
        "playground": t135["playground"],
        "thresholds": t135["thresholds"],
        "cached_prefix": cached,
        "frozen_inputs": {
            name: receipt(path) for name, path in frozen_inputs.items()
        },
        "checks": checks,
        "failed_checks": failed,
        "decision_rule": t135["decision_rule"],
        "execution_now": {
            "cached_calibration_prefixes": 1,
            "new_calibration_prefixes": 0,
            "formal_behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "three_missing_cpu_calibration_prefixes": True,
            "static_router_transform_preregistration": False,
            "behavior_evaluation": False,
            "training": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    value["recovery_contract_sha256"] = canonical_sha256(value)
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T135B interrupted calibration-context router recovery\n\n"
        f"- Status: `{value['status']}`\n"
        "- Preserved exact prefix: `P30 / nominal`\n"
        "- Remaining prefixes: `3`\n"
        "- Formal locomotion / optimizer / Colab / robot: `0/0/0/0`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"contract_sha256={value['recovery_contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
