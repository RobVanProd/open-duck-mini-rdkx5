#!/usr/bin/env python3
"""Freeze T156B's exact 16-cell positive-COM endpoint matrix."""

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


T156B = ANALYSIS / "t156b_positive_router_gap_midpoint_result.json"
BASIS = ANALYSIS / "t145_conditional_path_negative_endpoint_preregistration.json"
OUTPUT = ANALYSIS / "t157_positive_com_endpoint_preregistration.json"
MARKDOWN = (
    ANALYSIS / "T157_POSITIVE_COM_ENDPOINT_PREREGISTRATION_20260729.md"
)
BUILDER = Path(__file__).resolve()
RUNNER = ROOT / "tools" / "run_t157_positive_com_endpoint.py"
TEST = ROOT / "tests" / "test_t157_positive_com_endpoint.py"


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T157: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T157 preregistration requires clean worktree")
    t156b = json.loads(T156B.read_text(encoding="utf-8"))
    basis = json.loads(BASIS.read_text(encoding="utf-8"))
    policies = [
        {
            "checkpoint_id": f"T156B_THREE_WAY_{label}",
            "step": int(step),
            **t156b["graphs"][step]["transformed"],
        }
        for label, step in (("HALF", "1003520"), ("FINAL", "2007040"))
    ]
    frozen = {
        "builder": BUILDER,
        "runner": RUNNER,
        "test": TEST,
        "t156b_transform": T156B,
        "endpoint_basis": BASIS,
    }
    checks = {
        "t156b_transform_green": (
            t156b["status"]
            == "PASS_T156B_POSITIVE_ROUTER_GAP_MIDPOINT"
            and t156b["failed_checks"] == []
            and t156b["decision"]
            == "EARN_T157_POSITIVE_COM_ENDPOINT_PREREGISTRATION_ONLY"
        ),
        "policies_match_t156b": all(
            {key: item[key] for key in ("path", "bytes", "sha256")}
            == t156b["graphs"][str(item["step"])]["transformed"]
            for item in policies
        ),
        "selected_source_identity_proved": all(
            contract["all_selected_source_outputs_bit_exact"]
            and contract["all_action_feedback_bit_exact"]
            for contract in t156b["contracts"].values()
        ),
        "basis_is_compatible_endpoint_matrix": (
            basis["status"]
            == "PREREGISTERED_T145_CONDITIONAL_PATH_NEGATIVE_ENDPOINT_MATRIX"
            and basis["matrix"]["cells"] == 16
            and basis["commands_x_m_s"] == [0.0, 0.074, 0.077, 0.08]
        ),
        "repository_inputs_present": all(
            Path(item["path"]).is_file()
            for item in basis["repository_inputs"].values()
        ),
        "frozen_inputs_present": all(
            path.is_file() for path in frozen.values()
        ),
        "no_training_colab_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T157 preregistration checks failed: {failed}")
    copied = {
        name: basis[name]
        for name in (
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
            "open_duck.t157_positive_com_endpoint_preregistration.v1"
        ),
        "status": "PREREGISTERED_T157_POSITIVE_COM_ENDPOINT",
        **copied,
        "condition": {
            "condition_index": 8,
            "id": "TORSO_COM_X_POS",
            "override": {
                "torso_com_offset_m": [0.05, 0.0, 0.0]
            },
        },
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
                "EARN_T158_RESUME_SEQUENTIAL_R2_PREREGISTRATION_ONLY"
            ),
            "fail_decision": "CLOSE_POSITIVE_ONLY_EXPERT_FORMULATION",
            "no_retry": True,
            "training_selection_weight": 0,
        },
        "frozen_inputs": {
            name: receipt(path) for name, path in frozen.items()
        },
        "checks": checks,
        "failed_checks": failed,
        "authority": {
            "one_cpu_positive_endpoint_matrix": True,
            "resume_r2_preregistration": False,
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
        "# T157 positive-COM endpoint preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Condition: exact torso COM x = `+0.05 m`\n"
        "- Matrix: `2 checkpoints × 2 fits × 4 commands = 16`\n"
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
