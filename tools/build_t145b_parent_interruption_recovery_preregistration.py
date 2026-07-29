#!/usr/bin/env python3
"""Freeze recovery from T145's parent-process interruption after 8 cells."""

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


T145 = ANALYSIS / "t145_conditional_path_negative_endpoint_preregistration.json"
OUTPUT = ANALYSIS / "t145b_parent_interruption_recovery_preregistration.json"
MARKDOWN = (
    ANALYSIS
    / "T145B_PARENT_INTERRUPTION_RECOVERY_PREREGISTRATION_20260729.md"
)
BUILDER = Path(__file__).resolve()
WRAPPER = ROOT / "tools" / "run_t145b_parent_interruption_recovery.py"
FIXED_RUNNER = ROOT / "tools" / "run_t145_conditional_path_negative_endpoint.py"
TEST = ROOT / "tests" / "test_t145b_parent_interruption_recovery.py"
CACHE = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t145_conditional_path_negative_endpoint_v1"
)


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T145B: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T145B preregistration requires clean worktree")
    source = json.loads(T145.read_text(encoding="utf-8"))
    manifests = sorted(CACHE.rglob("manifest.json"))
    evaluations = sorted(CACHE.rglob("evaluation.json"))
    completed_cells = 4 * len(manifests)
    source_inputs = dict(source["frozen_inputs"])
    obsolete_runner = source_inputs["runner"]
    source_inputs["runner"] = receipt(FIXED_RUNNER)
    source_inputs.update(
        {
            "recovery_builder": receipt(BUILDER),
            "recovery_wrapper": receipt(WRAPPER),
            "recovery_test": receipt(TEST),
            "source_t145_preregistration": receipt(T145),
            **{
                f"partial_manifest_{index}": receipt(path)
                for index, path in enumerate(manifests)
            },
            **{
                f"partial_evaluation_{index}": receipt(path)
                for index, path in enumerate(evaluations)
            },
        }
    )
    checks = {
        "source_t145_preregistered": (
            source["status"]
            == "PREREGISTERED_T145_CONDITIONAL_PATH_NEGATIVE_ENDPOINT_MATRIX"
        ),
        "source_result_absent": not (
            ANALYSIS / "t145_conditional_path_negative_endpoint_result.json"
        ).exists(),
        "exactly_two_complete_blocks": (
            len(manifests) == 2
            and len(evaluations) == 2
            and completed_cells == 8
        ),
        "partial_blocks_are_half_both_fits": (
            {path.parent.name for path in manifests} == {"p30", "p31_34"}
            and all("T143C_CONDITIONAL_PATH_HALF" in str(path) for path in manifests)
        ),
        "primary_runner_updated_only_for_resume": (
            obsolete_runner != source_inputs["runner"]
            and "ALLOW_EXISTING_CACHE = False"
            in FIXED_RUNNER.read_text(encoding="utf-8")
        ),
        "no_optimizer_colab_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T145B preregistration checks failed: {failed}")
    value: dict[str, Any] = {
        **{
            key: item
            for key, item in source.items()
            if key
            not in {
                "preregistered_contract_sha256",
                "frozen_inputs",
                "checks",
                "failed_checks",
            }
        },
        "schema_version": (
            "open_duck.t145b_parent_interruption_recovery_"
            "preregistration.v1"
        ),
        "recovery_kind": "T145_PARENT_INTERRUPTED_AFTER_TWO_BLOCKS",
        "source_t145_contract_sha256": source[
            "preregistered_contract_sha256"
        ],
        "frozen_inputs": source_inputs,
        "checks": checks,
        "failed_checks": failed,
        "execution_now": {
            "source_completed_behavior_cells": completed_cells,
            "recovery_cached_behavior_cells": completed_cells,
            "recovery_remaining_behavior_cells": 16 - completed_cells,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
    }
    value["preregistered_contract_sha256"] = canonical_sha256(value)
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T145B parent-interruption recovery preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Preserved complete blocks: half checkpoint, both fits (`8 cells`)\n"
        "- Recovery resumes the same cache for the final checkpoint (`8 cells`)\n"
        "- Policy, condition, thresholds, and decision rule are unchanged\n"
        "- Optimizer / Colab / robot: `0/0/0`\n",
        encoding="utf-8",
        newline="\n",
    )
    print("PREREGISTERED_T145B_PARENT_INTERRUPTION_RECOVERY")
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
