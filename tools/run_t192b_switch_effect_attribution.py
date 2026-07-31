#!/usr/bin/env python3
"""Compare T192's switch interval with the sealed original failure."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
from typing import Any

import numpy as np

from run_t136_static_calibration_router_transform import (
    ANALYSIS,
    ROOT,
    canonical_sha256,
    verify,
)


PREREG = ANALYSIS / "t192b_switch_effect_attribution_preregistration.json"
RESULT = ANALYSIS / "t192b_switch_effect_attribution_result.json"
MARKDOWN = ANALYSIS / "T192B_SWITCH_EFFECT_ATTRIBUTION_RESULT_20260730.md"


def read_rows(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
    ]


def numeric_delta(left: Any, right: Any) -> float:
    try:
        a = np.asarray(left, dtype=np.float64)
        b = np.asarray(right, dtype=np.float64)
    except (TypeError, ValueError):
        return 0.0 if left == right else float("inf")
    if a.shape != b.shape:
        return float("inf")
    if a.size == 0:
        return 0.0
    return float(np.max(np.abs(a - b)))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    parser.parse_args()
    for path in (RESULT, MARKDOWN):
        if path.exists():
            raise FileExistsError("refusing to overwrite T192B output")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T192B execution requires clean worktree")

    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    basis = {
        key: value
        for key, value in prereg.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        prereg["status"]
        != "PREREGISTERED_T192B_SWITCH_EFFECT_ATTRIBUTION"
        or prereg["failed_checks"]
        or canonical_sha256(basis)
        != prereg["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T192B preregistration changed")
    for name, item in prereg["frozen_inputs"].items():
        verify(item, f"frozen_inputs.{name}")

    original = read_rows(Path(prereg["original_trace"]["path"]))
    hybrid = read_rows(Path(prereg["hybrid_trace"]["path"]))
    start, stop = prereg["comparison"]["row_range_inclusive"]
    indices = list(range(start, stop + 1))
    excluded = set(prereg["comparison"]["switch_metadata_fields_excluded"])
    common_differences: dict[str, dict[str, Any]] = {}
    for key in sorted(original[0]):
        if key in excluded:
            continue
        changed = []
        maximum = 0.0
        for index in indices:
            delta = numeric_delta(original[index][key], hybrid[index][key])
            if delta != 0.0:
                changed.append(index)
            maximum = max(maximum, delta)
        common_differences[key] = {
            "changed_rows": len(changed),
            "first_changed_tick": changed[0] if changed else None,
            "maximum_abs_delta": maximum,
        }
    action_fields = prereg["comparison"]["primary_action_fields"]
    zero_action_effect = all(
        common_differences[field]["changed_rows"] == 0
        for field in action_fields
    )
    zero_common_effect = all(
        row["changed_rows"] == 0 for row in common_differences.values()
    )
    switch_flags_exact = all(
        hybrid[index]["policy_switch_active"] is True
        and hybrid[index]["policy_session_role"] == "switch"
        for index in indices
    )
    checks = {
        "both_traces_have_547_rows": len(original) == len(hybrid) == 547,
        "all_27_switch_rows_present": len(indices) == 27,
        "switch_flags_exact": switch_flags_exact,
        "zero_action_target_or_state_effect": zero_action_effect,
        "zero_effect_across_all_original_fields": zero_common_effect,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    zero_effect = not failed
    decision = (
        prereg["decision_rule"]["zero_effect"]
        if zero_effect
        else prereg["decision_rule"]["nonzero_effect"]
    )
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t192b_switch_effect_attribution_result.v1"
        ),
        "status": (
            "PASS_T192B_SWITCH_EFFECT_ATTRIBUTION"
            if zero_effect
            else "HOLD_T192B_SWITCH_EFFECT_ATTRIBUTION"
        ),
        "classification": (
            "FINAL_HEAD_OUTPUT_EQUIVALENT_ON_COMMITTED_FAILURE_STATE"
            if zero_effect
            else "LATE_SWITCH_CHANGED_TRAJECTORY_BUT_DID_NOT_RECOVER"
        ),
        "decision": decision,
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "checks": checks,
        "failed_checks": failed,
        "comparison": {
            "rows": len(indices),
            "range_inclusive": [start, stop],
            "common_fields": len(common_differences),
            "differences": common_differences,
        },
        "execution": {
            "trace_rows_read": len(original) + len(hybrid),
            "inference_rows": 0,
            "behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "dynamic_support_cpu_preregistration": zero_effect,
            "behavior": False,
            "training": False,
            "gate5": False,
            "robot_or_rdk": False,
        },
    }
    value["result_sha256"] = canonical_sha256(value)
    RESULT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T192B switch-effect attribution result\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Classification: `{value['classification']}`\n"
        f"- Decision: `{value['decision']}`\n"
        f"- Compared switch rows / common fields: "
        f"`{len(indices)}/{len(common_differences)}`\n"
        f"- Zero action effect / zero common-field effect: "
        f"`{zero_action_effect}/{zero_common_effect}`\n"
        "- Inference/behavior/training/hosted/robot: `0/0/0/0/0`\n"
        f"- Result SHA-256: `{value['result_sha256']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"classification={value['classification']}")
    print(f"decision={value['decision']}")
    print(f"result_sha256={value['result_sha256']}")
    return 0 if zero_effect else 1


if __name__ == "__main__":
    raise SystemExit(main())
