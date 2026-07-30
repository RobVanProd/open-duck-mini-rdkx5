#!/usr/bin/env python3
"""Analyze support-mode anatomy of the current eight saved policy falls."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
import time
from typing import Any, Mapping, Sequence

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = (
    ANALYSIS / "t184_bilateral_single_support_anatomy_preregistration.json"
)
RESULT = ANALYSIS / "t184_bilateral_single_support_anatomy_result.json"
MARKDOWN = (
    ANALYSIS / "T184_BILATERAL_SINGLE_SUPPORT_ANATOMY_RESULT_20260730.md"
)

sys.path.insert(0, str(ROOT / "tools"))
from run_t27_t23_robustness_matrix import (  # noqa: E402
    canonical_sha256,
    verify_receipt,
)


class T184Error(RuntimeError):
    """The frozen T184 contract was violated."""


def _require(condition: object, message: str) -> None:
    if not condition:
        raise T184Error(message)


def _load(path: Path) -> dict[str, Any]:
    _require(path.is_file(), f"missing input: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    _require(isinstance(value, dict), f"JSON root is not an object: {path}")
    return value


def _canonical_without(value: Mapping[str, Any], field: str) -> str:
    basis = dict(value)
    basis.pop(field, None)
    return canonical_sha256(basis)


def contact_mode(value: Sequence[int | bool]) -> str:
    pair = tuple(int(bool(item)) for item in value)
    mapping = {
        (0, 0): "none",
        (1, 0): "left_only",
        (0, 1): "right_only",
        (1, 1): "both",
    }
    if pair not in mapping:
        raise T184Error(f"invalid contact vector: {value}")
    return mapping[pair]


def read_trace(item: Mapping[str, Any]) -> list[dict[str, Any]]:
    verify_receipt(item, f"trace:{item['path']}")
    rows = []
    with Path(item["path"]).open("r", encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, start=1):
            row = json.loads(line)
            _require(
                int(row.get("tick", -1)) == line_number - 1,
                f"noncontiguous trace: {item['path']}:{line_number}",
            )
            contacts = row.get("foot_contacts")
            _require(
                isinstance(contacts, list) and len(contacts) == 2,
                f"contact vector missing: {item['path']}:{line_number}",
            )
            contact_mode(contacts)
            rows.append(row)
    _require(bool(rows), f"empty trace: {item['path']}")
    return rows


def contiguous_run_ending_at(modes: Sequence[str], index: int) -> int:
    target = modes[index]
    count = 0
    for cursor in range(index, -1, -1):
        if modes[cursor] != target:
            break
        count += 1
    return count


def summarize_trace(
    row: Mapping[str, Any],
    *,
    terminal_window_ticks: int,
    maximum_ticks_from_support_to_done: int,
) -> dict[str, Any]:
    records = read_trace(row["trace"])
    modes = [contact_mode(record["foot_contacts"]) for record in records]
    expected_green = bool(row["expected_green"])
    done = [bool(record.get("done")) for record in records]
    supported = [
        index for index, mode in enumerate(modes) if mode != "none"
    ]
    _require(bool(supported), f"trace has no support: {row['trace_id']}")
    last_supported_tick = supported[-1]
    last_supported_mode = modes[last_supported_tick]
    done_tick = next(
        (index for index, value in enumerate(done) if value), None
    )
    final_modes = modes[-terminal_window_ticks:]
    mode_counts = {
        mode: modes.count(mode)
        for mode in ("none", "left_only", "right_only", "both")
    }
    final_mode_counts = {
        mode: final_modes.count(mode)
        for mode in ("none", "left_only", "right_only", "both")
    }
    ticks_to_done = (
        None if done_tick is None else done_tick - last_supported_tick
    )
    terminal_link = (
        not expected_green
        and last_supported_mode in ("left_only", "right_only")
        and ticks_to_done is not None
        and 0 <= ticks_to_done <= maximum_ticks_from_support_to_done
    )
    pitches = np.asarray(
        [float(record["body_pitch_rad"]) for record in records],
        dtype=np.float64,
    )
    rolls = np.asarray(
        [float(record["body_roll_rad"]) for record in records],
        dtype=np.float64,
    )
    heights = np.asarray(
        [float(record["base_height_m"]) for record in records],
        dtype=np.float64,
    )
    return {
        "trace_id": row["trace_id"],
        "case_id": row["case_id"],
        "family": row["family"],
        "policy_role": row["policy_role"],
        "checkpoint_pair": row["checkpoint_pair"],
        "fit_id": row["fit_id"],
        "command_x_m_s": row["command_x_m_s"],
        "expected_green": expected_green,
        "rows": len(records),
        "done_tick": done_tick,
        "last_row_done": done[-1],
        "last_supported_tick": last_supported_tick,
        "last_supported_mode": last_supported_mode,
        "last_support_run_ticks": contiguous_run_ending_at(
            modes, last_supported_tick
        ),
        "ticks_from_last_supported_to_done": ticks_to_done,
        "terminal_single_support_link": terminal_link,
        "mode_counts": mode_counts,
        "terminal_window_mode_counts": final_mode_counts,
        "terminal_window_single_support_fraction": float(
            (
                final_mode_counts["left_only"]
                + final_mode_counts["right_only"]
            )
            / len(final_modes)
        ),
        "both_single_support_sides_observed": (
            mode_counts["left_only"] > 0
            and mode_counts["right_only"] > 0
        ),
        "last_supported_pitch_rad": float(pitches[last_supported_tick]),
        "last_supported_roll_rad": float(rolls[last_supported_tick]),
        "last_supported_base_height_m": float(
            heights[last_supported_tick]
        ),
        "maximum_abs_pitch_rad": float(np.max(np.abs(pitches))),
        "maximum_abs_roll_rad": float(np.max(np.abs(rolls))),
        "minimum_base_height_m": float(np.min(heights)),
    }


def run() -> dict[str, Any]:
    _require(not RESULT.exists(), f"refusing to overwrite: {RESULT}")
    _require(not MARKDOWN.exists(), f"refusing to overwrite: {MARKDOWN}")
    _require(
        not subprocess.check_output(
            ["git", "status", "--porcelain"], cwd=ROOT, text=True
        ).strip(),
        "T184 execution requires committed clean preregistration",
    )
    prereg = _load(PREREG)
    _require(
        prereg.get("status")
        == "PREREGISTERED_T184_BILATERAL_SINGLE_SUPPORT_ANATOMY",
        "unexpected T184 status",
    )
    _require(
        _canonical_without(prereg, "preregistered_contract_sha256")
        == prereg.get("preregistered_contract_sha256"),
        "T184 preregistration hash differs",
    )
    for name, item in prereg["frozen_inputs"].items():
        verify_receipt(item, name)
    contract = prereg["analysis_contract"]
    started = time.time()
    traces = [
        summarize_trace(
            row,
            terminal_window_ticks=int(
                contract["terminal_window_ticks"]
            ),
            maximum_ticks_from_support_to_done=int(
                contract["maximum_ticks_from_last_supported_to_done"]
            ),
        )
        for row in prereg["traces"]
    ]
    passing = [row for row in traces if row["expected_green"]]
    failing = [row for row in traces if not row["expected_green"]]
    last_failure_support_sides = sorted(
        {
            row["last_supported_mode"]
            for row in failing
            if row["last_supported_mode"]
            in ("left_only", "right_only")
        }
    )
    checks = {
        "trace_population_exact": (
            len(traces) == 13
            and len(passing) == 5
            and len(failing) == 8
        ),
        "all_passing_traces_full_duration_without_done": all(
            row["rows"] == 600
            and row["done_tick"] is None
            and not row["last_row_done"]
            for row in passing
        ),
        "all_failing_traces_short_and_end_done": all(
            row["rows"] < 600
            and row["done_tick"] == row["rows"] - 1
            and row["last_row_done"]
            for row in failing
        ),
        "all_failures_link_to_recent_single_support": all(
            row["terminal_single_support_link"] for row in failing
        ),
        "failure_last_support_is_bilateral_across_population": (
            last_failure_support_sides == ["left_only", "right_only"]
        ),
        "every_trace_observes_both_single_support_sides": all(
            row["both_single_support_sides_observed"] for row in traces
        ),
        "saved_trace_only_no_behavior_optimizer_hosted_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed_checks = sorted(
        name for name, passed in checks.items() if not passed
    )
    passed = not failed_checks
    basis: dict[str, Any] = {
        "schema_version": (
            "open_duck.t184_bilateral_single_support_anatomy_result.v1"
        ),
        "status": (
            "PASS_T184_BILATERAL_SINGLE_SUPPORT_ANATOMY"
            if passed
            else "HOLD_T184_BILATERAL_SINGLE_SUPPORT_ANATOMY"
        ),
        "decision": (
            prereg["decision_rule"]["pass"]
            if passed
            else prereg["decision_rule"]["fail"]
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "checks": checks,
        "failed_checks": failed_checks,
        "summary": {
            "traces": len(traces),
            "passing_traces": len(passing),
            "failing_traces": len(failing),
            "failure_last_support_sides": last_failure_support_sides,
            "failures_linked_to_recent_single_support": sum(
                row["terminal_single_support_link"] for row in failing
            ),
            "failure_terminal_single_support_fraction_min": min(
                row["terminal_window_single_support_fraction"]
                for row in failing
            ),
            "failure_terminal_single_support_fraction_mean": float(
                np.mean(
                    [
                        row["terminal_window_single_support_fraction"]
                        for row in failing
                    ],
                    dtype=np.float64,
                )
            ),
            "maximum_ticks_from_last_support_to_done": max(
                int(row["ticks_from_last_supported_to_done"])
                for row in failing
            ),
        },
        "traces": traces,
        "execution": {
            "saved_trace_rows": sum(row["rows"] for row in traces),
            "new_behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
            "wall_seconds": time.time() - started,
        },
        "authority": prereg["authority_after_result"],
    }
    basis["result_sha256"] = canonical_sha256(basis)
    RESULT.write_text(
        json.dumps(basis, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T184 bilateral single-support anatomy result\n\n"
        f"- Status: `{basis['status']}`\n"
        f"- Decision: `{basis['decision']}`\n"
        f"- Recent single-support links: "
        f"`{basis['summary']['failures_linked_to_recent_single_support']}/8`\n"
        f"- Last-support sides: "
        f"`{basis['summary']['failure_last_support_sides']}`\n"
        f"- Failed checks: `{failed_checks}`\n"
        "- New behavior / optimizer / hosted compute / robot: `0/0/0/0`\n",
        encoding="utf-8",
        newline="\n",
    )
    return basis


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    parser.parse_args()
    result = run()
    print(result["status"])
    print(f"decision={result['decision']}")
    print(f"result_sha256={result['result_sha256']}")
    return 0 if result["status"].startswith("PASS_") else 1


if __name__ == "__main__":
    raise SystemExit(main())
