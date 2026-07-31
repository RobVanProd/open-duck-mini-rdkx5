#!/usr/bin/env python3
"""Bind the unchanged reviewed 248-cell support gate to Winner-v52."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v53_full_action_teacher_support_gate_preregistration.json"
MARKDOWN = ANALYSIS / "WINNER_V53_FULL_ACTION_TEACHER_SUPPORT_GATE_PREREGISTRATION_20260722.md"
TRAINING_RESULT = ANALYSIS / "winner_v52_full_action_teacher_training_result.json"
TRAINING_PREREGISTRATION = ANALYSIS / "winner_v52_full_action_teacher_training_preregistration.json"
BASE_PREREGISTRATION = ANALYSIS / "winner_v12_full_calibrator_training_preregistration.json"

SOURCES = {
    "builder": Path("tools/build_winner_v53_full_action_teacher_support_gate_preregistration.py"),
    "gate_runner": Path("tools/run_winner_v53_full_action_teacher_support_gate.py"),
    "gate_tests": Path("tests/test_winner_v53_full_action_teacher_support_gate.py"),
    "training_result": Path("outputs/analysis/winner_v52_full_action_teacher_training_result.json"),
    "training_preregistration": Path("outputs/analysis/winner_v52_full_action_teacher_training_preregistration.json"),
    "training_runner": Path("tools/run_winner_v52_full_action_teacher_training.py"),
    "base_gate_preregistration": Path("outputs/analysis/winner_v12_full_calibrator_training_preregistration.json"),
    "base_gate_runner": Path("tools/run_winner_v12_calibrator_support_gate.py"),
    "calibrator_design": Path("outputs/analysis/winner_v12_calibrator_training_preregistration.json"),
    "variable_configuration_domain": Path("outputs/analysis/winner_v3_variable_configuration_replacement_preregistration.json"),
    "cpu_smoke": Path("tools/run_winner_v12_calibrator_cpu_smoke.py"),
    "normalized_checkpoint": Path("patches/winner_v22_normalized_predictor_v2.py"),
    "coordinate_adapter": Path("patches/winner_v22_normalized_support_gate.py"),
    "joint_recurrent": Path("patches/winner_v21_predictor_preserving_joint_support.py"),
    "full_action_teacher": Path("patches/winner_v49_full_action_static_target_teacher.py"),
    "runtime_observer": Path("artifacts/runtime_handoff/rdkx5_native_20260719/observer/winner_v2_contract.py"),
    "canonical_p30_fit": Path("outputs/analysis/fixed_target_p30_actuator_fit_20260712.json"),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def checkpoint(training: dict[str, Any], label: str, update: int) -> dict[str, Any]:
    snapshot = next(
        row for row in training["snapshot_manifest"]
        if row["completed_updates"] == update
    )
    persistent = next(
        row for row in training["persistent_checkpoints"]
        if row["label"] == label and row["completed_updates"] == update
    )
    return {"snapshot": snapshot, "graph": persistent["graph"]}


def validate_training(training: dict[str, Any]) -> None:
    if (
        training.get("schema_version")
        != "winner_v52.full_action_teacher_training_result.v1"
        or training.get("status")
        != "PASS_WINNER_V52_FULL_ACTION_TEACHER_TRAINING_ARTIFACT"
        or training.get("decision")
        != "AUTHORIZE_FULL_ACTION_TEACHER_SUPPORT_GATE_PREREGISTRATION_ONLY"
        or training.get("failed_checks") != []
        or training.get("execution", {}).get("optimizer_updates") != 100
        or training.get("execution", {}).get("formal_support_cells") != 0
        or training.get("execution", {}).get("robot_or_rdk_access") != 0
        or training.get("authority", {}).get("robot_clearance") is not False
        or [row.get("label") for row in training.get("persistent_checkpoints", [])]
        != ["half", "final"]
        or [
            row.get("completed_updates")
            for row in training.get("persistent_checkpoints", [])
        ]
        != [403, 453]
    ):
        raise ValueError("Winner-v52 does not authorize Winner-v53 preregistration")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite Winner-v53 contract: {path}")

    training = json.loads(TRAINING_RESULT.read_text(encoding="utf-8"))
    validate_training(training)
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
            "path": path.as_posix(),
            "hash_mode": "lf",
            "sha256": lf_sha256(ROOT / path),
        }
        for name, path in SOURCES.items()
    }
    payload = {
        "schema_version": "winner_v53.full_action_teacher_support_gate_preregistration.v1",
        "status": "PREREGISTERED_WINNER_V53_FULL_ACTION_TEACHER_SUPPORT_GATE",
        "decision": "AUTHORIZE_ONE_FROZEN_WINNER_V53_248_CELL_GATE_ONLY",
        "causal_question": (
            "Does the V52 full-14D teacher continuation preserve the complete inherited "
            "variable-configuration, plant, sensor, transport, context, and repeatability "
            "envelope at both persistence checkpoints?"
        ),
        "binding_change_only": (
            "The reviewed Winner-v12 evaluator, 248-cell population, 64 repeats, thresholds, "
            "seeds, P30/P31-34 plants, and all-or-nothing rule are unchanged. Only the exact "
            "Winner-v52 count-403/count-453 snapshots and graphs are bound read-only."
        ),
        "training_artifact": {
            "result": {
                "path": TRAINING_RESULT.relative_to(ROOT).as_posix(),
                "bytes": TRAINING_RESULT.stat().st_size,
                "sha256": sha256(TRAINING_RESULT),
            },
            "source_snapshot": training["source_snapshot"],
            "source_graph": training["source_graph"],
            "teacher_snapshot": training["teacher_snapshot"],
            "objective": training["objective"],
            "half": checkpoint(training, "half", 403),
            "final": checkpoint(training, "final", 453),
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
        "selection_rule": {
            "selected_only_if_every_pass_rule_is_true_at_both_checkpoints": True,
            "selected_checkpoint_if_pass": "final",
            "selected_update_if_pass": 453,
            "selection_basis": "fixed terminal endpoint after half/final persistence",
            "metric_ranking_or_closest_result": False,
            "no_selection_if_hold": True,
        },
        "sources": sources,
        "source_manifest_sha256": canonical_sha256(sources),
        "authority": {
            "robot_clearance": False,
            "formal_support_gate_authorized": True,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "pass_authorizes_only": (
                "offline selection and asset freeze for a separately authorized suspended Gate 5"
            ),
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown.write_text(
        "\n".join(
            [
                "# Winner-v53 full-action-teacher support-gate preregistration",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                "- Population: `124` main cells per checkpoint; `248` total",
                "- Repeats: `32` heldout cells per checkpoint; `64` total",
                "- Checkpoints: exact Winner-v52 count `403 / 453`",
                "- Pass: every check at both checkpoints; no closest result",
                "- Selection after pass: fixed final endpoint at count `453`",
                "- Locomotion / robot access in this gate: `0 / 0`",
                "",
                "A hold selects no checkpoint. A pass selects the final endpoint by the",
                "predeclared persistence rule, not by post-hoc metric ranking.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
