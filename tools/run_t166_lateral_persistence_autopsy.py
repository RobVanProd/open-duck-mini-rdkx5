#!/usr/bin/env python3
"""Run the frozen T166 negative-lateral-COM persistence autopsy."""

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
    sha256,
    verify,
)


PREREG = ANALYSIS / "t166_lateral_persistence_autopsy_preregistration.json"
RESULT = ANALYSIS / "t166_lateral_persistence_autopsy_result.json"
MARKDOWN = (
    ANALYSIS / "T166_LATERAL_PERSISTENCE_AUTOPSY_RESULT_20260729.md"
)


def key(item: dict[str, Any]) -> tuple[str, str, str, float]:
    return (
        str(item["condition_id"]),
        str(item["checkpoint_id"]),
        str(item["fit_id"]),
        float(item["command_x_m_s"]),
    )


def load_rows(item: dict[str, Any]) -> list[dict[str, Any]]:
    path = Path(item["path"])
    if (
        not path.is_file()
        or path.stat().st_size != item["bytes"]
        or sha256(path) != item["sha256"]
    ):
        raise RuntimeError(f"T166 protected trace changed: {path}")
    rows = [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
    ]
    if len(rows) != item["rows"]:
        raise RuntimeError(f"T166 trace row count changed: {path}")
    if [int(row["tick"]) for row in rows] != list(range(len(rows))):
        raise RuntimeError(f"T166 trace ticks are not contiguous: {path}")
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
        if value < threshold if below else value >= threshold:
            return int(row["tick"])
    return None


def failure_metrics(
    item: dict[str, Any],
    rows: list[dict[str, Any]],
    thresholds: dict[str, Any],
) -> dict[str, Any]:
    roll_tick = first_crossing(
        rows,
        "body_roll_rad",
        thresholds["absolute_roll_rad"],
        absolute=True,
    )
    pitch_tick = first_crossing(
        rows,
        "body_pitch_rad",
        thresholds["absolute_pitch_rad"],
        absolute=True,
    )
    height_tick = first_crossing(
        rows,
        "base_height_m",
        thresholds["minimum_base_height_m"],
        absolute=False,
        below=True,
    )
    crossing_order = sorted(
        (
            (name, tick)
            for name, tick in (
                ("roll", roll_tick),
                ("pitch", pitch_tick),
                ("height", height_tick),
            )
            if tick is not None
        ),
        key=lambda pair: pair[1],
    )
    return {
        "condition_id": item["condition_id"],
        "checkpoint_id": item["checkpoint_id"],
        "step": item["step"],
        "fit_id": item["fit_id"],
        "command_x_m_s": item["command_x_m_s"],
        "cell_green": item["cell_green"],
        "rows": len(rows),
        "context_sha256": item["context_sha256"],
        "first_absolute_roll_crossing_tick": roll_tick,
        "roll_at_first_roll_crossing_rad": (
            float(rows[roll_tick]["body_roll_rad"])
            if roll_tick is not None
            else None
        ),
        "first_absolute_pitch_crossing_tick": pitch_tick,
        "first_low_height_crossing_tick": height_tick,
        "first_failure_axis": crossing_order[0][0] if crossing_order else None,
        "roll_leads": bool(crossing_order and crossing_order[0][0] == "roll"),
        "maximum_absolute_roll_rad": float(
            max(abs(float(row["body_roll_rad"])) for row in rows)
        ),
        "maximum_absolute_pitch_rad": float(
            max(abs(float(row["body_pitch_rad"])) for row in rows)
        ),
        "minimum_height_m": float(
            min(float(row["base_height_m"]) for row in rows)
        ),
        "terminal_roll_rad": float(rows[-1]["body_roll_rad"]),
        "terminal_pitch_rad": float(rows[-1]["body_pitch_rad"]),
        "terminal_height_m": float(rows[-1]["base_height_m"]),
        "trace_sha256": item["sha256"],
    }


def vector_delta(
    left: list[dict[str, Any]],
    right: list[dict[str, Any]],
    field: str,
    joint_order: list[str],
    early_ticks: int,
) -> list[dict[str, Any]]:
    count = min(len(left), len(right))
    a = np.asarray([row[field] for row in left[:count]], dtype=np.float64)
    b = np.asarray([row[field] for row in right[:count]], dtype=np.float64)
    if a.shape != b.shape or a.ndim != 2 or a.shape[1] != len(joint_order):
        raise RuntimeError(f"T166 invalid paired vector field {field}: {a.shape}")
    delta = b - a
    early = delta[: min(early_ticks, count)]
    return [
        {
            "joint": joint,
            "tick0_delta": float(delta[0, index]),
            "early_rms": float(
                np.sqrt(np.mean(early[:, index] * early[:, index]))
            ),
            "early_mean_signed": float(np.mean(early[:, index])),
            "common_prefix_rms": float(
                np.sqrt(np.mean(delta[:, index] * delta[:, index]))
            ),
            "common_prefix_max_abs": float(
                np.max(np.abs(delta[:, index]))
            ),
        }
        for index, joint in enumerate(joint_order)
    ]


