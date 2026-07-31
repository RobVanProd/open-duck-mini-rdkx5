#!/usr/bin/env python3
"""Run T23's preregistered 16-cell nominal physical gate on CPU."""

from __future__ import annotations

import argparse
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

import run_winner_v110_pitch_guard_behavior as evaluator  # noqa: E402


ANALYSIS = ROOT / "outputs/analysis"
PREREG = ANALYSIS / "t25_t23_nominal_behavior_preregistration.json"
RESULT = ANALYSIS / "t25_t23_nominal_behavior_result.json"
MARKDOWN = ANALYSIS / "T25_T23_NOMINAL_BEHAVIOR_RESULT_20260726.md"
PREREG_STATUS = "PREREGISTERED_T25_T23_NOMINAL_BEHAVIOR"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    parser.add_argument("--policy-root", type=Path, required=True)
    parser.add_argument("--playground", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    args = parser.parse_args()
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    basis = {
        key: value
        for key, value in prereg.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        prereg.get("status") != PREREG_STATUS
        or prereg.get("failed_checks") != []
        or evaluator.canonical_sha256(basis)
        != prereg.get("preregistered_contract_sha256")
    ):
        raise ValueError("T25 preregistration changed")
    for name, expected in prereg["source_hashes"].items():
        if evaluator.sha256(ROOT / name) != expected:
            raise ValueError(f"T25 evaluator source changed: {name}")
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
    result["schema_version"] = "open_duck.t25_t23_nominal_behavior_result.v1"
    result["status"] = (
        "PASS_T25_T23_NOMINAL_BEHAVIOR_VALID_RESULT"
        if valid
        else "INVALID_T25_T23_NOMINAL_BEHAVIOR_RESULT"
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
    result["evaluator_reuse"] = {
        "kernel": "run_winner_v110_pitch_guard_behavior.execute",
        "gate_change": False,
        "matrix_shape_change": False,
        "current_or_torque_threshold_change": False,
        "playground": str(args.playground.resolve()),
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
                "# T25 T23 nominal behavior result",
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
                "- A valid persistent pass authorizes only a separate full "
                "frozen robustness-matrix preregistration. It does not select "
                "a checkpoint or authorize Gate 5, RDK-X5, or robot use.",
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
