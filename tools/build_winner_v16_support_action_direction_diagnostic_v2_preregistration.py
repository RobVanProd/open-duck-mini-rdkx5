#!/usr/bin/env python3
"""Preregister the comparator-corrected Winner-v16 direction diagnostic."""

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
    ANALYSIS
    / "winner_v16_support_action_direction_diagnostic_v2_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "WINNER_V16_SUPPORT_ACTION_DIRECTION_DIAGNOSTIC_V2_PREREGISTRATION_20260721.md"
)
TRAINING_RESULT = ANALYSIS / "winner_v15_pitch_margin_support_training_result.json"
FORMAL_RESULT = ANALYSIS / "winner_v15_pitch_margin_support_gate_result.json"
HOLD_ATTRIBUTION = ANALYSIS / "winner_v15_pitch_margin_support_hold_attribution.json"
INVALID_ATTRIBUTION = (
    ANALYSIS / "winner_v16_support_action_direction_invalid_attribution.json"
)
RUNNER = ROOT / "tools/run_winner_v16_support_action_direction_diagnostic_v2.py"
SOURCES = {
    "builder": Path(
        "tools/build_winner_v16_support_action_direction_diagnostic_v2_preregistration.py"
    ),
    "runner": Path("tools/run_winner_v16_support_action_direction_diagnostic_v2.py"),
    "base_runner": Path("tools/run_winner_v16_support_action_direction_diagnostic.py"),
    "intervention": Path("patches/winner_v16_support_action_direction.py"),
    "intervention_tests": Path("tests/test_winner_v16_support_action_direction.py"),
    "runner_tests": Path(
        "tests/test_winner_v16_support_action_direction_diagnostic_v2.py"
    ),
    "preregistration_tests": Path(
        "tests/test_winner_v16_support_action_direction_diagnostic_v2_preregistration.py"
    ),
    "workflow": Path(
        ".github/workflows/winner-v16-support-action-direction-diagnostic-v2.yml"
    ),
    "invalid_attribution": Path(
        "outputs/analysis/winner_v16_support_action_direction_invalid_attribution.json"
    ),
    "hold_attribution": Path(
        "outputs/analysis/winner_v15_pitch_margin_support_hold_attribution.json"
    ),
    "formal_gate_result": Path(
        "outputs/analysis/winner_v15_pitch_margin_support_gate_result.json"
    ),
    "training_result": Path(
        "outputs/analysis/winner_v15_pitch_margin_support_training_result.json"
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
    spec = importlib.util.spec_from_file_location("winner_v16_direction_runner_v2", RUNNER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load Winner-v16 v2 direction runner")
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
            raise FileExistsError(f"refusing to overwrite v2 preregistration: {path}")

    training = json.loads(TRAINING_RESULT.read_text(encoding="utf-8"))
    formal = json.loads(FORMAL_RESULT.read_text(encoding="utf-8"))
    hold = json.loads(HOLD_ATTRIBUTION.read_text(encoding="utf-8"))
    invalid = json.loads(INVALID_ATTRIBUTION.read_text(encoding="utf-8"))
    if (
        training.get("status")
        != "PASS_WINNER_V15_PITCH_MARGIN_SUPPORT_TRAINING_ARTIFACT"
        or training.get("failed_checks") != []
        or formal.get("status") != "HOLD_WINNER_V15_PITCH_MARGIN_SUPPORT_GATE"
        or formal.get("failed_checks") != ["all_248_main_cells_pass"]
        or hold.get("status")
        != "PASS_WINNER_V15_PITCH_MARGIN_SUPPORT_HOLD_ATTRIBUTION"
        or invalid.get("status")
        != "INVALID_WINNER_V16_SUPPORT_ACTION_DIRECTION_DIAGNOSTIC_ATTRIBUTED"
        or invalid.get("decision")
        != "CORRECT_ONLY_BASELINE_DERIVED_FLOAT_COMPARATOR_AND_FRESHLY_PREREGISTER"
    ):
        raise ValueError("Winner-v16 v2 source decision changed")
    repository = training.get("repository_attribution", {})
    if (
        repository.get("repository") != "RobVanProd/open-duck-mini-rdkx5"
        or repository.get("github_run_attempt") != 1
    ):
        raise ValueError("Winner-v16 v2 training attribution changed")
    runner = load_runner()
    interventions = [dict(row) for row in runner.INTERVENTIONS]
    if len(interventions) != 7 or interventions[0]["id"] != "BASELINE":
        raise ValueError("Winner-v16 v2 intervention population changed")
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
            "winner_v16.support_action_direction_diagnostic_preregistration.v2"
        ),
        "status": (
            "PREREGISTERED_WINNER_V16_SUPPORT_ACTION_DIRECTION_DIAGNOSTIC_V2"
        ),
        "decision": (
            "AUTHORIZE_ONE_COMPARATOR_CORRECTED_CPU_ONLY_DIRECTION_DIAGNOSTIC"
        ),
        "hypothesis": (
            "A bounded 0.03-rad bilateral pitch-chain target offset can identify "
            "whether one sagittal support axis has the sign needed to arrest the "
            "persistent negative-X backward-pitch exits."
        ),
        "frozen_screen": {
            "checkpoint_labels": ["half", "final"],
            "failure_configuration_ids": list(runner.FAILURE_IDS),
            "plants": ["P30_ALL_JOINT", "P31_34_PITCH_WITH_P30_NONPITCH"],
            "interventions": interventions,
            "target_offset_rad": 0.03,
            "normalized_offset": 0.12,
            "duration_ticks": 250,
            "cells_per_checkpoint_intervention": 12,
            "total_cells": 168,
            "optimizer_updates": 0,
        },
        "baseline_reproduction": {
            "derived_float_fields": ["terminal", "episode"],
            "finite_absolute_tolerance": runner.DERIVED_FLOAT_ABS_TOLERANCE,
            "all_other_compared_fields": "exact",
            "observation_action_prediction_hidden_trace_hashes": "exact",
        },
        "intervention_semantics": {
            "hip_pitch_magnitude": "left-negative/right-positive home-magnitude parity",
            "knee": "same-sign bilateral logical-coordinate offset",
            "ankle": "same-sign bilateral logical-coordinate offset",
            "application": (
                "add to source action each tick, then reapply exact absolute and "
                "per-tick graph bounds"
            ),
        },
        "validity_rule": (
            "The baseline must reproduce all 24 exact observation/action/prediction/"
            "hidden hashes and all gate-setting categorical fields; only finite derived "
            "terminal/episode doubles may differ by at most 1e-12 absolute. All 168 "
            "cells must retain the frozen intervention math, bounds, and zero optimizer/"
            "robot access."
        ),
        "advancement_rule": (
            "Only an intervention passing all 12 fixed cells at both checkpoints can "
            "advance to a separate CPU contract. If several pass, choose by minimum "
            "maximum action deviation, then minimum mean-squared deviation, then frozen "
            "intervention order. No closest failing result advances."
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
            "response_conditioned_locomotion_training_authorized": False,
            "pass_authorizes_only": (
                "a separate CPU-only selected-direction contract preregistration"
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
                "# Winner-v16 support action-direction diagnostic v2 preregistration",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                "- Screen: unchanged baseline plus six bilateral interventions",
                "- Population: `168` CPU-only cells",
                "- Optimizer / locomotion / robot: `0 / 0 / 0`",
                "",
                "The sole correction is the baseline verifier: policy/observer traces and",
                "gate-setting fields remain exact, while finite derived terminal/episode",
                "doubles have a preregistered `1e-12` absolute tolerance.",
                "",
                "The intervention population, offset, checkpoints, configurations, plants,",
                "thresholds, and no-closest-result selection rule are unchanged.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
