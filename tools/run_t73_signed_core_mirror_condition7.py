#!/usr/bin/env python3
"""Run T72's sole 16-cell signed-mirror condition-7 falsifier."""

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
PREREG = ANALYSIS / "t73_signed_core_mirror_condition7_preregistration.json"
RESULT = ANALYSIS / "t73_signed_core_mirror_condition7_result.json"
RESULT_MD = ANALYSIS / "T73_SIGNED_CORE_MIRROR_CONDITION7_RESULT_20260728.md"
CACHE_ROOT = (
    Path("D:/CodexArtifacts/open-duck-policy")
    / "t73_signed_core_mirror_condition7_v1"
)
sys.path.insert(0, str(ROOT / "tools"))
from run_t27_t23_robustness_matrix import (  # noqa: E402
    condition_summary,
    extract_block,
    run_or_load_block,
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


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
    if (
        actual != expected
        or prereg["status"]
        != "PREREGISTERED_T73_SIGNED_CORE_MIRROR_CONDITION7"
        or prereg["failed_checks"]
    ):
        raise ValueError("changed or invalid T73 preregistration")
    for item in prereg["frozen_inputs"].values():
        path = Path(item["path"])
        if not path.is_file() or sha256(path) != item["sha256"]:
            raise ValueError(f"changed frozen T73 input: {path}")
    for item in [
        *prereg["policies"],
        *prereg["fits"],
        prereg["calibrator"],
        prereg["reference_feature_table"],
    ]:
        path = Path(item["path"])
        if (
            not path.is_file()
            or path.stat().st_size != item["bytes"]
            or sha256(path) != item["sha256"]
        ):
            raise ValueError(f"changed T73 evaluated input: {path}")


def require_clean_worktree() -> str:
    status = subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    )
    if status.strip():
        raise RuntimeError("formal T73 execution requires a clean worktree")
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()


def write_markdown(result: Mapping[str, Any]) -> None:
    condition = result["condition"]
    RESULT_MD.write_text(
        "\n".join(
            [
                "# T73 signed recurrent-core mirror condition-7 result",
                "",
                f"- Status: `{result['status']}`",
                f"- Decision: `{result['decision']}`",
                f"- Green cells: `{condition['green_cells']}/16`",
                (
                    "- Worst tracking p95: "
                    f"`{condition['worst_tracking_p95_rad']:.9f} rad`"
                ),
                (
                    "- Minimum moving vx: "
                    f"`{condition['minimum_moving_vx_m_s']:.9f} m/s`"
                ),
                "",
                "Training, Colab, Gate 5, RDK-X5, and robot access remain closed.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if not args.execute:
        raise PermissionError("T73 formal behavior requires --execute")
    for path in (RESULT, RESULT_MD, CACHE_ROOT):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T73: {path}")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    verify_preregistration(prereg)
    commit = require_clean_worktree()
    condition = prereg["condition"]
    blocks: list[dict[str, Any]] = []
    started = time.time()
    for policy in prereg["policies"]:
        for fit in prereg["fits"]:
            manifest, cached = run_or_load_block(
                prereg, condition, policy, fit, CACHE_ROOT
            )
            manifest_path = (
                CACHE_ROOT
                / f"{int(condition['condition_index']):02d}_{condition['id']}"
                / policy["checkpoint_id"]
                / fit["fit_id"]
                / "manifest.json"
            )
            blocks.append(
                {
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
            )
    summary = condition_summary(condition, blocks)
    passed = summary["condition_green"]
    result: dict[str, Any] = {
        "schema_version": "open_duck.t73_signed_core_mirror_condition7_result.v1",
        "status": (
            "PASS_T73_SIGNED_CORE_MIRROR_CONDITION7"
            if passed
            else "HOLD_T73_SIGNED_CORE_MIRROR_CONDITION7"
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
        "execution": {
            "cpu_only": True,
            "formal_behavior_cells": 16,
            "wall_seconds": time.time() - started,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "nominal_preregistration": passed,
            "training": False,
            "colab": False,
            "gate5": False,
            "rdkx5_or_robot": False,
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
    print(f"green_cells={summary['green_cells']}/16")
    print(f"minimum_moving_vx_m_s={summary['minimum_moving_vx_m_s']}")
    print(f"result_sha256={result['result_sha256']}")
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
