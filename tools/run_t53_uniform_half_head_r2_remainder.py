#!/usr/bin/env python3
"""Run T53's frozen sequential R2 conditions 5-20."""

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
PREREG = (
    ANALYSIS
    / "t53_uniform_half_head_r2_remainder_preregistration.json"
)
RESULT = ANALYSIS / "t53_uniform_half_head_r2_remainder_result.json"
MARKDOWN = (
    ANALYSIS / "T53_UNIFORM_HALF_HEAD_R2_REMAINDER_RESULT_20260728.md"
)
DEFAULT_CACHE_ROOT = (
    Path("D:/CodexArtifacts/open-duck-policy")
    / "t53_uniform_half_head_r2_remainder_v1"
)

sys.path.insert(0, str(ROOT / "tools"))
from run_t27_t23_robustness_matrix import (  # noqa: E402
    condition_summary,
    extract_block,
    matrix_plan,
    receipt,
    run_or_load_block,
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def verify_receipt(value: Mapping[str, Any], label: str) -> None:
    path = Path(value["path"])
    if (
        not path.is_file()
        or path.stat().st_size != int(value["bytes"])
        or sha256(path) != value["sha256"]
    ):
        raise RuntimeError(f"T53 frozen receipt changed: {label}={path}")


def load_preregistration() -> dict[str, Any]:
    value = json.loads(PREREG.read_text(encoding="utf-8"))
    basis = {
        key: item
        for key, item in value.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        value.get("status")
        != "PREREGISTERED_T53_UNIFORM_HALF_HEAD_R2_REMAINDER"
        or value.get("failed_checks")
        or canonical_sha256(basis)
        != value.get("preregistered_contract_sha256")
    ):
        raise RuntimeError("T53 preregistration changed")
    for label, item in value["repository_inputs"].items():
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
        len(plan) != int(value["matrix"]["maximum_cells"])
        or canonical_sha256(plan) != value["matrix"]["plan_sha256"]
    ):
        raise RuntimeError("T53 matrix plan changed")
    return value


def write_markdown(result: Mapping[str, Any]) -> None:
    lines = [
        "# T53 uniform half-head R2 remainder result",
        "",
        f"- Status: `{result['status']}`",
        f"- Decision: `{result['decision']}`",
        (
            "- Conditions: "
            f"`{result['summary']['completed_conditions']}/16`"
        ),
        (
            "- Green cells: "
            f"`{result['summary']['green_cells']}/"
            f"{result['summary']['completed_cells']}`"
        ),
        (
            "- First failed condition: "
            f"`{result['summary']['first_failed_condition']}`"
        ),
        "",
        "| # | condition | green | tracking p95 | min vx | current run | "
        "overload run |",
        "|---:|---|---:|---:|---:|---:|---:|",
    ]
    for condition in result["conditions"]:
        lines.append(
            f"| {condition['condition_index']} | "
            f"`{condition['condition_id']}` | "
            f"{condition['green_cells']}/{condition['cells']} | "
            f"{condition['worst_tracking_p95_rad']:.9f} | "
            f"{condition['minimum_moving_vx_m_s']:.9f} | "
            f"{condition['worst_strict_overcurrent_run_ticks']} | "
            f"{condition['worst_strict_overload_run_ticks']} |"
        )
    lines.extend(
        [
            "",
            "Conditions ran in frozen order and stopped after the first "
            "complete failed condition. Raw traces remain on D:.",
            "",
            "A pass authorizes only Gate 5 deployment-package "
            "preregistration. Hardware, RDK-X5, robot access, torque, "
            "motion, and deployment remain closed.",
            "",
        ]
    )
    MARKDOWN.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    parser.add_argument(
        "--cache-root", type=Path, default=DEFAULT_CACHE_ROOT
    )
    args = parser.parse_args()
    if RESULT.exists() or MARKDOWN.exists():
        raise FileExistsError("refusing to overwrite T53 result")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T53 formal execution requires a clean worktree")
    prereg = load_preregistration()
    cache_root = args.cache_root.resolve()
    cache_root.mkdir(parents=True, exist_ok=True)
    started = time.time()
    all_blocks: list[dict[str, Any]] = []
    condition_results: list[dict[str, Any]] = []
    cache_hits = 0
    new_blocks = 0
    first_failed: str | None = None
    for condition in prereg["conditions"]:
        blocks = []
        for policy in prereg["policies"]:
            for fit in prereg["fits"]:
                manifest, cached = run_or_load_block(
                    prereg,
                    condition,
                    policy,
                    fit,
                    cache_root,
                )
                block_result = extract_block(prereg, condition, manifest)
                block = {
                    "condition_index": condition["condition_index"],
                    "condition_id": condition["id"],
                    "checkpoint_id": policy["checkpoint_id"],
                    "step": policy["step"],
                    "fit_id": fit["fit_id"],
                    "cached": cached,
                    "manifest": receipt(
                        Path(manifest["evaluation"]["path"]).parent
                        / "manifest.json"
                    ),
                    "result": block_result,
                }
                blocks.append(block)
                all_blocks.append(block)
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
                            "block_green": block_result["block_green"],
                            "elapsed_s": time.time() - started,
                        }
                    ),
                    flush=True,
                )
        summary = condition_summary(condition, blocks)
        condition_results.append(summary)
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
    complete = len(condition_results) == len(prereg["conditions"])
    all_green = complete and all(
        item["condition_green"] for item in condition_results
    )
    completed_cells = sum(item["cells"] for item in condition_results)
    green_cells = sum(item["green_cells"] for item in condition_results)
    result = {
        "schema_version": (
            "open_duck.t53_uniform_half_head_r2_remainder_result.v1"
        ),
        "status": (
            "PASS_T53_UNIFORM_HALF_HEAD_R2_REMAINDER"
            if all_green
            else "HOLD_T53_UNIFORM_HALF_HEAD_R2_REMAINDER"
        ),
        "decision": (
            prereg["decision_rule"]["pass_decision"]
            if all_green
            else prereg["decision_rule"]["fail_decision"]
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "repository_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "summary": {
            "expected_conditions": len(prereg["conditions"]),
            "completed_conditions": len(condition_results),
            "matrix_complete": complete,
            "completed_cells": completed_cells,
            "green_cells": green_cells,
            "all_completed_cells_green": green_cells == completed_cells,
            "all_sixteen_conditions_green": all_green,
            "first_failed_condition": first_failed,
            "cache_hits": cache_hits,
            "new_blocks": new_blocks,
            "wall_seconds": time.time() - started,
        },
        "conditions": condition_results,
        "blocks": all_blocks,
        "cache_root": str(cache_root),
        "authority": {
            "gate5_deployment_package_preregistration": all_green,
            "policy_promotion": False,
            "checkpoint_selection": False,
            "training": False,
            "colab": False,
            "deployment": False,
            "gate5_hardware": False,
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
