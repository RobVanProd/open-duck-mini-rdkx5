#!/usr/bin/env python3
"""Preregister the read-only T228 nominal closed-loop failure autopsy."""

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


T219 = ANALYSIS / "t219_t216_nominal_matrix_result.json"
T228 = ANALYSIS / "t228_command_atom_hosted_preregistration.json"
T229 = ANALYSIS / "t229_t228_recovered_training_validation.json"
T230 = ANALYSIS / "t230_t228_deployment_composition_result.json"
T231 = ANALYSIS / "t231_t228_nominal_matrix_result.json"
OUTPUT = ANALYSIS / "t232_t228_nominal_failure_autopsy_preregistration.json"
MARKDOWN = (
    ANALYSIS
    / "T232_T228_NOMINAL_FAILURE_AUTOPSY_PREREGISTRATION_20260730.md"
)
BUILDER = Path(__file__).resolve()
RUNNER = ROOT / "tools" / "run_t232_t228_nominal_failure_autopsy.py"
TEST = ROOT / "tests" / "test_t232_t228_nominal_failure_autopsy.py"

COMMANDS = (0.074, 0.077)
FITS = ("p30", "p31_34")


def cells(result: dict[str, Any]) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    for block in result["blocks"]:
        for cell in block["result"]["cells"]:
            found.append(
                {
                    "checkpoint_id": block["checkpoint_id"],
                    "step": int(block["step"]),
                    "fit_id": block["fit_id"],
                    "command_x_m_s": float(cell["command_x_m_s"]),
                    "cell_green": bool(cell["cell_green"]),
                    "samples": int(cell["behavior"]["samples"]),
                    "core_pass": bool(cell["behavior"]["core_pass"]),
                    "replacement_quality_pass": bool(
                        cell["behavior"]["replacement_quality_pass"]
                    ),
                    "termination_reason": cell["behavior"][
                        "termination_reason"
                    ],
                    "duration_protection_pass": bool(
                        cell["protection"]["duration_protection_pass"]
                    ),
                    "strict_overcurrent_run_ticks": int(
                        cell["protection"][
                            "worst_strict_overcurrent_run_ticks"
                        ]
                    ),
                    "strict_overload_run_ticks": int(
                        cell["protection"][
                            "worst_strict_overload_run_ticks"
                        ]
                    ),
                    "trace": receipt(Path(cell["protection"]["path"])),
                }
            )
    return found