def paired_metrics(
    left_item: dict[str, Any],
    right_item: dict[str, Any],
    rows: dict[tuple[str, str, str, float], list[dict[str, Any]]],
    prereg: dict[str, Any],
    comparison: str,
) -> dict[str, Any]:
    left_rows = rows[key(left_item)]
    right_rows = rows[key(right_item)]
    fields = (
        "action",
        "policy_base_action",
        "policy_phase_action_correction",
        "applied_target_rad",
        "actual_position_rad",
        "actuator_force_nm",
    )
    return {
        "comparison": comparison,
        "left": {
            name: left_item[name]
            for name in (
                "condition_id",
                "checkpoint_id",
                "step",
                "fit_id",
                "command_x_m_s",
                "cell_green",
            )
        },
        "right": {
            name: right_item[name]
            for name in (
                "condition_id",
                "checkpoint_id",
                "step",
                "fit_id",
                "command_x_m_s",
                "cell_green",
            )
        },
        "common_prefix_ticks": min(len(left_rows), len(right_rows)),
        "context_sha256_equal": (
            left_item["context_sha256"] == right_item["context_sha256"]
        ),
        "vectors": {
            field: vector_delta(
                left_rows,
                right_rows,
                field,
                prereg["joint_order"],
                prereg["thresholds"]["early_action_window_ticks"],
            )
            for field in fields
        },
    }


