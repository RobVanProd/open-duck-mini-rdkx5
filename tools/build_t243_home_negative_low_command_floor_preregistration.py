#!/usr/bin/env python3
"""Preregister T243's calibration-routed low-command floor transform."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
from typing import Any

import numpy as np

from run_t136_static_calibration_router_transform import (
    ANALYSIS,
    ROOT,
    canonical_sha256,
    receipt,
)


T167 = ANALYSIS / "t167_calibration_context_separability_result.json"
T240 = ANALYSIS / "t240_bounded_positive_router_result.json"
T241 = ANALYSIS / "t241_bounded_positive_router_transform_result.json"
T242B = ANALYSIS / "t242b_interrupted_reporter_recovery_result.json"
REFERENCE = ANALYSIS / "ground_up_projected_reference_feature_table.npz"
EVALUATOR = ROOT / "tools/closed_loop_sim_eval.py"
JOYSTICK = Path(
    "D:/CodexProjects/Open_Duck_Playground-composed-t19-v6/"
    "playground/open_duck_mini_v2/joystick.py"
)
OUTPUT = (
    ANALYSIS
    / "t243_home_negative_low_command_floor_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "T243_HOME_NEGATIVE_LOW_COMMAND_FLOOR_PREREGISTRATION_20260731.md"
)
RUNNER = ROOT / "tools/run_t243_home_negative_low_command_floor.py"
TEST = ROOT / "tests/test_t243_home_negative_low_command_floor.py"


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError("refusing to overwrite T243 preregistration")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T243 preregistration requires clean worktree")

    t167 = json.loads(T167.read_text(encoding="utf-8"))
    t240 = json.loads(T240.read_text(encoding="utf-8"))
    t241 = json.loads(T241.read_text(encoding="utf-8"))
    t242b = json.loads(T242B.read_text(encoding="utf-8"))
    contexts = t167["cells"]
    graphs = [
        {
            "step": int(row["step"]),
            "role": row["role"],
            "source": row["structure"]["transformed"],
        }
        for row in t241["graphs"]
    ]
    graphs.sort(key=lambda row: row["step"])
    cells = t242b["block"]["result"]["cells"]
    failed = [cell for cell in cells if not cell["cell_green"]]
    passing_077 = next(
        cell for cell in cells if float(cell["command_x_m_s"]) == 0.077
    )
    failed_074 = next(
        cell for cell in cells if float(cell["command_x_m_s"]) == 0.074
    )
    upper = float(t240["combined"]["upper_bound"])
    high_tail = [
        row
        for row in t240["combined"]["rows"]
        if float(row["score"]) > upper
    ]

    table = np.load(REFERENCE)
    commands = np.asarray(table["commands"], dtype=np.float32)
    nearest = {}
    for command in (0.074, 0.077, 0.080):
        query = np.asarray([command, 0.0, 0.0], dtype=np.float32)
        nearest[str(command)] = int(
            np.argmin(np.sum(np.abs(commands - query), axis=1))
        )

    checks = {
        "t242b_is_terminal_single_low_command_failure": (
            t242b["status"]
            == "HOLD_T242B_INTERRUPTED_REPORTER_RECOVERY"
            and t242b["decision"].startswith(
                "CLOSE_BOUNDED_POSITIVE_ROUTER"
            )
            and t242b["block"]["green_cells"] == 3
            and len(failed) == 1
            and float(failed[0]["command_x_m_s"]) == 0.074
            and failed_074["behavior"]["samples"] == 281
            and passing_077["cell_green"] is True
            and passing_077["behavior"]["samples"] == 600
        ),
        "automatic_context_high_tail_is_only_home_negative": (
            len(high_tail) == 2
            and {
                (row["condition_id"], row["fit_id"])
                for row in high_tail
            }
            == {
                ("HOME_JOINT_OFFSET_NEG", "p30"),
                ("HOME_JOINT_OFFSET_NEG", "p31_34"),
            }
        ),
        "t240_tail_margin_is_strict": (
            t240["status"] == "PASS_T240_BOUNDED_POSITIVE_ROUTER"
            and t240["checks"][
                "positive_lower_and_upper_margins_strictly_positive"
            ]
            and float(t240["combined"]["upper_separation_margin"]) > 0.0
        ),
        "two_t241_source_graphs_exact": (
            len(graphs) == 2
            and [row["step"] for row in graphs]
            == [1_003_520, 2_007_040]
            and all(Path(row["source"]["path"]).is_file() for row in graphs)
        ),
        "reference_feature_atom_same_for_three_commands": (
            len(set(nearest.values())) == 1
        ),
        "failed_and_passing_traces_present": (
            Path(failed_074["protection"]["path"]).is_file()
            and Path(passing_077["protection"]["path"]).is_file()
        ),
        "zero_behavior_optimizer_hosted_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed_checks = sorted(
        name for name, passed in checks.items() if not passed
    )
    if failed_checks:
        raise RuntimeError(
            f"T243 preregistration checks failed: {failed_checks}"
        )

    basis: dict[str, Any] = {
        "schema_version": (
            "open_duck.t243_home_negative_low_command_floor_"
            "preregistration.v1"
        ),
        "status": "PREREGISTERED_T243_HOME_NEGATIVE_LOW_COMMAND_FLOOR",
        "question": (
            "Can a deterministic graph transform map only x=.074 in the "
            "automatically calibrated negative-home-offset tail to the "
            "already passing x=.077 policy path, while preserving all other "
            "contexts, commands, recurrent outputs, and safety transforms?"
        ),
        "frozen_inputs": {
            "builder": receipt(Path(__file__)),
            "runner": receipt(RUNNER),
            "test": receipt(TEST),
            "t167_contexts": receipt(T167),
            "t240_router_geometry": receipt(T240),
            "t241_graphs": receipt(T241),
            "t242b_recovery": receipt(T242B),
            "reference_feature_table": receipt(REFERENCE),
            "evaluator": receipt(EVALUATOR),
            "joystick_observation_source": receipt(JOYSTICK),
        },
        "graphs": graphs,
        "contexts": contexts,
        "router": {
            "score_tensor": "duplicate exact t156 positive-router affine",
            "upper_bound_initializer": "t241_positive_router_upper_bound",
            "tail_rule": "score > upper_bound",
            "tail_rows": high_tail,
            "automatic_calibration_only": True,
            "manual_measurements": False,
        },
        "transform": {
            "source_command_tensor": "t222_raw_command_x",
            "base_capped_command_tensor": "t222_capped_command_x",
            "target_command_float32_m_s": float(np.float32(0.074)),
            "floor_command_float32_m_s": float(np.float32(0.077)),
            "condition": (
                "(calibration score > frozen upper bound) AND "
                "(raw command == float32(.074))"
            ),
            "mapped_policy_command": (
                "float32(.077) only when condition is true"
            ),
            "t234_exact_head_gate_uses_mapped_command": True,
            "x0_deadband_unchanged": True,
            "x008_global_cap_unchanged": True,
            "no_policy_parameter_change": True,
        },
        "causal_evidence": {
            "failed_trace": receipt(
                Path(failed_074["protection"]["path"])
            ),
            "passing_trace": receipt(
                Path(passing_077["protection"]["path"])
            ),
            "failed_command_samples": failed_074["behavior"]["samples"],
            "passing_command_samples": passing_077["behavior"]["samples"],
            "reference_feature_nearest_indices": nearest,
            "physics_claim_scope": (
                "graph-only contract; behavior still requires a separately "
                "preregistered CPU cell"
            ),
        },
        "contract": {
            "commands_x_m_s": [0.0, 0.074, 0.077, 0.080],
            "samples_per_context_command": 8,
            "random_seed": 243,
            "failed_trace_rows": 281,
            "expected_added_nodes": [
                "duplicate router MatMul",
                "duplicate router Add",
                "tail Greater",
                "exact-command Equal",
                "condition And",
                "mapped-command Where",
            ],
            "expected_changed_old_nodes": [
                "t222_cap_command output only",
                "t234_exact_command_gate input only",
            ],
            "all_non_target_context_commands_bit_exact": True,
            "target_exact_source_x0077": True,
            "stateful_abi_exact": True,
            "all_outputs_finite": True,
            "cpu_only": True,
        },
        "decision_rule": {
            "all_contract_checks_green": (
                "EARN_T244_HOME_NEGATIVE_LOW_COMMAND_BEHAVIOR_"
                "PREREGISTRATION_ONLY"
            ),
            "otherwise": (
                "CLOSE_HOME_NEGATIVE_LOW_COMMAND_FLOOR_WITHOUT_BEHAVIOR"
            ),
            "no_behavior_now": True,
            "no_hosted_run_authorized": True,
        },
        "checks": checks,
        "failed_checks": failed_checks,
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
            "targeted_behavior_preregistration": False,
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
        "# T243 home-negative low-command floor preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Transform: only calibrated home-negative x=.074 maps to the "
        "x=.077 policy path\n"
        "- Preserve: every other context/command, x=0, x=.08 cap, ABI\n"
        "- This stage is graph/inference only; behavior remains unproved\n"
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
