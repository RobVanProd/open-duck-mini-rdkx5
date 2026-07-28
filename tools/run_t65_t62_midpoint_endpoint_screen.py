#!/usr/bin/env python3
"""Run the preregistered T62 midpoint-endpoint causal screen."""

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
    ANALYSIS / "t65_t62_midpoint_endpoint_screen_preregistration_v2.json"
)
RESULT = ANALYSIS / "t65_t62_midpoint_endpoint_screen_result.json"
RESULT_MD = (
    ANALYSIS / "T65_T62_MIDPOINT_ENDPOINT_SCREEN_RESULT_20260728.md"
)
CACHE_ROOT = (
    Path("D:/CodexArtifacts/open-duck-policy")
    / "t65_t62_midpoint_endpoint_screen_v1"
)

sys.path.insert(0, str(ROOT / "tools"))
from run_t27_t23_robustness_matrix import (  # noqa: E402
    condition_summary,
    extract_block,
    run_or_load_block,
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: Any) -> str:
    payload = dict(value)
    payload.pop("result_sha256", None)
    return hashlib.sha256(
        json.dumps(
            payload,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def verify_preregistration(prereg: dict[str, Any]) -> None:
    expected = prereg["preregistered_contract_sha256"]
    actual = hashlib.sha256(
        json.dumps(
            {
                key: value
                for key, value in prereg.items()
                if key != "preregistered_contract_sha256"
            },
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()
    if actual != expected:
        raise ValueError("changed T65 preregistration")
    if prereg["status"] != (
        "PREREGISTERED_T65_T62_MIDPOINT_ENDPOINT_SCREEN_V2"
    ):
        raise ValueError("T65 preregistration is not green")
    for item in prereg["frozen_inputs"].values():
        path = Path(item["path"])
        if sha256(path) != item["sha256"]:
            raise ValueError(f"changed frozen T65 input: {path}")
    for item in [
        prereg["policy"],
        *prereg["fits"],
        prereg["calibrator"],
        prereg["reference_feature_table"],
    ]:
        path = Path(item["path"])
        if sha256(path) != item["sha256"]:
            raise ValueError(f"changed T65 evaluated input: {path}")


def require_clean_worktree() -> str:
    status = subprocess.check_output(
        ["git", "status", "--porcelain"],
        cwd=ROOT,
        text=True,
    )
    if status.strip():
        raise RuntimeError("formal T65 execution requires a clean worktree")
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        text=True,
    ).strip()


def write_markdown(result: Mapping[str, Any]) -> None:
    summary = result["condition"]
    RESULT_MD.write_text(
        "\n".join(
            [
                "# T65 T62 midpoint-endpoint screen result",
                "",
                f"- Status: `{result['status']}`",
                f"- Decision: `{result['decision']}`",
                f"- Green cells: `{summary['green_cells']}/8`",
                (
                    "- Worst tracking p95: "
                    f"`{summary['worst_tracking_p95_rad']:.9f} rad`"
                ),
                "- Selection weight: `0`",
                "- Policy promotion / training / Colab / robot: `0/0/0/0`",
                "",
                (
                    "This is a causal diagnostic of the midpoint objective, "
                    "not a deployable-checkpoint selection."
                ),
                "",
            ]
        ),
        encoding="utf-8",
        newline="\n",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if not args.execute:
        raise SystemExit("refusing outcome execution without --execute")
    if RESULT.exists() or RESULT_MD.exists():
        raise FileExistsError("refusing to overwrite formal T65 result")

    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    verify_preregistration(prereg)
    commit = require_clean_worktree()
    condition = prereg["conditions"][0]
    policy = prereg["policy"]
    blocks: list[dict[str, Any]] = []
    started = time.time()
    for fit in prereg["fits"]:
        manifest, cached = run_or_load_block(
            prereg,
            condition,
            policy,
            fit,
            CACHE_ROOT,
        )
        manifest_path = (
            CACHE_ROOT
            / f"{int(condition['condition_index']):02d}_{condition['id']}"
            / policy["checkpoint_id"]
            / fit["fit_id"]
            / "manifest.json"
        )
        block = {
            "condition_id": condition["id"],
            "condition_index": condition["condition_index"],
            "checkpoint_id": policy["checkpoint_id"],
            "fit_id": fit["fit_id"],
            "cached": cached,
            "manifest": {
                "path": str(manifest_path.resolve()),
                "bytes": manifest_path.stat().st_size,
                "sha256": sha256(manifest_path),
            },
            "result": extract_block(prereg, condition, manifest),
        }
        blocks.append(block)
        print(
            json.dumps(
                {
                    "block": f"{policy['checkpoint_id']}:{fit['fit_id']}",
                    "block_green": block["result"]["block_green"],
                    "elapsed_s": time.time() - started,
                }
            ),
            flush=True,
        )
    summary = condition_summary(condition, blocks)
    passed = summary["condition_green"] and summary["green_cells"] == 8
    result: dict[str, Any] = {
        "schema_version": (
            "open_duck.t65_t62_midpoint_endpoint_screen_result.v1"
        ),
        "status": (
            "PASS_T65_T62_MIDPOINT_ENDPOINT_SCREEN"
            if passed
            else "HOLD_T65_T62_MIDPOINT_ENDPOINT_SCREEN"
        ),
        "decision": (
            prereg["decision_rule"]["pass_decision"]
            if passed
            else prereg["decision_rule"]["fail_decision"]
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "repository_commit": commit,
        "condition": summary,
        "blocks": blocks,
        "finding": (
            "The midpoint-objective endpoint passes the complete nominal "
            "screen; later full-transfer optimization caused the observed "
            "regression."
            if passed
            else
            "The midpoint-objective endpoint is not a complete nominal "
            "policy, so later full-transfer optimization is not the sole "
            "cause and the balance-first reward-homotopy family closes."
        ),
        "execution": {
            "cpu_only": True,
            "formal_behavior_cells": 8,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "wall_seconds": time.time() - started,
        },
        "authority": {
            "t66_cpu_contract_preregistration": passed,
            "training": False,
            "colab": False,
            "policy_promotion": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    result["result_sha256"] = canonical_sha256(result)
    RESULT.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    write_markdown(result)
    print(result["status"])
    print(f"decision={result['decision']}")
    print(f"result_sha256={result['result_sha256']}")
    print(f"sha256={sha256(RESULT)}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
