#!/usr/bin/env python3
"""Freeze T17's bounded support-homeomorphism behavior screen."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from t17_support_homeomorphism_onnx import (
    ACTION_SCALE_RAD,
    CONTRACT_TOLERANCE,
    FLOAT32_EPSILON,
    HOME_ACTION_RAD,
    SUPPORT_ACTION,
    sha256,
)


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
OUTPUT = ANALYSIS / "t17_support_homeomorphism_preregistration.json"
MARKDOWN = (
    ANALYSIS / "T17_SUPPORT_HOMEOMORPHISM_PREREGISTRATION_20260726.md"
)
RUNNER = ROOT / "tools" / "run_t17_support_homeomorphism_screen.py"
TRANSFORM = ROOT / "tools" / "t17_support_homeomorphism_onnx.py"
TEST = ROOT / "tests" / "test_t17_support_homeomorphism.py"
T16_RUNNER = ROOT / "tools" / "run_t16_support_coordinate_screen.py"
T16_WORKER = ROOT / "tools" / "evaluate_t16_support_coordinate.py"


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def receipt(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def main() -> int:
    if OUTPUT.exists() or MARKDOWN.exists():
        raise FileExistsError("refusing to overwrite T17 preregistration")
    for path in (RUNNER, TRANSFORM, TEST, T16_RUNNER, T16_WORKER):
        if not path.is_file():
            raise FileNotFoundError(path)

    t12_path = ANALYSIS / "t12_response_prefix_com_result.json"
    t15_path = ANALYSIS / "t15_x0_deadband_structural_result.json"
    t16_prereg_path = (
        ANALYSIS / "t16_support_coordinate_preregistration.json"
    )
    t16_result_path = ANALYSIS / "t16_support_coordinate_result.json"
    t12 = json.loads(t12_path.read_text(encoding="utf-8"))
    t15 = json.loads(t15_path.read_text(encoding="utf-8"))
    t16_prereg = json.loads(t16_prereg_path.read_text(encoding="utf-8"))
    t16 = json.loads(t16_result_path.read_text(encoding="utf-8"))
    t16_cells = [
        cell for block in t16["blocks"] for cell in block["cells"]
    ]
    moving_cells = [
        cell for cell in t16_cells if cell["command_x_m_s"] > 0.0
    ]
    checks = {
        "t12_prefix_only_closed": (
            t12["decision"] == "CLOSE_RESPONSE_PREFIX_STATE_PREPARATION"
            and t12["summary"]["green_cells"] == 5
            and t12["summary"]["total_cells"] == 12
        ),
        "t15_x0_support_reopened": (
            t15["decision"]
            == "REOPEN_X0_BRANCH_FOR_CONFIGURATION_AWARE_SUPPORT_RETENTION"
        ),
        "t16_affine_translation_closed": (
            t16["decision"] == "CLOSE_EXACT_SUPPORT_COORDINATE_CONJUGATION"
            and t16["summary"]["green_cells"] == 8
            and t16["summary"]["total_cells"] == 32
        ),
        "t16_moving_physics_survived": (
            len(moving_cells) == 24
            and all(
                cell["behavior"]["core_checks"]["duration"]
                and cell["behavior"]["core_checks"]["height"]
                and cell["behavior"]["core_checks"]["positive_velocity"]
                and cell["behavior"]["core_checks"][
                    "bilateral_transitions"
                ]
                and cell["behavior"]["replacement_quality_checks"][
                    "tracking"
                ]
                and cell["behavior"]["replacement_quality_checks"][
                    "instant_rate"
                ]
                for cell in moving_cells
            )
        ),
        "t16_failure_is_output_saturation": (
            min(
                cell["behavior"]["action_saturation_pct"]
                for cell in moving_cells
            )
            >= 50.0
            and all(
                not cell["behavior"]["replacement_quality_checks"][
                    "zero_saturation"
                ]
                for cell in moving_cells
            )
        ),
        "candidate_pair_exact": (
            len(t16_prereg["candidate"]["checkpoints"]) == 2
        ),
        "fit_pair_exact": (
            set(t16_prereg["candidate"]["fits"]) == {"p30", "p31_34"}
        ),
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    sources = {
        "builder": receipt(Path(__file__).resolve()),
        "runner": receipt(RUNNER),
        "transform": receipt(TRANSFORM),
        "test": receipt(TEST),
        "shared_t16_runner_helpers": receipt(T16_RUNNER),
        "frozen_t16_worker": receipt(T16_WORKER),
        "t12_result": receipt(t12_path),
        "t15_result": receipt(t15_path),
        "t16_preregistration": receipt(t16_prereg_path),
        "t16_result": receipt(t16_result_path),
        "t8_evaluator_adapter": receipt(
            ROOT / "tools" / "t8_state_coherent_eval_adapter.py"
        ),
        "frozen_closed_loop_evaluator": receipt(
            ROOT / "tools" / "closed_loop_sim_eval.py"
        ),
    }
    basis = {
        "schema_version": (
            "open_duck.t17_support_homeomorphism_preregistration.v1"
        ),
        "status": "PREREGISTERED_T17_SUPPORT_HOMEOMORPHISM_SCREEN",
        "question": (
            "Does the unique bounded support-centered action "
            "homeomorphism retain T16's support-rescued locomotion without "
            "the affine translation's structurally created saturation?"
        ),
        "causal_basis": {
            "t12": (
                "A support prefix followed by unchanged V121 is insufficient "
                "at negative torso COM: only 5/12 moving cells pass."
            ),
            "t15": (
                "The x=0 exact-zero branch is structurally invalid under "
                "variable configuration, while the universal support action "
                "is an existing stable counterexample."
            ),
            "t16": (
                "Affine support translation makes every moving cell complete "
                "600 ticks, move forward, transition bilaterally, track "
                "inside 0.2 rad, and obey the measured rate vector, but "
                "clip-created saturation reaches 57.17-68.83 percent."
            ),
            "materially_distinct_mechanism": (
                "T17 does not select a scale or subset and does not add then "
                "clip. Per joint it uses the only continuous map affine on "
                "each side of zero satisfying F(-1)=-1, F(0)=support, and "
                "F(1)=1. It is bijective on the whole action box, preserves "
                "both endpoints, has a closed-form inverse for all "
                "action-coordinate observation/state inputs, and cannot "
                "create saturation from an interior source action."
            ),
        },
        "sources": sources,
        "playground": t16_prereg["playground"],
        "candidate": t16_prereg["candidate"],
        "transform": {
            "name": "bounded_support_centered_piecewise_affine_homeomorphism",
            "support_action": SUPPORT_ACTION.astype(float).tolist(),
            "home_action_rad": HOME_ACTION_RAD.astype(float).tolist(),
            "action_scale_rad": float(ACTION_SCALE_RAD),
            "forward": (
                "F_s(a)=s+(1-s)*a for a>=0; "
                "F_s(a)=s+(1+s)*a for a<0"
            ),
            "inverse": (
                "G_s(y)=(y-s)/(1-s) for y>=s; "
                "G_s(y)=(y-s)/(1+s) for y<s"
            ),
            "input_inverse_slices": {
                "joint_position_error_rad": [13, 27],
                "action_history_1": [41, 55],
                "action_history_2": [55, 69],
                "action_history_3": [69, 83],
                "applied_absolute_target_rad": [83, 97],
                "previous_action": [0, 14],
            },
            "unchanged_observation_slices": [
                [0, 13],
                [27, 41],
                [97, 115],
            ],
            "reference_action_101_115": "unchanged",
            "command_and_phase": "unchanged",
            "hidden_state": "bit-exact source h_out",
            "external_abi": t16_prereg["transform"]["external_abi"],
            "contract_cases": 256,
            "contract_seed": 20260726,
            "float32_epsilon": FLOAT32_EPSILON,
            "contract_tolerance": CONTRACT_TOLERANCE,
            "contract_tolerance_derivation": (
                "32 * IEEE-754 float32 machine epsilon; frozen before "
                "behavior execution"
            ),
            "free_scalar_count": 0,
            "output_clip_nodes": 0,
        },
        "matrix": t16_prereg["matrix"],
        "handoff_contract": t16_prereg["handoff_contract"],
        "behavior_contract": t16_prereg["behavior_contract"],
        "protection_contract": t16_prereg["protection_contract"],
        "decision_rule": {
            "pass": (
                "Both wrapped checkpoints pass all 32 nominal and "
                "negative-COM cells under both measured fits and all four "
                "commands; all x=0 ticks equal the exact support action; "
                "every wrapper, ABI, handoff, readback, rate, saturation, "
                "and manufacturer-duration protection check passes."
            ),
            "pass_next_action": (
                "Earn only a separately preregistered sequential full R2 "
                "screen of the exact two wrapped policies. No training, "
                "hardware, or Gate 5 is earned."
            ),
            "fail": (
                "Close the bounded support-centered homeomorphism. Do not "
                "search a curve, breakpoint, exponent, support vector, "
                "joint subset, checkpoint blend, or tolerance."
            ),
            "partial_results_selection_weight": 0,
            "no_threshold_changes_after_execution": True,
        },
        "authority": {
            "cpu_only": True,
            "optimizer_steps": 0,
            "hosted_or_colab_compute": False,
            "checkpoint_selection": False,
            "deployment_or_gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
        "execution_now": {
            "wrapped_policies": 0,
            "behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
    }
    if failed:
        basis["status"] = "HOLD_T17_PREREGISTRATION_INPUTS"
    value = {
        **basis,
        "preregistered_contract_sha256": canonical_sha256(basis),
        "failed_checks": failed,
        "checks": checks,
    }
    OUTPUT.write_text(
        json.dumps(
            value,
            allow_nan=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T17 bounded support-homeomorphism preregistration",
                "",
                f"- Status: `{value['status']}`",
                (
                    "- Mechanism: unique endpoint-preserving, "
                    "support-centered piecewise-affine homeomorphism"
                ),
                "- Free scalars / optimizer steps: `0 / 0`",
                (
                    "- Matrix: 2 checkpoints x 2 fits x 2 COM conditions x "
                    "4 commands = `32` cells"
                ),
                "- CPU only; hosted/robot execution: `0/0`",
                (
                    "- Pass earns only a separately preregistered full R2 "
                    "screen."
                ),
                (
                    f"- Canonical SHA-256: "
                    f"`{value['preregistered_contract_sha256']}`"
                ),
                "",
            ]
        ),
        encoding="utf-8",
        newline="\n",
    )
    print(OUTPUT.relative_to(ROOT))
    print(MARKDOWN.relative_to(ROOT))
    print(value["status"])
    print(value["preregistered_contract_sha256"])
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
