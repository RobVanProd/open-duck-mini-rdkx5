#!/usr/bin/env python3
"""Run T159's frozen mechanics-compensated +COM endpoint matrix."""

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
    ANALYSIS / "t160_mechanics_positive_endpoint_preregistration.json"
)
RESULT = ANALYSIS / "t160_mechanics_positive_endpoint_result.json"
MARKDOWN = (
    ANALYSIS / "T160_MECHANICS_POSITIVE_ENDPOINT_RESULT_20260729.md"
)
CACHE = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t160_mechanics_positive_endpoint_v1"
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
        raise RuntimeError(f"changed T160 input: {path}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    parser.parse_args()
    if RESULT.exists() or MARKDOWN.exists() or CACHE.exists():
        raise FileExistsError("refusing to overwrite T160 output")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T160 execution requires clean worktree")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    basis = {
        key: item
        for key, item in prereg.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        prereg["status"]
        != "PREREGISTERED_T160_MECHANICS_POSITIVE_ENDPOINT"
        or prereg["failed_checks"]
        or canonical_sha256(basis)
        != prereg["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T160 preregistration changed")
    for item in prereg["frozen_inputs"].values():
        verify(item)
    for item in [
        *prereg["repository_inputs"].values(),
        *prereg["policies"],
        *prereg["fits"],
        prereg["calibrator"],
        prereg["reference_feature_table"],
        prereg["playground"]["manifest"],
    ]:
        verify(item)
    CACHE.mkdir(parents=True)
    condition = prereg["condition"]
    blocks = []
    started = time.time()
    for policy in prereg["policies"]:
        for fit in prereg["fits"]:
            manifest, cached = run_or_load_block(
                prereg,
                condition,
                policy,
                fit,
                CACHE,
            )
            block_result = extract_block(
                prereg,
                condition,
                manifest,
            )
            manifest_path = (
                CACHE
                / f"{condition['condition_index']:02d}_{condition['id']}"
                / policy["checkpoint_id"]
                / fit["fit_id"]
                / "manifest.json"
            )
            blocks.append(
                {
                    "condition_id": condition["id"],
                    "condition_index": condition["condition_index"],
                    "checkpoint_id": policy["checkpoint_id"],
                    "step": policy["step"],
                    "fit_id": fit["fit_id"],
                    "cached": cached,
                    "manifest": receipt(manifest_path),
                    "result": block_result,
                }
            )
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
    summary = condition_summary(condition, blocks)
    passed = bool(summary["condition_green"])
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t160_mechanics_positive_endpoint_result.v1"
        ),
        "status": (
            "PASS_T160_MECHANICS_POSITIVE_ENDPOINT"
            if passed
            else "HOLD_T160_MECHANICS_POSITIVE_ENDPOINT"
        ),
        "decision": (
            prereg["decision_rule"]["pass_decision"]
            if passed
            else prereg["decision_rule"]["fail_decision"]
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "condition": summary,
        "blocks": blocks,
        "execution": {
            "behavior_cells": 16,
            "wall_seconds": time.time() - started,
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
    value["result_sha256"] = canonical_sha256(value)
    RESULT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T160 mechanics positive endpoint result\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Decision: `{value['decision']}`\n"
        f"- Green cells: `{summary['green_cells']}/16`\n"
        f"- Worst tracking p95: "
        f"`{summary['worst_tracking_p95_rad']:.9f}`\n"
        "- Training / Colab / robot: `0/0/0`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"decision={value['decision']}")
    print(f"result_sha256={value['result_sha256']}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
