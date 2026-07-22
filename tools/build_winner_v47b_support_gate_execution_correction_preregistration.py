#!/usr/bin/env python3
"""Preregister the provenance-adapter-only correction for failed V47."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = (
    ANALYSIS / "winner_v47b_support_gate_execution_correction_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "WINNER_V47B_SUPPORT_GATE_EXECUTION_CORRECTION_PREREGISTRATION_20260722.md"
)
ORIGINAL = (
    ANALYSIS / "winner_v47_static_target_teacher_support_gate_preregistration.json"
)
SOURCES = {
    "builder": Path(
        "tools/build_winner_v47b_support_gate_execution_correction_preregistration.py"
    ),
    "runner": Path("tools/run_winner_v47b_support_gate_execution_correction.py"),
    "runner_tests": Path(
        "tests/test_winner_v47b_support_gate_execution_correction.py"
    ),
    "preregistration_tests": Path(
        "tests/test_winner_v47b_support_gate_execution_correction_preregistration.py"
    ),
    "importer": Path(
        "tools/import_winner_v47b_support_gate_execution_correction_result.py"
    ),
    "importer_tests": Path(
        "tests/test_winner_v47b_support_gate_execution_correction_import.py"
    ),
    "workflow": Path(
        ".github/workflows/winner-v47b-support-gate-execution-correction.yml"
    ),
    "original_v47_preregistration": Path(
        "outputs/analysis/winner_v47_static_target_teacher_support_gate_preregistration.json"
    ),
    "original_v47_builder": Path(
        "tools/build_winner_v47_static_target_teacher_support_gate_preregistration.py"
    ),
    "original_v47_runner": Path(
        "tools/run_winner_v47_static_target_teacher_support_gate.py"
    ),
    "original_v47_importer": Path(
        "tools/import_winner_v47_static_target_teacher_support_gate_result.py"
    ),
    "base_gate_runner": Path("tools/run_winner_v12_calibrator_support_gate.py"),
    "base_full_training_preregistration": Path(
        "outputs/analysis/winner_v12_full_calibrator_training_preregistration.json"
    ),
    "calibrator_design_preregistration": Path(
        "outputs/analysis/winner_v12_calibrator_training_preregistration.json"
    ),
    "training_result": Path(
        "outputs/analysis/winner_v46_static_target_teacher_training_result.json"
    ),
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
        raise FileExistsError("refusing to overwrite Winner-v47b contract")
    original = json.loads(ORIGINAL.read_text(encoding="utf-8"))
    if (
        original.get("status")
        != "PREREGISTERED_WINNER_V47_STATIC_TARGET_TEACHER_SUPPORT_GATE"
        or original.get("decision")
        != "AUTHORIZE_ONE_FROZEN_WINNER_V47_248_CELL_GATE_ONLY"
        or original.get("future_frozen_support_gate", {}).get(
            "cells_per_checkpoint"
        )
        != 124
        or original.get("future_frozen_support_gate", {}).get("duration_ticks")
        != 250
        or original.get("pass_rule", {}).get("closest_checkpoint_selection")
        is not False
    ):
        raise ValueError("original Winner-v47 contract changed")
    sources = {
        name: {
            "path": path.as_posix(),
            "hash_mode": "lf",
            "sha256": lf_sha256(ROOT / path),
        }
        for name, path in SOURCES.items()
    }
    payload = {
        "schema_version": (
            "winner_v47b.support_gate_execution_correction_preregistration.v1"
        ),
        "status": "PREREGISTERED_WINNER_V47B_EXECUTION_CORRECTION",
        "decision": "AUTHORIZE_ONE_V47B_FIRST_ATTEMPT_ONLY",
        "failed_execution": {
            "github_run_id": 29914159165,
            "github_run_attempt": 1,
            "github_run_head_sha": "e47a9941eff7a5a5ce102b8fd8cb72488a71058a",
            "github_job_id": 88903940383,
            "job_conclusion": "failure",
            "artifact_count": 0,
            "formal_support_cells_executed": 0,
            "failure": "ValueError: calibrator-design provenance changed",
            "failed_before": "checkpoint loading and every formal cell loop",
            "preserved_log_sha256": (
                "db26d7477565dfa7d2eb20d4634bdd760bafc75cadf78f9dba931f3bb47ab1d5"
            ),
            "preserved_log_bytes": 54763,
        },
        "exact_correction": {
            "old_argument": (
                "Winner-v47 preregistration passed to load_calibrator_design"
            ),
            "old_source_key": "calibrator_design",
            "required_source_key": "calibrator_design_preregistration",
            "new_argument": "exact Winner-v12 full-training preregistration",
            "loader": "unchanged Winner-v12 load_calibrator_design",
            "gate_population_threshold_seed_checkpoint_or_policy_change": False,
        },
        "original_v47_contract_sha256": lf_sha256(ORIGINAL),
        "training_artifact": original["training_artifact"],
        "future_frozen_support_gate": original["future_frozen_support_gate"],
        "pass_rule": original["pass_rule"],
        "execution_now": {
            "formal_support_cells": 0,
            "heldout_repeat_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": original["authority"],
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
                "# Winner-v47b support-gate execution correction preregistration",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                "- Failed V47 run: `29914159165` (zero formal cells)",
                "- Correction: pass the exact Winner-v12 full-training preregistration to its unchanged calibrator-design provenance loader",
                "- Gate/checkpoints/population/thresholds/seeds/policy: unchanged",
                "- Formal cells now / locomotion / robot: `0 / 0 / 0`",
                "",
                "This authorizes one separately named first-attempt CPU execution only.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
