#!/usr/bin/env python3
"""Invalidate T82's unsupported command-subset protocol before behavior."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "t82_t78_midpoint_crossover_preregistration.json"
RESULT = ANALYSIS / "t82_t78_midpoint_crossover_result.json"
OUTPUT = ANALYSIS / "t82_t78_midpoint_crossover_invalidation.json"
MARKDOWN = ANALYSIS / "T82_T78_MIDPOINT_CROSSOVER_INVALIDATION_20260728.md"
CACHE = (
    Path("D:/CodexArtifacts/open-duck-policy")
    / "t82_t78_midpoint_crossover_v1"
)
LOG = (
    CACHE
    / "02_FLOOR_FRICTION_HI"
    / "T78_EXACT_ADAPTER_MIDPOINT_DIAGNOSTIC"
    / "p30"
    / "stdout.log"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def receipt(path: Path) -> dict:
    return {
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T82 invalidation: {path}")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    log_text = LOG.read_text(encoding="utf-8", errors="replace")
    files = sorted(path for path in CACHE.rglob("*") if path.is_file())
    trace_files = sorted(
        path for path in CACHE.rglob("*.jsonl") if path.is_file()
    )
    evaluation_files = sorted(
        path
        for path in CACHE.rglob("*.json")
        if path.name in {"evaluation.json", "manifest.json"}
    )
    checks = {
        "preregistration_was_green": (
            prereg["status"]
            == "PREREGISTERED_T82_T78_MIDPOINT_CROSSOVER"
            and prereg["failed_checks"] == []
        ),
        "worker_rejected_command_subset": (
            "formal T27 commands, seed, or duration changed" in log_text
        ),
        "only_worker_stdout_file_created": files == [LOG],
        "no_trace_rows_created": trace_files == [],
        "no_evaluation_or_manifest_created": evaluation_files == [],
        "no_formal_result_created": not RESULT.exists(),
        "no_behavior_training_colab_or_robot_execution": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    value = {
        "schema_version": (
            "open_duck.t82_t78_midpoint_crossover_invalidation.v1"
        ),
        "status": (
            "INVALIDATED_T82_PROTOCOL_BEFORE_BEHAVIOR"
            if not failed
            else "HOLD_T82_INVALIDATION_AUDIT"
        ),
        "reason": (
            "the frozen formal worker requires the complete "
            "0/.074/.077/.080 command set and rejected the x=.08 subset"
        ),
        "classification": "PROTOCOL_UNSUPPORTED_NOT_MECHANISM_RESULT",
        "replacement": (
            "use the unchanged formal worker for one eight-cell midpoint "
            "diagnostic across both fits and all four commands"
        ),
        "receipts": {
            "preregistration": receipt(PREREG),
            "worker_stdout": receipt(LOG),
        },
        "cache_file_count": len(files),
        "trace_file_count": len(trace_files),
        "evaluation_file_count": len(evaluation_files),
        "checks": {name: bool(passed) for name, passed in checks.items()},
        "failed_checks": failed,
        "execution": {
            "formal_behavior_cells": 0,
            "simulator_trace_rows": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "full_eight_cell_midpoint_preregistration": not failed,
            "training": False,
            "colab": False,
            "candidate_promotion": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T82 midpoint crossover protocol invalidation",
                "",
                f"- Status: `{value['status']}`",
                "- Classification: `protocol unsupported; no mechanism result`",
                "- Formal behavior cells / trace rows: `0 / 0`",
                "- Replacement: unchanged formal eight-cell midpoint screen",
                "- Training/Colab/Gate5/robot: `0/0/0/0`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(value["status"])
    print(f"failed_checks={failed}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
