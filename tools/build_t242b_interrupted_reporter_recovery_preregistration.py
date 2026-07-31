#!/usr/bin/env python3
"""Freeze read-only recovery of T242's completed first behavior block."""

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


T242_PREREG = (
    ANALYSIS / "t242_bounded_router_home_offset_preregistration.json"
)
T242_RESULT = ANALYSIS / "t242_bounded_router_home_offset_result.json"
CACHE = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t242_bounded_router_home_offset_v1"
)
STDERR = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t242_runner_20260731_stderr.log"
)
OUTPUT = (
    ANALYSIS
    / "t242b_interrupted_reporter_recovery_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "T242B_INTERRUPTED_REPORTER_RECOVERY_PREREGISTRATION_20260731.md"
)
RUNNER = ROOT / "tools/run_t242b_interrupted_reporter_recovery.py"
TEST = ROOT / "tests/test_t242b_interrupted_reporter_recovery.py"


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError("refusing to overwrite T242B preregistration")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T242B preregistration requires clean worktree")

    source = json.loads(T242_PREREG.read_text(encoding="utf-8"))
    manifests = sorted(CACHE.rglob("manifest.json"))
    cache_files = sorted(path for path in CACHE.rglob("*") if path.is_file())
    completed = [
        {
            "checkpoint_id": path.parents[1].name,
            "fit_id": path.parent.name,
            "manifest": receipt(path),
        }
        for path in manifests
    ]
    referenced_files = 0
    for row in completed:
        manifest = json.loads(
            Path(row["manifest"]["path"]).read_text(encoding="utf-8")
        )
        referenced_files += (
            1
            + 1
            + 1
            + len(manifest.get("traces") or [])
        )

    checks = {
        "t242_exact_preregistration": (
            source["status"]
            == "PREREGISTERED_T242_BOUNDED_ROUTER_HOME_OFFSET"
            and not source["failed_checks"]
            and source["preregistered_contract_sha256"]
            == "5131981e7968346b86b31bb131e23e270fad024a6022f25c54ecd86d679c072b"
        ),
        "t242_formal_result_absent": not T242_RESULT.exists(),
        "exactly_one_completed_first_block": (
            len(completed) == 1
            and completed[0]["checkpoint_id"]
            == "T241_BOUNDED_ROUTER_HALF"
            and completed[0]["fit_id"] == "p30"
        ),
        "completed_block_has_four_traces": (
            len(
                json.loads(
                    Path(completed[0]["manifest"]["path"]).read_text(
                        encoding="utf-8"
                    )
                )["traces"]
            )
            == 4
        ),
        "no_unmanifested_partial_cache_files": (
            len(cache_files) == referenced_files
        ),
        "reporter_traceback_is_frozen": (
            STDERR.is_file()
            and "KeyError: 'evaluation_path'"
            in STDERR.read_text(encoding="utf-8")
        ),
        "source_requires_all_sixteen_cells": (
            source["matrix"]["cells"] == 16
            and source["matrix"]["both_checkpoints_required"] is True
            and source["decision_rule"]["no_retry"] is True
        ),
        "zero_new_behavior_optimizer_hosted_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise RuntimeError(f"T242B preregistration checks failed: {failed}")

    basis: dict[str, Any] = {
        "schema_version": (
            "open_duck.t242b_interrupted_reporter_recovery_"
            "preregistration.v1"
        ),
        "status": "PREREGISTERED_T242B_INTERRUPTED_REPORTER_RECOVERY",
        "question": (
            "Does the one immutable completed T242 block already contain a "
            "frozen-gate failure, allowing the bounded positive router to be "
            "closed without rerunning that block or executing the remaining "
            "twelve cells?"
        ),
        "source_t242_contract_sha256": source[
            "preregistered_contract_sha256"
        ],
        "frozen_inputs": {
            "builder": receipt(Path(__file__)),
            "runner": receipt(RUNNER),
            "test": receipt(TEST),
            "t242_preregistration": receipt(T242_PREREG),
            "reporter_stderr": receipt(STDERR),
        },
        "completed_blocks": completed,
        "cache_root": str(CACHE),
        "recovery": {
            "cause": (
                "post-simulation reporter used obsolete "
                "manifest['evaluation_path'] instead of "
                "manifest['evaluation']['path']"
            ),
            "read_only": True,
            "reuse_completed_block": True,
            "rerun_completed_cells": False,
            "run_missing_cells": False,
            "selection_weight_of_observed_console_output": 0,
        },
        "decision_rule": {
            "failed_completed_cell": (
                "CLOSE_BOUNDED_POSITIVE_ROUTER; KEEP_REMAINING_12_NOT_RUN"
            ),
            "all_completed_cells_green": (
                "EARN_T242C_MISSING_BLOCK_RECOVERY_PREREGISTRATION_ONLY"
            ),
            "no_retry": True,
            "both_checkpoints_still_required_for_any_future_pass": True,
        },
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
            "read_only_recovery": True,
            "resume_t242": False,
            "training": False,
            "hosted": False,
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
        "# T242B interrupted reporter recovery preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Recover: one immutable half/P30 block (4 cells)\n"
        "- Execute/rerun remaining behavior cells: `0/0`\n"
        "- A failed recovered cell closes this router and leaves 12 cells "
        "`NOT_RUN`\n"
        "- Optimizer/hosted/robot: `0/0/0`\n"
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
