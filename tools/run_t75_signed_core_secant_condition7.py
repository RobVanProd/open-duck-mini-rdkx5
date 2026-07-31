#!/usr/bin/env python3
"""Run T74's sole 16-cell negative-secant condition-7 matrix."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "t75_signed_core_secant_condition7_preregistration.json"
RESULT = ANALYSIS / "t75_signed_core_secant_condition7_result.json"
MARKDOWN = ANALYSIS / "T75_SIGNED_CORE_SECANT_CONDITION7_RESULT_20260728.md"
CACHE_ROOT = (
    Path("D:/CodexArtifacts/open-duck-policy")
    / "t75_signed_core_secant_condition7_v1"
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


def verify_prereg(prereg: dict[str, Any]) -> None:
    actual = hashlib.sha256(
        json.dumps(
            {
                key: item
                for key, item in prereg.items()
                if key != "preregistered_contract_sha256"
            },
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()
    if (
        actual != prereg["preregistered_contract_sha256"]
        or prereg["status"]
        != "PREREGISTERED_T75_SIGNED_CORE_SECANT_CONDITION7"
        or prereg["failed_checks"]
    ):
        raise RuntimeError("changed or invalid T75 preregistration")
    for item in prereg["frozen_inputs"].values():
        path = Path(item["path"])
        if not path.is_file() or sha256(path) != item["sha256"]:
            raise RuntimeError(f"changed T75 frozen input: {path}")
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
            raise RuntimeError(f"changed T75 evaluated input: {path}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if not args.execute:
        raise PermissionError("T75 formal behavior requires --execute")
    for path in (RESULT, MARKDOWN, CACHE_ROOT):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T75: {path}")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    verify_prereg(prereg)
    status = subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    )
    if status.strip():
        raise RuntimeError("T75 execution requires a clean worktree")
    commit = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()
    condition = prereg["condition"]
    blocks = []
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
    value: dict[str, Any] = {
        "schema_version": "open_duck.t75_signed_core_secant_condition7_result.v1",
        "status": (
            "PASS_T75_SIGNED_CORE_SECANT_CONDITION7"
            if passed
            else "HOLD_T75_SIGNED_CORE_SECANT_CONDITION7"
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
    value["result_sha256"] = canonical_sha256(value)
    RESULT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T75 signed recurrent-core secant condition-7 result",
                "",
                f"- Status: `{value['status']}`",
                f"- Decision: `{value['decision']}`",
                f"- Green cells: `{summary['green_cells']}/16`",
                (
                    "- Minimum moving vx: "
                    f"`{summary['minimum_moving_vx_m_s']:.9f} m/s`"
                ),
                "- Training / Colab / Gate5 / robot: `0/0/0/0`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(value["status"])
    print(f"decision={value['decision']}")
    print(f"green_cells={summary['green_cells']}/16")
    print(f"minimum_moving_vx_m_s={summary['minimum_moving_vx_m_s']}")
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
