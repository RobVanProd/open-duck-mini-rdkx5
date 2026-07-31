#!/usr/bin/env python3
"""Run the frozen paired T151/T157 positive-COM trace autopsy."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import statistics
import subprocess
from typing import Any

import numpy as np

from run_t136_static_calibration_router_transform import (
    ANALYSIS,
    ROOT,
    canonical_sha256,
    sha256,
    verify,
)


PREREG = (
    ANALYSIS
    / "t158_positive_expert_failure_autopsy_preregistration.json"
)
RESULT = ANALYSIS / "t158_positive_expert_failure_autopsy_result.json"
MARKDOWN = (
    ANALYSIS / "T158_POSITIVE_EXPERT_FAILURE_AUTOPSY_RESULT_20260729.md"
)


def trace_key(
    block: dict[str, Any],
    cell: dict[str, Any],
) -> tuple[int, str, float]:
    return (
        int(block["step"]),
        str(block["fit_id"]),
        float(cell["command_x_m_s"]),
    )


def blocks(
    result: dict[str, Any],
) -> dict[tuple[int, str, float], dict[str, Any]]:
    values = {}
    for block in result["blocks"]:
        if block["condition_id"] != "TORSO_COM_X_POS":
            continue
        for cell in block["result"]["cells"]:
            values[trace_key(block, cell)] = {
                "block": block,
                "cell": cell,
            }
    return values


def load_rows(cell: dict[str, Any]) -> list[dict[str, Any]]:
    protection = cell["protection"]
    path = Path(protection["path"])
    if (
        not path.is_file()
        or sha256(path) != protection["sha256"]
        or path.stat().st_size
        != next(
            item["bytes"]
            for item in PREREG_VALUE[
                "old_traces" if "t151_" in str(path) else "new_traces"
            ]
            if item["path"] == str(path)
        )
    ):
        raise RuntimeError(f"T158 trace changed: {path}")
    rows = [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
    ]
    if len(rows) != protection["rows"]:
        raise RuntimeError(f"T158 trace row count changed: {path}")
    return rows


def first_crossing(
    rows: list[dict[str, Any]],
    field: str,
    threshold: float,
    *,
    absolute: bool,
    below: bool = False,
) -> int | None:
    for row in rows:
        value = float(row[field])
        if absolute:
            value = abs(value)
        crossed = value < threshold if below else value >= threshold
        if crossed:
            return int(row["tick"])
    return None


def action_delta(
    old_rows: list[dict[str, Any]],
    new_rows: list[dict[str, Any]],
    joint_order: list[str],
) -> list[dict[str, Any]]:
    count = min(len(old_rows), len(new_rows))
    old = np.asarray(
        [row["action"] for row in old_rows[:count]],
        dtype=np.float64,
    )
    new = np.asarray(
        [row["action"] for row in new_rows[:count]],
        dtype=np.float64,
    )
    delta = new - old
    return [
        {
            "joint": joint,
            "mean_abs": float(np.mean(np.abs(delta[:, index]))),
            "rms": float(np.sqrt(np.mean(delta[:, index] ** 2))),
            "max_abs": float(np.max(np.abs(delta[:, index]))),
            "tick0": float(delta[0, index]),
        }
        for index, joint in enumerate(joint_order)
    ]


def paired_row(
    key: tuple[int, str, float],
    old_item: dict[str, Any],
    new_item: dict[str, Any],
    prereg: dict[str, Any],
) -> dict[str, Any]:
    old_rows = load_rows(old_item["cell"])
    new_rows = load_rows(new_item["cell"])
    thresholds = prereg["thresholds"]
    pitch_tick = first_crossing(
        new_rows,
        "body_pitch_rad",
        thresholds["forward_pitch_rad"],
        absolute=False,
    )
    roll_tick = first_crossing(
        new_rows,
        "body_roll_rad",
        thresholds["absolute_roll_rad"],
        absolute=True,
    )
    height_tick = first_crossing(
        new_rows,
        "base_height_m",
        thresholds["minimum_base_height_m"],
        absolute=False,
        below=True,
    )
    pre_pitch = (
        new_rows
        if pitch_tick is None
        else new_rows[: max(1, pitch_tick)]
    )
    command = key[2]
    pre_pitch_vx = float(
        np.mean([row["local_linvel_m_s"][0] for row in pre_pitch])
    )
    new_behavior = new_item["cell"]["behavior"]
    return {
        "step": key[0],
        "fit_id": key[1],
        "command_x_m_s": command,
        "old_ticks": len(old_rows),
        "new_ticks": len(new_rows),
        "survival_gain_ticks": len(new_rows) - len(old_rows),
        "new_pitch_crossing_tick": pitch_tick,
        "new_roll_crossing_tick": roll_tick,
        "new_height_crossing_tick": height_tick,
        "positive_pitch_leads": (
            pitch_tick is not None
            and roll_tick is not None
            and height_tick is not None
            and pitch_tick < roll_tick
            and pitch_tick < height_tick
        ),
        "pre_pitch_mean_vx_m_s": pre_pitch_vx,
        "pre_pitch_command_ratio": (
            pre_pitch_vx / command if command > 0.0 else None
        ),
        "new_zero_saturation": (
            new_behavior["action_saturation_pct"] == 0.0
        ),
        "new_zero_rate_excess": (
            new_behavior["instant_rate_excess_rad_s"] == 0.0
            and new_behavior["p95_rate_excess_rad_s"] == 0.0
        ),
        "new_tracking_green": (
            new_behavior["pitch_tracking_p95_rad"] <= 0.20
        ),
        "action_delta_common_prefix": action_delta(
            old_rows,
            new_rows,
            prereg["joint_order"],
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if not args.execute:
        raise PermissionError("T158 requires --execute")
    for path in (RESULT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T158: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("formal T158 execution requires clean worktree")

    global PREREG_VALUE
    PREREG_VALUE = json.loads(PREREG.read_text(encoding="utf-8"))
    prereg = PREREG_VALUE
    basis = {
        key: item
        for key, item in prereg.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        prereg["status"]
        != "PREREGISTERED_T158_POSITIVE_EXPERT_FAILURE_AUTOPSY"
        or prereg["failed_checks"]
        or canonical_sha256(basis)
        != prereg["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T158 preregistration changed")
    for name, item in prereg["frozen_inputs"].items():
        verify(item, name)

    old_result = json.loads(
        Path(prereg["frozen_inputs"]["t151_result"]["path"]).read_text(
            encoding="utf-8"
        )
    )
    new_result = json.loads(
        Path(prereg["frozen_inputs"]["t157_result"]["path"]).read_text(
            encoding="utf-8"
        )
    )
    old = blocks(old_result)
    new = blocks(new_result)
    if set(old) != set(new):
        raise RuntimeError("T158 paired matrix changed")
    x0_keys = sorted(key for key in new if key[2] == 0.0)
    moving_keys = sorted(key for key in new if key[2] > 0.0)
    pairs = [
        paired_row(key, old[key], new[key], prereg)
        for key in moving_keys
    ]
    old_ticks = [row["old_ticks"] for row in pairs]
    new_ticks = [row["new_ticks"] for row in pairs]
    half_ticks = [
        row["new_ticks"] for row in pairs if row["step"] == 1003520
    ]
    final_ticks = [
        row["new_ticks"] for row in pairs if row["step"] == 2007040
    ]
    joint_summary = []
    for joint in prereg["joint_order"]:
        values = [
            next(
                item
                for item in row["action_delta_common_prefix"]
                if item["joint"] == joint
            )
            for row in pairs
        ]
        joint_summary.append(
            {
                "joint": joint,
                "mean_abs_across_pairs": float(
                    np.mean([item["mean_abs"] for item in values])
                ),
                "maximum_abs_across_pairs": max(
                    item["max_abs"] for item in values
                ),
                "mean_tick0_delta": float(
                    np.mean([item["tick0"] for item in values])
                ),
            }
        )
    joint_summary.sort(
        key=lambda item: item["mean_abs_across_pairs"],
        reverse=True,
    )
    x0_green = sum(new[key]["cell"]["cell_green"] for key in x0_keys)
    moving_green = sum(
        new[key]["cell"]["cell_green"] for key in moving_keys
    )
    summary = {
        "x0_green_cells": x0_green,
        "moving_green_cells": moving_green,
        "old_moving_median_ticks": statistics.median(old_ticks),
        "new_moving_median_ticks": statistics.median(new_ticks),
        "median_survival_gain_ticks": (
            statistics.median(new_ticks) - statistics.median(old_ticks)
        ),
        "maximum_new_survival_ticks": max(new_ticks),
        "half_median_ticks": statistics.median(half_ticks),
        "final_median_ticks": statistics.median(final_ticks),
        "positive_pitch_leads_count": sum(
            row["positive_pitch_leads"] for row in pairs
        ),
        "moving_pairs": len(pairs),
        "all_new_moving_quality_invariants": all(
            row["new_zero_saturation"]
            and row["new_zero_rate_excess"]
            and row["new_tracking_green"]
            for row in pairs
        ),
    }
    checks = {
        "four_x0_pass_twelve_moving_fail": (
            x0_green == 4 and moving_green == 0
        ),
        "median_survival_improved": (
            summary["new_moving_median_ticks"]
            > summary["old_moving_median_ticks"]
        ),
        "one_near_full_horizon": (
            summary["maximum_new_survival_ticks"]
            >= prereg["thresholds"]["near_full_horizon_ticks"]
        ),
        "positive_pitch_leads_all_failures": (
            summary["positive_pitch_leads_count"] == len(pairs) == 12
        ),
        "all_new_moving_quality_invariants": summary[
            "all_new_moving_quality_invariants"
        ],
        "final_survival_regressed_from_half": (
            summary["final_median_ticks"] < summary["half_median_ticks"]
        ),
        "read_only_no_behavior_optimizer_colab_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    passed = not failed
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t158_positive_expert_failure_autopsy_result.v1"
        ),
        "status": (
            "PASS_T158_POSITIVE_EXPERT_FAILURE_AUTOPSY"
            if passed
            else "HOLD_T158_POSITIVE_EXPERT_FAILURE_AUTOPSY"
        ),
        "decision": (
            prereg["decision_rule"]["pass_decision"]
            if passed
            else prereg["decision_rule"]["fail_decision"]
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "summary": summary,
        "pairs": pairs,
        "joint_action_delta_ranking": joint_summary,
        "checks": checks,
        "failed_checks": failed,
        "execution": {
            "trace_rows_read": sum(old_ticks) + sum(new_ticks),
            "behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "mechanics_screen_preregistration": passed,
            "behavior_evaluation": False,
            "training": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    value["result_sha256"] = canonical_sha256(value)
    RESULT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T158 positive-expert failure autopsy\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Decision: `{value['decision']}`\n"
        f"- Median survival: old `{summary['old_moving_median_ticks']}` "
        f"ticks, new `{summary['new_moving_median_ticks']}` ticks\n"
        f"- Leading positive-pitch failures: "
        f"`{summary['positive_pitch_leads_count']}/12`\n"
        f"- Half/final median: `{summary['half_median_ticks']}` / "
        f"`{summary['final_median_ticks']}` ticks\n"
        "- New behavior / optimizer / Colab / robot: `0/0/0/0`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"decision={value['decision']}")
    print(f"failed_checks={failed}")
    print(f"result_sha256={value['result_sha256']}")
    return 0 if passed else 1


if __name__ == "__main__":
    PREREG_VALUE: dict[str, Any] = {}
    raise SystemExit(main())
