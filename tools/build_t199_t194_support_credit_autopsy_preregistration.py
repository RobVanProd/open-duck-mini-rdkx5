#!/usr/bin/env python3
"""Preregister T199's saved-trace support-credit autopsy."""

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
T191 = ANALYSIS / "t191_t186_failure_exchange_autopsy_result.json"
T167 = ANALYSIS / "t167_calibration_context_separability_result.json"
OUTPUT = (
    ANALYSIS / "t199_t194_support_credit_autopsy_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "T199_T194_SUPPORT_CREDIT_AUTOPSY_PREREGISTRATION_20260730.md"
)
BUILDER = Path(__file__).resolve()
RUNNER = ROOT / "tools" / "run_t199_t194_support_credit_autopsy.py"
TEST = ROOT / "tests" / "test_t199_t194_support_credit_autopsy.py"
PLAYGROUND = Path("D:/CodexProjects/Open_Duck_Playground-composed-t19-v6")
POLYNOMIAL = (
    PLAYGROUND
    / "playground"
    / "open_duck_mini_v2"
    / "data"
    / "polynomial_coefficients.pkl"
)
POLYNOMIAL_MODULE = (
    PLAYGROUND
    / "playground"
    / "common"
    / "poly_reference_motion_numpy.py"
)
T193_OBJECTIVE = ROOT / "patches" / "t193_corrected_dynamic_reference_support.py"


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
    trace = Path(cell["protection"]["path"])
    return {
        "checkpoint_id": checkpoint,
        "step": int(block["step"]),
        "fit_id": fit,
        "command_x_m_s": command,
        "cell_green": bool(cell["cell_green"]),
        "samples": int(cell["behavior"]["samples"]),
        "termination_reason": cell["behavior"]["termination_reason"],
        "trace": {
            "path": str(trace),
            "bytes": trace.stat().st_size,
            "sha256": cell["protection"]["sha256"],
        },
    }


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T199: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T199 preregistration requires clean worktree")

    t196 = json.loads(T196.read_text(encoding="utf-8"))
    t198 = json.loads(T198.read_text(encoding="utf-8"))
    t191 = json.loads(T191.read_text(encoding="utf-8"))
    t167 = json.loads(T167.read_text(encoding="utf-8"))
    traces = [
        find_cell(t198, "T194_COMPOSED_HALF", "p31_34", 0.077),
        find_cell(t198, "T194_COMPOSED_FINAL", "p31_34", 0.077),
        find_cell(t198, "T194_COMPOSED_HALF", "p30", 0.077),
        find_cell(t198, "T194_COMPOSED_HALF", "p31_34", 0.074),
        find_cell(t198, "T194_COMPOSED_HALF", "p31_34", 0.080),
    ]
    graph_by_step = {
        int(row["step"]): row["structure"]["transformed"]
        for row in t196["graphs"]
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
    failure = traces[0]
    checks = {
        "t198_is_exact_15_of_16_hold": (
            t198["status"] == "HOLD_T198_T194_TARGETED_Y_NEGATIVE"
            and t198["decision"]
            == "CLOSE_T194_CORRECTED_DYNAMIC_REFERENCE_SUPPORT_CONTINUATION"
            and t198["condition"]["green_cells"] == 15
        ),
        "failure_is_half_p31_x0077_only": (
            failure["cell_green"] is False
            and failure["samples"] == 308
            and failure["termination_reason"] == "fall_or_nan"
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
        "t191_prior_support_collapse_autopsy_green": (
            t191["status"]
            == "PASS_T191_T186_FAILURE_EXCHANGE_AUTOPSY"
            and t191["classification"]
            == (
                "RESET_SUPPORT_CURRICULUM_SHIFTED_BUT_DID_NOT_"
                "ELIMINATE_LOCOMOTION_SUPPORT_COLLAPSE"
            )
        ),
        "reference_assets_present": (
            POLYNOMIAL.is_file()
            and POLYNOMIAL_MODULE.is_file()
            and T193_OBJECTIVE.is_file()
        ),
        "read_only_no_behavior_training_hosted_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T199 preregistration checks failed: {failed}")

    basis: dict[str, Any] = {
        "schema_version": (
            "open_duck.t199_t194_support_credit_autopsy_"
            "preregistration.v1"
        ),
        "status": "PREREGISTERED_T199_T194_SUPPORT_CREDIT_AUTOPSY",
        "question": (
            "Is the sole T194 fall preceded by a uniquely long interval "
            "where the reference requests exact single support but the "
            "observed policy-time contact state receives zero from T193's "
            "positive-only exact-match support term?"
        ),
        "frozen_inputs": {
            name: receipt(path)
            for name, path in {
                "builder": BUILDER,
                "runner": RUNNER,
                "test": TEST,
                "t196_composition": T196,
                "t198_result": T198,
                "t191_prior_autopsy": T191,
                "t167_contexts": T167,
                "polynomial_coefficients": POLYNOMIAL,
                "polynomial_module": POLYNOMIAL_MODULE,
                "t193_objective": T193_OBJECTIVE,
            }.items()
        },
        "graphs": graphs,
        "contexts": contexts,
        "traces": traces,
        "analysis": {
            "recorded_onnx_replay": "all stored rows, exact",
            "cross_checkpoint_replay": [
                "failing half/P31-34/x=.077 states",
                "passing final/P31-34/x=.077 states",
            ],
            "paired_dynamics": [
                "half versus final P31-34/x=.077",
                "half P31-34 versus P30 x=.077",
            ],
            "policy_contact_slice": [97, 99],
            "policy_phase_slice": [99, 101],
            "reference_contact_slice": [32, 34],
            "gait_period_ticks": 27,
            "failure_terminal_window_ticks": 54,
            "aligned_comparison_ticks_inclusive": [254, 307],
            "phase_reconstruction_max_error": 1.0e-6,
            "credit_rule": (
                "positive only when reference and observed sides are the "
                "same exact left-only or right-only support"
            ),
            "blindness_rule": {
                "failure_maximum_contiguous_zero_credit_at_least_ticks": 27,
                "failure_aligned_zero_credit_count_strictly_exceeds": (
                    "every matched pass over ticks 254..307"
                ),
                "failure_has_reference_single_support_mismatch": True,
            },
            "head_switch_excluded_by": (
                "T192 exact late-switch feasibility reproduced the fall"
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
            "positive_only_blindness_supported": (
                "EARN_T200_DENSE_SIGNED_REFERENCE_SUPPORT_"
                "DIAGNOSTIC_PREREGISTRATION_ONLY"
            ),
            "otherwise": (
                "RETURN_TO_MECHANISM_SELECTION_WITHOUT_SUPPORT_"
                "OBJECTIVE_CONTINUATION"
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
            "diagnostic_preregistration": False,
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
        "# T199 T194 support-credit autopsy preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Inputs: one frozen failure, four matched passes, both T194 heads\n"
        "- Work: exact replay and reference/observed support-credit census\n"
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
