#!/usr/bin/env python3
"""Preregister the T233 upper-Z startup-context separability falsifier."""

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


T167 = ANALYSIS / "t167_calibration_context_separability_result.json"
T225 = ANALYSIS / "t225_global_plateau_full_r2_result.json"
T226B = ANALYSIS / "t226b_t216_support_correction_result.json"
T232 = ANALYSIS / "t232_t228_nominal_failure_autopsy_result.json"
OUTPUT = ANALYSIS / "t233_upper_z_context_separability_preregistration.json"
MARKDOWN = (
    ANALYSIS
    / "T233_UPPER_Z_CONTEXT_SEPARABILITY_PREREGISTRATION_20260730.md"
)
BUILDER = Path(__file__).resolve()
RUNNER = ROOT / "tools" / "run_t233_upper_z_context_separability.py"
TEST = ROOT / "tests" / "test_t233_upper_z_context_separability.py"


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T233: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T233 preregistration requires a clean worktree")

    t167 = json.loads(T167.read_text(encoding="utf-8"))
    t225 = json.loads(T225.read_text(encoding="utf-8"))
    t226b = json.loads(T226B.read_text(encoding="utf-8"))
    t232 = json.loads(T232.read_text(encoding="utf-8"))
    cells = t167["cells"]
    coordinates = {
        (row["condition_id"], row["fit_id"]) for row in cells
    }
    fits = sorted({row["fit_id"] for row in cells})
    conditions = sorted({row["condition_id"] for row in cells})

    checks = {
        "t232_earned_cpu_falsifier_only": (
            t232["status"]
            == (
                "PASS_T232_TRAINING_DISTRIBUTION_IMPROVEMENT_WITH_"
                "NOMINAL_ATTRACTOR_LOSS"
            )
            and t232["decision"]
            == (
                "EARN_T233_SOURCE_ATTRACTOR_PRESERVATION_CPU_"
                "FALSIFIER_PREREGISTRATION_ONLY"
            )
        ),
        "t225_only_upper_z_condition_failed": (
            t225["status"] == "HOLD_T225_GLOBAL_PLATEAU_FULL_R2"
            and t225["conditions"][-1]["condition_id"]
            == "TORSO_COM_Z_POS"
            and t225["conditions"][-1]["green_cells"] == 14
            and t225["summary"]["completed_conditions"] == 12
        ),
        "t226b_corrected_support_question": (
            t226b["status"] == "PASS_T226B_T216_SUPPORT_CORRECTION"
            and t226b["classification"]
            == (
                "LOW_COMMAND_BOUNDARY_NOT_DETERMINISTICALLY_COVERED_"
                "WITH_EXACT_UPPER_Z_STRATUM_AND_LATE_ABI_FEASIBILITY"
            )
        ),
        "forty_frozen_contexts_exact": (
            len(cells) == 40
            and len(fits) == 2
            and len(conditions) == 20
            and len(coordinates) == 40
            and all(
                len(row["context"]) == 64
                and all(
                    isinstance(value, (int, float))
                    for value in row["context"]
                )
                for row in cells
            )
        ),
        "positive_and_control_present_both_fits": all(
            (condition, fit) in coordinates
            for condition in ("TORSO_COM_Z_POS", "FLOOR_FRICTION_HI")
            for fit in fits
        ),
        "reuse_contexts_no_new_calibration_or_behavior": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, value in checks.items() if not value)
    if failed:
        raise RuntimeError(f"T233 preregistration checks failed: {failed}")

    basis: dict[str, Any] = {
        "schema_version": (
            "open_duck.t233_upper_z_context_separability_"
            "preregistration.v1"
        ),
        "status": "PREREGISTERED_T233_UPPER_Z_CONTEXT_SEPARABILITY",
        "question": (
            "Can the already captured automatic 250-tick startup calibration "
            "context isolate TORSO_COM_Z_POS from every other frozen R2 "
            "condition across both actuator fits, so a future correction can "
            "remain bit-exactly off on nominal walking?"
        ),
        "frozen_inputs": {
            name: receipt(path)
            for name, path in {
                "builder": BUILDER,
                "runner": RUNNER,
                "test": TEST,
                "t167_contexts": T167,
                "t225_result": T225,
                "t226b_result": T226B,
                "t232_result": T232,
            }.items()
        },
        "population": {
            "cells": 40,
            "conditions": 20,
            "fits": fits,
            "context_dimensions": 64,
            "positive_condition": "TORSO_COM_Z_POS",
            "control_condition": "FLOOR_FRICTION_HI",
            "source": (
                "exact frozen T167 calibrator outputs; no new simulator calls"
            ),
        },
        "classifier": {
            "family": "fixed centroid-direction threshold",
            "direction": (
                "unit(context_positive - context_control) on the training fit"
            ),
            "threshold": (
                "midpoint between positive training score and maximum "
                "non-positive training score"
            ),
            "cross_fit": [
                {"train": fits[0], "test": fits[1]},
                {"train": fits[1], "test": fits[0]},
            ],
            "combined": (
                "unit mean of the two per-fit unit directions; threshold "
                "midpoint of minimum positive and maximum negative scores"
            ),
            "no_model_or_hyperparameter_search": True,
        },
        "decision_rule": {
            "pass_if": {
                "both_cross_fit_tests": "20/20",
                "each_cross_fit_true_positives": 1,
                "each_cross_fit_false_positives": 0,
                "each_training_margin": ">0",
                "combined": "40/40",
                "combined_true_positives": 2,
                "combined_false_positives": 0,
                "combined_margin": ">0",
            },
            "pass_decision": (
                "EARN_T234_UPPER_Z_EXACT_ROUTE_CPU_CONTRACT_"
                "PREREGISTRATION_ONLY"
            ),
            "fail_decision": (
                "CLOSE_STATIC_STARTUP_CONTEXT_ROUTING_FOR_UPPER_Z_AND_"
                "RETURN_TO_DYNAMIC_PRESERVATION"
            ),
            "no_behavior_or_training": True,
            "no_hosted_run_authorized": True,
        },
        "checks": checks,
        "failed_checks": failed,
        "execution_now": {
            "context_rows": 0,
            "simulator_calls": 0,
            "behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_sessions": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "execute_context_math": True,
            "route_cpu_contract_preregistration": False,
            "behavior": False,
            "training": False,
            "hosted": False,
            "gate5": False,
            "robot_or_rdk": False,
        },
    }
    value = {
        **basis,
        "preregistered_contract_sha256": canonical_sha256(basis),
    }
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T233 upper-Z context separability preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Input: 40 already frozen automatic calibration contexts\n"
        "- Positive: `TORSO_COM_Z_POS`; control: `FLOOR_FRICTION_HI`\n"
        "- Simulator/behavior/training/hosted/robot: `0/0/0/0/0`\n"
        f"- Contract SHA-256: `{value['preregistered_contract_sha256']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
