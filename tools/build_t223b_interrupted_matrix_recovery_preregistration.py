#!/usr/bin/env python3
"""Freeze recovery of T223's interrupted two-of-four block matrix."""

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


T223_PREREG = (
    ANALYSIS / "t223_global_plateau_nominal_matrix_preregistration.json"
)
T223_RESULT = ANALYSIS / "t223_global_plateau_nominal_matrix_result.json"
CACHE = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t223_global_plateau_nominal_matrix_v1"
)
OUTPUT = (
    ANALYSIS
    / "t223b_interrupted_matrix_recovery_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "T223B_INTERRUPTED_MATRIX_RECOVERY_PREREGISTRATION_20260730.md"
)
RUNNER = ROOT / "tools/run_t223b_interrupted_matrix_recovery.py"
TEST = ROOT / "tests/test_t223b_interrupted_matrix_recovery.py"


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError("refusing to overwrite T223B preregistration")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T223B preregistration requires clean worktree")
    source = json.loads(T223_PREREG.read_text(encoding="utf-8"))
    manifests = sorted(CACHE.rglob("manifest.json"))
    completed = [
        {
            "checkpoint_id": path.parents[1].name,
            "fit_id": path.parent.name,
            "manifest": receipt(path),
        }
        for path in manifests
    ]
    files = [path for path in CACHE.rglob("*") if path.is_file()]
    expected_completed = {
        ("T222_GLOBAL_PLATEAU_HALF", "p30"),
        ("T222_GLOBAL_PLATEAU_HALF", "p31_34"),
    }
    frozen = {
        "builder": receipt(Path(__file__)),
        "runner": receipt(RUNNER),
        "test": receipt(TEST),
        "t223_preregistration": receipt(T223_PREREG),
    }
    checks = {
        "t223_exact_preregistration": (
            source["status"]
            == "PREREGISTERED_T223_GLOBAL_PLATEAU_NOMINAL_MATRIX"
            and not source["failed_checks"]
            and source["preregistered_contract_sha256"]
            == "aea78c6a7e09d0196e993a8207b72bc9bcdf8119d5fdac11c1abc328263d35d0"
        ),
        "t223_formal_result_absent": not T223_RESULT.exists(),
        "exactly_two_completed_half_blocks": (
            len(completed) == 2
            and {
                (row["checkpoint_id"], row["fit_id"]) for row in completed
            }
            == expected_completed
        ),
        "no_unmanifested_partial_files": (
            len(files)
            == sum(
                1
                for row in completed
                for _ in Path(row["manifest"]["path"]).parent.rglob("*")
                if _.is_file()
            )
        ),
        "matrix_still_requires_final_two_blocks": (
            source["matrix"]["both_checkpoints_required"]
            and source["matrix"]["cells"] == 16
        ),
        "zero_optimizer_hosted_or_robot_now": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T223B preregistration checks failed: {failed}")
    basis: dict[str, Any] = {
        "schema_version": (
            "open_duck.t223b_interrupted_matrix_recovery_"
            "preregistration.v1"
        ),
        "status": "PREREGISTERED_T223B_INTERRUPTED_MATRIX_RECOVERY",
        "question": (
            "Can the two hash-frozen completed half blocks be reused exactly "
            "while running only the missing final/P30 and final/P31-34 blocks "
            "to complete the originally preregistered T223 matrix?"
        ),
        "frozen_inputs": frozen,
        "source_t223_contract_sha256": source[
            "preregistered_contract_sha256"
        ],
        "cache_root": str(CACHE),
        "completed_blocks": completed,
        "recovery": {
            "cause": "desktop command output pipe closed during long process",
            "reuse_completed_blocks": True,
            "rerun_completed_cells": False,
            "required_missing_blocks": [
                {
                    "checkpoint_id": "T222_GLOBAL_PLATEAU_FINAL",
                    "fit_id": "p30",
                    "cells": 4,
                },
                {
                    "checkpoint_id": "T222_GLOBAL_PLATEAU_FINAL",
                    "fit_id": "p31_34",
                    "cells": 4,
                },
            ],
            "selection_weight_of_completed_results": 0,
            "stop_after_first_failure": False,
            "both_checkpoints_still_mandatory": True,
        },
        "decision_rule": source["decision_rule"],
        "checks": checks,
        "failed_checks": failed,
        "execution_now": {
            "completed_behavior_cells_reused": 0,
            "new_behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "reuse_exact_completed_blocks": True,
            "run_only_missing_eight_cells": True,
            "targeted_y_negative": False,
            "training": False,
            "colab": False,
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
        "# T223B interrupted matrix recovery preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Reuse: two immutable completed half blocks\n"
        "- Execute: only final/P30 and final/P31-34 (8 cells)\n"
        "- Completed-cell rerun / optimizer / hosted / robot: `0/0/0/0`\n"
        f"- Contract SHA-256: `{value['preregistered_contract_sha256']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(
        "preregistered_contract_sha256="
        f"{value['preregistered_contract_sha256']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
