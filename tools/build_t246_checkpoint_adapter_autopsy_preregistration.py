#!/usr/bin/env python3
"""Preregister a read-only autopsy of T245's checkpoint split."""

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


T243 = ANALYSIS / "t243_home_negative_low_command_floor_preregistration.json"
T243B = ANALYSIS / "t243b_abi_helper_recovery_result.json"
T245 = ANALYSIS / "t245_home_negative_floor_remaining_matrix_result.json"
OUTPUT = ANALYSIS / "t246_checkpoint_adapter_autopsy_preregistration.json"
MARKDOWN = (
    ANALYSIS
    / "T246_CHECKPOINT_ADAPTER_AUTOPSY_PREREGISTRATION_20260731.md"
)
RUNNER = ROOT / "tools/run_t246_checkpoint_adapter_autopsy.py"
TEST = ROOT / "tests/test_t246_checkpoint_adapter_autopsy.py"


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError("refusing to overwrite T246 preregistration")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T246 preregistration requires clean worktree")
    t243 = json.loads(T243.read_text(encoding="utf-8"))
    t243b = json.loads(T243B.read_text(encoding="utf-8"))
    t245 = json.loads(T245.read_text(encoding="utf-8"))
    half = next(row for row in t243b["graphs"] if row["role"] == "half")
    final = next(row for row in t243b["graphs"] if row["role"] == "final")
    half_p30 = next(
        block
        for block in t245["blocks"]
        if block["checkpoint_id"] == "T243_HOME_NEGATIVE_FLOOR_HALF"
        and block["fit_id"] == "p30"
    )
    final_p30 = next(
        block
        for block in t245["blocks"]
        if block["checkpoint_id"] == "T243_HOME_NEGATIVE_FLOOR_FINAL"
        and block["fit_id"] == "p30"
    )
    half_moving = [
        cell
        for cell in half_p30["result"]["cells"]
        if float(cell["command_x_m_s"]) > 0.0
    ]
    final_moving = [
        cell
        for cell in final_p30["result"]["cells"]
        if float(cell["command_x_m_s"]) > 0.0
    ]
    checks = {
        "t245_split_is_exact_half_pass_final_failure": (
            t245["status"]
            == "HOLD_T245_HOME_NEGATIVE_FLOOR_REMAINING_MATRIX"
            and t245["condition"]["green_cells"] == 9
            and all(cell["cell_green"] for cell in half_moving)
            and all(not cell["cell_green"] for cell in final_moving)
            and {cell["behavior"]["samples"] for cell in half_moving}
            == {600}
            and {cell["behavior"]["samples"] for cell in final_moving}
            == {231}
        ),
        "two_complete_graphs_present": (
            Path(half["structure"]["transformed"]["path"]).is_file()
            and Path(final["structure"]["transformed"]["path"]).is_file()
        ),
        "moving_trace_receipts_present": all(
            Path(cell["protection"]["path"]).is_file()
            for cell in [*half_moving, *final_moving]
        ),
        "home_negative_context_available": any(
            row["condition_id"] == "HOME_JOINT_OFFSET_NEG"
            and row["fit_id"] == "p30"
            for row in t243["contexts"]
        ),
        "zero_behavior_optimizer_hosted_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T246 preregistration checks failed: {failed}")
    basis: dict[str, Any] = {
        "schema_version": (
            "open_duck.t246_checkpoint_adapter_autopsy_"
            "preregistration.v1"
        ),
        "status": "PREREGISTERED_T246_CHECKPOINT_ADAPTER_AUTOPSY",
        "question": (
            "Are T243 half and final structurally identical except for the "
            "two nominal-adapter tensors, with those tensors causally "
            "accounting for the 600-tick half versus 231-tick final split?"
        ),
        "frozen_inputs": {
            "builder": receipt(Path(__file__)),
            "runner": receipt(RUNNER),
            "test": receipt(TEST),
            "t243_contract": receipt(T243),
            "t243b_graph_result": receipt(T243B),
            "t245_behavior": receipt(T245),
        },
        "graphs": {
            "half": half["structure"]["transformed"],
            "final": final["structure"]["transformed"],
        },
        "traces": {
            "half": [
                {
                    "command_x_m_s": cell["command_x_m_s"],
                    "trace": receipt(Path(cell["protection"]["path"])),
                }
                for cell in half_moving
            ],
            "final": [
                {
                    "command_x_m_s": cell["command_x_m_s"],
                    "trace": receipt(Path(cell["protection"]["path"])),
                }
                for cell in final_moving
            ],
        },
        "contract": {
            "expected_different_initializers": [
                "nominal_condition_negative_adapter_bias",
                "nominal_condition_negative_adapter_weight",
            ],
            "expected_different_nodes": [],
            "half_moving_rows": 600,
            "final_moving_rows": 231,
            "final_trace_source_replay_exact": True,
            "half_adapter_counterfactual_action_sensitive": True,
            "within_checkpoint_three_command_trajectories_exact": True,
            "cpu_only": True,
        },
        "decision_rule": {
            "pass": (
                "EARN_T247_HOME_NEGATIVE_HALF_ADAPTER_ROUTE_"
                "PREREGISTRATION_ONLY"
            ),
            "fail": "RETURN_TO_HOME_OFFSET_MECHANISM_SELECTION",
            "no_behavior_now": True,
        },
        "checks": checks,
        "failed_checks": failed,
        "execution_now": {
            "onnx_inferences": 0,
            "simulator_steps": 0,
            "behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "run_read_only_autopsy": True,
            "adapter_route_preregistration": False,
            "training": False,
            "hosted": False,
            "gate5": False,
            "rdkx5_or_robot": False,
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
        "# T246 checkpoint-adapter autopsy preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Compare: half vs final graph identity and moving traces\n"
        "- Expected graph delta: exactly two nominal-adapter tensors\n"
        "- Simulator/behavior/optimizer/hosted/robot: `0/0/0/0/0`\n"
        f"- Contract SHA-256: `{value['preregistered_contract_sha256']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
