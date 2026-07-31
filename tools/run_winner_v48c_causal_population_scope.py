#!/usr/bin/env python3
"""Audit the exact captured Winner-v48 causal failure population."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
PREREGISTRATION = ANALYSIS / "winner_v48c_causal_population_scope_preregistration.json"
V48_RESULT = ANALYSIS / "winner_v48_static_teacher_causal_diagnostic_result.json"
V48B_RESULT = (
    ANALYSIS / "winner_v48b_evidence_comparator_correction_invalid_result.json"
)
V47B_RESULT = (
    ANALYSIS / "winner_v47b_support_gate_execution_correction_result.json"
)


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def validate_source_manifest(preregistration: Mapping[str, Any]) -> None:
    sources = preregistration.get("sources")
    if not isinstance(sources, Mapping) or not sources:
        raise ValueError("Winner-v48c source manifest is absent")
    for name, item in sources.items():
        if set(item) != {"hash_mode", "path", "sha256"}:
            raise ValueError(f"Winner-v48c source record changed: {name}")
        if item["hash_mode"] != "lf" or lf_sha256(ROOT / item["path"]) != item["sha256"]:
            raise ValueError(f"Winner-v48c source changed: {name}")
    if canonical_sha256(sources) != preregistration.get("source_manifest_sha256"):
        raise ValueError("Winner-v48c source-manifest digest changed")


def checkpoint_map(result: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    rows = result["checkpoint_results"]
    mapped = {row["label"]: row for row in rows}
    if set(mapped) != {"half", "final"} or len(mapped) != len(rows):
        raise ValueError("Winner-v48c checkpoint population changed")
    return mapped


def cell_map(rows: list[Mapping[str, Any]]) -> dict[tuple[str, str], Mapping[str, Any]]:
    mapped = {(row["configuration_id"], row["plant"]): row for row in rows}
    if len(mapped) != len(rows):
        raise ValueError("Winner-v48c cell population contains duplicates")
    return mapped


def discrete_outcome(cell: Mapping[str, Any]) -> dict[str, Any]:
    terminal = cell["terminal"]
    return {
        "support_pass": cell["support_pass"],
        "terminal_tick": None if terminal is None else terminal["tick"],
        "terminal_checks": None if terminal is None else terminal["checks"],
        "terminal_contacts": None if terminal is None else terminal["contacts"],
        "valid_ticks": cell["episode"]["valid_ticks"],
        "initial_contacts": cell["episode"]["initial_contacts"],
        "previous_action_chain_exact": cell["previous_action_chain_exact"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--markdown", type=Path)
    parser.add_argument("--offline-cpu-only", action="store_true")
    parser.add_argument("--causal-population-audit-authorized", action="store_true")
    args = parser.parse_args()
    if not args.offline_cpu_only or not args.causal_population_audit_authorized:
        raise PermissionError(
            "Winner-v48c requires --offline-cpu-only "
            "--causal-population-audit-authorized"
        )
    if args.output.exists():
        raise FileExistsError(f"refusing to overwrite Winner-v48c result: {args.output}")
    markdown = args.markdown or args.output.with_suffix(".md")
    if markdown.exists():
        raise FileExistsError(f"refusing to overwrite Winner-v48c summary: {markdown}")

    preregistration = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    if (
        preregistration.get("status")
        != "PREREGISTERED_WINNER_V48C_CAUSAL_POPULATION_SCOPE_AUDIT"
        or preregistration.get("decision")
        != "AUTHORIZE_ONE_CAPTURED_CAUSAL_POPULATION_AUDIT_ONLY"
        or preregistration.get("scope", {}).get("float_tolerance") is not None
        or preregistration.get("execution_now")
        != {
            "captured_failure_pair_audits": 0,
            "new_diagnostic_cells": 0,
            "optimizer_updates": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        }
    ):
        raise ValueError("Winner-v48c preregistration changed")
    validate_source_manifest(preregistration)

    captured = json.loads(V48_RESULT.read_text(encoding="utf-8"))
    invalid_audit = json.loads(V48B_RESULT.read_text(encoding="utf-8"))
    formal = json.loads(V47B_RESULT.read_text(encoding="utf-8"))
    if (
        captured.get("status")
        != "INVALID_WINNER_V48_STATIC_TEACHER_CAUSAL_DIAGNOSTIC"
        or invalid_audit.get("status")
        != "INVALID_WINNER_V48B_EVIDENCE_COMPARATOR_CORRECTION"
        or formal.get("status")
        != "HOLD_WINNER_V47B_SUPPORT_GATE_EXECUTION_CORRECTION"
    ):
        raise ValueError("Winner-v48c source identity changed")

    captured_checkpoints = checkpoint_map(captured)
    formal_checkpoints = checkpoint_map(formal)
    audits = []
    for label in ("half", "final"):
        captured_cells = cell_map(captured_checkpoints[label]["cells"])
        formal_cells = cell_map(
            formal_checkpoints[label]["core_model_plant_cells"]
        )
        for key, formal_cell in formal_cells.items():
            if formal_cell["support_pass"]:
                continue
            observed = captured_cells[key]["arms"]["graph"]
            audits.append(
                {
                    "checkpoint": label,
                    "configuration_id": key[0],
                    "plant": key[1],
                    "all_four_trace_hashes_exact": (
                        observed["trace_hashes"] == formal_cell["trace_hashes"]
                    ),
                    "discrete_outcome_exact": (
                        discrete_outcome(observed) == discrete_outcome(formal_cell)
                    ),
                }
            )

    classification_rows = captured["findings"]["classification_rows"]
    audited_keys = {
        (row["checkpoint"], row["configuration_id"], row["plant"])
        for row in audits
    }
    classification_keys = {
        (row["checkpoint"], row["configuration_id"], row["plant"])
        for row in classification_rows
    }
    counts = captured["findings"]["classification_counts"]
    other_v48_checks = {
        name: passed
        for name, passed in captured["checks"].items()
        if name != "all_graph_cells_bit_exact_to_v47b"
    }
    checks = {
        "exact_28_formal_failure_pairs": len(audits) == 28,
        "all_four_trace_hashes_exact_for_all_28_failure_pairs": all(
            row["all_four_trace_hashes_exact"] for row in audits
        ),
        "all_28_discrete_outcomes_exact": all(
            row["discrete_outcome_exact"] for row in audits
        ),
        "exact_28_captured_classifications": (
            len(classification_rows) == 28
            and classification_keys == audited_keys
            and sum(counts.values()) == 28
        ),
        "full_teacher_passes_all_32_captured_cells": (
            captured["findings"]["full_teacher_support_pass_count"] == 32
        ),
        "all_non_comparator_v48_validity_checks_remain_true": all(
            other_v48_checks.values()
        ),
        "at_least_one_full_14d_interaction_pair": (
            counts.get("pitch_nonpitch_interaction", 0) > 0
        ),
    }
    failed_checks = sorted(name for name, passed in checks.items() if not passed)
    valid = not failed_checks
    findings = {
        "full_teacher_support_pass_count": captured["findings"][
            "full_teacher_support_pass_count"
        ],
        "classification_counts": counts,
        "selected_problem_class": (
            "FULL_14D_STATIC_TEACHER_MAPPING"
            if valid
            else "UNRESOLVED_INVALID_EVIDENCE"
        ),
    }
    result = {
        "schema_version": "winner_v48c.causal_population_scope_result.v1",
        "status": (
            "PASS_WINNER_V48C_CAUSAL_POPULATION_SCOPE_AUDIT"
            if valid
            else "INVALID_WINNER_V48C_CAUSAL_POPULATION_SCOPE_AUDIT"
        ),
        "decision": (
            "AUTHORIZE_FULL_14D_STATIC_TEACHER_MECHANISM_PREREGISTRATION_ONLY"
            if valid
            else "DO_NOT_SELECT_NEXT_POLICY_MECHANISM"
        ),
        "checks": checks,
        "failed_checks": failed_checks,
        "findings": findings,
        "failure_pair_audits": audits,
        "sources": {
            "preregistration_lf_sha256": lf_sha256(PREREGISTRATION),
            "captured_v48_result_lf_sha256": lf_sha256(V48_RESULT),
            "invalid_v48b_result_lf_sha256": lf_sha256(V48B_RESULT),
            "formal_v47b_result_lf_sha256": lf_sha256(V47B_RESULT),
            "runner_lf_sha256": lf_sha256(Path(__file__)),
        },
        "execution": {
            "captured_failure_pair_audits": len(audits),
            "new_diagnostic_cells": 0,
            "optimizer_updates": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "training_authorized": False,
            "robot_clearance": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "result_authorizes": "one separate full-14D static-teacher mechanism preregistration only",
        },
    }
    args.output.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    markdown.write_text(
        "\n".join(
            [
                "# Winner-v48c causal-population scope result",
                "",
                f"- Status: `{result['status']}`",
                f"- Decision: `{result['decision']}`",
                "- Exact formal failure-pair traces/outcomes: `28/28`",
                f"- Full-teacher support: `{findings['full_teacher_support_pass_count']}/32`",
                f"- Causal classification: `{json.dumps(counts, sort_keys=True)}`",
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
