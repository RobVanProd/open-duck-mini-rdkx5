#!/usr/bin/env python3
"""Preregister T203's saved-trace roll-risk persistence autopsy."""

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
T201B = ANALYSIS / "t201b_roll_risk_source_transfer_result.json"
T202 = ANALYSIS / "t202_predicted_roll_risk_cpu_preregistration.json"
T204 = ANALYSIS / "t204_t203_recovered_training_validation.json"
T205 = ANALYSIS / "t205_t203_postexport_composition_result.json"
T206 = ANALYSIS / "t206_t203_nominal_matrix_result.json"
T207 = ANALYSIS / "t207_t203_targeted_y_negative_result.json"
T167 = ANALYSIS / "t167_calibration_context_separability_result.json"
OUTPUT = ANALYSIS / "t208_t203_persistence_autopsy_preregistration.json"
MARKDOWN = (
    ANALYSIS / "T208_T203_PERSISTENCE_AUTOPSY_PREREGISTRATION_20260730.md"
)
BUILDER = Path(__file__).resolve()
RUNNER = ROOT / "tools" / "run_t208_t203_persistence_autopsy.py"
TEST = ROOT / "tests" / "test_t208_t203_persistence_autopsy.py"


def find_cells(result: dict[str, Any]) -> list[dict[str, Any]]:
    cells = []
    for block in result["blocks"]:
        for cell in block["result"]["cells"]:
            trace = Path(cell["protection"]["path"])
            cells.append(
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
    return cells


def find_one(
    cells: list[dict[str, Any]],
    checkpoint: str,
    fit: str,
    command: float,
) -> dict[str, Any]:
    return next(
        row
        for row in cells
        if row["checkpoint_id"] == checkpoint
        and row["fit_id"] == fit
        and row["command_x_m_s"] == command
    )


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T208: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T208 preregistration requires clean worktree")

    paths = {
        "t198_result": T198,
        "t201b_roll_signal": T201B,
        "t202_cpu_preregistration": T202,
        "t204_training_validation": T204,
        "t205_composition": T205,
        "t206_nominal_result": T206,
        "t207_targeted_result": T207,
        "t167_contexts": T167,
    }
    values = {
        name: json.loads(path.read_text(encoding="utf-8"))
        for name, path in paths.items()
    }
    t198 = values["t198_result"]
    t201b = values["t201b_roll_signal"]
    t202 = values["t202_cpu_preregistration"]
    t204 = values["t204_training_validation"]
    t205 = values["t205_composition"]
    t206 = values["t206_nominal_result"]
    t207 = values["t207_targeted_result"]
    t167 = values["t167_contexts"]

    traces = find_cells(t207)
    old_cells = find_cells(t198)
    old_failure = find_one(
        old_cells, "T194_COMPOSED_HALF", "p31_34", 0.077
    )
    new_failure = find_one(
        traces, "T203_COMPOSED_FINAL", "p31_34", 0.077
    )
    new_paired_pass = find_one(
        traces, "T203_COMPOSED_HALF", "p31_34", 0.077
    )
    graph_by_step = {
        int(row["step"]): row["structure"]["transformed"]
        for row in t205["graphs"]
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
    hosted_cost = [float(value) for value in t204["roll_metrics"]["cost"]]
    hosted_excess = [
        float(value) for value in t204["roll_metrics"]["excess"]
    ]
    mechanism = t202["mechanism"]
    checks = {
        "t207_is_exact_15_of_16_hold": (
            t207["status"] == "HOLD_T207_T203_TARGETED_Y_NEGATIVE"
            and t207["decision"]
            == "CLOSE_T203_PREDICTED_ROLL_RISK_CONTINUATION"
            and t207["condition"]["green_cells"] == 15
        ),
        "new_failure_is_final_p31_x0077_only": (
            new_failure["cell_green"] is False
            and new_failure["samples"] == 363
            and new_failure["termination_reason"] == "fall_or_nan"
            and sum(not row["cell_green"] for row in traces) == 1
        ),
        "matched_half_cell_and_nominal_matrix_pass": (
            new_paired_pass["cell_green"]
            and new_paired_pass["samples"] == 600
            and t206["status"] == "PASS_T206_T203_NOMINAL_MATRIX"
            and t206["condition"]["green_cells"] == 16
        ),
        "old_t194_failure_exact": (
            old_failure["cell_green"] is False
            and old_failure["samples"] == 308
            and old_failure["termination_reason"] == "fall_or_nan"
        ),
        "sixteen_new_traces_and_old_failure_present": (
            len(traces) == 16
            and all(Path(row["trace"]["path"]).is_file() for row in traces)
            and Path(old_failure["trace"]["path"]).is_file()
        ),
        "two_composed_graphs_present": (
            set(graphs) == {"half", "final"}
            and all(Path(row["path"]).is_file() for row in graphs.values())
        ),
        "two_y_negative_contexts_exact": set(contexts) == {"p30", "p31_34"},
        "t201b_roll_signal_green": (
            t201b["status"] == "PASS_T201B_ROLL_RISK_SOURCE_TRANSFER"
            and t201b["separation_rule_passed"]
            and t201b["combined_passing_envelope_rad"]
            == mechanism["passing_envelope_rad"]
            and t201b["prediction_horizon_s"]
            == mechanism["prediction_horizon_s"]
        ),
        "t204_training_validation_green": (
            t204["status"]
            == "PASS_T204_T203_RECOVERED_TRAINING_VALIDATION"
            and not t204["failed_checks"]
            and len(hosted_cost) == 3
            and len(hosted_excess) == 3
        ),
        "read_only_no_behavior_training_hosted_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T208 preregistration checks failed: {failed}")

    basis: dict[str, Any] = {
        "schema_version": (
            "open_duck.t208_t203_persistence_autopsy_"
            "preregistration.v1"
        ),
        "status": "PREREGISTERED_T208_T203_PERSISTENCE_AUTOPSY",
        "question": (
            "Did the frozen predicted-roll signal remain pass-separable in "
            "T203 while the fixed-price continuation lost persistence from "
            "half to final, thereby earning a separate adaptive cost channel "
            "for CPU-contract work only?"
        ),
        "frozen_inputs": {
            name: receipt(path)
            for name, path in {
                "builder": BUILDER,
                "runner": RUNNER,
                "test": TEST,
                **paths,
            }.items()
        },
        "graphs": graphs,
        "contexts": contexts,
        "traces": traces,
        "old_t194_failure": old_failure,
        "analysis": {
            "prediction_horizon_s": mechanism["prediction_horizon_s"],
            "passing_envelope_rad": mechanism["passing_envelope_rad"],
            "fixed_cost_scale": mechanism["scale"],
            "cost": (
                "scale * square(max(0, "
                "abs(roll + horizon*roll_rate) - envelope))"
            ),
            "recorded_onnx_replay": "all 16 T207 traces, exact",
            "signal_retention_rule": {
                "all_15_passing_exceedance_rows": 0,
                "failure_minimum_exceedance_rows": 1,
                "minimum_failure_lead_ticks": 4,
                "failure_integral_strictly_exceeds_every_pass": True,
            },
            "fixed_price_drift_rule": {
                "hosted_cost_half_strictly_less_than_step_zero": True,
                "hosted_cost_final_strictly_greater_than_half": True,
                "hosted_excess_half_strictly_less_than_step_zero": True,
                "hosted_excess_final_strictly_greater_than_half": True,
                "paired_half_pass_final_failure": True,
            },
            "hosted_metric_order": ["step_zero", "half", "final"],
            "hosted_cost": hosted_cost,
            "hosted_excess": hosted_excess,
            "selection_weight": 0,
        },
        "decision_rule": {
            "signal_retained_and_fixed_price_drifted": (
                "EARN_T209_DUAL_ROLL_COST_CPU_CONTRACT_"
                "PREREGISTRATION_ONLY"
            ),
            "otherwise": (
                "RETURN_TO_MECHANISM_SELECTION_WITHOUT_DUAL_ROLL_COST"
            ),
            "no_optimizer_or_behavior": True,
        },
        "checks": checks,
        "failed_checks": failed,
        "execution_now": {
            "inference_rows": 0,
            "trace_rows": 0,
            "behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "execute_read_only_autopsy": True,
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
        "# T208 T203 persistence autopsy preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Inputs: all 16 frozen T207 traces, the old T194 failure, both "
        "T203 heads, and hosted objective metrics\n"
        "- Work: exact replay, frozen risk census, half-to-final drift audit\n"
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
