#!/usr/bin/env python3
"""Preregister the Winner-v17 sign-consistent support-combination diagnostic."""

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
    ANALYSIS / "winner_v17_support_action_combination_diagnostic_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "WINNER_V17_SUPPORT_ACTION_COMBINATION_DIAGNOSTIC_PREREGISTRATION_20260721.md"
)
TRAINING_RESULT = ANALYSIS / "winner_v15_pitch_margin_support_training_result.json"
FORMAL_RESULT = ANALYSIS / "winner_v15_pitch_margin_support_gate_result.json"
V16_RESULT = (
    ANALYSIS / "winner_v16_support_action_direction_diagnostic_v2_result.json"
)
HOLD_ATTRIBUTION = (
    ANALYSIS / "winner_v16_support_action_direction_hold_attribution.json"
)
RUNNER = ROOT / "tools/run_winner_v17_support_action_combination_diagnostic.py"
SOURCES = {
    "builder": Path(
        "tools/build_winner_v17_support_action_combination_diagnostic_preregistration.py"
    ),
    "runner": Path("tools/run_winner_v17_support_action_combination_diagnostic.py"),
    "combination": Path("patches/winner_v17_support_action_combination.py"),
    "combination_tests": Path("tests/test_winner_v17_support_action_combination.py"),
    "runner_tests": Path(
        "tests/test_winner_v17_support_action_combination_diagnostic.py"
    ),
    "preregistration_tests": Path(
        "tests/test_winner_v17_support_action_combination_diagnostic_preregistration.py"
    ),
    "workflow": Path(
        ".github/workflows/winner-v17-support-action-combination-diagnostic.yml"
    ),
    "direction_result": Path(
        "outputs/analysis/winner_v16_support_action_direction_diagnostic_v2_result.json"
    ),
    "hold_attribution": Path(
        "outputs/analysis/winner_v16_support_action_direction_hold_attribution.json"
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
    "direction_transform": Path("patches/winner_v16_support_action_direction.py"),
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
    spec = importlib.util.spec_from_file_location("winner_v17_runner", RUNNER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load Winner-v17 runner")
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
            raise FileExistsError(f"refusing to overwrite Winner-v17 preregistration: {path}")

    training = json.loads(TRAINING_RESULT.read_text(encoding="utf-8"))
    formal = json.loads(FORMAL_RESULT.read_text(encoding="utf-8"))
    direction_result = json.loads(V16_RESULT.read_text(encoding="utf-8"))
    hold = json.loads(HOLD_ATTRIBUTION.read_text(encoding="utf-8"))
    if (
        training.get("status")
        != "PASS_WINNER_V15_PITCH_MARGIN_SUPPORT_TRAINING_ARTIFACT"
        or training.get("failed_checks") != []
        or formal.get("status") != "HOLD_WINNER_V15_PITCH_MARGIN_SUPPORT_GATE"
        or direction_result.get("status")
        != "PASS_WINNER_V16_SUPPORT_ACTION_DIRECTION_DIAGNOSTIC_V2"
        or direction_result.get("full_pass_candidates") != []
        or hold.get("status")
        != "PASS_WINNER_V16_SUPPORT_ACTION_DIRECTION_HOLD_ATTRIBUTION"
        or hold.get("decision")
        != "CLOSE_SINGLE_AXIS_CONSTANT_OFFSET_PREREGISTER_SIGN_CONSISTENT_COMBINATION_DIAGNOSTIC"
    ):
        raise ValueError("Winner-v17 source decision changed")
    repository = training.get("repository_attribution", {})
    if (
        repository.get("repository") != "RobVanProd/open-duck-mini-rdkx5"
        or repository.get("github_run_attempt") != 1
    ):
        raise ValueError("Winner-v17 training artifact attribution changed")
    runner = load_runner()
    interventions = [dict(row) for row in runner.INTERVENTIONS]
    if len(interventions) != 8 or interventions[0]["id"] != "BASELINE":
        raise ValueError("Winner-v17 intervention population changed")
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
            "winner_v17.support_action_combination_diagnostic_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_WINNER_V17_SUPPORT_ACTION_COMBINATION_DIAGNOSTIC"
        ),
        "decision": (
            "AUTHORIZE_ONE_CPU_ONLY_SIGN_CONSISTENT_COMBINATION_DIAGNOSTIC"
        ),
        "hypothesis": (
            "The unanimous hip-negative, knee-positive, and ankle-positive survival "
            "directions interact additively enough that at least one nonempty subset "
            "passes all negative-X cells at both frozen checkpoints."
        ),
        "causal_basis": {
            name: hold["direction_evidence"][name]
            for name in ("HIP_MAG_NEG", "KNEE_POS", "ANKLE_POS")
        },
        "frozen_screen": {
            "checkpoint_labels": ["half", "final"],
            "failure_configuration_ids": list(runner.FAILURE_IDS),
            "plants": ["P30_ALL_JOINT", "P31_34_PITCH_WITH_P30_NONPITCH"],
            "interventions": interventions,
            "target_offset_per_active_axis_rad": 0.03,
            "normalized_offset_per_active_axis": 0.12,
            "duration_ticks": 250,
            "cells_per_checkpoint_intervention": 12,
            "total_cells": 192,
            "optimizer_updates": 0,
        },
        "baseline_reproduction": {
            "derived_float_fields": ["terminal", "episode"],
            "finite_absolute_tolerance": runner.DERIVED_FLOAT_ABS_TOLERANCE,
            "all_other_compared_fields": "exact",
            "observation_action_prediction_hidden_trace_hashes": "exact",
        },
        "validity_rule": (
            "The baseline must reproduce all 24 exact trace hashes and gate-setting "
            "fields under the reviewed derived-float tolerance. All 192 cells must "
            "preserve exact combination math, graph bounds, finite values, and zero "
            "optimizer/robot access."
        ),
        "advancement_rule": (
            "Only a combination passing all 12 cells at both checkpoints advances. "
            "Select fewest active axes, then minimum maximum action deviation, then "
            "minimum mean-squared deviation, then frozen intervention order. No closest "
            "failing combination advances."
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
                "a separate CPU-only selected-combination contract preregistration"
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
                "# Winner-v17 support action-combination diagnostic preregistration",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                "- Interventions: baseline plus all seven nonempty subsets of the",
                "  evidence-selected hip-negative, knee-positive, ankle-positive vector",
                "- Population: `192` CPU-only cells",
                "- Optimizer / locomotion / robot: `0 / 0 / 0`",
                "",
                "This is not a closest-single-axis promotion. Each chosen sign beat both",
                "baseline and its opposite in all `24/24` paired cells. Only a complete",
                "two-checkpoint pass can advance; no closest failing subset advances.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
