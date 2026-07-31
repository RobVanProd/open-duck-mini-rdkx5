#!/usr/bin/env python3
"""Freeze one clean T12 recovery after external process termination."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "t12_response_prefix_com_preregistration.json"
RESULT = ANALYSIS / "t12_response_prefix_com_result.json"
OUTPUT = ANALYSIS / "t12_execution_recovery_amendment.json"
MARKDOWN = (
    ANALYSIS / "T12_EXECUTION_RECOVERY_AMENDMENT_20260726.md"
)
PARTIAL = Path(
    r"D:\CodexArtifacts\open-duck-policy\t12_response_prefix_com_v1"
)
LAUNCHER_STDOUT = Path(
    r"D:\CodexArtifacts\open-duck-policy\t12_launcher_v1.stdout.log"
)
LAUNCHER_STDERR = Path(
    r"D:\CodexArtifacts\open-duck-policy\t12_launcher_v1.stderr.log"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def receipt(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    if not args.write:
        raise SystemExit("T12 recovery amendment requires --write")
    if OUTPUT.exists() or MARKDOWN.exists():
        raise FileExistsError("refusing to overwrite T12 recovery")
    if RESULT.exists():
        raise RuntimeError("T12 formal result already exists")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    evaluation = next(PARTIAL.rglob("evaluation.json"))
    traces = sorted(PARTIAL.rglob("*.jsonl"))
    stdout = next(PARTIAL.rglob("stdout.log"))
    if (
        len(traces) != 3
        or len(list(PARTIAL.rglob("evaluation.json"))) != 1
        or len(list(PARTIAL.rglob("stdout.log"))) != 1
    ):
        raise RuntimeError("T12 incomplete execution shape changed")
    basis = {
        "schema_version": "open_duck.t12_execution_recovery.v1",
        "status": "PREREGISTERED_T12_SINGLE_CLEAN_EXECUTION_RECOVERY",
        "original_preregistration": {
            "path": str(PREREG.resolve()),
            "sha256": sha256(PREREG),
            "preregistered_contract_sha256": prereg[
                "preregistered_contract_sha256"
            ],
        },
        "failed_execution": {
            "classification": "EXTERNAL_TERMINATION_NO_TRACEBACK",
            "formal_result_exists": False,
            "completed_blocks": 1,
            "completed_cells": 3,
            "decision_weight": 0,
            "selection_use_forbidden": True,
            "evaluation": receipt(evaluation),
            "stdout": receipt(stdout),
            "traces": [receipt(path) for path in traces],
            "launcher_stdout": receipt(LAUNCHER_STDOUT),
            "launcher_stderr": receipt(LAUNCHER_STDERR),
            "optimizer_steps": 0,
            "hosted_or_colab_compute": 0,
            "robot_or_rdk_access": 0,
        },
        "authorized_recovery": {
            "attempts_exact": 1,
            "cache_root": (
                r"D:\CodexArtifacts\open-duck-policy"
                r"\t12_response_prefix_com_v2"
            ),
            "must_start_empty": True,
            "reuse_partial_v1_forbidden": True,
            "matrix_cells_exact": 12,
            "managed_foreground_process": True,
        },
        "unchanged_contract": {
            "question": True,
            "candidate": True,
            "matrix": True,
            "thresholds": True,
            "decision_rule": True,
            "partial_results_selection_weight": 0,
            "optimizer_steps": 0,
            "hosted_or_colab_compute": 0,
            "robot_or_rdk_access": 0,
        },
        "execution_now": {
            "formal_decision_cells": 0,
            "optimizer_steps": 0,
            "hosted_or_colab_compute": 0,
            "robot_or_rdk_access": 0,
        },
    }
    value = {
        **basis,
        "amendment_contract_sha256": canonical_sha256(basis),
    }
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T12 execution recovery amendment\n\n"
        f"- Status: `{value['status']}`\n"
        "- Failed execution: one complete three-cell block, no formal result, "
        "no traceback, decision weight `0`.\n"
        "- Recovery: exactly one fresh full 12-cell execution from the "
        "frozen contract; partial v1 reuse is forbidden.\n"
        "- Optimizer/hosted/robot execution: `0/0/0`\n"
        f"- Canonical SHA-256: "
        f"`{value['amendment_contract_sha256']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(
        "amendment_contract_sha256="
        f"{value['amendment_contract_sha256']}"
    )
    print(f"file_sha256={sha256(OUTPUT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
