#!/usr/bin/env python3
"""Recover T249 using the correct readback extractor for each condition."""

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
PREREG = ANALYSIS / "t249b_reporter_recovery_preregistration.json"
RESULT = ANALYSIS / "t249b_reporter_recovery_result.json"
MARKDOWN = ANALYSIS / "T249B_REPORTER_RECOVERY_RESULT_20260731.md"
CACHE = Path("D:/CodexArtifacts/open-duck-policy/t249_remaining_r2_v1")
PROGRESS = CACHE / "recovery_progress.json"
sys.path.insert(0, str(ROOT / "tools"))
from run_t136_static_calibration_router_transform import (  # noqa: E402
    canonical_sha256,
    receipt,
    sha256,
)
from run_t242_bounded_router_home_offset import (  # noqa: E402
    corrected_extract_block,
)
from run_t27_t23_robustness_matrix import (  # noqa: E402
    condition_summary,
    extract_block,
    run_or_load_block,
)


def verify(value: Mapping[str, Any]) -> None:
    path = Path(value["path"])
    if (
        not path.is_file()
        or path.stat().st_size != value["bytes"]
        or sha256(path) != value["sha256"]
    ):
        raise RuntimeError(f"changed T249B input: {path}")


def load_contract(recovery: Mapping[str, Any]) -> dict[str, Any]:
    path = Path(recovery["execution_contract"]["path"])
    value = json.loads(path.read_text(encoding="utf-8"))
    basis = {
        key: item
        for key, item in value.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        value["status"] != "PREREGISTERED_T249_REMAINING_R2"
        or value["failed_checks"]
        or canonical_sha256(basis)
        != value["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T249 execution contract changed")
    for item in [
        *value["repository_inputs"].values(),
        *value["policies"],
        *value["fits"],
        value["calibrator"],
        value["reference_feature_table"],
        value["playground"]["manifest"],
        value["reused_evidence"]["conditions_1_through_16"],
        value["reused_evidence"]["condition_17"],
    ]:
        verify(item)
    return value


def inherited_conditions(contract: Mapping[str, Any]) -> list[dict[str, Any]]:
    t237 = json.loads(
        Path(
            contract["reused_evidence"]["conditions_1_through_16"]["path"]
        ).read_text(encoding="utf-8")
    )
    t248 = json.loads(
        Path(contract["reused_evidence"]["condition_17"]["path"]).read_text(
            encoding="utf-8"
        )
    )
    rows = [dict(row) for row in t237["conditions"][:16]]
    rows.append(dict(t248["condition"]))
    return rows


def load_progress_seed(recovery: Mapping[str, Any]) -> list[dict[str, Any]]:
    receipt_value = (
        receipt(PROGRESS)
        if PROGRESS.is_file()
        else recovery["condition_18_progress"]
    )
    verify(receipt_value)
    value = json.loads(
        Path(receipt_value["path"]).read_text(encoding="utf-8")
    )
    rows = [dict(row) for row in value["new_conditions"]]
    if (
        not rows
        or rows[0]["condition_id"] != "HOME_JOINT_OFFSET_POS"
        or not all(row["condition_green"] for row in rows)
    ):
        raise RuntimeError("T249B progress seed changed")
    return rows


def manifest_path(
    condition: Mapping[str, Any],
    policy: Mapping[str, Any],
    fit: Mapping[str, Any],
) -> Path:
    return (
        CACHE
        / f"{int(condition['condition_index']):02d}_{condition['id']}"
        / str(policy["checkpoint_id"])
        / str(fit["fit_id"])
        / "manifest.json"
    )


def all_manifest_receipts(
    contract: Mapping[str, Any],
    condition_ids: set[str],
) -> list[dict[str, Any]]:
    rows = []
    for condition in contract["remaining_conditions"]:
        if condition["id"] not in condition_ids:
            continue
        for policy in contract["policies"]:
            for fit in contract["fits"]:
                rows.append(
                    {
                        "condition_id": condition["id"],
                        "checkpoint_id": policy["checkpoint_id"],
                        "fit_id": fit["fit_id"],
                        "manifest": receipt(
                            manifest_path(condition, policy, fit)
                        ),
                    }
                )
    return rows


def write_progress(
    recovery: Mapping[str, Any],
    contract: Mapping[str, Any],
    rows: list[dict[str, Any]],
    *,
    cache_hits: int,
    new_blocks: int,
    wall_seconds: float,
) -> None:
    ids = {row["condition_id"] for row in rows}
    basis: dict[str, Any] = {
        "schema_version": "open_duck.t249b_reporter_recovery_progress.v1",
        "status": "IN_PROGRESS_T249B_REPORTER_RECOVERY",
        "preregistered_contract_sha256": recovery[
            "preregistered_contract_sha256"
        ],
        "completed_new_conditions": len(rows),
        "expected_new_conditions": 3,
        "new_conditions": rows,
        "block_manifests": all_manifest_receipts(contract, ids),
        "cache_hits_this_invocation": cache_hits,
        "new_blocks_this_invocation": new_blocks,
        "wall_seconds_this_invocation": wall_seconds,
        "selection_or_decision_made": False,
        "optimizer_steps": 0,
        "hosted_compute_units": 0,
        "robot_or_rdk_access": 0,
    }
    value = {**basis, "progress_sha256": canonical_sha256(basis)}
    PROGRESS.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def finalize(
    recovery: Mapping[str, Any],
    contract: Mapping[str, Any],
    conditions: list[dict[str, Any]],
    *,
    started: float,
) -> int:
    complete = len(conditions) == 20
    all_green = complete and all(row["condition_green"] for row in conditions)
    first_failed = next(
        (
            row["condition_id"]
            for row in conditions
            if not row["condition_green"]
        ),
        None,
    )
    completed_ids = {
        row["condition_id"]
        for row in conditions
        if int(row["condition_index"]) >= 18
    }
    basis: dict[str, Any] = {
        "schema_version": "open_duck.t249b_reporter_recovery_result.v1",
        "status": (
            "PASS_T249B_REPORTER_RECOVERY"
            if all_green
            else "HOLD_T249B_REPORTER_RECOVERY"
        ),
        "decision": (
            recovery["decision_rule"]["pass"]
            if all_green
            else recovery["decision_rule"]["fail"]
        ),
        "preregistered_contract_sha256": recovery[
            "preregistered_contract_sha256"
        ],
        "summary": {
            "expected_conditions": 20,
            "completed_conditions": len(conditions),
            "green_conditions": sum(
                bool(row["condition_green"]) for row in conditions
            ),
            "matrix_complete": complete,
            "completed_cells": sum(int(row["cells"]) for row in conditions),
            "green_cells": sum(
                int(row["green_cells"]) for row in conditions
            ),
            "all_twenty_conditions_green": all_green,
            "first_failed_condition": first_failed,
        },
        "conditions": conditions,
        "block_manifests": all_manifest_receipts(
            contract, completed_ids
        ),
        "recovery": {
            "reporter_only": True,
            "condition_18_reused": True,
            "condition_19_half_p30_reused": True,
            "completed_cells_rerun": 0,
        },
        "execution": {
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
            "wall_seconds_final_invocation": time.time() - started,
        },
        "authority": {
            "offline_deployment_contract_audit_preregistration": all_green,
            "training": False,
            "hosted": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    value = {**basis, "result_sha256": canonical_sha256(basis)}
    RESULT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    lines = [
        "# T249B reporter recovery result",
        "",
        f"- Status: `{value['status']}`",
        f"- Decision: `{value['decision']}`",
        f"- Green conditions: `{value['summary']['green_conditions']}/20`",
        f"- Green cells: `{value['summary']['green_cells']}/"
        f"{value['summary']['completed_cells']}`",
        f"- First failure: `{value['summary']['first_failed_condition']}`",
        f"- Frozen manifests: `{len(value['block_manifests'])}`",
        "- Completed cells rerun: `0`",
        "- Optimizer/hosted/robot: `0/0/0`",
        f"- Result SHA-256: `{value['result_sha256']}`",
    ]
    MARKDOWN.write_text(
        "\n".join(lines) + "\n", encoding="utf-8", newline="\n"
    )
    print(value["status"])
    print(f"decision={value['decision']}")
    print(f"green_conditions={value['summary']['green_conditions']}/20")
    print(f"result_sha256={value['result_sha256']}")
    return 0 if all_green else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    parser.parse_args()
    if RESULT.exists() or MARKDOWN.exists():
        raise FileExistsError("refusing to overwrite T249B result")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T249B execution requires clean worktree")
    recovery = json.loads(PREREG.read_text(encoding="utf-8"))
    basis = {
        key: value
        for key, value in recovery.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        recovery["status"] != "PREREGISTERED_T249B_REPORTER_RECOVERY"
        or recovery["failed_checks"]
        or canonical_sha256(basis)
        != recovery["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T249B preregistration changed")
    for item in recovery["frozen_inputs"].values():
        verify(item)
    contract = load_contract(recovery)
    inherited = inherited_conditions(contract)
    prior_new = load_progress_seed(recovery)
    completed_ids = {row["condition_id"] for row in prior_new}
    current_new = list(prior_new)
    started = time.time()
    cache_hits = 0
    new_blocks = 0

    for condition in contract["remaining_conditions"]:
        if condition["id"] in completed_ids:
            continue
        blocks: list[dict[str, Any]] = []
        condition_had_new_block = False
        for policy in contract["policies"]:
            for fit in contract["fits"]:
                manifest, cached = run_or_load_block(
                    contract, condition, policy, fit, CACHE
                )
                extractor = (
                    corrected_extract_block
                    if "joint_qpos0_offset_rad" in condition["override"]
                    else extract_block
                )
                manifest_alias = {
                    **manifest,
                    "evaluation_path": manifest["evaluation"]["path"],
                }
                block_result = extractor(
                    contract, condition, manifest_alias
                )
                blocks.append(
                    {
                        "condition_index": condition["condition_index"],
                        "condition_id": condition["id"],
                        "checkpoint_id": policy["checkpoint_id"],
                        "step": policy["step"],
                        "fit_id": fit["fit_id"],
                        "cached": cached,
                        "manifest": receipt(
                            manifest_path(condition, policy, fit)
                        ),
                        "result": block_result,
                    }
                )
                cache_hits += int(cached)
                new_blocks += int(not cached)
                condition_had_new_block |= not cached
                print(
                    json.dumps(
                        {
                            "condition": condition["id"],
                            "block": (
                                f"{policy['checkpoint_id']}:{fit['fit_id']}"
                            ),
                            "block_green": block_result["block_green"],
                            "cached": cached,
                            "elapsed_s": time.time() - started,
                        }
                    ),
                    flush=True,
                )
        summary = condition_summary(condition, blocks)
        current_new.append(summary)
        conditions = inherited + current_new
        print(
            json.dumps(
                {
                    "completed_new_conditions": len(current_new),
                    "condition": condition["id"],
                    "green_cells": summary["green_cells"],
                    "condition_green": summary["condition_green"],
                    "elapsed_s": time.time() - started,
                }
            ),
            flush=True,
        )
        if not summary["condition_green"]:
            return finalize(
                recovery, contract, conditions, started=started
            )
        if condition_had_new_block and len(current_new) < 3:
            write_progress(
                recovery,
                contract,
                current_new,
                cache_hits=cache_hits,
                new_blocks=new_blocks,
                wall_seconds=time.time() - started,
            )
            print("IN_PROGRESS_T249B_REPORTER_RECOVERY")
            print(f"green_conditions={len(conditions)}/20")
            print(f"progress={PROGRESS}")
            print(f"progress_sha256={receipt(PROGRESS)['sha256']}")
            return 0

    return finalize(
        recovery, contract, inherited + current_new, started=started
    )


if __name__ == "__main__":
    raise SystemExit(main())
