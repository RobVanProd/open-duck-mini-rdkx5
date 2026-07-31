#!/usr/bin/env python3
"""Preregister one CPU-only bilateral pitch-chain action-direction diagnostic."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v16_support_action_direction_diagnostic_preregistration.json"
MARKDOWN = ANALYSIS / "WINNER_V16_SUPPORT_ACTION_DIRECTION_DIAGNOSTIC_PREREGISTRATION_20260721.md"
TRAINING_RESULT = ANALYSIS / "winner_v15_pitch_margin_support_training_result.json"
FORMAL_RESULT = ANALYSIS / "winner_v15_pitch_margin_support_gate_result.json"
HOLD_ATTRIBUTION = ANALYSIS / "winner_v15_pitch_margin_support_hold_attribution.json"
RUNNER = ROOT / "tools/run_winner_v16_support_action_direction_diagnostic.py"
SOURCES = {
    "builder": Path("tools/build_winner_v16_support_action_direction_diagnostic_preregistration.py"),
    "runner": Path("tools/run_winner_v16_support_action_direction_diagnostic.py"),
    "intervention": Path("patches/winner_v16_support_action_direction.py"),
    "intervention_tests": Path("tests/test_winner_v16_support_action_direction.py"),
    "runner_tests": Path("tests/test_winner_v16_support_action_direction_diagnostic.py"),
    "preregistration_tests": Path("tests/test_winner_v16_support_action_direction_diagnostic_preregistration.py"),
    "workflow": Path(".github/workflows/winner-v16-support-action-direction-diagnostic.yml"),
    "hold_attribution": Path("outputs/analysis/winner_v15_pitch_margin_support_hold_attribution.json"),
    "formal_gate_result": Path("outputs/analysis/winner_v15_pitch_margin_support_gate_result.json"),
    "training_result": Path("outputs/analysis/winner_v15_pitch_margin_support_training_result.json"),
    "v14_diagnostic_runner": Path("tools/run_winner_v14_support_action_diagnostic.py"),
    "v14_transform": Path("patches/winner_v14_support_action_diagnostic.py"),
    "v15_gate_adapter": Path("tools/run_winner_v15_pitch_margin_support_gate.py"),
    "environment_preparation": Path("tools/prepare_winner_v15_cpu_environment.py"),
    "base_gate_runner": Path("tools/run_winner_v12_calibrator_support_gate.py"),
    "calibrator_design_preregistration": Path("outputs/analysis/winner_v12_calibrator_training_preregistration.json"),
    "variable_configuration_domain": Path("outputs/analysis/winner_v3_variable_configuration_replacement_preregistration.json"),
    "normalized_training": Path("patches/winner_v13_normalized_calibrator_training.py"),
    "deployable_network": Path("patches/winner_v12_decomposed_backend_networks.py"),
}


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def load_runner() -> Any:
    spec = importlib.util.spec_from_file_location("winner_v16_direction_runner", RUNNER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load Winner-v16 direction runner")
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
            raise FileExistsError(f"refusing to overwrite direction preregistration: {path}")
    training = json.loads(TRAINING_RESULT.read_text(encoding="utf-8"))
    formal = json.loads(FORMAL_RESULT.read_text(encoding="utf-8"))
    attribution = json.loads(HOLD_ATTRIBUTION.read_text(encoding="utf-8"))
    if (
        training.get("status") != "PASS_WINNER_V15_PITCH_MARGIN_SUPPORT_TRAINING_ARTIFACT"
        or training.get("failed_checks") != []
        or formal.get("status") != "HOLD_WINNER_V15_PITCH_MARGIN_SUPPORT_GATE"
        or formal.get("failed_checks") != ["all_248_main_cells_pass"]
        or attribution.get("status") != "PASS_WINNER_V15_PITCH_MARGIN_SUPPORT_HOLD_ATTRIBUTION"
        or attribution.get("decision") != "CLOSE_PITCH_MARGIN_OBJECTIVE_PREREGISTER_ACTION_DIRECTION_DIAGNOSTIC"
    ):
        raise ValueError("Winner-v16 source decision changed")
    repository = training.get("repository_attribution", {})
    if repository.get("repository") != "RobVanProd/open-duck-mini-rdkx5" or repository.get("github_run_attempt") != 1:
        raise ValueError("Winner-v16 training artifact attribution changed")
    runner = load_runner()
    interventions = [dict(row) for row in runner.INTERVENTIONS]
    if len(interventions) != 7 or interventions[0]["id"] != "BASELINE":
        raise ValueError("Winner-v16 intervention population changed")
    sources = {
        name: {"path": str(path).replace("\\", "/"), "hash_mode": "lf", "sha256": lf_sha256(ROOT / path)}
        for name, path in SOURCES.items()
    }
    payload = {
        "schema_version": "winner_v16.support_action_direction_diagnostic_preregistration.v1",
        "status": "PREREGISTERED_WINNER_V16_SUPPORT_ACTION_DIRECTION_DIAGNOSTIC",
        "decision": "AUTHORIZE_ONE_CPU_ONLY_BILATERAL_PITCH_CHAIN_DIRECTION_DIAGNOSTIC",
        "hypothesis": (
            "A bounded 0.03-rad bilateral pitch-chain target offset can identify whether a single sagittal support axis has the sign needed to arrest the persistent negative-X backward-pitch exits."
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
        "intervention_semantics": {
            "hip_pitch_magnitude": "left-negative/right-positive home-magnitude parity",
            "knee": "same-sign bilateral logical-coordinate offset",
            "ankle": "same-sign bilateral logical-coordinate offset",
            "application": "add to source action each tick, then reapply exact absolute and per-tick graph bounds",
        },
        "validity_rule": (
            "The zero-offset baseline must reproduce all 24 source formal cells exactly; all 168 cells must preserve exact intervention math, action bounds, source previous-action output, finite values, and zero optimizer/robot access."
        ),
        "advancement_rule": (
            "Only an intervention passing all 12 fixed cells at both checkpoints can advance to a separate CPU contract. If several pass, choose by minimum maximum action deviation, then minimum mean-squared deviation, then frozen intervention order. No closest failing result advances."
        ),
        "training_artifact": {
            "repository_attribution": repository,
            "half": {"snapshot": training["snapshot_manifest"][49], "graph": training["persistent_checkpoints"][0]["graph"]},
            "final": {"snapshot": training["snapshot_manifest"][99], "graph": training["persistent_checkpoints"][1]["graph"]},
        },
        "execution_now": {"optimizer_updates": 0, "diagnostic_cells": 0, "locomotion_steps": 0, "robot_or_rdk_access": 0},
        "authority": {
            "robot_clearance": False,
            "response_conditioned_locomotion_training_authorized": False,
            "pass_authorizes_only": "a separate CPU-only selected-direction contract preregistration",
        },
        "sources": sources,
        "source_manifest_sha256": canonical_sha256(sources),
    }
    args.output.write_text(json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.markdown.write_text("\n".join([
        "# Winner-v16 support action-direction diagnostic preregistration", "",
        f"- Status: `{payload['status']}`", f"- Decision: `{payload['decision']}`",
        "- Interventions: baseline plus ± bilateral hip-pitch magnitude, knee, and ankle",
        "- Offset: `0.03 rad` target / `0.12` normalized action",
        "- Population: `168` CPU-only diagnostic cells", "- Optimizer / locomotion / robot: `0 / 0 / 0`", "",
        "The baseline must reproduce all 24 fixed formal cells exactly. Only a direction",
        "that passes all 12 cells at both checkpoints can advance; no closest failure advances.", "",
    ]), encoding="utf-8")
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
