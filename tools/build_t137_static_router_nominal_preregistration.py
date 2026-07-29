#!/usr/bin/env python3
"""Freeze the T136 static-router 16-cell nominal persistence matrix."""

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


T136B = ANALYSIS / "t136b_x0_coordinate_recovery_result.json"
T136 = ANALYSIS / "t136_static_calibration_router_result.json"
BASIS = ANALYSIS / "t132_t129_nominal_preregistration.json"
OUTPUT = ANALYSIS / "t137_static_router_nominal_preregistration.json"
MARKDOWN = (
    ANALYSIS / "T137_STATIC_ROUTER_NOMINAL_PREREGISTRATION_20260729.md"
)
BUILDER = Path(__file__).resolve()
RUNNER = ROOT / "tools" / "run_t137_static_router_nominal.py"
TEST = ROOT / "tests" / "test_t137_static_router_nominal.py"
GRAPH_ROOT = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t136_t129_static_calibration_router_v1"
)


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T137: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T137 preregistration requires clean worktree")
    t136b = json.loads(T136B.read_text(encoding="utf-8"))
    t136 = json.loads(T136.read_text(encoding="utf-8"))
    basis = json.loads(BASIS.read_text(encoding="utf-8"))
    policies = [
        {
            "checkpoint_id": f"T136_STATIC_ROUTER_{label}",
            "step": int(step),
            **receipt(
                GRAPH_ROOT / step / "static_calibration_router.onnx"
            ),
        }
        for label, step in (
            ("HALF", "1003520"),
            ("FINAL", "2007040"),
        )
    ]
    frozen_inputs = {
        "builder": BUILDER,
        "runner": RUNNER,
        "test": TEST,
        "t136b_recovery": T136B,
        "t136_transform": T136,
        "nominal_basis": BASIS,
    }
    checks = {
        "t136_recovered": (
            t136b["status"] == "PASS_T136B_X0_COORDINATE_RECOVERY"
            and t136b["failed_checks"] == []
            and t136b["decision"]
            == "RECOVER_T136_AND_EARN_T137_STATIC_ROUTER_NOMINAL_"
            "MATRIX_PREREGISTRATION_ONLY"
        ),
        "t136_all_non_x0_checks_green": all(
            passed
            for name, passed in t136["checks"].items()
            if name != "all_x0_paths_exact_zero"
        ),
        "policies_present": all(
            Path(item["path"]).is_file() for item in policies
        ),
        "policies_match_t136_result": all(
            {
                key: item[key]
                for key in ("path", "bytes", "sha256")
            }
            == t136["graphs"][str(item["step"])]["transformed"]
            for item in policies
        ),
        "basis_exact": (
            basis["status"] == "PREREGISTERED_T132_T129_NOMINAL_MATRIX"
            and basis["matrix"]["cells"] == 16
            and basis["matrix"]["both_checkpoints_required"]
        ),
        "frozen_inputs_present": all(
            path.is_file() for path in frozen_inputs.values()
        ),
        "no_training_colab_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T137 preregistration checks failed: {failed}")
    copied = {
        name: basis[name]
        for name in (
            "conditions",
            "commands_x_m_s",
            "seed",
            "fits",
            "calibrator",
            "reference_feature_table",
            "playground",
            "support_handoff",
            "behavior_contract",
            "protection_contract",
            "repository_inputs",
        )
    }
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t137_static_router_nominal_preregistration.v1"
        ),
        "status": "PREREGISTERED_T137_STATIC_ROUTER_NOMINAL_MATRIX",
        **copied,
        "policies": policies,
        "matrix": {
            "cells": 16,
            "both_checkpoints_required": True,
            "no_checkpoint_selection": True,
            "condition": "nominal",
        },
        "decision_rule": {
            "pass_decision": (
                "EARN_T138_STATIC_ROUTER_NEGATIVE_ENDPOINT_"
                "PREREGISTRATION_ONLY"
            ),
            "fail_decision": "CLOSE_STATIC_ROUTER_ZERO_TRAINING_REPAIR",
            "no_retry": True,
            "training_selection_weight": 0,
        },
        "frozen_inputs": {
            name: receipt(path) for name, path in frozen_inputs.items()
        },
        "checks": checks,
        "failed_checks": failed,
        "authority": {
            "one_cpu_nominal_matrix": True,
            "negative_endpoint_preregistration": False,
            "training": False,
            "colab": False,
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
        "# T137 static-router nominal preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Matrix: `2 checkpoints x 2 fits x 4 commands = 16`\n"
        "- Both checkpoints mandatory; no selection or retry\n"
        "- Training / Colab / robot: `0/0/0`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
