#!/usr/bin/env python3
"""Run T193B's immutable-event metric namespace recovery."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
ANALYSIS = ROOT / "outputs" / "analysis"
sys.path.insert(0, str(TOOLS))

import run_t20_support_trainthrough_one_update as t20  # noqa: E402
import run_t55_dynamic_single_support_cpu_contract as t55  # noqa: E402


PREREG = (
    ANALYSIS / "t193b_metric_namespace_recovery_preregistration.json"
)
RESULT = ANALYSIS / "t193b_metric_namespace_recovery_result.json"
MARKDOWN = (
    ANALYSIS / "T193B_METRIC_NAMESPACE_RECOVERY_RESULT_20260730.md"
)


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def canonical_without(value: dict[str, Any], field: str) -> str:
    basis = dict(value)
    basis.pop(field, None)
    return t20.canonical_sha256(basis)


def finite_values(
    events: dict[str, list[dict[str, float | int]]],
    tag: str,
) -> list[float]:
    values = [float(row["value"]) for row in events.get(tag, [])]
    if not values or not all(math.isfinite(value) for value in values):
        return []
    return values


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--saved-artifact-authorized", action="store_true")
    args = parser.parse_args()
    if not args.saved_artifact_authorized:
        raise PermissionError(
            "T193B requires --saved-artifact-authorized"
        )
    for path in (RESULT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T193B: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("formal T193B execution requires clean worktree")

    prereg = load(PREREG)
    if (
        prereg.get("status")
        != "PREREGISTERED_T193B_METRIC_NAMESPACE_RECOVERY"
        or prereg.get("failed_checks")
        or canonical_without(
            prereg, "preregistered_contract_sha256"
        )
        != prereg.get("preregistered_contract_sha256")
    ):
        raise RuntimeError("T193B preregistration identity changed")
    for name, item in prereg["sources"].items():
        t20.verify_receipt(item, name)
    source = load(Path(prereg["sources"]["t193_result"]["path"]))
    events = t55.all_scalar_events(
        Path(prereg["sources"]["event_file"]["path"])
    )
    contract = prereg["saved_artifact_contract"]
    support_values = {
        tag: finite_values(events, tag)
        for tag in contract["support_tags"]
    }
    reference_values = {
        tag: finite_values(events, tag)
        for tag in contract["reference_tags"]
    }
    original_values = finite_values(
        events, contract["original_reward_tag"]
    )
    rows = int(contract["required_rows_per_tag"])
    minimum = float(contract["required_minimum_value_exclusive"])
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
        "source_only_metric_readback_held": (
            source["failed_checks"]
            == ["training_metrics_finite_and_bilateral"]
        ),
        "all_other_t193_checks_true": all(substantive.values()),
        "support_metrics_finite_positive_both_evaluations": all(
            len(values) == rows and min(values) > minimum
            for values in support_values.values()
        ),
        "reference_metrics_finite_positive_both_evaluations": all(
            len(values) == rows and min(values) > minimum
            for values in reference_values.values()
        ),
        "original_reward_finite_positive_both_evaluations": (
            len(original_values) == rows
            and min(original_values) > minimum
        ),
        "incorrect_metric_namespaces_absent": all(
            tag not in events
            for tag in contract["incorrect_tags_must_be_absent"]
        ),
        "no_new_simulator_optimizer_inference_behavior_hosted_or_robot": (
            True
        ),
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    passed = not failed
    basis: dict[str, Any] = {
        "schema_version": (
            "open_duck.t193b_metric_namespace_recovery_result.v1"
        ),
        "status": (
            "PASS_T193B_METRIC_NAMESPACE_RECOVERY"
            if passed
            else "HOLD_T193B_METRIC_NAMESPACE_RECOVERY"
        ),
        "classification": (
            "T193_CPU_HOLD_WAS_REPORTING_NAMESPACE_ONLY"
            if passed
            else "T193_BILATERAL_METRIC_CONTRACT_NOT_RECOVERED"
        ),
        "decision": (
            prereg["decision_rule"]["pass"]
            if passed
            else prereg["decision_rule"]["fail"]
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "source_result_sha256": source["result_sha256"],
        "observed": {
            "support_metric_values": support_values,
            "reference_metric_values": reference_values,
            "original_reward_values": original_values,
            "event_scalar_tag_count": len(events),
            "event_scalar_row_count": sum(
                len(values) for values in events.values()
            ),
        },
        "preserved_t193_checks": substantive,
        "checks": checks,
        "failed_checks": failed,
        "execution_now": {
            "saved_event_files": 1,
            "simulator_transitions": 0,
            "optimizer_steps": 0,
            "model_inference_rows": 0,
            "formal_behavior_cells": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "hosted_preregistration": passed,
            "hosted_training": False,
            "behavior_evaluation": False,
            "policy_promotion": False,
            "deployment_audit": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    value = {**basis, "result_sha256": t20.canonical_sha256(basis)}
    RESULT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T193B metric namespace recovery result\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Classification: `{value['classification']}`\n"
        f"- Decision: `{value['decision']}`\n"
        f"- Failed checks: `{failed}`\n"
        "- New simulator / optimizer / inference / behavior / hosted / "
        "robot: `0/0/0/0/0/0`\n"
        f"- Result SHA-256: `{value['result_sha256']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"classification={value['classification']}")
    print(f"decision={value['decision']}")
    print(f"failed_checks={failed}")
    print(f"result_sha256={value['result_sha256']}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
