#!/usr/bin/env python3
"""Run T40's exact recovery of T39's two missing nominal blocks."""

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
PREREG = ANALYSIS / "t40_t39_exact_recovery_preregistration.json"
SOURCE_PREREG = (
    ANALYSIS
    / "t39_uniform_normalizer_rollback_nominal_preregistration.json"
)
RESULT = ANALYSIS / "t40_t39_exact_recovery_result.json"
RESULT_MD = ANALYSIS / "T40_T39_EXACT_RECOVERY_RESULT_20260728.md"
CACHE_ROOT = (
    Path("D:/CodexArtifacts/open-duck-policy")
    / "t39_uniform_normalizer_rollback_nominal_v1"
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


def verify_canonical(value: dict, field: str) -> None:
    actual = hashlib.sha256(
        json.dumps(
            {key: item for key, item in value.items() if key != field},
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()
    if actual != value[field]:
        raise ValueError(f"changed canonical contract: {field}")


def verify_preregistration(prereg: dict, source: dict) -> None:
    verify_canonical(prereg, "preregistered_contract_sha256")
    verify_canonical(source, "preregistered_contract_sha256")
    if prereg["status"] != "PREREGISTERED_T40_T39_EXACT_RECOVERY":
        raise ValueError("T40 preregistration is not green")
    if source["status"] != (
        "PREREGISTERED_T39_UNIFORM_NORMALIZER_ROLLBACK_NOMINAL_MATRIX"
    ):
        raise ValueError("source T39 preregistration is not green")
    for item in prereg["frozen_inputs"].values():
        path = Path(item["path"])
        if sha256(path) != item["sha256"]:
            raise ValueError(f"changed frozen T40 input: {path}")
    for item in [
        *source["policies"],
        *source["fits"],
        source["calibrator"],
        source["reference_feature_table"],
    ]:
        path = Path(item["path"])
        if sha256(path) != item["sha256"]:
            raise ValueError(f"changed T40 evaluated input: {path}")


def require_clean_worktree() -> str:
    status = subprocess.run(
        ["git", "status", "--short"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    if status.strip():
        raise RuntimeError("formal T40 execution requires a clean worktree")
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def manifest_path(
    condition: Mapping[str, Any],
    policy: Mapping[str, Any],
    fit: Mapping[str, Any],
) -> Path:
    return (
        CACHE_ROOT
        / f"{int(condition['condition_index']):02d}_{condition['id']}"
        / str(policy["checkpoint_id"])
        / str(fit["fit_id"])
        / "manifest.json"
    )


def verify_preexecution_cache(prereg: dict, source: dict) -> None:
    expected_completed = {
        Path(item["path"]): item["sha256"]
        for item in prereg["recovery"]["completed_manifest_receipts"]
    }
    actual = set(CACHE_ROOT.rglob("manifest.json"))
    if actual != set(expected_completed):
        raise RuntimeError("T40 preexecution manifest inventory changed")
    for path, expected_sha in expected_completed.items():
        if sha256(path) != expected_sha:
            raise RuntimeError(f"changed immutable T39 manifest: {path}")
    for item in prereg["recovery"]["missing_blocks"]:
        if Path(item["manifest_path"]).exists():
            raise RuntimeError("T40 missing block already exists before execution")
    if (ANALYSIS / "t39_uniform_normalizer_rollback_nominal_result.json").exists():
        raise RuntimeError("unexpected T39 result appeared")
    if RESULT.exists() or RESULT_MD.exists():
        raise RuntimeError("refusing to overwrite T40 result")


def write_markdown(result: Mapping[str, Any]) -> None:
    condition = result["condition"]
    RESULT_MD.write_text(
        "\n".join(
            [
                "# T40 exact T39 recovery result",
                "",
                f"- Status: `{result['status']}`",
                f"- Aggregated green cells: `{condition['green_cells']}/16`",
                "- Reused immutable blocks: `2`",
                "- Newly executed blocks: `2`",
                (
                    "- Worst tracking p95: "
                    f"`{condition['worst_tracking_p95_rad']:.9f} rad`"
                ),
                "",
                "A pass authorizes only preregistration of the sequential "
                "R2 robustness ladder. Gate 5 and robot access remain closed.",
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
        raise SystemExit("refusing T40 recovery without --execute")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    source = json.loads(SOURCE_PREREG.read_text(encoding="utf-8"))
    verify_preregistration(prereg, source)
    verify_preexecution_cache(prereg, source)
    commit = require_clean_worktree()
    condition = source["conditions"][0]
    blocks: list[dict[str, Any]] = []
    cache_hits = 0
    new_blocks = 0
    started = time.time()
    for policy in source["policies"]:
        for fit in source["fits"]:
            manifest, cached = run_or_load_block(
                source,
                condition,
                policy,
                fit,
                CACHE_ROOT,
            )
            expected_cached = (
                policy["checkpoint_id"] == "T39_UNIFORM_NORMALIZER_HALF"
            )
            if cached != expected_cached:
                raise RuntimeError(
                    "T40 cached/new block classification changed"
                )
            path = manifest_path(condition, policy, fit)
            block = {
                "condition_id": condition["id"],
                "condition_index": condition["condition_index"],
                "checkpoint_id": policy["checkpoint_id"],
                "fit_id": fit["fit_id"],
                "cached": cached,
                "manifest": {
                    "path": str(path.resolve()),
                    "bytes": path.stat().st_size,
                    "sha256": sha256(path),
                },
                "result": extract_block(source, condition, manifest),
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
                        "cached": cached,
                        "block_green": block["result"]["block_green"],
                        "elapsed_s": time.time() - started,
                    }
                ),
                flush=True,
            )
    if cache_hits != 2 or new_blocks != 2:
        raise RuntimeError("T40 did not reuse/execute exactly 2/2 blocks")
    summary = condition_summary(condition, blocks)
    passed = summary["condition_green"]
    result: dict[str, Any] = {
        "schema_version": "open_duck.t40_t39_exact_recovery_result.v1",
        "status": (
            "PASS_T40_T39_EXACT_RECOVERY"
            if passed
            else "HOLD_T40_T39_EXACT_RECOVERY"
        ),
        "decision": (
            prereg["decision_rule"]["pass_decision"]
            if passed
            else prereg["decision_rule"]["fail_decision"]
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "source_t39_contract_sha256": source[
            "preregistered_contract_sha256"
        ],
        "repository_commit": commit,
        "condition": summary,
        "blocks": blocks,
        "execution": {
            "cpu_only": True,
            "aggregated_formal_behavior_cells": 16,
            "reused_formal_behavior_cells": 8,
            "new_formal_behavior_cells": 8,
            "cache_hits": cache_hits,
            "new_blocks": new_blocks,
            "wall_seconds_recovery": time.time() - started,
            "training_steps": 0,
            "hosted_compute_units": 0,
        },
        "authority": {
            "robustness_preregistration": passed,
            "robustness_execution": False,
            "training": False,
            "colab": False,
            "deployment": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
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
    print(f"result_sha256={result['result_sha256']}")
    print(f"sha256={sha256(RESULT)}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
