#!/usr/bin/env python3
"""Audit captured Winner-v48 evidence with its corrected comparator."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
PREREGISTRATION = (
    ANALYSIS / "winner_v48b_evidence_comparator_correction_preregistration.json"
)
V48_RESULT = ANALYSIS / "winner_v48_static_teacher_causal_diagnostic_result.json"
V47B_RESULT = (
    ANALYSIS / "winner_v47b_support_gate_execution_correction_result.json"
)
FLOAT64_ABSOLUTE_TOLERANCE = 1.0e-12


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def validate_source_manifest(preregistration: Mapping[str, Any]) -> None:
    sources = preregistration.get("sources")
    if not isinstance(sources, Mapping) or not sources:
        raise ValueError("Winner-v48b source manifest is absent")
    for name, item in sources.items():
        if set(item) != {"hash_mode", "path", "sha256"}:
            raise ValueError(f"Winner-v48b source record changed: {name}")
        if item["hash_mode"] != "lf" or lf_sha256(ROOT / item["path"]) != item["sha256"]:
            raise ValueError(f"Winner-v48b source changed: {name}")
    if canonical_sha256(sources) != preregistration.get("source_manifest_sha256"):
        raise ValueError("Winner-v48b source-manifest digest changed")


def formal_projection(cell: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "support_pass": cell["support_pass"],
        "terminal": cell["terminal"],
        "episode": cell["episode"],
        "previous_action_chain_exact": cell["previous_action_chain_exact"],
        "maximum_jax_onnx_hidden_error": cell["maximum_jax_onnx_hidden_error"],
        "trace_hashes": cell["trace_hashes"],
    }


def compare_evidence(
    observed: Any, expected: Any, *, path: str = "root"
) -> dict[str, Any]:
    maximum = 0.0
    numeric_count = 0
    discrete_mismatches: list[str] = []

    def visit(left: Any, right: Any, location: str) -> None:
        nonlocal maximum, numeric_count
        if isinstance(left, Mapping) and isinstance(right, Mapping):
            if set(left) != set(right):
                discrete_mismatches.append(f"{location}:keys")
                return
            for key in sorted(left):
                visit(left[key], right[key], f"{location}.{key}")
            return
        if isinstance(left, list) and isinstance(right, list):
            if len(left) != len(right):
                discrete_mismatches.append(f"{location}:length")
                return
            for index, (left_item, right_item) in enumerate(zip(left, right)):
                visit(left_item, right_item, f"{location}[{index}]")
            return
        if (
            isinstance(left, (int, float))
            and not isinstance(left, bool)
            and isinstance(right, (int, float))
            and not isinstance(right, bool)
            and (isinstance(left, float) or isinstance(right, float))
        ):
            left_float = float(left)
            right_float = float(right)
            if not math.isfinite(left_float) or not math.isfinite(right_float):
                discrete_mismatches.append(f"{location}:nonfinite")
                return
            maximum = max(maximum, abs(left_float - right_float))
            numeric_count += 1
            return
        if type(left) is not type(right) or left != right:
            discrete_mismatches.append(location)

    visit(observed, expected, path)
    return {
        "maximum_abs_float64_difference": maximum,
        "float64_leaf_count": numeric_count,
        "discrete_mismatches": discrete_mismatches,
        "discrete_exact": not discrete_mismatches,
        "float64_within_absolute_1e_12": maximum <= FLOAT64_ABSOLUTE_TOLERANCE,
    }


def cell_map(checkpoint: Mapping[str, Any], key: str) -> dict[tuple[str, str], Any]:
    rows = checkpoint[key]
    result = {(row["configuration_id"], row["plant"]): row for row in rows}
    if len(result) != len(rows):
        raise ValueError("Winner-v48b source cell population contains duplicates")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--markdown", type=Path)
    parser.add_argument("--offline-cpu-only", action="store_true")
    parser.add_argument("--captured-evidence-audit-authorized", action="store_true")
    args = parser.parse_args()
    if not args.offline_cpu_only or not args.captured_evidence_audit_authorized:
        raise PermissionError(
            "Winner-v48b requires --offline-cpu-only "
            "--captured-evidence-audit-authorized"
        )
    if args.output.exists():
        raise FileExistsError(f"refusing to overwrite Winner-v48b result: {args.output}")
    markdown = args.markdown or args.output.with_suffix(".md")
    if markdown.exists():
        raise FileExistsError(f"refusing to overwrite Winner-v48b summary: {markdown}")

    preregistration = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    if (
        preregistration.get("status")
        != "PREREGISTERED_WINNER_V48B_EVIDENCE_COMPARATOR_CORRECTION"
        or preregistration.get("decision")
        != "AUTHORIZE_ONE_CAPTURED_EVIDENCE_AUDIT_ONLY"
        or preregistration.get("execution_now")
        != {
            "captured_cell_audits": 0,
            "new_diagnostic_cells": 0,
            "optimizer_updates": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        }
        or preregistration.get("exact_correction", {})
        .get("new_float64_rule", {})
        .get("absolute_tolerance")
        != FLOAT64_ABSOLUTE_TOLERANCE
    ):
        raise ValueError("Winner-v48b preregistration changed")
    validate_source_manifest(preregistration)

    captured = json.loads(V48_RESULT.read_text(encoding="utf-8"))
    formal = json.loads(V47B_RESULT.read_text(encoding="utf-8"))
    if (
        captured.get("status")
        != "INVALID_WINNER_V48_STATIC_TEACHER_CAUSAL_DIAGNOSTIC"
        or captured.get("failed_checks") != ["all_graph_cells_bit_exact_to_v47b"]
        or formal.get("status")
        != "HOLD_WINNER_V47B_SUPPORT_GATE_EXECUTION_CORRECTION"
    ):
        raise ValueError("Winner-v48b captured evidence identity changed")

    audits = []
    for captured_checkpoint in captured["checkpoint_results"]:
        label = captured_checkpoint["label"]
        formal_checkpoint = next(
            row for row in formal["checkpoint_results"] if row["label"] == label
        )
        captured_cells = cell_map(captured_checkpoint, "cells")
        formal_cells = cell_map(formal_checkpoint, "core_model_plant_cells")
        for key, row in captured_cells.items():
            observed = row["arms"]["graph"]
            expected = formal_projection(formal_cells[key])
            comparison = compare_evidence(observed, expected, path="graph")
            audits.append(
                {
                    "checkpoint": label,
                    "configuration_id": key[0],
                    "plant": key[1],
                    "trace_hashes_exact": (
                        observed["trace_hashes"] == expected["trace_hashes"]
                    ),
                    **comparison,
                }
            )

    other_v48_checks = {
        name: value
        for name, value in captured["checks"].items()
        if name != "all_graph_cells_bit_exact_to_v47b"
    }
    checks = {
        "exact_32_captured_graph_cell_audits": len(audits) == 32,
        "all_32_graph_trace_hash_sets_exact": all(
            row["trace_hashes_exact"] for row in audits
        ),
        "all_32_graph_discrete_outcomes_exact": all(
            row["discrete_exact"] for row in audits
        ),
        "all_shared_float64_differences_at_most_1e_12": all(
            row["float64_within_absolute_1e_12"] for row in audits
        ),
        "all_other_v48_validity_checks_remain_true": all(
            other_v48_checks.values()
        ),
        "exact_128_captured_cells": (
            captured.get("execution", {}).get("diagnostic_cells") == 128
        ),
    }
    failed_checks = sorted(name for name, passed in checks.items() if not passed)
    valid = not failed_checks
    findings = {
        "maximum_graph_evidence_abs_float64_difference": max(
            row["maximum_abs_float64_difference"] for row in audits
        ),
        "full_teacher_support_pass_count": captured["findings"][
            "full_teacher_support_pass_count"
        ],
        "classification_counts": captured["findings"]["classification_counts"],
        "selected_problem_class": (
            "FULL_14D_STATIC_TEACHER_MAPPING"
            if valid
            else "UNRESOLVED_INVALID_EVIDENCE"
        ),
    }
    result = {
        "schema_version": "winner_v48b.evidence_comparator_correction_result.v1",
        "status": (
            "PASS_WINNER_V48B_EVIDENCE_COMPARATOR_CORRECTION"
            if valid
            else "INVALID_WINNER_V48B_EVIDENCE_COMPARATOR_CORRECTION"
        ),
        "decision": (
            "AUTHORIZE_FULL_14D_STATIC_TEACHER_MECHANISM_PREREGISTRATION_ONLY"
            if valid
            else "DO_NOT_SELECT_NEXT_POLICY_MECHANISM"
        ),
        "checks": checks,
        "failed_checks": failed_checks,
        "findings": findings,
        "graph_cell_audits": audits,
        "captured_v48_checks": captured["checks"],
        "sources": {
            "preregistration_lf_sha256": lf_sha256(PREREGISTRATION),
            "captured_v48_result_lf_sha256": lf_sha256(V48_RESULT),
            "formal_v47b_result_lf_sha256": lf_sha256(V47B_RESULT),
            "runner_lf_sha256": lf_sha256(Path(__file__)),
        },
        "execution": {
            "captured_cell_audits": len(audits),
            "new_diagnostic_cells": 0,
            "optimizer_updates": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "robot_clearance": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "training_authorized": False,
            "result_authorizes": "one separate full-14D teacher mechanism preregistration only",
        },
    }
    args.output.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    markdown.write_text(
        "\n".join(
            [
                "# Winner-v48b evidence-comparator correction result",
                "",
                f"- Status: `{result['status']}`",
                f"- Decision: `{result['decision']}`",
                f"- Maximum shared float64 difference: `{findings['maximum_graph_evidence_abs_float64_difference']:.17g}`",
                f"- Full-teacher support: `{findings['full_teacher_support_pass_count']}/32`",
                f"- Causal classification: `{json.dumps(findings['classification_counts'], sort_keys=True)}`",
                "- New physics cells / optimizer / locomotion / robot: `0 / 0 / 0 / 0`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(result["status"])
    print(json.dumps(findings, sort_keys=True))
    return 0 if valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
