#!/usr/bin/env python3
"""Freeze recovery of T243's post-save ABI-helper failure."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
from typing import Any

import onnx

from run_t136_static_calibration_router_transform import (
    ANALYSIS,
    ROOT,
    canonical_sha256,
    receipt,
)


T243_PREREG = (
    ANALYSIS
    / "t243_home_negative_low_command_floor_preregistration.json"
)
T243_RESULT = ANALYSIS / "t243_home_negative_low_command_floor_result.json"
PARTIAL = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t243_home_negative_low_command_floor_v1/graphs/1003520/"
    "home_negative_low_command_floor.onnx"
)
OUTPUT = (
    ANALYSIS
    / "t243b_abi_helper_recovery_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "T243B_ABI_HELPER_RECOVERY_PREREGISTRATION_20260731.md"
)
RUNNER = ROOT / "tools/run_t243b_abi_helper_recovery.py"
TEST = ROOT / "tests/test_t243b_abi_helper_recovery.py"
T243_RUNNER = ROOT / "tools/run_t243_home_negative_low_command_floor.py"
ABI_HELPER = ROOT / "tools/run_t136_static_calibration_router_transform.py"


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError("refusing to overwrite T243B preregistration")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T243B preregistration requires clean worktree")

    source = json.loads(T243_PREREG.read_text(encoding="utf-8"))
    runner_text = T243_RUNNER.read_text(encoding="utf-8")
    helper_text = ABI_HELPER.read_text(encoding="utf-8")
    partial_files = sorted(
        path
        for path in PARTIAL.parents[2].rglob("*")
        if path.is_file()
    )
    model = onnx.load(PARTIAL)
    onnx.checker.check_model(model)
    t243_nodes = [
        node.name
        for node in model.graph.node
        if node.name.startswith("t243_")
    ]
    checks = {
        "t243_exact_preregistration": (
            source["status"]
            == "PREREGISTERED_T243_HOME_NEGATIVE_LOW_COMMAND_FLOOR"
            and not source["failed_checks"]
            and source["preregistered_contract_sha256"]
            == "600aaec0e30e0e88f05a9249bbbfd5ebee253df795b7d759f4ee3cad699e0723"
        ),
        "t243_formal_result_absent": not T243_RESULT.exists(),
        "exactly_one_partial_half_graph": (
            partial_files == [PARTIAL]
            and PARTIAL.is_file()
            and PARTIAL.stat().st_size > 0
        ),
        "partial_graph_onnx_checker_green": True,
        "partial_graph_has_all_expected_t243_nodes": (
            t243_nodes
            == [
                "t243_home_negative_router_matmul",
                "t243_home_negative_router_add",
                "t243_home_negative_tail_gate",
                "t243_exact_low_command_gate",
                "t243_home_negative_low_command_gate",
                "t243_map_home_negative_low_command",
            ]
        ),
        "failure_is_exact_path_vs_model_helper_mismatch": (
            '"source_abi": abi(source)' in runner_text
            and '"transformed_abi": abi(destination)' in runner_text
            and "def abi(model: onnx.ModelProto)" in helper_text
            and "model.graph.input" in helper_text
        ),
        "failure_occurs_after_graph_save_before_inference": (
            runner_text.index("onnx.save(model, destination)")
            < runner_text.index('"source_abi": abi(source)')
            < runner_text.index("def random_contract(")
        ),
        "zero_inference_behavior_optimizer_hosted_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T243B preregistration checks failed: {failed}")

    basis: dict[str, Any] = {
        "schema_version": (
            "open_duck.t243b_abi_helper_recovery_preregistration.v1"
        ),
        "status": "PREREGISTERED_T243B_ABI_HELPER_RECOVERY",
        "question": (
            "Can T243 be recovered by reusing its immutable checker-green "
            "half graph, applying the source transform only to the missing "
            "final graph with the ABI helper called on loaded models, and "
            "then executing the originally frozen inference contracts?"
        ),
        "source_t243_contract_sha256": source[
            "preregistered_contract_sha256"
        ],
        "frozen_inputs": {
            "builder": receipt(Path(__file__)),
            "runner": receipt(RUNNER),
            "test": receipt(TEST),
            "t243_preregistration": receipt(T243_PREREG),
            "t243_runner": receipt(T243_RUNNER),
            "abi_helper": receipt(ABI_HELPER),
            "partial_half_graph": receipt(PARTIAL),
        },
        "recovery": {
            "cause": (
                "report-only ABI call passed Path objects to a helper that "
                "accepts loaded ONNX ModelProto objects"
            ),
            "reuse_partial_half_graph": True,
            "overwrite_partial_graph": False,
            "construct_only_missing_final_graph": True,
            "source_transform_logic_changed": False,
            "abi_reporting_call_only_corrected": True,
            "execute_original_random_and_trace_contracts": True,
        },
        "decision_rule": source["decision_rule"],
        "checks": checks,
        "failed_checks": failed,
        "execution_now": {
            "onnx_transforms": 0,
            "onnx_inferences": 0,
            "behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "reuse_partial_half_graph": True,
            "construct_missing_final_and_run_cpu_contract": True,
            "behavior": False,
            "training": False,
            "hosted": False,
            "gate5": False,
            "rdkx5_or_robot": False,
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
        "# T243B ABI-helper recovery preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Reuse: immutable checker-green half graph\n"
        "- Build: only the missing final graph\n"
        "- Correction: report-only Path-to-Model ABI helper call\n"
        "- Behavior/optimizer/hosted/robot: `0/0/0/0`\n"
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
