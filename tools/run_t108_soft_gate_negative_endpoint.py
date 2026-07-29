#!/usr/bin/env python3
"""Run the frozen continuous-gate negative-COM endpoint matrix."""

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
PREREG = ANALYSIS / "t108_soft_gate_negative_endpoint_preregistration.json"
RESULT = ANALYSIS / "t108_soft_gate_negative_endpoint_result.json"
MARKDOWN = ANALYSIS / "T108_SOFT_GATE_NEGATIVE_ENDPOINT_RESULT_20260728.md"
DEFAULT_CACHE_ROOT = Path(
    "D:/CodexArtifacts/open-duck-policy/t108_soft_gate_negative_endpoint_v1"
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
        raise RuntimeError(f"T108 frozen receipt changed: {label}={path}")


def load_preregistration() -> dict[str, Any]:
    value = json.loads(PREREG.read_text(encoding="utf-8"))
    if (
        value.get("status")
        != "PREREGISTERED_T108_SOFT_GATE_NEGATIVE_ENDPOINT"
        or value.get("failed_checks")
        or canonical_sha256(value, "preregistered_contract_sha256")
        != value.get("preregistered_contract_sha256")
    ):
        raise RuntimeError("T108 preregistration changed")
    for label, item in value["repository_inputs"].items():
        verify_receipt(item, label)
    for item in [
        *value["policies"],
        *value["fits"],
        value["calibrator"],
        value["reference_feature_table"],
        value["playground"]["manifest"],
    ]:
        verify_receipt(item, item.get("checkpoint_id", item["path"]))
    plan = matrix_plan(
        [value["condition"]],
        value["policies"],
        value["fits"],
        value["commands_x_m_s"],
        int(value["seed"]),
    )
    if (
        len(plan) != int(value["matrix"]["cells"])
        or canonical_sha256({"plan": plan}, "unused")
        != value["matrix"]["plan_sha256"]
    ):
        raise RuntimeError("T108 matrix plan changed")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    parser.add_argument(
        "--cache-root", type=Path, default=DEFAULT_CACHE_ROOT
    )
    args = parser.parse_args()
    if RESULT.exists() or MARKDOWN.exists():
        raise FileExistsError("refusing to overwrite T108 result")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T108 formal execution requires a clean worktree")
    prereg = load_preregistration()
    cache_root = args.cache_root.resolve()
    cache_root.mkdir(parents=True, exist_ok=True)
    started = time.time()
    blocks: list[dict[str, Any]] = []
    cache_hits = 0
    new_blocks = 0
    for policy in prereg["policies"]:
        for fit in prereg["fits"]:
            manifest, cached = run_or_load_block(
                prereg,
                prereg["condition"],
                policy,
                fit,
                cache_root,
            )
            block_result = extract_block(
                prereg, prereg["condition"], manifest
            )
            manifest_path = (
                cache_root
                / (
                    f"{int(prereg['condition']['condition_index']):02d}_"
                    f"{prereg['condition']['id']}"
                )
                / policy["checkpoint_id"]
                / fit["fit_id"]
                / "manifest.json"
            )
            block = {
                "condition_id": prereg["condition"]["id"],
                "condition_index": prereg["condition"]["condition_index"],
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
    summary = condition_summary(prereg["condition"], blocks)
    passed = bool(summary["condition_green"])
    result: dict[str, Any] = {
        "schema_version": (
            "open_duck.t108_soft_gate_negative_endpoint_result.v1"
        ),
        "status": (
            "PASS_T108_SOFT_GATE_NEGATIVE_ENDPOINT"
            if passed
            else "HOLD_T108_SOFT_GATE_NEGATIVE_ENDPOINT"
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
            "negative_endpoint_repaired": passed,
            "both_checkpoints_persistent": passed,
            "hosted_run_earned": False,
            "gate5_open": False,
        },
        "authority": {
            "t109_full_r2_preregistration": passed,
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
                "# T108 continuous-gate negative endpoint result",
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
