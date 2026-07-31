#!/usr/bin/env python3
"""Run the one preregistered T182 shared-failure behavior cell."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
import time
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREGISTRATION = (
    ANALYSIS / "t182_shared_failure_single_cell_preregistration.json"
)
RESULT = ANALYSIS / "t182_shared_failure_single_cell_result.json"
MARKDOWN = ANALYSIS / "T182_SHARED_FAILURE_SINGLE_CELL_RESULT_20260730.md"
CACHE = Path(
    r"D:\CodexArtifacts\open-duck-policy"
    r"\t182_shared_failure_single_cell_v1"
)

sys.path.insert(0, str(ROOT / "tools"))
from run_t27_t23_robustness_matrix import (  # noqa: E402
    canonical_sha256,
    extract_block,
    receipt,
    run_or_load_block,
    verify_receipt,
)


class T182Error(RuntimeError):
    """The frozen T182 single-cell contract was violated."""


def _require(condition: object, message: str) -> None:
    if not condition:
        raise T182Error(message)


def _load_json(path: Path) -> dict[str, Any]:
    _require(path.is_file(), f"missing JSON artifact: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    _require(isinstance(value, dict), f"JSON root is not an object: {path}")
    return value


def _canonical_without(value: Mapping[str, Any], field: str) -> str:
    basis = dict(value)
    basis.pop(field, None)
    return canonical_sha256(basis)


def decision(cell_green: bool) -> tuple[str, str]:
    if cell_green:
        return (
            "PASS_T182_SHARED_FAILURE_SINGLE_CELL",
            "EARN_T183_DUAL_CONDITION_32_CELL_PREREGISTRATION_ONLY",
        )
    return (
        "HOLD_T182_SHARED_FAILURE_SINGLE_CELL",
        "CLOSE_COUNT_WEIGHTED_ALPHA_0P2_WITHOUT_MORE_BEHAVIOR",
    )


def run(
    preregistration_path: Path = PREREGISTRATION,
    result_path: Path = RESULT,
    markdown_path: Path = MARKDOWN,
    cache_root: Path = CACHE,
) -> dict[str, Any]:
    _require(not result_path.exists(), f"refusing to overwrite: {result_path}")
    _require(not markdown_path.exists(), f"refusing to overwrite: {markdown_path}")
    _require(not cache_root.exists(), f"refusing to reuse cache: {cache_root}")
    _require(
        not subprocess.check_output(
            ["git", "status", "--porcelain"], cwd=ROOT, text=True
        ).strip(),
        "T182 execution requires committed clean preregistration",
    )
    prereg = _load_json(preregistration_path)
    _require(
        prereg.get("status")
        == "PREREGISTERED_T182_SHARED_FAILURE_SINGLE_CELL",
        "unexpected T182 preregistration status",
    )
    _require(
        _canonical_without(prereg, "preregistered_contract_sha256")
        == prereg.get("preregistered_contract_sha256"),
        "T182 preregistration hash differs",
    )
    for label, item in prereg["frozen_inputs"].items():
        verify_receipt(item, label)
    verify_receipt(prereg["policy"], "policy")
    verify_receipt(prereg["fit"], "fit")
    verify_receipt(prereg["calibrator"], "calibrator")
    verify_receipt(prereg["reference_feature_table"], "reference")
    verify_receipt(prereg["playground"]["manifest"], "playground_manifest")
    cache_root.mkdir(parents=True)
    started = time.time()
    manifest, cached = run_or_load_block(
        prereg,
        prereg["condition"],
        prereg["policy"],
        prereg["fit"],
        cache_root,
    )
    _require(not cached, "T182 requires a fresh behavior cell")
    block_result = extract_block(
        prereg, prereg["condition"], manifest
    )
    _require(
        len(block_result["cells"]) == 1,
        "T182 worker did not return exactly one cell",
    )
    cell = block_result["cells"][0]
    status, next_decision = decision(bool(cell["cell_green"]))
    manifest_path = (
        cache_root
        / "12_TORSO_COM_Z_POS"
        / prereg["policy"]["checkpoint_id"]
        / prereg["fit"]["fit_id"]
        / "manifest.json"
    )
    basis: dict[str, Any] = {
        "schema_version": "open_duck.t182_shared_failure_single_cell_result.v1",
        "status": status,
        "decision": next_decision,
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "cell": cell,
        "manifest": receipt(manifest_path),
        "execution": {
            "new_behavior_cells": 1,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
            "wall_seconds": time.time() - started,
        },
        "authority": prereg["authority_after_result"],
    }
    basis["result_sha256"] = canonical_sha256(basis)
    result_path.write_text(
        json.dumps(basis, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    markdown_path.write_text(
        "# T182 shared-failure single-cell result\n\n"
        f"- Status: `{status}`\n"
        f"- Decision: `{next_decision}`\n"
        f"- Cell green: `{cell['cell_green']}`\n"
        f"- Samples: `{cell['behavior']['samples']}`\n"
        f"- Termination: `{cell['behavior']['termination_reason']}`\n"
        "- Optimizer / hosted compute / robot: `0/0/0`\n",
        encoding="utf-8",
        newline="\n",
    )
    return basis


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true", required=True)
    parser.add_argument("--preregistration", type=Path, default=PREREGISTRATION)
    parser.add_argument("--result", type=Path, default=RESULT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    parser.add_argument("--cache-root", type=Path, default=CACHE)
    args = parser.parse_args()
    result = run(
        args.preregistration,
        args.result,
        args.markdown,
        args.cache_root,
    )
    print(result["status"])
    print(f"decision={result['decision']}")
    print(f"result_sha256={result['result_sha256']}")
    return 0 if result["cell"]["cell_green"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
