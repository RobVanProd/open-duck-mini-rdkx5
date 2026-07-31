#!/usr/bin/env python3
"""Complete T243's negative-home-offset matrix without rerunning four cells."""

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
PREREG = (
    ANALYSIS
    / "t245_home_negative_floor_remaining_matrix_preregistration.json"
)
RESULT = (
    ANALYSIS / "t245_home_negative_floor_remaining_matrix_result.json"
)
MARKDOWN = (
    ANALYSIS
    / "T245_HOME_NEGATIVE_FLOOR_REMAINING_MATRIX_RESULT_20260731.md"
)
CACHE = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t245_home_negative_floor_remaining_matrix_v1"
)
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
        raise RuntimeError(f"changed T245 input: {path}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    parser.parse_args()
    if RESULT.exists() or MARKDOWN.exists() or CACHE.exists():
        raise FileExistsError("refusing to overwrite T245 output")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T245 execution requires clean worktree")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    basis = {
        key: value
        for key, value in prereg.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        prereg["status"]
        != "PREREGISTERED_T245_HOME_NEGATIVE_FLOOR_REMAINING_MATRIX"
        or prereg["failed_checks"]
        or canonical_sha256(basis)
        != prereg["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T245 preregistration changed")
    for item in prereg["frozen_inputs"].values():
        verify(item)
    for item in [
        *prereg["repository_inputs"].values(),
        *prereg["policies"],
        *prereg["fits"],
        prereg["calibrator"],
        prereg["reference_feature_table"],
        prereg["playground"]["manifest"],
        prereg["reused_evidence"]["source_non_target_block_manifest"],
        prereg["reused_evidence"]["target_cell_manifest"],
    ]:
        verify(item)

    t242b = json.loads(
        Path(prereg["frozen_inputs"]["t242b_recovery"]["path"])
        .read_text(encoding="utf-8")
    )
    t244 = json.loads(
        Path(prereg["frozen_inputs"]["t244_behavior"]["path"])
        .read_text(encoding="utf-8")
    )
    source_cells = [
        cell
        for cell in t242b["block"]["result"]["cells"]
        if float(cell["command_x_m_s"]) != 0.074
    ]
    recovered_cells = [*source_cells, t244["cell"]]
    recovered_cells.sort(key=lambda cell: float(cell["command_x_m_s"]))
    if (
        [float(cell["command_x_m_s"]) for cell in recovered_cells]
        != [0.0, 0.074, 0.077, 0.080]
        or not all(cell["cell_green"] for cell in recovered_cells)
    ):
        raise RuntimeError("T245 reused half/P30 cells changed")
    blocks: list[dict[str, Any]] = [
        {
            "condition_id": prereg["condition"]["id"],
            "condition_index": prereg["condition"]["condition_index"],
            "checkpoint_id": "T243_HOME_NEGATIVE_FLOOR_HALF",
            "step": 1_003_520,
            "fit_id": "p30",
            "cached": True,
            "reused_from_prior_evidence": True,
            "manifests": prereg["reused_evidence"],
            "result": {
                "worker_inputs_exact": True,
                "execution_platform": "cpu",
                "cells": recovered_cells,
                "block_green": True,
            },
        }
    ]
    CACHE.mkdir(parents=True)
    started = time.time()
    new_blocks = 0
    for block_plan in prereg["ordered_new_blocks"]:
        policy = next(
            row
            for row in prereg["policies"]
            if row["checkpoint_id"] == block_plan["checkpoint_id"]
        )
        fit = next(
            row
            for row in prereg["fits"]
            if row["fit_id"] == block_plan["fit_id"]
        )
        manifest, cached = run_or_load_block(
            prereg, prereg["condition"], policy, fit, CACHE
        )
        if cached:
            raise RuntimeError("T245 new block was unexpectedly cached")
        manifest_alias = {
            **manifest,
            "evaluation_path": manifest["evaluation"]["path"],
        }
        block_result = corrected_extract_block(
            prereg, prereg["condition"], manifest_alias
        )
        manifest_path = (
            CACHE
            / (
                f"{prereg['condition']['condition_index']:02d}_"
                f"{prereg['condition']['id']}"
            )
            / policy["checkpoint_id"]
            / fit["fit_id"]
            / "manifest.json"
        )
        blocks.append(
            {
                "condition_id": prereg["condition"]["id"],
                "condition_index": prereg["condition"][
                    "condition_index"
                ],
                "checkpoint_id": policy["checkpoint_id"],
                "step": policy["step"],
                "fit_id": fit["fit_id"],
                "cached": False,
                "reused_from_prior_evidence": False,
                "manifest": receipt(manifest_path),
                "result": block_result,
            }
        )
        new_blocks += 1
        print(
            json.dumps(
                {
                    "block": (
                        f"{policy['checkpoint_id']}:{fit['fit_id']}"
                    ),
                    "green_cells": sum(
                        cell["cell_green"]
                        for cell in block_result["cells"]
                    ),
                    "elapsed_s": time.time() - started,
                }
            ),
            flush=True,
        )
        if not block_result["block_green"]:
            break

    summary = condition_summary(prereg["condition"], blocks)
    completed_cells = sum(
        len(block["result"]["cells"]) for block in blocks
    )
    passed = bool(
        len(blocks) == 4
        and new_blocks == 3
        and summary["condition_green"]
        and summary["green_cells"] == 16
    )
    basis_result: dict[str, Any] = {
        "schema_version": (
            "open_duck.t245_home_negative_floor_remaining_matrix_result.v1"
        ),
        "status": (
            "PASS_T245_HOME_NEGATIVE_FLOOR_REMAINING_MATRIX"
            if passed
            else "HOLD_T245_HOME_NEGATIVE_FLOOR_REMAINING_MATRIX"
        ),
        "decision": (
            prereg["decision_rule"]["pass"]
            if passed
            else prereg["decision_rule"]["fail"]
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "condition": summary,
        "blocks": blocks,
        "recovery": {
            "blocks_reused": 1,
            "cells_reused": 4,
            "new_blocks_executed": new_blocks,
            "new_cells_executed": new_blocks * 4,
            "remaining_cells_not_run": 16 - completed_cells,
            "reused_cells_rerun": 0,
        },
        "execution": {
            "behavior_cells_total_completed": completed_cells,
            "behavior_cells_reused": 4,
            "new_behavior_cells": new_blocks * 4,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
            "wall_seconds": time.time() - started,
        },
        "authority": {
            "full_r2_preservation_preregistration": passed,
            "training": False,
            "hosted": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    value = {
        **basis_result,
        "result_sha256": canonical_sha256(basis_result),
    }
    RESULT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T245 home-negative floor remaining matrix result\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Decision: `{value['decision']}`\n"
        f"- Green/completed cells: "
        f"`{summary['green_cells']}/{completed_cells}`\n"
        f"- Reused/new/not-run cells: "
        f"`4/{new_blocks * 4}/{16 - completed_cells}`\n"
        f"- Worst tracking p95: "
        f"`{summary['worst_tracking_p95_rad']:.9f}`\n"
        "- Optimizer/hosted/robot: `0/0/0`\n"
        f"- Result SHA-256: `{value['result_sha256']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"decision={value['decision']}")
    print(
        f"green_cells={summary['green_cells']}/{completed_cells}"
    )
    print(f"result_sha256={value['result_sha256']}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
