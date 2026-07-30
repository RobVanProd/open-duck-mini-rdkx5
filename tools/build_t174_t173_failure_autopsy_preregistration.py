#!/usr/bin/env python3
"""Freeze a read-only autopsy of T173's sole failing behavior cell."""

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


T173 = ANALYSIS / "t173_t170_targeted_y_negative_result.json"
T172 = ANALYSIS / "t172_t170_postexport_composition_result.json"
T167 = ANALYSIS / "t167_calibration_context_separability_result.json"
OUTPUT = ANALYSIS / "t174_t173_failure_autopsy_preregistration.json"
MARKDOWN = ANALYSIS / "T174_T173_FAILURE_AUTOPSY_PREREGISTRATION_20260729.md"
BUILDER = Path(__file__).resolve()
RUNNER = ROOT / "tools" / "run_t174_t173_failure_autopsy.py"
TEST = ROOT / "tests" / "test_t174_t173_failure_autopsy.py"


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
    return {
        "checkpoint_id": checkpoint,
        "step": block["step"],
        "fit_id": fit,
        "command_x_m_s": command,
        "cell_green": cell["cell_green"],
        "samples": cell["behavior"]["samples"],
        "termination_reason": cell["behavior"]["termination_reason"],
        "trace": {
            "path": cell["protection"]["path"],
            "bytes": Path(cell["protection"]["path"]).stat().st_size,
            "sha256": cell["protection"]["sha256"],
        },
    }


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T174: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T174 preregistration requires clean worktree")
    t173 = json.loads(T173.read_text(encoding="utf-8"))
    t172 = json.loads(T172.read_text(encoding="utf-8"))
    t167 = json.loads(T167.read_text(encoding="utf-8"))
    traces = [
        find_cell(t173, "T170_COMPOSED_FINAL", "p30", 0.080),
        find_cell(t173, "T170_COMPOSED_HALF", "p30", 0.080),
        find_cell(t173, "T170_COMPOSED_FINAL", "p31_34", 0.080),
        find_cell(t173, "T170_COMPOSED_FINAL", "p30", 0.077),
    ]
    graph_by_step = {
        int(row["step"]): row["structure"]["transformed"]
        for row in t172["graphs"]
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
    frozen = {
        "builder": receipt(BUILDER),
        "runner": receipt(RUNNER),
        "test": receipt(TEST),
        "t173_result": receipt(T173),
        "t172_result": receipt(T172),
        "t167_result": receipt(T167),
    }
    checks = {
        "t173_is_exact_15_of_16_hold": (
            t173["status"] == "HOLD_T173_T170_TARGETED_Y_NEGATIVE"
            and t173["condition"]["green_cells"] == 15
        ),
        "one_failing_cell_is_final_p30_x008": (
            traces[0]["cell_green"] is False
            and traces[0]["samples"] == 281
            and traces[0]["termination_reason"] == "fall_or_nan"
            and all(row["cell_green"] for row in traces[1:])
        ),
        "paired_traces_present": all(
            Path(row["trace"]["path"]).is_file() for row in traces
        ),
        "two_composed_graphs_present": (
            set(graphs) == {"half", "final"}
            and all(Path(row["path"]).is_file() for row in graphs.values())
        ),
        "two_y_negative_contexts_exact": set(contexts) == {"p30", "p31_34"},
        "read_only_no_behavior_training_hosted_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T174 preregistration checks failed: {failed}")
    basis: dict[str, Any] = {
        "schema_version": (
            "open_duck.t174_t173_failure_autopsy_preregistration.v1"
        ),
        "status": "PREREGISTERED_T174_T173_FAILURE_AUTOPSY",
        "question": (
            "Where does the sole final/P30/x=.08 fall first diverge from "
            "the matched halfway pass, and which action coordinates carry "
            "the exact half/final head difference on protected trace states?"
        ),
        "frozen_inputs": frozen,
        "graphs": graphs,
        "contexts": contexts,
        "traces": traces,
        "analysis": {
            "recorded_onnx_replay": "all stored rows, exact",
            "cross_checkpoint_replay": [
                "failing final/P30/x=.08 states",
                "passing half/P30/x=.08 states",
            ],
            "paired_dynamics": (
                "half versus final P30/x=.08 tick-aligned prefix"
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
            "pass": "FILE_T174_CAUSAL_AUTOPSY_FOR_MECHANISM_SELECTION",
            "fail": "HOLD_MECHANISM_SELECTION_AND_AUDIT_TRACE_INTEGRITY",
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
        "# T174 T173 failure autopsy preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Inputs: four frozen T173 traces and both T170 composed graphs\n"
        "- Work: exact replay and tick-aligned read-only attribution\n"
        "- Behavior/training/hosted/robot: `0/0/0/0`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(
        "contract_sha256="
        f"{value['preregistered_contract_sha256']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
