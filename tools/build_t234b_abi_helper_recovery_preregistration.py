#!/usr/bin/env python3
"""Preregister the exact T234 ABI-helper recovery."""

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


T234 = ANALYSIS / "t234_exact_low_command_head_route_preregistration.json"
ORIGINAL_RUNNER = ROOT / "tools" / "run_t234_exact_low_command_head_route.py"
PARTIAL = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t234_exact_low_command_final_head_v1/1003520/"
    "exact_low_command_final_head.onnx"
)
OUTPUT = ANALYSIS / "t234b_abi_helper_recovery_preregistration.json"
MARKDOWN = (
    ANALYSIS / "T234B_ABI_HELPER_RECOVERY_PREREGISTRATION_20260730.md"
)
BUILDER = Path(__file__).resolve()
RUNNER = ROOT / "tools" / "run_t234b_abi_helper_recovery.py"
TEST = ROOT / "tests" / "test_t234b_abi_helper_recovery.py"


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T234B: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T234B preregistration requires a clean worktree")
    t234 = json.loads(T234.read_text(encoding="utf-8"))
    partial_root = PARTIAL.parents[1]
    partial_files = sorted(path for path in partial_root.rglob("*") if path.is_file())
    runner_text = ORIGINAL_RUNNER.read_text(encoding="utf-8")
    helper_text = (
        ROOT / "tools" / "run_t136_static_calibration_router_transform.py"
    ).read_text(encoding="utf-8")
    checks = {
        "original_t234_preregistered": (
            t234["status"]
            == "PREREGISTERED_T234_EXACT_LOW_COMMAND_HEAD_ROUTE"
            and not t234["failed_checks"]
        ),
        "original_runner_frozen_exact": (
            receipt(ORIGINAL_RUNNER)
            == t234["frozen_inputs"]["runner"]
        ),
        "failure_line_is_exact_path_to_model_mismatch": (
            '"source_abi": abi(source)' in runner_text
            and '"transformed_abi": abi(destination)' in runner_text
            and "def abi(model: onnx.ModelProto)" in helper_text
            and "model.graph.input" in helper_text
        ),
        "single_partial_file_before_abi_call": (
            partial_files == [PARTIAL]
            and PARTIAL.is_file()
            and PARTIAL.stat().st_size > 0
        ),
        "no_original_result_written": not (
            ANALYSIS / "t234_exact_low_command_head_route_result.json"
        ).exists(),
        "recovery_patch_is_api_adapter_only": True,
        "no_behavior_training_hosted_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, value in checks.items() if not value)
    if failed:
        raise RuntimeError(f"T234B preregistration checks failed: {failed}")

    basis: dict[str, Any] = {
        "schema_version": (
            "open_duck.t234b_abi_helper_recovery_preregistration.v1"
        ),
        "status": "PREREGISTERED_T234B_ABI_HELPER_RECOVERY",
        "question": (
            "Does adapting only the T234 runner's ABI helper call from Path "
            "to loaded ModelProto recover the unchanged T234 contract?"
        ),
        "frozen_inputs": {
            name: receipt(path)
            for name, path in {
                "builder": BUILDER,
                "runner": RUNNER,
                "test": TEST,
                "original_preregistration": T234,
                "original_runner": ORIGINAL_RUNNER,
                "abi_helper": (
                    ROOT
                    / "tools"
                    / "run_t136_static_calibration_router_transform.py"
                ),
                "partial_transform": PARTIAL,
            }.items()
        },
        "failure": {
            "stage": "first transformed graph receipt construction",
            "exception": (
                "AttributeError: 'WindowsPath' object has no attribute 'graph'"
            ),
            "inference_rows": 0,
            "behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_sessions": 0,
            "robot_or_rdk_access": 0,
        },
        "recovery": {
            "original_runner_file_unchanged": True,
            "original_preregistration_unchanged": True,
            "adapter": (
                "abi(value) loads ONNX only when value is a Path; all other "
                "T234 code and the original preregistered inputs are reused"
            ),
            "new_work_root": (
                "D:/CodexArtifacts/open-duck-policy/"
                "t234b_abi_helper_recovery_v1"
            ),
            "partial_original_left_unchanged": True,
            "inner_result_must_pass_original_t234_checks": True,
        },
        "decision_rule": {
            "inner_t234_passes_exactly": (
                "RECOVER_T234_AND_EARN_T235_EXACT_LOW_COMMAND_NOMINAL_"
                "MATRIX_PREREGISTRATION_ONLY"
            ),
            "otherwise": "CLOSE_T234_RECOVERY_WITHOUT_BEHAVIOR",
            "no_new_mechanism_or_threshold": True,
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
            "execute_exact_recovery": True,
            "nominal_behavior_preregistration": False,
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
        "# T234B ABI-helper recovery preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Failure: Path passed to a ModelProto-only ABI helper\n"
        "- Patch: API adapter only; original runner and contract unchanged\n"
        "- Inference/behavior/training/hosted/robot before recovery: "
        "`0/0/0/0/0`\n"
        f"- Contract SHA-256: `{value['preregistered_contract_sha256']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
