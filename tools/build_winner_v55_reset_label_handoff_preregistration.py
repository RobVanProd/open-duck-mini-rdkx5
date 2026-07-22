#!/usr/bin/env python3
"""Preregister one reset-label collision and delayed-teacher handoff audit."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v55_reset_label_handoff_preregistration.json"
MARKDOWN = ANALYSIS / "WINNER_V55_RESET_LABEL_HANDOFF_PREREGISTRATION_20260722.md"
V54_RESULT = ANALYSIS / "winner_v54_residual_teacher_causal_result.json"
V54_RESULT_SHA256 = "74d2e7f2e8009eedd0c425aff575b136ef0cac5e1cd233072915c6f2a3de2680"
V42_RESULT = ANALYSIS / "winner_v42_static_target_teacher_table_result.json"
V42_RESULT_SHA256 = "ff1f12d556661548df272ef4b5a6c5f69bd614d2e54d3d7e17654be6de9ebc1c"

TEACHER_CONFIGURATION_IDS = [
    "COM_CORNER_00",
    "COM_CORNER_01",
    "COM_CORNER_02",
    "COM_CORNER_03",
    "COM_X_NEG",
    "DISCOVERY_02",
    "DISCOVERY_03",
    "DISCOVERY_06",
    "DISCOVERY_09",
    "DISCOVERY_10",
    "HELDOUT_04",
    "HELDOUT_07",
    "HELDOUT_09",
    "HELDOUT_15",
    "OPTIONAL_AGGREGATE_HEAVY_AFT",
]
FAILURE_CONFIGURATION_IDS = [
    "COM_X_NEG",
    "COM_CORNER_01",
    "COM_CORNER_03",
    "DISCOVERY_03",
    "HELDOUT_04",
    "HELDOUT_09",
]
PLANTS = ["P30_ALL_JOINT", "P31_34_PITCH_WITH_P30_NONPITCH"]
HANDOFF_TICKS = [0, 1, 2, 4, 8, 12, 16, 20, 250]

SOURCES = {
    "builder": Path("tools/build_winner_v55_reset_label_handoff_preregistration.py"),
    "runner": Path("tools/run_winner_v55_reset_label_handoff.py"),
    "tests": Path("tests/test_winner_v55_reset_label_handoff.py"),
    "v54_result": Path("outputs/analysis/winner_v54_residual_teacher_causal_result.json"),
    "v54_preregistration": Path("outputs/analysis/winner_v54_residual_teacher_causal_preregistration.json"),
    "v54_runner": Path("tools/run_winner_v54_residual_teacher_causal.py"),
    "v53_result": Path("outputs/analysis/winner_v53_full_action_teacher_support_gate_result.json"),
    "v52_result": Path("outputs/analysis/winner_v52_full_action_teacher_training_result.json"),
    "teacher_table": Path("outputs/analysis/winner_v42_static_target_teacher_table_result.json"),
    "teacher_loader": Path("patches/winner_v43_static_target_teacher.py"),
    "base_gate_runner": Path("tools/run_winner_v12_calibrator_support_gate.py"),
    "base_smoke_runner": Path("tools/run_winner_v12_calibrator_cpu_smoke.py"),
    "base_gate_preregistration": Path("outputs/analysis/winner_v12_full_calibrator_training_preregistration.json"),
    "variable_configuration_domain": Path("outputs/analysis/winner_v3_variable_configuration_replacement_preregistration.json"),
    "response_use_evidence": Path("outputs/analysis/winner_v23_negative_x_response_use_diagnostic_result.json"),
    "early_prefix_evidence": Path("outputs/analysis/winner_v27_early_prefix_recovery_scan_result.json"),
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite Winner-v55 contract: {path}")

    v54 = json.loads(V54_RESULT.read_text(encoding="utf-8"))
    v42 = json.loads(V42_RESULT.read_text(encoding="utf-8"))
    if (
        sha256(V54_RESULT) != V54_RESULT_SHA256
        or v54.get("status")
        != "PASS_WINNER_V54_RESIDUAL_TEACHER_CAUSAL_DIAGNOSTIC"
        or v54.get("findings", {}).get("support_pass_counts")
        != {"full_teacher": 12, "graph": 0, "nonpitch_zero": 0, "pitch_teacher": 11}
        or v54.get("authority", {}).get("robot_clearance") is not False
    ):
        raise ValueError("Winner-v54 causal source changed")
    if (
        sha256(V42_RESULT) != V42_RESULT_SHA256
        or v42.get("status") != "PASS_WINNER_V42_STATIC_TARGET_TEACHER_TABLE"
        or list(v42.get("teacher_table", {})) != TEACHER_CONFIGURATION_IDS
        or v42.get("summary", {}).get("configuration_pass_count") != 15
    ):
        raise ValueError("Winner-v42 teacher-table source changed")

    sources = {
        name: {
            "path": path.as_posix(),
            "hash_mode": "lf",
            "sha256": lf_sha256(ROOT / path),
        }
        for name, path in SOURCES.items()
    }
    value = {
        "schema_version": "winner_v55.reset_label_handoff_preregistration.v1",
        "status": "PREREGISTERED_WINNER_V55_RESET_LABEL_HANDOFF_DIAGNOSTIC",
        "decision": "AUTHORIZE_ONE_READ_ONLY_RESET_AND_108_CELL_CPU_DIAGNOSTIC_ONLY",
        "causal_question": (
            "Does the deployable graph receive one identical reset input while the "
            "privileged static teacher requires multiple bounded first actions, and "
            "if so how long can the unchanged graph supply a safe observation prefix "
            "before the sufficient teacher must take over?"
        ),
        "frozen_source": {
            "v54_result_sha256": V54_RESULT_SHA256,
            "v42_result_sha256": V42_RESULT_SHA256,
            "checkpoint_label": "final",
            "completed_updates": 453,
            "teacher_configuration_ids": TEACHER_CONFIGURATION_IDS,
            "failure_configuration_ids": FAILURE_CONFIGURATION_IDS,
            "plants": PLANTS,
            "pitch_indices": [2, 3, 4, 11, 12, 13],
        },
        "reset_collision_audit": {
            "rows": 30,
            "input": "exact float32 obs[115] + zero previous_action[14] + zero h_in[64]",
            "required_label": (
                "V42 raw teacher target passed through the unchanged graph-authoritative "
                "boundary from zero previous_action"
            ),
            "collision": (
                "one exact reset-input hash maps to more than one exact bounded-teacher-action hash"
            ),
            "no_rounding_or_fitted_threshold": True,
        },
        "handoff_audit": {
            "handoff_ticks": HANDOFF_TICKS,
            "semantics": (
                "use unchanged graph action for ticks strictly before the handoff; "
                "from the handoff onward replace all 14 outputs with the V42 target "
                "before the unchanged graph boundary while retaining graph h_out"
            ),
            "cells": 108,
            "ticks_per_cell": 250,
            "tick_0_must_match_v54_full_teacher_bit_exact": True,
            "tick_250_must_match_v54_graph_bit_exact": True,
            "selected_positive_handoff": (
                "the greatest member of [1,2,4,8,12,16,20] with all 12 support cells passing"
            ),
            "no_closest_cell_or_posthoc_tick": True,
        },
        "classification": {
            "TEACHER_ENDPOINT_INSUFFICIENT": "handoff tick 0 does not pass all 12 cells",
            "NO_RESET_LABEL_CONFLICT": "no exact reset input maps to multiple required labels",
            "RESET_LABEL_CONFLICT_WITH_DELAYED_HANDOFF_FEASIBLE": (
                "a reset collision exists and at least one positive handoff passes all 12 cells"
            ),
            "RESET_LABEL_CONFLICT_IMMEDIATE_TEACHER_ONLY": (
                "a reset collision exists, tick 0 passes all 12, and no positive handoff passes all 12"
            ),
        },
        "pass_rule": {
            "exact_30_reset_rows": True,
            "exact_108_handoff_cells": True,
            "tick_0_endpoint_bit_exact_to_v54": True,
            "tick_250_endpoint_bit_exact_to_v54": True,
            "all_previous_action_chains_exact": True,
            "all_jax_onnx_hidden_errors_at_most_1e_7": True,
            "all_values_finite": True,
        },
        "execution_now": {
            "reset_rows": 0,
            "diagnostic_cells": 0,
            "optimizer_updates": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "sources": sources,
        "source_manifest_sha256": canonical_sha256(sources),
        "authority": {
            "robot_clearance": False,
            "training_authorized": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "result_authorizes_only": (
                "a separately preregistered CPU mechanism selected by the frozen classification"
            ),
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown.write_text(
        "\n".join(
            [
                "# Winner-v55 reset-label and handoff preregistration",
                "",
                f"- Status: `{value['status']}`",
                f"- Decision: `{value['decision']}`",
                "- Reset rows: `15 configurations x 2 plants = 30`",
                "- Handoff cells: `6 configurations x 2 plants x 9 ticks = 108`",
                "- Optimizer / locomotion / robot: `0 / 0 / 0`",
                "",
                "This is a read-only observability and feasibility diagnostic.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(value["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
