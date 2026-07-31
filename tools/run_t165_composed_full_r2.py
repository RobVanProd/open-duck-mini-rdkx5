#!/usr/bin/env python3
"""Run T164's sequential full R2 matrix one condition per invocation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
import time
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "t165_composed_full_r2_preregistration.json"
RESULT = ANALYSIS / "t165_composed_full_r2_result.json"
MARKDOWN = ANALYSIS / "T165_COMPOSED_FULL_R2_RESULT_20260729.md"
CACHE = Path(
    "D:/CodexArtifacts/open-duck-policy/t165_composed_full_r2_v1"
)
sys.path.insert(0, str(ROOT / "tools"))
from run_t27_t23_robustness_matrix import (  # noqa: E402
    canonical_sha256,
    condition_summary,
    extract_block,
    matrix_plan,
    receipt,
    run_or_load_block,
    sha256,
    verify_receipt,
)


def load_preregistration() -> dict[str, Any]:
    value = json.loads(PREREG.read_text(encoding="utf-8"))
    basis = {
        key: item
        for key, item in value.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        value.get("status") != "PREREGISTERED_T165_COMPOSED_FULL_R2"
        or value.get("failed_checks")
        or canonical_sha256(basis)
        != value.get("preregistered_contract_sha256")
    ):
        raise RuntimeError("T165 preregistration changed")
    for label, item in value["repository_inputs"].items():
        verify_receipt(item, label)
    for label, item in value["frozen_inputs"].items():
        verify_receipt(item, label)
    for policy in value["policies"]:
        verify_receipt(policy, f"policy:{policy['checkpoint_id']}")
    for fit in value["fits"]:
        verify_receipt(fit, f"fit:{fit['fit_id']}")
    verify_receipt(value["calibrator"], "calibrator")
    verify_receipt(value["reference_feature_table"], "reference")
    verify_receipt(value["playground"]["manifest"], "playground_manifest")
    plan = matrix_plan(
        value["conditions"],
        value["policies"],
        value["fits"],
        value["commands_x_m_s"],
        int(value["seed"]),
    )
    if (
        len(plan) != value["matrix"]["maximum_cells"]
        or canonical_sha256(plan) != value["matrix"]["plan_sha256"]
    ):
        raise RuntimeError("T165 matrix plan changed")
    return value


def write_progress(
    prereg: dict[str, Any],
    conditions: list[dict[str, Any]],
    *,
    cache_hits: int,
    new_blocks: int,
    wall_seconds: float,
) -> Path:
    value = {
        "schema_version": "open_duck.t165_composed_full_r2_progress.v1",
        "status": "IN_PROGRESS_T165_COMPOSED_FULL_R2",
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "completed_conditions": len(conditions),
        "expected_conditions": len(prereg["conditions"]),
        "conditions": conditions,
        "cache_hits": cache_hits,
        "new_blocks": new_blocks,
        "wall_seconds_this_invocation": wall_seconds,
        "selection_or_decision_made": False,
        "hosted_compute_units": 0,
        "robot_or_rdk_access": 0,
    }
    value["progress_sha256"] = canonical_sha256(value)
    path = CACHE / "progress.json"
    path.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return path


def write_markdown(value: dict[str, Any]) -> None:
    lines = [
        "# T165 composed full R2 result",
        "",
        f"- Status: `{value['status']}`",
        f"- Decision: `{value['decision']}`",
        f"- Completed conditions: "
        f"`{value['summary']['completed_conditions']}/20`",
        f"- Green cells: "
        f"`{value['summary']['green_cells']}/"
        f"{value['summary']['completed_cells']}`",
        f"- First failure: "
        f"`{value['summary']['first_failed_condition']}`",
        "- Training / Colab / robot: `0/0/0`",
        "",
        "| index | condition | green | tracking p95 | min vx | overcurrent run | overload run |",
        "|---:|---|---:|---:|---:|---:|---:|",
    ]
    for item in value["conditions"]:
        lines.append(
            f"| {item['condition_index']} | `{item['condition_id']}` | "
            f"{item['green_cells']}/{item['cells']} | "
            f"{item['worst_tracking_p95_rad']:.9f} | "
            f"{item['minimum_moving_vx_m_s']:.9f} | "
            f"{item['worst_strict_overcurrent_run_ticks']} | "
            f"{item['worst_strict_overload_run_ticks']} |"
        )
    MARKDOWN.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    parser.add_argument(
        "--maximum-new-conditions",
        type=int,
        choices=[1],
        default=1,
    )
    args = parser.parse_args()
    if RESULT.exists() or MARKDOWN.exists():
        raise FileExistsError("refusing to overwrite T165 result")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T165 execution requires clean worktree")
    prereg = load_preregistration()
    CACHE.mkdir(parents=True, exist_ok=True)
    started = time.time()
    all_blocks: list[dict[str, Any]] = []
    condition_results: list[dict[str, Any]] = []
    cache_hits = 0
    new_blocks = 0
    new_conditions = 0
    first_failed: str | None = None
    paused = False

    for condition in prereg["conditions"]:
        blocks = []
        condition_had_new_block = False
        for policy in prereg["policies"]:
            for fit in prereg["fits"]:
                manifest, cached = run_or_load_block(
                    prereg, condition, policy, fit, CACHE
                )
                block_result = extract_block(prereg, condition, manifest)
                manifest_path = (
                    CACHE
                    / f"{condition['condition_index']:02d}_{condition['id']}"
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
                blocks.append(block)
                all_blocks.append(block)
                cache_hits += int(cached)
                new_blocks += int(not cached)
                condition_had_new_block |= not cached
                print(
                    json.dumps(
                        {
                            "condition": condition["id"],
                            "block": (
                                f"{policy['checkpoint_id']}:"
                                f"{fit['fit_id']}"
                            ),
                            "block_green": block_result["block_green"],
                            "cached": cached,
                            "elapsed_s": time.time() - started,
                        }
                    ),
                    flush=True,
                )
        summary = condition_summary(condition, blocks)
        condition_results.append(summary)
        if condition_had_new_block:
            new_conditions += 1
        print(
            json.dumps(
                {
                    "completed_conditions": len(condition_results),
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
        if new_conditions >= args.maximum_new_conditions:
            paused = len(condition_results) < len(prereg["conditions"])
            break

    complete = len(condition_results) == len(prereg["conditions"])
    all_green = complete and all(
        item["condition_green"] for item in condition_results
    )
    if paused and first_failed is None:
        progress = write_progress(
            prereg,
            condition_results,
            cache_hits=cache_hits,
            new_blocks=new_blocks,
            wall_seconds=time.time() - started,
        )
        print("IN_PROGRESS_T165_COMPOSED_FULL_R2")
        print(f"completed_conditions={len(condition_results)}/20")
        print(f"progress={progress}")
        print(f"progress_sha256={sha256(progress)}")
        return 0

    completed_cells = sum(item["cells"] for item in condition_results)
    green_cells = sum(item["green_cells"] for item in condition_results)
    value: dict[str, Any] = {
        "schema_version": "open_duck.t165_composed_full_r2_result.v1",
        "status": (
            "PASS_T165_COMPOSED_FULL_R2"
            if all_green
            else "HOLD_T165_COMPOSED_FULL_R2"
        ),
        "decision": (
            prereg["decision_rule"]["pass_decision"]
            if all_green
            else prereg["decision_rule"]["fail_decision"]
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "summary": {
            "expected_conditions": len(prereg["conditions"]),
            "completed_conditions": len(condition_results),
            "matrix_complete": complete,
            "completed_cells": completed_cells,
            "green_cells": green_cells,
            "all_completed_cells_green": green_cells == completed_cells,
            "all_twenty_conditions_green": all_green,
            "first_failed_condition": first_failed,
            "cache_hits": cache_hits,
            "new_blocks": new_blocks,
            "wall_seconds": time.time() - started,
        },
        "conditions": condition_results,
        "blocks": all_blocks,
        "cache_root": str(CACHE),
        "execution": {
            "behavior_cells": completed_cells,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "deployment_contract_audit_preregistration": all_green,
            "gate5_hardware_authorized": False,
            "additional_training_authorized": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    value["result_sha256"] = canonical_sha256(value)
    RESULT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    write_markdown(value)
    print(value["status"])
    print(f"decision={value['decision']}")
    print(f"result_sha256={value['result_sha256']}")
    return 0 if all_green else 1


if __name__ == "__main__":
    raise SystemExit(main())
