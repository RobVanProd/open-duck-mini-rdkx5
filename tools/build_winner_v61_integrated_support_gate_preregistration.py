#!/usr/bin/env python3
"""Bind the unchanged reviewed 248-cell support gate to Winner-v60."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v61_integrated_support_gate_preregistration.json"
MARKDOWN = ANALYSIS / "WINNER_V61_INTEGRATED_SUPPORT_GATE_PREREGISTRATION_20260722.md"
TRAINING_RESULT = ANALYSIS / "winner_v60_integrated_numeric_guard_training_result.json"
TRAINING_RESULT_SHA256 = "50622331dea979369bdea7bb001cd168f94162270a0ea0ec1bdb4d6d9f6b8b57"
TRAINING_PREREGISTRATION = ANALYSIS / "winner_v60_integrated_numeric_guard_training_preregistration.json"
BASE_PREREGISTRATION = ANALYSIS / "winner_v12_full_calibrator_training_preregistration.json"
V53_RUNNER = ROOT / "tools/run_winner_v53_full_action_teacher_support_gate.py"

SOURCES = {
    "builder": Path("tools/build_winner_v61_integrated_support_gate_preregistration.py"),
    "gate_runner": Path("tools/run_winner_v61_integrated_support_gate.py"),
    "gate_tests": Path("tests/test_winner_v61_integrated_support_gate.py"),
    "training_result": Path(
        "outputs/analysis/winner_v60_integrated_numeric_guard_training_result.json"
    ),
    "training_preregistration": Path(
        "outputs/analysis/winner_v60_integrated_numeric_guard_training_preregistration.json"
    ),
    "training_runner": Path("tools/run_winner_v60_integrated_numeric_guard_training.py"),
    "v53_reviewed_gate_runner": Path(
        "tools/run_winner_v53_full_action_teacher_support_gate.py"
    ),
    "base_gate_preregistration": Path(
        "outputs/analysis/winner_v12_full_calibrator_training_preregistration.json"
    ),
    "base_gate_runner": Path("tools/run_winner_v12_calibrator_support_gate.py"),
    "calibrator_design": Path(
        "outputs/analysis/winner_v12_calibrator_training_preregistration.json"
    ),
    "variable_configuration_domain": Path(
        "outputs/analysis/winner_v3_variable_configuration_replacement_preregistration.json"
    ),
    "cpu_smoke": Path("tools/run_winner_v12_calibrator_cpu_smoke.py"),
    "normalized_checkpoint": Path("patches/winner_v22_normalized_predictor_v2.py"),
    "coordinate_adapter": Path("patches/winner_v22_normalized_support_gate.py"),
    "joint_recurrent": Path("patches/winner_v21_predictor_preserving_joint_support.py"),
    "runtime_observer": Path(
        "artifacts/runtime_handoff/rdkx5_native_20260719/observer/winner_v2_contract.py"
    ),
    "canonical_p30_fit": Path(
        "outputs/analysis/fixed_target_p30_actuator_fit_20260712.json"
    ),
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


def replace_exact(source: str, old: str, new: str, receipts: list[dict[str, Any]]) -> str:
    actual = source.count(old)
    if actual != 1:
        raise ValueError(
            f"Winner-v61 transform count changed: expected 1, found {actual}: {old!r}"
        )
    receipts.append(
        {
            "old_sha256": hashlib.sha256(old.encode()).hexdigest(),
            "new_sha256": hashlib.sha256(new.encode()).hexdigest(),
            "replacement_count": 1,
        }
    )
    return source.replace(old, new)


def transformed_source() -> tuple[str, list[dict[str, Any]]]:
    source = V53_RUNNER.read_text(encoding="utf-8")
    receipts: list[dict[str, Any]] = []

    def replace(old: str, new: str) -> None:
        nonlocal source
        source = replace_exact(source, old, new, receipts)

    for old, new in (
        ("winner_v53", "winner_v61"),
        ("Winner-v53", "Winner-v61"),
        ("WINNER_V53", "WINNER_V61"),
        ("winner_v52", "winner_v60"),
        ("Winner-v52", "Winner-v60"),
        ("WINNER_V52", "WINNER_V60"),
    ):
        actual = source.count(old)
        if actual <= 0:
            raise ValueError(f"Winner-v61 transform token absent: {old}")
        updated = source.replace(old, new)
        receipts.append(
            {
                "old_sha256": hashlib.sha256(old.encode()).hexdigest(),
                "new_sha256": hashlib.sha256(new.encode()).hexdigest(),
                "replacement_count": actual,
            }
        )
        source = updated
    replace(
        '"winner_v61_full_action_teacher_support_gate_preregistration.json"',
        '"winner_v61_integrated_support_gate_preregistration.json"',
    )
    replace(
        '"winner_v60_full_action_teacher_training_result.json"',
        '"winner_v60_integrated_numeric_guard_training_result.json"',
    )
    replace(
        '"winner_v60_full_action_teacher_training_preregistration.json"',
        '"winner_v60_integrated_numeric_guard_training_preregistration.json"',
    )
    replace("((\"half\", 403), (\"final\", 453))", "((\"half\", 504), (\"final\", 554))")
    replace("update not in {403, 453}", "update not in {504, 554}")
    replace(
        'metadata.get("source_completed_updates") != 353',
        'metadata.get("source_completed_updates") != 454',
    )
    replace(
        'expected_stage="full_action_static_target_teacher_joint_stage2"',
        'expected_stage="integrated_first_tick_teacher_joint_stage2"',
    )
    replace('mapping = {"half": 403, "final": 453}', 'mapping = {"half": 504, "final": 554}')
    replace(
        'f"snapshot_full_action_teacher_update_{update:03d}.npz"',
        'f"snapshot_integrated_first_tick_teacher_update_{update:03d}.npz"',
    )
    replace(
        '"winner_v61.full_action_teacher_support_gate_preregistration.v1"',
        '"winner_v61.integrated_support_gate_preregistration.v1"',
    )
    replace(
        '"PREREGISTERED_WINNER_V61_FULL_ACTION_TEACHER_SUPPORT_GATE"',
        '"PREREGISTERED_WINNER_V61_INTEGRATED_SUPPORT_GATE"',
    )
    if source.count("403") != 0 or source.count("453") != 4:
        raise ValueError("Winner-v61 remaining checkpoint literal count changed")
    source = source.replace("453", "554")
    receipts.append(
        {
            "old_sha256": hashlib.sha256(b"453").hexdigest(),
            "new_sha256": hashlib.sha256(b"554").hexdigest(),
            "replacement_count": 4,
        }
    )
    replace(
        '"winner_v61.full_action_teacher_support_gate_result.v1"',
        '"winner_v61.integrated_support_gate_result.v1"',
    )
    old_status = "WINNER_V61_FULL_ACTION_TEACHER_SUPPORT_GATE"
    new_status = "WINNER_V61_INTEGRATED_SUPPORT_GATE"
    if source.count(old_status) != 4:
        raise ValueError("Winner-v61 remaining status-token count changed")
    source = source.replace(old_status, new_status)
    receipts.append(
        {
            "old_sha256": hashlib.sha256(old_status.encode()).hexdigest(),
            "new_sha256": hashlib.sha256(new_status.encode()).hexdigest(),
            "replacement_count": 4,
        }
    )
    replace(
        '"PASS_WINNER_V60_FULL_ACTION_TEACHER_TRAINING_ARTIFACT"',
        '"PASS_WINNER_V60_INTEGRATED_FIRST_TICK_TEACHER_TRAINING_ARTIFACT"',
    )
    replace(
        '"AUTHORIZE_FULL_ACTION_TEACHER_SUPPORT_GATE_PREREGISTRATION_ONLY"',
        '"AUTHORIZE_INTEGRATED_FIRST_TICK_TEACHER_SUPPORT_GATE_PREREGISTRATION_ONLY"',
    )
    compile(source, "winner_v61_integrated_support_gate.py", "exec")
    return source, receipts


def checkpoint(training: dict[str, Any], label: str, update: int) -> dict[str, Any]:
    snapshot = next(
        row for row in training["snapshot_manifest"] if row["completed_updates"] == update
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
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite Winner-v61 contract: {path}")
    if sha256(TRAINING_RESULT) != TRAINING_RESULT_SHA256:
        raise ValueError("Winner-v61 training result changed")
    training = json.loads(TRAINING_RESULT.read_text(encoding="utf-8"))
    if (
        training.get("status")
        != "PASS_WINNER_V60_INTEGRATED_FIRST_TICK_TEACHER_TRAINING_ARTIFACT"
        or training.get("decision")
        != "AUTHORIZE_INTEGRATED_FIRST_TICK_TEACHER_SUPPORT_GATE_PREREGISTRATION_ONLY"
        or training.get("failed_checks") != []
        or training.get("execution", {}).get("optimizer_updates") != 100
        or training.get("execution", {}).get("formal_support_cells") != 0
        or training.get("authority", {}).get("robot_clearance") is not False
        or [row.get("completed_updates") for row in training["persistent_checkpoints"]]
        != [504, 554]
    ):
        raise ValueError("Winner-v60 does not authorize Winner-v61 preregistration")
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
    transformed, receipts = transformed_source()
    sources = {
        name: {
            "path": path.as_posix(),
            "hash_mode": "lf",
            "sha256": lf_sha256(ROOT / path),
        }
        for name, path in SOURCES.items()
    }
    payload = {
        "schema_version": "winner_v61.integrated_support_gate_preregistration.v1",
        "status": "PREREGISTERED_WINNER_V61_INTEGRATED_SUPPORT_GATE",
        "decision": "AUTHORIZE_ONE_FROZEN_WINNER_V61_248_CELL_GATE_ONLY",
        "causal_question": (
            "Does Winner-v60 preserve the complete inherited variable-configuration, "
            "plant, sensor, transport, context, and repeatability envelope at both "
            "persistence checkpoints?"
        ),
        "binding_change_only": (
            "The reviewed Winner-v12 evaluator, 248-cell population, 64 repeats, "
            "thresholds, seeds, P30/P31-34 plants, and all-or-nothing rule are unchanged. "
            "Only the exact Winner-v60 count-504/count-554 artifacts are bound read-only."
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
            "half": checkpoint(training, "half", 504),
            "final": checkpoint(training, "final", 554),
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
            "selected_update_if_pass": 554,
            "selection_basis": "fixed terminal endpoint after half/final persistence",
            "metric_ranking_or_closest_result": False,
            "no_selection_if_hold": True,
        },
        "transformation": {
            "base_v53_runner_lf_sha256": lf_sha256(V53_RUNNER),
            "transformed_source_sha256": hashlib.sha256(transformed.encode()).hexdigest(),
            "replacements": receipts,
            "replacement_groups": len(receipts),
        },
        "sources": sources,
        "source_manifest_sha256": canonical_sha256(sources),
        "authority": {
            "robot_clearance": False,
            "formal_support_gate_authorized": True,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "pass_authorizes_only": (
                "offline selection and asset freeze for separately authorized suspended Gate 5"
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
                "# Winner-v61 integrated support-gate preregistration",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                "- Population: `124` main cells per checkpoint; `248` total",
                "- Repeats: `32` heldout cells per checkpoint; `64` total",
                "- Checkpoints: exact Winner-v60 counts `504 / 554`",
                "- Pass: every check at both checkpoints; no closest result",
                "- Selection after pass: fixed final endpoint at count `554`",
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
