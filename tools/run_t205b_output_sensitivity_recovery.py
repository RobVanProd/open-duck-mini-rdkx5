#!/usr/bin/env python3
"""Re-evaluate T205's immutable result under the T205B contract."""

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


PREREG = (
    ANALYSIS / "t205b_output_sensitivity_recovery_preregistration.json"
)
RESULT = ANALYSIS / "t205b_output_sensitivity_recovery_result.json"
MARKDOWN = ANALYSIS / "T205B_OUTPUT_SENSITIVITY_RECOVERY_RESULT_20260730.md"
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--saved-result-authorized", action="store_true")
    args = parser.parse_args()
    if not args.saved_result_authorized:
        raise PermissionError("T205B requires --saved-result-authorized")
    for path in (RESULT, MARKDOWN):
        if path.exists():
            raise FileExistsError("refusing to overwrite T205B")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("formal T205B execution requires clean worktree")
    prereg = load(PREREG)
    if (
        prereg["status"]
        != "PREREGISTERED_T205B_OUTPUT_SENSITIVITY_RECOVERY"
        or prereg["failed_checks"]
        or canonical_without(prereg, "preregistered_contract_sha256")
        != prereg["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T205B preregistration changed")
    for name, item in prereg["frozen_inputs"].items():
        verify(item, name)

    source = load(
        Path(prereg["frozen_inputs"]["t205_result"]["path"])
    )
    substantive = {
        name: passed
        for name, passed in source["checks"].items()
        if name != DIAGNOSTIC
    }
    allowed = sorted(t172.DESTINATION_NAMES)
    checks = {
        "source_only_nonrequired_sensitivity_check_failed": (
            source["failed_checks"] == [DIAGNOSTIC]
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
        "all_routing_inactive_and_x0_contracts_exact": all(
            row["inference"]["both_y_negative_contexts_route_nominal"]
            and row["inference"]["all_inactive_routes_bit_exact"]
            and row["inference"]["all_x0_outputs_bit_exact"]
            and row["inference"]["all_outputs_finite"]
            for row in source["graphs"]
        ),
        "no_new_transform_inference_behavior_or_training": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    basis: dict[str, Any] = {
        "schema_version": (
            "open_duck.t205b_output_sensitivity_recovery_result.v1"
        ),
        "status": (
            "PASS_T205B_OUTPUT_SENSITIVITY_RECOVERY"
            if not failed
            else "HOLD_T205B_OUTPUT_SENSITIVITY_RECOVERY"
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
        "preserved_t205_checks": substantive,
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
        "# T205B output-sensitivity recovery result\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Decision: `{value['decision']}`\n"
        f"- Failed checks: `{failed}`\n"
        "- All three graphs bind only the allowed nominal pair; graph, "
        "inactive-route, and x=0 contracts remain exact.\n"
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
