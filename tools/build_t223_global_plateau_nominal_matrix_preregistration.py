#!/usr/bin/env python3
"""Freeze T222B's 16-cell nominal/default behavior matrix."""

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
BASIS = ANALYSIS / "t165_composed_full_r2_preregistration.json"
OUTPUT = ANALYSIS / "t223_global_plateau_nominal_matrix_preregistration.json"
MARKDOWN = (
    ANALYSIS
    / "T223_GLOBAL_PLATEAU_NOMINAL_MATRIX_PREREGISTRATION_20260730.md"
)
BUILDER = Path(__file__).resolve()
RUNNER = ROOT / "tools/run_t223_global_plateau_nominal_matrix.py"
TEST = ROOT / "tests/test_t223_global_plateau_nominal_matrix.py"


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T223: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T223 preregistration requires clean worktree")
    t222b = json.loads(T222B.read_text(encoding="utf-8"))
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
        row for row in basis["conditions"] if row["id"] == "FLOOR_FRICTION_HI"
    )
    checks = {
        "t222b_transform_recovery_green": (
            t222b["status"] == "PASS_T222B_ABI_HELPER_RECOVERY"
            and not t222b["failed_checks"]
            and t222b["decision"]
            == (
                "RECOVER_T222_AND_EARN_T223_GLOBAL_PLATEAU_"
                "NOMINAL_MATRIX_PREREGISTRATION_ONLY"
            )
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
        "condition_is_exact_nominal_default": (
            condition["condition_index"] == 2
            and condition["override"] == {"floor_friction": 1.0}
        ),
        "both_checkpoints_required": True,
        "fresh_cache_required": True,
        "no_training_colab_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T223 preregistration checks failed: {failed}")
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
            "open_duck.t223_global_plateau_nominal_matrix_"
            "preregistration.v1"
        ),
        "status": "PREREGISTERED_T223_GLOBAL_PLATEAU_NOMINAL_MATRIX",
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
                "EARN_T224_GLOBAL_PLATEAU_TARGETED_Y_NEGATIVE_"
                "MATRIX_PREREGISTRATION_ONLY"
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
            "one_cpu_nominal_matrix": True,
            "targeted_y_negative": False,
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
        "# T223 global plateau nominal matrix preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Condition: floor friction `1.0` (nominal/default boundary)\n"
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
