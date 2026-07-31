#!/usr/bin/env python3
"""Preregister T201's saved-trace predicted-roll risk diagnostic."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
from typing import Any

from run_t136_static_calibration_router_transform import (
    ANALYSIS,
    ROOT,
    canonical_sha256,
    receipt,
)


T198 = ANALYSIS / "t198_t194_targeted_y_negative_result.json"
T199 = ANALYSIS / "t199_t194_support_credit_autopsy_result.json"
T200 = ANALYSIS / "t200_t194_command_chord_result.json"
OUTPUT = ANALYSIS / "t201_t194_predicted_roll_risk_preregistration.json"
MARKDOWN = (
    ANALYSIS
    / "T201_T194_PREDICTED_ROLL_RISK_PREREGISTRATION_20260730.md"
)
BUILDER = Path(__file__).resolve()
RUNNER = ROOT / "tools" / "run_t201_t194_predicted_roll_risk.py"
TEST = ROOT / "tests" / "test_t201_t194_predicted_roll_risk.py"


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T201: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T201 preregistration requires clean worktree")

    t198 = json.loads(T198.read_text(encoding="utf-8"))
    t199 = json.loads(T199.read_text(encoding="utf-8"))
    t200 = json.loads(T200.read_text(encoding="utf-8"))
    traces = []
    for block in t198["blocks"]:
        for cell in block["result"]["cells"]:
            trace = Path(cell["protection"]["path"])
            traces.append(
                {
                    "checkpoint_id": block["checkpoint_id"],
                    "step": int(block["step"]),
                    "fit_id": block["fit_id"],
                    "command_x_m_s": float(cell["command_x_m_s"]),
                    "cell_green": bool(cell["cell_green"]),
                    "samples": int(cell["behavior"]["samples"]),
                    "termination_reason": cell["behavior"][
                        "termination_reason"
                    ],
                    "trace": {
                        "path": str(trace),
                        "bytes": trace.stat().st_size,
                        "sha256": cell["protection"]["sha256"],
                    },
                }
            )
    failed_traces = [row for row in traces if not row["cell_green"]]
    checks = {
        "t198_exact_15_of_16_hold": (
            t198["status"] == "HOLD_T198_T194_TARGETED_Y_NEGATIVE"
            and t198["condition"]["green_cells"] == 15
            and len(traces) == 16
            and len(failed_traces) == 1
        ),
        "sole_failure_is_roll_collapse": (
            failed_traces[0]["checkpoint_id"] == "T194_COMPOSED_HALF"
            and failed_traces[0]["fit_id"] == "p31_34"
            and failed_traces[0]["command_x_m_s"] == 0.077
            and failed_traces[0]["samples"] == 308
            and failed_traces[0]["termination_reason"] == "fall_or_nan"
        ),
        "support_and_command_hypotheses_closed": (
            t199["decision"]
            == (
                "RETURN_TO_MECHANISM_SELECTION_WITHOUT_SUPPORT_"
                "OBJECTIVE_CONTINUATION"
            )
            and t200["decision"]
            == "RETURN_TO_MECHANISM_SELECTION_WITHOUT_COMMAND_CHORD"
        ),
        "all_sixteen_traces_present": all(
            Path(row["trace"]["path"]).is_file() for row in traces
        ),
        "read_only_no_behavior_training_hosted_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T201 preregistration checks failed: {failed}")

    basis: dict[str, Any] = {
        "schema_version": (
            "open_duck.t201_t194_predicted_roll_risk_"
            "preregistration.v1"
        ),
        "status": "PREREGISTERED_T201_T194_PREDICTED_ROLL_RISK",
        "question": (
            "Does a runtime-observable four-tick predicted-roll risk exceed "
            "the complete 15-cell passing envelope early and densely enough "
            "on the sole failure to support a training-only roll-risk "
            "objective rather than merely labeling the terminal fall?"
        ),
        "frozen_inputs": {
            name: receipt(path)
            for name, path in {
                "builder": BUILDER,
                "runner": RUNNER,
                "test": TEST,
                "t198_result": T198,
                "t199_result": T199,
                "t200_result": T200,
            }.items()
        },
        "traces": traces,
        "analysis": {
            "control_dt_s": 0.02,
            "prediction_horizon_ticks": 4,
            "prediction_horizon_s": 0.08,
            "risk": "abs(body_roll_rad + 0.08 * body_roll_rate_rad_s)",
            "passing_envelope": (
                "nextafter(maximum risk over every row of all 15 passing "
                "cells, +infinity)"
            ),
            "candidate_cost": "square(max(0, risk - passing_envelope))",
            "separation_rule": {
                "all_passing_exceedance_rows": 0,
                "failure_minimum_exceedance_rows": 4,
                "minimum_failure_lead_ticks": 4,
                "failure_maximum_strictly_above_envelope": True,
            },
            "runtime_inputs_available": [
                "body roll from projected gravity",
                "body roll rate from IMU gyro",
            ],
            "deployment_graph_change": False,
            "selection_weight": 0,
        },
        "decision_rule": {
            "risk_is_early_dense_and_separable": (
                "EARN_T202_PREDICTED_ROLL_RISK_CPU_CONTRACT_"
                "PREREGISTRATION_ONLY"
            ),
            "otherwise": (
                "RETURN_TO_MECHANISM_SELECTION_WITHOUT_ROLL_RISK_"
                "OBJECTIVE"
            ),
            "no_optimizer_or_behavior": True,
        },
        "checks": checks,
        "failed_checks": failed,
        "execution_now": {
            "trace_rows": 0,
            "behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "execute_saved_trace_diagnostic": True,
            "cpu_contract_preregistration": False,
            "behavior": False,
            "training": False,
            "full_r2": False,
            "gate5": False,
            "robot_or_rdk": False,
        },
    }
    value = {
        **basis,
        "preregistered_contract_sha256": canonical_sha256(basis),
    }
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T201 T194 predicted-roll risk preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Inputs: all 16 frozen T198 traces\n"
        "- Risk: `abs(roll + 0.08 * roll_rate)`\n"
        "- Threshold: exact maximum of all 15 passes, advanced by nextafter\n"
        "- Behavior/training/hosted/robot: `0/0/0/0`\n"
        f"- Contract SHA-256: `{value['preregistered_contract_sha256']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
