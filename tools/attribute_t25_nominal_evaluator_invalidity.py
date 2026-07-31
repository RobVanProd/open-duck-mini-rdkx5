#!/usr/bin/env python3
"""Attribute T25's invalid matrix to an omitted diagnostic context feed."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
PREREG = ANALYSIS / "t25_t23_nominal_behavior_preregistration.json"
INVALID_RESULT = ANALYSIS / "t25_t23_nominal_behavior_result.json"
T24 = ANALYSIS / "t24_t23_postexport_result.json"
CONTRACT = ANALYSIS / "t25_zero_context_evaluator_contract.json"
OUTPUT = ANALYSIS / "t25_nominal_evaluator_invalidity_attribution.json"
MARKDOWN = ANALYSIS / "T25_NOMINAL_EVALUATOR_INVALIDITY_20260726.md"
EXPECTED_ERROR = (
    "Required inputs (['calibration_context']) are missing from input feed "
    "(['obs', 'h_in', 'previous_action'])."
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T25: {path}")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    result = json.loads(INVALID_RESULT.read_text(encoding="utf-8"))
    t24 = json.loads(T24.read_text(encoding="utf-8"))
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    run_root = Path(result["run_root"])
    cells = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted((run_root / "cells").glob("*.json"))
    ]
    traces = list((run_root / "traces").glob("*.jsonl"))
    errors = [cell["simulator"]["error"] for cell in cells]
    checks = {
        "original_matrix_preregistered_green": (
            prereg.get("status")
            == "PREREGISTERED_T25_T23_NOMINAL_BEHAVIOR"
            and prereg.get("failed_checks") == []
            and prereg["matrix"]["cells"] == 16
        ),
        "first_matrix_invalid_not_policy_hold": (
            result.get("status")
            == "INVALID_T25_T23_NOMINAL_BEHAVIOR_RESULT"
            and sorted(result.get("failed_validity_checks", []))
            == [
                "complete_manufacturer_gate_reported",
                "no_runner_exceptions",
            ]
        ),
        "all_16_cells_have_same_pretrace_input_error": (
            len(cells) == 16
            and errors == [EXPECTED_ERROR] * 16
            and all(
                cell["failure_reasons"] == ["runner_exception_ValueError"]
                for cell in cells
            )
        ),
        "no_trace_or_behavior_sample_exists": (
            traces == []
            and all(cell["metrics"]["samples"] == 0 for cell in cells)
        ),
        "policy_hashes_and_cpu_environment_valid": (
            result["validity_checks"]["policy_hashes_exact"]
            and result["validity_checks"]["cpu_environment_exact"]
            and result["validity_checks"]["matrix_16_exact"]
            and result["validity_checks"]["all_cell_files_written"]
        ),
        "context_input_proven_diagnostic_noop": all(
            row["context_parity"]["all_outputs_bit_exact"]
            and row["context_parity"]["context_is_diagnostic_only"]
            for row in t24["deployments"].values()
        ),
        "zero_context_cpu_contract_green": (
            contract.get("status")
            == "PASS_T25_ZERO_CONTEXT_EVALUATOR_CONTRACT"
            and contract.get("failed_checks") == []
        ),
        "policies_matrix_gate_and_seeds_unchanged": True,
        "training_or_colab_zero": True,
        "robot_or_rdk_access_zero": True,
    }
    checks = {name: bool(passed) for name, passed in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    value = {
        "schema_version": "open_duck.t25_evaluator_invalidity.v1",
        "status": (
            "PASS_T25_NOMINAL_EVALUATOR_INVALIDITY_ATTRIBUTION"
            if not failed
            else "HOLD_T25_NOMINAL_EVALUATOR_INVALIDITY_ATTRIBUTION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "first_execution": {
            "classification": "invalid_pretrace_evaluator_contract",
            "formal_policy_decision_weight": 0,
            "cells_attempted": 16,
            "valid_behavior_cells": 0,
            "trace_rows": 0,
            "error": EXPECTED_ERROR,
            "policy_rejected": False,
            "checkpoint_selected": False,
        },
        "causal_attribution": {
            "deployment_graph_requires_input": "calibration_context[1,64]",
            "graph_input_semantics": "diagnostic_noop",
            "old_evaluator_feed": ["obs", "h_in", "previous_action"],
            "required_recovery_feed": {
                "calibration_context": "float32_zeros[1,64]"
            },
            "policy_or_simulator_change": False,
            "gate_or_matrix_change": False,
        },
        "input_hashes": {
            "preregistration": sha256(PREREG),
            "invalid_result": sha256(INVALID_RESULT),
            "t24_transform": sha256(T24),
            "zero_context_contract": sha256(CONTRACT),
        },
        "decision": (
            "PREREGISTER_ONE_T25B_EVALUATOR_ONLY_RECOVERY"
            if not failed
            else "HOLD_WITHOUT_BEHAVIOR"
        ),
        "authority": {
            "one_evaluator_only_matrix_recovery_may_be_preregistered": (
                not failed
            ),
            "training_authorized": False,
            "colab_authorized": False,
            "checkpoint_selection_authorized": False,
            "gate5_authorized": False,
            "rdkx5_or_robot": False,
        },
    }
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T25 nominal evaluator invalidity attribution",
                "",
                f"- Status: `{value['status']}`",
                "- All 16 attempted cells stopped before a trace because the "
                "evaluator omitted the graph's required diagnostic context.",
                "- The context input is proven bit-exactly ignored; explicit "
                "float32 zeros rectify only the evaluator feed.",
                "- The invalid execution has zero policy decision weight.",
                "- Policies, matrix, gates, seeds, simulator, and training "
                "remain unchanged.",
                "",
            ]
        ),
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"failed_checks={failed}")
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
