#!/usr/bin/env python3
"""Complete only T190's missing final-checkpoint blocks."""

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
T190 = ANALYSIS / "t190_t186_targeted_y_negative_preregistration.json"
PREREG = ANALYSIS / "t190b_interrupted_execution_recovery_preregistration.json"
RESULT = ANALYSIS / "t190b_interrupted_execution_recovery_result.json"
MARKDOWN = ANALYSIS / "T190B_INTERRUPTED_EXECUTION_RECOVERY_RESULT_20260730.md"
CACHE = Path(
    "D:/CodexArtifacts/open-duck-policy/t190_t186_targeted_y_negative_v1"
)
sys.path.insert(0, str(ROOT / "tools"))
from run_t27_t23_robustness_matrix import (  # noqa: E402
    condition_summary,
    extract_block,
    receipt,
    run_or_load_block,
)
from run_t136_static_calibration_router_transform import (  # noqa: E402
    canonical_sha256,
    sha256,
)


def verify(value: Mapping[str, Any]) -> None:
    path = Path(value["path"])
    if (
        not path.is_file()
        or path.stat().st_size != value["bytes"]
        or sha256(path) != value["sha256"]
    ):
        raise RuntimeError(f"changed T190B input: {path}")


def find_policy(prereg: Mapping[str, Any], checkpoint_id: str) -> dict[str, Any]:
    return next(
        dict(row)
        for row in prereg["policies"]
        if row["checkpoint_id"] == checkpoint_id
    )


def find_fit(prereg: Mapping[str, Any], fit_id: str) -> dict[str, Any]:
    return next(
        dict(row) for row in prereg["fits"] if row["fit_id"] == fit_id
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    parser.parse_args()
    if RESULT.exists() or MARKDOWN.exists():
        raise FileExistsError("refusing to overwrite T190B output")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T190B execution requires clean worktree")

    t190 = json.loads(T190.read_text(encoding="utf-8"))
    recovery = json.loads(PREREG.read_text(encoding="utf-8"))
    recovery_basis = {
        key: value
        for key, value in recovery.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        recovery["status"]
        != "PREREGISTERED_T190B_INTERRUPTED_EXECUTION_RECOVERY"
        or recovery["failed_checks"]
        or canonical_sha256(recovery_basis)
        != recovery["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T190B preregistration changed")
    for item in recovery["frozen_inputs"].values():
        verify(item)
    for item in [
        *t190["repository_inputs"].values(),
        *t190["policies"],
        *t190["fits"],
        t190["calibrator"],
        t190["reference_feature_table"],
        t190["playground"]["manifest"],
    ]:
        verify(item)

    condition = t190["condition"]
    blocks = []
    started = time.time()
    for row in recovery["completed_blocks"]:
        verify(row["manifest"])
        manifest = json.loads(
            Path(row["manifest"]["path"]).read_text(encoding="utf-8")
        )
        policy = find_policy(t190, row["checkpoint_id"])
        block_result = extract_block(t190, condition, manifest)
        blocks.append(
            {
                "condition_id": condition["id"],
                "condition_index": condition["condition_index"],
                "checkpoint_id": row["checkpoint_id"],
                "step": policy["step"],
                "fit_id": row["fit_id"],
                "cached": True,
                "reused_from_interrupted_run": True,
                "manifest": row["manifest"],
                "result": block_result,
            }
        )

    for row in recovery["missing_blocks"]:
        policy = find_policy(t190, row["checkpoint_id"])
        fit = find_fit(t190, row["fit_id"])
        if Path(row["manifest_path"]).exists():
            raise FileExistsError(
                f"missing T190B block unexpectedly exists: {row['manifest_path']}"
            )
        manifest, cached = run_or_load_block(
            t190,
            condition,
            policy,
            fit,
            CACHE,
        )
        if cached:
            raise RuntimeError("T190B missing block was unexpectedly cached")
        block_result = extract_block(t190, condition, manifest)
        manifest_path = Path(row["manifest_path"])
        blocks.append(
            {
                "condition_id": condition["id"],
                "condition_index": condition["condition_index"],
                "checkpoint_id": row["checkpoint_id"],
                "step": policy["step"],
                "fit_id": row["fit_id"],
                "cached": False,
                "reused_from_interrupted_run": False,
                "manifest": receipt(manifest_path),
                "result": block_result,
            }
        )
        print(
            json.dumps(
                {
                    "block": f"{row['checkpoint_id']}:{row['fit_id']}",
                    "green_cells": sum(
                        cell["cell_green"] for cell in block_result["cells"]
                    ),
                    "elapsed_s": time.time() - started,
                }
            ),
            flush=True,
        )

    summary = condition_summary(condition, blocks)
    passed = bool(summary["condition_green"])
    basis_result: dict[str, Any] = {
        "schema_version": (
            "open_duck.t190b_interrupted_execution_recovery_result.v1"
        ),
        "status": (
            "PASS_T190B_INTERRUPTED_EXECUTION_RECOVERY"
            if passed
            else "HOLD_T190B_INTERRUPTED_EXECUTION_RECOVERY"
        ),
        "decision": (
            recovery["decision_rule"]["pass_decision"]
            if passed
            else recovery["decision_rule"]["fail_decision"]
        ),
        "preregistered_contract_sha256": recovery[
            "preregistered_contract_sha256"
        ],
        "condition": summary,
        "blocks": blocks,
        "execution": {
            "behavior_cells_total": 16,
            "behavior_cells_reused": 8,
            "behavior_cells_executed_now": 8,
            "wall_seconds_now": time.time() - started,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "full_r2_preregistration": passed,
            "training": False,
            "colab": False,
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
        "# T190B interrupted-execution recovery result\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Decision: `{value['decision']}`\n"
        f"- Green cells: `{summary['green_cells']}/16`\n"
        "- Reused / executed now: `8/8` cells\n"
        f"- Worst tracking p95: "
        f"`{summary['worst_tracking_p95_rad']:.9f}`\n"
        f"- Minimum moving vx: "
        f"`{summary['minimum_moving_vx_m_s']:.9f}`\n"
        "- Training / Colab / robot: `0/0/0`\n"
        f"- Result SHA-256: `{value['result_sha256']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"decision={value['decision']}")
    print(f"result_sha256={value['result_sha256']}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
