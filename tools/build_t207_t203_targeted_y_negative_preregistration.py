#!/usr/bin/env python3
"""Freeze T203's exact 16-cell Y-negative persistence matrix."""

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


T205 = ANALYSIS / "t205_t203_postexport_composition_result.json"
T205B = ANALYSIS / "t205b_output_sensitivity_recovery_result.json"
T206 = ANALYSIS / "t206_t203_nominal_matrix_result.json"
BASIS = ANALYSIS / "t165_composed_full_r2_preregistration.json"
OUTPUT = ANALYSIS / "t207_t203_targeted_y_negative_preregistration.json"
MARKDOWN = (
    ANALYSIS / "T207_T203_TARGETED_Y_NEGATIVE_PREREGISTRATION_20260730.md"
)
BUILDER = Path(__file__).resolve()
RUNNER = ROOT / "tools" / "run_t207_t203_targeted_y_negative.py"
TEST = ROOT / "tests" / "test_t207_t203_targeted_y_negative.py"
NON_REQUIRED_DIAGNOSTIC = (
    "both_y_negative_fits_exercise_changed_moving_action"
)


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T207: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T207 preregistration requires clean worktree")

    t205 = json.loads(T205.read_text(encoding="utf-8"))
    t205b = json.loads(T205B.read_text(encoding="utf-8"))
    t206 = json.loads(T206.read_text(encoding="utf-8"))
    basis = json.loads(BASIS.read_text(encoding="utf-8"))
    graph_by_step = {
        int(row["step"]): row["structure"]["transformed"]
        for row in t205["graphs"]
    }
    policies = [
        {
            "checkpoint_id": f"T203_COMPOSED_{label}",
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
        "t206_nominal_matrix_green": (
            t206["status"] == "PASS_T206_T203_NOMINAL_MATRIX"
            and t206["condition"]["condition_green"]
            and t206["condition"]["green_cells"] == 16
            and t206["decision"]
            == (
                "EARN_T207_T203_TARGETED_Y_NEGATIVE_MATRIX_"
                "PREREGISTRATION_ONLY"
            )
        ),
        "t205b_composition_recovery_green": (
            t205b["status"]
            == "PASS_T205B_OUTPUT_SENSITIVITY_RECOVERY"
            and not t205b["failed_checks"]
        ),
        "t205_all_substantive_composition_checks_green": all(
            passed
            for name, passed in t205["checks"].items()
            if name != NON_REQUIRED_DIAGNOSTIC
        ),
        "policies_match_t205": (
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
        raise RuntimeError(f"T207 preregistration checks failed: {failed}")

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
            "open_duck.t207_t203_targeted_y_negative_preregistration.v1"
        ),
        "status": "PREREGISTERED_T207_T203_TARGETED_Y_NEGATIVE",
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
                "EARN_T208_T203_FULL_R2_PREREGISTRATION_ONLY"
            ),
            "fail_decision": (
                "CLOSE_T203_PREDICTED_ROLL_RISK_CONTINUATION"
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
                "t205_composition": T205,
                "t205b_recovery": T205B,
                "t206_nominal_result": T206,
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
        "# T207 T203 targeted Y-negative preregistration\n\n"
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
