#!/usr/bin/env python3
"""Freeze the read-only correction to T14's dimension check."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "t14_domain_gradient_geometry_preregistration.json"
RAW = ANALYSIS / "t14_domain_gradient_geometry_result.json"
OUTPUT = ANALYSIS / "t14_dimension_reporting_correction.json"
MARKDOWN = ANALYSIS / "T14_DIMENSION_REPORTING_CORRECTION_20260726.md"
RUNNER = ROOT / "tools" / "run_t14_domain_gradient_geometry.py"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    if OUTPUT.exists() or MARKDOWN.exists():
        raise FileExistsError("refusing to overwrite T14 correction")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    raw = json.loads(RAW.read_text(encoding="utf-8"))
    expected_dimensions = {
        "environments_per_domain": 256,
        "ticks_per_environment": 80,
        "unroll_length": 20,
        "minibatches": 4,
        "sequences_per_domain": 1024,
        "observations_per_domain": 20_480,
        "optimizer_steps": 0,
        "behavior_cells": 0,
    }
    substantive_failures = {
        "at_least_three_of_four_minibatches_show_harm",
        "primary_broad_and_negative_gradients_conflict",
        "primary_broad_descent_strictly_harms_negative_com",
        "source_normalizer_sensitivity_preserves_harm_sign",
    }
    checks = {
        "preregistration_was_green": (
            prereg["status"]
            == "PREREGISTERED_T14_DOMAIN_GRADIENT_GEOMETRY"
            and prereg["failed_checks"] == []
        ),
        "raw_result_is_hold": (
            raw["status"] == "HOLD_T14_DOMAIN_GRADIENT_GEOMETRY"
        ),
        "raw_dimensions_payload_exact": (
            raw["dimensions"] == expected_dimensions
        ),
        "raw_dimension_check_only_reporting_defect": (
            raw["checks"]["formal_dimensions_exact"] is False
            and set(raw["failed_checks"])
            == substantive_failures | {"formal_dimensions_exact"}
        ),
        "raw_decision_already_closes_route": (
            raw["decision"]
            == "CLOSE_WORST_DOMAIN_OBJECTIVE_FROM_V121_HALF"
        ),
        "all_four_minibatches_align_not_conflict": (
            raw["geometry"]["broad_updated"][
                "negative_harmed_minibatches"
            ]
            == 0
        ),
        "primary_and_sensitivity_dots_positive": (
            raw["geometry"]["broad_updated"][
                "broad_vs_negative_com"
            ]["gradient_dot"]
            > 0.0
            and raw["geometry"]["source_frozen"][
                "broad_vs_negative_com"
            ]["gradient_dot"]
            > 0.0
        ),
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": (
            "open_duck.t14_dimension_reporting_correction.v1"
        ),
        "status": (
            "APPROVED_T14_DIMENSION_REPORTING_CORRECTION"
            if not failed
            else "HOLD_T14_DIMENSION_REPORTING_CORRECTION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": {
            "preregistration": sha256(PREREG),
            "raw_result": sha256(RAW),
            "corrected_runner": sha256(RUNNER),
        },
        "correction": {
            "original_predicate": (
                "environments == 256 and ticks == 80 and "
                "len(permutation) == 20480"
            ),
            "defect": (
                "The frozen permutation indexes 1,024 20-tick sequences; "
                "20,480 is the observation count, not permutation length."
            ),
            "corrected_dimensions": expected_dimensions,
            "formal_dimensions_exact": True,
            "raw_result_mutated": False,
            "formal_execution_rerun": False,
            "threshold_or_geometry_changed": False,
        },
        "corrected_classification": {
            "status": "HOLD_T14_DOMAIN_GRADIENT_GEOMETRY",
            "failed_checks": sorted(substantive_failures),
            "decision": (
                "CLOSE_WORST_DOMAIN_OBJECTIVE_FROM_V121_HALF"
            ),
        },
        "authority": {
            "classification_only": True,
            "new_rollouts": 0,
            "optimizer_steps": 0,
            "hosted_compute": False,
            "behavior_cells": 0,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    OUTPUT.write_text(
        json.dumps(
            payload,
            allow_nan=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T14 dimension reporting correction",
                "",
                f"- Status: `{payload['status']}`",
                "- Raw formal result is preserved unchanged.",
                "- Correct dimensions: 1,024 sequences × 20 ticks = 20,480 observations.",
                (
                    "- The substantive result remains a hold: all four "
                    "minibatches aligned with, rather than opposed, the "
                    "negative-COM gradient."
                ),
                (
                    "- Decision remains "
                    "`CLOSE_WORST_DOMAIN_OBJECTIVE_FROM_V121_HALF`."
                ),
                "- No rerun, optimizer, hosted compute, behavior, or hardware.",
                "",
            ]
        ),
        encoding="utf-8",
        newline="\n",
    )
    print(payload["status"])
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
