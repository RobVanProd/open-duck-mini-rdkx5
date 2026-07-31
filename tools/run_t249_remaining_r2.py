#!/usr/bin/env python3
"""Run T249's remaining R2 conditions, one condition per invocation."""

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
PREREG = ANALYSIS / "t249_remaining_r2_preregistration.json"
RESULT = ANALYSIS / "t249_remaining_r2_result.json"
MARKDOWN = ANALYSIS / "T249_REMAINING_R2_RESULT_20260731.md"
CACHE = Path("D:/CodexArtifacts/open-duck-policy/t249_remaining_r2_v1")
PROGRESS = CACHE / "progress.json"
sys.path.insert(0, str(ROOT / "tools"))
from run_t136_static_calibration_router_transform import (  # noqa: E402
    canonical_sha256,
    receipt,
    sha256,
)
from run_t242_bounded_router_home_offset import (  # noqa: E402
    corrected_extract_block,
)
from run_t27_t23_robustness_matrix import (  # noqa: E402
    condition_summary,
    run_or_load_block,
)


def verify(value: Mapping[str, Any]) -> None:
    path = Path(value["path"])
    if (
        not path.is_file()
        or path.stat().st_size != value["bytes"]
        or sha256(path) != value["sha256"]
    ):
        raise RuntimeError(f"changed T249 input: {path}")


def reused_conditions(prereg: Mapping[str, Any]) -> list[dict[str, Any]]:
    t237 = json.loads(
        Path(
            prereg["reused_evidence"]["conditions_1_through_16"]["path"]
        ).read_text(encoding="utf-8")
    )
    t248 = json.loads(
        Path(prereg["reused_evidence"]["condition_17"]["path"]).read_text(
            encoding="utf-8"
        )
    )
    rows = [dict(row) for row in t237["conditions"][:16]]
    rows.append(dict(t248["condition"]))
    if (
        [row["condition_index"] for row in rows] != list(range(1, 18))
        or not all(
            row["condition_green"] and row["green_cells"] == 16
            for row in rows
        )
    ):
        raise RuntimeError("T249 reused condition evidence changed")
    return rows


def progress_conditions() -> list[dict[str, Any]]:
    if not PROGRESS.is_file():
        return []
    value = json.loads(PROGRESS.read_text(encoding="utf-8"))
    basis = {
        key: item for key, item in value.items() if key != "progress_sha256"
    }
    if (
        value["status"] != "IN_PROGRESS_T249_REMAINING_R2"
        or canonical_sha256(basis) != value["progress_sha256"]
    ):
        raise RuntimeError("T249 progress changed")
    return [dict(row) for row in value["new_conditions"]]


def write_progress(
    prereg: Mapping[str, Any],
    rows: list[dict[str, Any]],
    *,
    cache_hits: int,
    new_blocks: int,
    wall_seconds: float,
) -> None:
    basis: dict[str, Any] = {
        "schema_version": "open_duck.t249_remaining_r2_progress.v1",
        "status": "IN_PROGRESS_T249_REMAINING_R2",
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "completed_new_conditions": len(rows),
        "expected_new_conditions": 3,
        "new_conditions": rows,
        "cache_hits_this_invocation": cache_hits,
        "new_blocks_this_invocation": new_blocks,
        "wall_seconds_this_invocation": wall_seconds,
        "selection_or_decision_made": False,
        "optimizer_steps": 0,
        "hosted_compute_units": 0,
        "robot_or_rdk_access": 0,
    }
    value = {**basis, "progress_sha256": canonical_sha256(basis)}
    PROGRESS.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def write_markdown(value: Mapping[str, Any]) -> None:
    lines = [
        "# T249 remaining R2 result",
        "",
        f"- Status: `{value['status']}`",
        f"- Decision: `{value['decision']}`",
        f"- Green conditions: `{value['summary']['green_conditions']}/20`",
        f"- Green cells: `{value['summary']['green_cells']}/"
        f"{value['summary']['completed_cells']}`",
        f"- First failure: `{value['summary']['first_failed_condition']}`",
        "- Optimizer/hosted/robot: `0/0/0`",
        f"- Result SHA-256: `{value['result_sha256']}`",
        "",
        "| index | condition | green | tracking p95 | min vx |",
        "|---:|---|---:|---:|---:|",
    ]
    for row in value["conditions"]:
        lines.append(
            f"| {row['condition_index']} | `{row['condition_id']}` | "
            f"{row['green_cells']}/{row['cells']} | "
            f"{row['worst_tracking_p95_rad']:.9f} | "
            f"{row['minimum_moving_vx_m_s']:.9f} |"
        )
    MARKDOWN.write_text(
        "\n".join(lines) + "\n", encoding="utf-8", newline="\n"
    )


