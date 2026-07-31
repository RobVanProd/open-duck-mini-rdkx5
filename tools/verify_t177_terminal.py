#!/usr/bin/env python3
"""Independently verify the complete terminal T177 evidence graph."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREGISTRATION = (
    ANALYSIS / "t177_head_prefix_mean_full_r2_preregistration.json"
)
RESULT = ANALYSIS / "t177_head_prefix_mean_full_r2_result.json"

sys.path.insert(0, str(ROOT / "tools"))
from run_t27_t23_robustness_matrix import (  # noqa: E402
    block_contract,
    canonical_sha256,
    condition_summary,
    extract_block,
    verify_receipt,
)


class T177TerminalVerificationError(RuntimeError):
    """The terminal T177 evidence is incomplete or internally inconsistent."""


def _require(condition: object, message: str) -> None:
    if not condition:
        raise T177TerminalVerificationError(message)


def _load_json(path: Path) -> dict[str, Any]:
    _require(path.is_file(), f"missing JSON artifact: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    _require(isinstance(value, dict), f"JSON root is not an object: {path}")
    return value


def _result_hash(value: dict[str, Any]) -> str:
    basis = dict(value)
    recorded = basis.pop("result_sha256", None)
    _require(isinstance(recorded, str), "result_sha256 is missing")
    observed = canonical_sha256(basis)
    _require(
        observed == recorded,
        f"result_sha256 mismatch: observed {observed}, recorded {recorded}",
    )
    return recorded


def verify(
    preregistration_path: Path = PREREGISTRATION,
    result_path: Path = RESULT,
) -> dict[str, Any]:
    preregistration = _load_json(preregistration_path)
    result = _load_json(result_path)
    result_sha256 = _result_hash(result)

    _require(
        result.get("schema_version")
        == "open_duck.t177_head_prefix_mean_full_r2_result.v1",
        "unexpected result schema",
    )
    _require(
        result.get("preregistered_contract_sha256")
        == preregistration.get("preregistered_contract_sha256"),
        "result/preregistration contract identity differs",
    )
    _require(
        result.get("execution")
        == {
            "behavior_cells": result["summary"]["completed_cells"],
            "hosted_compute_units": 0,
            "optimizer_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "execution authority/cell accounting differs",
    )
    authority = result.get("authority", {})
    _require(
        authority.get("gate5_hardware_authorized") is False
        and authority.get("additional_training_authorized") is False
        and authority.get("rdkx5_or_robot") is False
        and authority.get("torque_or_motion") is False,
        "terminal result broadened offline authority",
    )

    preregistered_conditions = preregistration["conditions"]
    conditions = result["conditions"]
    blocks = result["blocks"]
    summary = result["summary"]
    completed = len(conditions)
    _require(completed > 0, "terminal result contains no conditions")
    _require(
        completed == summary["completed_conditions"],
        "completed-condition count differs",
    )
    _require(
        summary["expected_conditions"] == len(preregistered_conditions) == 20,
        "expected-condition count differs",
    )
    _require(
        len(blocks) == completed * 4,
        "terminal result does not contain four blocks per condition",
    )
    _require(
        summary["completed_cells"] == completed * 16,
        "terminal result does not contain sixteen cells per condition",
    )

    expected_condition_prefix = preregistered_conditions[:completed]
    for expected, observed in zip(
        expected_condition_prefix, conditions, strict=True
    ):
        _require(
            observed["condition_index"] == expected["condition_index"]
            and observed["condition_id"] == expected["id"]
            and observed["override"] == expected["override"],
            "condition order or override differs from preregistration",
        )

    expected_block_keys = {
        (
            condition["condition_index"],
            policy["checkpoint_id"],
            fit["fit_id"],
        )
        for condition in expected_condition_prefix
        for policy in preregistration["policies"]
        for fit in preregistration["fits"]
    }
    observed_block_keys = {
        (
            block["condition_index"],
            block["checkpoint_id"],
            block["fit_id"],
        )
        for block in blocks
    }
    _require(
        observed_block_keys == expected_block_keys,
        "terminal block population differs from preregistration",
    )
    _require(
        len(observed_block_keys) == len(blocks),
        "terminal result contains duplicate blocks",
    )

    nested_trace_count = 0
    for block in blocks:
        manifest_receipt = block["manifest"]
        label = (
            f"{block['condition_id']}:{block['checkpoint_id']}:"
            f"{block['fit_id']}"
        )
        verify_receipt(manifest_receipt, f"manifest:{label}")
        manifest_path = Path(manifest_receipt["path"])
        manifest = _load_json(manifest_path)
        verify_receipt(manifest["evaluation"], f"evaluation:{label}")
        verify_receipt(manifest["stdout"], f"stdout:{label}")
        for index, trace in enumerate(manifest["traces"]):
            verify_receipt(trace, f"trace:{label}:{index}")
            nested_trace_count += 1

        condition = next(
            item
            for item in expected_condition_prefix
            if item["condition_index"] == block["condition_index"]
        )
        policy = next(
            item
            for item in preregistration["policies"]
            if item["checkpoint_id"] == block["checkpoint_id"]
        )
        fit = next(
            item
            for item in preregistration["fits"]
            if item["fit_id"] == block["fit_id"]
        )
        expected_contract = block_contract(
            preregistration, condition, policy, fit
        )
        _require(
            manifest.get("block_contract") == expected_contract
            and manifest.get("block_contract_sha256")
            == canonical_sha256(expected_contract),
            f"block contract differs: {label}",
        )
        _require(
            extract_block(preregistration, condition, manifest)
            == block["result"],
            f"extracted block result differs: {label}",
        )

    _require(
        nested_trace_count == summary["completed_cells"],
        "nested trace population differs from completed-cell count",
    )
    for condition_result in conditions:
        condition = next(
            item
            for item in expected_condition_prefix
            if item["condition_index"] == condition_result["condition_index"]
        )
        condition_blocks = [
            block
            for block in blocks
            if block["condition_index"] == condition_result["condition_index"]
        ]
        _require(
            condition_summary(condition, condition_blocks) == condition_result,
            f"condition summary differs: {condition_result['condition_id']}",
        )

    green_cells = sum(item["green_cells"] for item in conditions)
    all_green = completed == 20 and all(
        item["condition_green"] for item in conditions
    )
    first_failed = next(
        (
            item["condition_id"]
            for item in conditions
            if not item["condition_green"]
        ),
        None,
    )
    _require(summary["green_cells"] == green_cells, "green-cell count differs")
    _require(
        summary["all_completed_cells_green"]
        is (green_cells == summary["completed_cells"]),
        "all-completed-cells flag differs",
    )
    _require(
        summary["matrix_complete"] is (completed == 20),
        "matrix-complete flag differs",
    )
    _require(
        summary["all_twenty_conditions_green"] is all_green,
        "all-twenty-conditions flag differs",
    )
    _require(
        summary["first_failed_condition"] == first_failed,
        "first-failed condition differs",
    )
    if all_green:
        _require(
            result["status"] == "PASS_T177_HEAD_PREFIX_MEAN_FULL_R2"
            and result["decision"]
            == preregistration["decision_rule"]["pass_decision"],
            "passing terminal decision differs",
        )
    else:
        _require(
            first_failed is not None
            and conditions[-1]["condition_id"] == first_failed,
            "terminal HOLD did not stop at the first failed condition",
        )
        _require(
            result["status"] == "HOLD_T177_HEAD_PREFIX_MEAN_FULL_R2"
            and result["decision"]
            == preregistration["decision_rule"]["fail_decision"],
            "holding terminal decision differs",
        )

    return {
        "status": "PASS_T177_TERMINAL_VERIFICATION",
        "terminal_status": result["status"],
        "decision": result["decision"],
        "result_sha256": result_sha256,
        "completed_conditions": completed,
        "completed_cells": summary["completed_cells"],
        "green_cells": green_cells,
        "blocks": len(blocks),
        "nested_traces": nested_trace_count,
        "first_failed_condition": first_failed,
        "hosted_compute_units": 0,
        "robot_or_rdk_access": 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preregistration", type=Path, default=PREREGISTRATION)
    parser.add_argument("--result", type=Path, default=RESULT)
    args = parser.parse_args()
    print(
        json.dumps(
            verify(args.preregistration.resolve(), args.result.resolve()),
            allow_nan=False,
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
