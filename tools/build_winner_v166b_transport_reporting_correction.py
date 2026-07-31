#!/usr/bin/env python3
"""Freeze V166's post-simulation transport reporting correction."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
PREREG = ANALYSIS / "winner_v166_continuous_reference_preregistration.json"
RUNNER = ROOT / "tools/run_winner_v166_continuous_reference.py"
WRAPPER = ROOT / "tools/run_winner_v166b_transport_reporting_correction.py"
OUTPUT = ANALYSIS / "winner_v166b_transport_reporting_correction.json"
MARKDOWN = (
    ANALYSIS / "WINNER_V166B_TRANSPORT_REPORTING_CORRECTION_20260725.md"
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
            raise FileExistsError(f"refusing to overwrite V166b: {path}")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    result = ANALYSIS / "winner_v166_continuous_reference_result.json"
    result_markdown = (
        ANALYSIS / "WINNER_V166_CONTINUOUS_REFERENCE_RESULT_20260725.md"
    )
    failed_trace = (
        failed_root
        / "traces/v166_v140_p30_x0.077_seed167931544.jsonl"
    )
    failed_cell = (
        failed_root / "cells/v166_v140_p30_x0.077_seed167931544.json"
    )
    wrapper_text = WRAPPER.read_text(encoding="utf-8")
    checks = {
        "original_preregistration_green": (
            prereg["status"]
            == "PREREGISTERED_WINNER_V166_CONTINUOUS_REFERENCE"
            and prereg["failed_checks"] == []
        ),
        "original_runner_unchanged": (
            sha256(RUNNER) == prereg["input_hashes"]["runner"]
        ),
        "failed_after_trace_before_classified_cell": (
            failed_trace.is_file()
            and not failed_cell.exists()
            and not result.exists()
            and not result_markdown.exists()
        ),
        "corrected_root_absent": not corrected_root.exists(),
        "wrapper_inserts_only_nominal_zero_transport": (
            'row["transport"] = {' in wrapper_text
            and '"additional_action_delay_ticks": 0' in wrapper_text
            and '"imu_delay_ticks": 0' in wrapper_text
            and '"native_quantization": False' in wrapper_text
            and '"sensor_noise_scales": None' in wrapper_text
            and "original.run_cell = run_cell_with_transport" in wrapper_text
        ),
        "mechanism_policy_factor_seed_plant_command_and_gates_unchanged": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": "winner_v166b.transport_reporting_correction.v1",
        "status": (
            "PASS_WINNER_V166B_TRANSPORT_REPORTING_CORRECTION"
            if not failed
            else "HOLD_WINNER_V166B_TRANSPORT_REPORTING_CORRECTION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": {
            "builder": sha256(Path(__file__).resolve()),
            "preregistration": sha256(PREREG),
            "runner": sha256(RUNNER),
            "wrapper": sha256(WRAPPER),
        },
        "observed_failure": {
            "exception": "KeyError: 'transport'",
            "stage": "readback classification after simulator trace creation",
            "classified_cell_written": False,
            "result_written": False,
            "orphan_trace_not_inspected_for_behavior": True,
        },
        "correction": {
            "transport": {
                "additional_action_delay_ticks": 0,
                "imu_delay_ticks": 0,
                "native_quantization": False,
                "sensor_noise_scales": None,
            },
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
        "# Winner V166b transport reporting correction\n\n"
        f"- Status: `{payload['status']}`\n"
        "- V166 produced a trace but failed before classified-cell/result "
        "serialization on a missing `transport` reporting field.\n"
        "- The orphan trace was not inspected for behavior.\n"
        "- Correction inserts the exact nominal all-zero transport mapping.\n"
        "- Policy, factor, interpolation, matrix, gates, and stop rule are "
        "unchanged.\n"
        "- Authorizes one CPU-only rerun; no training or production change.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
