#!/usr/bin/env python3
"""Freeze the evidence-only comparator correction for invalid Winner-v48."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = (
    ANALYSIS / "winner_v48b_evidence_comparator_correction_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "WINNER_V48B_EVIDENCE_COMPARATOR_CORRECTION_PREREGISTRATION_20260722.md"
)
V48_RESULT = ANALYSIS / "winner_v48_static_teacher_causal_diagnostic_result.json"
V47B_RESULT = (
    ANALYSIS / "winner_v47b_support_gate_execution_correction_result.json"
)
V48_RESULT_SHA256 = "cc4ec3cb64c60aa1b498da0286ecbdadac01f7f6344123893105830f756e31cc"
FLOAT64_ABSOLUTE_TOLERANCE = 1.0e-12
SOURCES = {
    "builder": Path(
        "tools/build_winner_v48b_evidence_comparator_correction_preregistration.py"
    ),
    "runner": Path("tools/run_winner_v48b_evidence_comparator_correction.py"),
    "tests": Path("tests/test_winner_v48b_evidence_comparator_correction.py"),
    "v48_preregistration": Path(
        "outputs/analysis/winner_v48_static_teacher_causal_diagnostic_preregistration.json"
    ),
    "v48_result": Path(
        "outputs/analysis/winner_v48_static_teacher_causal_diagnostic_result.json"
    ),
    "v47b_result": Path(
        "outputs/analysis/winner_v47b_support_gate_execution_correction_result.json"
    ),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def validate_invalid_v48(result: Mapping[str, Any]) -> None:
    findings = result.get("findings", {})
    if (
        result.get("schema_version")
        != "winner_v48.static_teacher_causal_diagnostic_result.v1"
        or result.get("status")
        != "INVALID_WINNER_V48_STATIC_TEACHER_CAUSAL_DIAGNOSTIC"
        or result.get("decision") != "DO_NOT_SELECT_NEXT_POLICY_MECHANISM"
        or result.get("failed_checks") != ["all_graph_cells_bit_exact_to_v47b"]
        or result.get("execution")
        != {
            "diagnostic_cells": 128,
            "optimizer_updates": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        }
        or result.get("checks", {}).get("exact_128_cells") is not True
        or result.get("checks", {}).get("exact_28_formal_failed_pair_classifications")
        is not True
        or result.get("checks", {}).get("all_previous_action_chains_exact") is not True
        or result.get("checks", {}).get(
            "all_jax_onnx_hidden_errors_at_most_1e_7"
        )
        is not True
        or findings.get("full_teacher_support_pass_count") != 32
        or findings.get("classification_counts")
        != {
            "either_single_intervention_rescues": 0,
            "nonpitch_output_causal": 0,
            "pitch_nonpitch_interaction": 3,
            "pitch_output_causal": 25,
            "teacher_insufficient": 0,
        }
        or result.get("authority", {}).get("robot_clearance") is not False
    ):
        raise ValueError("invalid Winner-v48 evidence changed")


def validate_v47b_hold(result: Mapping[str, Any]) -> None:
    if (
        result.get("schema_version")
        != "winner_v47b.support_gate_execution_correction_result.v1"
        or result.get("status")
        != "HOLD_WINNER_V47B_SUPPORT_GATE_EXECUTION_CORRECTION"
        or result.get("decision") != "DO_NOT_TRAIN_RESPONSE_CONDITIONED_LOCOMOTION"
        or result.get("execution", {}).get("formal_support_cells") != 248
    ):
        raise ValueError("Winner-v47b source evidence changed")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite Winner-v48b contract: {path}")

    v48 = json.loads(V48_RESULT.read_text(encoding="utf-8"))
    v47b = json.loads(V47B_RESULT.read_text(encoding="utf-8"))
    validate_invalid_v48(v48)
    validate_v47b_hold(v47b)
    if sha256(V48_RESULT) != V48_RESULT_SHA256:
        raise ValueError("Winner-v48 result bytes changed")
    sources = {
        name: {
            "path": path.as_posix(),
            "hash_mode": "lf",
            "sha256": lf_sha256(ROOT / path),
        }
        for name, path in SOURCES.items()
    }
    payload = {
        "schema_version": "winner_v48b.evidence_comparator_correction_preregistration.v1",
        "status": "PREREGISTERED_WINNER_V48B_EVIDENCE_COMPARATOR_CORRECTION",
        "decision": "AUTHORIZE_ONE_CAPTURED_EVIDENCE_AUDIT_ONLY",
        "invalid_execution": {
            "v48_result_sha256": V48_RESULT_SHA256,
            "diagnostic_cells_already_executed": 128,
            "failed_check": "all_graph_cells_bit_exact_to_v47b",
            "other_validity_checks_passed": 6,
            "rerun_authorized": False,
        },
        "exact_correction": {
            "old_comparator": "whole Python public-cell dictionary equality",
            "rejected_values": (
                "float64 MuJoCo terminal/summary diagnostics differing only below "
                "the frozen absolute bookkeeping tolerance"
            ),
            "new_trace_rule": (
                "all four float32 action, observation, prediction, and hidden trace "
                "SHA-256 values must match exactly for all 32 graph cells"
            ),
            "new_discrete_rule": (
                "support outcome, terminal tick, validity checks, contacts, valid tick "
                "count, previous-action chaining, and string/hash evidence must match exactly"
            ),
            "new_float64_rule": {
                "absolute_tolerance": FLOAT64_ABSOLUTE_TOLERANCE,
                "relative_tolerance": 0.0,
                "scope": "shared terminal and episode diagnostic leaves only",
                "behavior_threshold_or_selection_change": False,
            },
            "cells_policy_checkpoint_plant_or_action_change": False,
        },
        "captured_findings_not_yet_promoted": {
            "full_teacher_support_pass_count": 32,
            "formal_failed_pairs": 28,
            "pitch_output_causal": 25,
            "pitch_nonpitch_interaction": 3,
        },
        "pass_rule": {
            "exact_32_graph_trace_hash_sets": True,
            "exact_32_graph_discrete_outcomes": True,
            "all_shared_float64_differences_at_most_1e_12": True,
            "all_other_v48_validity_checks_remain_true": True,
            "exact_128_captured_cells": True,
        },
        "pass_authorizes_only": (
            "the captured causal classification and a separate full-14D teacher "
            "mechanism preregistration"
        ),
        "execution_now": {
            "captured_cell_audits": 0,
            "new_diagnostic_cells": 0,
            "optimizer_updates": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "robot_clearance": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "training_authorized": False,
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
                "# Winner-v48b evidence-comparator correction preregistration",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                "- Previously captured cells / new cells: `128 / 0`",
                "- Trace rule: four float32 hashes exact for all `32` graph cells",
                "- Float64 bookkeeping tolerance: absolute `1e-12`, relative `0`",
                "- Optimizer / locomotion / robot: `0 / 0 / 0`",
                "",
                "This correction audits the existing result only. It does not rerun",
                "physics, change a behavior gate, or authorize training or deployment.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
