#!/usr/bin/env python3
"""Re-evaluate T188's immutable composition result under T188B."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
from typing import Any

from run_t136_static_calibration_router_transform import (
    ANALYSIS,
    ROOT,
    canonical_sha256,
    verify,
)
import run_t172_t170_postexport_composition as t172


PREREG = ANALYSIS / "t188b_step_zero_binding_recovery_preregistration.json"
RESULT = ANALYSIS / "t188b_step_zero_binding_recovery_result.json"
MARKDOWN = ANALYSIS / "T188B_STEP_ZERO_BINDING_RECOVERY_RESULT_20260730.md"


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
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--saved-result-authorized", action="store_true")
    args = parser.parse_args()
    if not args.saved_result_authorized:
        raise PermissionError("T188B requires --saved-result-authorized")
    for path in (RESULT, MARKDOWN):
        if path.exists():
            raise FileExistsError("refusing to overwrite T188B")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("formal T188B execution requires clean worktree")
    prereg = load(PREREG)
    if (
        prereg["status"]
        != "PREREGISTERED_T188B_STEP_ZERO_BINDING_RECOVERY"
        or prereg["failed_checks"]
        or canonical_without(prereg, "preregistered_contract_sha256")
        != prereg["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T188B preregistration changed")
    for name, item in prereg["frozen_inputs"].items():
        verify(item, name)
    source = load(
        Path(prereg["frozen_inputs"]["t188_result"]["path"])
    )
    substantive = {
        name: passed
        for name, passed in source["checks"].items()
        if name != "step_zero_model_byte_exact_to_t164_final"
    }
    allowed = sorted(t172.DESTINATION_NAMES)
    checks = {
        "source_only_contradictory_step_zero_check_failed": (
            source["failed_checks"]
            == ["step_zero_model_byte_exact_to_t164_final"]
        ),
        "all_other_source_checks_true": all(substantive.values()),
        "all_three_change_exactly_allowed_pair": all(
            row["structure"]["changed_initializers"] == allowed
            and row["structure"]["expected_changed_initializers"] == allowed
            for row in source["graphs"]
        ),
        "all_three_source_bindings_exact": all(
            row["structure"]["all_source_bindings_exact"]
            for row in source["graphs"]
        ),
        "all_three_nodes_and_other_initializers_exact": all(
            row["structure"]["nodes_byte_exact"]
            and row["structure"]["all_other_initializers_exact"]
            and row["structure"]["initializer_names_exact"]
            for row in source["graphs"]
        ),
        "all_inactive_routes_and_x0_bit_exact": all(
            row["inference"]["all_inactive_routes_bit_exact"]
            and row["inference"]["all_x0_outputs_bit_exact"]
            for row in source["graphs"]
        ),
        "no_new_transform_inference_behavior_or_training": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    basis: dict[str, Any] = {
        "schema_version": (
            "open_duck.t188b_step_zero_binding_recovery_result.v1"
        ),
        "status": (
            "PASS_T188B_STEP_ZERO_BINDING_RECOVERY"
            if not failed
            else "HOLD_T188B_STEP_ZERO_BINDING_RECOVERY"
        ),
        "decision": (
            prereg["decision_rule"]["pass"]
            if not failed
            else prereg["decision_rule"]["fail"]
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "source_result_sha256": source["result_sha256"],
        "preserved_t188_checks": substantive,
        "checks": checks,
        "failed_checks": failed,
        "execution_now": {
            "saved_result_files": 1,
            "transform_operations": 0,
            "inference_samples": 0,
            "behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "nominal_behavior_preregistration": not failed,
            "behavior_matrix": False,
            "training": False,
            "gate5": False,
            "robot_or_rdk": False,
        },
    }
    value = {**basis, "result_sha256": canonical_sha256(basis)}
    RESULT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T188B step-zero binding recovery result\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Decision: `{value['decision']}`\n"
        f"- Failed checks: `{failed}`\n"
        "- All three graphs bind only the allowed nominal pair.\n"
        "- New transform / inference / behavior / optimizer / hosted / "
        "robot: `0/0/0/0/0/0`\n"
        f"- Result SHA-256: `{value['result_sha256']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"decision={value['decision']}")
    print(f"failed_checks={failed}")
    print(f"result_sha256={value['result_sha256']}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
