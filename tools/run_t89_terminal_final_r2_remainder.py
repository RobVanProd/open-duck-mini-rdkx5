#!/usr/bin/env python3
"""Run T89's diagnostic terminal-final R2 remainder."""

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
PREREG = ANALYSIS / "t89_terminal_final_r2_remainder_preregistration.json"
RESULT = ANALYSIS / "t89_terminal_final_r2_remainder_result.json"
MARKDOWN = ANALYSIS / "T89_TERMINAL_FINAL_R2_REMAINDER_RESULT_20260728.md"
DEFAULT_CACHE_ROOT = (
    Path("D:/CodexArtifacts/open-duck-policy")
    / "t89_terminal_final_r2_remainder_v1"
)

sys.path.insert(0, str(ROOT / "tools"))
from run_t27_t23_robustness_matrix import (  # noqa: E402
    extract_block,
    matrix_plan,
    receipt,
    run_or_load_block,
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


def verify_receipt(value: Mapping[str, Any], label: str) -> None:
    path = Path(value["path"])
    if (
        not path.is_file()
        or path.stat().st_size != int(value["bytes"])
        or sha256(path) != value["sha256"]
    ):
        raise RuntimeError(f"T89 frozen receipt changed: {label}={path}")


def load_preregistration() -> dict[str, Any]:
    value = json.loads(PREREG.read_text(encoding="utf-8"))
    basis = {
        key: item
        for key, item in value.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        value.get("status")
        != "PREREGISTERED_T89_TERMINAL_FINAL_R2_REMAINDER_DIAGNOSTIC"
        or value.get("failed_checks")
        or canonical_sha256(basis)
        != value.get("preregistered_contract_sha256")
    ):
        raise RuntimeError("T89 preregistration changed")
    for label, item in value["repository_inputs"].items():
        verify_receipt(item, label)
    for policy in value["policies"]:
        verify_receipt(policy, f"policy:{policy['checkpoint_id']}")
    for fit in value["fits"]:
        verify_receipt(fit, f"fit:{fit['fit_id']}")
    verify_receipt(value["calibrator"], "calibrator")
    verify_receipt(value["reference_feature_table"], "reference")
    verify_receipt(value["playground"]["manifest"], "playground_manifest")
    immutable = value["immutable_conditions_one_through_four"]
    verify_receipt(immutable["source_result"], "immutable:result")
    for condition in immutable["conditions"]:
        for block in condition["blocks"]:
            verify_receipt(
                block["manifest"],
                (
                    f"immutable:{condition['condition']['id']}:"
                    f"{block['fit_id']}"
                ),
            )
    plan = matrix_plan(
        value["conditions"],
        value["policies"],
        value["fits"],
        value["commands_x_m_s"],
        int(value["seed"]),
    )
    if (
        len(plan) != int(value["matrix"]["maximum_new_cells"])
        or canonical_sha256(plan) != value["matrix"]["plan_sha256"]
    ):
        raise RuntimeError("T89 matrix plan changed")
    return value


def condition_summary(
    condition: Mapping[str, Any],
    blocks: list[dict[str, Any]],
) -> dict[str, Any]:
    cells = [
        cell
        for block in blocks
        for cell in block["result"]["cells"]
    ]
    moving = [
        cell for cell in cells if cell["command_x_m_s"] > 0.0
    ]
    return {
        "condition_index": condition["condition_index"],
        "condition_id": condition["id"],
        "override": condition["override"],
        "cells": len(cells),
        "green_cells": sum(cell["cell_green"] for cell in cells),
        "condition_green": (
            len(blocks) == 2
            and all(block["result"]["block_green"] for block in blocks)
            and len(cells) == 8
            and all(cell["cell_green"] for cell in cells)
        ),
        "worst_tracking_p95_rad": max(
            cell["behavior"]["pitch_tracking_p95_rad"] for cell in cells
        ),
        "minimum_moving_vx_m_s": min(
            cell["behavior"]["mean_local_vx_m_s"] for cell in moving
        ),
        "worst_strict_overcurrent_run_ticks": max(
            cell["protection"]["worst_strict_overcurrent_run_ticks"]
            for cell in cells
        ),
        "worst_strict_overload_run_ticks": max(
            cell["protection"]["worst_strict_overload_run_ticks"]
            for cell in cells
        ),
    }


def write_markdown(result: Mapping[str, Any]) -> None:
    lines = [
        "# T89 terminal-final R2 remainder result",
        "",
        f"- Status: `{result['status']}`",
        f"- Decision: `{result['decision']}`",
        (
            "- New conditions: "
            f"`{result['summary']['completed_new_conditions']}/16`"
        ),
        (
            "- Combined cells: "
            f"`{result['summary']['combined_green_cells']}/"
            f"{result['summary']['combined_cells']}`"
        ),
        (
            "- First failed condition: "
            f"`{result['summary']['first_failed_condition']}`"
        ),
        "",
        "| # | condition | green | tracking p95 | min vx |",
        "|---:|---|---:|---:|---:|",
    ]
    for condition in result["conditions"]:
        lines.append(
            f"| {condition['condition_index']} | "
            f"`{condition['condition_id']}` | "
            f"{condition['green_cells']}/{condition['cells']} | "
            f"{condition['worst_tracking_p95_rad']:.9f} | "
            f"{condition['minimum_moving_vx_m_s']:.9f} |"
        )
    lines.extend(
        [
            "",
            "This is a single-checkpoint diagnostic and cannot satisfy the "
            "two-export persistence gate or authorize deployment.",
            "",
            "Training, Gate 5, RDK-X5, robot, torque, and motion remain closed.",
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
        raise FileExistsError("refusing to overwrite T89 result")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T89 formal execution requires a clean worktree")

    prereg = load_preregistration()
    cache_root = args.cache_root.resolve()
    cache_root.mkdir(parents=True, exist_ok=True)
    started = time.time()
    policy = prereg["policies"][0]
    all_blocks: list[dict[str, Any]] = []
    condition_results: list[dict[str, Any]] = []
    cache_hits = 0
    first_failed: str | None = None

    for condition in prereg["conditions"]:
        blocks = []
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
            print(
                json.dumps(
                    {
                        "condition": condition["id"],
                        "block": (
                            f"{policy['checkpoint_id']}:{fit['fit_id']}"
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
                    "completed_new_conditions": len(condition_results),
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
    new_cells = sum(item["cells"] for item in condition_results)
    new_green = sum(item["green_cells"] for item in condition_results)
    immutable = prereg["immutable_conditions_one_through_four"]
    combined_cells = int(immutable["cells"]) + new_cells
    combined_green = int(immutable["green_cells"]) + new_green
    result = {
        "schema_version": (
            "open_duck.t89_terminal_final_r2_remainder_result.v1"
        ),
        "status": (
            "PASS_T89_TERMINAL_FINAL_FULL_R2_DIAGNOSTIC"
            if all_green
            else "HOLD_T89_TERMINAL_FINAL_R2_REMAINDER"
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
            "expected_new_conditions": len(prereg["conditions"]),
            "completed_new_conditions": len(condition_results),
            "new_matrix_complete": complete,
            "new_cells": new_cells,
            "new_green_cells": new_green,
            "combined_cells": combined_cells,
            "combined_green_cells": combined_green,
            "terminal_final_all_twenty_green": (
                all_green
                and combined_cells == 160
                and combined_green == 160
            ),
            "first_failed_condition": first_failed,
            "cache_hits": cache_hits,
            "new_blocks": len(all_blocks) - cache_hits,
            "wall_seconds": time.time() - started,
        },
        "conditions": condition_results,
        "blocks": all_blocks,
        "immutable_conditions_one_through_four": immutable,
        "cache_root": str(cache_root),
        "authority": {
            "persistence_stabilization_cpu_contract_preregistration": (
                all_green
            ),
            "training": False,
            "colab": False,
            "checkpoint_selection": False,
            "candidate_promotion": False,
            "gate5": False,
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
