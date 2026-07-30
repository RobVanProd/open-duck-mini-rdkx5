#!/usr/bin/env python3
"""Preregister T188B's immutable step-zero binding recovery."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
from typing import Any

import numpy as np
import onnx

from run_t136_static_calibration_router_transform import (
    ANALYSIS,
    ROOT,
    canonical_sha256,
    receipt,
)
import run_t172_t170_postexport_composition as t172


T188_PREREG = ANALYSIS / "t188_t186_postexport_composition_preregistration.json"
T188_RESULT = ANALYSIS / "t188_t186_postexport_composition_result.json"
T187 = ANALYSIS / "t187_t186_recovered_training_validation.json"
OUTPUT = (
    ANALYSIS
    / "t188b_step_zero_binding_recovery_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "T188B_STEP_ZERO_BINDING_RECOVERY_PREREGISTRATION_20260730.md"
)


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def canonical_without(value: dict[str, Any], field: str) -> str:
    basis = dict(value)
    basis.pop(field, None)
    return canonical_sha256(basis)


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError("refusing to overwrite T188B")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T188B preregistration requires clean worktree")
    prereg = load(T188_PREREG)
    result = load(T188_RESULT)
    t187 = load(T187)
    if (
        canonical_without(prereg, "preregistered_contract_sha256")
        != prereg["preregistered_contract_sha256"]
        or canonical_without(result, "result_sha256")
        != result["result_sha256"]
    ):
        raise RuntimeError("T188 identity changed")
    zero_graph = next(
        graph for graph in prereg["graphs"] if int(graph["step"]) == 0
    )
    raw_values = t172.arrays(onnx.load(zero_graph["raw"]["path"]))
    base_values = t172.arrays(onnx.load(zero_graph["base"]["path"]))
    pair_equal = {
        target: bool(np.array_equal(base_values[target], raw_values[source]))
        for source, target in zip(
            t172.SOURCE_NAMES, t172.DESTINATION_NAMES, strict=True
        )
    }
    other_checks = {
        name: passed
        for name, passed in result["checks"].items()
        if name != "step_zero_model_byte_exact_to_t164_final"
    }
    checks = {
        "t188_only_step_zero_expectation_failed": (
            result["status"] == "HOLD_T188_T186_POSTEXPORT_COMPOSITION"
            and result["failed_checks"]
            == ["step_zero_model_byte_exact_to_t164_final"]
            and all(other_checks.values())
        ),
        "t187_step_zero_is_t170_half_exact": (
            t187["status"]
            == "PASS_T187_T186_RECOVERED_TRAINING_VALIDATION"
            and t187["checks"]["step_zero_tree_source_bit_exact"]
            and t187["checks"]["step_zero_raw_onnx_byte_exact"]
            and next(
                row["sha256"] for row in t187["exports"]["onnx"]
                if int(row["step"]) == 0
            )
            == zero_graph["raw"]["sha256"]
        ),
        "step_zero_source_pair_differs_from_t164_destination_pair": (
            not all(pair_equal.values())
        ),
        "all_three_results_bind_only_allowed_pair": all(
            row["structure"]["changed_initializers"]
            == sorted(t172.DESTINATION_NAMES)
            and row["structure"]["expected_changed_initializers"]
            == sorted(t172.DESTINATION_NAMES)
            and row["structure"]["all_source_bindings_exact"]
            for row in result["graphs"]
        ),
        "zero_new_transform_inference_behavior_or_training": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    basis: dict[str, Any] = {
        "schema_version": (
            "open_duck.t188b_step_zero_binding_recovery_"
            "preregistration.v1"
        ),
        "status": "PREREGISTERED_T188B_STEP_ZERO_BINDING_RECOVERY",
        "classification": (
            "CONTRADICTORY_STEP_ZERO_BASE_IDENTITY_EXPECTATION"
        ),
        "frozen_inputs": {
            "builder": receipt(Path(__file__)),
            "runner": receipt(
                ROOT / "tools" / "run_t188b_step_zero_binding_recovery.py"
            ),
            "t188_preregistration": receipt(T188_PREREG),
            "t188_result": receipt(T188_RESULT),
            "t187_validation": receipt(T187),
            "step_zero_raw": zero_graph["raw"],
            "t164_final_base": zero_graph["base"],
        },
        "observed": {
            "step_zero_pair_equal_to_base_before_transform": pair_equal,
            "step_zero_changed_initializers": next(
                row["structure"]["changed_initializers"]
                for row in result["graphs"] if int(row["step"]) == 0
            ),
            "all_other_t188_checks": other_checks,
        },
        "corrected_contract": {
            "all_three_graphs_must_change_exactly": sorted(
                t172.DESTINATION_NAMES
            ),
            "all_three_source_bindings_exact": True,
            "all_nodes_and_other_initializers_exact": True,
            "inactive_routes_and_x0_bit_exact": True,
            "scientific_transform_change": False,
            "new_inference_samples": 0,
        },
        "decision_rule": {
            "pass": (
                "EARN_T189_T186_NOMINAL_BEHAVIOR_MATRIX_"
                "PREREGISTRATION_ONLY"
            ),
            "fail": "HOLD_T186_BEHAVIOR_AND_AUDIT_COMPOSITION",
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
        "# T188B step-zero binding recovery preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Classification: `{value['classification']}`\n"
        f"- Failed checks: `{failed}`\n"
        "- Corrected rule: all three T186 graphs bind exactly the allowed "
        "nominal pair\n"
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
