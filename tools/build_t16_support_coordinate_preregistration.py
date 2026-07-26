#!/usr/bin/env python3
"""Freeze T16's zero-training support-coordinate behavior screen."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from t16_support_coordinate_onnx import (
    ACTION_SCALE_RAD,
    SUPPORT_ACTION,
    observation_delta,
    sha256,
)


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
OUTPUT = ANALYSIS / "t16_support_coordinate_preregistration.json"
MARKDOWN = ANALYSIS / "T16_SUPPORT_COORDINATE_PREREGISTRATION_20260726.md"
RUNNER = ROOT / "tools" / "run_t16_support_coordinate_screen.py"
WORKER = ROOT / "tools" / "evaluate_t16_support_coordinate.py"
TRANSFORM = ROOT / "tools" / "t16_support_coordinate_onnx.py"
TEST = ROOT / "tests" / "test_t16_support_coordinate.py"


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
        raise FileExistsError("refusing to overwrite T16 preregistration")
    for path in (RUNNER, WORKER, TRANSFORM, TEST):
        if not path.is_file():
            raise FileNotFoundError(path)

    t12_prereg_path = (
        ANALYSIS / "t12_response_prefix_com_preregistration.json"
    )
    t12_result_path = ANALYSIS / "t12_response_prefix_com_result.json"
    t15_path = ANALYSIS / "t15_x0_deadband_structural_result.json"
    t12_prereg = json.loads(t12_prereg_path.read_text(encoding="utf-8"))
    t12 = json.loads(t12_result_path.read_text(encoding="utf-8"))
    t15 = json.loads(t15_path.read_text(encoding="utf-8"))
    checks = {
        "t12_prefix_only_route_closed": (
            t12["decision"] == "CLOSE_RESPONSE_PREFIX_STATE_PREPARATION"
            and t12["summary"]["green_cells"] == 5
            and t12["summary"]["total_cells"] == 12
        ),
        "t15_x0_deadband_contradiction_green": (
            t15["status"]
            == "PASS_T15_X0_DEADBAND_STRUCTURAL_CONTRADICTION"
            and t15["decision"]
            == "REOPEN_X0_BRANCH_FOR_CONFIGURATION_AWARE_SUPPORT_RETENTION"
        ),
        "source_checkpoint_pair_exact": (
            len(t12_prereg["candidate"]["checkpoints"]) == 2
        ),
        "measured_fit_pair_exact": (
            set(t12_prereg["candidate"]["fits"]) == {"p30", "p31_34"}
        ),
    }
    failed = sorted(name for name, passed in checks.items() if not passed)

    sources = {
        "builder": receipt(Path(__file__).resolve()),
        "runner": receipt(RUNNER),
        "worker": receipt(WORKER),
        "transform": receipt(TRANSFORM),
        "test": receipt(TEST),
        "t12_preregistration": receipt(t12_prereg_path),
        "t12_result": receipt(t12_result_path),
        "t15_result": receipt(t15_path),
        "t8_evaluator_adapter": receipt(
            ROOT / "tools" / "t8_state_coherent_eval_adapter.py"
        ),
        "frozen_closed_loop_evaluator": receipt(
            ROOT / "tools" / "closed_loop_sim_eval.py"
        ),
    }
    delta = observation_delta()
    nonzero_slices = {
        "joint_position_error_13_27": (
            SUPPORT_ACTION * ACTION_SCALE_RAD
        ).astype(float).tolist(),
        "action_history_41_55": SUPPORT_ACTION.astype(float).tolist(),
        "action_history_55_69": SUPPORT_ACTION.astype(float).tolist(),
        "action_history_69_83": SUPPORT_ACTION.astype(float).tolist(),
        "applied_target_rad_83_97": (
            SUPPORT_ACTION * ACTION_SCALE_RAD
        ).astype(float).tolist(),
    }
    basis = {
        "schema_version": (
            "open_duck.t16_support_coordinate_preregistration.v1"
        ),
        "status": "PREREGISTERED_T16_SUPPORT_COORDINATE_SCREEN",
        "question": (
            "Can an exact action-coordinate conjugation re-center the frozen "
            "V121 gait on the already-proven universal support posture while "
            "preserving its learned waveform, recurrent state, rate "
            "increments, ABI, nominal behavior, and negative-COM behavior?"
        ),
        "causal_basis": {
            "t7": (
                "The exact universal support action holds nominal and both "
                "signed COM endpoints for 600 ticks and all 124 prior support "
                "configurations."
            ),
            "t12": (
                "Removing that posture after the prefix leaves only 5/12 "
                "negative-COM moving cells green, so transient preparation "
                "alone is insufficient."
            ),
            "t15": (
                "At x=0 the unconditional exact-zero branch makes the "
                "negative-COM failure policy-independent, while retaining the "
                "support action is already a stable counterexample."
            ),
            "materially_distinct_mechanism": (
                "T16 is not a post-policy additive bias. It subtracts the "
                "same support coordinate from joint-error, three action "
                "history slots, applied target, and recurrent previous-action "
                "inputs before source inference, then adds it to both action "
                "outputs. This is a conjugate coordinate transform with no "
                "learned or tuned scalar."
            ),
        },
        "sources": sources,
        "playground": t12_prereg["playground"],
        "candidate": t12_prereg["candidate"],
        "transform": {
            "name": "exact_universal_support_coordinate_conjugation",
            "support_action": SUPPORT_ACTION.astype(float).tolist(),
            "action_scale_rad": float(ACTION_SCALE_RAD),
            "observation_subtractions": nonzero_slices,
            "observation_delta_sha256": hashlib.sha256(
                delta.tobytes()
            ).hexdigest(),
            "previous_action_input": "previous_action - support_action",
            "source_action_output": (
                "clip(source_action + support_action, -1, 1)"
            ),
            "source_previous_action_output": (
                "clip(source_previous_action_out + support_action, -1, 1)"
            ),
            "hidden_state": "bit-exact source h_out",
            "reference_action_101_115": "unchanged",
            "command_and_phase": "unchanged",
            "external_abi": {
                "inputs": {
                    "obs": [1, 115],
                    "previous_action": [1, 14],
                    "h_in": [1, 64],
                    "calibration_context": [1, 64],
                },
                "outputs": {
                    "continuous_actions": [1, 14],
                    "previous_action_out": [1, 14],
                    "h_out": [1, 64],
                },
            },
            "contract_cases": 256,
            "contract_seed": 20260726,
            "contract_tolerance": 0.0,
            "saturation": (
                "clip remains part of the graph, but any nonzero behavior "
                "saturation fails the unchanged gate"
            ),
        },
        "matrix": {
            "conditions": [
                {"id": "NOMINAL", "torso_com_x_m": 0.0},
                {"id": "TORSO_COM_X_NEG", "torso_com_x_m": -0.05},
            ],
            "checkpoints": [
                row["checkpoint_id"]
                for row in t12_prereg["candidate"]["checkpoints"]
            ],
            "fits": ["p30", "p31_34"],
            "commands_x_m_s": [0.0, 0.074, 0.077, 0.08],
            "seed": 167931544,
            "duration_ticks": 600,
            "calibration_ticks": 250,
            "home_return_ticks": 0,
            "behavior_cells": 32,
            "worker_blocks": 8,
        },
        "handoff_contract": t12_prereg["handoff_contract"],
        "behavior_contract": t12_prereg["behavior_contract"],
        "protection_contract": t12_prereg["protection_contract"],
        "decision_rule": {
            "pass": (
                "Both wrapped checkpoints pass all 32 nominal and "
                "negative-COM cells under both measured fits and all four "
                "commands; x=0 retains the exact support action; every "
                "wrapper equation/ABI/handoff/readback/rate/protection check "
                "passes."
            ),
            "pass_next_action": (
                "Earn only a separately preregistered sequential full R2 "
                "screen of the exact two wrapped policies. No training, "
                "hardware, or Gate 5 is earned."
            ),
            "fail": (
                "Close exact support-coordinate conjugation. Do not search a "
                "scale, subset, alternate support vector, observation slice, "
                "checkpoint blend, or closest cell."
            ),
            "reviewed_x0_contract_change": (
                "T15 evidence replaces exact-zero action with exact support "
                "retention only inside this candidate graph; the unchanged "
                "physical x=0 stability/velocity/rate/protection gates remain."
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
        basis["status"] = "HOLD_T16_PREREGISTRATION_INPUTS"
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
                "# T16 support-coordinate behavior preregistration",
                "",
                f"- Status: `{value['status']}`",
                (
                    "- Mechanism: exact universal-support coordinate "
                    "conjugation, no scalar or optimizer"
                ),
                (
                    "- Matrix: 2 checkpoints x 2 fits x 2 COM conditions x "
                    "4 commands = `32` cells"
                ),
                "- CPU only; optimizer/hosted/robot execution: `0/0/0`",
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
