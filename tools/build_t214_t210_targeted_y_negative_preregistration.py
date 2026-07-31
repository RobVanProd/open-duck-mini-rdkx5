#!/usr/bin/env python3
"""Freeze T210's exact 16-cell Y-negative persistence matrix."""

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


T212 = ANALYSIS / "t212_t210_postexport_composition_result.json"
T213 = ANALYSIS / "t213_t210_nominal_matrix_result.json"
BASIS = ANALYSIS / "t165_composed_full_r2_preregistration.json"
OUTPUT = ANALYSIS / "t214_t210_targeted_y_negative_preregistration.json"
MARKDOWN = (
    ANALYSIS / "T214_T210_TARGETED_Y_NEGATIVE_PREREGISTRATION_20260730.md"
)
BUILDER = Path(__file__).resolve()
RUNNER = ROOT / "tools" / "run_t214_t210_targeted_y_negative.py"
TEST = ROOT / "tests" / "test_t214_t210_targeted_y_negative.py"


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T214: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T214 preregistration requires clean worktree")

    t212 = json.loads(T212.read_text(encoding="utf-8"))
    t213 = json.loads(T213.read_text(encoding="utf-8"))
    basis = json.loads(BASIS.read_text(encoding="utf-8"))
    graph_by_step = {
        int(row["step"]): row["structure"]["transformed"]
        for row in t212["graphs"]
    }
    policies = [
        {
            "checkpoint_id": f"T210_COMPOSED_{label}",
            "step": value,
            **graph_by_step[value],
        }
        for label, value in (
            ("HALF", 1_003_520),
            ("FINAL", 2_007_040),
        )
    ]
    condition = next(
        row for row in basis["conditions"] if row["id"] == "TORSO_COM_Y_NEG"
    )
    checks = {
        "t213_nominal_matrix_green": (
            t213["status"] == "PASS_T213_T210_NOMINAL_MATRIX"
            and t213["condition"]["condition_green"]
            and t213["condition"]["green_cells"] == 16
            and t213["decision"]
            == "EARN_T214_T210_TARGETED_Y_NEGATIVE_MATRIX_"
            "PREREGISTRATION_ONLY"
        ),
        "t212_composition_green": (
            t212["status"] == "PASS_T212_T210_POSTEXPORT_COMPOSITION"
            and not t212["failed_checks"]
        ),
        "policies_match_t212": (
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
        raise RuntimeError(f"T214 preregistration checks failed: {failed}")

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
            "open_duck.t214_t210_targeted_y_negative_preregistration.v1"
        ),
        "status": "PREREGISTERED_T214_T210_TARGETED_Y_NEGATIVE",
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
                "EARN_T215_T210_FULL_R2_PREREGISTRATION_ONLY"
            ),
            "fail_decision": "CLOSE_T210_DUAL_ROLL_COST_CONTINUATION",
            "no_retry": True,
            "training_selection_weight": 0,
        },
        "frozen_inputs": {
            name: receipt(path)
            for name, path in {
                "builder": BUILDER,
                "runner": RUNNER,
                "test": TEST,
                "t212_composition": T212,
                "t213_nominal_result": T213,
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
        "# T214 T210 targeted Y-negative preregistration\n\n"
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
