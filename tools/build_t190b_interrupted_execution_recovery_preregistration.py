#!/usr/bin/env python3
"""Freeze continuation of T190 after an external launcher interruption."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
from typing import Any

from run_t136_static_calibration_router_transform import (
    ANALYSIS,
    ROOT,
    canonical_sha256,
    receipt,
)


T190 = ANALYSIS / "t190_t186_targeted_y_negative_preregistration.json"
T190_RESULT = ANALYSIS / "t190_t186_targeted_y_negative_result.json"
OUTPUT = ANALYSIS / "t190b_interrupted_execution_recovery_preregistration.json"
MARKDOWN = (
    ANALYSIS
    / "T190B_INTERRUPTED_EXECUTION_RECOVERY_PREREGISTRATION_20260730.md"
)
BUILDER = Path(__file__).resolve()
RUNNER = ROOT / "tools" / "run_t190b_interrupted_execution_recovery.py"
TEST = ROOT / "tests" / "test_t190b_interrupted_execution_recovery.py"
CACHE = Path(
    "D:/CodexArtifacts/open-duck-policy/t190_t186_targeted_y_negative_v1"
)
ORIGINAL_RUNNER_PIDS = (38932, 21468)


def process_exists(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def manifest_path(checkpoint_id: str, fit_id: str) -> Path:
    return (
        CACHE
        / "09_TORSO_COM_Y_NEG"
        / checkpoint_id
        / fit_id
        / "manifest.json"
    )


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T190B: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T190B preregistration requires clean worktree")

    t190 = json.loads(T190.read_text(encoding="utf-8"))
    completed = [
        {
            "checkpoint_id": "T186_COMPOSED_HALF",
            "fit_id": fit_id,
            "manifest": receipt(
                manifest_path("T186_COMPOSED_HALF", fit_id)
            ),
        }
        for fit_id in ("p30", "p31_34")
    ]
    missing = [
        {
            "checkpoint_id": "T186_COMPOSED_FINAL",
            "fit_id": fit_id,
            "manifest_path": str(
                manifest_path("T186_COMPOSED_FINAL", fit_id)
            ),
        }
        for fit_id in ("p30", "p31_34")
    ]
    checks = {
        "t190_contract_exact_and_green": (
            t190["status"]
            == "PREREGISTERED_T190_T186_TARGETED_Y_NEGATIVE"
            and not t190["failed_checks"]
            and t190["matrix"]["cells"] == 16
        ),
        "original_runner_processes_absent": all(
            not process_exists(pid) for pid in ORIGINAL_RUNNER_PIDS
        ),
        "canonical_t190_result_absent": not T190_RESULT.exists(),
        "exactly_two_completed_block_manifests": (
            len(list(CACHE.rglob("manifest.json"))) == 2
            and all(Path(row["manifest"]["path"]).is_file() for row in completed)
        ),
        "completed_blocks_are_half_checkpoint_only": (
            {(row["checkpoint_id"], row["fit_id"]) for row in completed}
            == {
                ("T186_COMPOSED_HALF", "p30"),
                ("T186_COMPOSED_HALF", "p31_34"),
            }
        ),
        "final_checkpoint_manifests_absent": all(
            not Path(row["manifest_path"]).exists() for row in missing
        ),
        "reuse_completed_blocks_without_execution": True,
        "execute_only_missing_final_blocks": True,
        "no_training_colab_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T190B preregistration checks failed: {failed}")

    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t190b_interrupted_execution_recovery_"
            "preregistration.v1"
        ),
        "status": "PREREGISTERED_T190B_INTERRUPTED_EXECUTION_RECOVERY",
        "interruption": {
            "cause": (
                "external_command_launcher_timeout_after_start; original "
                "child completed the half-checkpoint blocks and exited "
                "without a canonical result"
            ),
            "original_runner_pids": list(ORIGINAL_RUNNER_PIDS),
            "completed_behavior_cells": 8,
            "missing_behavior_cells": 8,
        },
        "completed_blocks": completed,
        "missing_blocks": missing,
        "decision_rule": {
            "pass_decision": (
                "EARN_T191_T186_FULL_R2_PREREGISTRATION_ONLY"
            ),
            "fail_decision": "CLOSE_T186_SINGLE_SUPPORT_CONTINUATION",
            "no_completed_cell_retry": True,
            "both_checkpoints_required": True,
            "training_selection_weight": 0,
        },
        "frozen_inputs": {
            name: receipt(path)
            for name, path in {
                "builder": BUILDER,
                "runner": RUNNER,
                "test": TEST,
                "t190_preregistration": T190,
                **{
                    f"completed_{row['fit_id']}_manifest": Path(
                        row["manifest"]["path"]
                    )
                    for row in completed
                },
            }.items()
        },
        "checks": checks,
        "failed_checks": failed,
        "execution_now": {
            "behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "reuse_two_completed_blocks": True,
            "execute_two_missing_blocks": True,
            "full_r2": False,
            "training": False,
            "colab": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    value["preregistered_contract_sha256"] = canonical_sha256(value)
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T190B interrupted-execution recovery preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Completed and frozen: T186 half under P30 and P31/34 (`8` cells)\n"
        "- Authorized now: T186 final under P30 and P31/34 (`8` cells)\n"
        "- Completed cells are reused read-only and are not retried\n"
        "- Both checkpoints remain mandatory; no policy selection\n"
        "- Training / Colab / robot: `0/0/0`\n"
        f"- Contract SHA-256: `{value['preregistered_contract_sha256']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