def joint_ranking(
    pairs: list[dict[str, Any]],
    field: str,
    joint_order: list[str],
    lateral_joint_names: list[str],
) -> tuple[list[dict[str, Any]], float]:
    ranking = []
    squares = []
    lateral_squares = []
    for joint in joint_order:
        values = [
            next(
                row
                for row in pair["vectors"][field]
                if row["joint"] == joint
            )
            for pair in pairs
        ]
        early_rms = float(
            np.sqrt(np.mean([row["early_rms"] ** 2 for row in values]))
        )
        common_rms = float(
            np.sqrt(
                np.mean([row["common_prefix_rms"] ** 2 for row in values])
            )
        )
        item = {
            "joint": joint,
            "early_rms_across_pairs": early_rms,
            "common_prefix_rms_across_pairs": common_rms,
            "maximum_abs_across_pairs": float(
                max(row["common_prefix_max_abs"] for row in values)
            ),
            "mean_tick0_delta": float(
                np.mean([row["tick0_delta"] for row in values])
            ),
        }
        ranking.append(item)
        squares.append(early_rms * early_rms)
        if joint in lateral_joint_names:
            lateral_squares.append(early_rms * early_rms)
    ranking.sort(
        key=lambda item: item["early_rms_across_pairs"],
        reverse=True,
    )
    total = sum(squares)
    share = float(sum(lateral_squares) / total) if total > 0.0 else 0.0
    return ranking, share


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if not args.execute:
        raise PermissionError("T166 requires --execute")
    for path in (RESULT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T166: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("formal T166 execution requires clean worktree")

    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    basis = {
        name: value
        for name, value in prereg.items()
        if name != "preregistered_contract_sha256"
    }
    if (
        prereg["status"]
        != "PREREGISTERED_T166_LATERAL_PERSISTENCE_AUTOPSY"
        or prereg["failed_checks"]
        or canonical_sha256(basis)
        != prereg["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T166 preregistration changed")
    for name, item in prereg["frozen_inputs"].items():
        verify(item, name)

    items = {key(item): item for item in prereg["traces"]}
    rows = {item_key: load_rows(item) for item_key, item in items.items()}
    cell_metrics = [
        failure_metrics(item, rows[item_key], prereg["thresholds"])
        for item_key, item in sorted(items.items())
    ]
    half_final_pairs = []
    for fit_id in prereg["populations"]["fits"]:
        for command in prereg["populations"]["commands_x_m_s"]:
            left = items[
                ("TORSO_COM_Y_NEG", "T164_COMPOSED_HALF", fit_id, command)
            ]
            right = items[
                ("TORSO_COM_Y_NEG", "T164_COMPOSED_FINAL", fit_id, command)
            ]
            half_final_pairs.append(
                paired_metrics(
                    left,
                    right,
                    rows,
                    prereg,
                    "half_to_final_negative_lateral",
                )
            )
    condition_control_pairs = []
    for checkpoint in prereg["populations"]["checkpoints"]:
        for fit_id in prereg["populations"]["fits"]:
            for command in prereg["populations"]["commands_x_m_s"]:
                left = items[("ARMATURE_LO", checkpoint, fit_id, command)]
                right = items[
                    ("TORSO_COM_Y_NEG", checkpoint, fit_id, command)
                ]
                condition_control_pairs.append(
                    paired_metrics(
                        left,
                        right,
                        rows,
                        prereg,
                        "control_to_negative_lateral",
                    )
                )

    y_cells = [
        row for row in cell_metrics if row["condition_id"] == "TORSO_COM_Y_NEG"
    ]
    half_cells = [
        row for row in y_cells if row["checkpoint_id"] == "T164_COMPOSED_HALF"
    ]
    final_cells = [
        row for row in y_cells if row["checkpoint_id"] == "T164_COMPOSED_FINAL"
    ]
    half_failures = [row for row in half_cells if not row["cell_green"]]
    action_ranking, lateral_share = joint_ranking(
        half_final_pairs,
        "action",
        prereg["joint_order"],
        prereg["lateral_joint_names"],
    )
    base_ranking, _ = joint_ranking(
        half_final_pairs,
        "policy_base_action",
        prereg["joint_order"],
        prereg["lateral_joint_names"],
    )
    correction_ranking, correction_lateral_share = joint_ranking(
        half_final_pairs,
        "policy_phase_action_correction",
        prereg["joint_order"],
        prereg["lateral_joint_names"],
    )
    contexts_equal = all(
        pair["context_sha256_equal"] for pair in half_final_pairs
    )
    final_green = sum(row["cell_green"] for row in final_cells)
    half_green = sum(row["cell_green"] for row in half_cells)
    roll_leading = sum(row["roll_leads"] for row in half_failures)
    final_quality_green = all(
        item["cell_green"]
        for item in prereg["traces"]
        if item["condition_id"] == "TORSO_COM_Y_NEG"
        and item["checkpoint_id"] == "T164_COMPOSED_FINAL"
    )
    checks = {
        "final_eight_of_eight_half_below_eight": (
            final_green
            == prereg["thresholds"]["minimum_final_green_cells"]
            and half_green < final_green
        ),
        "five_half_failures_protected": (
            len(half_failures) == 5
            and all(row["trace_sha256"] for row in half_failures)
        ),
        "roll_leads_at_least_four_failures": (
            roll_leading
            >= prereg["thresholds"][
                "minimum_roll_leading_failures_for_lateral_class"
            ]
        ),
        "paired_contexts_identical_between_checkpoints": contexts_equal,
        "all_final_cells_quality_green": final_quality_green,
        "read_only_no_behavior_optimizer_colab_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    passed = not failed
    summary = {
        "negative_lateral_half_green_cells": half_green,
        "negative_lateral_final_green_cells": final_green,
        "half_failures": len(half_failures),
        "half_roll_leading_failures": roll_leading,
        "half_failure_rows": [
            {
                name: row[name]
                for name in (
                    "fit_id",
                    "command_x_m_s",
                    "rows",
                    "first_failure_axis",
                    "first_absolute_roll_crossing_tick",
                    "roll_at_first_roll_crossing_rad",
                    "first_absolute_pitch_crossing_tick",
                    "first_low_height_crossing_tick",
                )
            }
            for row in half_failures
        ],
        "paired_contexts_identical_between_checkpoints": contexts_equal,
        "early_action_lateral_joint_energy_share": lateral_share,
        "early_phase_correction_lateral_joint_energy_share": (
            correction_lateral_share
        ),
        "top_half_final_action_delta_joints": action_ranking[:6],
        "top_half_final_base_action_delta_joints": base_ranking[:6],
        "top_half_final_phase_correction_delta_joints": (
            correction_ranking[:6]
        ),
        "trace_rows_read": sum(len(value) for value in rows.values()),
    }
    value: dict[str, Any] = {
        "schema_version": (
            "open_duck.t166_lateral_persistence_autopsy_result.v1"
        ),
        "status": (
            "PASS_T166_LATERAL_PERSISTENCE_AUTOPSY"
            if passed
            else "HOLD_T166_LATERAL_PERSISTENCE_AUTOPSY"
        ),
        "decision": (
            prereg["decision_rule"]["pass_decision"]
            if passed
            else prereg["decision_rule"]["fail_decision"]
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "checks": checks,
        "failed_checks": failed,
        "summary": summary,
        "cell_metrics": cell_metrics,
        "half_final_pairs": half_final_pairs,
        "condition_control_pairs": condition_control_pairs,
        "rankings": {
            "half_final_action": action_ranking,
            "half_final_base_action": base_ranking,
            "half_final_phase_action_correction": correction_ranking,
        },
        "execution": {
            "trace_rows_read": summary["trace_rows_read"],
            "behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": prereg["authority"],
    }
    value["result_sha256"] = canonical_sha256(value)
    RESULT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T166 lateral-persistence autopsy result\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Decision: `{value['decision']}`\n"
        f"- Negative-lateral half/final: `{half_green}/8` / "
        f"`{final_green}/8`\n"
        f"- Roll-leading half failures: `{roll_leading}/"
        f"{len(half_failures)}`\n"
        f"- Early action lateral-joint energy share: "
        f"`{lateral_share:.6f}`\n"
        f"- Trace rows read: `{summary['trace_rows_read']}`\n"
        "- New behavior / optimizer / Colab / robot: `0 / 0 / 0 / 0`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(value["decision"])
    print(json.dumps(summary, allow_nan=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
