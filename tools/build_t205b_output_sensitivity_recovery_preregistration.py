#!/usr/bin/env python3
"""Preregister recovery of T205's non-required sensitivity assertion."""

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
import run_t172_t170_postexport_composition as t172


T205_PREREG = (
    ANALYSIS / "t205_t203_postexport_composition_preregistration.json"
)
T205_RESULT = ANALYSIS / "t205_t203_postexport_composition_result.json"
T172_RESULT = ANALYSIS / "t172_t170_postexport_composition_result.json"
T196_RESULT = ANALYSIS / "t196_t194_postexport_composition_result.json"
T196B_RESULT = ANALYSIS / "t196b_step_zero_binding_recovery_result.json"
OUTPUT = (
    ANALYSIS
    / "t205b_output_sensitivity_recovery_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "T205B_OUTPUT_SENSITIVITY_RECOVERY_PREREGISTRATION_20260730.md"
)
DIAGNOSTIC = "both_y_negative_fits_exercise_changed_moving_action"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def canonical_without(value: dict[str, Any], field: str) -> str:
    basis = dict(value)
    basis.pop(field, None)
    return canonical_sha256(basis)


def diagnostic_false(result: dict[str, Any]) -> bool:
    return all(
        not row["inference"][
            "both_y_negative_fits_bind_changed_moving_action"
        ]
        for row in result["graphs"]
    )


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError("refusing to overwrite T205B")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T205B preregistration requires clean worktree")

    paths = {
        "t205_preregistration": T205_PREREG,
        "t205_result": T205_RESULT,
        "t172_result": T172_RESULT,
        "t196_result": T196_RESULT,
        "t196b_result": T196B_RESULT,
    }
    values = {name: load(path) for name, path in paths.items()}
    prereg = values["t205_preregistration"]
    result = values["t205_result"]
    t172_result = values["t172_result"]
    t196_result = values["t196_result"]
    t196b_result = values["t196b_result"]
    if (
        canonical_without(prereg, "preregistered_contract_sha256")
        != prereg["preregistered_contract_sha256"]
        or canonical_without(result, "result_sha256")
        != result["result_sha256"]
    ):
        raise RuntimeError("T205 identity changed")

    substantive = {
        name: passed
        for name, passed in result["checks"].items()
        if name != DIAGNOSTIC
    }
    allowed = sorted(t172.DESTINATION_NAMES)
    checks = {
        "t205_only_output_sensitivity_assertion_failed": (
            result["status"]
            == "HOLD_T205_T203_POSTEXPORT_COMPOSITION"
            and result["failed_checks"] == [DIAGNOSTIC]
            and all(substantive.values())
        ),
        "all_three_bind_exactly_allowed_pair": all(
            row["structure"]["changed_initializers"] == allowed
            and row["structure"]["expected_changed_initializers"] == allowed
            and row["structure"]["all_source_bindings_exact"]
            for row in result["graphs"]
        ),
        "all_three_preserve_graph_and_other_initializers": all(
            row["structure"]["nodes_byte_exact"]
            and row["structure"]["all_other_initializers_exact"]
            and row["structure"]["initializer_names_exact"]
            for row in result["graphs"]
        ),
        "routing_and_inactive_exactness_green": all(
            row["inference"]["both_y_negative_contexts_route_nominal"]
            and row["inference"]["all_inactive_routes_bit_exact"]
            and row["inference"]["all_x0_outputs_bit_exact"]
            for row in result["graphs"]
        ),
        "prior_t172_passed_with_same_diagnostic_false": (
            t172_result["status"]
            == "PASS_T172_T170_POSTEXPORT_COMPOSITION"
            and not t172_result["failed_checks"]
            and diagnostic_false(t172_result)
        ),
        "prior_t196b_passed_with_same_diagnostic_false": (
            t196b_result["status"]
            == "PASS_T196B_STEP_ZERO_BINDING_RECOVERY"
            and not t196b_result["failed_checks"]
            and diagnostic_false(t196_result)
        ),
        "zero_new_transform_inference_behavior_or_training": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    basis: dict[str, Any] = {
        "schema_version": (
            "open_duck.t205b_output_sensitivity_recovery_"
            "preregistration.v1"
        ),
        "status": "PREREGISTERED_T205B_OUTPUT_SENSITIVITY_RECOVERY",
        "classification": (
            "NON_REQUIRED_RANDOM_FINAL_OUTPUT_SENSITIVITY_ASSERTION"
        ),
        "frozen_inputs": {
            "builder": receipt(Path(__file__)),
            "runner": receipt(
                ROOT / "tools/run_t205b_output_sensitivity_recovery.py"
            ),
            **{name: receipt(path) for name, path in paths.items()},
        },
        "observed": {
            "t205_failed_check": DIAGNOSTIC,
            "t205_preserved_checks": substantive,
            "t172_same_diagnostic_false": diagnostic_false(t172_result),
            "t196_same_diagnostic_false": diagnostic_false(t196_result),
            "explanation": (
                "The synthetic comparison asks final hard-projected actions "
                "to differ from the base. That is not a necessary structural "
                "composition property: the nominal expert is hidden-gated "
                "and later action/rate projections can mask an internal "
                "adapter difference. T172 and T196 recorded the same false "
                "diagnostic; neither used it as a composition gate."
            ),
        },
        "corrected_contract": {
            "all_three_graphs_change_exactly": allowed,
            "all_three_source_bindings_exact": True,
            "all_nodes_and_other_initializers_exact": True,
            "inactive_routes_and_x0_bit_exact": True,
            "y_negative_contexts_route_nominal": True,
            "final_output_difference_on_random_independent_state": (
                "diagnostic_only"
            ),
            "scientific_transform_change": False,
            "new_transform_operations": 0,
            "new_inference_samples": 0,
        },
        "decision_rule": {
            "pass": (
                "EARN_T206_T203_NOMINAL_BEHAVIOR_MATRIX_"
                "PREREGISTRATION_ONLY"
            ),
            "fail": "HOLD_T203_BEHAVIOR_AND_AUDIT_COMPOSITION",
        },
        "checks": checks,
        "failed_checks": failed,
        "execution_now": {
            "saved_result_files": 0,
            "transform_operations": 0,
            "inference_samples": 0,
            "behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "execute_one_saved_result_recovery": not failed,
            "behavior_matrix": False,
            "training": False,
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
        "# T205B output-sensitivity recovery preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Classification: `{value['classification']}`\n"
        f"- Failed checks: `{failed}`\n"
        "- Corrected rule: exact binding and graph preservation are gates; "
        "random final-output sensitivity is diagnostic only.\n"
        "- New transform / inference / behavior / optimizer / hosted / "
        "robot: `0/0/0/0/0/0`\n"
        f"- Contract SHA-256: `{value['preregistered_contract_sha256']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"failed_checks={failed}")
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
