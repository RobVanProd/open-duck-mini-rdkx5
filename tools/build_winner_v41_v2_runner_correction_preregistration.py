#!/usr/bin/env python3
"""Freeze the narrow Winner-v41 static-target expansion correction."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v41_v2_runner_correction_preregistration.json"
MARKDOWN = ANALYSIS / "WINNER_V41_V2_RUNNER_CORRECTION_PREREGISTRATION_20260722.md"
FAILURE = ANALYSIS / "winner_v41_first_attempt_failure_receipt.json"

SOURCES = {
    "builder": Path("tools/build_winner_v41_v2_runner_correction_preregistration.py"),
    "correction_runner": Path(
        "tools/run_winner_v41_v2_static_equilibrium_target_feasibility.py"
    ),
    "correction_runner_tests": Path(
        "tests/test_winner_v41_v2_static_equilibrium_target_feasibility.py"
    ),
    "correction_preregistration_tests": Path(
        "tests/test_winner_v41_v2_runner_correction_preregistration.py"
    ),
    "corrected_result_importer": Path(
        "tools/import_winner_v41_v2_static_equilibrium_target_feasibility.py"
    ),
    "corrected_result_importer_tests": Path(
        "tests/test_winner_v41_v2_static_equilibrium_target_feasibility_import.py"
    ),
    "corrected_workflow": Path(
        ".github/workflows/winner-v41-v2-static-equilibrium-target-feasibility.yml"
    ),
    "first_attempt_failure_receipt": Path(
        "outputs/analysis/winner_v41_first_attempt_failure_receipt.json"
    ),
    "first_attempt_failure_markdown": Path(
        "outputs/analysis/WINNER_V41_FIRST_ATTEMPT_FAILURE_RECEIPT_20260722.md"
    ),
    "base_preregistration": Path(
        "outputs/analysis/winner_v41_static_equilibrium_target_feasibility_preregistration.json"
    ),
    "base_runner": Path("tools/run_winner_v41_static_equilibrium_target_feasibility.py"),
    "base_importer": Path("tools/import_winner_v41_static_equilibrium_target_feasibility.py"),
    "reviewed_mirror_basis": Path("patches/winner_v16_support_action_direction.py"),
}


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
    if args.output.exists() or args.markdown.exists():
        raise FileExistsError("refusing to overwrite Winner-v41-v2 correction")
    failure = json.loads(FAILURE.read_text(encoding="utf-8"))
    if failure != {
        "artifact_count": 0,
        "classification": "PRE_CANDIDATE_STATIC_TARGET_EXPANSION_SHAPE_DEFECT",
        "decision": "AUTHORIZE_NARROW_V41_V2_RUNNER_CORRECTION_PREREGISTRATION_ONLY",
        "failure": {
            "exception": "ValueError",
            "message": "Winner-v38 mirrored block sequence shape changed",
            "source_call": "v38.expand_mirrored_blocks(coordinates[None, :])",
            "source_line": 115,
            "stage": "first candidate target expansion",
        },
        "github_run": {
            "attempt": 1,
            "conclusion": "failure",
            "head_sha": "cd89be92cdd3b669cdb8ec5a50486dcc65484ca8",
            "run_id": 29901924055,
            "url": "https://github.com/RobVanProd/open-duck-mini-rdkx5/actions/runs/29901924055",
        },
        "schema_version": "winner_v41.first_attempt_failure_receipt.v1",
        "status": "INVALID_WINNER_V41_FIRST_ATTEMPT_NO_RESULT",
        "work_executed": {
            "candidate_plant_cells": 0,
            "optimizer_updates": 0,
            "robot_or_rdk_access": 0,
            "static_target_candidates": 0,
        },
    }:
        raise ValueError("Winner-v41 first-attempt failure receipt changed")
    sources = {
        name: {"path": path.as_posix(), "hash_mode": "lf", "sha256": lf_sha256(ROOT / path)}
        for name, path in SOURCES.items()
    }
    value = {
        "schema_version": "winner_v41.v2_runner_correction_preregistration.v1",
        "status": "PREREGISTERED_WINNER_V41_V2_RUNNER_CORRECTION",
        "decision": "AUTHORIZE_ONE_CORRECTED_CPU_ONLY_V41_SCREEN",
        "correction": {
            "old_call": "v38.expand_mirrored_blocks(coordinates[None, :])",
            "new_call": "coordinates @ v38.MIRROR_MATRIX.T into the same six indices",
            "changed_behavior": "accept exactly one three-coordinate static target",
            "unchanged_behavior": (
                "grid, basis, action boundary, plants, duration, selection, pass rule, "
                "execution counts, and authority"
            ),
        },
        "first_attempt": failure,
        "execution_now": {
            "static_target_candidates": 0,
            "candidate_plant_cells": 0,
            "optimizer_updates": 0,
            "locomotion_training_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "pass_rule": (
            "unchanged winner_v41.static_equilibrium_target_feasibility_preregistration.v1"
        ),
        "sources": sources,
        "source_manifest_sha256": canonical_sha256(sources),
        "authority": {
            "first_attempt_rerun_authorized": False,
            "one_versioned_corrected_run_authorized": True,
            "robot_clearance": False,
            "training_authorized": False,
            "runtime_static_target_or_action_wrapper_authorized": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown.write_text(
        "\n".join([
            "# Winner-v41 v2 runner-correction preregistration", "",
            f"- Status: `{value['status']}`",
            f"- Decision: `{value['decision']}`",
            "- Preserved failed run: `29901924055`, no artifact, zero candidates",
            "- Only change: `(1,3)` target expansion through the frozen mirror matrix",
            "- Grid / plants / ticks: `729 / 2 / 250` unchanged",
            "- Optimizer / locomotion training / robot: `0 / 0 / 0`", "",
            "The failed workflow is not rerun. One separately named corrected workflow",
            "may execute the original gate with only the target-shape call repaired.", "",
        ]),
        encoding="utf-8",
    )
    print(value["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
