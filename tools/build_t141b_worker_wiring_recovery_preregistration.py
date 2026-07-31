#!/usr/bin/env python3
"""Freeze recovery from T141's zero-cell worker-wiring failure."""

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


T141 = ANALYSIS / "t141_expert_bank_negative_endpoint_preregistration.json"
BASIS = ANALYSIS / "t103_t100c_negative_endpoint_preregistration.json"
OUTPUT = ANALYSIS / "t141b_worker_wiring_recovery_preregistration.json"
MARKDOWN = (
    ANALYSIS / "T141B_WORKER_WIRING_RECOVERY_PREREGISTRATION_20260729.md"
)
BUILDER = Path(__file__).resolve()
RUNNER = ROOT / "tools" / "run_t141b_worker_wiring_recovery.py"
TEST = ROOT / "tests" / "test_t141b_worker_wiring_recovery.py"
CRASH_STDERR = Path(
    "D:/CodexArtifacts/open-duck-policy/t141_runner_stderr.log"
)
OLD_CACHE = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t141_expert_bank_negative_endpoint_v1"
)


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T141B: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T141B preregistration requires clean worktree")
    source = json.loads(T141.read_text(encoding="utf-8"))
    basis = json.loads(BASIS.read_text(encoding="utf-8"))
    old_files = (
        list(OLD_CACHE.rglob("*")) if OLD_CACHE.exists() else []
    )
    completed_files = [
        path
        for path in old_files
        if path.is_file()
        and (
            path.name == "manifest.json"
            or path.suffix in {".jsonl", ".json"}
        )
    ]
    frozen_inputs = {
        **source["frozen_inputs"],
        "recovery_builder": receipt(BUILDER),
        "recovery_runner": receipt(RUNNER),
        "recovery_test": receipt(TEST),
        "source_t141_preregistration": receipt(T141),
        "crash_stderr": receipt(CRASH_STDERR),
    }
    checks = {
        "source_t141_preregistered": (
            source["status"]
            == "PREREGISTERED_T141_EXPERT_BANK_NEGATIVE_ENDPOINT_MATRIX"
        ),
        "source_result_absent": not (
            ANALYSIS / "t141_expert_bank_negative_endpoint_result.json"
        ).exists(),
        "old_cache_has_zero_completed_behavior_files": not completed_files,
        "crash_is_missing_repository_inputs_only": (
            "KeyError: 'repository_inputs'"
            in CRASH_STDERR.read_text(encoding="utf-8")
        ),
        "basis_repository_inputs_present": all(
            Path(item["path"]).is_file()
            for item in basis["repository_inputs"].values()
        ),
        "fresh_recovery_cache_absent": not Path(
            "D:/CodexArtifacts/open-duck-policy/"
            "t141b_expert_bank_negative_endpoint_v1"
        ).exists(),
        "no_behavior_training_colab_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T141B preregistration checks failed: {failed}")
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
            "open_duck.t141b_worker_wiring_recovery_"
            "preregistration.v1"
        ),
        "recovery_kind": (
            "T141_PRE_BEHAVIOR_REPOSITORY_INPUT_WIRING"
        ),
        "source_t141_contract_sha256": source[
            "preregistered_contract_sha256"
        ],
        "repository_inputs": basis["repository_inputs"],
        "frozen_inputs": frozen_inputs,
        "checks": checks,
        "failed_checks": failed,
        "execution_now": {
            "source_attempt_behavior_cells": 0,
            "recovery_behavior_cells": 0,
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
        "# T141B worker-wiring recovery preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Source T141 stopped before any behavior cell\n"
        "- Correction: restore the frozen worker receipt mapping\n"
        "- Recovery uses a fresh cache and the unchanged 16-cell matrix\n"
        "- Training / Colab / robot: `0/0/0`\n",
        encoding="utf-8",
        newline="\n",
    )
    print("PREREGISTERED_T141B_WORKER_WIRING_RECOVERY")
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
