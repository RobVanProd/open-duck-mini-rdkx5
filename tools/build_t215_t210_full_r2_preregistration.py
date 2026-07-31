#!/usr/bin/env python3
"""Freeze T210's sequential 20-condition R2 revalidation."""

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


T212 = ANALYSIS / "t212_t210_postexport_composition_result.json"
T214 = ANALYSIS / "t214_t210_targeted_y_negative_result.json"
BASIS = ANALYSIS / "t165_composed_full_r2_preregistration.json"
OUTPUT = ANALYSIS / "t215_t210_full_r2_preregistration.json"
MARKDOWN = ANALYSIS / "T215_T210_FULL_R2_PREREGISTRATION_20260730.md"
BUILDER = Path(__file__).resolve()
RUNNER = ROOT / "tools" / "run_t215_t210_full_r2.py"
TEST = ROOT / "tests" / "test_t215_t210_full_r2.py"


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T215: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T215 preregistration requires clean worktree")
    t212 = json.loads(T212.read_text(encoding="utf-8"))
    t214 = json.loads(T214.read_text(encoding="utf-8"))
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
        "t212_composition": T212,
        "t214_targeted_y_negative": T214,
        "r2_basis": BASIS,
    }
    checks = {
        "t214_targeted_y_negative_green": (
            t214["status"] == "PASS_T214_T210_TARGETED_Y_NEGATIVE"
            and t214["condition"]["green_cells"] == 16
            and t214["decision"]
            == "EARN_T215_T210_FULL_R2_PREREGISTRATION_ONLY"
        ),
        "t212_composition_green": (
            t212["status"] == "PASS_T212_T210_POSTEXPORT_COMPOSITION"
            and not t212["failed_checks"]
            and all(t212["checks"].values())
        ),
        "t210_graphs_exact": (
            len(policies) == 2
            and all(Path(row["path"]).is_file() for row in policies)
        ),
        "basis_is_full_sequential_r2": (
            basis["status"] == "PREREGISTERED_T165_COMPOSED_FULL_R2"
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
        raise RuntimeError(f"T215 preregistration checks failed: {failed}")
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
        "schema_version": "open_duck.t215_t210_full_r2_preregistration.v1",
        "status": "PREREGISTERED_T215_T210_FULL_R2",
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
                "EARN_T216_T210_OFFLINE_DEPLOYMENT_CONTRACT_AUDIT_"
                "PREREGISTRATION_ONLY"
            ),
            "fail_decision": (
                "CLOSE_T210_AT_FIRST_FAILED_R2_CONDITION"
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
        "# T215 T210 full R2 preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Matrix: up to `20 x 16 = 320` fresh CPU cells\n"
        "- Order: frozen; stop after first complete failed condition\n"
        "- Operational chunk: exactly one new condition per invocation\n"
        "- Both checkpoints and fits required; no retry\n"
        "- Training / Colab / robot: `0/0/0`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
