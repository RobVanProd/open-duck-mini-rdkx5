#!/usr/bin/env python3
"""Preregister T185D's saved-artifact metric-readback recovery."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
from typing import Any

from run_t136_static_calibration_router_transform import (
    ANALYSIS,
    ROOT,
    canonical_sha256,
    receipt,
)


SOURCE = ANALYSIS / "t185c_in_episode_single_support_cpu_result.json"
ATTRIBUTION = ANALYSIS / "t185c_metric_readback_attribution_20260730.json"
OUTPUT = (
    ANALYSIS
    / "t185d_metric_readback_recovery_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "T185D_METRIC_READBACK_RECOVERY_PREREGISTRATION_20260730.md"
)
BUILDER = Path(__file__).resolve()
RUNNER = ROOT / "tools" / "run_t185d_metric_readback_recovery.py"


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
            raise FileExistsError(f"refusing to overwrite T185D: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T185D preregistration requires clean worktree")
    source = load(SOURCE)
    attribution = load(ATTRIBUTION)
    if (
        canonical_without(source, "result_sha256")
        != source["result_sha256"]
        or canonical_without(attribution, "result_sha256")
        != attribution["result_sha256"]
        or attribution["source_result_sha256"] != source["result_sha256"]
        or attribution["status"]
        != "PASS_T185C_METRIC_READBACK_ATTRIBUTION"
        or attribution["failed_checks"]
    ):
        raise RuntimeError("T185D source attribution identity changed")

    basis: dict[str, Any] = {
        "schema_version": (
            "open_duck.t185d_metric_readback_recovery_"
            "preregistration.v1"
        ),
        "status": "PREREGISTERED_T185D_METRIC_READBACK_RECOVERY",
        "question": (
            "Does the frozen T185C event artifact satisfy the intended "
            "prefix-exposure and same-episode-resume metric contract when "
            "read using the metric namespaces actually emitted by the "
            "training driver?"
        ),
        "sources": {
            "builder": receipt(BUILDER),
            "runner": receipt(RUNNER),
            "t185c_result": receipt(SOURCE),
            "t185c_attribution": receipt(ATTRIBUTION),
            "event_file": {
                "kind": "file",
                **source["training"]["event_file"],
            },
        },
        "saved_artifact_contract": {
            "support_tags": [
                "eval/episode_reward/t185_single_support_balance",
                "eval/episode_reward/t185_left_support_match",
                "eval/episode_reward/t185_right_support_match",
            ],
            "support_tag_rule": (
                "exactly two finite values per tag and every value > 0"
            ),
            "terminal_prefix_tag": "eval/episode_t185/prefix_active",
            "terminal_prefix_rule": (
                "exactly two finite values and every value == 0"
            ),
            "same_episode_reward_tag": "eval/episode_t185/original_reward",
            "same_episode_reward_rule": (
                "exactly two finite values and every value > 0"
            ),
            "incorrect_tag_must_be_absent": (
                "eval/episode_reward/t185/prefix_active"
            ),
            "all_other_t185c_checks_must_remain_true": True,
        },
        "recovery_contract": {
            "new_simulator_execution": False,
            "new_optimizer_execution": False,
            "new_model_inference": False,
            "new_behavior_evaluation": False,
            "event_artifact_immutable": True,
            "scientific_contract_change": False,
            "only_change": (
                "replace the nonexistent positive prefix-active readback "
                "with positive accumulated support metrics plus an exact "
                "zero terminal prefix-active state and positive resumed "
                "original reward"
            ),
        },
        "decision_rule": {
            "pass": (
                "EARN_T186_IN_EPISODE_SINGLE_SUPPORT_HOSTED_"
                "PREREGISTRATION_ONLY"
            ),
            "fail": (
                "CLOSE_T185_IN_EPISODE_SINGLE_SUPPORT_PREFIX_AND_RETURN_"
                "TO_MECHANISM_SELECTION"
            ),
            "no_optimizer_retry": True,
        },
        "execution_now": {
            "saved_event_files": 0,
            "simulator_transitions": 0,
            "optimizer_steps": 0,
            "formal_behavior_cells": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "execute_one_saved_artifact_recovery": True,
            "optimizer": False,
            "behavior_evaluation": False,
            "hosted_preregistration": False,
            "hosted_training": False,
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
        "# T185D metric-readback recovery preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Contract SHA-256: `{value['preregistered_contract_sha256']}`\n"
        "- Input: the immutable T185C event artifact\n"
        "- New simulator / optimizer / behavior / hosted / robot: "
        "`0/0/0/0/0`\n"
        "- Pass earns T186 hosted preregistration only; not training\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
