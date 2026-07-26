#!/usr/bin/env python3
"""Run the evaluator-only recovery of T23's unchanged 16-cell gate."""

from __future__ import annotations

import argparse
from dataclasses import replace
import json
import os
from pathlib import Path
import sys

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["HIP_VISIBLE_DEVICES"] = ""
os.environ["ROCR_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"
os.environ["JAX_PLATFORM_NAME"] = "cpu"


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

import run_winner_v109_recurrent_source_screen as v109  # noqa: E402
import run_winner_v110_pitch_guard_behavior as evaluator  # noqa: E402


ANALYSIS = ROOT / "outputs/analysis"
PREREG = ANALYSIS / "t25_t23_nominal_behavior_preregistration.json"
RECOVERY = ANALYSIS / "t25b_nominal_evaluator_recovery_preregistration.json"
RESULT = ANALYSIS / "t25b_t23_nominal_behavior_result.json"
MARKDOWN = ANALYSIS / "T25B_T23_NOMINAL_BEHAVIOR_RESULT_20260726.md"
PREREG_STATUS = "PREREGISTERED_T25_T23_NOMINAL_BEHAVIOR"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    parser.add_argument("--policy-root", type=Path, required=True)
    parser.add_argument("--playground", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    args = parser.parse_args()
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    recovery = json.loads(RECOVERY.read_text(encoding="utf-8"))
    recovery_basis = {
        key: value
        for key, value in recovery.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        recovery.get("status")
        != "PREREGISTERED_T25B_NOMINAL_EVALUATOR_RECOVERY"
        or recovery.get("failed_checks") != []
        or evaluator.canonical_sha256(recovery_basis)
        != recovery.get("preregistered_contract_sha256")
        or recovery["frozen_matrix_sha256"] != prereg["matrix"]["sha256"]
    ):
        raise ValueError("T25B recovery preregistration changed")
    for name, expected in recovery["source_hashes"].items():
        if evaluator.sha256(ROOT / name) != expected:
            raise ValueError(f"T25B evaluator source changed: {name}")

    original_run_closed_loop_sim = v109.run_closed_loop_sim

    def diagnostic_zero_context(config):
        return original_run_closed_loop_sim(
            replace(
                config,
                policy_context_input_name="calibration_context",
                policy_zero_context_input=True,
            )
        )

    v109.run_closed_loop_sim = diagnostic_zero_context
    evaluator.PREREG = PREREG
    evaluator.RESULT_JSON = RESULT
    evaluator.RESULT_MD = MARKDOWN
    evaluator.PREREG_SHA256 = evaluator.sha256(PREREG)
    evaluator.PREREG_STATUS = PREREG_STATUS
    evaluator.MATRIX_SHA256 = prereg["matrix"]["sha256"]
    result = evaluator.execute(
        policy_root=args.policy_root.resolve(),
        playground=args.playground.resolve(),
        run_root=args.run_root.resolve(),
    )
    valid = not result["failed_validity_checks"]
    persistent = bool(
        result["summary"]["persistent_both_checkpoint_pass"]
    )
    result["schema_version"] = "open_duck.t25b_nominal_behavior_result.v1"
    result["status"] = (
        "PASS_T25B_T23_NOMINAL_BEHAVIOR_VALID_RESULT"
        if valid
        else "INVALID_T25B_T23_NOMINAL_BEHAVIOR_RESULT"
    )
    result["decision"] = {
        "status": (
            "ADVANCE_T23_TO_FULL_FROZEN_ROBUSTNESS_MATRIX"
            if valid and persistent
            else "REJECT_T23_NOMINAL_POLICY"
        ),
        "persistent_both_checkpoint_pass": persistent,
        "next_action": (
            "preregister the unchanged full frozen robustness matrix"
            if valid and persistent
            else "attribute the nominal failure before further policy work"
        ),
    }
    result["evaluator_recovery"] = {
        "classification": "diagnostic_zero_context_feed_only",
        "calibration_context": "float32_zeros[1,64]",
        "response_calibrator": False,
        "unscored_prefix_ticks": 0,
        "policy_change": False,
        "matrix_change": False,
        "gate_change": False,
        "simulator_change": False,
        "first_invalid_execution_decision_weight": 0,
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
        newline="\n",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T25B T23 nominal behavior result",
                "",
                f"- Status: `{result['status']}`",
                f"- Decision: `{result['decision']['status']}`",
                f"- Passing cells: "
                f"`{result['summary']['passing_cells']}/16`",
                f"- Persistent pass: `{persistent}`",
                f"- Worst tracking p95: "
                f"`{result['summary']['worst_tracking_p95_rad']}` rad",
                f"- Worst peak current: "
                f"`{result['summary']['worst_peak_current_a']}` A",
                f"- Worst peak torque: "
                f"`{result['summary']['worst_peak_torque_nm']}` N.m",
                "- T25B changes only the feed of a proven ignored diagnostic "
                "input. A pass authorizes only robustness preregistration.",
                "",
            ]
        ),
        encoding="utf-8",
        newline="\n",
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
