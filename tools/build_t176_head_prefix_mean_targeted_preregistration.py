#!/usr/bin/env python3
"""Freeze the 16-cell Y-negative matrix for T175 prefix means."""

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


T175 = ANALYSIS / "t175_head_prefix_mean_result.json"
BASIS = ANALYSIS / "t173_t170_targeted_y_negative_preregistration.json"
OUTPUT = ANALYSIS / "t176_head_prefix_mean_targeted_preregistration.json"
MARKDOWN = (
    ANALYSIS / "T176_HEAD_PREFIX_MEAN_TARGETED_PREREGISTRATION_20260729.md"
)
BUILDER = Path(__file__).resolve()
RUNNER = ROOT / "tools" / "run_t176_head_prefix_mean_targeted.py"
TEST = ROOT / "tests" / "test_t176_head_prefix_mean_targeted.py"


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T176: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T176 preregistration requires clean worktree")
    t175 = json.loads(T175.read_text(encoding="utf-8"))
    basis = json.loads(BASIS.read_text(encoding="utf-8"))
    graph_by_id = {
        row["checkpoint_id"]: row["structure"]["transformed"]
        for row in t175["graphs"]
    }
    policies = [
        {
            "checkpoint_id": checkpoint_id,
            "step": step,
            **graph_by_id[checkpoint_id],
        }
        for checkpoint_id, step in (
            ("T175_HEAD_MEAN_HALF", 1_003_520),
            ("T175_HEAD_MEAN_FINAL", 2_007_040),
        )
    ]
    frozen = {
        "builder": BUILDER,
        "runner": RUNNER,
        "test": TEST,
        "t175_transform": T175,
        "t173_matrix_basis": BASIS,
    }
    checks = {
        "t175_transform_green": (
            t175["status"] == "PASS_T175_HEAD_PREFIX_MEAN"
            and not t175["failed_checks"]
            and all(t175["checks"].values())
        ),
        "two_prefix_mean_policies_present": (
            len(policies) == 2
            and all(Path(row["path"]).is_file() for row in policies)
        ),
        "basis_is_exact_y_negative_matrix": (
            basis["status"]
            == "PREREGISTERED_T173_T170_TARGETED_Y_NEGATIVE"
            and basis["condition"]["id"] == "TORSO_COM_Y_NEG"
            and basis["matrix"]["cells"] == 16
        ),
        "both_checkpoints_required": True,
        "fresh_cache_required": True,
        "no_training_colab_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T176 preregistration checks failed: {failed}")
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
            "condition",
        )
    }
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t176_head_prefix_mean_targeted_"
            "preregistration.v1"
        ),
        "status": "PREREGISTERED_T176_HEAD_PREFIX_MEAN_TARGETED",
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
            "fresh_cache": True,
        },
        "decision_rule": {
            "pass_decision": (
                "EARN_T177_HEAD_PREFIX_MEAN_FULL_R2_"
                "PREREGISTRATION_ONLY"
            ),
            "fail_decision": "CLOSE_HEAD_PREFIX_MEAN",
            "no_retry": True,
            "training_selection_weight": 0,
        },
        "frozen_inputs": {
            name: receipt(path) for name, path in frozen.items()
        },
        "checks": checks,
        "failed_checks": failed,
        "execution_now": {
            "behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "one_cpu_y_negative_matrix": True,
            "full_r2": False,
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
        "# T176 head-prefix-mean targeted preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Condition: exact torso COM y = `-0.05 m`\n"
        "- Matrix: `2 checkpoints x 2 fits x 4 commands = 16`\n"
        "- Fresh cache; both checkpoints mandatory; no retry\n"
        "- Training / Colab / robot: `0/0/0`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
