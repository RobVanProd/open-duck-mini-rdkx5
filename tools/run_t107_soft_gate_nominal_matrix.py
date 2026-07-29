#!/usr/bin/env python3
"""Run T106 soft-gate policies' frozen 16-cell nominal matrix."""

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
PREREG = ANALYSIS / "t107_soft_gate_nominal_preregistration.json"
RESULT = ANALYSIS / "t107_soft_gate_nominal_result.json"
MARKDOWN = ANALYSIS / "T107_SOFT_GATE_NOMINAL_RESULT_20260728.md"
DEFAULT_CACHE_ROOT = Path(
    "D:/CodexArtifacts/open-duck-policy/t107_soft_gate_nominal_v1"
)

sys.path.insert(0, str(ROOT / "tools"))
from run_t27_t23_robustness_matrix import (  # noqa: E402
    condition_summary,
    extract_block,
    receipt,
    run_or_load_block,
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


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


def verify_receipt(value: Mapping[str, Any], label: str) -> None:
    path = Path(value["path"])
    if (
        not path.is_file()
        or path.stat().st_size != int(value["bytes"])
        or sha256(path) != value["sha256"]
    ):
        raise RuntimeError(f"T107 frozen receipt changed: {label}={path}")


def load_preregistration() -> dict[str, Any]:
    value = json.loads(PREREG.read_text(encoding="utf-8"))
    if (
        value.get("status")
        != "PREREGISTERED_T107_SOFT_GATE_NOMINAL_MATRIX"
        or value.get("failed_checks")
        or canonical_sha256(value, "preregistered_contract_sha256")
        != value.get("preregistered_contract_sha256")
    ):
        raise RuntimeError("T107 preregistration changed")
    for label, item in value["frozen_inputs"].items():
        verify_receipt(item, label)
    for item in [
        *value["policies"],
        *value["fits"],
        value["calibrator"],
        value["reference_feature_table"],
        value["playground"]["manifest"],
    ]:
        verify_receipt(item, item.get("checkpoint_id", item["path"]))
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    parser.add_argument(
        "--cache-root", type=Path, default=DEFAULT_CACHE_ROOT
    )
    args = parser.parse_args()
    if RESULT.exists() or MARKDOWN.exists():
        raise FileExistsError("refusing to overwrite T107 result")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T107 formal execution requires a clean worktree")
    prereg = load_preregistration()
    cache_root = args.cache_root.resolve()
    cache_root.mkdir(parents=True, exist_ok=True)
    condition = prereg["conditions"][0]
    started = time.time()
    blocks: list[dict[str, Any]] = []
    cache_hits = 0
    new_blocks = 0
    for policy in prereg["policies"]:
        for fit in prereg["fits"]:
            manifest, cached = run_or_load_block(
                prereg, condition, policy, fit, cache_root
            )
            block_result = extract_block(prereg, condition, manifest)
            manifest_path = (
                cache_root
                / f"{int(condition['condition_index']):02d}_{condition['id']}"
                / policy["checkpoint_id"]
                / fit["fit_id"]
                / "manifest.json"
            )
            block = {
                "condition_id": condition["id"],
                "condition_index": condition["condition_index"],
                "checkpoint_id": policy["checkpoint_id"],
                "step": policy["step"],
                "fit_id": fit["fit_id"],
                "cached": cached,
                "manifest": receipt(manifest_path),
                "result": block_result,
            }
            blocks.append(block)
            cache_hits += int(cached)
            new_blocks += int(not cached)
            print(
                json.dumps(
                    {
                        "block": (
                            f"{policy['checkpoint_id']}:{fit['fit_id']}"
                        ),
                        "green_cells": sum(
                            int(cell["cell_green"])
                            for cell in block_result["cells"]
                        ),
                        "elapsed_s": time.time() - started,
                    }
                ),
                flush=True,
            )
    summary = condition_summary(condition, blocks)
    passed = bool(summary["condition_green"])
    result: dict[str, Any] = {
        "schema_version": "open_duck.t107_soft_gate_nominal_result.v1",
        "status": (
            "PASS_T107_SOFT_GATE_NOMINAL_MATRIX"
            if passed
            else "HOLD_T107_SOFT_GATE_NOMINAL_MATRIX"
        ),
        "decision": (
            prereg["decision_rule"]["pass_decision"]
            if passed
            else prereg["decision_rule"]["fail_decision"]
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "repository_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "condition": summary,
        "blocks": blocks,
        "execution": {
            "cpu_only": True,
            "behavior_cells": 16,
            "cache_hits": cache_hits,
            "new_blocks": new_blocks,
            "wall_seconds": time.time() - started,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "interpretation": {
            "nominal_preserved": passed,
            "hosted_run_earned": False,
            "gate5_open": False,
        },
        "authority": {
            "t108_negative_endpoint_preregistration": passed,
            "training": False,
            "colab": False,
            "deployment": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    result["result_sha256"] = canonical_sha256(result, "result_sha256")
    RESULT.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T107 continuous-gate nominal result",
                "",
                f"- Status: `{result['status']}`",
                f"- Decision: `{result['decision']}`",
                (
                    "- Green cells: "
                    f"`{summary['green_cells']}/{summary['cells']}`"
                ),
                (
                    "- Worst tracking p95: "
                    f"`{summary['worst_tracking_p95_rad']:.9f} rad`"
                ),
                (
                    "- Minimum moving vx: "
                    f"`{summary['minimum_moving_vx_m_s']:.9f} m/s`"
                ),
                "- Training / Colab / robot: `0 / 0 / 0`",
                "",
            ]
        ),
        encoding="utf-8",
        newline="\n",
    )
    print(result["status"])
    print(f"decision={result['decision']}")
    print(f"result_sha256={result['result_sha256']}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
