#!/usr/bin/env python3
"""Freeze the path-only isolation of the V126 evaluator."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v126_evaluator_isolation_amendment.json"
MARKDOWN = ANALYSIS / "WINNER_V126_EVALUATOR_ISOLATION_AMENDMENT_20260724.md"
SHARED_EVALUATOR = ROOT / "tools/closed_loop_sim_eval.py"
V126_EVALUATOR = ROOT / "tools/closed_loop_sim_eval_v126.py"
BEHAVIOR_PREREG = (
    ANALYSIS / "winner_v126_exact_oracle_behavior_preregistration.json"
)
SPARSE_CONTRACT = (
    ANALYSIS / "winner_v126_sparse_oracle_schedule_cpu_contract.json"
)
BEHAVIOR_RUNNER = ROOT / "tools/run_winner_v126_exact_oracle_behavior.py"

EXPECTED_SHARED_SHA256 = (
    "66f2969d3acb324d21694771b8579a20662b9068b84020cb708667f99fa70504"
)
EXPECTED_V126_SHA256 = (
    "5d3baac76bed70bb4cb5d81212b61a60b47d961b5bbc0d9675d71044c7d7ff52"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    if OUTPUT.exists() or MARKDOWN.exists():
        raise FileExistsError("refusing to overwrite V126 isolation amendment")

    behavior_prereg = json.loads(BEHAVIOR_PREREG.read_text(encoding="utf-8"))
    sparse_contract = json.loads(SPARSE_CONTRACT.read_text(encoding="utf-8"))
    runner_text = BEHAVIOR_RUNNER.read_text(encoding="utf-8")
    observed = {
        "shared_evaluator": sha256(SHARED_EVALUATOR),
        "v126_evaluator": sha256(V126_EVALUATOR),
        "behavior_prereg_frozen_evaluator": behavior_prereg["evidence"][
            "evaluator"
        ]["sha256"],
        "sparse_contract_frozen_evaluator": sparse_contract["input_hashes"][
            "evaluator"
        ],
    }
    checks = {
        "shared_evaluator_restored_exactly": (
            observed["shared_evaluator"] == EXPECTED_SHARED_SHA256
        ),
        "isolated_evaluator_matches_behavior_preregistration": (
            observed["v126_evaluator"]
            == observed["behavior_prereg_frozen_evaluator"]
            == EXPECTED_V126_SHA256
        ),
        "isolated_evaluator_matches_sparse_contract": (
            observed["v126_evaluator"]
            == observed["sparse_contract_frozen_evaluator"]
        ),
        "formal_runner_imports_isolated_evaluator": (
            "from closed_loop_sim_eval_v126 import" in runner_text
        ),
        "formal_runner_hashes_isolated_evaluator": (
            'sha256(ROOT / "tools/closed_loop_sim_eval_v126.py")'
            in runner_text
        ),
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise RuntimeError(f"V126 evaluator isolation failed: {failed}")

    result = {
        "schema": "open-duck/winner-v126-evaluator-isolation-amendment/v1",
        "status": "PASS_WINNER_V126_EVALUATOR_ISOLATION_AMENDMENT",
        "created_utc": "2026-07-24",
        "git_head_before_amendment": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "reason": (
            "V126 must not modify the shared closed-loop evaluator because "
            "historical evidence freezes that file. The exact V126 bytes "
            "already CPU-contracted are moved to a V126-only module; the "
            "shared evaluator is restored byte-for-byte to HEAD."
        ),
        "classification": "path-only isolation; no V126 algorithm change",
        "observed_sha256": observed,
        "expected_sha256": {
            "shared_evaluator": EXPECTED_SHARED_SHA256,
            "v126_evaluator": EXPECTED_V126_SHA256,
        },
        "checks": checks,
        "failed_checks": failed,
        "formal_screen_rule": (
            "The 16-cell runner must import and hash "
            "tools/closed_loop_sim_eval_v126.py. No earlier evidence is "
            "reclassified and no behavior cell is consumed by this amendment."
        ),
        "authority": {
            "training": False,
            "formal_behavior_cells": 0,
            "hosted_or_colab": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    OUTPUT.write_text(
        json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# V126 evaluator-isolation amendment\n\n"
        f"- Status: `{result['status']}`\n"
        f"- Shared evaluator: `{observed['shared_evaluator']}`\n"
        f"- V126 evaluator: `{observed['v126_evaluator']}`\n"
        "- Change class: path-only isolation; no V126 algorithm change.\n"
        "- Formal behavior cells consumed: `0`.\n"
        "- Hosted training authorized: `NO`.\n",
        encoding="utf-8",
    )
    print(OUTPUT)
    print(sha256(OUTPUT))


if __name__ == "__main__":
    main()
