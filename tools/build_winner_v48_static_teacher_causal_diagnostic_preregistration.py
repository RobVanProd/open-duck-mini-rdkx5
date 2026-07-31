#!/usr/bin/env python3
"""Freeze the read-only Winner-v48 teacher/action causal diagnostic."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v48_static_teacher_causal_diagnostic_preregistration.json"
MARKDOWN = (
    ANALYSIS
    / "WINNER_V48_STATIC_TEACHER_CAUSAL_DIAGNOSTIC_PREREGISTRATION_20260722.md"
)
V47B_RESULT = (
    ANALYSIS / "winner_v47b_support_gate_execution_correction_result.json"
)
V42_RESULT = ANALYSIS / "winner_v42_static_target_teacher_table_result.json"
EXPECTED_CONFIGURATION_IDS = [
    "COM_CORNER_00",
    "COM_CORNER_01",
    "COM_CORNER_02",
    "COM_CORNER_03",
    "COM_X_NEG",
    "DISCOVERY_03",
    "HELDOUT_04",
    "HELDOUT_09",
]
EXPECTED_FAILED_PAIR_COUNT = 28
ARMS = ("graph", "full_teacher", "pitch_teacher", "nonpitch_zero")
SOURCES = {
    "builder": Path(
        "tools/build_winner_v48_static_teacher_causal_diagnostic_preregistration.py"
    ),
    "runner": Path("tools/run_winner_v48_static_teacher_causal_diagnostic.py"),
    "tests": Path("tests/test_winner_v48_static_teacher_causal_diagnostic.py"),
    "v47b_result": Path(
        "outputs/analysis/winner_v47b_support_gate_execution_correction_result.json"
    ),
    "v47_runner": Path(
        "tools/run_winner_v47_static_target_teacher_support_gate.py"
    ),
    "base_gate_runner": Path("tools/run_winner_v12_calibrator_support_gate.py"),
    "full_training_preregistration": Path(
        "outputs/analysis/winner_v12_full_calibrator_training_preregistration.json"
    ),
    "calibrator_design_preregistration": Path(
        "outputs/analysis/winner_v12_calibrator_training_preregistration.json"
    ),
    "v46_training_result": Path(
        "outputs/analysis/winner_v46_static_target_teacher_training_result.json"
    ),
    "v46_training_preregistration": Path(
        "outputs/analysis/winner_v46_static_target_teacher_training_preregistration.json"
    ),
    "v42_teacher_table": Path(
        "outputs/analysis/winner_v42_static_target_teacher_table_result.json"
    ),
    "v43_teacher_implementation": Path(
        "patches/winner_v43_static_target_teacher.py"
    ),
    "variable_configuration_domain": Path(
        "outputs/analysis/winner_v3_variable_configuration_replacement_preregistration.json"
    ),
    "training_primitives": Path("patches/winner_v12_calibrator_training.py"),
    "runtime_observer": Path(
        "artifacts/runtime_handoff/rdkx5_native_20260719/observer/winner_v2_contract.py"
    ),
    "canonical_p30_fit": Path(
        "outputs/analysis/fixed_target_p30_actuator_fit_20260712.json"
    ),
}


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def failed_cells(result: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "checkpoint": checkpoint["label"],
            "configuration_id": cell["configuration_id"],
            "plant": cell["plant"],
            "terminal_tick": cell["terminal"]["tick"],
        }
        for checkpoint in result["checkpoint_results"]
        for cell in checkpoint["core_model_plant_cells"]
        if cell["support_pass"] is False
    ]


def validate_v47b_hold(result: Mapping[str, Any]) -> None:
    failures = failed_cells(result)
    counts = {
        label: sum(row["checkpoint"] == label for row in failures)
        for label in ("half", "final")
    }
    configuration_ids = sorted({row["configuration_id"] for row in failures})
    failure_cells = [
        cell
        for checkpoint in result.get("checkpoint_results", [])
        for cell in checkpoint.get("core_model_plant_cells", [])
        if cell.get("support_pass") is False
    ]
    expected_true_checks = {
        "base_z",
        "both_contacts",
        "current",
        "finite",
        "overcurrent_streak",
        "torque",
    }
    if (
        result.get("schema_version")
        != "winner_v47b.support_gate_execution_correction_result.v1"
        or result.get("status")
        != "HOLD_WINNER_V47B_SUPPORT_GATE_EXECUTION_CORRECTION"
        or result.get("decision") != "DO_NOT_TRAIN_RESPONSE_CONDITIONED_LOCOMOTION"
        or result.get("execution")
        != {
            "formal_support_cells": 248,
            "heldout_repeat_cells": 64,
            "locomotion_training_steps": 0,
            "robot_or_rdk_access": 0,
        }
        or counts != {"half": 16, "final": 12}
        or len(failures) != EXPECTED_FAILED_PAIR_COUNT
        or configuration_ids != EXPECTED_CONFIGURATION_IDS
        or result.get("authority", {}).get("robot_clearance") is not False
        or any(
            cell.get("terminal", {}).get("checks", {}).get("roll_pitch") is not False
            or {
                name
                for name, passed in cell.get("terminal", {}).get("checks", {}).items()
                if passed is True
            }
            != expected_true_checks
            for cell in failure_cells
        )
    ):
        raise ValueError("Winner-v47b HOLD evidence changed")


def validate_teacher_table(result: Mapping[str, Any]) -> None:
    table = result.get("teacher_table")
    if (
        result.get("schema_version")
        != "winner_v42.static_target_teacher_table_result.v1"
        or result.get("status") != "PASS_WINNER_V42_STATIC_TARGET_TEACHER_TABLE"
        or result.get("decision")
        != "AUTHORIZE_STATIC_TARGET_TEACHER_ABI_CPU_CONTRACT_ONLY"
        or not isinstance(table, Mapping)
        or any(
            configuration_id not in table
            or table[configuration_id].get("shared_support_pass") is not True
            for configuration_id in EXPECTED_CONFIGURATION_IDS
        )
    ):
        raise ValueError("Winner-v42 teacher evidence changed")


def source_manifest() -> dict[str, dict[str, str]]:
    return {
        name: {
            "path": path.as_posix(),
            "hash_mode": "lf",
            "sha256": lf_sha256(ROOT / path),
        }
        for name, path in SOURCES.items()
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite Winner-v48 contract: {path}")

    v47b = json.loads(V47B_RESULT.read_text(encoding="utf-8"))
    teacher = json.loads(V42_RESULT.read_text(encoding="utf-8"))
    validate_v47b_hold(v47b)
    validate_teacher_table(teacher)
    sources = source_manifest()
    payload = {
        "schema_version": "winner_v48.static_teacher_causal_diagnostic_preregistration.v1",
        "status": "PREREGISTERED_WINNER_V48_STATIC_TEACHER_CAUSAL_DIAGNOSTIC",
        "decision": "AUTHORIZE_ONE_READ_ONLY_CPU_CAUSAL_DIAGNOSTIC",
        "question": (
            "Does the exact Winner-v42 full static teacher still stabilize every "
            "Winner-v47b failure, and is each failure rescued by replacing only the "
            "six pitch-chain outputs or only the eight unsupervised non-pitch outputs?"
        ),
        "frozen_population": {
            "checkpoint_labels": ["half", "final"],
            "plants": ["P30_ALL_JOINT", "P31_34_PITCH_WITH_P30_NONPITCH"],
            "configuration_ids": EXPECTED_CONFIGURATION_IDS,
            "duration_ticks": 250,
            "formal_failed_pairs": EXPECTED_FAILED_PAIR_COUNT,
            "arms": list(ARMS),
            "cells_per_arm": 32,
            "total_cells": 128,
        },
        "interventions": {
            "graph": "unchanged checkpoint ONNX action and state chain",
            "full_teacher": (
                "replace all 14 outputs with the exact Winner-v42 raw static target, "
                "then apply the unchanged graph boundary relative to the actually "
                "applied previous action"
            ),
            "pitch_teacher": (
                "replace only action indices [2,3,4,11,12,13] with the exact teacher; "
                "retain graph outputs elsewhere; reapply the unchanged graph boundary"
            ),
            "nonpitch_zero": (
                "retain graph pitch-chain outputs; drive the other eight outputs toward "
                "exact zero through the unchanged graph boundary"
            ),
            "state_semantics": (
                "retain the graph h_out; h_out is action-independent by the frozen "
                "response-step equation; feed the actually applied intervention action "
                "as previous_action on the next tick"
            ),
        },
        "validity_rules": {
            "all_32_graph_cells_bit_exact_to_imported_v47b": True,
            "all_128_cells_previous_action_chain_exact": True,
            "all_128_cells_jax_onnx_hidden_error_at_most_1e_7": True,
            "exact_cell_counts": True,
            "no_stochastic_sensor_or_transport_condition": True,
        },
        "classification_rules": {
            "teacher_insufficient": "full_teacher fails",
            "pitch_output_causal": "full_teacher and pitch_teacher pass; nonpitch_zero fails",
            "nonpitch_output_causal": "full_teacher and nonpitch_zero pass; pitch_teacher fails",
            "either_single_intervention_rescues": (
                "full_teacher, pitch_teacher, and nonpitch_zero all pass"
            ),
            "pitch_nonpitch_interaction": (
                "full_teacher passes while both single interventions fail"
            ),
            "population": "the 28 imported graph-failing checkpoint/configuration/plant pairs only",
        },
        "action_alignment_report": {
            "reference": (
                "the exact teacher target graph-bounded independently at every tick "
                "relative to the graph arm's previous action"
            ),
            "subsets": {
                "pitch": [2, 3, 4, 11, 12, 13],
                "nonpitch": [0, 1, 5, 6, 7, 8, 9, 10],
            },
            "metrics": ["mean_abs", "rms", "maximum_abs", "per_tick_rms_and_maximum_abs"],
            "threshold_or_closest_selection": False,
        },
        "interpretation": {
            "full_teacher_all_pass": (
                "the table remains sufficient and the learned action mapping, not hidden "
                "configuration observability, is the selected problem class"
            ),
            "any_full_teacher_failure": "close the static-teacher route",
            "result_authorizes_only": (
                "a separate prospective mechanism preregistration selected from the "
                "frozen causal classifications"
            ),
        },
        "execution_now": {
            "diagnostic_cells": 0,
            "optimizer_updates": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "robot_clearance": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "pass_authorizes_only": (
                "one offline CPU diagnostic and a later separately reviewed preregistration"
            ),
        },
        "sources": sources,
        "source_manifest_sha256": canonical_sha256(sources),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown.write_text(
        "\n".join(
            [
                "# Winner-v48 static-teacher causal diagnostic preregistration",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                "- Frozen graph failures: `28` across `8` configurations",
                "- Arms / total CPU cells: `4 / 128`",
                "- Optimizer / locomotion / robot: `0 / 0 / 0`",
                "",
                "This is a read-only factorial intervention. It cannot select a",
                "checkpoint, tune a threshold, train locomotion, or clear the robot.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
