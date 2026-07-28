#!/usr/bin/env python3
"""Run T78 midpoint's preregistered full eight-cell formal matrix."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "t83_t78_midpoint_full_preregistration.json"
RESULT = ANALYSIS / "t83_t78_midpoint_full_result.json"
MARKDOWN = ANALYSIS / "T83_T78_MIDPOINT_FULL_RESULT_20260728.md"
CACHE_ROOT = (
    Path("D:/CodexArtifacts/open-duck-policy")
    / "t83_t78_midpoint_full_v1"
)

sys.path.insert(0, str(ROOT / "tools"))
from run_t27_t23_robustness_matrix import (  # noqa: E402
    condition_summary,
    extract_block,
    run_or_load_block,
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: Any) -> str:
    payload = dict(value)
    payload.pop("result_sha256", None)
    return hashlib.sha256(
        json.dumps(
            payload,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def verify_preregistration(prereg: dict[str, Any]) -> None:
    expected = prereg["preregistered_contract_sha256"]
    actual = hashlib.sha256(
        json.dumps(
            {
                key: value
                for key, value in prereg.items()
                if key != "preregistered_contract_sha256"
            },
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()
    if actual != expected:
        raise ValueError("changed T83 preregistration")
    if prereg["status"] != "PREREGISTERED_T83_T78_MIDPOINT_FULL_MATRIX":
        raise ValueError("T83 preregistration is not green")
    for item in prereg["frozen_inputs"].values():
        path = Path(item["path"])
        if sha256(path) != item["sha256"]:
            raise ValueError(f"changed frozen T83 input: {path}")
    for item in [
        *prereg["policies"],
        *prereg["fits"],
        prereg["calibrator"],
        prereg["reference_feature_table"],
    ]:
        path = Path(item["path"])
        if sha256(path) != item["sha256"]:
            raise ValueError(f"changed T83 evaluated input: {path}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if not args.execute:
        raise SystemExit("refusing T83 outcome execution without --execute")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    verify_preregistration(prereg)
    status = subprocess.run(
        ["git", "status", "--short"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    if status.strip():
        raise RuntimeError("formal T83 execution requires a clean worktree")
    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    condition = prereg["conditions"][0]
    policy = prereg["policies"][0]
    blocks: list[dict[str, Any]] = []
    started = time.time()
    for fit in prereg["fits"]:
        manifest, cached = run_or_load_block(
            prereg,
            condition,
            policy,
            fit,
            CACHE_ROOT,
        )
        manifest_path = (
            CACHE_ROOT
            / f"{int(condition['condition_index']):02d}_{condition['id']}"
            / policy["checkpoint_id"]
            / fit["fit_id"]
            / "manifest.json"
        )
        block = {
            "condition_id": condition["id"],
            "condition_index": condition["condition_index"],
            "checkpoint_id": policy["checkpoint_id"],
            "fit_id": fit["fit_id"],
            "cached": cached,
            "manifest": {
                "path": str(manifest_path.resolve()),
                "bytes": manifest_path.stat().st_size,
                "sha256": sha256(manifest_path),
            },
            "result": extract_block(prereg, condition, manifest),
        }
        blocks.append(block)
        print(
            json.dumps(
                {
                    "fit": fit["fit_id"],
                    "block_green": block["result"]["block_green"],
                    "elapsed_s": time.time() - started,
                }
            ),
            flush=True,
        )
    summary = condition_summary(condition, blocks)
    passed = (
        summary["cells"] == 8
        and summary["green_cells"] == 8
        and summary["condition_green"]
    )
    value: dict[str, Any] = {
        "schema_version": "open_duck.t83_t78_midpoint_full_result.v1",
        "status": (
            "PASS_T83_T78_MIDPOINT_FULL_MATRIX"
            if passed
            else "HOLD_T83_T78_MIDPOINT_FULL_MATRIX"
        ),
        "decision": (
            prereg["decision_rule"]["pass_decision"]
            if passed
            else prereg["decision_rule"]["fail_decision"]
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "repository_commit": commit,
        "condition": summary,
        "blocks": blocks,
        "execution": {
            "cpu_only": True,
            "formal_behavior_cells": 8,
            "wall_seconds": time.time() - started,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "classification": {
            "candidate_status": "diagnostic_only",
            "persistence_satisfied": False,
            "coefficient_search": False,
        },
        "authority": {
            "persistent_mechanism_preregistration": passed,
            "training": False,
            "colab": False,
            "candidate_promotion": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    value["result_sha256"] = canonical_sha256(value)
    RESULT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T83 T78 midpoint full-matrix result",
                "",
                f"- Status: `{value['status']}`",
                f"- Decision: `{value['decision']}`",
                f"- Green cells: `{summary['green_cells']}/8`",
                (
                    "- Worst tracking p95: "
                    f"`{summary['worst_tracking_p95_rad']:.9f} rad`"
                ),
                "- Candidate status: `diagnostic only; persistence unsatisfied`",
                "- Training/Colab/Gate5/robot: `0/0/0/0`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(value["status"])
    print(f"decision={value['decision']}")
    print(f"result_sha256={value['result_sha256']}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
