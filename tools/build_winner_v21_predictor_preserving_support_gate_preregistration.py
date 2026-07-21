#!/usr/bin/env python3
"""Freeze the unchanged support/context gate for Winner-v21 checkpoints."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v21_predictor_preserving_support_gate_preregistration.json"
MARKDOWN = ANALYSIS / "WINNER_V21_PREDICTOR_PRESERVING_SUPPORT_GATE_PREREGISTRATION_20260721.md"
TRAINING_RESULT = ANALYSIS / "winner_v21_predictor_preserving_training_result.json"
BASE_PREREGISTRATION = ANALYSIS / "winner_v12_full_calibrator_training_preregistration.json"
SOURCES = {
    "builder": Path("tools/build_winner_v21_predictor_preserving_support_gate_preregistration.py"),
    "gate_runner": Path("tools/run_winner_v21_predictor_preserving_support_gate.py"),
    "gate_tests": Path("tests/test_winner_v21_predictor_preserving_support_gate.py"),
    "preregistration_tests": Path("tests/test_winner_v21_predictor_preserving_support_gate_preregistration.py"),
    "result_importer": Path("tools/import_winner_v21_predictor_preserving_support_gate_result.py"),
    "result_importer_tests": Path("tests/test_winner_v21_predictor_preserving_support_gate_import.py"),
    "workflow": Path(".github/workflows/winner-v21-predictor-preserving-support-gate.yml"),
    "training_result": Path("outputs/analysis/winner_v21_predictor_preserving_training_result.json"),
    "training_preregistration": Path("outputs/analysis/winner_v21_predictor_preserving_training_preregistration.json"),
    "training_runner": Path("tools/run_winner_v21_predictor_preserving_training.py"),
    "training_importer": Path("tools/import_winner_v21_predictor_preserving_training.py"),
    "predictor_mechanics": Path("patches/winner_v21_predictor_preserving_joint_support.py"),
    "explicit_gradient_mechanics": Path("patches/winner_v21_predictor_preserving_joint_support_v2.py"),
    "joint_recurrent_mechanics": Path("patches/winner_v20_joint_recurrent_support.py"),
    "pitch_margin_patch": Path("patches/winner_v15_pitch_margin_support.py"),
    "environment_preparation": Path("tools/prepare_winner_v15_cpu_environment.py"),
    "base_gate_runner": Path("tools/run_winner_v12_calibrator_support_gate.py"),
    "calibrator_design_preregistration": Path("outputs/analysis/winner_v12_calibrator_training_preregistration.json"),
    "full_training_preregistration": Path("outputs/analysis/winner_v12_full_calibrator_training_preregistration.json"),
    "variable_configuration_domain": Path("outputs/analysis/winner_v3_variable_configuration_replacement_preregistration.json"),
    "cpu_smoke": Path("tools/run_winner_v12_calibrator_cpu_smoke.py"),
    "training_primitives": Path("patches/winner_v12_calibrator_training.py"),
    "deployable_network": Path("patches/winner_v12_decomposed_backend_networks.py"),
    "runtime_observer": Path("artifacts/runtime_handoff/rdkx5_native_20260719/observer/winner_v2_contract.py"),
    "canonical_p30_fit": Path("outputs/analysis/fixed_target_p30_actuator_fit_20260712.json"),
}


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
    if args.output.exists() or args.markdown.exists():
        raise FileExistsError("refusing to overwrite Winner-v21 support-gate contract")
    training = json.loads(TRAINING_RESULT.read_text(encoding="utf-8"))
    if (
        training.get("status")
        != "PASS_WINNER_V21_PREDICTOR_PRESERVING_TRAINING_ARTIFACT"
        or training.get("decision")
        != "AUTHORIZE_SEPARATE_UNCHANGED_SUPPORT_GATE_PREREGISTRATION_ONLY"
        or training.get("failed_checks") != []
        or training.get("execution", {}).get("formal_support_cells") != 0
        or training.get("predictor_scale") != 8.393629541414427e-11
    ):
        raise ValueError("Winner-v21 training does not authorize a gate")
    attribution = training.get("repository_attribution", {})
    if (
        attribution.get("repository") != "RobVanProd/open-duck-mini-rdkx5"
        or attribution.get("github_run_attempt") != 1
        or attribution.get("github_run_id", 0) <= 0
        or attribution.get("github_artifact_id", 0) <= 0
    ):
        raise ValueError("Winner-v21 training attribution changed")
    checkpoints = training.get("persistent_checkpoints", [])
    if [row.get("label") for row in checkpoints] != ["half", "final"]:
        raise ValueError("Winner-v21 checkpoints changed")
    base = json.loads(BASE_PREREGISTRATION.read_text(encoding="utf-8"))
    gate = base["future_frozen_support_gate"]
    if (
        gate.get("cells_per_checkpoint") != 124
        or gate.get("checkpoint_labels") != ["half", "final"]
        or gate.get("duration_ticks") != 250
        or gate.get("all_cells_at_both_checkpoints_must_pass") is not True
        or gate.get("selection_by_closest_result") is not False
    ):
        raise ValueError("reviewed support-gate definition changed")
    sources = {
        name: {
            "path": str(path).replace("\\", "/"),
            "hash_mode": "lf",
            "sha256": lf_sha256(ROOT / path),
        }
        for name, path in SOURCES.items()
    }
    payload = {
        "schema_version": "winner_v21.predictor_preserving_support_gate_preregistration.v1",
        "status": "PREREGISTERED_WINNER_V21_PREDICTOR_PRESERVING_SUPPORT_GATE",
        "decision": "AUTHORIZE_ONE_FROZEN_UNCHANGED_248_CELL_GATE_ONLY",
        "binding_change_only": (
            "The reviewed Winner-v12 evaluator, populations, thresholds, seeds, predictor "
            "comparison, and all-or-nothing half/final rule are unchanged. Only the verified "
            "Winner-v21 snapshot and graph paths are bound through a read-only in-memory alias."
        ),
        "training_artifact": {
            "repository_attribution": attribution,
            "source_stage1_snapshot": training["source_stage1_snapshot"],
            "predictor_scale": training["predictor_scale"],
            "half": {
                "snapshot": training["snapshot_manifest"][49],
                "graph": checkpoints[0]["graph"],
            },
            "final": {
                "snapshot": training["snapshot_manifest"][99],
                "graph": checkpoints[1]["graph"],
            },
        },
        "future_frozen_support_gate": gate,
        "execution_now": {
            "formal_support_cells": 0,
            "heldout_repeat_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "pass_rule": {
            "all_124_main_cells_at_both_checkpoints": True,
            "all_32_heldout_repeats_at_both_checkpoints": True,
            "all_16_heldout_contexts_separate_at_both_checkpoints": True,
            "learned_prediction_beats_constant_per_plant": True,
            "closest_checkpoint_selection": False,
        },
        "authority": {
            "robot_clearance": False,
            "response_conditioned_locomotion_training_authorized": False,
            "pass_authorizes_only": "a separate response-conditioned locomotion-training preregistration",
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
                "# Winner-v21 predictor-preserving support-gate preregistration",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                "- Population: `124` main cells per checkpoint; `248` total",
                "- Repeats: `32` heldout cells per checkpoint; `64` total",
                "- Predictor: learned MSE must beat constant per plant at both checkpoints",
                "- Selection: every check at both checkpoints; no closest result",
                "- Locomotion / robot access: `0 / 0`",
                "",
                "This is the unchanged reviewed support/context gate rebound to the",
                "independently imported Winner-v21 half/final artifacts.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
