#!/usr/bin/env python3
"""Attribute the valid Winner-v16 single-axis direction-screen hold."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
RESULT = ANALYSIS / "winner_v16_support_action_direction_diagnostic_v2_result.json"
OUTPUT = ANALYSIS / "winner_v16_support_action_direction_hold_attribution.json"
MARKDOWN = ANALYSIS / "WINNER_V16_SUPPORT_ACTION_DIRECTION_HOLD_ATTRIBUTION_20260721.md"
DURATION_TICKS = 250
DIRECTION_PAIRS = (
    ("HIP_MAG_NEG", "HIP_MAG_POS"),
    ("KNEE_POS", "KNEE_NEG"),
    ("ANKLE_POS", "ANKLE_NEG"),
)


def cell_key(cell: Mapping[str, Any]) -> tuple[str, str]:
    return str(cell["configuration_id"]), str(cell["plant"])


def lifetime(cell: Mapping[str, Any]) -> int:
    return DURATION_TICKS if cell["support_pass"] else int(cell["terminal"]["tick"])


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
        != "PASS_WINNER_V16_SUPPORT_ACTION_DIRECTION_DIAGNOSTIC_V2"
        or result.get("decision")
        != "NO_SINGLE_BILATERAL_AXIS_DIRECTION_PASSES_STOP_WITH_ATTRIBUTION"
        or result.get("failed_validity_checks") != []
        or result.get("full_pass_candidates") != []
        or result.get("selected_direction") is not None
        or result.get("repository_attribution", {}).get("github_run_id")
        != 29847108867
    ):
        raise ValueError("Winner-v16 direction result changed")

    direction_evidence: dict[str, Any] = {}
    for desired, opposite in DIRECTION_PAIRS:
        desired_minus_baseline: list[int] = []
        desired_minus_opposite: list[int] = []
        opposite_minus_baseline: list[int] = []
        compared_cells = 0
        for checkpoint in result["checkpoint_results"]:
            index = {
                row["intervention"]["id"]: {
                    cell_key(cell): cell for cell in row["cells"]
                }
                for row in checkpoint["intervention_results"]
            }
            if set(index["BASELINE"]) != set(index[desired]) or set(index[desired]) != set(index[opposite]):
                raise ValueError("Winner-v16 paired direction populations changed")
            for key, baseline in index["BASELINE"].items():
                desired_lifetime = lifetime(index[desired][key])
                opposite_lifetime = lifetime(index[opposite][key])
                baseline_lifetime = lifetime(baseline)
                desired_minus_baseline.append(desired_lifetime - baseline_lifetime)
                desired_minus_opposite.append(desired_lifetime - opposite_lifetime)
                opposite_minus_baseline.append(opposite_lifetime - baseline_lifetime)
                compared_cells += 1
        if (
            compared_cells != 24
            or not all(value > 0 for value in desired_minus_baseline)
            or not all(value > 0 for value in desired_minus_opposite)
            or not all(value < 0 for value in opposite_minus_baseline)
        ):
            raise ValueError("Winner-v16 sign dominance is not uniform")
        direction_evidence[desired] = {
            "opposite": opposite,
            "compared_cells": compared_cells,
            "desired_outlives_baseline_cells": sum(
                value > 0 for value in desired_minus_baseline
            ),
            "desired_outlives_opposite_cells": sum(
                value > 0 for value in desired_minus_opposite
            ),
            "opposite_shortens_baseline_cells": sum(
                value < 0 for value in opposite_minus_baseline
            ),
            "desired_minus_baseline_tick_range": [
                min(desired_minus_baseline),
                max(desired_minus_baseline),
            ],
            "desired_minus_opposite_tick_range": [
                min(desired_minus_opposite),
                max(desired_minus_opposite),
            ],
            "opposite_minus_baseline_tick_range": [
                min(opposite_minus_baseline),
                max(opposite_minus_baseline),
            ],
        }

    summaries = result["intervention_summary"]
    if any(row["passes_both_checkpoints"] for row in summaries.values()):
        raise ValueError("Winner-v16 single-axis class unexpectedly has a full pass")
    payload = {
        "schema_version": "winner_v16.support_action_direction_hold_attribution.v1",
        "status": "PASS_WINNER_V16_SUPPORT_ACTION_DIRECTION_HOLD_ATTRIBUTION",
        "decision": (
            "CLOSE_SINGLE_AXIS_CONSTANT_OFFSET_PREREGISTER_SIGN_CONSISTENT_COMBINATION_DIAGNOSTIC"
        ),
        "single_axis_result": {
            name: {
                "half_failure_count": summaries[name]["half_failure_count"],
                "final_failure_count": summaries[name]["final_failure_count"],
                "passes_both_checkpoints": summaries[name]["passes_both_checkpoints"],
            }
            for name in summaries
        },
        "direction_evidence": direction_evidence,
        "causal_interpretation": (
            "No constant single-axis offset passes, so that mechanism class is closed. "
            "However, the same hip-negative, knee-positive, and ankle-positive sign "
            "outlives both baseline and its opposite in every one of 24 paired cells, "
            "while each opposite sign shortens baseline in all 24. This selects the "
            "complete nonempty subset screen of that sign vector as a causal interaction "
            "diagnostic; it does not promote the closest failing single axis."
        ),
        "next_screen": {
            "interventions": [
                "BASELINE",
                "HIP_MAG_NEG",
                "KNEE_POS",
                "ANKLE_POS",
                "HIP_NEG_KNEE_POS",
                "HIP_NEG_ANKLE_POS",
                "KNEE_POS_ANKLE_POS",
                "HIP_NEG_KNEE_POS_ANKLE_POS",
            ],
            "checkpoints": ["half", "final"],
            "cells_per_checkpoint_intervention": 12,
            "total_cells": 192,
            "offset_per_active_axis_rad": 0.03,
            "selection": (
                "full 12-cell pass at both checkpoints; then fewest active axes, "
                "minimum action deviation, and frozen order"
            ),
            "optimizer_updates": 0,
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
                "one separately preregistered CPU-only sign-consistent combination diagnostic"
            ),
        },
        "source": {
            "github_run_id": result["repository_attribution"]["github_run_id"],
            "github_artifact_id": result["repository_attribution"]["github_artifact_id"],
            "artifact_zip_sha256": result["repository_attribution"]["artifact_zip_sha256"],
            "result_sha256": result["repository_attribution"]["raw_result_sha256"],
        },
    }
    args.output.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown.write_text(
        "\n".join(
            [
                "# Winner-v16 support action-direction hold attribution",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                "- Single-axis full passes: `0 / 6`",
                "- New training / robot access: `0 / 0`",
                "",
                "The constant single-axis mechanism is closed. This is not a closest-result",
                "promotion: three paired sign tests are directionally unanimous across all",
                "24 checkpoint/plant/configuration cells.",
                "",
                "Hip-negative, knee-positive, and ankle-positive each outlive baseline and",
                "their opposite in `24/24` cells; each opposite shortens baseline in `24/24`.",
                "That selects one frozen CPU-only screen over all nonempty subsets of the",
                "three evidence-selected directions. No optimizer or robot is authorized.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
