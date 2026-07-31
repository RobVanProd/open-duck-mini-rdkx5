#!/usr/bin/env python3
"""Freeze the read-only T129 train/deploy forward-path audit."""

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


T128 = ANALYSIS / "t128_negative_only_expert_cpu_result.json"
T129 = ANALYSIS / "t129_negative_only_expert_hosted_preregistration.json"
T131_PREREG = ANALYSIS / "t131_t129_postexport_preregistration.json"
T141B = ANALYSIS / "t141b_worker_wiring_recovery_result.json"
OUTPUT = (
    ANALYSIS / "t142_t129_forward_path_mismatch_preregistration.json"
)
MARKDOWN = (
    ANALYSIS / "T142_T129_FORWARD_PATH_MISMATCH_PREREGISTRATION_20260729.md"
)
BUILDER = Path(__file__).resolve()
RUNNER = ROOT / "tools" / "run_t142_t129_forward_path_mismatch_audit.py"
TEST = ROOT / "tests" / "test_t142_t129_forward_path_mismatch.py"
RAW_ROOT = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t129_colab_extracted_20260729/"
    "t129_negative_only_expert_continuation/training"
)
HARD_ROOT = Path(
    "D:/CodexArtifacts/open-duck-policy/t131_t129_deployments_v1"
)
RAW = {
    "1003520": RAW_ROOT / "2026_07_29_101025_1003520.onnx",
    "2007040": RAW_ROOT / "2026_07_29_101552_2007040.onnx",
}
HARD = {
    step: HARD_ROOT / step / "deployment" / "action_margin.onnx"
    for step in RAW
}


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T142: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T142 preregistration requires clean worktree")
    t141 = json.loads(T141B.read_text(encoding="utf-8"))
    frozen_inputs = {
        "builder": BUILDER,
        "runner": RUNNER,
        "test": TEST,
        "t128_result": T128,
        "t129_prereg": T129,
        "t131_prereg": T131_PREREG,
        "t141b_result": T141B,
    }
    checks = {
        "t141_closed_hard_gated_expert_bank": (
            t141["status"]
            == "HOLD_T141B_EXPERT_BANK_NEGATIVE_ENDPOINT_MATRIX"
            and t141["decision"] == "CLOSE_CONTEXT_SELECTED_EXPERT_BANK"
            and t141["condition"]["green_cells"] == 4
        ),
        "raw_and_hard_graphs_present": all(
            path.is_file() for path in (*RAW.values(), *HARD.values())
        ),
        "frozen_inputs_present": all(
            path.is_file() for path in frozen_inputs.values()
        ),
        "read_only_no_behavior_training_colab_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T142 preregistration checks failed: {failed}")
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t142_t129_forward_path_mismatch_"
            "preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T142_T129_FORWARD_PATH_MISMATCH_AUDIT"
        ),
        "question": (
            "Was T129 trained with its negative expert always on but "
            "evaluated only after T131 restored a hard hidden-state gate?"
        ),
        "raw_training_graphs": {
            step: receipt(path) for step, path in RAW.items()
        },
        "hard_gate_deployments": {
            step: receipt(path) for step, path in HARD.items()
        },
        "frozen_inputs": {
            name: receipt(path) for name, path in frozen_inputs.items()
        },
        "checks": checks,
        "failed_checks": failed,
        "decision_rule": {
            "pass_decision": (
                "EARN_T143_CALIBRATION_CONDITIONAL_FORWARD_PATH_"
                "TRANSFORM_PREREGISTRATION_ONLY"
            ),
            "fail_decision": "CLOSE_T129_FORWARD_PATH_MISMATCH",
        },
        "execution_now": {
            "onnx_graphs_read": 0,
            "formal_behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "one_read_only_cpu_audit": True,
            "conditional_forward_path_transform_preregistration": False,
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
        "# T142 T129 forward-path mismatch preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Compare raw hosted exports to hard-gated deployments\n"
        "- No graph mutation or behavior in this audit\n"
        "- Optimizer / Colab / robot: `0/0/0`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
