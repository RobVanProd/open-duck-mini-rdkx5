#!/usr/bin/env python3
"""Freeze the T7 current-stack universal response-support falsifier."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
JSON_OUTPUT = ANALYSIS / "t7_universal_response_support_preregistration.json"
MARKDOWN_OUTPUT = (
    ANALYSIS / "T7_UNIVERSAL_RESPONSE_SUPPORT_PREREGISTRATION_20260725.md"
)
DEFAULT_PLAYGROUND = Path(r"D:\CodexProjects\Open_Duck_Playground-composed-v175")
DEFAULT_POLICY = Path(
    r"D:\CodexArtifacts\open-duck-mini-rdkx5"
    r"\winner-v96-response-conditioned-mechanics"
    r"\winner_v96_universal_calibrator.onnx"
)
EXPECTED_POLICY_SHA256 = (
    "0f3aebfd9946a6271fdb14adec3d68d556648f270984639d372c973a7d7dc576"
)
UNIVERSAL_TARGET = [
    0.0,
    0.0,
    -0.5,
    0.25,
    0.25,
    0.0,
    0.0,
    0.0,
    0.0,
    0.0,
    0.0,
    0.5,
    0.25,
    0.25,
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def file_receipt(path: Path) -> dict[str, Any]:
    resolved = path.resolve()
    if not resolved.is_file():
        raise FileNotFoundError(resolved)
    return {
        "path": str(resolved),
        "bytes": resolved.stat().st_size,
        "sha256": sha256(resolved),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--playground-root", type=Path, default=DEFAULT_PLAYGROUND)
    parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
    args = parser.parse_args()

    if JSON_OUTPUT.exists() or MARKDOWN_OUTPUT.exists():
        raise FileExistsError("refusing to overwrite the T7 preregistration")

    policy = args.policy.resolve()
    if sha256(policy) != EXPECTED_POLICY_SHA256:
        raise RuntimeError("the frozen V96 universal calibrator graph changed")

    t6_prereg = json.loads(
        (ANALYSIS / "t6_corrected_robustness_screen_preregistration.json").read_text(
            encoding="utf-8"
        )
    )
    playground = args.playground_root.resolve()
    if str(playground) != t6_prereg["playground"]["path"]:
        raise RuntimeError("T7 must use the exact T6 composed Playground")

    repository_inputs = {
        "builder": file_receipt(Path(__file__)),
        "runner": file_receipt(
            ROOT / "tools" / "run_t7_universal_response_support.py"
        ),
        "evaluator": file_receipt(ROOT / "tools" / "evaluate_ground_up_policy.py"),
        "closed_loop": file_receipt(ROOT / "tools" / "closed_loop_sim_eval.py"),
        "actuator_model": file_receipt(ROOT / "tools" / "actuator_bridge_model.py"),
        "fit_p30": file_receipt(
            ANALYSIS / "fixed_target_p30_actuator_fit_20260712.json"
        ),
        "fit_p31_34": file_receipt(
            ANALYSIS / "fixed_target_p31_34_actuator_fit_20260712.json"
        ),
        "reference_features": file_receipt(
            ANALYSIS / "ground_up_projected_reference_feature_table.npz"
        ),
        "v91_result": file_receipt(
            ANALYSIS / "winner_v91_universal_target_full_gate_result.json"
        ),
        "v92_result": file_receipt(
            ANALYSIS / "winner_v92_universal_target_response_observer_result.json"
        ),
        "v96_preregistration": file_receipt(
            ANALYSIS / "winner_v96_response_conditioned_mechanics_preregistration.json"
        ),
        "v103_runner": file_receipt(
            ROOT / "tools" / "run_winner_v103_response_conditioned_behavior.py"
        ),
        "response_training_wrapper": file_receipt(
            playground
            / "playground"
            / "common"
            / "winner_v98_response_calibration_wrapper.py"
        ),
        "t5_result": file_receipt(
            ANALYSIS / "t5_actuator_protection_reanalysis_result.json"
        ),
        "t6_result": file_receipt(
            ANALYSIS / "t6_corrected_robustness_screen_result.json"
        ),
    }

    playground_contract = {
        "path": str(playground),
        "control_commit": t6_prereg["playground"]["control_commit"],
        "required_file_sha256": t6_prereg["playground"]["required_file_sha256"],
        "composition_manifests": t6_prereg["playground"]["composition_manifests"],
    }
    for relative, expected in playground_contract["required_file_sha256"].items():
        if sha256(playground / relative) != expected:
            raise RuntimeError(f"composed Playground file changed: {relative}")

    frozen_policy = {
        **file_receipt(policy),
        "expected_sha256": EXPECTED_POLICY_SHA256,
        "abi": {
            "inputs": {
                "obs": [1, 115],
                "previous_action": [1, 14],
                "h_in": [1, 64],
            },
            "outputs": {
                "calibration_actions": [1, 14],
                "previous_action_out": [1, 14],
                "h_out": [1, 64],
            },
        },
        "universal_raw_action": UNIVERSAL_TARGET,
        "universal_raw_action_sha256": canonical_sha256(UNIVERSAL_TARGET),
    }

    matrix = {
        "configurations": [
            {
                "id": "NOMINAL",
                "override": {"torso_com_offset_m": [0.0, 0.0, 0.0]},
            },
            {
                "id": "TORSO_COM_X_NEG",
                "override": {"torso_com_offset_m": [-0.05, 0.0, 0.0]},
            },
            {
                "id": "TORSO_COM_X_POS",
                "override": {"torso_com_offset_m": [0.05, 0.0, 0.0]},
            },
        ],
        "fits": ["p30", "p31_34"],
        "repeats": [0, 1],
        "command_x_m_s": 0.0,
        "seed": 167931544,
        "frequency_hz": 50,
        "response_context_tick": 249,
        "duration_ticks": 600,
        "cells": 12,
    }
    behavior_contract = {
        "all_cells": {
            "duration_ticks": 600,
            "minimum_base_height_m": 0.12,
            "maximum_absolute_mean_local_vx_m_s": 0.02,
            "maximum_body_pitch_p95_rad": 0.25,
            "maximum_action_saturation_pct": 0.0,
            "maximum_sent_or_conservative_rate_excess_rad_s": 0.0,
            "graph_action_matches_bounded_universal_target_bit_exact": True,
            "previous_action_and_hidden_chains_bit_exact": True,
            "host_action_delta_max_abs": 0.0,
            "model_com_readback_exact": True,
        },
        "servo_protection": {
            "source": "T5 corrected manufacturer-duration rules",
            "motor_constant_nm_per_a": 0.784532,
            "strict_overcurrent_threshold_a": 2.0,
            "strict_overload_threshold_nm": 1.5298374,
            "maximum_consecutive_ticks": 99,
            "instantaneous_peak_current_and_torque": "diagnostic_only",
        },
        "response_signal": {
            "context_tick": 249,
            "repeat_trace_and_context_bit_exact": True,
            "all_contexts_finite": True,
            "minimum_signed_com_endpoint_linf_separation_per_fit": 0.15,
            "nominal_context_must_differ_from_each_signed_endpoint": True,
            "nominal_difference_floor_linf": 1.0e-7,
            "signed_threshold_source": (
                "the previously frozen V96 same-plant COM_X_NEG versus "
                "COM_X_POS context threshold"
            ),
        },
    }
    causal_audit = {
        "training_wrapper": (
            "The V98/V102 training wrapper computes hidden state from the frozen "
            "calibrator weights but replaces the action head with the V91 "
            "universal target before the graph rate boundary."
        ),
        "formal_evaluator": (
            "The V103 formal evaluator instead executed the calibrator ONNX "
            "calibration_actions output directly. Therefore its negative-X "
            "prefix failures did not test the training action semantics."
        ),
        "t6_relevance": (
            "T6 proves exact zero action at shifted COM is not a viable support "
            "strategy; T7 deliberately holds the universal target and does not "
            "perform the known-bad zero-action home-return phase."
        ),
        "scope": (
            "T7 tests only stable automatic excitation plus response-signal "
            "transport on the exact current stack. It does not test locomotion "
            "or authorize a policy continuation."
        ),
    }
    decision_rule = {
        "partial_results_selection_weight": 0,
        "pass": (
            "all 12 cells pass behavior, exact graph-chain, corrected servo "
            "duration, repeatability, readback, and response-signal contracts"
        ),
        "pass_next_action": (
            "authorize one separately preregistered, zero-training, "
            "state-coherent support-to-locomotion handoff screen; do not "
            "authorize hosted training yet"
        ),
        "fail_next_action": (
            "close transfer of the V91/V96 universal response-support mechanism "
            "to the current stack; do not train this mechanism"
        ),
    }
    authority = {
        "offline_cpu_behavior_cells": True,
        "training_or_hosted_compute": False,
        "policy_or_simulator_modification": False,
        "robot_rdkx5_torque_motion": False,
        "gate5": False,
    }
    execution_contract = {
        "cpu_only": True,
        "no_early_stop": True,
        "two_exact_repeats_per_configuration_fit": True,
        "raw_logs_external_to_repository": True,
        "cache_root": (
            r"D:\CodexArtifacts\open-duck-policy"
            r"\t7_universal_response_support_v1"
        ),
        "runner_refuses_unpreregistered_inputs_or_overwrite": True,
        "training_steps": 0,
    }

    basis = {
        "repository_inputs": repository_inputs,
        "playground": playground_contract,
        "frozen_policy": frozen_policy,
        "causal_audit": causal_audit,
        "matrix": matrix,
        "behavior_contract": behavior_contract,
        "decision_rule": decision_rule,
        "authority": authority,
        "execution_contract": execution_contract,
    }
    payload = {
        "schema_version": "open_duck.t7_universal_response_support_preregistration.v1",
        "status": "PREREGISTERED_T7_UNIVERSAL_RESPONSE_SUPPORT",
        **basis,
        "preregistered_contract_sha256": canonical_sha256(basis),
    }
    JSON_OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    lines = [
        "# T7 universal response-support preregistration",
        "",
        f"- Status: `{payload['status']}`",
        f"- Contract SHA-256: `{payload['preregistered_contract_sha256']}`",
        "- Cells: `12` (`3 configurations × 2 fits × 2 exact repeats`)",
        "- Training: `0 steps`",
        "- Robot/RDK-X5 access: `forbidden`",
        "",
        "## Causal question",
        "",
        "Does the frozen V91/V96 universal target keep the exact current composed "
        "robot supported for 600 ticks while producing a repeatable, "
        "configuration-sensitive 64-D response context?",
        "",
        "## Historical mismatch",
        "",
        causal_audit["training_wrapper"],
        "",
        causal_audit["formal_evaluator"],
        "",
        "T7 therefore runs the preserved universal-target graph directly. It "
        "does not treat the old V103 prefix failure as evidence against this "
        "mechanism.",
        "",
        "## Decision",
        "",
        f"- Pass: {decision_rule['pass_next_action']}.",
        f"- Fail: {decision_rule['fail_next_action']}.",
        "",
        "A pass does not authorize training, Gate 5, robot access, torque, "
        "motion, or deployment.",
    ]
    MARKDOWN_OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(payload["status"])
    print(f"contract_sha256={payload['preregistered_contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
