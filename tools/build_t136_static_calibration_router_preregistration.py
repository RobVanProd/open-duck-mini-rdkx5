#!/usr/bin/env python3
"""Freeze the T136 static calibration-router graph transform."""

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


T135B = (
    ANALYSIS
    / "t135b_interrupted_calibration_context_router_recovery_result.json"
)
T131 = ANALYSIS / "t131_t129_postexport_result.json"
OUTPUT = ANALYSIS / "t136_static_calibration_router_preregistration.json"
MARKDOWN = (
    ANALYSIS / "T136_STATIC_CALIBRATION_ROUTER_PREREGISTRATION_20260729.md"
)
BUILDER = Path(__file__).resolve()
RUNNER = ROOT / "tools" / "run_t136_static_calibration_router_transform.py"
TEST = ROOT / "tests" / "test_t136_static_calibration_router.py"
T131_ROOT = Path(
    "D:/CodexArtifacts/open-duck-policy/t131_t129_deployments_v1"
)
STEPS = ("0", "1003520", "2007040")


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T136: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T136 preregistration requires clean worktree")
    t135b = json.loads(T135B.read_text(encoding="utf-8"))
    t131 = json.loads(T131.read_text(encoding="utf-8"))
    asset = Path(t135b["classifier"]["asset"]["path"])
    source_graphs = {
        step: T131_ROOT / step / "deployment" / "action_margin.onnx"
        for step in STEPS
    }
    frozen_inputs = {
        "builder": BUILDER,
        "runner": RUNNER,
        "test": TEST,
        "t135b_result": T135B,
        "t131_result": T131,
        "router_asset": asset,
    }
    checks = {
        "t135b_static_router_screen_green": (
            t135b["status"]
            == "PASS_T135B_INTERRUPTED_CALIBRATION_CONTEXT_ROUTER_RECOVERY"
            and t135b["failed_checks"] == []
            and t135b["decision"]
            == "EARN_T136_STATIC_CALIBRATION_ROUTER_TRANSFORM_"
            "PREREGISTRATION_ONLY"
        ),
        "t131_source_chain_green": (
            t131["status"]
            == "PASS_T131_T129_HARD_GATE_POSTEXPORT_TRANSFORM"
            and t131["failed_checks"] == []
        ),
        "router_asset_receipt_exact": (
            receipt(asset) == t135b["classifier"]["asset"]
        ),
        "three_source_graphs_present": all(
            path.is_file() for path in source_graphs.values()
        ),
        "frozen_inputs_present": all(
            path.is_file() for path in frozen_inputs.values()
        ),
        "no_behavior_training_colab_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T136 preregistration checks failed: {failed}")
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t136_static_calibration_router_"
            "preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T136_STATIC_CALIBRATION_ROUTER_TRANSFORM"
        ),
        "question": (
            "Can the frozen calibration-context classifier replace only "
            "the conditional expert's drifting per-tick gate while "
            "preserving the complete deployment ABI and safety chain?"
        ),
        "source_graphs": {
            step: receipt(path) for step, path in source_graphs.items()
        },
        "frozen_inputs": {
            name: receipt(path) for name, path in frozen_inputs.items()
        },
        "transform": {
            "insert_before": (
                "Where(negative_com_gate, negative_adapter_location, "
                "zero_adapter_location)"
            ),
            "replacement_gate": (
                "MatMul(calibration_context, coefficient) + intercept >= 0"
            ),
            "dynamic_gate_retained_diagnostic_only": True,
            "conditional_expert_and_all_downstream_nodes_unchanged": True,
        },
        "checks": checks,
        "failed_checks": failed,
        "decision_rule": {
            "pass_decision": (
                "EARN_T137_STATIC_ROUTER_NOMINAL_MATRIX_"
                "PREREGISTRATION_ONLY"
            ),
            "fail_decision": "CLOSE_STATIC_CALIBRATION_ROUTER_TRANSFORM",
        },
        "execution_now": {
            "graphs_transformed": 0,
            "formal_behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "one_cpu_graph_transform": True,
            "nominal_matrix_preregistration": False,
            "behavior_evaluation": False,
            "negative_matrix": False,
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
        "# T136 static calibration-router preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Transform all three T131 graphs; evaluate no behavior\n"
        "- Replace only the conditional expert gate\n"
        "- Preserve ABI, safety chain, and x=0 exact-zero path\n"
        "- Optimizer / Colab / robot: `0/0/0`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
