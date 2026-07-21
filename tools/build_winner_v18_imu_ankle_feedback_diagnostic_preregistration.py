#!/usr/bin/env python3
"""Preregister the Winner-v18 one-sided IMU ankle-feedback diagnostic."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v18_imu_ankle_feedback_diagnostic_preregistration.json"
MARKDOWN = (
    ANALYSIS / "WINNER_V18_IMU_ANKLE_FEEDBACK_DIAGNOSTIC_PREREGISTRATION_20260721.md"
)
TRAINING_RESULT = ANALYSIS / "winner_v15_pitch_margin_support_training_result.json"
FORMAL_RESULT = ANALYSIS / "winner_v15_pitch_margin_support_gate_result.json"
V17_RESULT = ANALYSIS / "winner_v17_support_action_combination_diagnostic_result.json"
HOLD_ATTRIBUTION = (
    ANALYSIS / "winner_v17_support_action_combination_hold_attribution.json"
)
RUNNER = ROOT / "tools/run_winner_v18_imu_ankle_feedback_diagnostic.py"
SOURCES = {
    "builder": Path(
        "tools/build_winner_v18_imu_ankle_feedback_diagnostic_preregistration.py"
    ),
    "runner": Path("tools/run_winner_v18_imu_ankle_feedback_diagnostic.py"),
    "feedback": Path("patches/winner_v18_imu_ankle_feedback.py"),
    "feedback_tests": Path("tests/test_winner_v18_imu_ankle_feedback.py"),
    "runner_tests": Path("tests/test_winner_v18_imu_ankle_feedback_diagnostic.py"),
    "preregistration_tests": Path(
        "tests/test_winner_v18_imu_ankle_feedback_diagnostic_preregistration.py"
    ),
    "workflow": Path(".github/workflows/winner-v18-imu-ankle-feedback-diagnostic.yml"),
    "combination_result": Path(
        "outputs/analysis/winner_v17_support_action_combination_diagnostic_result.json"
    ),
    "hold_attribution": Path(
        "outputs/analysis/winner_v17_support_action_combination_hold_attribution.json"
    ),
    "training_result": Path(
        "outputs/analysis/winner_v15_pitch_margin_support_training_result.json"
    ),
    "formal_result": Path(
        "outputs/analysis/winner_v15_pitch_margin_support_gate_result.json"
    ),
    "base_direction_runner": Path(
        "tools/run_winner_v16_support_action_direction_diagnostic.py"
    ),
    "baseline_comparator_runner": Path(
        "tools/run_winner_v16_support_action_direction_diagnostic_v2.py"
    ),
    "v14_diagnostic_runner": Path("tools/run_winner_v14_support_action_diagnostic.py"),
    "v14_transform": Path("patches/winner_v14_support_action_diagnostic.py"),
    "v15_gate_adapter": Path("tools/run_winner_v15_pitch_margin_support_gate.py"),
    "environment_preparation": Path("tools/prepare_winner_v15_cpu_environment.py"),
    "base_gate_runner": Path("tools/run_winner_v12_calibrator_support_gate.py"),
    "calibrator_design_preregistration": Path(
        "outputs/analysis/winner_v12_calibrator_training_preregistration.json"
    ),
    "variable_configuration_domain": Path(
        "outputs/analysis/winner_v3_variable_configuration_replacement_preregistration.json"
    ),
    "normalized_training": Path("patches/winner_v13_normalized_calibrator_training.py"),
    "deployable_network": Path("patches/winner_v12_decomposed_backend_networks.py"),
}


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def load_runner() -> Any:
    spec = importlib.util.spec_from_file_location("winner_v18_runner", RUNNER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load Winner-v18 runner")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite Winner-v18 preregistration: {path}")
    training = json.loads(TRAINING_RESULT.read_text(encoding="utf-8"))
    formal = json.loads(FORMAL_RESULT.read_text(encoding="utf-8"))
    combination = json.loads(V17_RESULT.read_text(encoding="utf-8"))
    hold = json.loads(HOLD_ATTRIBUTION.read_text(encoding="utf-8"))
    if (
        training.get("status")
        != "PASS_WINNER_V15_PITCH_MARGIN_SUPPORT_TRAINING_ARTIFACT"
        or training.get("failed_checks") != []
        or formal.get("status") != "HOLD_WINNER_V15_PITCH_MARGIN_SUPPORT_GATE"
        or combination.get("status")
        != "PASS_WINNER_V17_SUPPORT_ACTION_COMBINATION_DIAGNOSTIC"
        or combination.get("full_pass_candidates") != []
        or hold.get("status")
        != "PASS_WINNER_V17_SUPPORT_ACTION_COMBINATION_HOLD_ATTRIBUTION"
        or hold.get("decision")
        != "CLOSE_FIXED_003_RAD_OFFSET_SUBSET_PREREGISTER_ONE_SIDED_IMU_ANKLE_FEEDBACK_DIAGNOSTIC"
    ):
        raise ValueError("Winner-v18 source decision changed")
    repository = training.get("repository_attribution", {})
    if (
        repository.get("repository") != "RobVanProd/open-duck-mini-rdkx5"
        or repository.get("github_run_attempt") != 1
    ):
        raise ValueError("Winner-v18 training artifact attribution changed")
    runner = load_runner()
    interventions = [dict(row) for row in runner.INTERVENTIONS]
    if len(interventions) != 7 or interventions[0]["id"] != "BASELINE":
        raise ValueError("Winner-v18 intervention population changed")
    sources = {
        name: {
            "path": str(path).replace("\\", "/"),
            "hash_mode": "lf",
            "sha256": lf_sha256(ROOT / path),
        }
        for name, path in SOURCES.items()
    }
    payload = {
        "schema_version": "winner_v18.imu_ankle_feedback_diagnostic_preregistration.v1",
        "status": "PREREGISTERED_WINNER_V18_IMU_ANKLE_FEEDBACK_DIAGNOSTIC",
        "decision": (
            "AUTHORIZE_ONE_CPU_ONLY_ONE_SIDED_IMU_ANKLE_FEEDBACK_DIAGNOSTIC"
        ),
        "hypothesis": (
            "The positive-ankle survival direction fails when continuously asserted but "
            "can pass when its magnitude is one-sided and proportional to deployable "
            "backward tilt and/or pitch-rate observations."
        ),
        "frozen_screen": {
            "checkpoint_labels": ["half", "final"],
            "failure_configuration_ids": list(runner.FAILURE_IDS),
            "plants": ["P30_ALL_JOINT", "P31_34_PITCH_WITH_P30_NONPITCH"],
            "interventions": interventions,
            "maximum_target_offset_rad": 0.03,
            "maximum_normalized_offset": 0.12,
            "tilt_boundary_rad": 0.35,
            "rate_reference_rad_s": 1.75,
            "gyro_pitch_rate_observation_index": 1,
            "accelerometer_observation_slice": [3, 6],
            "duration_ticks": 250,
            "cells_per_checkpoint_intervention": 12,
            "total_cells": 168,
            "optimizer_updates": 0,
        },
        "feedback_semantics": {
            "pitch_proxy": "atan2(-accelerometer_x, hypot(accelerometer_y, accelerometer_z))",
            "backward_tilt_activation": "clip(-pitch_proxy / 0.35, 0, 1)",
            "opposite_tilt_activation": "clip(pitch_proxy / 0.35, 0, 1)",
            "backward_rate_activation": "clip(-gyro_y / 1.75, 0, 1)",
            "opposite_rate_activation": "clip(gyro_y / 1.75, 0, 1)",
            "combined_activation": "max(backward_tilt_activation, backward_rate_activation)",
            "application": (
                "add activation * 0.12 to both ankle action coordinates, then reapply "
                "exact graph absolute and per-tick bounds"
            ),
        },
        "baseline_reproduction": {
            "derived_float_fields": ["terminal", "episode"],
            "finite_absolute_tolerance": runner.v2.DERIVED_FLOAT_ABS_TOLERANCE,
            "all_other_compared_fields": "exact",
            "observation_action_prediction_hidden_trace_hashes": "exact",
        },
        "validity_rule": (
            "The baseline must reproduce all 24 formal trace hashes and gate fields; all "
            "168 cells must preserve exact feedback math, action bounds, finite values, "
            "and zero optimizer/robot access."
        ),
        "advancement_rule": (
            "Only a feedback mode passing all 12 cells at both checkpoints advances. "
            "If several pass, select minimum maximum action deviation, then minimum "
            "mean-squared deviation, then frozen intervention order. No closest failing "
            "mode advances."
        ),
        "training_artifact": {
            "repository_attribution": repository,
            "half": {
                "snapshot": training["snapshot_manifest"][49],
                "graph": training["persistent_checkpoints"][0]["graph"],
            },
            "final": {
                "snapshot": training["snapshot_manifest"][99],
                "graph": training["persistent_checkpoints"][1]["graph"],
            },
        },
        "execution_now": {
            "optimizer_updates": 0,
            "diagnostic_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "robot_clearance": False,
            "training_authorized": False,
            "pass_authorizes_only": (
                "a separate CPU-only selected-feedback contract preregistration"
            ),
        },
        "sources": sources,
        "source_manifest_sha256": canonical_sha256(sources),
    }
    args.output.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown.write_text(
        "\n".join(
            [
                "# Winner-v18 IMU ankle-feedback diagnostic preregistration",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                "- Inputs: deployable `obs[1]` gyro-y and `obs[3:6]` accelerometer",
                "- Maximum ankle offset: `0.03 rad`",
                "- Population: `168` CPU-only cells",
                "- Optimizer / locomotion / robot: `0 / 0 / 0`",
                "",
                "The screen compares baseline, the closed constant ankle offset, one-sided",
                "tilt/rate feedback and their opposite-sign controls, plus combined backward",
                "feedback. Only a full two-checkpoint pass advances.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
