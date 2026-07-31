#!/usr/bin/env python3
"""Attribute T17's physical-rate failures from its frozen traces."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
SOURCE = ANALYSIS / "t17_support_homeomorphism_result.json"
OUTPUT = ANALYSIS / "t17_rate_anatomy.json"
MARKDOWN = ANALYSIS / "T17_RATE_ANATOMY_20260726.md"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def main() -> int:
    if OUTPUT.exists() or MARKDOWN.exists():
        raise FileExistsError("refusing to overwrite T17 rate anatomy")
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    if source["decision"] != "CLOSE_BOUNDED_SUPPORT_HOMEOMORPHISM":
        raise RuntimeError("T17 source decision changed")
    moving = [
        cell
        for block in source["blocks"]
        for cell in block["cells"]
        if cell["command_x_m_s"] > 0.0
    ]
    joint_counts: Counter[int] = Counter()
    tick_counts = []
    event_counts = []
    trace_rows = []
    for cell in moving:
        trace = cell["trace"]
        path = Path(trace["path"])
        if (
            not path.is_file()
            or path.stat().st_size != trace["bytes"]
            or sha256(path) != trace["sha256"]
        ):
            raise RuntimeError(f"T17 trace receipt changed: {path}")
        ticks = set()
        events = 0
        maximum = 0.0
        for line in path.read_text(encoding="utf-8").splitlines():
            row = json.loads(line)
            excess = np.asarray(
                row["conservative_rate_excess_rad_s"], dtype=float
            )
            indices = np.flatnonzero(excess > 1.0e-12)
            for index in indices:
                joint_counts[int(index)] += 1
                ticks.add(int(row["tick"]))
                events += 1
                maximum = max(maximum, float(excess[index]))
        tick_counts.append(len(ticks))
        event_counts.append(events)
        trace_rows.append(
            {
                "checkpoint_id": cell["checkpoint_id"],
                "fit_id": cell["fit_id"],
                "condition_id": cell["condition_id"],
                "command_x_m_s": cell["command_x_m_s"],
                "samples": cell["behavior"]["samples"],
                "violating_ticks": len(ticks),
                "violation_events": events,
                "maximum_excess_rad_s": maximum,
                "trace_sha256": trace["sha256"],
            }
        )
    checks = {
        "all_24_moving_traces_present": len(moving) == 24,
        "every_moving_trace_has_rate_violations": all(
            value > 0 for value in tick_counts
        ),
        "every_moving_trace_has_persistent_rate_violations": all(
            value >= 200 for value in tick_counts
        ),
        "rate_failure_is_not_a_startup_seam": all(
            value >= 100 for value in tick_counts
        ),
        "optimizer_hosted_robot_zero": (
            source["execution"]
            == {
                "hosted_or_colab_compute": 0,
                "optimizer_steps": 0,
                "robot_or_rdk_access": 0,
                "simulator_behavior_cells": 32,
            }
        ),
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    basis = {
        "schema_version": "open_duck.t17_rate_anatomy.v1",
        "status": (
            "PASS_T17_PERSISTENT_RATE_FAILURE_ATTRIBUTION"
            if not failed
            else "HOLD_T17_RATE_FAILURE_ATTRIBUTION"
        ),
        "decision": (
            "REQUIRE_RATE_COHERENT_TRANSITION_BEFORE_TRAIN_THROUGH"
            if not failed
            else "NO_RATE_MECHANISM_SELECTED"
        ),
        "source": {
            "path": str(SOURCE.resolve()),
            "sha256": sha256(SOURCE),
            "result_sha256": source["result_sha256"],
        },
        "checks": checks,
        "failed_checks": failed,
        "summary": {
            "moving_traces": len(moving),
            "minimum_violating_ticks_per_trace": min(tick_counts),
            "maximum_violating_ticks_per_trace": max(tick_counts),
            "total_violation_events": sum(event_counts),
            "joint_violation_events": {
                str(index): count
                for index, count in sorted(joint_counts.items())
            },
        },
        "traces": trace_rows,
        "authority": {
            "new_behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_or_colab_compute": 0,
            "robot_or_rdk_access": 0,
        },
    }
    value = {**basis, "result_sha256": canonical_sha256(basis)}
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T17 rate-failure anatomy\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Decision: `{value['decision']}`\n"
        f"- Moving traces: `{len(moving)}/24`\n"
        "- Violating ticks per trace: "
        f"`{min(tick_counts)}-{max(tick_counts)}` of 600\n"
        f"- Total joint/tick violation events: `{sum(event_counts)}`\n"
        "- New behavior cells / optimizer / hosted / robot: `0/0/0/0`\n"
        f"- Result SHA-256: `{value['result_sha256']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"decision={value['decision']}")
    print(
        "violating_ticks_per_trace="
        f"{min(tick_counts)}-{max(tick_counts)}"
    )
    print(f"result_sha256={value['result_sha256']}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
