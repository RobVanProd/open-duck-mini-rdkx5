#!/usr/bin/env python3
"""Freeze a saved-trace autopsy of T210's sole nominal failure."""

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


T213 = ANALYSIS / "t213_t210_nominal_matrix_result.json"
T201 = ANALYSIS / "t201_t194_predicted_roll_risk_result.json"
OUTPUT = ANALYSIS / "t213b_support_continuity_autopsy_preregistration.json"
MARKDOWN = (
    ANALYSIS
    / "T213B_SUPPORT_CONTINUITY_AUTOPSY_PREREGISTRATION_20260730.md"
)
RUNNER = ROOT / "tools/run_t213b_support_continuity_autopsy.py"
TEST = ROOT / "tests/test_t213b_support_continuity_autopsy.py"


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError("refusing to overwrite T213B preregistration")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T213B preregistration requires clean worktree")
    t213 = json.loads(T213.read_text(encoding="utf-8"))
    t201 = json.loads(T201.read_text(encoding="utf-8"))
    traces = []
    for block in t213["blocks"]:
        for cell in block["result"]["cells"]:
            protection = cell["protection"]
            traces.append(
                {
                    "checkpoint_id": block["checkpoint_id"],
                    "step": block["step"],
                    "fit_id": block["fit_id"],
                    "command_x_m_s": cell["command_x_m_s"],
                    "cell_green": cell["cell_green"],
                    "samples": cell["behavior"]["samples"],
                    "trace": {
                        "path": protection["path"],
                        "bytes": Path(protection["path"]).stat().st_size,
                        "sha256": protection["sha256"],
                    },
                }
            )
    failures = [row for row in traces if not row["cell_green"]]
    frozen = {
        "builder": receipt(Path(__file__)),
        "runner": receipt(RUNNER),
        "test": receipt(TEST),
        "t213_result": receipt(T213),
        "t201_result": receipt(T201),
    }
    checks = {
        "t213_exact_nominal_hold": (
            t213["status"] == "HOLD_T213_T210_NOMINAL_MATRIX"
            and t213["condition"]["green_cells"] == 15
            and t213["decision"]
            == "CLOSE_T210_DUAL_ROLL_COST_CONTINUATION"
        ),
        "exactly_one_failure": (
            len(failures) == 1
            and failures[0]["checkpoint_id"] == "T210_COMPOSED_FINAL"
            and failures[0]["fit_id"] == "p30"
            and failures[0]["command_x_m_s"] == 0.08
        ),
        "all_sixteen_traces_present": (
            len(traces) == 16
            and all(Path(row["trace"]["path"]).is_file() for row in traces)
        ),
        "t201_roll_signal_authority_green": (
            t201["status"] == "PASS_T201_T194_PREDICTED_ROLL_RISK"
            and not t201["failed_checks"]
        ),
        "zero_simulator_optimizer_onnx_behavior_hosted_or_robot_now": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T213B preregistration checks failed: {failed}")
    basis: dict[str, Any] = {
        "schema_version": (
            "open_duck.t213b_support_continuity_autopsy_"
            "preregistration.v1"
        ),
        "status": "PREREGISTERED_T213B_SUPPORT_CONTINUITY_AUTOPSY",
        "question": (
            "Does T210's sole nominal failure first leave the passing "
            "support-continuity envelope, followed by monotone height "
            "collapse, while predicted-roll risk remains too late for "
            "the selected constrained objective?"
        ),
        "frozen_inputs": frozen,
        "traces": traces,
        "signals": {
            "support_loss": "foot_contacts == [0, 0]",
            "support_statistic": "maximum_consecutive_support_loss_ticks",
            "failure_support_lead_required_ticks": 4,
            "roll_risk": "abs(body_roll_rad + 0.08*body_roll_rate_rad_s)",
            "current_pass_envelope": (
                "nextafter(maximum risk over every row of all 15 passing "
                "T213 traces, +infinity)"
            ),
            "frozen_t201_envelope_rad": t201["passing_envelope_rad"],
            "late_roll_lead_maximum_ticks": 3,
            "late_roll_lead_derivation": (
                "strictly less than T201's frozen four-tick precursor rule"
            ),
            "height_collapse": (
                "base_height_m strictly decreases from first anomalous "
                "support-loss run through terminal row"
            ),
        },
        "decision_rule": {
            "select_support_continuity_if": [
                "failure support-loss run strictly exceeds every pass",
                "first anomalous run begins at least 4 ticks before terminal",
                "height then decreases strictly through terminal",
                "current-pass and frozen-T201 roll thresholds first cross later",
                "both roll thresholds have at most 3 ticks terminal lead",
            ],
            "pass": (
                "EARN_T214B_SUPPORT_CONTINUITY_CURRICULUM_"
                "CPU_FALSIFIER_PREREGISTRATION_ONLY"
            ),
            "fail": "RETURN_TO_MECHANISM_SELECTION_WITHOUT_SUPPORT_CURRICULUM",
            "threshold_tuning": False,
        },
        "checks": checks,
        "failed_checks": failed,
        "execution_now": {
            "saved_trace_rows": 0,
            "simulator_transitions": 0,
            "optimizer_steps": 0,
            "onnx_inferences": 0,
            "behavior_cells": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "execute_saved_trace_autopsy": True,
            "support_curriculum_cpu_preregistration": False,
            "training": False,
            "colab": False,
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
        "# T213B support-continuity autopsy preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Inputs: all 16 frozen T213 traces; no simulator replay\n"
        "- Primary discriminator: consecutive ticks with neither foot in contact\n"
        "- Ordering: support loss -> height collapse -> late roll-risk crossing\n"
        "- Simulator / optimizer / ONNX / behavior / hosted / robot: "
        "`0/0/0/0/0/0`\n"
        f"- Contract SHA-256: `{value['preregistered_contract_sha256']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(
        "preregistered_contract_sha256="
        f"{value['preregistered_contract_sha256']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
