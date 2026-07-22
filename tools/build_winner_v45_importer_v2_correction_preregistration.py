#!/usr/bin/env python3
"""Freeze the reporting-only Winner-v45 importer-v2 correction."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v45_importer_v2_correction_preregistration.json"
MARKDOWN = ANALYSIS / "WINNER_V45_IMPORTER_V2_CORRECTION_PREREGISTRATION_20260722.md"
SOURCES = {
    "builder": Path("tools/build_winner_v45_importer_v2_correction_preregistration.py"),
    "corrected_importer": Path("tools/import_winner_v45_static_target_teacher_one_update_cpu_result_v2.py"),
    "corrected_importer_tests": Path("tests/test_winner_v45_importer_v2_correction.py"),
    "frozen_v1_importer": Path("tools/import_winner_v45_static_target_teacher_one_update_cpu_result.py"),
    "winner_v45_contract": Path("outputs/analysis/winner_v45_static_target_teacher_one_update_cpu_contract.json"),
    "winner_v45_workflow": Path(".github/workflows/winner-v45-static-target-teacher-one-update-cpu.yml"),
}


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    if args.output.exists() or args.markdown.exists():
        raise FileExistsError("refusing to overwrite Winner-v45 importer correction")
    sources = {
        name: {"path": path.as_posix(), "hash_mode": "lf", "sha256": lf_sha256(ROOT / path)}
        for name, path in SOURCES.items()
    }
    value = {
        "schema_version": "winner_v45.importer_v2_correction_preregistration.v1",
        "status": "PREREGISTERED_WINNER_V45_IMPORTER_V2_REPORTING_FIX",
        "decision": "AUTHORIZE_ONE_IMPORT_OF_SAME_IMMUTABLE_V45_ARTIFACT_ONLY",
        "failure": {
            "classification": "POST_VALIDATION_MARKDOWN_LOCAL_VARIABLE_NAME_ERROR",
            "exception": "NameError: name 'before' is not defined",
            "location": "frozen v1 importer Markdown rendering after raw and attributed validate_result passes",
            "artifact_or_proof_invalidated": False,
        },
        "allowed_change": "bind teacher_loss_before/after from the already validated raw result before Markdown rendering",
        "forbidden_changes": [
            "workflow rerun", "optimizer update", "artifact mutation", "validation weakening",
            "source-result mutation", "formal support gate", "continuation training", "robot access",
        ],
        "artifact": {
            "run_id": 29907921832,
            "run_attempt": 1,
            "run_head_sha": "501e3b0f2295e2bf0d45252ed15300958d3883fc",
            "artifact_id": 8524663581,
            "artifact_name": "winner-v45-static-target-teacher-one-update-29907921832",
            "artifact_digest": "sha256:5ff180cdd05eb00b77c136b0ac2747896cf77043dafb980a5fd661ce665523aa",
            "artifact_zip_bytes": 247738,
        },
        "execution_now": {
            "workflow_runs": 0, "optimizer_updates": 0, "formal_support_cells": 0,
            "continuation_training_updates": 0, "robot_or_rdk_access": 0,
        },
        "sources": sources,
        "source_manifest_sha256": canonical_sha256(sources),
        "authority": {
            "robot_clearance": False,
            "pass_authorizes_only": "import the already produced immutable Winner-v45 artifact once",
        },
    }
    args.output.write_text(json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.markdown.write_text("\n".join([
        "# Winner-v45 importer-v2 correction preregistration", "",
        f"- Status: `{value['status']}`", f"- Decision: `{value['decision']}`",
        "- Failure: `post-validation Markdown local-variable NameError`",
        "- Allowed change: bind the two already validated loss values before rendering",
        "- Workflow rerun / optimizer update / support / training / robot: `0 / 0 / 0 / 0 / 0`", "",
        "The original artifact and frozen v1 importer remain unchanged.", "",
    ]), encoding="utf-8")
    print(value["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

