#!/usr/bin/env python3
"""Freeze T194's exact 16-cell Y-negative persistence matrix."""

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


T196 = ANALYSIS / "t196_t194_postexport_composition_result.json"
T196B = ANALYSIS / "t196b_step_zero_binding_recovery_result.json"
T197 = ANALYSIS / "t197_t194_nominal_matrix_result.json"
BASIS = ANALYSIS / "t165_composed_full_r2_preregistration.json"
OUTPUT = ANALYSIS / "t198_t194_targeted_y_negative_preregistration.json"
MARKDOWN = (
    ANALYSIS / "T198_T194_TARGETED_Y_NEGATIVE_PREREGISTRATION_20260730.md"
)
BUILDER = Path(__file__).resolve()
RUNNER = ROOT / "tools" / "run_t198_t194_targeted_y_negative.py"
TEST = ROOT / "tests" / "test_t198_t194_targeted_y_negative.py"


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T198: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T198 preregistration requires clean worktree")

    t196 = json.loads(T196.read_text(encoding="utf-8"))
    t196b = json.loads(T196B.read_text(encoding="utf-8"))
    t197 = json.loads(T197.read_text(encoding="utf-8"))
    basis = json.loads(BASIS.read_text(encoding="utf-8"))
    graph_by_step = {
        int(row["step"]): row["structure"]["transformed"]
        for row in t196["graphs"]
    }
    policies = [
        {
            "checkpoint_id": f"T194_COMPOSED_{label}",
            "step": step,
            **graph_by_step[step],
        }
        for label, step in (
            ("HALF", 1_003_520),
            ("FINAL", 2_007_040),
        )
    ]
    condition = next(
        row for row in basis["conditions"] if row["id"] == "TORSO_COM_Y_NEG"
    )
    checks = {
        "t197_nominal_matrix_green": (
            t197["status"] == "PASS_T197_T194_NOMINAL_MATRIX"
            and t197["condition"]["condition_green"]
            and t197["condition"]["green_cells"] == 16
            and t197["decision"]
            == (
                "EARN_T198_T194_TARGETED_Y_NEGATIVE_MATRIX_"
                "PREREGISTRATION_ONLY"
            )
        ),
        "t196b_composition_recovery_green": (
            t196b["status"] == "PASS_T196B_STEP_ZERO_BINDING_RECOVERY"
            and not t196b["failed_checks"]
        ),
        "t196_all_substantive_composition_checks_green": all(
            passed
            for name, passed in t196["checks"].items()
            if name != "step_zero_model_byte_exact_to_t164_final"
        ),
        "policies_match_t196": (
            len(policies) == 2
            and all(Path(row["path"]).is_file() for row in policies)
        ),
        "basis_is_green_frozen_matrix_contract": (
            basis["status"] == "PREREGISTERED_T165_COMPOSED_FULL_R2"
            and not basis["failed_checks"]
            and basis["commands_x_m_s"] == [0.0, 0.074, 0.077, 0.08]
        ),
        "condition_is_exact_y_negative": (
            condition["condition_index"] == 9
            and condition["override"]
            == {"torso_com_offset_m": [0.0, -0.05, 0.0]}
        ),
        "both_checkpoints_required": True,
        "fresh_cache_required": True,
        "no_training_colab_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T198 preregistration checks failed: {failed}")

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
            "open_duck.t198_t194_targeted_y_negative_preregistration.v1"
        ),
        "status": "PREREGISTERED_T198_T194_TARGETED_Y_NEGATIVE",
        **copied,
        "condition": condition,
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
                "EARN_T199_T194_FULL_R2_PREREGISTRATION_ONLY"
            ),
            "fail_decision": (
                "CLOSE_T194_CORRECTED_DYNAMIC_REFERENCE_SUPPORT_"
                "CONTINUATION"
            ),
            "no_retry": True,
            "training_selection_weight": 0,
        },
        "frozen_inputs": {
            name: receipt(path)
            for name, path in {
                "builder": BUILDER,
                "runner": RUNNER,
                "test": TEST,
                "t196_composition": T196,
                "t196b_recovery": T196B,
                "t197_nominal_result": T197,
                "t165_matrix_basis": BASIS,
            }.items()
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
        "# T198 T194 targeted Y-negative preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Condition: exact torso COM y = `-0.05 m`\n"
        "- Matrix: `2 checkpoints x 2 fits x 4 commands = 16`\n"
        "- Fresh cache; both checkpoints mandatory; no retry\n"
        "- Training / Colab / robot: `0/0/0`\n"
        f"- Contract SHA-256: `{value['preregistered_contract_sha256']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
