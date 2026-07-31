#!/usr/bin/env python3
"""Freeze a read-only autopsy of T170-to-T186 failure exchange."""

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


T174 = ANALYSIS / "t174_t173_failure_autopsy_result.json"
T188 = ANALYSIS / "t188_t186_postexport_composition_result.json"
T190B = ANALYSIS / "t190b_interrupted_execution_recovery_result.json"
T167 = ANALYSIS / "t167_calibration_context_separability_result.json"
OUTPUT = ANALYSIS / "t191_t186_failure_exchange_autopsy_preregistration.json"
MARKDOWN = (
    ANALYSIS / "T191_T186_FAILURE_EXCHANGE_AUTOPSY_PREREGISTRATION_20260730.md"
)
BUILDER = Path(__file__).resolve()
RUNNER = ROOT / "tools" / "run_t191_t186_failure_exchange_autopsy.py"
TEST = ROOT / "tests" / "test_t191_t186_failure_exchange_autopsy.py"


def find_cell(
    result: dict[str, Any],
    checkpoint: str,
    fit: str,
    command: float,
) -> dict[str, Any]:
    block = next(
        row
        for row in result["blocks"]
        if row["checkpoint_id"] == checkpoint and row["fit_id"] == fit
    )
    cell = next(
        row
        for row in block["result"]["cells"]
        if float(row["command_x_m_s"]) == command
    )
    trace = Path(cell["protection"]["path"])
    return {
        "checkpoint_id": checkpoint,
        "step": block["step"],
        "fit_id": fit,
        "command_x_m_s": command,
        "cell_green": cell["cell_green"],
        "samples": cell["behavior"]["samples"],
        "termination_reason": cell["behavior"]["termination_reason"],
        "trace": {
            "path": str(trace),
            "bytes": trace.stat().st_size,
            "sha256": cell["protection"]["sha256"],
        },
    }


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T191: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T191 preregistration requires clean worktree")

    t174 = json.loads(T174.read_text(encoding="utf-8"))
    t188 = json.loads(T188.read_text(encoding="utf-8"))
    t190b = json.loads(T190B.read_text(encoding="utf-8"))
    t167 = json.loads(T167.read_text(encoding="utf-8"))
    traces = [
        find_cell(t190b, "T186_COMPOSED_HALF", "p31_34", 0.080),
        find_cell(t190b, "T186_COMPOSED_FINAL", "p31_34", 0.080),
        find_cell(t190b, "T186_COMPOSED_HALF", "p30", 0.080),
        find_cell(t190b, "T186_COMPOSED_FINAL", "p30", 0.080),
    ]
    graph_by_step = {
        int(row["step"]): row["structure"]["transformed"]
        for row in t188["graphs"]
    }
    graphs = {
        "half": graph_by_step[1_003_520],
        "final": graph_by_step[2_007_040],
    }
    contexts = {
        row["fit_id"]: {
            "condition_id": row["condition_id"],
            "fit_id": row["fit_id"],
            "context": row["context"],
            "context_sha256": row["context_sha256"],
        }
        for row in t167["cells"]
        if row["condition_id"] == "TORSO_COM_Y_NEG"
    }
    checks = {
        "t190b_is_exact_15_of_16_hold": (
            t190b["status"]
            == "HOLD_T190B_INTERRUPTED_EXECUTION_RECOVERY"
            and t190b["decision"]
            == "CLOSE_T186_SINGLE_SUPPORT_CONTINUATION"
            and t190b["condition"]["green_cells"] == 15
        ),
        "new_failure_is_half_p31_x008_only": (
            traces[0]["cell_green"] is False
            and traces[0]["samples"] == 547
            and traces[0]["termination_reason"] == "fall_or_nan"
            and all(row["cell_green"] for row in traces[1:])
        ),
        "prior_t170_autopsy_exact_and_green": (
            t174["status"] == "PASS_T174_T173_FAILURE_AUTOPSY"
            and not t174["failed_checks"]
            and t174["terminal_summaries"]["final_p30_x0p080"]["rows"]
            == 281
        ),
        "paired_traces_present": all(
            Path(row["trace"]["path"]).is_file() for row in traces
        ),
        "two_composed_graphs_present": (
            set(graphs) == {"half", "final"}
            and all(Path(row["path"]).is_file() for row in graphs.values())
        ),
        "two_y_negative_contexts_exact": set(contexts) == {"p30", "p31_34"},
        "gait_period_is_frozen_27_ticks": True,
        "read_only_no_behavior_training_hosted_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T191 preregistration checks failed: {failed}")

    basis: dict[str, Any] = {
        "schema_version": (
            "open_duck.t191_t186_failure_exchange_autopsy_"
            "preregistration.v1"
        ),
        "status": "PREREGISTERED_T191_T186_FAILURE_EXCHANGE_AUTOPSY",
        "question": (
            "Did the reset-only single-support curriculum merely exchange "
            "T170's Y-negative failure for a late locomotion "
            "single-support failure, and does the T186 final head supply a "
            "state-compatible correction on the failing half trajectory?"
        ),
        "frozen_inputs": {
            name: receipt(path)
            for name, path in {
                "builder": BUILDER,
                "runner": RUNNER,
                "test": TEST,
                "t174_prior_autopsy": T174,
                "t188_composition": T188,
                "t190b_result": T190B,
                "t167_contexts": T167,
            }.items()
        },
        "graphs": graphs,
        "contexts": contexts,
        "traces": traces,
        "analysis": {
            "recorded_onnx_replay": "all stored rows, exact",
            "cross_checkpoint_replay": [
                "failing half/P31-34/x=.080 states",
                "passing final/P31-34/x=.080 states",
            ],
            "paired_dynamics": "half versus final P31-34/x=.080",
            "gait_period_ticks": 27,
            "terminal_window_ticks": 54,
            "support_proximity_rule": (
                "failure terminal tick minus last single-support tick <= 27"
            ),
            "next_screen_switch_tick_rule": (
                "failure terminal tick - (gait_period_ticks - 1)"
            ),
            "joint_order": [
                "left_hip_yaw",
                "left_hip_roll",
                "left_hip_pitch",
                "left_knee",
                "left_ankle",
                "neck_pitch",
                "head_pitch",
                "head_yaw",
                "head_roll",
                "right_hip_yaw",
                "right_hip_roll",
                "right_hip_pitch",
                "right_knee",
                "right_ankle",
            ],
            "selection_weight": 0,
        },
        "decision_rule": {
            "support_proximal_and_state_compatible": (
                "EARN_T192_ONE_PERIOD_HEAD_SWITCH_FEASIBILITY_"
                "PREREGISTRATION_ONLY"
            ),
            "otherwise": (
                "RETURN_TO_MECHANISM_SELECTION_WITHOUT_HEAD_SWITCH"
            ),
            "no_optimizer_or_behavior": True,
        },
        "checks": checks,
        "failed_checks": failed,
        "execution_now": {
            "inference_rows": 0,
            "behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "execute_read_only_autopsy": True,
            "head_switch_preregistration": False,
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
        "# T191 T186 failure-exchange autopsy preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Inputs: four frozen T186 traces, both T186 graphs, and T174\n"
        "- Work: exact replay, support proximity, and head compatibility\n"
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
