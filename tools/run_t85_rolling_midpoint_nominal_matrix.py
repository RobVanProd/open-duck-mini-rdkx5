#!/usr/bin/env python3
"""Run the rolling-midpoint pair's 16-cell nominal persistence gate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "t85_rolling_midpoint_nominal_preregistration.json"
RESULT = ANALYSIS / "t85_rolling_midpoint_nominal_result.json"
MARKDOWN = ANALYSIS / "T85_ROLLING_MIDPOINT_NOMINAL_RESULT_20260728.md"
CACHE_ROOT = (
    Path("D:/CodexArtifacts/open-duck-policy")
    / "t85_rolling_midpoint_nominal_v1"
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
        raise ValueError("changed T85 preregistration")
    if prereg["status"] != (
        "PREREGISTERED_T85_ROLLING_MIDPOINT_NOMINAL_MATRIX"
    ):
        raise ValueError("T85 preregistration is not green")
    for item in prereg["frozen_inputs"].values():
        path = Path(item["path"])
        if sha256(path) != item["sha256"]:
            raise ValueError(f"changed frozen T85 input: {path}")
    for item in [
        *prereg["policies"],
        *prereg["fits"],
        prereg["calibrator"],
        prereg["reference_feature_table"],
    ]:
        path = Path(item["path"])
        if sha256(path) != item["sha256"]:
            raise ValueError(f"changed T85 evaluated input: {path}")


def write_markdown(result: Mapping[str, Any]) -> None:
    condition = result["condition"]
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T85 rolling-midpoint nominal result",
                "",
                f"- Status: `{result['status']}`",
                f"- Green cells: `{condition['green_cells']}/16`",
                (
                    "- Worst tracking p95: "
                    f"`{condition['worst_tracking_p95_rad']:.9f} rad`"
                ),
                (
                    "- Worst strict >2 A run: "
                    f"`{condition['worst_strict_overcurrent_run_ticks']} ticks`"
                ),
                (
                    "- Worst strict overload run: "
                    f"`{condition['worst_strict_overload_run_ticks']} ticks`"
                ),
                "",
                "A pass authorizes only R2 revalidation preregistration; "
                "Gate 5 and robot access remain closed.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if not args.execute:
        raise SystemExit("refusing T85 outcome execution without --execute")
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
        raise RuntimeError("formal T85 execution requires a clean worktree")
    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    condition = prereg["conditions"][0]
    blocks: list[dict[str, Any]] = []
    started = time.time()
    for policy in prereg["policies"]:
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
                        "block": (
                            f"{policy['checkpoint_id']}:{fit['fit_id']}"
                        ),
                        "block_green": block["result"]["block_green"],
                        "elapsed_s": time.time() - started,
                    }
                ),
                flush=True,
            )
    summary = condition_summary(condition, blocks)
    passed = summary["condition_green"]
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t85_rolling_midpoint_nominal_result.v1"
        ),
        "status": (
            "PASS_T85_ROLLING_MIDPOINT_NOMINAL_MATRIX"
            if passed
            else "HOLD_T85_ROLLING_MIDPOINT_NOMINAL_MATRIX"
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
            "formal_behavior_cells": 16,
            "wall_seconds": time.time() - started,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "robustness_preregistration": passed,
            "robustness_execution": False,
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
    write_markdown(value)
    print(value["status"])
    print(f"decision={value['decision']}")
    print(f"result_sha256={value['result_sha256']}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
