#!/usr/bin/env python3
"""Preregister the frozen X-positive context-router separability audit."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from run_t136_static_calibration_router_transform import (
    ANALYSIS,
    ROOT,
    canonical_sha256,
    receipt,
)


T167 = ANALYSIS / "t167_calibration_context_separability_result.json"
T238 = ANALYSIS / "t238_home_offset_route_autopsy_result.json"
OUTPUT = (
    ANALYSIS / "t239_x_positive_router_separability_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "T239_X_POSITIVE_ROUTER_SEPARABILITY_PREREGISTRATION_20260731.md"
)
BUILDER = Path(__file__).resolve()
RUNNER = ROOT / "tools" / "run_t239_x_positive_router_separability.py"
TEST = ROOT / "tests" / "test_t239_x_positive_router_separability.py"


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T239: {path}")
    t167 = json.loads(T167.read_text(encoding="utf-8"))
    t238 = json.loads(T238.read_text(encoding="utf-8"))
    conditions = {
        row["condition_id"] for row in t167["cells"]
    }
    checks = {
        "t238_selected_router_separability_only": (
            t238["status"]
            == "PASS_T238_HOME_OFFSET_FALSE_POSITIVE_X_POSITIVE_ROUTE"
            and t238["decision"]
            == "EARN_T239_X_POSITIVE_ROUTER_SEPARABILITY_PREREGISTRATION_ONLY"
            and t238["classification_pass"] is True
        ),
        "forty_frozen_contexts_two_fits_twenty_conditions": (
            len(t167["cells"]) == 40
            and {row["fit_id"] for row in t167["cells"]}
            == {"p30", "p31_34"}
            and len(conditions) == 20
            and all(
                len(
                    [
                        row
                        for row in t167["cells"]
                        if row["condition_id"] == condition
                    ]
                )
                == 2
                for condition in conditions
            )
        ),
        "positive_and_control_present": (
            "TORSO_COM_X_POS" in conditions
            and "ARMATURE_LO" in conditions
            and "HOME_JOINT_OFFSET_NEG" in conditions
        ),
        "frozen_t167_family_available": True,
        "read_only_no_simulator_optimizer_hosted_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T239 preregistration checks failed: {failed}")

    basis: dict[str, Any] = {
        "schema_version": (
            "open_duck.t239_x_positive_router_separability_"
            "preregistration.v1"
        ),
        "status": "PREREGISTERED_T239_X_POSITIVE_ROUTER_SEPARABILITY",
        "question": (
            "Can the already-frozen T167 cross-fit linear family separate "
            "TORSO_COM_X_POS from every other R2 response context, including "
            "HOME_JOINT_OFFSET_NEG, without fitting a scalar?"
        ),
        "frozen_inputs": {
            "builder": receipt(BUILDER),
            "runner": receipt(RUNNER),
            "test": receipt(TEST),
            "t167_contexts": receipt(T167),
            "t238_result": receipt(T238),
        },
        "classifier": {
            "positive_condition": "TORSO_COM_X_POS",
            "control_condition": "ARMATURE_LO",
            "feature": "calibration_context[1,64]",
            "per_fit_direction": (
                "unit(TORSO_COM_X_POS - ARMATURE_LO) on the training fit"
            ),
            "per_fit_threshold": (
                "midpoint of the training-fit positive score and maximum "
                "training-fit non-positive score"
            ),
            "cross_fit_test": (
                "train p30/test all twenty p31_34 contexts, then reverse"
            ),
            "combined_direction": (
                "unit(mean of the two per-fit positive-minus-control unit "
                "vectors)"
            ),
            "combined_threshold": (
                "midpoint of the minimum positive and maximum negative score "
                "over all forty frozen contexts"
            ),
            "no_scalar_search": True,
        },
        "decision_rule": {
            "pass_if": {
                "both_cross_fit_classifiers": "20/20",
                "cross_fit_true_positives": 1,
                "cross_fit_false_positives": 0,
                "both_cross_fit_training_margins_positive": True,
                "combined_classifier": "40/40",
                "combined_true_positives": 2,
                "combined_false_positives": 0,
                "combined_margin_positive": True,
            },
            "pass_decision": (
                "EARN_T240_X_POSITIVE_ROUTER_TRANSFORM_"
                "PREREGISTRATION_ONLY"
            ),
            "fail_decision": (
                "RETURN_TO_CONTEXT_GEOMETRY_SELECTION_WITHOUT_ROUTER_"
                "TRANSFORM"
            ),
            "no_behavior_or_training_authorized": True,
        },
        "checks": checks,
        "failed_checks": failed,
        "execution_now": {
            "context_rows": 0,
            "simulator_steps": 0,
            "behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_sessions": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "execute_saved_context_audit": True,
            "router_transform_preregistration": False,
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
        "# T239 X-positive router separability preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Frozen population: `40` contexts (`20` conditions x `2` fits)\n"
        "- Classifier: unchanged T167 cross-fit linear family; no scalar "
        "search\n"
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
