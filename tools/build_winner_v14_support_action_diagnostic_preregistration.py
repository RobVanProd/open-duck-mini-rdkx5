#!/usr/bin/env python3
"""Freeze the Winner-v14 normalized-score support-action diagnostic."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v14_support_action_diagnostic_preregistration.json"
MARKDOWN = ANALYSIS / "WINNER_V14_SUPPORT_ACTION_DIAGNOSTIC_PREREGISTRATION_20260721.md"
FORMAL = ANALYSIS / "winner_v13_support_controller_gate_result.json"
ATTRIBUTION = ANALYSIS / "winner_v13_support_controller_hold_attribution.json"
V13_PREREG = ANALYSIS / "winner_v13_support_controller_gate_preregistration.json"
TRAINING = ANALYSIS / "winner_v13_support_controller_training_result.json"
EPISODE_BINDING_ATTRIBUTION = (
    ANALYSIS / "winner_v14_support_action_episode_binding_failure_attribution.json"
)
EXPECTED_FORMAL_SHA256 = (
    "350bd845a27bf0257e2569f5bc1027a76f8e0fcb551cffff745cb43068f9ad2a"
)
EXPECTED_FORMAL_LF_SHA256 = (
    "ad6e0ea99cf0d96fbcd336d7984467efccdd430591201d6fd5242a328518ce05"
)
SCALES = [0.0, 0.25, 0.5, 0.75, 1.0]
SOURCES = {
    "builder": Path(
        "tools/build_winner_v14_support_action_diagnostic_preregistration.py"
    ),
    "runner": Path("tools/run_winner_v14_support_action_diagnostic.py"),
    "primitives": Path("patches/winner_v14_support_action_diagnostic.py"),
    "tests": Path("tests/test_winner_v14_support_action_diagnostic.py"),
    "workflow": Path(".github/workflows/winner-v14-support-action-diagnostic.yml"),
    "hold_attribution": Path(
        "outputs/analysis/winner_v13_support_controller_hold_attribution.json"
    ),
    "preexecution_failure_attribution": Path(
        "outputs/analysis/winner_v14_support_action_preexecution_failure_attribution.json"
    ),
    "episode_binding_failure_attribution": Path(
        "outputs/analysis/winner_v14_support_action_episode_binding_failure_attribution.json"
    ),
    "episode_binding_failure_attribution_builder": Path(
        "tools/build_winner_v14_support_action_episode_binding_failure_attribution.py"
    ),
    "episode_binding_failure_attribution_test": Path(
        "tests/test_winner_v14_support_action_episode_binding_failure_attribution.py"
    ),
    "formal_gate_result": Path(
        "outputs/analysis/winner_v13_support_controller_gate_result.json"
    ),
    "formal_gate_preregistration": Path(
        "outputs/analysis/winner_v13_support_controller_gate_preregistration.json"
    ),
    "v13_gate_runner": Path("tools/run_winner_v13_support_controller_gate.py"),
    "reviewed_base_gate_runner": Path(
        "tools/run_winner_v12_calibrator_support_gate.py"
    ),
    "training_result": Path(
        "outputs/analysis/winner_v13_support_controller_training_result.json"
    ),
    "normalized_stage1_result": Path(
        "outputs/analysis/winner_v13_normalized_response_stage1_v2_result.json"
    ),
    "normalized_training_primitives": Path(
        "patches/winner_v13_normalized_calibrator_training.py"
    ),
    "legacy_training_primitives": Path(
        "patches/winner_v12_calibrator_training.py"
    ),
    "deployable_network": Path("patches/winner_v12_decomposed_backend_networks.py"),
    "configuration_domain": Path(
        "outputs/analysis/winner_v3_variable_configuration_replacement_preregistration.json"
    ),
    "runtime_observer": Path(
        "artifacts/runtime_handoff/rdkx5_native_20260719/observer/winner_v2_contract.py"
    ),
    "canonical_p30_fit": Path(
        "outputs/analysis/fixed_target_p30_actuator_fit_20260712.json"
    ),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite preregistration: {path}")

    formal = json.loads(FORMAL.read_text(encoding="utf-8"))
    attribution = json.loads(ATTRIBUTION.read_text(encoding="utf-8"))
    preexecution = json.loads(
        (ANALYSIS / "winner_v14_support_action_preexecution_failure_attribution.json").read_text(
            encoding="utf-8"
        )
    )
    episode_binding = json.loads(
        EPISODE_BINDING_ATTRIBUTION.read_text(encoding="utf-8")
    )
    v13_prereg = json.loads(V13_PREREG.read_text(encoding="utf-8"))
    training = json.loads(TRAINING.read_text(encoding="utf-8"))
    if (
        sha256(FORMAL) != EXPECTED_FORMAL_SHA256
        or lf_sha256(FORMAL) != EXPECTED_FORMAL_LF_SHA256
        or formal.get("status") != "HOLD_WINNER_V13_SUPPORT_CONTROLLER_GATE"
        or attribution.get("status")
        != "PASS_WINNER_V13_SUPPORT_CONTROLLER_HOLD_ATTRIBUTION"
        or attribution.get("decision")
        != "KEEP_GATE_HOLD_CORRECT_REPORTING_BEFORE_CAUSAL_REPAIR"
        or attribution.get("evidence_selected_next_step", {}).get(
            "flat_transport_kernel_selected"
        )
        is not False
        or training.get("status")
        != "PASS_WINNER_V13_SUPPORT_CONTROLLER_TRAINING_ARTIFACT"
        or preexecution.get("status")
        != "INVALID_WINNER_V14_SUPPORT_ACTION_DIAGNOSTIC_PREEXECUTION"
        or preexecution.get("decision")
        != "CORRECT_ONLY_FORMAL_RESULT_HASH_MODE_AND_FRESHLY_PREREGISTER"
        or preexecution.get("execution", {}).get("main_cells") != 0
        or episode_binding.get("status")
        != "INVALID_WINNER_V14_SUPPORT_ACTION_DIAGNOSTIC_EPISODE_BINDING"
        or episode_binding.get("decision")
        != "CORRECT_ONLY_REVIEWED_EPISODE_TYPE_BINDING_AND_FRESHLY_PREREGISTER"
        or episode_binding.get("execution", {}).get("completed_main_cells") != 0
        or episode_binding.get("execution", {}).get("completed_repeat_cells") != 0
        or episode_binding.get("execution", {}).get("result_json_created") is not False
    ):
        raise ValueError("Winner-v14 diagnostic source evidence changed")
    old_gate = v13_prereg["future_frozen_support_gate"]
    if (
        old_gate["cells_per_checkpoint"] != 124
        or old_gate["duration_ticks"] != 250
        or old_gate["checkpoint_labels"] != ["half", "final"]
    ):
        raise ValueError("Winner-v13 gate dimensions changed")
    sources = {
        name: {
            "path": str(path).replace("\\", "/"),
            "hash_mode": "lf",
            "sha256": lf_sha256(ROOT / path),
        }
        for name, path in SOURCES.items()
    }
    payload = {
        "schema_version": "winner_v14.support_action_diagnostic_preregistration.v3",
        "status": "PREREGISTERED_WINNER_V14_SUPPORT_ACTION_DIAGNOSTIC_V3",
        "decision": "AUTHORIZE_ONE_EPISODE_BINDING_CORRECTED_CPU_ONLY_FIVE_SCALE_SUPPORT_DIAGNOSTIC",
        "causal_question": (
            "Can a fixed reduction of the deployable calibration action preserve "
            "identifiable response context while preventing the observed negative-X "
            "early pitch exits across the complete unchanged support gate?"
        ),
        "frozen_screen": {
            "scales": SCALES,
            "checkpoint_labels": ["half", "final"],
            "cells_per_checkpoint_scale": 124,
            "heldout_repeats_per_checkpoint_scale": 32,
            "main_cells": 1240,
            "repeat_cells": 320,
            "duration_ticks": 250,
            "sensor_noise_seed_includes_scale": False,
        },
        "single_change": {
            "source_action": "the frozen checkpoint's final bounded 14-D ONNX action",
            "candidate": "float32(scale) * source_action",
            "final_action": (
                "clip candidate to [-1,1] and to previous_action +/- the unchanged "
                "per-joint graph delta"
            ),
            "state_feedback": "final_action is the next previous_action",
            "scope": (
                "diagnostic emulation of an append-only graph-owned transform; no "
                "runtime host limiter or deployable graph is produced here"
            ),
            "scale_one_must_reproduce_all_formal_cells": True,
        },
        "scoring_correction": {
            "prediction_coordinates": "normalized response",
            "target_coordinates": "(target_raw - target_mean) / target_std",
            "learned_error": (
                "square(prediction_normalized - "
                "((target_raw - target_mean) / target_std))"
            ),
            "constant_baseline": "square((target_raw - target_mean) / target_std)",
            "formal_v13_result_is_not_rewritten": True,
        },
        "unchanged_gates": {
            "physical_support": old_gate["gates"],
            "sensor_transport_population": old_gate["sensor_transport_population"],
            "sensor_transport_population_sha256": old_gate[
                "sensor_transport_population_sha256"
            ],
            "heldout_context_linf_strictly_above": 1.0e-7,
            "heldout_prediction": (
                "corrected learned aggregate strictly below the identical constant "
                "baseline separately by checkpoint and plant"
            ),
            "repeat": (
                "all actions, source actions, observations, normalized predictions, "
                "and hidden states bit-exact in all 32 repeats per checkpoint/scale"
            ),
            "all_124_main_cells_must_pass": True,
            "both_checkpoints_must_pass": True,
        },
        "selection_rule": {
            "complete_pass": (
                "all unchanged physical, action-bound, hidden, repeat, context, and "
                "corrected-predictor checks pass at both checkpoints"
            ),
            "winner": "largest complete-pass scale",
            "why_largest": "retain maximum response excitation among complete passes",
            "no_complete_pass": (
                "select no scale and preregister a support-objective repair; no "
                "post-hoc scale or closest result"
            ),
        },
        "formal_result": {
            "path": str(FORMAL.relative_to(ROOT)).replace("\\", "/"),
            "windows_raw_sha256": EXPECTED_FORMAL_SHA256,
            "cross_platform_lf_sha256": EXPECTED_FORMAL_LF_SHA256,
        },
        "preexecution_correction": {
            "failed_run_id": 29833400247,
            "failed_run_main_cells": 0,
            "failed_run_repeat_cells": 0,
            "only_change": "formal result comparison uses LF-normalized SHA-256",
        },
        "correction_history": [
            {
                "failed_run_id": 29833400247,
                "completed_main_cells": 0,
                "completed_repeat_cells": 0,
                "result_json_created": False,
                "only_change": "formal result comparison uses LF-normalized SHA-256",
            },
            {
                "failed_run_id": 29833729219,
                "completed_main_cells": 0,
                "completed_repeat_cells": 0,
                "result_json_created": False,
                "only_change": "replace base.Episode with base.smoke.Episode",
            },
        ],
        "training_artifact": v13_prereg["training_artifact"],
        "execution_now": {
            "optimizer_updates": 0,
            "main_cells": 0,
            "repeat_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "robot_clearance": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "pass_authorizes_only": (
                "a separate selected-scale graph-transform contract, or a separate "
                "support-objective preregistration when no scale passes"
            ),
        },
        "sources": sources,
        "source_manifest_sha256": canonical_sha256(sources),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown.write_text(
        "\n".join(
            [
                "# Winner-v14 support-action diagnostic preregistration",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                "- Scales: `0 / .25 / .50 / .75 / 1.0`",
                "- Main / repeat cells: `1,240 / 320`",
                "- Training / locomotion / robot access: `0 / 0 / 0`",
                "",
                "This is one finite causal screen, not post-hoc tuning. Each scale",
                "runs the complete unchanged support/context gate at both persistent",
                "checkpoints. The source action is scaled and rebound against the same",
                "graph limits, with the realized final action returned as state.",
                "",
                "Predictor scoring is corrected for the normalized Stage-1 head without",
                "rewriting the frozen Winner-v13 HOLD. The largest complete-pass scale",
                "advances only to a separate graph-transform contract. If no scale passes,",
                "the entire inference-scale repair closes.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(json.dumps({"status": payload["status"], "sha256": sha256(args.output)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
