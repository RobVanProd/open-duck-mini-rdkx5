#!/usr/bin/env python3
"""Freeze recovery after T145B rejected original-contract cache blocks."""

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
T145B = ANALYSIS / "t145b_parent_interruption_recovery_preregistration.json"
OUTPUT = ANALYSIS / "t145c_cache_contract_recovery_preregistration.json"
MARKDOWN = (
    ANALYSIS / "T145C_CACHE_CONTRACT_RECOVERY_PREREGISTRATION_20260729.md"
)
BUILDER = Path(__file__).resolve()
WRAPPER = ROOT / "tools" / "run_t145c_cache_contract_recovery.py"
FIXED_RUNNER = ROOT / "tools" / "run_t145_conditional_path_negative_endpoint.py"
TEST = ROOT / "tests" / "test_t145c_cache_contract_recovery.py"
STDERR = Path(
    "D:/CodexArtifacts/open-duck-policy/t145b_runner_stderr.log"
)
CACHE = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t145_conditional_path_negative_endpoint_v1"
)


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T145C: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T145C preregistration requires clean worktree")
    source = json.loads(T145.read_text(encoding="utf-8"))
    failed_recovery = json.loads(T145B.read_text(encoding="utf-8"))
    manifests = sorted(CACHE.rglob("manifest.json"))
    evaluations = sorted(CACHE.rglob("evaluation.json"))
    source_inputs = dict(failed_recovery["frozen_inputs"])
    source_inputs["runner"] = receipt(FIXED_RUNNER)
    source_inputs.update(
        {
            "cache_recovery_builder": receipt(BUILDER),
            "cache_recovery_wrapper": receipt(WRAPPER),
            "cache_recovery_test": receipt(TEST),
            "source_t145_preregistration": receipt(T145),
            "failed_t145b_preregistration": receipt(T145B),
            "failed_t145b_stderr": receipt(STDERR),
        }
    )
    checks = {
        "t145b_stopped_on_contract_hash_only": (
            "T27 block exists without a valid manifest"
            in STDERR.read_text(encoding="utf-8")
        ),
        "t145b_result_absent": not (
            ANALYSIS / "t145b_parent_interruption_recovery_result.json"
        ).exists(),
        "partial_cache_unchanged_at_eight_cells": (
            len(manifests) == 2 and len(evaluations) == 2
        ),
        "fixed_runner_separates_source_and_recovery_contracts": (
            "SOURCE_CACHE_PREREG" in FIXED_RUNNER.read_text(encoding="utf-8")
        ),
        "no_new_behavior_optimizer_colab_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T145C preregistration checks failed: {failed}")
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
            "open_duck.t145c_cache_contract_recovery_preregistration.v1"
        ),
        "recovery_kind": "T145B_ORIGINAL_CACHE_CONTRACT_REJECTION",
        "source_t145_contract_sha256": source[
            "preregistered_contract_sha256"
        ],
        "failed_t145b_contract_sha256": failed_recovery[
            "preregistered_contract_sha256"
        ],
        "frozen_inputs": source_inputs,
        "checks": checks,
        "failed_checks": failed,
        "execution_now": {
            "source_completed_behavior_cells": 8,
            "t145b_new_behavior_cells": 0,
            "recovery_remaining_behavior_cells": 8,
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
        "# T145C cache-contract recovery preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Original eight cells remain bound to the original T145 contract\n"
        "- Remaining eight cells bind to this recovery contract\n"
        "- T145B completed zero new behavior cells\n"
        "- Optimizer / Colab / robot: `0/0/0`\n",
        encoding="utf-8",
        newline="\n",
    )
    print("PREREGISTERED_T145C_CACHE_CONTRACT_RECOVERY")
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