def select(
    rows: list[dict[str, Any]],
    checkpoint_id: str,
) -> list[dict[str, Any]]:
    return [
        row
        for row in rows
        if row["checkpoint_id"] == checkpoint_id
        and row["fit_id"] in FITS
        and row["command_x_m_s"] in COMMANDS
    ]


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T232: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T232 preregistration requires a clean worktree")

    inputs = {
        name: json.loads(path.read_text(encoding="utf-8"))
        for name, path in {
            "t219": T219,
            "t228": T228,
            "t229": T229,
            "t230": T230,
            "t231": T231,
        }.items()
    }
    t219_cells = cells(inputs["t219"])
    t231_cells = cells(inputs["t231"])
    source = select(t219_cells, "T216_COMPOSED_FINAL")
    half = select(t231_cells, "T228_COMMAND_ATOM_HALF")
    final = select(t231_cells, "T228_COMMAND_ATOM_FINAL")

    graphs = {
        str(int(row["step"])): {
            "role": row["role"],
            **receipt(Path(row["plateau"]["path"])),
        }
        for row in inputs["t230"]["graphs"]
    }
    eval_cost = inputs["t229"]["metrics"]["eval"][
        "eval/episode_cost/winner_v127_dense_torque_exceedance"
    ]
    eval_reward = inputs["t229"]["metrics"]["eval"]["eval/episode_reward"]
    policy_updates = inputs["t229"]["exports"]["policy_updates"]
    changed_leaf_names = sorted(
        {
            name
            for update in policy_updates
            for name in update["trainable_actor_leaf_deltas"]
        }
    )
    all_t231_failures = [
        row for row in t231_cells if not row["cell_green"]
    ]

    checks = {
        "t228_formally_closed_at_t231": (
            inputs["t231"]["status"] == "HOLD_T231_T228_NOMINAL_MATRIX"
            and inputs["t231"]["decision"]
            == "CLOSE_T228_COMMAND_ATOM_CONTINUATION"
            and inputs["t231"]["condition"]["green_cells"] == 8
            and inputs["t231"]["condition"]["cells"] == 16
        ),
        "paired_trace_lattice_exact": (
            len(source) == len(half) == len(final) == 4
            and {
                (row["fit_id"], row["command_x_m_s"]) for row in source
            }
            == {
                (fit, command) for fit in FITS for command in COMMANDS
            }
            and all(
                Path(row["trace"]["path"]).is_file()
                for row in source + half + final
            )
        ),
        "source_is_four_of_four_green": all(
            row["cell_green"] and row["samples"] == 600 for row in source
        ),
        "t228_final_is_zero_of_four_green": all(
            not row["cell_green"] for row in final
        ),
        "every_t231_failure_is_fall_with_quality_and_protection_green": all(
            row["termination_reason"] == "fall_or_nan"
            and row["replacement_quality_pass"]
            and row["duration_protection_pass"]
            for row in all_t231_failures
        ),
        "no_t231_duration_trip": all(
            row["strict_overcurrent_run_ticks"] < 100
            and row["strict_overload_run_ticks"] < 100
            for row in t231_cells
        ),
        "only_negative_adapter_location_trainable": (
            changed_leaf_names
            == [
                "1/params/negative_adapter_location/bias",
                "1/params/negative_adapter_location/kernel",
            ]
            and all(
                update["every_mature_actor_leaf_exact"]
                and update["normalizer_exact"]
                for update in policy_updates
            )
        ),
        "three_frozen_graphs_present": (
            set(graphs) == {"0", "1003520", "2007040"}
            and all(Path(row["path"]).is_file() for row in graphs.values())
        ),
        "hosted_metrics_have_three_exact_steps": (
            [int(row["step"]) for row in eval_cost]
            == [0, 1_003_520, 2_007_040]
            and [int(row["step"]) for row in eval_reward]
            == [0, 1_003_520, 2_007_040]
        ),
        "read_only_no_behavior_training_hosted_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, value in checks.items() if not value)
    if failed:
        raise RuntimeError(f"T232 preregistration checks failed: {failed}")

    basis: dict[str, Any] = {
        "schema_version": (
            "open_duck.t232_t228_nominal_failure_autopsy_"
            "preregistration.v1"
        ),
        "status": "PREREGISTERED_T232_T228_NOMINAL_FAILURE_AUTOPSY",
        "question": (
            "Did T228 improve its hosted randomized constraint objective "
            "while the only trainable negative-adapter output head drifted "
            "the previously passing nominal closed-loop attractor into "
            "falls?"
        ),
        "frozen_inputs": {
            name: receipt(path)
            for name, path in {
                "builder": BUILDER,
                "runner": RUNNER,
                "test": TEST,
                "t219_result": T219,
                "t228_preregistration": T228,
                "t229_validation": T229,
                "t230_composition": T230,
                "t231_result": T231,
            }.items()
        },
        "graphs": graphs,
        "traces": {
            "source_t216_final": source,
            "t228_half": half,
            "t228_final": final,
        },
        "hosted_metrics": {
            "eval_dense_torque_cost": eval_cost,
            "eval_reward": eval_reward,
        },
        "analysis": {
            "joint_order": [
                "left_hip_yaw",
                "left_hip_roll",
                "left_hip_pitch",
                "left_knee",
                "left_ankle",
                "neck_yaw",
                "head_pitch",
                "head_roll",
                "head_yaw",
                "right_hip_yaw",
                "right_hip_roll",
                "right_hip_pitch",
                "right_knee",
                "right_ankle",
            ],
            "graph_scope": (
                "verify source-to-half/final initializer changes are exactly "
                "nominal_condition_negative_adapter_weight and bias"
            ),
            "head_replay": (
                "on every frozen source trace row, compute the source, half, "
                "and final nominal-condition adapter locations from the "
                "stored h_out; report gate duty and per-command/per-joint "
                "head deltas"
            ),
            "closed_loop_drift": (
                "tick-align source against half/final for each fit and "
                "command; report first action/state divergence, prefix RMS, "
                "termination precursors, pitch, force, and contact changes"
            ),
            "hosted_distribution": (
                "compare exact step-0/half/final eval cost, reward, and "
                "episode length without assigning selection weight"
            ),
            "thresholds": {
                "nonzero_float32_effect": float(2**-23),
                "prefix_ticks": 64,
                "termination_precursor_ticks": 64,
                "trip_ticks": 100,
            },
        },
        "classification_rule": {
            "training_distribution_cost_improvement_with_nominal_attractor_loss_if": {
                "hosted_eval_cost_half_and_final_below_step_zero": True,
                "source_four_of_four_green": True,
                "t228_final_zero_of_four_green": True,
                "all_failures_are_falls_not_quality_or_duration_trips": True,
                "only_trainable_head_changed": True,
                "trained_head_nonzero_on_every_source_moving_trace": True,
            },
            "pass_decision": (
                "EARN_T233_SOURCE_ATTRACTOR_PRESERVATION_CPU_FALSIFIER_"
                "PREREGISTRATION_ONLY"
            ),
            "otherwise": (
                "RETURN_TO_MECHANISM_SELECTION_WITHOUT_ATTRACTOR_"
                "PRESERVATION"
            ),
            "no_checkpoint_selection": True,
            "no_hosted_run_authorized": True,
        },
        "checks": checks,
        "failed_checks": failed,
        "execution_now": {
            "trace_rows": 0,
            "inference_rows": 0,
            "behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_sessions": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "execute_read_only_autopsy": True,
            "cpu_falsifier_preregistration": False,
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
        "# T232 T228 nominal failure autopsy preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Frozen rows: source-final, T228-half, and T228-final at both "
        "fits and x=.074/.077\n"
        "- Question: hosted cost improvement versus nominal closed-loop "
        "attractor loss\n"
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
