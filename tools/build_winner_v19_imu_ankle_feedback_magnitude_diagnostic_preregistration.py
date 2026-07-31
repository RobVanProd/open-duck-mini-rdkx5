#!/usr/bin/env python3
"""Preregister the Winner-v19 feedback-magnitude feasibility screen."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = (
    ANALYSIS / "winner_v19_imu_ankle_feedback_magnitude_diagnostic_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "WINNER_V19_IMU_ANKLE_FEEDBACK_MAGNITUDE_DIAGNOSTIC_PREREGISTRATION_20260721.md"
)
TRAINING_RESULT = ANALYSIS / "winner_v15_pitch_margin_support_training_result.json"
FORMAL_RESULT = ANALYSIS / "winner_v15_pitch_margin_support_gate_result.json"
V18_RESULT = ANALYSIS / "winner_v18_imu_ankle_feedback_diagnostic_result.json"
HOLD_ATTRIBUTION = ANALYSIS / "winner_v18_imu_ankle_feedback_hold_attribution.json"
RUNNER = ROOT / "tools/run_winner_v19_imu_ankle_feedback_magnitude_diagnostic.py"
SOURCES = {
    "builder": Path(
        "tools/build_winner_v19_imu_ankle_feedback_magnitude_diagnostic_preregistration.py"
    ),
    "runner": Path("tools/run_winner_v19_imu_ankle_feedback_magnitude_diagnostic.py"),
    "magnitude": Path("patches/winner_v19_imu_ankle_feedback_magnitude.py"),
    "magnitude_tests": Path("tests/test_winner_v19_imu_ankle_feedback_magnitude.py"),
    "runner_tests": Path(
        "tests/test_winner_v19_imu_ankle_feedback_magnitude_diagnostic.py"
    ),
    "preregistration_tests": Path(
        "tests/test_winner_v19_imu_ankle_feedback_magnitude_diagnostic_preregistration.py"
    ),
    "workflow": Path(
        ".github/workflows/winner-v19-imu-ankle-feedback-magnitude-diagnostic.yml"
    ),
    "feedback_result": Path(
        "outputs/analysis/winner_v18_imu_ankle_feedback_diagnostic_result.json"
    ),
    "hold_attribution": Path(
        "outputs/analysis/winner_v18_imu_ankle_feedback_hold_attribution.json"
    ),
    "training_result": Path(
        "outputs/analysis/winner_v15_pitch_margin_support_training_result.json"
    ),
    "formal_result": Path(
        "outputs/analysis/winner_v15_pitch_margin_support_gate_result.json"
    ),
    "feedback_base_runner": Path("tools/run_winner_v18_imu_ankle_feedback_diagnostic.py"),
    "feedback_base": Path("patches/winner_v18_imu_ankle_feedback.py"),
    "direction_base_runner": Path(
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
    spec = importlib.util.spec_from_file_location("winner_v19_runner", RUNNER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load Winner-v19 runner")
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
            raise FileExistsError(f"refusing to overwrite Winner-v19 preregistration: {path}")
    training = json.loads(TRAINING_RESULT.read_text(encoding="utf-8"))
    formal = json.loads(FORMAL_RESULT.read_text(encoding="utf-8"))
    feedback_result = json.loads(V18_RESULT.read_text(encoding="utf-8"))
    hold = json.loads(HOLD_ATTRIBUTION.read_text(encoding="utf-8"))
    if (
        training.get("status")
        != "PASS_WINNER_V15_PITCH_MARGIN_SUPPORT_TRAINING_ARTIFACT"
        or training.get("failed_checks") != []
        or formal.get("status") != "HOLD_WINNER_V15_PITCH_MARGIN_SUPPORT_GATE"
        or feedback_result.get("status")
        != "PASS_WINNER_V18_IMU_ANKLE_FEEDBACK_DIAGNOSTIC"
        or feedback_result.get("full_pass_candidates") != []
        or hold.get("status")
        != "PASS_WINNER_V18_IMU_ANKLE_FEEDBACK_HOLD_ATTRIBUTION"
        or hold.get("decision")
        != "CLOSE_003_RAD_FEEDBACK_PREREGISTER_ONE_VARIABLE_MAGNITUDE_FEASIBILITY_SCREEN"
    ):
        raise ValueError("Winner-v19 source decision changed")
    repository = training.get("repository_attribution", {})
    if (
        repository.get("repository") != "RobVanProd/open-duck-mini-rdkx5"
        or repository.get("github_run_attempt") != 1
    ):
        raise ValueError("Winner-v19 training artifact attribution changed")
    runner = load_runner()
    interventions = [dict(row) for row in runner.INTERVENTIONS]
    if len(interventions) != 7 or interventions[0]["id"] != "BASELINE":
        raise ValueError("Winner-v19 intervention population changed")
    sources = {
        name: {
            "path": str(path).replace("\\", "/"),
            "hash_mode": "lf",
            "sha256": lf_sha256(ROOT / path),
        }
        for name, path in SOURCES.items()
    }
    payload = {
        "schema_version": (
            "winner_v19.imu_ankle_feedback_magnitude_diagnostic_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_WINNER_V19_IMU_ANKLE_FEEDBACK_MAGNITUDE_DIAGNOSTIC"
        ),
        "decision": "AUTHORIZE_ONE_CPU_ONLY_FEEDBACK_MAGNITUDE_FEASIBILITY_SCREEN",
        "hypothesis": (
            "Winner-v18 failed because one-sided feedback averaged only 31.3 percent "
            "activation under a 0.03-rad ceiling; a frozen 2x or 3x ceiling can supply "
            "enough conditional ankle correction to pass without changing the feedback law."
        ),
        "magnitude_basis": hold["magnitude_basis"],
        "frozen_screen": {
            "checkpoint_labels": ["half", "final"],
            "failure_configuration_ids": list(runner.FAILURE_IDS),
            "plants": ["P30_ALL_JOINT", "P31_34_PITCH_WITH_P30_NONPITCH"],
            "interventions": interventions,
            "maximum_target_offsets_rad": [0.03, 0.06, 0.09],
            "tilt_boundary_rad": 0.35,
            "rate_reference_rad_s": 1.75,
            "duration_ticks": 250,
            "cells_per_checkpoint_intervention": 12,
            "total_cells": 168,
            "optimizer_updates": 0,
        },
        "feedback_semantics": {
            "constant": "activation is exactly one",
            "state_dependent": "unchanged Winner-v18 max(backward tilt, backward gyro-y rate)",
            "only_variable": "maximum target offset 0.03, 0.06, or 0.09 rad",
            "application": "reapply exact graph absolute and per-tick action bounds",
        },
        "baseline_reproduction": {
            "derived_float_fields": ["terminal", "episode"],
            "finite_absolute_tolerance": runner.v18.v2.DERIVED_FLOAT_ABS_TOLERANCE,
            "all_other_compared_fields": "exact",
            "observation_action_prediction_hidden_trace_hashes": "exact",
        },
        "validity_rule": (
            "The baseline must reproduce all 24 formal trace hashes and gate fields; all "
            "168 cells must preserve exact feedback math, graph bounds, finite values, "
            "and zero optimizer/robot access."
        ),
        "advancement_rule": (
            "Only a mode passing all 12 cells at both checkpoints advances. Select the "
            "smallest maximum target offset, then minimum mean-squared action deviation, "
            "then frozen order. No closest failing mode advances."
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
                "a separate CPU-only selected-magnitude contract preregistration"
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
                "# Winner-v19 IMU ankle-feedback magnitude preregistration",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                "- Only variable: maximum target offset `0.03 / 0.06 / 0.09 rad`",
                "- Population: `168` CPU-only cells",
                "- Optimizer / locomotion / robot: `0 / 0 / 0`",
                "",
                "The 3x ceiling is derived from Winner-v18's `0.313` combined mean",
                "activation; 2x is the frozen bridge. The feedback law, policy, checkpoints,",
                "population, bounds, and full-pass-only rule remain unchanged.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
