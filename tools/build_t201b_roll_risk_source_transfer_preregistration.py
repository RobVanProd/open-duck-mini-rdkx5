#!/usr/bin/env python3
"""Preregister T201B's T170/T194 roll-risk source-transfer audit."""

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


T201_PREREG = (
    ANALYSIS / "t201_t194_predicted_roll_risk_preregistration.json"
)
T201_RESULT = ANALYSIS / "t201_t194_predicted_roll_risk_result.json"
T174_PREREG = ANALYSIS / "t174_t173_failure_autopsy_preregistration.json"
T174_RESULT = ANALYSIS / "t174_t173_failure_autopsy_result.json"
OUTPUT = (
    ANALYSIS / "t201b_roll_risk_source_transfer_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "T201B_ROLL_RISK_SOURCE_TRANSFER_PREREGISTRATION_20260730.md"
)
BUILDER = Path(__file__).resolve()
RUNNER = ROOT / "tools" / "run_t201b_roll_risk_source_transfer.py"
TEST = ROOT / "tests" / "test_t201b_roll_risk_source_transfer.py"


def tagged(family: str, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{"family": family, **row} for row in rows]


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T201B: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T201B preregistration requires clean worktree")

    t201_prereg = json.loads(T201_PREREG.read_text(encoding="utf-8"))
    t201_result = json.loads(T201_RESULT.read_text(encoding="utf-8"))
    t174_prereg = json.loads(T174_PREREG.read_text(encoding="utf-8"))
    t174_result = json.loads(T174_RESULT.read_text(encoding="utf-8"))
    traces = [
        *tagged("t194", t201_prereg["traces"]),
        *tagged("t170", t174_prereg["traces"]),
    ]
    failures = [row for row in traces if not row["cell_green"]]
    checks = {
        "t201_selects_roll_risk": (
            t201_result["status"]
            == "PASS_T201_T194_PREDICTED_ROLL_RISK"
            and t201_result["separation_rule_passed"]
            and t201_result["decision"]
            == (
                "EARN_T202_PREDICTED_ROLL_RISK_CPU_CONTRACT_"
                "PREREGISTRATION_ONLY"
            )
        ),
        "t174_exact_prior_t170_autopsy": (
            t174_result["status"] == "PASS_T174_T173_FAILURE_AUTOPSY"
            and not t174_result["failed_checks"]
            and t174_result["terminal_summaries"][
                "final_p30_x0p080"
            ]["rows"]
            == 281
        ),
        "twenty_traces_eighteen_passes_two_failures": (
            len(traces) == 20
            and sum(row["cell_green"] for row in traces) == 18
            and len(failures) == 2
        ),
        "failures_are_t170_and_t194_roll_collapses": (
            {row["family"] for row in failures} == {"t170", "t194"}
            and {row["samples"] for row in failures} == {281, 308}
            and all(
                row["termination_reason"] == "fall_or_nan"
                for row in failures
            )
        ),
        "all_twenty_traces_present": all(
            Path(row["trace"]["path"]).is_file() for row in traces
        ),
        "read_only_no_behavior_training_hosted_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T201B preregistration checks failed: {failed}")

    basis: dict[str, Any] = {
        "schema_version": (
            "open_duck.t201b_roll_risk_source_transfer_"
            "preregistration.v1"
        ),
        "status": "PREREGISTERED_T201B_ROLL_RISK_SOURCE_TRANSFER",
        "question": (
            "Does one threshold derived from all 18 passing T170/T194 "
            "traces preserve every known pass while detecting both known "
            "roll-collapse failures early and densely enough to justify a "
            "roll-risk CPU training contract from protected T170 half?"
        ),
        "frozen_inputs": {
            name: receipt(path)
            for name, path in {
                "builder": BUILDER,
                "runner": RUNNER,
                "test": TEST,
                "t201_preregistration": T201_PREREG,
                "t201_result": T201_RESULT,
                "t174_preregistration": T174_PREREG,
                "t174_result": T174_RESULT,
            }.items()
        },
        "traces": traces,
        "analysis": {
            "prediction_horizon_s": 0.08,
            "risk": "abs(body_roll_rad + 0.08 * body_roll_rate_rad_s)",
            "combined_passing_envelope": (
                "nextafter(maximum risk over every row of all 18 passing "
                "T170/T194 traces, +infinity)"
            ),
            "candidate_cost": "square(max(0, risk - combined_envelope))",
            "per_failure_rule": {
                "minimum_exceedance_rows": 4,
                "minimum_lead_ticks": 4,
                "maximum_strictly_above_envelope": True,
            },
            "all_passing_exceedance_rows": 0,
            "selection_weight": 0,
        },
        "decision_rule": {
            "both_failures_separable": (
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
            "execute_source_transfer_audit": True,
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
        "# T201B roll-risk source-transfer preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Inputs: 20 frozen T170/T194 traces (18 pass, 2 fail)\n"
        "- Threshold: nextafter of the complete combined passing envelope\n"
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
