#!/usr/bin/env python3
"""Freeze calibration-conditional T129 forward-path correction."""

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


T142 = ANALYSIS / "t142_t129_forward_path_mismatch_result.json"
T135B = (
    ANALYSIS
    / "t135b_interrupted_calibration_context_router_recovery_result.json"
)
OUTPUT = ANALYSIS / "t143_conditional_forward_path_preregistration.json"
MARKDOWN = (
    ANALYSIS
    / "T143_CONDITIONAL_FORWARD_PATH_PREREGISTRATION_20260729.md"
)
BUILDER = Path(__file__).resolve()
RUNNER = ROOT / "tools" / "run_t143_conditional_forward_path_transform.py"
TEST = ROOT / "tests" / "test_t143_conditional_forward_path.py"
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
            raise FileExistsError(f"refusing to overwrite T143: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T143 preregistration requires clean worktree")
    t142 = json.loads(T142.read_text(encoding="utf-8"))
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
        "t142_result": T142,
        "t135b_result": T135B,
        "router_asset": asset,
    }
    checks = {
        "t142_forward_path_mismatch_green": (
            t142["status"]
            == "PASS_T142_T129_FORWARD_PATH_MISMATCH_AUDIT"
            and t142["failed_checks"] == []
            and t142["decision"]
            == "EARN_T143_CALIBRATION_CONDITIONAL_FORWARD_PATH_"
            "TRANSFORM_PREREGISTRATION_ONLY"
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
        raise RuntimeError(f"T143 preregistration checks failed: {failed}")
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t143_conditional_forward_path_"
            "preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T143_CONDITIONAL_FORWARD_PATH_TRANSFORM"
        ),
        "question": (
            "Can calibration preserve T100C's dynamic-gated nominal path "
            "while using T129's exact always-on training path only for "
            "the negative-COM condition?"
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
            "nominal_context": "T100C expert behind original dynamic gate",
            "negative_context": "T129 expert always on",
            "calibration_context": "existing automatic 64-D response",
            "downstream_deployment_chain": "unchanged",
            "abi": "unchanged 115+14+64+64 to 14+14+64",
        },
        "checks": checks,
        "failed_checks": failed,
        "decision_rule": {
            "pass_decision": (
                "EARN_T144_CONDITIONAL_PATH_NOMINAL_IDENTITY_"
                "REUSE_PREREGISTRATION_ONLY"
            ),
            "fail_decision": "CLOSE_CONDITIONAL_FORWARD_PATH",
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
            "negative_endpoint_preregistration": False,
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
        "# T143 conditional forward-path preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Nominal dynamic gate; negative expert always on\n"
        "- Require bit-exact outputs to each selected source path\n"
        "- Behavior / optimizer / Colab / robot: `0/0/0/0`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
