#!/usr/bin/env python3
"""Freeze V166b's pre-simulation module-invocation correction."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
PREREG = ANALYSIS / "winner_v166_continuous_reference_preregistration.json"
REPORTING_CORRECTION = (
    ANALYSIS / "winner_v166b_transport_reporting_correction.json"
)
RUNNER = ROOT / "tools/run_winner_v166_continuous_reference.py"
WRAPPER = ROOT / "tools/run_winner_v166b_transport_reporting_correction.py"
OUTPUT = (
    ANALYSIS / "winner_v166c_module_invocation_correction.json"
)
MARKDOWN = (
    ANALYSIS / "WINNER_V166C_MODULE_INVOCATION_CORRECTION_20260725.md"
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
            raise FileExistsError(f"refusing to overwrite V166c: {path}")

    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    correction = json.loads(
        REPORTING_CORRECTION.read_text(encoding="utf-8")
    )
    result = ANALYSIS / "winner_v166_continuous_reference_result.json"
    result_markdown = (
        ANALYSIS / "WINNER_V166_CONTINUOUS_REFERENCE_RESULT_20260725.md"
    )
    checks = {
        "original_preregistration_green": (
            prereg["status"]
            == "PREREGISTERED_WINNER_V166_CONTINUOUS_REFERENCE"
            and prereg["failed_checks"] == []
        ),
        "reporting_correction_green": (
            correction["status"]
            == "PASS_WINNER_V166B_TRANSPORT_REPORTING_CORRECTION"
            and correction["failed_checks"] == []
        ),
        "runner_unchanged": (
            sha256(RUNNER) == prereg["input_hashes"]["runner"]
        ),
        "wrapper_unchanged": (
            sha256(WRAPPER)
            == correction["input_hashes"]["wrapper"]
        ),
        "failed_before_run_root_creation": not failed_root.exists(),
        "no_result_written": (
            not result.exists() and not result_markdown.exists()
        ),
        "corrected_root_absent": not corrected_root.exists(),
        "module_invocation_only": True,
        "mechanism_policy_factor_seed_plant_command_and_gates_unchanged": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": "winner_v166c.module_invocation_correction.v1",
        "status": (
            "PASS_WINNER_V166C_MODULE_INVOCATION_CORRECTION"
            if not failed
            else "HOLD_WINNER_V166C_MODULE_INVOCATION_CORRECTION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": {
            "builder": sha256(Path(__file__).resolve()),
            "preregistration": sha256(PREREG),
            "reporting_correction": sha256(REPORTING_CORRECTION),
            "runner": sha256(RUNNER),
            "wrapper": sha256(WRAPPER),
        },
        "observed_failure": {
            "command_form": "python tools/run_winner_v166b_"
            "transport_reporting_correction.py",
            "exception": "ModuleNotFoundError: No module named 'tools'",
            "stage": "wrapper import before argument parsing and simulation",
            "run_root_created": False,
            "trace_written": False,
            "classified_cell_written": False,
            "result_written": False,
        },
        "correction": {
            "command_form": (
                "python -m tools.run_winner_v166b_"
                "transport_reporting_correction"
            ),
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
        "# Winner V166c module-invocation correction\n\n"
        f"- Status: `{payload['status']}`\n"
        "- The V166b wrapper failed during import, before argument parsing, "
        "run-root creation, or simulation.\n"
        "- Correction changes only invocation from a file path to Python's "
        "module form so the repository root is importable.\n"
        "- Runner and wrapper hashes are unchanged.\n"
        "- Policy, factor, interpolation, matrix, gates, and stop rule are "
        "unchanged.\n"
        "- Authorizes one CPU-only rerun in a fresh root; no training or "
        "production change.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
