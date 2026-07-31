#!/usr/bin/env python3
"""Run the always-on expert's frozen negative-COM matrix."""

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
PREREG = ANALYSIS / "t111_always_on_negative_endpoint_preregistration.json"
RESULT = ANALYSIS / "t111_always_on_negative_endpoint_result.json"
MARKDOWN = ANALYSIS / "T111_ALWAYS_ON_NEGATIVE_ENDPOINT_RESULT_20260729.md"
CACHE = Path(
    "D:/CodexArtifacts/open-duck-policy/t111_always_on_negative_endpoint_v1"
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
        raise RuntimeError(f"changed T111 input: {path}")


def load() -> dict[str, Any]:
    value = json.loads(PREREG.read_text(encoding="utf-8"))
    if (
        value["status"]
        != "PREREGISTERED_T111_ALWAYS_ON_NEGATIVE_ENDPOINT"
        or value["failed_checks"]
        or canonical_sha256(value, "preregistered_contract_sha256")
        != value["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T111 preregistration changed")
    for item in value["repository_inputs"].values():
        verify(item)
    for item in [
        *value["policies"],
        *value["fits"],
        value["calibrator"],
        value["reference_feature_table"],
        value["playground"]["manifest"],
    ]:
        verify(item)
    plan = matrix_plan(
        [value["condition"]],
        value["policies"],
        value["fits"],
        value["commands_x_m_s"],
        int(value["seed"]),
    )
    if (
        len(plan) != 16
        or canonical_sha256({"plan": plan}, "unused")
        != value["matrix"]["plan_sha256"]
    ):
        raise RuntimeError("T111 matrix plan changed")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    args = parser.parse_args()
    if RESULT.exists() or MARKDOWN.exists() or CACHE.exists():
        raise FileExistsError("refusing to overwrite T111 output")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T111 execution requires clean worktree")
    prereg = load()
    CACHE.mkdir(parents=True)
    condition = prereg["condition"]
    blocks = []
    started = time.time()
    for policy in prereg["policies"]:
        for fit in prereg["fits"]:
            manifest, cached = run_or_load_block(
                prereg, condition, policy, fit, CACHE
            )
            result = extract_block(prereg, condition, manifest)
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
                    "result": result,
                }
            )
            print(
                json.dumps(
                    {
                        "block": (
                            f"{policy['checkpoint_id']}:{fit['fit_id']}"
                        ),
                        "green_cells": sum(
                            cell["cell_green"] for cell in result["cells"]
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
            "open_duck.t111_always_on_negative_endpoint_result.v1"
        ),
        "status": (
            "PASS_T111_ALWAYS_ON_NEGATIVE_ENDPOINT"
            if passed
            else "HOLD_T111_ALWAYS_ON_NEGATIVE_ENDPOINT"
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
        "interpretation": {
            "universal_expert_candidate": passed,
            "both_checkpoints_persistent": passed,
            "hosted_run_earned": False,
            "gate5_open": False,
        },
        "authority": {
            "t112_full_r2_preregistration": passed,
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
        "# T111 always-on negative endpoint result\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Decision: `{value['decision']}`\n"
        f"- Green cells: `{summary['green_cells']}/16`\n"
        f"- Minimum moving vx: `{summary['minimum_moving_vx_m_s']:.9f}`\n"
        f"- Worst tracking p95: `{summary['worst_tracking_p95_rad']:.9f}`\n"
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
