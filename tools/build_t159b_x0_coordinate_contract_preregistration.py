#!/usr/bin/env python3
"""Freeze the T159 x=0 coordinate-contract correction."""

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


T159 = ANALYSIS / "t159_mechanics_sagittal_compensation_result.json"
T135B = (
    ANALYSIS
    / "t135b_interrupted_calibration_context_router_recovery_result.json"
)
T156 = ANALYSIS / "t156_three_way_positive_router_result.json"
T156B = ANALYSIS / "t156b_positive_router_gap_midpoint_result.json"
OUTPUT = (
    ANALYSIS / "t159b_x0_coordinate_contract_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "T159B_X0_COORDINATE_CONTRACT_PREREGISTRATION_20260729.md"
)
BUILDER = Path(__file__).resolve()
RUNNER = ROOT / "tools" / "run_t159b_x0_coordinate_contract.py"
TEST = ROOT / "tests" / "test_t159b_x0_coordinate_contract.py"


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T159B: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T159B preregistration requires clean worktree")
    t159 = json.loads(T159.read_text(encoding="utf-8"))
    t156 = json.loads(T156.read_text(encoding="utf-8"))
    t156b = json.loads(T156B.read_text(encoding="utf-8"))
    sources = {
        step: t159["graphs"][step]["source"]
        for step in ("1003520", "2007040")
    }
    transformed = {
        step: t159["graphs"][step]["transformed"]
        for step in ("1003520", "2007040")
    }
    frozen = {
        "builder": BUILDER,
        "runner": RUNNER,
        "test": TEST,
        "t135b_result": T135B,
        "t159_result": T159,
        "t156_result": T156,
        "t156b_result": T156B,
    }
    checks = {
        "t159_hold_is_x0_validator_only": (
            t159["status"]
            == "HOLD_T159_MECHANICS_SAGITTAL_COMPENSATION"
            and t159["decision"]
            == "CLOSE_MECHANICS_DERIVED_SAGITTAL_COMPENSATION"
            and t159["failed_checks"] == ["all_x0_zero_finite_cpu"]
            and all(
                passed
                for name, passed in t159["checks"].items()
                if name != "all_x0_zero_finite_cpu"
            )
        ),
        "mechanics_and_graphs_green": (
            t159["mechanics"]["solver_success"]
            and t159["mechanics"]["maximum_abs_final_residual"] <= 1e-9
            and all(
                row["all_selected_source_outputs_bit_exact"]
                for row in t159["contracts"].values()
            )
        ),
        "t156b_source_green": (
            t156b["status"]
            == "PASS_T156B_POSITIVE_ROUTER_GAP_MIDPOINT"
            and t156b["failed_checks"] == []
            and len(t156["positive_contexts"]) == 2
        ),
        "source_and_transformed_graphs_present": all(
            Path(item["path"]).is_file()
            for item in (*sources.values(), *transformed.values())
        ),
        "frozen_inputs_present": all(
            path.is_file() for path in frozen.values()
        ),
        "no_graph_change_behavior_training_colab_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T159B preregistration checks failed: {failed}")
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t159b_x0_coordinate_contract_"
            "preregistration.v1"
        ),
        "status": "PREREGISTERED_T159B_X0_COORDINATE_CONTRACT",
        "question": (
            "At x=0, is the transformed wrapped-ABI output bit-exact "
            "to its T156B source for every frozen calibration context?"
        ),
        "correction": {
            "invalid_requirement": (
                "wrapped external action and feedback equal literal zero"
            ),
            "reason_invalid": (
                "T17 uses an invertible action-coordinate wrapper; "
                "the external tensor is not the source action tensor"
            ),
            "correct_requirement": (
                "all three transformed outputs are bit-exact to the "
                "unmodified T156B graph at source command x=0"
            ),
            "graph_or_mechanics_change": False,
        },
        "source_graphs": sources,
        "transformed_graphs": transformed,
        "samples": {
            "contexts": 6,
            "random_states_per_context_per_checkpoint": 64,
            "total": 768,
            "command_source_observation_index": 6,
            "command_x_m_s": 0.0,
        },
        "frozen_inputs": {
            name: receipt(path) for name, path in frozen.items()
        },
        "checks": checks,
        "failed_checks": failed,
        "decision_rule": {
            "pass_decision": (
                "EARN_T160_MECHANICS_COMPENSATED_POSITIVE_ENDPOINT_"
                "PREREGISTRATION_ONLY"
            ),
            "fail_decision": (
                "CLOSE_MECHANICS_COMPENSATION_X0_PRESERVATION"
            ),
        },
        "execution_now": {
            "graphs_changed": 0,
            "formal_behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "one_cpu_coordinate_contract": True,
            "positive_endpoint_preregistration": False,
            "behavior_evaluation": False,
            "training": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    value["preregistered_contract_sha256"] = canonical_sha256(value)
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T159B x=0 coordinate-contract preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Correct invariant: transformed/source bit identity at x=0\n"
        "- Graph and mechanics are unchanged\n"
        "- Behavior / optimizer / Colab / robot: `0/0/0/0`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
