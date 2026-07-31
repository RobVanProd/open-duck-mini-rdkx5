#!/usr/bin/env python3
"""Freeze the unchanged reviewed support gate for Winner-v32 half/final."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v33_prefix_right_pitch_anchor_support_gate_preregistration.json"
MARKDOWN = ANALYSIS / "WINNER_V33_PREFIX_RIGHT_PITCH_ANCHOR_SUPPORT_GATE_PREREGISTRATION_20260722.md"
TRAINING_RESULT = ANALYSIS / "winner_v32_prefix_right_pitch_anchor_training_result.json"
BASE_PREREGISTRATION = ANALYSIS / "winner_v12_full_calibrator_training_preregistration.json"
SOURCES = {
    "builder": Path("tools/build_winner_v33_prefix_right_pitch_anchor_support_gate_preregistration.py"),
    "gate_runner": Path("tools/run_winner_v33_prefix_right_pitch_anchor_support_gate.py"),
    "gate_tests": Path("tests/test_winner_v33_prefix_right_pitch_anchor_support_gate.py"),
    "preregistration_tests": Path("tests/test_winner_v33_prefix_right_pitch_anchor_support_gate_preregistration.py"),
    "result_importer": Path("tools/import_winner_v33_prefix_right_pitch_anchor_support_gate_result.py"),
    "result_importer_tests": Path("tests/test_winner_v33_prefix_right_pitch_anchor_support_gate_import.py"),
    "reviewed_result_importer": Path("tools/import_winner_v15_pitch_margin_support_gate_result.py"),
    "workflow": Path(".github/workflows/winner-v33-prefix-right-pitch-anchor-support-gate.yml"),
    "training_result": Path("outputs/analysis/winner_v32_prefix_right_pitch_anchor_training_result.json"),
    "training_preregistration": Path("outputs/analysis/winner_v32_prefix_right_pitch_anchor_training_preregistration.json"),
    "training_runner": Path("tools/run_winner_v32_prefix_right_pitch_anchor_training.py"),
    "training_importer": Path("tools/import_winner_v32_prefix_right_pitch_anchor_training.py"),
    "anchor_mechanics": Path("patches/winner_v29_prefix_right_pitch_anchor.py"),
    "objective_mechanics": Path("patches/winner_v24_symmetric_support_failure_v3.py"),
    "baseline_anchored_mechanics": Path("patches/winner_v24_symmetric_support_failure_v2.py"),
    "explicit_gradient_mechanics": Path("patches/winner_v22_normalized_predictor_v2.py"),
    "coordinate_adapter": Path("patches/winner_v22_normalized_support_gate.py"),
    "coordinate_adapter_tests": Path("tests/test_winner_v22_normalized_support_gate.py"),
    "joint_recurrent_mechanics": Path("patches/winner_v21_predictor_preserving_joint_support.py"),
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


def _checkpoint(training: dict[str, Any], label: str, update: int) -> dict[str, Any]:
    snapshot = next(
        row
        for row in training["snapshot_manifest"]
        if row["completed_updates"] == update
    )
    persistent = next(
        row
        for row in training["persistent_checkpoints"]
        if row["label"] == label and row["completed_updates"] == update
    )
    return {"snapshot": snapshot, "graph": persistent["graph"]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    if args.output.exists() or args.markdown.exists():
        raise FileExistsError("refusing to overwrite Winner-v33 support-gate contract")
    training = json.loads(TRAINING_RESULT.read_text(encoding="utf-8"))
    if (
        training.get("status")
        != "PASS_WINNER_V32_PREFIX_RIGHT_PITCH_ANCHOR_TRAINING_ARTIFACT"
        or training.get("decision")
        != "AUTHORIZE_SEPARATE_PREFIX_RIGHT_PITCH_ANCHOR_SUPPORT_GATE_PREREGISTRATION_ONLY"
        or training.get("failed_checks") != []
        or training.get("execution", {}).get("formal_support_cells") != 0
        or training.get("execution", {}).get("optimizer_updates") != 100
        or training.get("authority", {}).get("robot_clearance") is not False
    ):
        raise ValueError("Winner-v32 training does not authorize a gate")
    attribution = training.get("repository_attribution", {})
    if (
        attribution.get("repository") != "RobVanProd/open-duck-mini-rdkx5"
        or attribution.get("github_run_attempt") != 1
        or attribution.get("github_run_id", 0) <= 0
        or attribution.get("github_artifact_id", 0) <= 0
    ):
        raise ValueError("Winner-v32 training attribution changed")
    checkpoints = training.get("persistent_checkpoints", [])
    if [row.get("label") for row in checkpoints] != ["half", "final"]:
        raise ValueError("Winner-v32 checkpoints changed")
    if [row.get("completed_updates") for row in checkpoints] != [251, 301]:
        raise ValueError("Winner-v32 checkpoint update identities changed")
    base = json.loads(BASE_PREREGISTRATION.read_text(encoding="utf-8"))
    gate = json.loads(json.dumps(base["future_frozen_support_gate"]))
    if (
        gate.get("cells_per_checkpoint") != 124
        or gate.get("checkpoint_labels") != ["half", "final"]
        or gate.get("duration_ticks") != 250
        or gate.get("all_cells_at_both_checkpoints_must_pass") is not True
        or gate.get("selection_by_closest_result") is not False
    ):
        raise ValueError("reviewed support-gate definition changed")
    gate["predictor_scoring"] = {
        "head_output_coordinates": "normalized",
        "evaluated_coordinates": "raw through exact in-memory affine projection",
        "learned_error": "mean(square((prediction_raw - target_raw) / target_std))",
        "constant_error": "mean(square((target_mean - target_raw) / target_std))",
        "projection": {
            "auxiliary_hidden_weight": "normalized_weight * target_std",
            "auxiliary_action_weight": "normalized_weight * target_std",
            "auxiliary_bias": "normalized_bias * target_std + target_mean",
        },
        "physical_support_population_thresholds_seeds_unchanged": True,
        "checkpoint_and_onnx_bytes_unchanged": True,
    }
    sources = {
        name: {
            "path": str(path).replace("\\", "/"),
            "hash_mode": "lf",
            "sha256": lf_sha256(ROOT / path),
        }
        for name, path in SOURCES.items()
    }
    payload = {
        "schema_version": "winner_v33.prefix_right_pitch_anchor_support_gate_preregistration.v1",
        "status": "PREREGISTERED_WINNER_V33_PREFIX_RIGHT_PITCH_ANCHOR_SUPPORT_GATE",
        "decision": "AUTHORIZE_ONE_FROZEN_WINNER_V33_248_CELL_GATE_ONLY",
        "binding_change_only": (
            "The reviewed Winner-v12 physical evaluator, populations, thresholds, "
            "seeds, constant baseline, and all-or-nothing half/final rule are unchanged. "
            "The verified Winner-v32 count-251/count-301 paths are bound read-only and "
            "their normalized auxiliary head is projected exactly into raw scoring coordinates."
        ),
        "training_artifact": {
            "repository_attribution": attribution,
            "source_snapshot": training["source_snapshot"],
            "teacher_snapshot": training["teacher_snapshot"],
            "objective": training["objective"],
            "half": _checkpoint(training, "half", 251),
            "final": _checkpoint(training, "final", 301),
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
            "pass_authorizes_only": (
                "a separate response-conditioned locomotion-training preregistration"
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
                "# Winner-v33 prefix right-pitch anchor support-gate preregistration",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                "- Population: `124` main cells per checkpoint; `248` total",
                "- Repeats: `32` heldout cells per checkpoint; `64` total",
                "- Checkpoints: exact Winner-v32 count `251 / 301`",
                "- Selection: every check at both checkpoints; no closest result",
                "- Locomotion / robot access: `0 / 0`",
                "",
                "This binds only the frozen training artifacts to the unchanged reviewed",
                "support evaluator. It is not robot clearance.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
