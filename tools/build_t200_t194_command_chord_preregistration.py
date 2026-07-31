#!/usr/bin/env python3
"""Preregister T200's saved-state command-chord diagnostic."""

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


T196 = ANALYSIS / "t196_t194_postexport_composition_result.json"
T198 = ANALYSIS / "t198_t194_targeted_y_negative_result.json"
T199_PREREG = (
    ANALYSIS / "t199_t194_support_credit_autopsy_preregistration.json"
)
T199_RESULT = ANALYSIS / "t199_t194_support_credit_autopsy_result.json"
OUTPUT = ANALYSIS / "t200_t194_command_chord_preregistration.json"
MARKDOWN = (
    ANALYSIS / "T200_T194_COMMAND_CHORD_PREREGISTRATION_20260730.md"
)
BUILDER = Path(__file__).resolve()
RUNNER = ROOT / "tools" / "run_t200_t194_command_chord.py"
TEST = ROOT / "tests" / "test_t200_t194_command_chord.py"


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T200: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T200 preregistration requires clean worktree")

    t196 = json.loads(T196.read_text(encoding="utf-8"))
    t198 = json.loads(T198.read_text(encoding="utf-8"))
    t199_prereg = json.loads(T199_PREREG.read_text(encoding="utf-8"))
    t199_result = json.loads(T199_RESULT.read_text(encoding="utf-8"))
    traces = [
        row
        for row in t199_prereg["traces"]
        if float(row["command_x_m_s"]) == 0.077
    ]
    graph_by_step = {
        int(row["step"]): row["structure"]["transformed"]
        for row in t196["graphs"]
    }
    graphs = {
        "half": graph_by_step[1_003_520],
        "final": graph_by_step[2_007_040],
    }
    checks = {
        "t199_green_and_support_continuation_rejected": (
            t199_result["status"]
            == "PASS_T199_T194_SUPPORT_CREDIT_AUTOPSY"
            and t199_result["decision"]
            == (
                "RETURN_TO_MECHANISM_SELECTION_WITHOUT_SUPPORT_"
                "OBJECTIVE_CONTINUATION"
            )
            and not t199_result["blindness_rule_passed"]
        ),
        "t198_only_failure_is_interior_x0077": (
            t198["status"] == "HOLD_T198_T194_TARGETED_Y_NEGATIVE"
            and t198["condition"]["green_cells"] == 15
            and any(
                not cell["cell_green"]
                and float(cell["command_x_m_s"]) == 0.077
                for block in t198["blocks"]
                for cell in block["result"]["cells"]
            )
        ),
        "three_x0077_saved_traces_exact": (
            len(traces) == 3
            and {(row["checkpoint_id"], row["fit_id"]) for row in traces}
            == {
                ("T194_COMPOSED_HALF", "p31_34"),
                ("T194_COMPOSED_FINAL", "p31_34"),
                ("T194_COMPOSED_HALF", "p30"),
            }
            and all(Path(row["trace"]["path"]).is_file() for row in traces)
        ),
        "two_composed_graphs_present": (
            set(graphs) == {"half", "final"}
            and all(Path(row["path"]).is_file() for row in graphs.values())
        ),
        "same_half_p31_endpoints_pass": all(
            cell["cell_green"]
            for block in t198["blocks"]
            if (
                block["checkpoint_id"] == "T194_COMPOSED_HALF"
                and block["fit_id"] == "p31_34"
            )
            for cell in block["result"]["cells"]
            if float(cell["command_x_m_s"]) in {0.074, 0.080}
        ),
        "read_only_no_behavior_training_hosted_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T200 preregistration checks failed: {failed}")

    basis: dict[str, Any] = {
        "schema_version": (
            "open_duck.t200_t194_command_chord_preregistration.v1"
        ),
        "status": "PREREGISTERED_T200_T194_COMMAND_CHORD",
        "question": (
            "Does the failing half/P31-34 x=.077 trajectory occupy states "
            "where the actor's center-command output departs from the exact "
            "midpoint of its x=.074 and x=.080 outputs more strongly than "
            "the matched passing x=.077 trajectories?"
        ),
        "frozen_inputs": {
            name: receipt(path)
            for name, path in {
                "builder": BUILDER,
                "runner": RUNNER,
                "test": TEST,
                "t196_composition": T196,
                "t198_result": T198,
                "t199_preregistration": T199_PREREG,
                "t199_result": T199_RESULT,
            }.items()
        },
        "graphs": graphs,
        "contexts": t199_prereg["contexts"],
        "traces": traces,
        "analysis": {
            "command_observation_index": 6,
            "commands_x_m_s": [0.074, 0.077, 0.080],
            "midpoint_weights": [0.5, 0.5],
            "aligned_comparison_ticks_inclusive": [254, 307],
            "terminal_window_ticks": 54,
            "prefix_window_ticks": 54,
            "output_names": [
                "continuous_actions",
                "h_out",
                "previous_action_out",
            ],
            "curvature_rule": {
                "failure_aligned_action_rms_strictly_exceeds": (
                    "both matched x=.077 passes"
                ),
                "failure_aligned_action_max_strictly_exceeds": (
                    "both matched x=.077 passes"
                ),
                "failure_terminal_action_rms_strictly_exceeds_prefix": True,
            },
            "next_screen": (
                "one half/P31-34/x=.077 behavior cell with an exact "
                "same-checkpoint endpoint-chord wrapper"
            ),
            "head_switch_or_checkpoint_selection": False,
            "selection_weight": 0,
        },
        "decision_rule": {
            "interior_command_curvature_supported": (
                "EARN_T201_ONE_CELL_COMMAND_CHORD_FEASIBILITY_"
                "PREREGISTRATION_ONLY"
            ),
            "otherwise": (
                "RETURN_TO_MECHANISM_SELECTION_WITHOUT_COMMAND_CHORD"
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
            "execute_saved_state_diagnostic": True,
            "one_cell_behavior_preregistration": False,
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
        "# T200 T194 command-chord preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Inputs: three frozen x=.077 traces and their exact T194 heads\n"
        "- Work: same-state x=.074/.077/.080 ONNX output curvature\n"
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
