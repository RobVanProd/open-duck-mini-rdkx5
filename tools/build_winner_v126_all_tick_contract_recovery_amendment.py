#!/usr/bin/env python3
"""Freeze one evidence-recovery run after the all-tick runner lost a HOLD."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
PREREG = ANALYSIS / "winner_v126_all_tick_oracle_preregistration.json"
OUTPUT = (
    ANALYSIS
    / "winner_v126_all_tick_contract_recovery_amendment.json"
)
MARKDOWN = (
    ANALYSIS
    / "WINNER_V126_ALL_TICK_CONTRACT_RECOVERY_AMENDMENT_20260724.md"
)
FAILED_ROOT = Path(
    r"D:\CodexArtifacts\open-duck-mini-rdkx5"
    r"\winner-v126-all-tick-oracle-contract-20260724"
)
STDOUT = Path(str(FAILED_ROOT) + ".stdout.log")
STDERR = Path(str(FAILED_ROOT) + ".stderr.log")
FIRST_RUNNER_SHA256 = (
    "9cdb4f86b165c9ff8c11539aadc165e418734e936675db5e3528505c1a6a3128"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    if OUTPUT.exists() or MARKDOWN.exists():
        raise FileExistsError("refusing to overwrite recovery amendment")
    stderr = STDERR.read_text(encoding="utf-8")
    checks = {
        "preregistration_exact": (
            sha256(PREREG)
            == "4c187ad4dfb160d1d811e457a0ddd095f0d30dbfba2ca9697269d2ee3fc45745"
        ),
        "first_run_root_exists": FAILED_ROOT.is_dir(),
        "first_run_trace_absent": not (FAILED_ROOT / "trace.jsonl").exists(),
        "first_run_result_absent": not (
            ANALYSIS / "winner_v126_all_tick_oracle_cpu_contract.json"
        ).exists(),
        "first_runner_failed_while_reading_absent_trace": (
            "FileNotFoundError" in stderr
            and "trace.jsonl" in stderr
            and "run_winner_v126_all_tick_oracle_cpu_contract.py" in stderr
        ),
        "stdout_empty": STDOUT.stat().st_size == 0,
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise RuntimeError(f"recovery amendment checks failed: {failed}")
    payload = {
        "schema_version": (
            "winner_v126.all_tick_contract_recovery_amendment.v1"
        ),
        "status": "PREREGISTERED_WINNER_V126_ALL_TICK_CONTRACT_RECOVERY",
        "reason": (
            "The first runner invoked the simulator but then raised while "
            "unconditionally reading a trace that the simulator had not "
            "written. It serialized neither the simulator HOLD nor a contract "
            "result. Therefore the execution is invalid and has no selection "
            "weight."
        ),
        "allowed_change": (
            "Persist status/error/tick immediately after the simulator call "
            "and classify an absent trace as a deterministic HOLD. The oracle, "
            "policy, plant, matrix, thresholds, and 64-tick input are unchanged."
        ),
        "authorized_recovery_executions": 1,
        "first_execution": {
            "run_root": str(FAILED_ROOT),
            "runner_sha256": FIRST_RUNNER_SHA256,
            "stdout": {
                "path": str(STDOUT),
                "sha256": sha256(STDOUT),
                "bytes": STDOUT.stat().st_size,
            },
            "stderr": {
                "path": str(STDERR),
                "sha256": sha256(STDERR),
                "bytes": STDERR.stat().st_size,
            },
            "trace_exists": False,
            "result_exists": False,
            "selection_weight": 0,
        },
        "checks": checks,
        "failed_checks": failed,
        "authority": {
            "training": False,
            "hosted_or_colab": False,
            "formal_behavior_cells": 0,
            "gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# V126 all-tick contract recovery amendment\n\n"
        f"Status: `{payload['status']}`\n\n"
        "The first runner lost the simulator HOLD by reading a missing trace "
        "before serializing a result. One unchanged-input recovery execution "
        "is frozen; it must persist the simulator status before trace parsing.\n",
        encoding="utf-8",
    )
    print(OUTPUT)
    print(sha256(OUTPUT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
