#!/usr/bin/env python3
"""Complete T116 by reusing its frozen blocks and running only missing blocks."""

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
RECOVERY = ANALYSIS / "t116b_interrupted_nominal_recovery_preregistration.json"
T116 = ANALYSIS / "t116_t113_nominal_preregistration.json"
RESULT = ANALYSIS / "t116b_interrupted_nominal_recovery_result.json"
MARKDOWN = ANALYSIS / "T116B_INTERRUPTED_NOMINAL_RECOVERY_RESULT_20260729.md"
CACHE = Path("D:/CodexArtifacts/open-duck-policy/t116_t113_nominal_v1")
sys.path.insert(0, str(ROOT / "tools"))
from run_t27_t23_robustness_matrix import (  # noqa: E402
    condition_summary,
    extract_block,
    receipt,
    run_or_load_block,
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: Any, ignored: str) -> str:
    payload = dict(value)
    payload.pop(ignored, None)
    return hashlib.sha256(
        json.dumps(
            payload,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def verify(value: Mapping[str, Any]) -> None:
    path = Path(value["path"])
    if (
        not path.is_file()
        or path.stat().st_size != value["bytes"]
        or sha256(path) != value["sha256"]
    ):
        raise RuntimeError(f"changed T116B input: {path}")


def load() -> tuple[dict[str, Any], dict[str, Any]]:
    recovery = json.loads(RECOVERY.read_text(encoding="utf-8"))
    if (
        recovery["status"]
        != "PREREGISTERED_T116B_INTERRUPTED_NOMINAL_RECOVERY"
        or recovery["failed_checks"]
        or canonical_sha256(recovery, "preregistered_contract_sha256")
        != recovery["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T116B recovery preregistration changed")
    for item in recovery["frozen_inputs"].values():
        verify(item)
    for item in recovery["cached_blocks"]:
        verify(item["manifest"])
    t116 = json.loads(T116.read_text(encoding="utf-8"))
    if (
        t116["preregistered_contract_sha256"]
        != recovery["source_contract_sha256"]
    ):
        raise RuntimeError("T116 source contract changed")
    for item in t116["frozen_inputs"].values():
        verify(item)
    for item in [
        *t116["policies"],
        *t116["fits"],
        t116["calibrator"],
        t116["reference_feature_table"],
        t116["playground"]["manifest"],
    ]:
        verify(item)
    return recovery, t116


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    parser.parse_args()
    if RESULT.exists() or MARKDOWN.exists():
        raise FileExistsError("refusing to overwrite T116B output")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T116B execution requires clean worktree")
    recovery, prereg = load()
    condition = prereg["conditions"][0]
    blocks = []
    started = time.time()
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
                        "cached": cached,
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
            "open_duck.t116b_interrupted_nominal_recovery_result.v1"
        ),
        "status": (
            "PASS_T116B_T113_NOMINAL_MATRIX"
            if passed
            else "HOLD_T116B_T113_NOMINAL_MATRIX"
        ),
        "decision": (
            prereg["decision_rule"]["pass_decision"]
            if passed
            else prereg["decision_rule"]["fail_decision"]
        ),
        "recovery_contract_sha256": recovery[
            "preregistered_contract_sha256"
        ],
        "source_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "condition": summary,
        "blocks": blocks,
        "execution": {
            "behavior_cells_total": 16,
            "cached_behavior_cells": 8,
            "new_behavior_cells": 8,
            "wall_seconds": time.time() - started,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "t117_negative_endpoint_preregistration": passed,
            "training": False,
            "colab": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    value["result_sha256"] = canonical_sha256(value, "result_sha256")
    RESULT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T116B interrupted nominal recovery result\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Decision: `{value['decision']}`\n"
        f"- Green cells: `{summary['green_cells']}/16`\n"
        f"- Worst tracking p95: `{summary['worst_tracking_p95_rad']:.9f}`\n"
        "- Cached / newly run cells: `8 / 8`\n"
        "- Training / Colab / robot: `0 / 0 / 0`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"decision={value['decision']}")
    print(f"result_sha256={value['result_sha256']}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
