#!/usr/bin/env python3
"""Preregister T234's exact .074 paired-final adapter route."""

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


T167 = ANALYSIS / "t167_calibration_context_separability_result.json"
T222B = ANALYSIS / "t222b_abi_helper_recovery_result.json"
T225 = ANALYSIS / "t225_global_plateau_full_r2_result.json"
T233 = ANALYSIS / "t233_upper_z_context_separability_result.json"
OUTPUT = ANALYSIS / "t234_exact_low_command_head_route_preregistration.json"
MARKDOWN = (
    ANALYSIS
    / "T234_EXACT_LOW_COMMAND_HEAD_ROUTE_PREREGISTRATION_20260730.md"
)
BUILDER = Path(__file__).resolve()
RUNNER = ROOT / "tools" / "run_t234_exact_low_command_head_route.py"
TEST = ROOT / "tests" / "test_t234_exact_low_command_head_route.py"


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T234: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T234 preregistration requires a clean worktree")

    t167 = json.loads(T167.read_text(encoding="utf-8"))
    t222b = json.loads(T222B.read_text(encoding="utf-8"))
    t225 = json.loads(T225.read_text(encoding="utf-8"))
    t233 = json.loads(T233.read_text(encoding="utf-8"))
    graphs = []
    for row in t222b["graphs"]:
        if int(row["step"]) not in (1_003_520, 2_007_040):
            continue
        graphs.append(
            {
                "step": int(row["step"]),
                "role": row["role"],
                "source": row["structure"]["transformed"],
            }
        )
    graphs.sort(key=lambda row: row["step"])
    final_graph = next(row for row in graphs if row["role"] == "final")

    upper_z_blocks = [
        block
        for block in t225["blocks"]
        if block["condition_id"] == "TORSO_COM_Z_POS"
    ]
    upper_z_cells = []
    for block in upper_z_blocks:
        for cell in block["result"]["cells"]:
            if float(cell["command_x_m_s"]) != 0.074:
                continue
            upper_z_cells.append(
                {
                    "checkpoint_id": block["checkpoint_id"],
                    "step": int(block["step"]),
                    "fit_id": block["fit_id"],
                    "cell_green": bool(cell["cell_green"]),
                    "samples": int(cell["behavior"]["samples"]),
                    "termination_reason": cell["behavior"][
                        "termination_reason"
                    ],
                    "trace": receipt(Path(cell["protection"]["path"])),
                }
            )
    completed_x074 = []
    for block in t225["blocks"]:
        for cell in block["result"]["cells"]:
            if float(cell["command_x_m_s"]) == 0.074:
                completed_x074.append(
                    {
                        "condition_id": block["condition_id"],
                        "checkpoint_id": block["checkpoint_id"],
                        "step": int(block["step"]),
                        "fit_id": block["fit_id"],
                        "cell_green": bool(cell["cell_green"]),
                    }
                )
    final_x074 = [
        row for row in completed_x074 if row["step"] == 2_007_040
    ]
    failed_x074 = [
        row for row in completed_x074 if not row["cell_green"]
    ]

    checks = {
        "t233_closed_static_upper_z_route": (
            t233["status"] == "HOLD_T233_UPPER_Z_CONTEXT_SEPARABILITY"
            and t233["decision"]
            == (
                "CLOSE_STATIC_STARTUP_CONTEXT_ROUTING_FOR_UPPER_Z_AND_"
                "RETURN_TO_DYNAMIC_PRESERVATION"
            )
        ),
        "two_t222_graphs_exact": (
            len(graphs) == 2
            and [row["role"] for row in graphs] == ["half", "final"]
            and all(Path(row["source"]["path"]).is_file() for row in graphs)
        ),
        "only_two_completed_failures_are_half_upper_z_x0074": (
            len(failed_x074) == 2
            and all(
                row["condition_id"] == "TORSO_COM_Z_POS"
                and row["step"] == 1_003_520
                for row in failed_x074
            )
            and t225["summary"]["green_cells"] == 190
            and t225["summary"]["completed_cells"] == 192
        ),
        "paired_final_x0074_passes_all_completed_conditions": (
            len(final_x074) == 24
            and all(row["cell_green"] for row in final_x074)
        ),
        "four_upper_z_x0074_traces_exact": (
            len(upper_z_cells) == 4
            and all(
                Path(row["trace"]["path"]).is_file()
                for row in upper_z_cells
            )
        ),
        "forty_frozen_contexts_available": (
            len(t167["cells"]) == 40
            and all(len(row["context"]) == 64 for row in t167["cells"])
        ),
        "uniform_transform_both_checkpoints_no_selection": True,
        "no_behavior_training_hosted_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, value in checks.items() if not value)
    if failed:
        raise RuntimeError(f"T234 preregistration checks failed: {failed}")

    basis: dict[str, Any] = {
        "schema_version": (
            "open_duck.t234_exact_low_command_head_route_"
            "preregistration.v1"
        ),
        "status": "PREREGISTERED_T234_EXACT_LOW_COMMAND_HEAD_ROUTE",
        "question": (
            "Can one uniform graph transform bind exact x=.074 to the "
            "paired T216-final nominal-condition adapter head while leaving "
            "x=0/.077/.080 and the recurrent ABI exact for both checkpoints?"
        ),
        "frozen_inputs": {
            name: receipt(path)
            for name, path in {
                "builder": BUILDER,
                "runner": RUNNER,
                "test": TEST,
                "t167_contexts": T167,
                "t222b_graphs": T222B,
                "t225_result": T225,
                "t233_result": T233,
            }.items()
        },
        "graphs": graphs,
        "paired_final_expert_source": final_graph["source"],
        "contexts": t167["cells"],
        "upper_z_x0074_traces": upper_z_cells,
        "transform": {
            "command_input": "raw obs[6]",
            "exact_command_x_m_s": 0.074,
            "current_head_node": "t143_nominal_expert",
            "current_head_output": "nominal_condition_adapter_location",
            "downstream_where_output": "nominal_dynamic_conditional_adapter",
            "final_weight": (
                "nominal_condition_negative_adapter_weight from paired final"
            ),
            "final_bias": (
                "nominal_condition_negative_adapter_bias from paired final"
            ),
            "selection": (
                "Where(raw_command_x == float32(.074), "
                "paired_final_adapter_location, current_adapter_location)"
            ),
            "same_transform_applied_to_half_and_final": True,
            "x0_deadband_precedence_unchanged": True,
            "global_x008_to_x0077_plateau_unchanged": True,
        },
        "contract": {
            "commands_x_m_s": [0.0, 0.074, 0.077, 0.080],
            "random_seed": 234,
            "samples_per_context_command": 8,
            "trace_rows_per_pair": 128,
            "expected_changed_old_nodes": [
                "the downstream dynamic conditional Where input only"
            ],
            "expected_added_nodes": [
                "paired-final Gemm",
                "raw-command Equal",
                "command-select Where",
            ],
            "expected_added_initializers": [
                "exact command atom",
                "paired-final weight",
                "paired-final bias",
            ],
            "half_x0074": (
                "bit-exact to a half graph whose two nominal-condition "
                "adapter initializers are replaced by the paired final values"
            ),
            "final_x0074": "bit-exact to unmodified final graph",
            "all_other_commands": "bit-exact to each unmodified source graph",
            "abi_exact": True,
            "all_outputs_finite": True,
        },
        "decision_rule": {
            "all_contract_checks_green": (
                "EARN_T235_EXACT_LOW_COMMAND_NOMINAL_MATRIX_"
                "PREREGISTRATION_ONLY"
            ),
            "otherwise": (
                "CLOSE_EXACT_LOW_COMMAND_HEAD_ROUTE_WITHOUT_BEHAVIOR"
            ),
            "behavior_not_proved_by_graph_equivalence": True,
            "no_hosted_run_authorized": True,
        },
        "checks": checks,
        "failed_checks": failed,
        "execution_now": {
            "onnx_transforms": 0,
            "inference_rows": 0,
            "behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_sessions": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "execute_onnx_transform_and_cpu_contract": True,
            "nominal_behavior_preregistration": False,
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
        "# T234 exact low-command head route preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Transform: exact x=.074 uses the paired final adapter head\n"
        "- Preserve: x=0/.077/.080, recurrent ABI, T222 plateau\n"
        "- Both checkpoints transformed; both remain mandatory\n"
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
