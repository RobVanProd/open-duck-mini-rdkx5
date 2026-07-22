#!/usr/bin/env python3
"""Apply the preregistered V47 provenance adapter, then run the same gate."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path
import sys
from typing import Any, Mapping

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
ANALYSIS = ROOT / "outputs/analysis"
sys.path.insert(0, str(TOOLS))

PREREGISTRATION = (
    ANALYSIS / "winner_v47b_support_gate_execution_correction_preregistration.json"
)
ORIGINAL_PREREGISTRATION = (
    ANALYSIS / "winner_v47_static_target_teacher_support_gate_preregistration.json"
)
BASE_PREREGISTRATION = (
    ANALYSIS / "winner_v12_full_calibrator_training_preregistration.json"
)
ORIGINAL_RUNNER = ROOT / "tools/run_winner_v47_static_target_teacher_support_gate.py"
ORIGINAL_IMPORTER = (
    ROOT / "tools/import_winner_v47_static_target_teacher_support_gate_result.py"
)
BASE_RUNNER = ROOT / "tools/run_winner_v12_calibrator_support_gate.py"


def lf_sha256(path: Path) -> str:
    import hashlib

    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def _load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def correction_sources() -> dict[str, str]:
    return {
        "correction_preregistration_lf_sha256": lf_sha256(PREREGISTRATION),
        "correction_runner_lf_sha256": lf_sha256(Path(__file__)),
        "original_v47_preregistration_lf_sha256": lf_sha256(
            ORIGINAL_PREREGISTRATION
        ),
        "original_v47_runner_lf_sha256": lf_sha256(ORIGINAL_RUNNER),
        "original_v47_importer_lf_sha256": lf_sha256(ORIGINAL_IMPORTER),
        "base_full_training_preregistration_lf_sha256": lf_sha256(
            BASE_PREREGISTRATION
        ),
        "base_gate_runner_lf_sha256": lf_sha256(BASE_RUNNER),
    }


def validate_preregistration(value: Mapping[str, Any]) -> None:
    original = json.loads(ORIGINAL_PREREGISTRATION.read_text(encoding="utf-8"))
    if (
        value.get("schema_version")
        != "winner_v47b.support_gate_execution_correction_preregistration.v1"
        or value.get("status")
        != "PREREGISTERED_WINNER_V47B_EXECUTION_CORRECTION"
        or value.get("decision") != "AUTHORIZE_ONE_V47B_FIRST_ATTEMPT_ONLY"
        or value.get("original_v47_contract_sha256")
        != lf_sha256(ORIGINAL_PREREGISTRATION)
        or value.get("training_artifact") != original.get("training_artifact")
        or value.get("future_frozen_support_gate")
        != original.get("future_frozen_support_gate")
        or value.get("pass_rule") != original.get("pass_rule")
        or value.get("execution_now")
        != {
            "formal_support_cells": 0,
            "heldout_repeat_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        }
        or value.get("authority")
        != {
            "robot_clearance": False,
            "response_conditioned_locomotion_training_authorized": False,
            "pass_authorizes_only": (
                "a separate response-conditioned locomotion-training preregistration"
            ),
        }
    ):
        raise ValueError("Winner-v47b correction contract changed")
    failure = value.get("failed_execution", {})
    if failure != {
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
    }:
        raise ValueError("Winner-v47b failed-run attribution changed")
    if value.get("exact_correction") != {
        "old_argument": "Winner-v47 preregistration passed to load_calibrator_design",
        "old_source_key": "calibrator_design",
        "required_source_key": "calibrator_design_preregistration",
        "new_argument": "exact Winner-v12 full-training preregistration",
        "loader": "unchanged Winner-v12 load_calibrator_design",
        "gate_population_threshold_seed_checkpoint_or_policy_change": False,
    }:
        raise ValueError("Winner-v47b correction scope changed")


def _adapt_to_v47(value: Mapping[str, Any]) -> dict[str, Any]:
    status = value.get("status")
    mapping = {
        "PASS_WINNER_V47B_SUPPORT_GATE_EXECUTION_CORRECTION": (
            "PASS_WINNER_V47_STATIC_TARGET_TEACHER_SUPPORT_GATE"
        ),
        "HOLD_WINNER_V47B_SUPPORT_GATE_EXECUTION_CORRECTION": (
            "HOLD_WINNER_V47_STATIC_TARGET_TEACHER_SUPPORT_GATE"
        ),
    }
    if status not in mapping:
        raise ValueError("Winner-v47b result status changed")
    fields = {
        "authority",
        "checkpoint_results",
        "checks",
        "decision",
        "execution",
        "failed_checks",
    }
    adapted = {name: value[name] for name in fields}
    adapted["schema_version"] = (
        "winner_v47.static_target_teacher_support_gate_result.v1"
    )
    adapted["status"] = mapping[status]
    adapted["sources"] = value["reviewed_v47_sources"]
    return adapted


def validate_corrected_result(value: Mapping[str, Any]) -> None:
    preregistration = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    expected_fields = {
        "authority",
        "checkpoint_results",
        "checks",
        "correction_sources",
        "decision",
        "execution",
        "execution_correction",
        "failed_checks",
        "reviewed_v47_sources",
        "schema_version",
        "status",
    }
    if (
        set(value) != expected_fields
        or value.get("schema_version")
        != "winner_v47b.support_gate_execution_correction_result.v1"
        or value.get("execution_correction")
        != preregistration.get("exact_correction")
        or value.get("correction_sources") != correction_sources()
    ):
        raise ValueError("Winner-v47b corrected result schema changed")
    original_importer = _load_module("winner_v47b_original_importer", ORIGINAL_IMPORTER)
    original_importer.validate_result(_adapt_to_v47(value))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--training-work-root", type=Path, required=True)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--canonical-fit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--offline-cpu-only", action="store_true")
    parser.add_argument("--formal-gate-authorized", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if not args.offline_cpu_only or not args.formal_gate_authorized:
        raise PermissionError(
            "Winner-v47b requires --offline-cpu-only --formal-gate-authorized"
        )
    if args.output.exists():
        raise FileExistsError(args.output)
    preregistration = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    validate_preregistration(preregistration)

    base_gate = _load_module("winner_v47b_base_gate", BASE_RUNNER)
    original_loader = base_gate.load_calibrator_design

    def corrected_loader(_incorrect_preregistration: Mapping[str, Any]) -> dict[str, Any]:
        reviewed = json.loads(BASE_PREREGISTRATION.read_text(encoding="utf-8"))
        return original_loader(reviewed)

    sys.modules["run_winner_v12_calibrator_support_gate"] = base_gate
    v47 = _load_module("winner_v47b_original_runner", ORIGINAL_RUNNER)
    base_gate.load_calibrator_design = corrected_loader
    try:
        return_code = v47.main()
    finally:
        base_gate.load_calibrator_design = original_loader
    reviewed = json.loads(args.output.read_text(encoding="utf-8"))
    original_importer = _load_module("winner_v47b_original_result", ORIGINAL_IMPORTER)
    original_importer.validate_result(reviewed)
    original_status = reviewed["status"]
    reviewed_sources = reviewed.pop("sources")
    reviewed["schema_version"] = (
        "winner_v47b.support_gate_execution_correction_result.v1"
    )
    reviewed["status"] = (
        "PASS_WINNER_V47B_SUPPORT_GATE_EXECUTION_CORRECTION"
        if original_status == "PASS_WINNER_V47_STATIC_TARGET_TEACHER_SUPPORT_GATE"
        else "HOLD_WINNER_V47B_SUPPORT_GATE_EXECUTION_CORRECTION"
    )
    reviewed["reviewed_v47_sources"] = reviewed_sources
    reviewed["execution_correction"] = preregistration["exact_correction"]
    reviewed["correction_sources"] = correction_sources()
    validate_corrected_result(reviewed)
    args.output.write_text(
        json.dumps(reviewed, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(reviewed["status"])
    return return_code


if __name__ == "__main__":
    raise SystemExit(main())
