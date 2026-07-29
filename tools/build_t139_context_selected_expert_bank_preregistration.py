#!/usr/bin/env python3
"""Freeze the exact context-selected expert-bank transform."""

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


T138 = ANALYSIS / "t138_expert_bank_causality_result.json"
T135B = (
    ANALYSIS
    / "t135b_interrupted_calibration_context_router_recovery_result.json"
)
OUTPUT = (
    ANALYSIS / "t139_context_selected_expert_bank_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "T139_CONTEXT_SELECTED_EXPERT_BANK_PREREGISTRATION_20260729.md"
)
BUILDER = Path(__file__).resolve()
RUNNER = (
    ROOT / "tools" / "run_t139_context_selected_expert_bank_transform.py"
)
TEST = ROOT / "tests" / "test_t139_context_selected_expert_bank.py"
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
            raise FileExistsError(f"refusing to overwrite T139: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T139 preregistration requires clean worktree")
    t138 = json.loads(T138.read_text(encoding="utf-8"))
    t135b = json.loads(T135B.read_text(encoding="utf-8"))
    asset = Path(t135b["classifier"]["asset"]["path"])
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
        "t138_result": T138,
        "t135b_result": T135B,
        "router_asset": asset,
    }
    checks = {
        "t138_expert_bank_causality_green": (
            t138["status"] == "PASS_T138_EXPERT_BANK_CAUSALITY_AUDIT"
            and t138["failed_checks"] == []
            and t138["decision"]
            == "EARN_T139_CONTEXT_SELECTED_EXPERT_BANK_TRANSFORM_"
            "PREREGISTRATION_ONLY"
        ),
        "router_asset_exact": (
            receipt(asset) == t135b["classifier"]["asset"]
        ),
        "paired_graphs_present": all(
            path.is_file() for path in (*nominal.values(), *negative.values())
        ),
        "frozen_inputs_present": all(
            path.is_file() for path in frozen_inputs.values()
        ),
        "no_behavior_training_colab_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T139 preregistration checks failed: {failed}")
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t139_context_selected_expert_bank_"
            "preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T139_CONTEXT_SELECTED_EXPERT_BANK_TRANSFORM"
        ),
        "question": (
            "Can calibration context select only the T100C/T129 negative "
            "expert parameter bank while preserving the dynamic gate, "
            "deployment ABI, and every downstream safety transform?"
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
        "transform": {
            "context_nominal": "T100C negative expert weight/bias",
            "context_negative": "T129 negative expert weight/bias",
            "dynamic_negative_com_gate": "unchanged",
            "downstream_deployment_chain": "unchanged",
            "abi": "unchanged 115+14+64+64 to 14+14+64",
        },
        "checks": checks,
        "failed_checks": failed,
        "decision_rule": {
            "pass_decision": (
                "EARN_T140_NOMINAL_IDENTITY_REUSE_"
                "PREREGISTRATION_ONLY"
            ),
            "fail_decision": "CLOSE_CONTEXT_SELECTED_EXPERT_BANK",
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
            "nominal_identity_reuse_preregistration": False,
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
        "# T139 context-selected expert-bank preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Select only expert weight/bias; keep dynamic gate unchanged\n"
        "- Require bit-exact outputs to the selected source graph\n"
        "- Behavior / optimizer / Colab / robot: `0/0/0/0`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
