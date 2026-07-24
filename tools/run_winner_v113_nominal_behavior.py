#!/usr/bin/env python3
"""Run the preregistered V113 16-cell nominal physical gate on CPU."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

import run_winner_v110_pitch_guard_behavior as evaluator  # noqa: E402


ANALYSIS = ROOT / "outputs/analysis"
PREREG = ANALYSIS / "winner_v113_nominal_behavior_preregistration.json"
RESULT = ANALYSIS / "winner_v113_nominal_behavior_result.json"
MARKDOWN = ANALYSIS / "WINNER_V113_NOMINAL_BEHAVIOR_RESULT_20260724.md"
PREREG_SHA256 = (
    "f6b370f7caab4ff89bd23b488162f31f07ca99d98b4d91674e7aceeae6df4339"
)
MATRIX_SHA256 = (
    "242aa6d3f8f002ae068b57ee22ffc0b7e7fef1da9a378ca9cf9b42dd0cf805d7"
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    parser.add_argument("--policy-root", type=Path, required=True)
    parser.add_argument("--playground", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    args = parser.parse_args()
    evaluator.PREREG = PREREG
    evaluator.RESULT_JSON = RESULT
    evaluator.RESULT_MD = MARKDOWN
    evaluator.PREREG_SHA256 = PREREG_SHA256
    evaluator.MATRIX_SHA256 = MATRIX_SHA256
    result = evaluator.execute(
        policy_root=args.policy_root.resolve(),
        playground=args.playground.resolve(),
        run_root=args.run_root.resolve(),
    )
    valid = not result["failed_validity_checks"]
    persistent = bool(result["summary"]["persistent_both_checkpoint_pass"])
    result["schema_version"] = "winner_v113.nominal_behavior_result.v1"
    result["status"] = (
        "PASS_WINNER_V113_NOMINAL_BEHAVIOR_VALID_RESULT"
        if valid
        else "INVALID_WINNER_V113_NOMINAL_BEHAVIOR"
    )
    result["decision"] = {
        "status": (
            "ADVANCE_V113_TO_FULL_FROZEN_MATRIX"
            if valid and persistent
            else "REJECT_V113_NOMINAL_POLICY"
        ),
        "persistent_both_checkpoint_pass": persistent,
        "next_action": (
            "preregister the full frozen robustness matrix"
            if valid and persistent
            else "attribute the nominal failure before any further policy work"
        ),
    }
    result["evaluator_reuse"] = {
        "kernel": "run_winner_v110_pitch_guard_behavior.execute",
        "gate_change": False,
        "matrix_shape_change": False,
        "current_or_torque_threshold_change": False,
    }
    result["authority"] = {
        "full_frozen_matrix_preregistration_authorized": (
            valid and persistent
        ),
        "behavior_evaluation_authorized": False,
        "checkpoint_selection_authorized": False,
        "gate5_authorized": False,
        "robot_clearance": False,
        "rdkx5_or_robot": False,
        "torque_or_motion": False,
    }
    RESULT.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner-v113 nominal behavior result\n\n"
        f"Status: `{result['status']}`\n\n"
        f"Decision: `{result['decision']['status']}`\n\n"
        f"Passing cells: `{result['summary']['passing_cells']}/16`\n\n"
        f"Persistent pass: `{persistent}`\n\n"
        f"Worst tracking p95: "
        f"`{result['summary']['worst_tracking_p95_rad']}` rad\n\n"
        f"Worst peak current: "
        f"`{result['summary']['worst_peak_current_a']}` A\n\n"
        f"Worst peak torque: "
        f"`{result['summary']['worst_peak_torque_nm']}` N.m\n\n"
        "A valid persistent pass authorizes only a separate full frozen "
        "robustness-matrix preregistration. It does not select a checkpoint or "
        "authorize Gate 5, robot use, torque, or motion.\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": result["status"],
                "decision": result["decision"],
                "summary": result["summary"],
            }
        ),
        flush=True,
    )
    return 0 if valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
