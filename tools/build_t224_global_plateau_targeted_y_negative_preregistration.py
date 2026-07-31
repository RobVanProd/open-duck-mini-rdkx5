#!/usr/bin/env python3
"""Freeze T222B's exact 16-cell Y-negative persistence matrix."""

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


T222B = ANALYSIS / "t222b_abi_helper_recovery_result.json"
T223B = ANALYSIS / "t223b_interrupted_matrix_recovery_result.json"
BASIS = ANALYSIS / "t165_composed_full_r2_preregistration.json"
OUTPUT = (
    ANALYSIS
    / "t224_global_plateau_targeted_y_negative_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "T224_GLOBAL_PLATEAU_TARGETED_Y_NEGATIVE_PREREGISTRATION_20260730.md"
)
BUILDER = Path(__file__).resolve()
RUNNER = ROOT / "tools/run_t224_global_plateau_targeted_y_negative.py"
TEST = ROOT / "tests/test_t224_global_plateau_targeted_y_negative.py"


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T224: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T224 preregistration requires clean worktree")
    t222b = json.loads(T222B.read_text(encoding="utf-8"))
    t223b = json.loads(T223B.read_text(encoding="utf-8"))
    basis = json.loads(BASIS.read_text(encoding="utf-8"))
    graph_by_step = {
        int(row["step"]): row["structure"]["transformed"]
        for row in t222b["graphs"]
    }
    policies = [
        {
            "checkpoint_id": f"T222_GLOBAL_PLATEAU_{label}",
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
        "t223b_nominal_matrix_green": (
            t223b["status"] == "PASS_T223B_INTERRUPTED_MATRIX_RECOVERY"
            and t223b["condition"]["condition_green"]
            and t223b["condition"]["green_cells"] == 16
            and t223b["decision"]
            == (
                "EARN_T224_GLOBAL_PLATEAU_TARGETED_Y_NEGATIVE_"
                "MATRIX_PREREGISTRATION_ONLY"
            )
            and t223b["recovery"]["recovery_exact"]
        ),
        "t222b_transform_green": (
            t222b["status"] == "PASS_T222B_ABI_HELPER_RECOVERY"
            and not t222b["failed_checks"]
        ),
        "policies_match_t222b": (
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
        raise RuntimeError(f"T224 preregistration checks failed: {failed}")
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
            "open_duck.t224_global_plateau_targeted_y_negative_"
            "preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T224_GLOBAL_PLATEAU_TARGETED_Y_NEGATIVE"
        ),
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
                "EARN_T225_GLOBAL_PLATEAU_FULL_R2_"
                "PREREGISTRATION_ONLY"
            ),
            "fail_decision": "CLOSE_GLOBAL_COMMAND_PLATEAU",
            "no_retry": True,
            "training_selection_weight": 0,
        },
        "frozen_inputs": {
            name: receipt(path)
            for name, path in {
                "builder": BUILDER,
                "runner": RUNNER,
                "test": TEST,
                "t222b_transform": T222B,
                "t223b_nominal_result": T223B,
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
        "# T224 global plateau targeted Y-negative preregistration\n\n"
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
