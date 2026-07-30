#!/usr/bin/env python3
"""Freeze T222B's ABI-helper-only pre-execution recovery."""

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


T222_PREREG = ANALYSIS / "t222_global_command_plateau_preregistration.json"
T222_RESULT = ANALYSIS / "t222_global_command_plateau_result.json"
PARTIAL = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t222_global_command_plateau_v1/1003520/global_command_plateau.onnx"
)
OUTPUT = (
    ANALYSIS / "t222b_abi_helper_recovery_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "T222B_ABI_HELPER_RECOVERY_PREREGISTRATION_20260730.md"
)
SOURCE_RUNNER = ROOT / "tools/run_t222_global_command_plateau_transform.py"
RUNNER = ROOT / "tools/run_t222b_abi_helper_recovery.py"
TEST = ROOT / "tests/test_t222b_abi_helper_recovery.py"


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError("refusing to overwrite T222B preregistration")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T222B preregistration requires clean worktree")
    source = json.loads(T222_PREREG.read_text(encoding="utf-8"))
    source_text = SOURCE_RUNNER.read_text(encoding="utf-8")
    frozen = {
        "builder": receipt(Path(__file__)),
        "runner": receipt(RUNNER),
        "test": receipt(TEST),
        "t222_preregistration": receipt(T222_PREREG),
        "t222_source_runner": receipt(SOURCE_RUNNER),
        "t222_partial_half_graph": receipt(PARTIAL),
    }
    checks = {
        "t222_exact_preregistration": (
            source["status"] == "PREREGISTERED_T222_GLOBAL_COMMAND_PLATEAU"
            and not source["failed_checks"]
            and source["preregistered_contract_sha256"]
            == "626b4a9a66d16430be69b0606e1b2ef483c1e650a5042a023f5be64d713e3f9d"
        ),
        "t222_formal_result_absent": not T222_RESULT.exists(),
        "single_partial_half_graph_exists": (
            PARTIAL.is_file()
            and not Path(
                "D:/CodexArtifacts/open-duck-policy/"
                "t222_global_command_plateau_v1/2007040/"
                "global_command_plateau.onnx"
            ).exists()
        ),
        "abi_path_call_defect_exact": (
            '"source_abi": abi(source)' in source_text
            and '"transformed_abi": abi(destination)' in source_text
        ),
        "failure_occurs_after_graph_save_before_contract_result": (
            source_text.index("onnx.save(model, destination)")
            < source_text.index('"source_abi": abi(source)')
        ),
        "zero_simulator_optimizer_behavior_hosted_or_robot_now": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T222B preregistration checks failed: {failed}")
    basis: dict[str, Any] = {
        "schema_version": (
            "open_duck.t222b_abi_helper_recovery_preregistration.v1"
        ),
        "status": "PREREGISTERED_T222B_ABI_HELPER_RECOVERY",
        "question": (
            "Does adapting only the ABI helper call from Path to loaded "
            "ModelProto recover the exact frozen T222 transform and contract?"
        ),
        "frozen_inputs": frozen,
        "source_t222_contract_sha256": source[
            "preregistered_contract_sha256"
        ],
        "recovery": {
            "failure": (
                "run_t136 abi() expects ModelProto; T222 passed WindowsPath"
            ),
            "allowed_change": (
                "in-process adapter loads Path with onnx.load before calling "
                "the immutable shared abi helper"
            ),
            "source_runner_change": False,
            "transform_change": False,
            "cap_change": False,
            "contract_change": False,
            "fresh_output_root": (
                "D:/CodexArtifacts/open-duck-policy/"
                "t222b_abi_helper_recovery_v1"
            ),
            "partial_graph_must_match_regenerated_half_sha256": True,
        },
        "decision_rule": {
            "pass": (
                "RECOVER_T222_AND_EARN_T223_GLOBAL_PLATEAU_"
                "NOMINAL_MATRIX_PREREGISTRATION_ONLY"
            ),
            "fail": "CLOSE_GLOBAL_COMMAND_PLATEAU_WITHOUT_BEHAVIOR",
            "rerun_original_output": False,
            "no_retry_after_recovery": True,
        },
        "checks": checks,
        "failed_checks": failed,
        "execution_now": {
            "onnx_transforms": 0,
            "onnx_inferences": 0,
            "simulator_transitions": 0,
            "optimizer_steps": 0,
            "behavior_cells": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "execute_abi_helper_recovery": True,
            "nominal_matrix_preregistration": False,
            "behavior": False,
            "training": False,
            "colab": False,
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
        "# T222B ABI-helper recovery preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Allowed recovery: Path -> `onnx.load(Path)` -> immutable ABI helper\n"
        "- Transform, cap, equivalence contract, and source runner unchanged\n"
        "- Simulator / optimizer / behavior / hosted / robot: `0/0/0/0/0`\n"
        f"- Contract SHA-256: `{value['preregistered_contract_sha256']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(
        "preregistered_contract_sha256="
        f"{value['preregistered_contract_sha256']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
