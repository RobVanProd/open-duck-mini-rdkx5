#!/usr/bin/env python3
"""Preregister the read-only T237 home-offset route autopsy."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from run_t136_static_calibration_router_transform import (
    ANALYSIS,
    ROOT,
    canonical_sha256,
    receipt,
)


T167 = ANALYSIS / "t167_calibration_context_separability_result.json"
T234B = ANALYSIS / "t234b_abi_helper_recovery_result.json"
T237 = ANALYSIS / "t237_exact_low_command_full_r2_result.json"
OUTPUT = ANALYSIS / "t238_home_offset_route_autopsy_preregistration.json"
MARKDOWN = (
    ANALYSIS
    / "T238_HOME_OFFSET_ROUTE_AUTOPSY_PREREGISTRATION_20260731.md"
)
BUILDER = Path(__file__).resolve()
RUNNER = ROOT / "tools" / "run_t238_home_offset_route_autopsy.py"
TEST = ROOT / "tests" / "test_t238_home_offset_route_autopsy.py"

CONDITIONS = ("FLOOR_FRICTION_LO", "HOME_JOINT_OFFSET_NEG")
MOVING_COMMANDS = (0.074, 0.077, 0.08)


def frozen_blocks(result: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for block in result["blocks"]:
        if block["condition_id"] not in CONDITIONS:
            continue
        cells: list[dict[str, Any]] = []
        for cell in block["result"]["cells"]:
            command = float(cell["command_x_m_s"])
            if command not in MOVING_COMMANDS:
                continue
            cells.append(
                {
                    "command_x_m_s": command,
                    "cell_green": bool(cell["cell_green"]),
                    "core_pass": bool(cell["behavior"]["core_pass"]),
                    "replacement_quality_pass": bool(
                        cell["behavior"]["replacement_quality_pass"]
                    ),
                    "duration_protection_pass": bool(
                        cell["protection"]["duration_protection_pass"]
                    ),
                    "termination_reason": cell["behavior"][
                        "termination_reason"
                    ],
                    "samples": int(cell["behavior"]["samples"]),
                    "context_sha256": cell["handoff"]["context_sha256"],
                    "trace": receipt(Path(cell["protection"]["path"])),
                }
            )
        rows.append(
            {
                "condition_id": block["condition_id"],
                "condition_index": int(block["condition_index"]),
                "checkpoint_id": block["checkpoint_id"],
                "step": int(block["step"]),
                "fit_id": block["fit_id"],
                "cells": cells,
            }
        )
    return rows


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T238: {path}")

    t167 = json.loads(T167.read_text(encoding="utf-8"))
    t234b = json.loads(T234B.read_text(encoding="utf-8"))
    t237 = json.loads(T237.read_text(encoding="utf-8"))
    blocks = frozen_blocks(t237)
    graphs = [
        {
            "role": graph["role"],
            "step": int(graph["step"]),
            **receipt(Path(graph["structure"]["transformed"]["path"])),
        }
        for graph in t234b["graphs"]
    ]
    condition_rows = {
        row["condition_id"]: row for row in t237["conditions"]
    }
    checks = {
        "t167_has_forty_finite_contexts": (
            t167["summary"]["contexts"] == 40
            and len(t167["cells"]) == 40
            and t167["execution"]["formal_behavior_cells"] == 0
        ),
        "t234b_graph_pair_exact": (
            t234b["status"] == "PASS_T234B_ABI_HELPER_RECOVERY"
            and not t234b["failed_checks"]
            and {row["role"] for row in graphs} == {"half", "final"}
            and all(Path(row["path"]).is_file() for row in graphs)
        ),
        "t237_closed_at_home_offset_negative": (
            t237["status"] == "HOLD_T237_EXACT_LOW_COMMAND_FULL_R2"
            and t237["decision"]
            == "CLOSE_EXACT_LOW_COMMAND_HEAD_ROUTE_AT_FIRST_FAILED_R2_CONDITION"
            and t237["summary"]["completed_conditions"] == 17
            and t237["summary"]["first_failed_condition"]
            == "HOME_JOINT_OFFSET_NEG"
        ),
        "matched_pass_and_failure_blocks_exact": (
            len(blocks) == 8
            and all(len(block["cells"]) == 3 for block in blocks)
            and {
                (
                    block["condition_id"],
                    block["checkpoint_id"],
                    block["fit_id"],
                )
                for block in blocks
            }
            == {
                (condition, checkpoint, fit)
                for condition in CONDITIONS
                for checkpoint in (
                    "T234_EXACT_LOW_COMMAND_HALF",
                    "T234_EXACT_LOW_COMMAND_FINAL",
                )
                for fit in ("p30", "p31_34")
            }
        ),
        "matched_condition_passed_and_home_offset_failed": (
            condition_rows["FLOOR_FRICTION_LO"]["condition_green"] is True
            and condition_rows["FLOOR_FRICTION_LO"]["green_cells"] == 16
            and condition_rows["HOME_JOINT_OFFSET_NEG"][
                "condition_green"
            ]
            is False
            and condition_rows["HOME_JOINT_OFFSET_NEG"]["green_cells"] == 0
        ),
        "read_only_no_simulator_optimizer_hosted_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T238 preregistration checks failed: {failed}")

    basis: dict[str, Any] = {
        "schema_version": (
            "open_duck.t238_home_offset_route_autopsy_preregistration.v1"
        ),
        "status": "PREREGISTERED_T238_HOME_OFFSET_ROUTE_AUTOPSY",
        "question": (
            "Did the frozen positive-COM context router falsely send "
            "HOME_JOINT_OFFSET_NEG through the shared positive expert, "
            "bypassing the checkpoint-specific adapter that passed the "
            "first sixteen R2 conditions?"
        ),
        "frozen_inputs": {
            "builder": receipt(BUILDER),
            "runner": receipt(RUNNER),
            "test": receipt(TEST),
            "t167_contexts": receipt(T167),
            "t234b_graphs": receipt(T234B),
            "t237_result": receipt(T237),
        },
        "graphs": graphs,
        "blocks": blocks,
        "analysis": {
            "replay": (
                "compute the exact negative, positive, and hidden router "
                "scores from frozen ONNX initializers, stored calibration "
                "contexts, and stored h_out rows"
            ),
            "positive_router_population": (
                "classify all forty T167 contexts and list every condition "
                "selected by the positive router"
            ),
            "checkpoint_path_identity": (
                "compare half/final positive adapter initializers and paired "
                "trace hashes for each fit and moving command"
            ),
            "readback_attribution": (
                "record the separate scalar-to-vector equality defect in the "
                "legacy R2 readback verifier without using it to excuse any "
                "moving fall"
            ),
        },
        "classification_rule": {
            "positive_router_false_positive_home_offset_if": {
                "positive_router_selects_exactly_x_positive_and_home_negative": (
                    True
                ),
                "home_negative_selects_positive_in_both_fits": True,
                "matched_floor_condition_does_not_select_positive": True,
                "positive_adapter_is_identical_between_checkpoints": True,
                "home_negative_half_final_traces_are_pairwise_identical": True,
                "all_home_negative_moving_cells_fall_with_quality_and_protection_green": (
                    True
                ),
                "x_positive_condition_passed_sixteen_of_sixteen": True,
            },
            "pass_decision": (
                "EARN_T239_X_POSITIVE_ROUTER_SEPARABILITY_"
                "PREREGISTRATION_ONLY"
            ),
            "otherwise": (
                "RETURN_TO_HOME_OFFSET_MECHANISM_SELECTION_WITHOUT_ROUTER_"
                "CORRECTION"
            ),
            "no_behavior_or_training_authorized": True,
        },
        "checks": checks,
        "failed_checks": failed,
        "execution_now": {
            "trace_rows": 0,
            "onnx_inference_rows": 0,
            "behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_sessions": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "execute_read_only_autopsy": True,
            "router_separability_preregistration": False,
            "behavior": False,
            "training": False,
            "hosted": False,
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
        "# T238 home-offset route autopsy preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Frozen data: `24` moving traces from the matched pass and "
        "condition-17 failure\n"
        "- Question: positive-COM router false positive versus a new gait "
        "failure\n"
        "- Simulator/behavior/training/hosted/robot: `0/0/0/0/0`\n"
        f"- Contract SHA-256: `{value['preregistered_contract_sha256']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
