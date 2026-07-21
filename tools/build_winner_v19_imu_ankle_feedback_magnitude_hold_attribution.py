#!/usr/bin/env python3
"""Attribute the Winner-v19 feedback-authority hold."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
RESULT = ANALYSIS / "winner_v19_imu_ankle_feedback_magnitude_diagnostic_result.json"
OUTPUT = ANALYSIS / "winner_v19_imu_ankle_feedback_magnitude_hold_attribution.json"
MARKDOWN = ANALYSIS / "WINNER_V19_IMU_ANKLE_FEEDBACK_MAGNITUDE_HOLD_ATTRIBUTION_20260721.md"


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
        != "PASS_WINNER_V19_IMU_ANKLE_FEEDBACK_MAGNITUDE_DIAGNOSTIC"
        or result.get("decision")
        != "INSUFFICIENT_FEEDBACK_AUTHORITY_FALSIFIED_STOP_WITH_ATTRIBUTION"
        or result.get("failed_validity_checks") != []
        or result.get("full_pass_candidates") != []
        or result.get("selected_direction") is not None
        or result.get("repository_attribution", {}).get("github_run_id")
        != 29850348125
    ):
        raise ValueError("Winner-v19 result changed")

    summaries = result["intervention_summary"]
    expected_failures = {
        "BASELINE": [12, 12],
        "CONSTANT_003": [8, 6],
        "CONSTANT_006": [12, 12],
        "CONSTANT_009": [12, 12],
        "TILT_RATE_003": [10, 10],
        "TILT_RATE_006": [10, 8],
        "TILT_RATE_009": [10, 8],
    }
    observed = {
        name: [row["half_failure_count"], row["final_failure_count"]]
        for name, row in summaries.items()
    }
    if observed != expected_failures:
        raise ValueError("Winner-v19 failure pattern changed")
    if any(row["passes_both_checkpoints"] for row in summaries.values()):
        raise ValueError("Winner-v19 unexpectedly contains a full pass")
    if not (
        summaries["CONSTANT_006"]["mean_squared_action_delta_from_source"]
        > summaries["CONSTANT_003"]["mean_squared_action_delta_from_source"]
        and summaries["TILT_RATE_009"]["mean_squared_action_delta_from_source"]
        > summaries["TILT_RATE_006"]["mean_squared_action_delta_from_source"]
        > summaries["TILT_RATE_003"]["mean_squared_action_delta_from_source"]
    ):
        raise ValueError("Winner-v19 action-authority ordering changed")

    payload = {
        "schema_version": "winner_v19.imu_ankle_feedback_magnitude_hold_attribution.v1",
        "status": "PASS_WINNER_V19_IMU_ANKLE_FEEDBACK_MAGNITUDE_HOLD_ATTRIBUTION",
        "decision": (
            "CLOSE_POST_POLICY_ACTION_WRAPPERS_PREREGISTER_TRAINING_SIDE_CAUSAL_REPAIR"
        ),
        "failure_counts_half_final": expected_failures,
        "authority_evidence": {
            name: {
                "maximum_target_offset_rad": row["maximum_target_offset_rad"],
                "activation_mean": row["activation_mean"],
                "maximum_abs_action_delta_from_source": row[
                    "maximum_abs_action_delta_from_source"
                ],
                "mean_squared_action_delta_from_source": row[
                    "mean_squared_action_delta_from_source"
                ],
            }
            for name, row in summaries.items()
        },
        "causal_interpretation": (
            "Insufficient post-policy correction authority is falsified. Doubling the "
            "constant ankle correction worsens both checkpoints from 8/6 failures to "
            "12/12, while doubling and tripling the state-dependent ceiling plateaus "
            "at 10/8 failures despite monotonically larger action deviation. Together "
            "with Winner-v16 through Winner-v18, this closes constant, combined, and "
            "deployable IMU-conditioned action wrappers. The missing recovery must be "
            "learned within the policy under the failed support contexts rather than "
            "appended after policy inference."
        ),
        "closed_mechanisms": [
            "single bilateral fixed-axis direction",
            "all nonempty sign-consistent fixed-axis subsets",
            "one-sided deployable IMU ankle feedback at 0.03 rad",
            "one-sided deployable IMU ankle feedback at 0.03/0.06/0.09 rad",
        ],
        "next_work": {
            "mechanism_class": "training_side_state_dependent_support_recovery",
            "required_first_step": (
                "a separately reviewed CPU contract and preregistration derived from "
                "the frozen Winner-v15 source and the failed support-cell traces"
            ),
            "optimizer_updates_authorized_now": 0,
            "diagnostic_cells_authorized_now": 0,
            "prohibited": [
                "another post-policy target or action wrapper",
                "post-result scalar tuning",
                "checkpoint selection by closest failure",
            ],
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
                "offline source audit and a separately reviewed CPU-only training-repair contract"
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
                "# Winner-v19 feedback-magnitude hold attribution",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                "- Full passes: `0 / 6` non-baseline interventions",
                "- Optimizer / robot access: `0 / 0`",
                "",
                "More correction does not solve the negative-support failures. The",
                "constant arm worsens to `12/12` failures at `0.06 rad`; deployable",
                "state feedback plateaus at `10/8` failures at both `0.06` and `0.09 rad`",
                "despite larger action deviation.",
                "",
                "Winner-v16 through Winner-v19 therefore close post-policy action",
                "wrappers. The next admissible mechanism is a separately contracted",
                "training-side recovery learned in the failed support contexts. This",
                "attribution grants no training run and no robot authority.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
