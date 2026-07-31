#!/usr/bin/env python3
"""Preregister the bounded positive-router score audit."""

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
T234B = ANALYSIS / "t234b_abi_helper_recovery_result.json"
T238 = ANALYSIS / "t238_home_offset_route_autopsy_result.json"
T239 = ANALYSIS / "t239_x_positive_router_separability_result.json"
OUTPUT = ANALYSIS / "t240_bounded_positive_router_preregistration.json"
MARKDOWN = (
    ANALYSIS / "T240_BOUNDED_POSITIVE_ROUTER_PREREGISTRATION_20260731.md"
)
BUILDER = Path(__file__).resolve()
RUNNER = ROOT / "tools" / "run_t240_bounded_positive_router.py"
TEST = ROOT / "tests" / "test_t240_bounded_positive_router.py"


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T240: {path}")
    t167 = json.loads(T167.read_text(encoding="utf-8"))
    t234b = json.loads(T234B.read_text(encoding="utf-8"))
    t238 = json.loads(T238.read_text(encoding="utf-8"))
    t239 = json.loads(T239.read_text(encoding="utf-8"))
    graphs = [
        {
            "role": row["role"],
            "step": int(row["step"]),
            **receipt(Path(row["structure"]["transformed"]["path"])),
        }
        for row in t234b["graphs"]
    ]
    checks = {
        "t238_proves_ordered_false_positive": (
            t238["status"]
            == "PASS_T238_HOME_OFFSET_FALSE_POSITIVE_X_POSITIVE_ROUTE"
            and t238["classification_pass"] is True
        ),
        "t239_closes_one_sided_linear_family": (
            t239["status"] == "HOLD_T239_X_POSITIVE_ROUTER_SEPARABILITY"
            and t239["decision"]
            == "RETURN_TO_CONTEXT_GEOMETRY_SELECTION_WITHOUT_ROUTER_TRANSFORM"
            and t239["summary"]["combined_margin"] < 0.0
        ),
        "forty_contexts_and_two_exact_graphs": (
            len(t167["cells"]) == 40
            and {row["role"] for row in graphs} == {"half", "final"}
            and all(Path(row["path"]).is_file() for row in graphs)
        ),
        "read_only_no_simulator_optimizer_hosted_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T240 preregistration checks failed: {failed}")

    basis: dict[str, Any] = {
        "schema_version": (
            "open_duck.t240_bounded_positive_router_preregistration.v1"
        ),
        "status": "PREREGISTERED_T240_BOUNDED_POSITIVE_ROUTER",
        "question": (
            "Does the existing positive-router score contain a cross-fit "
            "bounded interval that preserves TORSO_COM_X_POS while excluding "
            "the higher-scoring HOME_JOINT_OFFSET_NEG false positive?"
        ),
        "frozen_inputs": {
            "builder": receipt(BUILDER),
            "runner": receipt(RUNNER),
            "test": receipt(TEST),
            "t167_contexts": receipt(T167),
            "t234b_graphs": receipt(T234B),
            "t238_result": receipt(T238),
            "t239_result": receipt(T239),
        },
        "graphs": graphs,
        "classifier": {
            "score": (
                "float32(calibration_context @ positive_router_coefficient "
                "+ positive_router_intercept)"
            ),
            "lower_bound": "existing score >= float32(0)",
            "training_fit_upper_bound": (
                "float32 midpoint between the X-positive score and the "
                "minimum non-X-positive score that passes the lower bound"
            ),
            "cross_fit_test": (
                "derive on p30/test all twenty p31_34 contexts, then reverse"
            ),
            "combined_upper_bound": (
                "float32 midpoint between maximum X-positive score and "
                "minimum lower-bound false-positive score over all forty "
                "contexts"
            ),
            "selection": "lower_bound AND score <= upper_bound",
            "no_scalar_search": True,
        },
        "decision_rule": {
            "pass_if": {
                "both_graph_router_parameters_bit_exact": True,
                "both_cross_fit_classifiers": "20/20",
                "combined_classifier": "40/40",
                "combined_true_positives": 2,
                "combined_false_positives": 0,
                "positive_lower_and_upper_margins": "strictly positive",
            },
            "pass_decision": (
                "EARN_T241_BOUNDED_POSITIVE_ROUTER_TRANSFORM_"
                "PREREGISTRATION_ONLY"
            ),
            "fail_decision": (
                "RETURN_TO_CONTEXT_GEOMETRY_SELECTION_WITHOUT_BOUNDED_"
                "ROUTER"
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
        "# T240 bounded positive-router preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Geometry: retain the existing lower gate and derive one upper "
        "midpoint from frozen float32 scores\n"
        "- Validation: two cross-fit tests plus the combined `40`-context "
        "population\n"
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
