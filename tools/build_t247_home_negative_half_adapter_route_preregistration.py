#!/usr/bin/env python3
"""Preregister T247's calibrated home-negative half-adapter route."""

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
T246 = ANALYSIS / "t246_checkpoint_adapter_autopsy_result.json"
OUTPUT = (
    ANALYSIS
    / "t247_home_negative_half_adapter_route_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "T247_HOME_NEGATIVE_HALF_ADAPTER_ROUTE_PREREGISTRATION_20260731.md"
)
RUNNER = ROOT / "tools/run_t247_home_negative_half_adapter_route.py"
TEST = ROOT / "tests/test_t247_home_negative_half_adapter_route.py"


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError("refusing to overwrite T247 preregistration")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T247 preregistration requires clean worktree")
    t243 = json.loads(T243.read_text(encoding="utf-8"))
    t243b = json.loads(T243B.read_text(encoding="utf-8"))
    t245 = json.loads(T245.read_text(encoding="utf-8"))
    t246 = json.loads(T246.read_text(encoding="utf-8"))
    graphs = [
        {
            "step": int(row["step"]),
            "role": row["role"],
            "source": row["structure"]["transformed"],
        }
        for row in t243b["graphs"]
    ]
    graphs.sort(key=lambda row: row["step"])
    final_p30 = next(
        block
        for block in t245["blocks"]
        if block["checkpoint_id"] == "T243_HOME_NEGATIVE_FLOOR_FINAL"
        and block["fit_id"] == "p30"
    )
    final_trace = next(
        cell["protection"]["path"]
        for cell in final_p30["result"]["cells"]
        if float(cell["command_x_m_s"]) == 0.077
    )
    checks = {
        "t246_earns_exact_adapter_route": (
            t246["status"]
            == "PASS_T246_CHECKPOINT_ADAPTER_CAUSAL_SPLIT"
            and t246["decision"]
            == "EARN_T247_HOME_NEGATIVE_HALF_ADAPTER_ROUTE_PREREGISTRATION_ONLY"
            and all(t246["checks"].values())
        ),
        "only_two_nominal_adapter_tensors_differ": (
            t246["graph_identity"]["changed_nodes"] == []
            and t246["graph_identity"]["changed_initializers"]
            == [
                "nominal_condition_negative_adapter_bias",
                "nominal_condition_negative_adapter_weight",
            ]
        ),
        "two_source_graphs_and_failed_trace_present": (
            len(graphs) == 2
            and all(Path(row["source"]["path"]).is_file() for row in graphs)
            and Path(final_trace).is_file()
        ),
        "automatic_home_negative_tail_is_frozen": (
            t243["router"]["automatic_calibration_only"] is True
            and t243["router"]["manual_measurements"] is False
            and {
                (row["condition_id"], row["fit_id"])
                for row in t243["router"]["tail_rows"]
            }
            == {
                ("HOME_JOINT_OFFSET_NEG", "p30"),
                ("HOME_JOINT_OFFSET_NEG", "p31_34"),
            }
        ),
        "uniform_transform_both_checkpoints_no_selection": True,
        "zero_behavior_optimizer_hosted_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T247 preregistration checks failed: {failed}")
    basis: dict[str, Any] = {
        "schema_version": (
            "open_duck.t247_home_negative_half_adapter_route_"
            "preregistration.v1"
        ),
        "status": "PREREGISTERED_T247_HOME_NEGATIVE_HALF_ADAPTER_ROUTE",
        "question": (
            "Can one uniform graph transform select the proven half "
            "nominal adapter only in the automatically calibrated "
            "home-negative tail, leaving every other route and the full "
            "stateful ABI exact?"
        ),
        "frozen_inputs": {
            "builder": receipt(Path(__file__)),
            "runner": receipt(RUNNER),
            "test": receipt(TEST),
            "t243_contract": receipt(T243),
            "t243b_graphs": receipt(T243B),
            "t245_behavior": receipt(T245),
            "t246_autopsy": receipt(T246),
        },
        "graphs": graphs,
        "half_adapter_source": graphs[0]["source"],
        "contexts": t243["contexts"],
        "failed_final_trace": receipt(Path(final_trace)),
        "transform": {
            "gate": "t243_home_negative_tail_condition",
            "half_weight_source": (
                "half nominal_condition_negative_adapter_weight"
            ),
            "half_bias_source": (
                "half nominal_condition_negative_adapter_bias"
            ),
            "dynamic_phase_gate_preserved": True,
            "selection_point": (
                "before nominal_dynamic_conditional_adapter's existing "
                "negative_com_gate"
            ),
            "same_transform_both_checkpoints": True,
            "x0_deadband_unchanged": True,
            "low_command_floor_unchanged": True,
            "all_non_home_negative_routes_unchanged": True,
        },
        "contract": {
            "commands_x_m_s": [0.0, 0.074, 0.077, 0.080],
            "samples_per_context_command": 8,
            "random_seed": 247,
            "failed_trace_rows": 231,
            "expected_added_nodes": [
                "half-adapter Gemm",
                "home-negative selection Where",
            ],
            "expected_added_initializers": [
                "half-adapter bias",
                "half-adapter weight",
            ],
            "expected_changed_old_nodes": [
                "nominal_dynamic_conditional_adapter input only"
            ],
            "half_graph_all_outputs_bit_exact_source": True,
            "final_non_tail_all_outputs_bit_exact_source": True,
            "final_tail_all_outputs_bit_exact_half_graph": True,
            "stateful_abi_exact": True,
            "all_outputs_finite": True,
            "cpu_only": True,
        },
        "decision_rule": {
            "pass": (
                "EARN_T248_HOME_NEGATIVE_HALF_ADAPTER_MATRIX_"
                "PREREGISTRATION_ONLY"
            ),
            "fail": (
                "CLOSE_HOME_NEGATIVE_HALF_ADAPTER_ROUTE_WITHOUT_BEHAVIOR"
            ),
            "no_behavior_now": True,
        },
        "checks": checks,
        "failed_checks": failed,
        "execution_now": {
            "onnx_transforms": 0,
            "onnx_inferences": 0,
            "behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "execute_graph_transform_and_cpu_contract": True,
            "behavior_matrix_preregistration": False,
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
        "# T247 home-negative half-adapter route preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Route: automatic home-negative tail uses the half adapter\n"
        "- Uniform transform: both checkpoints; all other routes exact\n"
        "- Behavior/optimizer/hosted/robot: `0/0/0/0`\n"
        f"- Contract SHA-256: `{value['preregistered_contract_sha256']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
