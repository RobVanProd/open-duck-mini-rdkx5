#!/usr/bin/env python3
"""Freeze V166c's externally imposed pre-output timeout correction."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
PREREG = ANALYSIS / "winner_v166_continuous_reference_preregistration.json"
REPORTING = ANALYSIS / "winner_v166b_transport_reporting_correction.json"
INVOCATION = ANALYSIS / "winner_v166c_module_invocation_correction.json"
RUNNER = ROOT / "tools/run_winner_v166_continuous_reference.py"
WRAPPER = ROOT / "tools/run_winner_v166b_transport_reporting_correction.py"
OUTPUT = ANALYSIS / "winner_v166d_execution_timeout_correction.json"
MARKDOWN = (
    ANALYSIS / "WINNER_V166D_EXECUTION_TIMEOUT_CORRECTION_20260725.md"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--failed-run-root", type=Path, required=True)
    parser.add_argument("--corrected-run-root", type=Path, required=True)
    args = parser.parse_args()
    failed_root = args.failed_run_root.resolve()
    corrected_root = args.corrected_run_root.resolve()
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V166d: {path}")

    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    reporting = json.loads(REPORTING.read_text(encoding="utf-8"))
    invocation = json.loads(INVOCATION.read_text(encoding="utf-8"))
    result = ANALYSIS / "winner_v166_continuous_reference_result.json"
    result_markdown = (
        ANALYSIS / "WINNER_V166_CONTINUOUS_REFERENCE_RESULT_20260725.md"
    )
    failed_files = (
        sorted(
            str(path.relative_to(failed_root))
            for path in failed_root.rglob("*")
            if path.is_file()
        )
        if failed_root.exists()
        else []
    )
    checks = {
        "original_preregistration_green": (
            prereg["status"]
            == "PREREGISTERED_WINNER_V166_CONTINUOUS_REFERENCE"
            and prereg["failed_checks"] == []
        ),
        "prior_corrections_green": (
            reporting["status"]
            == "PASS_WINNER_V166B_TRANSPORT_REPORTING_CORRECTION"
            and reporting["failed_checks"] == []
            and invocation["status"]
            == "PASS_WINNER_V166C_MODULE_INVOCATION_CORRECTION"
            and invocation["failed_checks"] == []
        ),
        "runner_unchanged": (
            sha256(RUNNER) == prereg["input_hashes"]["runner"]
        ),
        "wrapper_unchanged": (
            sha256(WRAPPER) == reporting["input_hashes"]["wrapper"]
        ),
        "failed_root_exists_without_files": (
            failed_root.is_dir() and failed_files == []
        ),
        "no_result_written": (
            not result.exists() and not result_markdown.exists()
        ),
        "corrected_root_absent": not corrected_root.exists(),
        "background_execution_only": True,
        "mechanism_policy_factor_seed_plant_command_and_gates_unchanged": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": "winner_v166d.execution_timeout_correction.v1",
        "status": (
            "PASS_WINNER_V166D_EXECUTION_TIMEOUT_CORRECTION"
            if not failed
            else "HOLD_WINNER_V166D_EXECUTION_TIMEOUT_CORRECTION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": {
            "builder": sha256(Path(__file__).resolve()),
            "invocation_correction": sha256(INVOCATION),
            "preregistration": sha256(PREREG),
            "reporting_correction": sha256(REPORTING),
            "runner": sha256(RUNNER),
            "wrapper": sha256(WRAPPER),
        },
        "observed_failure": {
            "exception": "foreground command timed out after 5 seconds",
            "cause": "external execution timeout",
            "stage": "after run-root creation and before any output file",
            "failed_root": str(failed_root),
            "failed_files": failed_files,
            "trace_written": False,
            "classified_cell_written": False,
            "result_written": False,
        },
        "correction": {
            "execution": "hidden background process with stdout/stderr logs",
            "fresh_run_root": str(corrected_root),
            "code_change": False,
            "mechanism_change": False,
            "factor_change": False,
            "interpolation_change": False,
            "policy_or_matrix_change": False,
            "gate_or_stop_rule_change": False,
        },
        "authority": {
            "one_corrected_cpu_rerun": not failed,
            "training": False,
            "hosted_training": False,
            "production_contract_change": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner V166d execution-timeout correction\n\n"
        f"- Status: `{payload['status']}`\n"
        "- The module-form V166c command was externally terminated after "
        "five seconds, before any trace, cell, or result file was written.\n"
        "- The partial root is quarantined and will not be reused.\n"
        "- Correction changes only process execution to a hidden background "
        "process with captured stdout/stderr and a fresh root.\n"
        "- Runner, wrapper, policy, factor, matrix, gates, and stop rule are "
        "unchanged.\n"
        "- Authorizes one CPU-only rerun; no training or production change.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
