#!/usr/bin/env python3
"""Preregister T193B's immutable-event metric namespace recovery."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
SOURCE_RESULT = (
    ANALYSIS
    / "t193_corrected_dynamic_reference_support_cpu_result.json"
)
OUTPUT = (
    ANALYSIS / "t193b_metric_namespace_recovery_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "T193B_METRIC_NAMESPACE_RECOVERY_PREREGISTRATION_20260730.md"
)
BUILDER = Path(__file__).resolve()
RUNNER = ROOT / "tools/run_t193b_metric_namespace_recovery.py"
TEST = ROOT / "tests/test_t193_corrected_dynamic_reference_support.py"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def file_receipt(path: Path) -> dict[str, Any]:
    return {
        "kind": "file",
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def canonical_without(value: dict[str, Any], field: str) -> str:
    basis = dict(value)
    basis.pop(field, None)
    return canonical_sha256(basis)


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T193B: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T193B preregistration requires clean worktree")
    for path in (SOURCE_RESULT, BUILDER, RUNNER, TEST):
        if not path.is_file():
            raise FileNotFoundError(path)
    source = load(SOURCE_RESULT)
    event_receipt = source["training"]["event_file"]
    event_path = Path(event_receipt["path"])
    substantive = {
        name: passed
        for name, passed in source["checks"].items()
        if name != "training_metrics_finite_and_bilateral"
    }
    checks = {
        "source_result_hash_exact": (
            canonical_without(source, "result_sha256")
            == source["result_sha256"]
        ),
        "source_held_only_on_metric_readback": (
            source["failed_checks"]
            == ["training_metrics_finite_and_bilateral"]
        ),
        "all_substantive_cpu_checks_green": all(substantive.values()),
        "event_file_receipt_exact": (
            event_path.is_file()
            and event_path.stat().st_size == event_receipt["bytes"]
            and sha256(event_path) == event_receipt["sha256"]
        ),
        "no_optimizer_retry": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    basis: dict[str, Any] = {
        "schema_version": (
            "open_duck.t193b_metric_namespace_recovery_"
            "preregistration.v1"
        ),
        "status": "PREREGISTERED_T193B_METRIC_NAMESPACE_RECOVERY",
        "question": (
            "Does the immutable T193 event file satisfy the intended "
            "bilateral support and reference-exposure contract when the "
            "training driver's emitted metric namespaces are read exactly?"
        ),
        "saved_artifact_contract": {
            "support_tags": [
                "eval/episode_reward/t193_reference_support_balance",
                "eval/episode_reward/t193_left_support_match",
                "eval/episode_reward/t193_right_support_match",
            ],
            "reference_tags": [
                "eval/episode_t193/reference_left_requested",
                "eval/episode_t193/reference_right_requested",
                "eval/episode_t193/reference_single_support_requested",
            ],
            "original_reward_tag": "eval/episode_t193/original_reward",
            "required_rows_per_tag": 2,
            "required_minimum_value_exclusive": 0.0,
            "incorrect_tags_must_be_absent": [
                "eval/episode_reward/t193/reference_left_requested",
                "eval/episode_reward/t193/reference_right_requested",
            ],
            "all_other_t193_checks_must_remain_true": True,
        },
        "recovery_contract": {
            "only_change": (
                "read environment metrics from eval/episode_t193/* rather "
                "than the nonexistent eval/episode_reward/t193/* namespace"
            ),
            "scientific_contract_change": False,
            "event_artifact_immutable": True,
            "new_simulator_execution": False,
            "new_optimizer_execution": False,
            "new_model_inference": False,
            "new_behavior_evaluation": False,
        },
        "sources": {
            "builder": file_receipt(BUILDER),
            "runner": file_receipt(RUNNER),
            "test": file_receipt(TEST),
            "t193_result": file_receipt(SOURCE_RESULT),
            "event_file": file_receipt(event_path),
        },
        "preserved_t193_checks": substantive,
        "checks": checks,
        "failed_checks": failed,
        "decision_rule": {
            "pass": (
                "EARN_T194_CORRECTED_DYNAMIC_REFERENCE_SUPPORT_HOSTED_"
                "PREREGISTRATION_ONLY"
            ),
            "fail": (
                "CLOSE_T193_CORRECTED_DYNAMIC_REFERENCE_SUPPORT_AND_"
                "RETURN_TO_MECHANISM_SELECTION"
            ),
            "no_optimizer_retry": True,
        },
        "execution_now": {
            "saved_event_files": 0,
            "simulator_transitions": 0,
            "optimizer_steps": 0,
            "model_inference_rows": 0,
            "formal_behavior_cells": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "execute_one_saved_artifact_recovery": not failed,
            "hosted_preregistration": False,
            "hosted_training": False,
            "optimizer": False,
            "behavior_evaluation": False,
            "policy_promotion": False,
            "deployment_audit": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    value = {
        **basis,
        "preregistered_contract_sha256": canonical_sha256(basis),
    }
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T193B metric namespace recovery preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Contract SHA-256: `{value['preregistered_contract_sha256']}`\n"
        "- Only change: read the immutable event file's emitted "
        "`eval/episode_t193/*` environment namespace\n"
        "- New simulator / optimizer / inference / behavior / hosted / "
        "robot: `0/0/0/0/0/0`\n"
        f"- Failed checks: `{failed}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"failed_checks={failed}")
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
