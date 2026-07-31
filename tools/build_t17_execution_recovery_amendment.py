#!/usr/bin/env python3
"""Freeze one clean T17 recovery after external process termination."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "t17_support_homeomorphism_preregistration.json"
RESULT = ANALYSIS / "t17_support_homeomorphism_result.json"
OUTPUT = ANALYSIS / "t17_execution_recovery_amendment.json"
MARKDOWN = ANALYSIS / "T17_EXECUTION_RECOVERY_AMENDMENT_20260726.md"
PARTIAL = Path(
    r"D:\CodexArtifacts\open-duck-policy\t17_support_homeomorphism_v1"
)
RECOVERY = Path(
    r"D:\CodexArtifacts\open-duck-policy\t17_support_homeomorphism_v2"
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
        raise SystemExit("T17 recovery amendment requires --write")
    if OUTPUT.exists() or MARKDOWN.exists():
        raise FileExistsError("refusing to overwrite T17 recovery")
    if RESULT.exists():
        raise RuntimeError("T17 formal result already exists")
    if RECOVERY.exists():
        raise RuntimeError("T17 recovery cache already exists")

    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    evaluations = sorted(PARTIAL.rglob("evaluation.json"))
    traces = sorted(PARTIAL.rglob("*.jsonl"))
    stdout = sorted(PARTIAL.rglob("stdout.log"))
    wrappers = sorted(PARTIAL.rglob("*.onnx"))
    if (
        len(evaluations) != 1
        or len(traces) != 4
        or len(stdout) != 1
        or len(wrappers) != 2
    ):
        raise RuntimeError("T17 incomplete execution shape changed")
    evaluation_payload = json.loads(
        evaluations[0].read_text(encoding="utf-8")
    )
    if (
        evaluation_payload["status"]
        != "COMPLETE_T16_SUPPORT_COORDINATE_BLOCK"
        or len(evaluation_payload["runs"]) != 4
        or [row["command_x"] for row in evaluation_payload["runs"]]
        != [0.0, 0.074, 0.077, 0.08]
        or evaluation_payload["execution"]
        != {
            "platform": "cpu",
            "optimizer_steps": 0,
            "hosted_or_colab_compute": 0,
            "robot_or_rdk_access": 0,
        }
    ):
        raise RuntimeError("T17 completed partial block contract changed")

    basis = {
        "schema_version": "open_duck.t17_execution_recovery.v1",
        "status": "PREREGISTERED_T17_SINGLE_CLEAN_EXECUTION_RECOVERY",
        "original_preregistration": {
            "path": str(PREREG.resolve()),
            "sha256": sha256(PREREG),
            "preregistered_contract_sha256": prereg[
                "preregistered_contract_sha256"
            ],
        },
        "failed_execution": {
            "classification": "EXTERNAL_EXEC_CELL_TERMINATION_NO_TRACEBACK",
            "formal_result_exists": False,
            "completed_blocks": 1,
            "completed_cells": 4,
            "decision_weight": 0,
            "selection_use_forbidden": True,
            "evaluation": receipt(evaluations[0]),
            "stdout": receipt(stdout[0]),
            "traces": [receipt(path) for path in traces],
            "wrapped_policies": [receipt(path) for path in wrappers],
            "next_block_directory_created_without_files": (
                str(
                    (
                        PARTIAL
                        / "blocks"
                        / "V121_TRAIN_MATCHED_HALF"
                        / "p30"
                        / "TORSO_COM_X_NEG"
                    ).resolve()
                )
            ),
            "optimizer_steps": 0,
            "hosted_or_colab_compute": 0,
            "robot_or_rdk_access": 0,
        },
        "authorized_recovery": {
            "attempts_exact": 1,
            "cache_root": str(RECOVERY.resolve()),
            "must_start_empty": True,
            "reuse_partial_v1_forbidden": True,
            "matrix_cells_exact": 32,
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
        "# T17 execution recovery amendment\n\n"
        f"- Status: `{value['status']}`\n"
        "- Failed execution: one complete four-cell block, no formal result "
        "and no traceback; decision weight `0`.\n"
        "- Recovery: exactly one fresh full 32-cell execution from the "
        "unchanged frozen contract; partial v1 reuse is forbidden.\n"
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
