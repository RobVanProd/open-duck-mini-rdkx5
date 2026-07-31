#!/usr/bin/env python3
"""Run T78 midpoint's preregistered two-cell x=.08 crossover screen."""

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
PREREG = ANALYSIS / "t82_t78_midpoint_crossover_preregistration.json"
RESULT = ANALYSIS / "t82_t78_midpoint_crossover_result.json"
MARKDOWN = ANALYSIS / "T82_T78_MIDPOINT_CROSSOVER_RESULT_20260728.md"
CACHE_ROOT = (
    Path("D:/CodexArtifacts/open-duck-policy")
    / "t82_t78_midpoint_crossover_v1"
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
        raise ValueError("changed T82 preregistration")
    if prereg["status"] != "PREREGISTERED_T82_T78_MIDPOINT_CROSSOVER":
        raise ValueError("T82 preregistration is not green")
    for item in prereg["frozen_inputs"].values():
        path = Path(item["path"])
        if sha256(path) != item["sha256"]:
            raise ValueError(f"changed frozen T82 input: {path}")
    for item in [
        *prereg["policies"],
        *prereg["fits"],
        prereg["calibrator"],
        prereg["reference_feature_table"],
    ]:
        path = Path(item["path"])
        if sha256(path) != item["sha256"]:
            raise ValueError(f"changed T82 evaluated input: {path}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if not args.execute:
        raise SystemExit("refusing T82 outcome execution without --execute")
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
        raise RuntimeError("formal T82 execution requires a clean worktree")
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
        summary["cells"] == 2
        and summary["green_cells"] == 2
        and summary["condition_green"]
    )
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t82_t78_midpoint_crossover_result.v1"
        ),
        "status": (
            "PASS_T82_T78_MIDPOINT_CROSSOVER"
            if passed
            else "HOLD_T82_T78_MIDPOINT_CROSSOVER"
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
            "formal_behavior_cells": 2,
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
            "full_midpoint_preregistration": passed,
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
                "# T82 T78 midpoint crossover result",
                "",
                f"- Status: `{value['status']}`",
                f"- Decision: `{value['decision']}`",
                f"- Green cells: `{summary['green_cells']}/2`",
                (
                    "- Worst tracking p95: "
                    f"`{summary['worst_tracking_p95_rad']:.9f} rad`"
                ),
                "- Candidate status: `diagnostic only`",
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
