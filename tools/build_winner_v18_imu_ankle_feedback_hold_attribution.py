#!/usr/bin/env python3
"""Attribute the Winner-v18 same-ceiling IMU feedback hold."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
RESULT = ANALYSIS / "winner_v18_imu_ankle_feedback_diagnostic_result.json"
OUTPUT = ANALYSIS / "winner_v18_imu_ankle_feedback_hold_attribution.json"
MARKDOWN = ANALYSIS / "WINNER_V18_IMU_ANKLE_FEEDBACK_HOLD_ATTRIBUTION_20260721.md"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite attribution: {path}")
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    if (
        result.get("status") != "PASS_WINNER_V18_IMU_ANKLE_FEEDBACK_DIAGNOSTIC"
        or result.get("decision")
        != "NO_ONE_SIDED_IMU_ANKLE_FEEDBACK_PASSES_STOP_WITH_ATTRIBUTION"
        or result.get("failed_validity_checks") != []
        or result.get("full_pass_candidates") != []
        or result.get("selected_direction") is not None
        or result.get("repository_attribution", {}).get("github_run_id")
        != 29849401796
    ):
        raise ValueError("Winner-v18 result changed")
    summaries = result["intervention_summary"]
    expected_failures = {
        "BASELINE": [12, 12],
        "CONSTANT_ANKLE_POS": [8, 6],
        "TILT_BACKWARD": [10, 10],
        "TILT_OPPOSITE": [11, 10],
        "RATE_BACKWARD": [12, 10],
        "RATE_OPPOSITE": [12, 10],
        "TILT_RATE_BACKWARD": [10, 10],
    }
    observed = {
        name: [row["half_failure_count"], row["final_failure_count"]]
        for name, row in summaries.items()
    }
    if observed != expected_failures:
        raise ValueError("Winner-v18 failure pattern changed")
    combined = summaries["TILT_RATE_BACKWARD"]
    if not (0.30 < combined["activation_mean"] < 0.32):
        raise ValueError("Winner-v18 combined activation changed")
    payload = {
        "schema_version": "winner_v18.imu_ankle_feedback_hold_attribution.v1",
        "status": "PASS_WINNER_V18_IMU_ANKLE_FEEDBACK_HOLD_ATTRIBUTION",
        "decision": (
            "CLOSE_003_RAD_FEEDBACK_PREREGISTER_ONE_VARIABLE_MAGNITUDE_FEASIBILITY_SCREEN"
        ),
        "failure_counts_half_final": expected_failures,
        "activation_evidence": {
            name: {
                "minimum": row["activation_minimum"],
                "mean": row["activation_mean"],
                "maximum": row["activation_maximum"],
            }
            for name, row in summaries.items()
        },
        "causal_interpretation": (
            "The deployable feedback signs are valid but the 0.03-rad ceiling supplies "
            "only 0.007-0.009 rad average correction in the backward modes, less than "
            "the constant intervention that produced the strongest survival evidence. "
            "A single frozen 1x/2x/3x ceiling screen can falsify insufficient feedback "
            "authority without changing the feedback law or tuning after results."
        ),
        "magnitude_basis": {
            "combined_mean_activation": combined["activation_mean"],
            "one_over_mean_activation": 1.0 / combined["activation_mean"],
            "selected_multipliers": [1, 2, 3],
            "maximum_target_offsets_rad": [0.03, 0.06, 0.09],
            "reason": (
                "3x gives approximately the constant-0.03 average correction under the "
                "observed 0.313 mean activation; 2x is the preregistered bridge."
            ),
        },
        "next_screen": {
            "interventions": [
                "BASELINE",
                "CONSTANT_003",
                "CONSTANT_006",
                "CONSTANT_009",
                "TILT_RATE_003",
                "TILT_RATE_006",
                "TILT_RATE_009",
            ],
            "feedback_formula": "unchanged Winner-v18 TILT_RATE_BACKWARD",
            "checkpoints": ["half", "final"],
            "cells_per_checkpoint_intervention": 12,
            "total_cells": 168,
            "optimizer_updates": 0,
            "selection": (
                "full 12-cell pass at both checkpoints; then smallest ceiling, minimum "
                "mean-squared action deviation, frozen order; no closest failure"
            ),
        },
        "execution": {
            "new_diagnostic_cells": 0,
            "optimizer_updates": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "robot_clearance": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "authorizes_only": (
                "one separately preregistered CPU-only magnitude feasibility diagnostic"
            ),
        },
        "source": {
            "github_run_id": result["repository_attribution"]["github_run_id"],
            "github_artifact_id": result["repository_attribution"]["github_artifact_id"],
            "artifact_zip_sha256": result["repository_attribution"]["artifact_zip_sha256"],
            "raw_result_sha256": result["repository_attribution"]["raw_result_sha256"],
        },
    }
    args.output.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown.write_text(
        "\n".join(
            [
                "# Winner-v18 IMU ankle-feedback hold attribution",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                "- Same-ceiling feedback full passes: `0 / 5`",
                f"- Combined mean activation: `{combined['activation_mean']:.9f}`",
                "- Optimizer / robot access: `0 / 0`",
                "",
                "At a `0.03 rad` ceiling, combined feedback averages only about `31.3%`",
                "activation. The frozen `0.03/0.06/0.09 rad` feasibility screen tests",
                "whether insufficient conditional authority is causal. No post-result",
                "tuning or closest failure is allowed.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
