#!/usr/bin/env python3
"""Attribute T185C's sole post-run metric-readback hold."""

from __future__ import annotations

import json
import math
from pathlib import Path
import subprocess
from typing import Any

from run_t136_static_calibration_router_transform import (
    ANALYSIS,
    ROOT,
    canonical_sha256,
    receipt,
)
import run_t20_support_trainthrough_one_update as t20
import run_t55_dynamic_single_support_cpu_contract as t55


SOURCE = ANALYSIS / "t185c_in_episode_single_support_cpu_result.json"
OUTPUT = ANALYSIS / "t185c_metric_readback_attribution_20260730.json"
MARKDOWN = ANALYSIS / "T185C_METRIC_READBACK_ATTRIBUTION_20260730.md"
BUILDER = Path(__file__).resolve()
SUPPORT_TAGS = (
    "eval/episode_reward/t185_single_support_balance",
    "eval/episode_reward/t185_left_support_match",
    "eval/episode_reward/t185_right_support_match",
)
OLD_PREFIX_TAG = "eval/episode_reward/t185/prefix_active"
ACTUAL_PREFIX_TAG = "eval/episode_t185/prefix_active"
ORIGINAL_REWARD_TAG = "eval/episode_t185/original_reward"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def canonical_without(value: dict[str, Any], field: str) -> str:
    basis = dict(value)
    basis.pop(field, None)
    return canonical_sha256(basis)


def finite_values(
    events: dict[str, list[dict[str, float | int]]],
    tag: str,
) -> list[float]:
    values = [float(row["value"]) for row in events.get(tag, [])]
    if not values or not all(math.isfinite(value) for value in values):
        return []
    return values


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite attribution: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T185C attribution requires clean worktree")

    source = load(SOURCE)
    source_hash_exact = (
        canonical_without(source, "result_sha256")
        == source["result_sha256"]
    )
    event_receipt = {
        "kind": "file",
        **source["training"]["event_file"],
    }
    t20.verify_receipt(event_receipt, "T185C event file")
    event_path = Path(event_receipt["path"])
    events = t55.all_scalar_events(event_path)
    support_values = {
        tag: finite_values(events, tag) for tag in SUPPORT_TAGS
    }
    prefix_values = finite_values(events, ACTUAL_PREFIX_TAG)
    original_values = finite_values(events, ORIGINAL_REWARD_TAG)
    checks = {
        "source_result_hash_exact": source_hash_exact,
        "source_status_and_only_hold_exact": (
            source["status"]
            == "HOLD_T185C_IN_EPISODE_SINGLE_SUPPORT_CPU_CONTRACT"
            and source["failed_checks"]
            == ["training_metrics_finite_and_prefix_exercised"]
        ),
        "all_substantive_source_checks_green": all(
            passed
            for name, passed in source["checks"].items()
            if name != "training_metrics_finite_and_prefix_exercised"
        ),
        "support_metrics_finite_positive_at_both_evaluations": all(
            len(values) == 2 and min(values) > 0.0
            for values in support_values.values()
        ),
        "requested_prefix_tag_absent": OLD_PREFIX_TAG not in events,
        "actual_terminal_prefix_tag_finite_zero": (
            len(prefix_values) == 2
            and all(value == 0.0 for value in prefix_values)
        ),
        "same_episode_original_reward_finite_positive": (
            len(original_values) == 2 and min(original_values) > 0.0
        ),
        "no_new_optimizer_behavior_hosted_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    basis: dict[str, Any] = {
        "schema_version": "open_duck.t185c_metric_readback_attribution.v1",
        "status": (
            "PASS_T185C_METRIC_READBACK_ATTRIBUTION"
            if not failed
            else "HOLD_T185C_METRIC_READBACK_ATTRIBUTION"
        ),
        "classification": (
            "POSTRUN_METRIC_NAMESPACE_AND_TERMINAL_STATE_CHECKER_MISMATCH"
        ),
        "source_result_sha256": source["result_sha256"],
        "sources": {
            "builder": receipt(BUILDER),
            "t185c_result": receipt(SOURCE),
            "event_file": event_receipt,
        },
        "observed": {
            "support_metric_values": support_values,
            "requested_prefix_tag": OLD_PREFIX_TAG,
            "requested_prefix_tag_present": OLD_PREFIX_TAG in events,
            "actual_prefix_tag": ACTUAL_PREFIX_TAG,
            "actual_prefix_values": prefix_values,
            "original_reward_tag": ORIGINAL_REWARD_TAG,
            "original_reward_values": original_values,
        },
        "interpretation": {
            "prefix_exposure": (
                "finite positive accumulated balance, left-support, and "
                "right-support metrics at both evaluations"
            ),
            "same_episode_resume": (
                "the actual non-reward prefix-active metric is terminal "
                "state and is zero after the 27-tick prefix"
            ),
            "scientific_contract_change": False,
            "optimizer_rerun_required": False,
        },
        "checks": checks,
        "failed_checks": failed,
        "decision": (
            "EARN_T185D_SAVED_ARTIFACT_METRIC_READBACK_RECOVERY_"
            "PREREGISTRATION_ONLY"
            if not failed
            else "CLOSE_T185C_METRIC_READBACK_ATTRIBUTION"
        ),
        "execution_now": {
            "simulator_transitions": 0,
            "optimizer_steps": 0,
            "formal_behavior_cells": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "t185d_preregistration": not failed,
            "artifact_reanalysis": False,
            "optimizer": False,
            "behavior_evaluation": False,
            "hosted_training": False,
            "deployment_audit": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    value = {**basis, "result_sha256": canonical_sha256(basis)}
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T185C metric-readback attribution\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Classification: `{value['classification']}`\n"
        f"- Failed checks: `{failed}`\n"
        f"- Requested tag present: `{OLD_PREFIX_TAG in events}`\n"
        f"- Actual terminal prefix values: `{prefix_values}`\n"
        "- Three prefix support metrics: finite and positive at both "
        "evaluations\n"
        "- New optimizer / behavior / hosted / robot: `0/0/0/0`\n"
        f"- Result SHA-256: `{value['result_sha256']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"failed_checks={failed}")
    print(f"decision={value['decision']}")
    print(f"result_sha256={value['result_sha256']}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
