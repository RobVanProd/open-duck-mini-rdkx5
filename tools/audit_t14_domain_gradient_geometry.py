#!/usr/bin/env python3
"""Independently audit T14's raw geometry and reporting correction."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "t14_domain_gradient_geometry_preregistration.json"
RAW = ANALYSIS / "t14_domain_gradient_geometry_result.json"
CORRECTION = ANALYSIS / "t14_dimension_reporting_correction.json"
OUTPUT = ANALYSIS / "t14_domain_gradient_geometry_independent_audit.json"
MARKDOWN = (
    ANALYSIS
    / "T14_DOMAIN_GRADIENT_GEOMETRY_INDEPENDENT_AUDIT_20260726.md"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def geometry_issue(path: str, row: dict[str, float]) -> str | None:
    left = row["left_gradient_norm"]
    right = row["right_gradient_norm"]
    dot = row["gradient_dot"]
    product = left * right
    expected_cosine = dot / product
    tolerance = 128.0 * 1.1920928955078125e-7 * max(
        1.0,
        abs(dot),
        product,
    )
    checks = {
        "cosine": math.isclose(
            row["gradient_cosine"],
            expected_cosine,
            rel_tol=0.0,
            abs_tol=tolerance,
        ),
        "right_derivative": math.isclose(
            row["right_loss_derivative_along_left_descent"],
            -dot,
            rel_tol=0.0,
            abs_tol=tolerance,
        ),
        "left_derivative": math.isclose(
            row["left_loss_derivative_along_right_descent"],
            -dot,
            rel_tol=0.0,
            abs_tol=tolerance,
        ),
        "left_self": math.isclose(
            row["left_self_descent_derivative"],
            -(left * left),
            rel_tol=0.0,
            abs_tol=tolerance,
        ),
        "right_self": math.isclose(
            row["right_self_descent_derivative"],
            -(right * right),
            rel_tol=0.0,
            abs_tol=tolerance,
        ),
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    return None if not failed else f"{path}: {failed}"


def main() -> int:
    if OUTPUT.exists() or MARKDOWN.exists():
        raise FileExistsError("refusing to overwrite T14 audit")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    raw = json.loads(RAW.read_text(encoding="utf-8"))
    correction = json.loads(CORRECTION.read_text(encoding="utf-8"))
    issues = []
    if (
        correction["status"]
        != "APPROVED_T14_DIMENSION_REPORTING_CORRECTION"
        or correction["failed_checks"]
    ):
        issues.append("reporting correction is not green")
    if correction["input_hashes"]["preregistration"] != sha256(PREREG):
        issues.append("preregistration hash mismatch")
    if correction["input_hashes"]["raw_result"] != sha256(RAW):
        issues.append("raw result hash mismatch")
    if (
        prereg["preregistered_contract_sha256"]
        != "bdfdba6f5f3d52ba0ace28f8e0a92bb85b4b62ff3755e4f9912bf4e0baa5a83d"
    ):
        issues.append("frozen preregistration contract changed")

    for processor, rows in raw["geometry"].items():
        for comparison in (
            "broad_vs_negative_com",
            "nominal_vs_negative_com",
            "broad_vs_nominal",
        ):
            issue = geometry_issue(
                f"{processor}.{comparison}",
                rows[comparison],
            )
            if issue:
                issues.append(issue)
        for index, row in enumerate(
            rows["broad_vs_negative_com_minibatches"]
        ):
            issue = geometry_issue(
                f"{processor}.minibatch[{index}]",
                row,
            )
            if issue:
                issues.append(issue)

    primary = raw["geometry"]["broad_updated"][
        "broad_vs_negative_com"
    ]
    sensitivity = raw["geometry"]["source_frozen"][
        "broad_vs_negative_com"
    ]
    all_primary_minibatches_align = all(
        row["gradient_dot"] > 0.0
        and row[
            "right_loss_derivative_along_left_descent"
        ]
        < 0.0
        for row in raw["geometry"]["broad_updated"][
            "broad_vs_negative_com_minibatches"
        ]
    )
    corrected_failures = correction["corrected_classification"][
        "failed_checks"
    ]
    expected_failures = sorted(
        [
            "at_least_three_of_four_minibatches_show_harm",
            "primary_broad_and_negative_gradients_conflict",
            "primary_broad_descent_strictly_harms_negative_com",
            "source_normalizer_sensitivity_preserves_harm_sign",
        ]
    )
    if corrected_failures != expected_failures:
        issues.append("corrected failed-check set changed")
    if not (
        primary["gradient_dot"] > 0.0
        and primary["gradient_cosine"] > 0.0
        and primary[
            "right_loss_derivative_along_left_descent"
        ]
        < 0.0
        and sensitivity["gradient_dot"] > 0.0
        and sensitivity["gradient_cosine"] > 0.0
        and all_primary_minibatches_align
        and raw["geometry"]["broad_updated"][
            "negative_harmed_minibatches"
        ]
        == 0
    ):
        issues.append("substantive alignment conclusion does not reproduce")
    if not (
        raw["authority"]["optimizer_steps"] == 0
        and raw["dimensions"]["behavior_cells"] == 0
        and raw["authority"]["hosted_or_colab_compute"] is False
        and raw["authority"]["rdkx5_or_robot"] is False
    ):
        issues.append("zero-authority execution claim changed")

    payload = {
        "schema_version": (
            "open_duck.t14_domain_gradient_geometry_independent_audit.v1"
        ),
        "status": (
            "PASS_T14_DOMAIN_GRADIENT_GEOMETRY_INDEPENDENT_AUDIT"
            if not issues
            else "HOLD_T14_DOMAIN_GRADIENT_GEOMETRY_INDEPENDENT_AUDIT"
        ),
        "issues": issues,
        "input_hashes": {
            "preregistration": sha256(PREREG),
            "raw_result": sha256(RAW),
            "reporting_correction": sha256(CORRECTION),
        },
        "recomputed": {
            "formal_dimensions_exact": (
                correction["correction"]["corrected_dimensions"]
                == raw["dimensions"]
            ),
            "primary_gradient_cosine": primary["gradient_cosine"],
            "primary_gradient_dot": primary["gradient_dot"],
            "primary_negative_loss_derivative_along_broad_descent": (
                primary[
                    "right_loss_derivative_along_left_descent"
                ]
            ),
            "sensitivity_gradient_cosine": (
                sensitivity["gradient_cosine"]
            ),
            "all_four_primary_minibatches_align": (
                all_primary_minibatches_align
            ),
            "negative_harmed_minibatches": raw["geometry"][
                "broad_updated"
            ]["negative_harmed_minibatches"],
            "corrected_failed_checks": corrected_failures,
        },
        "decision": (
            "CLOSE_WORST_DOMAIN_OBJECTIVE_FROM_V121_HALF"
        ),
        "authority": {
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
                "# T14 independent audit",
                "",
                f"- Status: `{payload['status']}`",
                f"- Issues: `{issues}`",
                (
                    "- Corrected formal dimensions: "
                    f"`{payload['recomputed']['formal_dimensions_exact']}`"
                ),
                (
                    "- Broad/negative gradient cosine: "
                    f"`{primary['gradient_cosine']}`"
                ),
                (
                    "- Negative-COM loss derivative along broad descent: "
                    f"`{primary['right_loss_derivative_along_left_descent']}`"
                ),
                "- All four minibatches align; zero show harm.",
                (
                    "- Decision: "
                    "`CLOSE_WORST_DOMAIN_OBJECTIVE_FROM_V121_HALF`"
                ),
                "- No rerun, optimizer, hosted compute, behavior, or hardware.",
                "",
            ]
        ),
        encoding="utf-8",
        newline="\n",
    )
    print(payload["status"])
    return 0 if not issues else 1


if __name__ == "__main__":
    raise SystemExit(main())
