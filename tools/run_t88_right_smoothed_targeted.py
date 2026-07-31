#!/usr/bin/env python3
"""Run T88's frozen targeted behavior matrix."""

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
PREREG = ANALYSIS / "t88_right_smoothed_targeted_preregistration.json"
RESULT = ANALYSIS / "t88_right_smoothed_targeted_result.json"
MARKDOWN = ANALYSIS / "T88_RIGHT_SMOOTHED_TARGETED_RESULT_20260728.md"
DEFAULT_CACHE_ROOT = (
    Path("D:/CodexArtifacts/open-duck-policy")
    / "t88_right_smoothed_targeted_v1"
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
        raise RuntimeError(f"T88 frozen receipt changed: {label}={path}")


def load_preregistration() -> dict[str, Any]:
    value = json.loads(PREREG.read_text(encoding="utf-8"))
    basis = {
        key: item
        for key, item in value.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        value.get("status")
        != "PREREGISTERED_T88_RIGHT_SMOOTHED_TARGETED_BEHAVIOR"
        or value.get("failed_checks")
        or canonical_sha256(basis)
        != value.get("preregistered_contract_sha256")
    ):
        raise RuntimeError("T88 preregistration changed")
    for label, item in value["repository_inputs"].items():
        verify_receipt(item, label)
    for policy in value["policies"]:
        verify_receipt(policy, f"policy:{policy['checkpoint_id']}")
    for fit in value["fits"]:
        verify_receipt(fit, f"fit:{fit['fit_id']}")
    verify_receipt(value["terminal_final_policy"], "terminal_final")
    verify_receipt(value["calibrator"], "calibrator")
    verify_receipt(value["reference_feature_table"], "reference")
    verify_receipt(value["playground"]["manifest"], "playground_manifest")
    for evidence in value["immutable_terminal_evidence"]:
        verify_receipt(
            evidence["source_result"],
            f"immutable:{evidence['condition']['id']}:result",
        )
        for block in evidence["blocks"]:
            verify_receipt(
                block["manifest"],
                (
                    f"immutable:{evidence['condition']['id']}:"
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
        raise RuntimeError("T88 matrix plan changed")
    return value


def new_half_summary(
    condition: Mapping[str, Any],
    blocks: list[dict[str, Any]],
) -> dict[str, Any]:
    cells = [
        cell
        for block in blocks
        for cell in block["result"]["cells"]
    ]
    return {
        "condition_index": condition["condition_index"],
        "condition_id": condition["id"],
        "cells": len(cells),
        "green_cells": sum(cell["cell_green"] for cell in cells),
        "green": (
            len(blocks) == 2
            and len(cells) == 8
            and all(block["result"]["block_green"] for block in blocks)
            and all(cell["cell_green"] for cell in cells)
        ),
        "worst_tracking_p95_rad": max(
            cell["behavior"]["pitch_tracking_p95_rad"] for cell in cells
        ),
        "minimum_moving_vx_m_s": min(
            cell["behavior"]["mean_local_vx_m_s"]
            for cell in cells
            if cell["command_x_m_s"] > 0.0
        ),
    }


def write_markdown(result: Mapping[str, Any]) -> None:
    lines = [
        "# T88 right-smoothed targeted behavior result",
        "",
        f"- Status: `{result['status']}`",
        f"- Decision: `{result['decision']}`",
        (
            "- New cells: "
            f"`{result['summary']['new_green_cells']}/"
            f"{result['summary']['new_cells']}`"
        ),
        (
            "- Combined cells: "
            f"`{result['summary']['combined_green_cells']}/"
            f"{result['summary']['combined_cells']}`"
        ),
        "",
        "| # | condition | new half | immutable final | combined |",
        "|---:|---|---:|---:|---:|",
    ]
    for row in result["conditions"]:
        lines.append(
            f"| {row['condition_index']} | `{row['condition_id']}` | "
            f"{row['new_half']['green_cells']}/"
            f"{row['new_half']['cells']} | "
            f"{row['immutable_final']['green_cells']}/"
            f"{row['immutable_final']['cells']} | "
            f"{row['combined_green_cells']}/{row['combined_cells']} |"
        )
    lines.extend(
        [
            "",
            "Only the changed half ran new behavior cells. Immutable final "
            "cells were accepted only through hash-verified result and block "
            "manifest receipts.",
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
        raise FileExistsError("refusing to overwrite T88 result")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T88 formal execution requires a clean worktree")

    prereg = load_preregistration()
    cache_root = args.cache_root.resolve()
    cache_root.mkdir(parents=True, exist_ok=True)
    started = time.time()
    all_blocks: list[dict[str, Any]] = []
    rows: list[dict[str, Any]] = []
    cache_hits = 0
    first_failed: str | None = None
    policy = prereg["policies"][0]

    evidence_by_id = {
        item["condition"]["id"]: item
        for item in prereg["immutable_terminal_evidence"]
    }
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
        new_half = new_half_summary(condition, blocks)
        immutable = evidence_by_id[condition["id"]]
        combined_green = (
            new_half["green"]
            and immutable["cells"] == 8
            and immutable["green_cells"] == 8
        )
        row = {
            "condition_index": condition["condition_index"],
            "condition_id": condition["id"],
            "new_half": new_half,
            "immutable_final": immutable,
            "combined_cells": new_half["cells"] + immutable["cells"],
            "combined_green_cells": (
                new_half["green_cells"] + immutable["green_cells"]
            ),
            "condition_green": combined_green,
        }
        rows.append(row)
        print(
            json.dumps(
                {
                    "condition": condition["id"],
                    "new_half_green_cells": new_half["green_cells"],
                    "combined_green_cells": row[
                        "combined_green_cells"
                    ],
                    "condition_green": combined_green,
                    "elapsed_s": time.time() - started,
                }
            ),
            flush=True,
        )
        if not combined_green:
            first_failed = str(condition["id"])
            break

    complete = len(rows) == len(prereg["conditions"])
    all_green = complete and all(row["condition_green"] for row in rows)
    new_cells = sum(row["new_half"]["cells"] for row in rows)
    new_green = sum(row["new_half"]["green_cells"] for row in rows)
    combined_cells = sum(row["combined_cells"] for row in rows)
    combined_green = sum(row["combined_green_cells"] for row in rows)
    result = {
        "schema_version": (
            "open_duck.t88_right_smoothed_targeted_result.v1"
        ),
        "status": (
            "PASS_T88_RIGHT_SMOOTHED_TARGETED_BEHAVIOR"
            if all_green
            else "HOLD_T88_RIGHT_SMOOTHED_TARGETED_BEHAVIOR"
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
            "completed_conditions": len(rows),
            "expected_conditions": len(prereg["conditions"]),
            "matrix_complete": complete,
            "new_cells": new_cells,
            "new_green_cells": new_green,
            "combined_cells": combined_cells,
            "combined_green_cells": combined_green,
            "all_green": all_green,
            "first_failed_condition": first_failed,
            "cache_hits": cache_hits,
            "new_blocks": len(all_blocks) - cache_hits,
            "wall_seconds": time.time() - started,
        },
        "conditions": rows,
        "blocks": all_blocks,
        "cache_root": str(cache_root),
        "authority": {
            "full_r2_revalidation_preregistration": all_green,
            "training": False,
            "colab": False,
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
