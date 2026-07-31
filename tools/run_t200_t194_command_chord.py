#!/usr/bin/env python3
"""Run T194's saved-state command-chord diagnostic."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import time
from typing import Any

import numpy as np

from run_t136_static_calibration_router_transform import (
    ANALYSIS,
    ROOT,
    canonical_sha256,
    verify,
)
from run_t174_t173_failure_autopsy import (
    OUTPUT_NAMES,
    feed,
    load_rows,
    make_session,
    recorded_outputs,
)


PREREG = ANALYSIS / "t200_t194_command_chord_preregistration.json"
RESULT = ANALYSIS / "t200_t194_command_chord_result.json"
MARKDOWN = ANALYSIS / "T200_T194_COMMAND_CHORD_RESULT_20260730.md"


def label(item: dict[str, Any]) -> str:
    checkpoint = (
        "half" if item["checkpoint_id"].endswith("HALF") else "final"
    )
    return f"{checkpoint}_{item['fit_id']}_x0p077"


def window_metrics(
    action: np.ndarray,
    hidden: np.ndarray,
    previous: np.ndarray,
    joint_order: list[str],
) -> dict[str, Any]:
    def metrics(value: np.ndarray) -> dict[str, float]:
        return {
            "rms": float(np.sqrt(np.mean(np.square(value)))),
            "maximum_abs": float(np.max(np.abs(value))),
            "mean_abs": float(np.mean(np.abs(value))),
        }

    return {
        "rows": int(action.shape[0]),
        "action": metrics(action),
        "hidden": metrics(hidden),
        "previous_action": metrics(previous),
        "action_joints": sorted(
            [
                {
                    "joint": joint,
                    "rms": float(
                        np.sqrt(np.mean(np.square(action[:, index])))
                    ),
                    "maximum_abs": float(
                        np.max(np.abs(action[:, index]))
                    ),
                    "mean_signed": float(np.mean(action[:, index])),
                }
                for index, joint in enumerate(joint_order)
            ],
            key=lambda row: row["rms"],
            reverse=True,
        ),
    }


def chord_profile(
    rows: list[dict[str, Any]],
    session: Any,
    context: np.ndarray,
    *,
    command_index: int,
    commands: list[float],
    aligned_ticks: list[int],
    terminal_window: int,
    prefix_window: int,
    joint_order: list[str],
) -> dict[str, Any]:
    low, center, high = commands
    action_curvature = []
    hidden_curvature = []
    previous_curvature = []
    ticks = []
    exact_center_rows = 0
    maximum_center_delta = 0.0
    finite = True
    for row in rows:
        outputs = {}
        for name, command in (
            ("low", low),
            ("center", center),
            ("high", high),
        ):
            values = feed(row, context)
            values["obs"] = values["obs"].copy()
            values["obs"][0, command_index] = np.float32(command)
            outputs[name] = session.run(OUTPUT_NAMES, values)
        expected = recorded_outputs(row)
        exact = all(
            np.array_equal(left, right)
            for left, right in zip(
                outputs["center"], expected, strict=True
            )
        )
        exact_center_rows += int(exact)
        maximum_center_delta = max(
            maximum_center_delta,
            max(
                float(
                    np.max(
                        np.abs(
                            left.astype(np.float64)
                            - right.astype(np.float64)
                        )
                    )
                )
                for left, right in zip(
                    outputs["center"], expected, strict=True
                )
            ),
        )
        curvature = [
            center_value.astype(np.float64)
            - 0.5
            * (
                low_value.astype(np.float64)
                + high_value.astype(np.float64)
            )
            for low_value, center_value, high_value in zip(
                outputs["low"],
                outputs["center"],
                outputs["high"],
                strict=True,
            )
        ]
        action_curvature.append(curvature[0].reshape(-1))
        hidden_curvature.append(curvature[1].reshape(-1))
        previous_curvature.append(curvature[2].reshape(-1))
        ticks.append(int(row["tick"]))
        finite &= all(
            np.all(np.isfinite(value))
            for group in outputs.values()
            for value in group
        )
    action = np.asarray(action_curvature, np.float64)
    hidden = np.asarray(hidden_curvature, np.float64)
    previous = np.asarray(previous_curvature, np.float64)
    ticks_array = np.asarray(ticks, np.int64)

    def select(mask: np.ndarray) -> dict[str, Any]:
        return window_metrics(
            action[mask],
            hidden[mask],
            previous[mask],
            joint_order,
        )

    lo_tick, hi_tick = aligned_ticks
    aligned = (ticks_array >= lo_tick) & (ticks_array <= hi_tick)
    return {
        "rows": len(rows),
        "center_recorded_bit_exact_rows": exact_center_rows,
        "all_center_recorded_outputs_bit_exact": (
            exact_center_rows == len(rows)
        ),
        "maximum_center_recorded_delta": maximum_center_delta,
        "all_outputs_finite": bool(finite),
        "full": select(np.ones(len(rows), dtype=bool)),
        "prefix": select(np.arange(len(rows)) < prefix_window),
        "terminal": select(
            np.arange(len(rows)) >= len(rows) - terminal_window
        ),
        "aligned": select(aligned),
        "aligned_ticks_inclusive": [lo_tick, hi_tick],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    parser.parse_args()
    for path in (RESULT, MARKDOWN):
        if path.exists():
            raise FileExistsError("refusing to overwrite T200 output")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T200 execution requires clean worktree")

    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    basis = {
        key: value
        for key, value in prereg.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        prereg["status"] != "PREREGISTERED_T200_T194_COMMAND_CHORD"
        or prereg["failed_checks"]
        or canonical_sha256(basis)
        != prereg["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T200 preregistration changed")
    for name, item in prereg["frozen_inputs"].items():
        verify(item, f"frozen_inputs.{name}")
    for name, item in prereg["graphs"].items():
        verify(item, f"graphs.{name}")
    for index, item in enumerate(prereg["traces"]):
        verify(item["trace"], f"traces[{index}]")

    started = time.time()
    sessions = {
        name: make_session(Path(item["path"]))
        for name, item in prereg["graphs"].items()
    }
    contexts = {
        fit: np.asarray(item["context"], np.float32).reshape(1, 64)
        for fit, item in prereg["contexts"].items()
    }
    profiles = {}
    for item in prereg["traces"]:
        name = label(item)
        graph_name = (
            "half" if item["checkpoint_id"].endswith("HALF") else "final"
        )
        profiles[name] = chord_profile(
            load_rows(item),
            sessions[graph_name],
            contexts[item["fit_id"]],
            command_index=int(
                prereg["analysis"]["command_observation_index"]
            ),
            commands=[
                float(value)
                for value in prereg["analysis"]["commands_x_m_s"]
            ],
            aligned_ticks=prereg["analysis"][
                "aligned_comparison_ticks_inclusive"
            ],
            terminal_window=int(
                prereg["analysis"]["terminal_window_ticks"]
            ),
            prefix_window=int(prereg["analysis"]["prefix_window_ticks"]),
            joint_order=[
                "left_hip_yaw",
                "left_hip_roll",
                "left_hip_pitch",
                "left_knee",
                "left_ankle",
                "neck_pitch",
                "head_pitch",
                "head_yaw",
                "head_roll",
                "right_hip_yaw",
                "right_hip_roll",
                "right_hip_pitch",
                "right_knee",
                "right_ankle",
            ],
        )
    failure_name = "half_p31_34_x0p077"
    comparators = [
        "final_p31_34_x0p077",
        "half_p30_x0p077",
    ]
    failure = profiles[failure_name]
    failure_rms = failure["aligned"]["action"]["rms"]
    failure_max = failure["aligned"]["action"]["maximum_abs"]
    comparator_rms = {
        name: profiles[name]["aligned"]["action"]["rms"]
        for name in comparators
    }
    comparator_max = {
        name: profiles[name]["aligned"]["action"]["maximum_abs"]
        for name in comparators
    }
    curvature_supported = (
        failure_rms > max(comparator_rms.values())
        and failure_max > max(comparator_max.values())
        and failure["terminal"]["action"]["rms"]
        > failure["prefix"]["action"]["rms"]
    )
    checks = {
        "three_profiles_exact": set(profiles)
        == {
            "half_p31_34_x0p077",
            "final_p31_34_x0p077",
            "half_p30_x0p077",
        },
        "all_center_outputs_bit_exact": all(
            row["all_center_recorded_outputs_bit_exact"]
            for row in profiles.values()
        ),
        "all_endpoint_and_center_outputs_finite": all(
            row["all_outputs_finite"] for row in profiles.values()
        ),
        "failure_has_308_rows": failure["rows"] == 308,
        "comparators_have_600_rows": all(
            profiles[name]["rows"] == 600 for name in comparators
        ),
        "all_aligned_windows_have_54_rows": all(
            row["aligned"]["rows"] == 54 for row in profiles.values()
        ),
        "command_is_exact_midpoint": (
            np.float64(0.077)
            == 0.5 * (np.float64(0.074) + np.float64(0.080))
        ),
        "cpu_only": all(
            session.get_providers()[0] == "CPUExecutionProvider"
            for session in sessions.values()
        ),
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    earned = not failed and curvature_supported
    decision = (
        prereg["decision_rule"]["interior_command_curvature_supported"]
        if earned
        else prereg["decision_rule"]["otherwise"]
    )
    value: dict[str, Any] = {
        "schema_version": "open_duck.t200_t194_command_chord_result.v1",
        "status": (
            "PASS_T200_T194_COMMAND_CHORD"
            if not failed
            else "HOLD_T200_T194_COMMAND_CHORD"
        ),
        "classification": (
            "INTERIOR_COMMAND_CHORD_CURVATURE_SELECTS_ONE_CELL_SCREEN"
            if curvature_supported
            else "INTERIOR_COMMAND_CHORD_CURVATURE_NOT_FAILURE_SPECIFIC"
        ),
        "decision": decision,
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "checks": checks,
        "failed_checks": failed,
        "curvature_rule_passed": curvature_supported,
        "failure_aligned_action": failure["aligned"]["action"],
        "failure_prefix_action": failure["prefix"]["action"],
        "failure_terminal_action": failure["terminal"]["action"],
        "comparator_aligned_action_rms": comparator_rms,
        "comparator_aligned_action_maximum_abs": comparator_max,
        "profiles": profiles,
        "execution": {
            "inference_rows": 3
            * sum(row["rows"] for row in profiles.values()),
            "behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
            "wall_seconds": time.time() - started,
        },
        "authority": {
            "one_cell_behavior_preregistration": earned,
            "behavior": False,
            "training": False,
            "full_r2": False,
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
    top = failure["aligned"]["action_joints"][:3]
    MARKDOWN.write_text(
        "# T200 T194 command-chord result\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Classification: `{value['classification']}`\n"
        f"- Decision: `{value['decision']}`\n"
        f"- Failure aligned action RMS/max: "
        f"`{failure_rms:.9f}/{failure_max:.9f}`\n"
        f"- Comparator aligned action RMS: `{comparator_rms}`\n"
        f"- Highest failure curvature joints: "
        f"`{[row['joint'] for row in top]}`\n"
        "- Behavior/training/hosted/robot: `0/0/0/0`\n"
        f"- Result SHA-256: `{value['result_sha256']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"classification={value['classification']}")
    print(f"decision={value['decision']}")
    print(f"result_sha256={value['result_sha256']}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
