#!/usr/bin/env python3
"""Repeat the V126 CPU contract after the no-semantic-change optimization."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

import run_winner_v126_exact_oracle_cpu_contract as contract  # noqa: E402


ANALYSIS = ROOT / "outputs/analysis"
AMENDMENT = ANALYSIS / "winner_v126_oracle_optimization_amendment.json"
AMENDMENT_SHA256 = (
    "197fa6d89215eb8c722afc0de510fb0aa70235b39ead282df729357f85cf7959"
)
OUTPUT = ANALYSIS / "winner_v126_exact_oracle_cpu_contract_v2.json"
MARKDOWN = ANALYSIS / "WINNER_V126_EXACT_ORACLE_CPU_CONTRACT_V2_20260724.md"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    if sha256(AMENDMENT) != AMENDMENT_SHA256:
        raise ValueError("V126 optimization amendment changed")
    contract.PREREG = AMENDMENT
    contract.PREREG_SHA256 = AMENDMENT_SHA256
    contract.OUTPUT = OUTPUT
    contract.MARKDOWN = MARKDOWN
    status = contract.main()
    if not OUTPUT.is_file():
        return status
    result = json.loads(OUTPUT.read_text(encoding="utf-8"))
    result["schema_version"] = (
        "winner_v126.exact_oracle_cpu_contract.optimized.v2"
    )
    result["optimization_amendment"] = {
        "path": str(AMENDMENT.relative_to(ROOT)),
        "sha256": sha256(AMENDMENT),
        "wrapper_runner_sha256": sha256(Path(__file__).resolve()),
    }
    result["status"] = (
        "PASS_WINNER_V126_EXACT_ORACLE_CPU_CONTRACT_OPTIMIZED"
        if not result["failed_checks"]
        else "HOLD_WINNER_V126_EXACT_ORACLE_CPU_CONTRACT_OPTIMIZED"
    )
    OUTPUT.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner-v126 optimized exact-oracle CPU contract\n\n"
        f"Status: `{result['status']}`\n\n"
        f"Failed checks: `{result['failed_checks']}`.\n\n"
        "This revalidates only the semantics-preserving cached-rollout "
        "optimization. A pass authorizes the frozen 16-cell CPU screen, not "
        "training, hosted compute, Gate 5, RDK-X5, robot, torque, or motion.\n",
        encoding="utf-8",
    )
    return status


if __name__ == "__main__":
    raise SystemExit(main())
