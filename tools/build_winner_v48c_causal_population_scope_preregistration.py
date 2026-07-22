#!/usr/bin/env python3
"""Freeze the no-tolerance causal-population audit for captured Winner-v48."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v48c_causal_population_scope_preregistration.json"
MARKDOWN = (
    ANALYSIS / "WINNER_V48C_CAUSAL_POPULATION_SCOPE_PREREGISTRATION_20260722.md"
)
V48_RESULT = ANALYSIS / "winner_v48_static_teacher_causal_diagnostic_result.json"
V48B_RESULT = (
    ANALYSIS / "winner_v48b_evidence_comparator_correction_invalid_result.json"
)
V47B_RESULT = (
    ANALYSIS / "winner_v47b_support_gate_execution_correction_result.json"
)
SOURCES = {
    "builder": Path("tools/build_winner_v48c_causal_population_scope_preregistration.py"),
    "runner": Path("tools/run_winner_v48c_causal_population_scope.py"),
    "tests": Path("tests/test_winner_v48c_causal_population_scope.py"),
    "v48_preregistration": Path(
        "outputs/analysis/winner_v48_static_teacher_causal_diagnostic_preregistration.json"
    ),
    "v48_result": Path(
        "outputs/analysis/winner_v48_static_teacher_causal_diagnostic_result.json"
    ),
    "v48b_preregistration": Path(
        "outputs/analysis/winner_v48b_evidence_comparator_correction_preregistration.json"
    ),
    "v48b_result": Path(
        "outputs/analysis/winner_v48b_evidence_comparator_correction_invalid_result.json"
    ),
    "v47b_result": Path(
        "outputs/analysis/winner_v47b_support_gate_execution_correction_result.json"
    ),
}


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def validate_sources(
    v48: Mapping[str, Any], v48b: Mapping[str, Any], v47b: Mapping[str, Any]
) -> None:
    if (
        v48.get("status") != "INVALID_WINNER_V48_STATIC_TEACHER_CAUSAL_DIAGNOSTIC"
        or v48.get("failed_checks") != ["all_graph_cells_bit_exact_to_v47b"]
        or v48.get("execution", {}).get("diagnostic_cells") != 128
        or v48.get("findings", {}).get("full_teacher_support_pass_count") != 32
        or len(v48.get("findings", {}).get("classification_rows", [])) != 28
    ):
        raise ValueError("Winner-v48 captured evidence changed")
    if (
        v48b.get("status")
        != "INVALID_WINNER_V48B_EVIDENCE_COMPARATOR_CORRECTION"
        or sorted(v48b.get("failed_checks", []))
        != sorted(
            [
                "all_32_graph_discrete_outcomes_exact",
                "all_32_graph_trace_hash_sets_exact",
                "all_shared_float64_differences_at_most_1e_12",
            ]
        )
        or v48b.get("execution", {}).get("new_diagnostic_cells") != 0
    ):
        raise ValueError("Winner-v48b invalid audit changed")
    if (
        v47b.get("status")
        != "HOLD_WINNER_V47B_SUPPORT_GATE_EXECUTION_CORRECTION"
        or sum(
            not cell["support_pass"]
            for checkpoint in v47b.get("checkpoint_results", [])
            for cell in checkpoint.get("core_model_plant_cells", [])
        )
        != 28
    ):
        raise ValueError("Winner-v47b failure population changed")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite Winner-v48c contract: {path}")

    v48 = json.loads(V48_RESULT.read_text(encoding="utf-8"))
    v48b = json.loads(V48B_RESULT.read_text(encoding="utf-8"))
    v47b = json.loads(V47B_RESULT.read_text(encoding="utf-8"))
    validate_sources(v48, v48b, v47b)
    sources = {
        name: {
            "path": path.as_posix(),
            "hash_mode": "lf",
            "sha256": lf_sha256(ROOT / path),
        }
        for name, path in SOURCES.items()
    }
    payload = {
        "schema_version": "winner_v48c.causal_population_scope_preregistration.v1",
        "status": "PREREGISTERED_WINNER_V48C_CAUSAL_POPULATION_SCOPE_AUDIT",
        "decision": "AUTHORIZE_ONE_CAPTURED_CAUSAL_POPULATION_AUDIT_ONLY",
        "scope": {
            "source_population": (
                "the exact 28 checkpoint/configuration/plant pairs that failed the "
                "imported V47b graph support gate"
            ),
            "excluded_from_causal_claim": (
                "the four full-duration graph control pairs that did not fail V47b"
            ),
            "captured_intervention_cells": 128,
            "new_physics_cells": 0,
            "float_tolerance": None,
        },
        "pass_rule": {
            "exact_28_formal_failure_pairs": True,
            "all_four_trace_hashes_exact_for_each_failure_pair": True,
            "support_outcome_terminal_tick_checks_contacts_and_valid_ticks_exact": True,
            "exact_28_captured_classifications": True,
            "full_teacher_passes_all_32_captured_cells": True,
            "all_non_comparator_v48_validity_checks_remain_true": True,
        },
        "interpretation_rule": {
            "pitch_output_causal": (
                "full teacher and pitch replacement pass while non-pitch-zero alone fails"
            ),
            "pitch_nonpitch_interaction": (
                "only the full 14-D teacher passes the failed pair"
            ),
            "selection": (
                "if all 28 exact failure pairs are classified, full teacher is 32/32, "
                "and any interaction pair exists, authorize only a full-14D static-"
                "teacher mechanism preregistration"
            ),
        },
        "execution_now": {
            "captured_failure_pair_audits": 0,
            "new_diagnostic_cells": 0,
            "optimizer_updates": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "training_authorized": False,
            "robot_clearance": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "pass_authorizes_only": "a separate full-14D static-teacher mechanism preregistration",
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
                "# Winner-v48c causal-population scope preregistration",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                "- Causal source population: exact `28` V47b graph failures",
                "- Captured intervention cells / new physics cells: `128 / 0`",
                "- Float tolerance: none; exact trace hashes and discrete outcomes only",
                "- Optimizer / locomotion / robot: `0 / 0 / 0`",
                "",
                "The four graph pairs that formally passed are controls, not members of",
                "the failure-cause claim. This audit does not rerun or tune anything.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
