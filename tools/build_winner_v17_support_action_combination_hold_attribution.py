#!/usr/bin/env python3
"""Attribute the Winner-v17 fixed-offset combination hold."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
RESULT = ANALYSIS / "winner_v17_support_action_combination_diagnostic_result.json"
OUTPUT = ANALYSIS / "winner_v17_support_action_combination_hold_attribution.json"
MARKDOWN = ANALYSIS / "WINNER_V17_SUPPORT_ACTION_COMBINATION_HOLD_ATTRIBUTION_20260721.md"


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
        result.get("status")
        != "PASS_WINNER_V17_SUPPORT_ACTION_COMBINATION_DIAGNOSTIC"
        or result.get("decision")
        != "NO_SIGN_CONSISTENT_COMBINATION_PASSES_CLOSE_CONSTANT_OFFSET_CLASS"
        or result.get("failed_validity_checks") != []
        or result.get("full_pass_candidates") != []
        or result.get("selected_direction") is not None
        or result.get("repository_attribution", {}).get("github_run_id")
        != 29848345372
    ):
        raise ValueError("Winner-v17 result changed")
    summaries = result["intervention_summary"]
    if any(row["passes_both_checkpoints"] for row in summaries.values()):
        raise ValueError("Winner-v17 unexpectedly contains a fixed-offset pass")
    expected_failures = {
        "BASELINE": (12, 12),
        "HIP_MAG_NEG": (12, 12),
        "KNEE_POS": (10, 10),
        "ANKLE_POS": (8, 6),
        "HIP_NEG_KNEE_POS": (12, 12),
        "HIP_NEG_ANKLE_POS": (12, 12),
        "KNEE_POS_ANKLE_POS": (8, 7),
        "HIP_NEG_KNEE_POS_ANKLE_POS": (12, 12),
    }
    observed = {
        name: (row["half_failure_count"], row["final_failure_count"])
        for name, row in summaries.items()
    }
    if observed != expected_failures:
        raise ValueError("Winner-v17 failure pattern changed")
    hip_combinations = [
        name
        for name in summaries
        if name.startswith("HIP_") and name != "HIP_MAG_NEG"
    ]
    if any(observed[name] != (12, 12) for name in hip_combinations):
        raise ValueError("Winner-v17 hip interaction pattern changed")

    payload = {
        "schema_version": "winner_v17.support_action_combination_hold_attribution.v1",
        "status": "PASS_WINNER_V17_SUPPORT_ACTION_COMBINATION_HOLD_ATTRIBUTION",
        "decision": (
            "CLOSE_FIXED_003_RAD_OFFSET_SUBSET_PREREGISTER_ONE_SIDED_IMU_ANKLE_FEEDBACK_DIAGNOSTIC"
        ),
        "failure_counts_half_final": {
            name: list(counts) for name, counts in expected_failures.items()
        },
        "interaction_evidence": {
            "positive_ankle": {
                "half_final_failures": [8, 6],
                "interpretation": (
                    "The unanimously selected ankle sign retains the only persistent "
                    "survival benefit, but a constant offset does not pass."
                ),
            },
            "positive_knee_plus_ankle": {
                "half_final_failures": [8, 7],
                "delta_from_ankle": [0, 1],
                "interpretation": "Adding the knee does not improve persistence.",
            },
            "hip_containing_combinations": {
                "ids": hip_combinations,
                "all_half_final_failures": [12, 12],
                "interpretation": "Every hip-containing fixed subset loses the ankle benefit.",
            },
        },
        "causal_interpretation": (
            "The fixed 0.03-rad-per-active-axis offset subset is closed. The ankle sign "
            "is still causally directional, but its required magnitude must depend on "
            "the observed falling state rather than remain continuously asserted."
        ),
        "next_screen": {
            "mechanism": "one-sided deployable IMU-proxy modulation of ANKLE_POS",
            "observation_inputs": {
                "gyro_pitch_rate": {"index": 1, "source": "gyro y"},
                "accelerometer_pitch_proxy": {"index": 3, "source": "accelerometer x"},
            },
            "interventions": [
                "BASELINE",
                "CONSTANT_ANKLE_POS",
                "TILT_BACKWARD",
                "TILT_OPPOSITE",
                "RATE_BACKWARD",
                "RATE_OPPOSITE",
                "TILT_RATE_BACKWARD",
            ],
            "maximum_target_offset_rad": 0.03,
            "tilt_boundary_rad": 0.35,
            "rate_reference_rad_s": 1.75,
            "checkpoints": ["half", "final"],
            "cells_per_checkpoint_intervention": 12,
            "total_cells": 168,
            "optimizer_updates": 0,
            "selection": "all 12 cells pass at both checkpoints; no closest failure",
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
                "one separately preregistered CPU-only IMU ankle-feedback diagnostic"
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
                "# Winner-v17 support action-combination hold attribution",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                "- Fixed-offset full passes: `0 / 7`",
                "- Optimizer / robot access: `0 / 0`",
                "",
                "All fixed `0.03 rad` subsets are closed. Positive ankle alone reduces",
                "failures to `8/6`; adding knee yields `8/7`, and every hip-containing",
                "combination returns to `12/12`.",
                "",
                "The next diagnostic keeps the evidence-selected ankle direction but makes",
                "its magnitude one-sided and state-dependent using only deployable gyro-y",
                "and accelerometer-x observations. It performs no training and grants no",
                "robot authority.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