def finalize(
    prereg: Mapping[str, Any],
    conditions: list[dict[str, Any]],
    blocks: list[dict[str, Any]],
    *,
    started: float,
) -> int:
    complete = len(conditions) == 20
    all_green = complete and all(row["condition_green"] for row in conditions)
    first_failed = next(
        (
            row["condition_id"]
            for row in conditions
            if not row["condition_green"]
        ),
        None,
    )
    completed_cells = sum(int(row["cells"]) for row in conditions)
    green_cells = sum(int(row["green_cells"]) for row in conditions)
    basis: dict[str, Any] = {
        "schema_version": "open_duck.t249_remaining_r2_result.v1",
        "status": (
            "PASS_T249_REMAINING_R2"
            if all_green
            else "HOLD_T249_REMAINING_R2"
        ),
        "decision": (
            prereg["decision_rule"]["pass"]
            if all_green
            else prereg["decision_rule"]["fail"]
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "summary": {
            "expected_conditions": 20,
            "completed_conditions": len(conditions),
            "green_conditions": sum(
                bool(row["condition_green"]) for row in conditions
            ),
            "matrix_complete": complete,
            "completed_cells": completed_cells,
            "green_cells": green_cells,
            "all_twenty_conditions_green": all_green,
            "first_failed_condition": first_failed,
        },
        "conditions": conditions,
        "new_blocks": blocks,
        "reuse": {
            "conditions_reused": 17,
            "cells_reused": 272,
            "reused_cells_rerun": 0,
            "evidence": prereg["reused_evidence"],
        },
        "execution": {
            "new_behavior_cells": len(blocks) * 4,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
            "wall_seconds_final_invocation": time.time() - started,
        },
        "authority": {
            "offline_deployment_contract_audit_preregistration": all_green,
            "training": False,
            "hosted": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    value = {**basis, "result_sha256": canonical_sha256(basis)}
    RESULT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    write_markdown(value)
    print(value["status"])
    print(f"decision={value['decision']}")
    print(f"green_conditions={value['summary']['green_conditions']}/20")
    print(f"result_sha256={value['result_sha256']}")
    return 0 if all_green else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    parser.parse_args()
    if RESULT.exists() or MARKDOWN.exists():
        raise FileExistsError("refusing to overwrite T249 result")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T249 execution requires clean worktree")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    prereg_basis = {
        key: value
        for key, value in prereg.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        prereg["status"] != "PREREGISTERED_T249_REMAINING_R2"
        or prereg["failed_checks"]
        or canonical_sha256(prereg_basis)
        != prereg["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T249 preregistration changed")
    for item in prereg["frozen_inputs"].values():
        verify(item)
    for item in [
        *prereg["repository_inputs"].values(),
        *prereg["policies"],
        *prereg["fits"],
        prereg["calibrator"],
        prereg["reference_feature_table"],
        prereg["playground"]["manifest"],
        prereg["reused_evidence"]["conditions_1_through_16"],
        prereg["reused_evidence"]["condition_17"],
    ]:
        verify(item)
    CACHE.mkdir(parents=True, exist_ok=True)
    started = time.time()
    inherited = reused_conditions(prereg)
    prior_new = progress_conditions()
    completed_ids = {row["condition_id"] for row in prior_new}
    blocks: list[dict[str, Any]] = []
    cache_hits = 0
    new_blocks = 0
    new_condition_executed = False
    current_new = list(prior_new)

    for condition in prereg["remaining_conditions"]:
        if condition["id"] in completed_ids:
            continue
        condition_blocks: list[dict[str, Any]] = []
        for policy in prereg["policies"]:
            for fit in prereg["fits"]:
                manifest, cached = run_or_load_block(
                    prereg, condition, policy, fit, CACHE
                )
                manifest_alias = {
                    **manifest,
                    "evaluation_path": manifest["evaluation"]["path"],
                }
                block_result = corrected_extract_block(
                    prereg, condition, manifest_alias
                )
                manifest_path = (
                    CACHE
                    / (
                        f"{condition['condition_index']:02d}_"
                        f"{condition['id']}"
                    )
                    / policy["checkpoint_id"]
                    / fit["fit_id"]
                    / "manifest.json"
                )
                block = {
                    "condition_index": condition["condition_index"],
                    "condition_id": condition["id"],
                    "checkpoint_id": policy["checkpoint_id"],
                    "step": policy["step"],
                    "fit_id": fit["fit_id"],
                    "cached": cached,
                    "manifest": receipt(manifest_path),
                    "result": block_result,
                }
                condition_blocks.append(block)
                blocks.append(block)
                cache_hits += int(cached)
                new_blocks += int(not cached)
                new_condition_executed |= not cached
                print(
                    json.dumps(
                        {
                            "condition": condition["id"],
                            "block": (
                                f"{policy['checkpoint_id']}:{fit['fit_id']}"
                            ),
                            "block_green": block_result["block_green"],
                            "cached": cached,
                            "elapsed_s": time.time() - started,
                        }
                    ),
                    flush=True,
                )
        summary = condition_summary(condition, condition_blocks)
        current_new.append(summary)
        print(
            json.dumps(
                {
                    "completed_new_conditions": len(current_new),
                    "condition": condition["id"],
                    "green_cells": summary["green_cells"],
                    "condition_green": summary["condition_green"],
                    "elapsed_s": time.time() - started,
                }
            ),
            flush=True,
        )
        conditions = inherited + current_new
        if not summary["condition_green"]:
            return finalize(
                prereg, conditions, blocks, started=started
            )
        if new_condition_executed and len(current_new) < 3:
            write_progress(
                prereg,
                current_new,
                cache_hits=cache_hits,
                new_blocks=new_blocks,
                wall_seconds=time.time() - started,
            )
            print("IN_PROGRESS_T249_REMAINING_R2")
            print(f"green_conditions={len(conditions)}/20")
            print(f"progress={PROGRESS}")
            print(f"progress_sha256={receipt(PROGRESS)['sha256']}")
            return 0

    return finalize(prereg, inherited + current_new, blocks, started=started)


if __name__ == "__main__":
    raise SystemExit(main())
