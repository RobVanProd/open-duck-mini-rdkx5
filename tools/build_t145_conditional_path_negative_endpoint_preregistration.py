#!/usr/bin/env python3
"""Freeze T143C's exact 16-cell negative-COM endpoint matrix."""

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


T144 = ANALYSIS / "t144_nominal_identity_reuse_result.json"
T143C = ANALYSIS / "t143c_runner_receipt_recovery_result.json"
BASIS = ANALYSIS / "t103_t100c_negative_endpoint_preregistration.json"
OUTPUT = ANALYSIS / "t145_conditional_path_negative_endpoint_preregistration.json"
MARKDOWN = (
    ANALYSIS
    / "T145_CONDITIONAL_PATH_NEGATIVE_ENDPOINT_PREREGISTRATION_20260729.md"
)
BUILDER = Path(__file__).resolve()
RUNNER = ROOT / "tools" / "run_t145_conditional_path_negative_endpoint.py"
TEST = ROOT / "tests" / "test_t145_conditional_path_negative_endpoint.py"
GRAPH_ROOT = Path(
    "D:/CodexArtifacts/open-duck-policy/t143c_conditional_forward_path_v1"
)


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T145: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T145 preregistration requires clean worktree")
    t144 = json.loads(T144.read_text(encoding="utf-8"))
    t143c = json.loads(T143C.read_text(encoding="utf-8"))
    basis = json.loads(BASIS.read_text(encoding="utf-8"))
    policies = [
        {
            "checkpoint_id": f"T143C_CONDITIONAL_PATH_{label}",
            "step": int(step),
            **receipt(GRAPH_ROOT / step / "conditional_forward_path.onnx"),
        }
        for label, step in (("HALF", "1003520"), ("FINAL", "2007040"))
    ]
    frozen = {
        "builder": BUILDER,
        "runner": RUNNER,
        "test": TEST,
        "t144_nominal_identity": T144,
        "t143c_transform": T143C,
        "negative_basis": BASIS,
    }
    checks = {
        "t144_nominal_identity_green": (
            t144["status"] == "PASS_T144_NOMINAL_IDENTITY_REUSE"
            and t144["failed_checks"] == []
            and t144["decision"]
            == "EARN_T145_CONDITIONAL_PATH_NEGATIVE_ENDPOINT_"
            "PREREGISTRATION_ONLY"
        ),
        "t143c_transform_green": (
            t143c["status"] == "PASS_T143C_CONDITIONAL_FORWARD_PATH_TRANSFORM"
            and t143c["failed_checks"] == []
        ),
        "policies_match_t143c": all(
            {key: item[key] for key in ("path", "bytes", "sha256")}
            == t143c["graphs"][str(item["step"])]["transformed"]
            for item in policies
        ),
        "basis_is_exact_negative_com": (
            basis["status"]
            == "PREREGISTERED_T103_T100C_NEGATIVE_ENDPOINT_MATRIX"
            and basis["condition"]
            == {
                "condition_index": 7,
                "id": "TORSO_COM_X_NEG",
                "override": {"torso_com_offset_m": [-0.05, 0.0, 0.0]},
            }
            and basis["matrix"]["cells"] == 16
        ),
        "repository_inputs_present": all(
            Path(item["path"]).is_file()
            for item in basis["repository_inputs"].values()
        ),
        "frozen_inputs_present": all(path.is_file() for path in frozen.values()),
        "no_training_colab_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T145 preregistration checks failed: {failed}")
    copied = {
        name: basis[name]
        for name in (
            "condition",
            "fits",
            "calibrator",
            "reference_feature_table",
            "playground",
            "commands_x_m_s",
            "seed",
            "support_handoff",
            "behavior_contract",
            "protection_contract",
            "repository_inputs",
        )
    }
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t145_conditional_path_negative_endpoint_"
            "preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T145_CONDITIONAL_PATH_NEGATIVE_ENDPOINT_MATRIX"
        ),
        **copied,
        "policies": policies,
        "matrix": {
            "conditions": 1,
            "checkpoints": 2,
            "fits": 2,
            "commands": 4,
            "cells": 16,
            "both_checkpoints_required": True,
            "checkpoint_cherry_pick": False,
        },
        "decision_rule": {
            "pass_decision": (
                "EARN_T146_CONDITIONAL_PATH_FULL_R2_REVALIDATION_"
                "PREREGISTRATION_ONLY"
            ),
            "fail_decision": "CLOSE_T129_TRAIN_MATCHED_CONDITIONAL_PATH",
            "no_retry": True,
            "training_selection_weight": 0,
        },
        "frozen_inputs": {name: receipt(path) for name, path in frozen.items()},
        "checks": checks,
        "failed_checks": failed,
        "authority": {
            "one_cpu_negative_endpoint_matrix": True,
            "full_r2_preregistration": False,
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
        "# T145 conditional-path negative endpoint preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Condition: exact torso COM x = `-0.05 m`\n"
        "- Matrix: `2 checkpoints x 2 fits x 4 commands = 16`\n"
        "- Negative branch is the exact T129 always-on training path\n"
        "- Both checkpoints mandatory; no retry\n"
        "- Training / Colab / robot: `0/0/0`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
