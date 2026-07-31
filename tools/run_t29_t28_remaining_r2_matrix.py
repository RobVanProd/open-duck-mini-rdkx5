#!/usr/bin/env python3
"""Run T28 through original R2 conditions 2-20, stopping at first failure."""

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
PREREG = ANALYSIS / "t29_t28_remaining_r2_preregistration.json"
RESULT = ANALYSIS / "t29_t28_remaining_r2_result.json"
RESULT_MD = ANALYSIS / "T29_T28_REMAINING_R2_RESULT_20260726.md"
CACHE_ROOT = (
    Path(r"D:\CodexArtifacts\open-duck-policy")
    / "t29_t28_remaining_r2_matrix_v1"
)

sys.path.insert(0, str(ROOT / "tools"))
from run_t27_t23_robustness_matrix import (  # noqa: E402
    block_directory,
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


def matrix_plan(payload: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "cell_index": index,
            "condition_index": condition["condition_index"],
            "condition_id": condition["id"],
            "checkpoint_id": policy["checkpoint_id"],
            "fit_id": fit["fit_id"],
            "command_x_m_s": float(command),
        }
        for index, (condition, policy, fit, command) in enumerate(
            (
                (condition, policy, fit, command)
                for condition in payload["conditions"]
                for policy in payload["policies"]
                for fit in payload["fits"]
                for command in payload["commands_x_m_s"]
            ),
            start=1,
        )
    ]


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
        raise ValueError("changed T29 preregistration")
    if prereg["status"] != "PREREGISTERED_T29_T28_REMAINING_R2_MATRIX":
        raise ValueError("T29 preregistration is not green")
    plan = matrix_plan(prereg)
    plan_sha = hashlib.sha256(
        json.dumps(
            plan,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()
    if plan_sha != prereg["matrix"]["plan_sha256"]:
        raise ValueError("changed T29 matrix plan")
    if len(plan) != 304:
        raise ValueError("T29 plan is not exactly 304 cells")
    for item in prereg["repository_inputs"].values():
        path = Path(item["path"])
        if sha256(path) != item["sha256"]:
            raise ValueError(f"changed T29 repository input: {path}")
    for item in [
        *prereg["policies"],
        *prereg["fits"],
        prereg["calibrator"],
        prereg["reference_feature_table"],
    ]:
        path = Path(item["path"])
        if sha256(path) != item["sha256"]:
            raise ValueError(f"changed T29 evaluated input: {path}")


def require_clean_worktree() -> str:
    status = subprocess.run(
        ["git", "status", "--short"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    if status.strip():
        raise RuntimeError("formal T29 execution requires a clean worktree")
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def write_markdown(result: Mapping[str, Any]) -> None:
    summary = result["summary"]
    lines = [
        "# T29 T28 remaining R2 result",
        "",
        f"status: `{result['status']}`",
        "",
        f"- total green cells: `{summary['total_green_cells']}`",
        f"- total completed cells: `{summary['total_completed_cells']}`",
        (
            "- completed R2 conditions: "
            f"`{summary['total_completed_conditions']}/20`"
        ),
        (
            "- first failed condition: "
            f"`{summary['first_failed_condition']}`"
        ),
        "",
    ]
    if summary["all_twenty_conditions_green"]:
        lines.append(
            "All 320 R2 cells pass. This authorizes only Gate 5 package "
            "preregistration; hardware Gate 5 remains unauthorized."
        )
    else:
        lines.append(
            "The ladder stopped after completing the first failed condition. "
            "No training or hardware work is automatically authorized."
        )
    lines.append("")
    RESULT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Execute the preregistered CPU matrix.",
    )
    args = parser.parse_args()
    if not args.execute:
        raise SystemExit("refusing outcome execution without --execute")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    verify_preregistration(prereg)
    commit = require_clean_worktree()
    started = time.time()
    blocks: list[dict[str, Any]] = []
    condition_results: list[dict[str, Any]] = []
    cache_hits = 0
    new_blocks = 0
    first_failed: str | None = None
    for condition in prereg["conditions"]:
        condition_blocks: list[dict[str, Any]] = []
        for policy in prereg["policies"]:
            for fit in prereg["fits"]:
                manifest, cached = run_or_load_block(
                    prereg,
                    condition,
                    policy,
                    fit,
                    CACHE_ROOT,
                )
                directory = block_directory(
                    CACHE_ROOT,
                    int(condition["condition_index"]),
                    str(condition["id"]),
                    str(policy["checkpoint_id"]),
                    str(fit["fit_id"]),
                )
                block = {
                    "condition_id": condition["id"],
                    "condition_index": condition["condition_index"],
                    "checkpoint_id": policy["checkpoint_id"],
                    "fit_id": fit["fit_id"],
                    "cached": cached,
                    "manifest": {
                        "path": str((directory / "manifest.json").resolve()),
                        "bytes": (directory / "manifest.json").stat().st_size,
                        "sha256": sha256(directory / "manifest.json"),
                    },
                    "result": extract_block(prereg, condition, manifest),
                }
                blocks.append(block)
                condition_blocks.append(block)
                cache_hits += int(cached)
                new_blocks += int(not cached)
                print(
                    json.dumps(
                        {
                            "condition": condition["id"],
                            "block": (
                                f"{policy['checkpoint_id']}:"
                                f"{fit['fit_id']}"
                            ),
                            "block_green": block["result"]["block_green"],
                            "elapsed_s": time.time() - started,
                        }
                    ),
                    flush=True,
                )
        summary = condition_summary(condition, condition_blocks)
        condition_results.append(summary)
        print(
            json.dumps(
                {
                    "new_completed_conditions": len(condition_results),
                    "condition": condition["id"],
                    "green_cells": summary["green_cells"],
                    "condition_green": summary["condition_green"],
                    "elapsed_s": time.time() - started,
                }
            ),
            flush=True,
        )
        if not summary["condition_green"]:
            first_failed = str(condition["id"])
            break
    remaining_complete = len(condition_results) == 19
    remaining_green = remaining_complete and all(
        item["condition_green"] for item in condition_results
    )
    new_cells = sum(item["cells"] for item in condition_results)
    new_green = sum(item["green_cells"] for item in condition_results)
    all_green = remaining_green and new_green == 304
    result: dict[str, Any] = {
        "schema_version": "open_duck.t29_t28_remaining_r2_result.v1",
        "status": (
            "PASS_T29_T28_FULL_R2_ROBUSTNESS"
            if all_green
            else "HOLD_T29_T28_REMAINING_R2"
        ),
        "decision": (
            "EARN_T28_GATE5_PACKAGE_PREREGISTRATION"
            if all_green
            else "STOP_T28_AT_FIRST_FAILED_REMAINING_R2_CONDITION"
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "repository_commit": commit,
        "condition_one_basis": prereg["condition_one_basis"],
        "summary": {
            "expected_new_conditions": 19,
            "completed_new_conditions": len(condition_results),
            "remaining_matrix_complete": remaining_complete,
            "new_completed_cells": new_cells,
            "new_green_cells": new_green,
            "total_completed_conditions": 1 + len(condition_results),
            "total_completed_cells": 16 + new_cells,
            "total_green_cells": 16 + new_green,
            "all_twenty_conditions_green": all_green,
            "first_failed_condition": first_failed,
            "cache_hits": cache_hits,
            "new_blocks": new_blocks,
            "wall_seconds": time.time() - started,
        },
        "conditions": condition_results,
        "blocks": blocks,
        "cache_root": str(CACHE_ROOT),
        "authority": {
            "gate5_package_preregistration": all_green,
            "gate5_hardware": False,
            "training": False,
            "colab": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    result["result_sha256"] = canonical_sha256(result)
    RESULT.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_markdown(result)
    print(result["status"])
    print(f"decision={result['decision']}")
    print(f"result_sha256={result['result_sha256']}")
    print(f"sha256={sha256(RESULT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
