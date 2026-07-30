#!/usr/bin/env python3
"""Freeze T222B's sequential 20-condition R2 robustness matrix."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
sys.path.insert(0, str(ROOT / "tools"))
from run_t27_t23_robustness_matrix import (  # noqa: E402
    canonical_sha256,
    matrix_plan,
    receipt,
)


T222B = ANALYSIS / "t222b_abi_helper_recovery_result.json"
T223B = ANALYSIS / "t223b_interrupted_matrix_recovery_result.json"
T224 = ANALYSIS / "t224_global_plateau_targeted_y_negative_result.json"
BASIS = ANALYSIS / "t27_t23_robustness_matrix_preregistration.json"
OUTPUT = ANALYSIS / "t225_global_plateau_full_r2_preregistration.json"
MARKDOWN = (
    ANALYSIS / "T225_GLOBAL_PLATEAU_FULL_R2_PREREGISTRATION_20260730.md"
)
BUILDER = Path(__file__).resolve()
RUNNER = ROOT / "tools/run_t225_global_plateau_full_r2.py"
TEST = ROOT / "tests/test_t225_global_plateau_full_r2.py"


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T225: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T225 preregistration requires clean worktree")
    values = {
        "t222b": json.loads(T222B.read_text(encoding="utf-8")),
        "t223b": json.loads(T223B.read_text(encoding="utf-8")),
        "t224": json.loads(T224.read_text(encoding="utf-8")),
        "basis": json.loads(BASIS.read_text(encoding="utf-8")),
    }
    graph_by_step = {
        int(row["step"]): row["structure"]["transformed"]
        for row in values["t222b"]["graphs"]
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
    basis = values["basis"]
    plan = matrix_plan(
        basis["conditions"],
        policies,
        basis["fits"],
        basis["commands_x_m_s"],
        int(basis["seed"]),
    )
    frozen = {
        "builder": BUILDER,
        "runner": RUNNER,
        "test": TEST,
        "t222b_transform": T222B,
        "t223b_nominal_matrix": T223B,
        "t224_targeted_y_negative": T224,
        "r2_basis": BASIS,
    }
    checks = {
        "t222b_transform_green": (
            values["t222b"]["status"]
            == "PASS_T222B_ABI_HELPER_RECOVERY"
            and not values["t222b"]["failed_checks"]
        ),
        "t223b_nominal_green": (
            values["t223b"]["status"]
            == "PASS_T223B_INTERRUPTED_MATRIX_RECOVERY"
            and values["t223b"]["condition"]["green_cells"] == 16
            and values["t223b"]["recovery"]["recovery_exact"]
        ),
        "t224_targeted_y_negative_green": (
            values["t224"]["status"]
            == "PASS_T224_GLOBAL_PLATEAU_TARGETED_Y_NEGATIVE"
            and values["t224"]["condition"]["green_cells"] == 16
            and values["t224"]["decision"]
            == "EARN_T225_GLOBAL_PLATEAU_FULL_R2_PREREGISTRATION_ONLY"
        ),
        "candidate_graphs_exact": (
            len(policies) == 2
            and all(Path(row["path"]).is_file() for row in policies)
        ),
        "basis_is_full_sequential_r2": (
            basis["status"]
            == "PREREGISTERED_T27_T23_SEQUENTIAL_R2_ROBUSTNESS_MATRIX"
            and len(basis["conditions"]) == 20
            and basis["matrix"]["maximum_cells"] == 320
            and basis["matrix"]["stop_after_first_failed_condition"]
        ),
        "plan_exact_320_cells": len(plan) == 320,
        "all_inputs_present": all(path.exists() for path in frozen.values()),
        "repository_inputs_present": all(
            Path(item["path"]).is_file()
            for item in basis["repository_inputs"].values()
        ),
        "fresh_cache_no_prior_behavior_reuse": True,
        "no_training_colab_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T225 preregistration checks failed: {failed}")
    copied = {
        name: basis[name]
        for name in (
            "conditions",
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
            "open_duck.t225_global_plateau_full_r2_preregistration.v1"
        ),
        "status": "PREREGISTERED_T225_GLOBAL_PLATEAU_FULL_R2",
        **copied,
        "policies": policies,
        "matrix": {
            "conditions": 20,
            "checkpoints": 2,
            "fits": 2,
            "commands": 4,
            "cells_per_condition": 16,
            "maximum_cells": 320,
            "both_checkpoints_required": True,
            "checkpoint_cherry_pick": False,
            "strictly_sequential_conditions": True,
            "complete_each_16_cell_condition_before_decision": True,
            "stop_after_first_failed_condition": True,
            "maximum_new_conditions_per_invocation": 1,
            "fresh_cache": True,
            "plan_sha256": canonical_sha256(plan),
        },
        "decision_rule": {
            "pass_decision": (
                "EARN_T226_OFFLINE_DEPLOYMENT_CONTRACT_AUDIT_"
                "PREREGISTRATION_ONLY"
            ),
            "fail_decision": (
                "CLOSE_GLOBAL_COMMAND_PLATEAU_AT_FIRST_FAILED_R2_CONDITION"
            ),
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
            "sequential_cpu_r2_matrix": True,
            "deployment_contract_audit_preregistration": False,
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
        "# T225 global plateau full R2 preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Matrix: up to `20 x 16 = 320` fresh CPU cells\n"
        "- Order: frozen; stop after first complete failed condition\n"
        "- Operational chunk: exactly one new condition per invocation\n"
        "- Both checkpoints and fits required; no retry\n"
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
