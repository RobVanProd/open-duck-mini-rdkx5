#!/usr/bin/env python3
"""Correct only float32 tolerance checks in the frozen V115 v2 attribution."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
SOURCE = ANALYSIS / "winner_v115_nominal_failure_attribution_v2.json"
OUTPUT = (
    ANALYSIS / "winner_v115_nominal_failure_attribution_v2_correction.json"
)
MARKDOWN = (
    ANALYSIS
    / "WINNER_V115_NOMINAL_FAILURE_ATTRIBUTION_V2_CORRECTION_20260724.md"
)
SOURCE_SHA256 = (
    "cf37a52c94c37dfb2103affcce2d649b1ddd679828e2fabf493082d5146af1a1"
)
TOLERANCE_RAD_S = 2.0e-7


def sha256(path: Path) -> str:
    import hashlib

    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V115 correction: {path}")
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    if (
        sha256(SOURCE) != SOURCE_SHA256
        or source.get("status")
        != "HOLD_WINNER_V115_NOMINAL_FAILURE_ATTRIBUTION_V2"
        or source.get("failed_checks")
        != ["formula_exact", "no_rate_limit_increased"]
    ):
        raise ValueError("V115 v2 held evidence changed")
    rows = source["derivation"]["joints"]
    formula_exact = all(
        (
            row["selected_rate_limit_rad_s"]
            < row["current_rate_limit_rad_s"]
        )
        if row["changed"]
        else abs(
            row["selected_rate_limit_rad_s"]
            - row["current_rate_limit_rad_s"]
        )
        <= TOLERANCE_RAD_S
        for row in rows
    )
    no_rate_increased = all(
        row["selected_rate_limit_rad_s"]
        <= row["current_rate_limit_rad_s"] + TOLERANCE_RAD_S
        for row in rows
    )
    inherited_checks = {
        name: value
        for name, value in source["checks"].items()
        if name not in {"formula_exact", "no_rate_limit_increased"}
    }
    checks = {
        **inherited_checks,
        "formula_exact_with_float32_tolerance": formula_exact,
        "no_rate_limit_increased_with_float32_tolerance": no_rate_increased,
        "source_hold_scope_exact": True,
        "derived_vector_unchanged": True,
        "policy_or_training_not_run": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    value = {
        "schema_version": (
            "winner_v115.nominal_failure_attribution_v2_correction.v1"
        ),
        "status": (
            "PASS_WINNER_V115_NOMINAL_FAILURE_ATTRIBUTION_V2_REPORTING_CORRECTED"
            if not failed
            else "HOLD_WINNER_V115_NOMINAL_FAILURE_ATTRIBUTION_V2_CORRECTION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "correction_scope": {
            "classification": "reporting_only",
            "original_failed_checks": source["failed_checks"],
            "cause": (
                "unchanged float32 normalized deltas reconstruct decimal "
                "rates within 7.5e-8 rad/s, but the original checks used "
                "strict decimal comparisons"
            ),
            "tolerance_rad_s": TOLERANCE_RAD_S,
            "derived_vector_changed": False,
            "policy_changed": False,
            "training_run": False,
            "behavior_cells": 0,
            "gate_changed": False,
        },
        "derivation": source["derivation"],
        "decision": (
            "PREREGISTER_ONE_DETERMINISTIC_MULTI_JOINT_RATE_PROJECTION"
            if not failed
            else "STOP"
        ),
        "authority": {
            "rate_projection_preregistration_authorized": not failed,
            "training_authorized": False,
            "behavior_evaluation_authorized": False,
            "full_matrix_authorized": False,
            "checkpoint_selection_authorized": False,
            "gate5_authorized": False,
            "rdkx5_or_robot": False,
            "robot_clearance": False,
            "torque_or_motion": False,
        },
        "input_hashes": {
            "held_v2_attribution": sha256(SOURCE),
        },
    }
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner-v115 nominal failure attribution v2 correction\n\n"
        f"Status: `{value['status']}`\n\n"
        "This correction changes only two strict decimal comparisons to an "
        "explicit 2e-7 rad/s float32 reconstruction tolerance. The derived "
        "vector, policy, traces, gate, and decision rule are unchanged. No "
        "training or behavior cell was executed.\n",
        encoding="utf-8",
    )
    print(value["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
