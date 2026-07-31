#!/usr/bin/env python3
"""Freeze the single T182 alpha=.20 shared-failure cell."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
BUILDER = Path(__file__).resolve()
RUNNER = ROOT / "tools" / "run_t182_shared_failure_single_cell.py"
TEST = ROOT / "tests" / "test_t182_shared_failure_single_cell.py"
T177_PREREG = ANALYSIS / "t177_head_prefix_mean_full_r2_preregistration.json"
T181 = ANALYSIS / "t181_count_weighted_head_interpolation_result.json"
OUTPUT = ANALYSIS / "t182_shared_failure_single_cell_preregistration.json"
MARKDOWN = (
    ANALYSIS / "T182_SHARED_FAILURE_SINGLE_CELL_PREREGISTRATION_20260730.md"
)

sys.path.insert(0, str(ROOT / "tools"))
from run_t27_t23_robustness_matrix import (  # noqa: E402
    canonical_sha256,
    matrix_plan,
    receipt,
    verify_receipt,
)


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"JSON root is not an object: {path}")
    return value


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T182: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T182 preregistration requires a clean worktree")
    t177 = _load_json(T177_PREREG)
    t181 = _load_json(T181)
    if (
        t181.get("status") != "PASS_T181_COUNT_WEIGHTED_HEAD_INTERPOLATION"
        or t181.get("result_sha256")
        != "889db5f9a0295d69741d09c759e7de7fa44f31b0665e283da7f94b8e016f7369"
        or float(t181.get("alpha")) != 0.2
    ):
        raise RuntimeError("T182 T181 identity differs")
    condition = next(
        item
        for item in t177["conditions"]
        if item["id"] == "TORSO_COM_Z_POS"
    )
    policy_graph = next(
        item
        for item in t181["graphs"]
        if item["checkpoint_id"] == "T181_ALPHA_0P2_HALF"
    )["structure"]["candidate"]
    policy = {
        "checkpoint_id": "T181_ALPHA_0P2_HALF",
        "step": 1_003_520,
        **policy_graph,
    }
    fit = next(item for item in t177["fits"] if item["fit_id"] == "p31_34")
    verify_receipt(policy, "policy")
    verify_receipt(fit, "fit")
    plan = matrix_plan(
        [condition], [policy], [fit], [0.077], int(t177["seed"])
    )
    if len(plan) != 1:
        raise RuntimeError("T182 plan is not one cell")
    frozen_paths = {
        "builder": BUILDER,
        "runner": RUNNER,
        "test": TEST,
        "t177_full_r2_preregistration": T177_PREREG,
        "t181_graph_contract": T181,
    }
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t182_shared_failure_single_cell_"
            "preregistration.v1"
        ),
        "status": "PREREGISTERED_T182_SHARED_FAILURE_SINGLE_CELL",
        "repository_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "condition": condition,
        "conditions": [condition],
        "policy": policy,
        "policies": [policy],
        "fit": fit,
        "fits": [fit],
        "commands_x_m_s": [0.077],
        "seed": t177["seed"],
        "calibrator": t177["calibrator"],
        "reference_feature_table": t177["reference_feature_table"],
        "playground": t177["playground"],
        "support_handoff": t177["support_handoff"],
        "behavior_contract": t177["behavior_contract"],
        "protection_contract": t177["protection_contract"],
        "repository_inputs": t177["repository_inputs"],
        "matrix": {
            "cells": 1,
            "plan_sha256": canonical_sha256(plan),
            "fresh_cache": True,
            "checkpoint_id": "T181_ALPHA_0P2_HALF",
            "fit_id": "p31_34",
            "command_x_m_s": 0.077,
            "condition_id": "TORSO_COM_Z_POS",
        },
        "decision_rule": {
            "pass": (
                "EARN_T183_DUAL_CONDITION_32_CELL_PREREGISTRATION_ONLY"
            ),
            "fail": (
                "CLOSE_COUNT_WEIGHTED_ALPHA_0P2_WITHOUT_MORE_BEHAVIOR"
            ),
            "no_retry_or_alternate_alpha": True,
        },
        "frozen_inputs": {
            name: receipt(path) for name, path in frozen_paths.items()
        },
        "execution_now": {
            "new_behavior_cells": 1,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority_after_result": {
            "t183_dual_condition_preregistration": True,
            "t183_execution": False,
            "additional_alpha": False,
            "additional_training": False,
            "colab": False,
            "deployment_contract_audit": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    value["preregistered_contract_sha256"] = canonical_sha256(value)
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T182 shared-failure single-cell preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Candidate: T181 half at alpha `0.20`\n"
        "- Cell: positive-Z / P31-34 / x=`.077`\n"
        "- Reason: both alpha endpoints failed this exact cell\n"
        "- New behavior cells: `1`; no retry or alternate alpha\n"
        "- Optimizer / hosted compute / robot: `0/0/0`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
