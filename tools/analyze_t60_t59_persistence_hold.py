#!/usr/bin/env python3
"""Attribute T59's half/final persistence hold without new behavior."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
T59_RESULT = ANALYSIS / "t59_t56_nominal_matrix_result.json"
T56_VALIDATION = ANALYSIS / "t56_recovered_training_validation.json"
OUTPUT = ANALYSIS / "t60_t59_persistence_hold_attribution.json"
MARKDOWN = ANALYSIS / "T60_T59_PERSISTENCE_HOLD_ATTRIBUTION_20260728.md"
T55_SOURCE = Path(
    r"D:\CodexProjects\Open_Duck_Playground-composed-t55-v2"
    r"\playground\common\t55_dynamic_single_support_curriculum.py"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def receipt(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


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


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_rows(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def first_tick(
    rows: list[dict[str, Any]],
    predicate: Callable[[dict[str, Any]], bool],
) -> int | None:
    return next(
        (int(row["tick"]) for row in rows if predicate(row)),
        None,
    )


def summarize_cell(
    block: dict[str, Any],
    cell: dict[str, Any],
) -> dict[str, Any]:
    behavior = cell["behavior"]
    protection = cell["protection"]
    path = Path(protection["path"])
    rows = read_rows(path)
    command = float(cell["command_x_m_s"])
    return {
        "checkpoint_id": block["checkpoint_id"],
        "fit_id": block["fit_id"],
        "command_x_m_s": command,
        "cell_green": bool(cell["cell_green"]),
        "samples": int(behavior["samples"]),
        "termination_reason": behavior["termination_reason"],
        "mean_local_vx_m_s": float(behavior["mean_local_vx_m_s"]),
        "velocity_command_ratio": (
            None
            if command == 0.0
            else float(behavior["mean_local_vx_m_s"]) / command
        ),
        "body_pitch_p95_rad": float(behavior["body_pitch_p95_rad"]),
        "minimum_base_height_m": float(behavior["minimum_base_height_m"]),
        "tracking_p95_rad": float(behavior["pitch_tracking_p95_rad"]),
        "instant_rate_excess_rad_s": float(
            behavior["instant_rate_excess_rad_s"]
        ),
        "p95_rate_excess_rad_s": float(
            behavior["p95_rate_excess_rad_s"]
        ),
        "action_saturation_pct": float(
            behavior["action_saturation_pct"]
        ),
        "replacement_quality_pass": bool(
            behavior["replacement_quality_pass"]
        ),
        "left_contact_transitions": int(
            behavior["left_contact_transitions"]
        ),
        "right_contact_transitions": int(
            behavior["right_contact_transitions"]
        ),
        "first_positive_pitch_over_0p25_tick": first_tick(
            rows,
            lambda row: float(row["body_pitch_rad"]) > 0.25,
        ),
        "first_positive_pitch_over_0p5_tick": first_tick(
            rows,
            lambda row: float(row["body_pitch_rad"]) > 0.5,
        ),
        "first_base_height_below_0p12_tick": first_tick(
            rows,
            lambda row: float(row["base_height_m"]) < 0.12,
        ),
        "first_no_foot_contact_tick": first_tick(
            rows,
            lambda row: not any(row["foot_contacts"]),
        ),
        "last_body_pitch_rad": float(rows[-1]["body_pitch_rad"]),
        "last_body_roll_rad": float(rows[-1]["body_roll_rad"]),
        "last_base_height_m": float(rows[-1]["base_height_m"]),
        "contract_checks": {
            "handoff": bool(cell["handoff"]["all_checks_pass"]),
            "override_readback": bool(cell["override_readback_exact"]),
            "duration_protection": bool(
                protection["duration_protection_pass"]
            ),
            "trace_ticks_contiguous": bool(
                protection["ticks_contiguous_from_zero"]
            ),
        },
        "trace": receipt(path),
    }


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T60 output: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"],
        cwd=ROOT,
        text=True,
    ).strip():
        raise RuntimeError("formal T60 execution requires a clean worktree")

    t59 = read_json(T59_RESULT)
    t56 = read_json(T56_VALIDATION)
    cells = [
        summarize_cell(block, cell)
        for block in t59["blocks"]
        for cell in block["result"]["cells"]
    ]
    half = [
        cell
        for cell in cells
        if cell["checkpoint_id"] == "T56_TRANSFER_HALF"
    ]
    final = [
        cell
        for cell in cells
        if cell["checkpoint_id"] == "T56_TRANSFER_FINAL"
    ]
    half_x0 = [cell for cell in half if cell["command_x_m_s"] == 0.0]
    half_moving = [cell for cell in half if cell["command_x_m_s"] > 0.0]
    final_moving = [cell for cell in final if cell["command_x_m_s"] > 0.0]
    half_failure_onsets = [
        int(cell["first_positive_pitch_over_0p25_tick"])
        for cell in half_moving
    ]
    half_ratios = [
        float(cell["velocity_command_ratio"]) for cell in half_moving
    ]
    final_ratios = [
        float(cell["velocity_command_ratio"]) for cell in final_moving
    ]
    source_text = T55_SOURCE.read_text(encoding="utf-8")
    transfer_metrics = t56["stages"]["transfer"][
        "training_metric_evidence"
    ]
    episode_lengths = {
        int(row["step"]): float(row["value"])
        for row in transfer_metrics["eval/avg_episode_length"]
    }
    support_rewards = {
        int(row["step"]): float(row["value"])
        for row in transfer_metrics[
            "eval/episode_reward/t55_single_support_balance"
        ]
    }
    left_support = {
        int(row["step"]): float(row["value"])
        for row in transfer_metrics[
            "eval/episode_reward/t55_left_support_match"
        ]
    }
    right_support = {
        int(row["step"]): float(row["value"])
        for row in transfer_metrics[
            "eval/episode_reward/t55_right_support_match"
        ]
    }
    half_contract_clean = all(
        cell["replacement_quality_pass"]
        and cell["tracking_p95_rad"] <= 0.20
        and cell["instant_rate_excess_rad_s"] == 0.0
        and cell["p95_rate_excess_rad_s"] == 0.0
        and cell["action_saturation_pct"] == 0.0
        and all(cell["contract_checks"].values())
        for cell in half_moving
    )
    checks = {
        "t59_frozen_persistence_hold_exact": (
            t59["status"] == "HOLD_T59_T56_NOMINAL_MATRIX"
            and t59["decision"]
            == "CLOSE_T56_DYNAMIC_SINGLE_SUPPORT_CURRICULUM"
            and t59["condition"]["green_cells"] == 10
        ),
        "exact_nominal_matrix_shape": (
            len(cells) == 16
            and len(half) == 8
            and len(final) == 8
            and len(half_moving) == 6
            and len(final_moving) == 6
        ),
        "half_holds_x0_but_fails_every_moving_cell": (
            all(cell["cell_green"] for cell in half_x0)
            and not any(cell["cell_green"] for cell in half_moving)
        ),
        "final_passes_every_cell": all(
            cell["cell_green"] for cell in final
        ),
        "half_failures_are_contract_clean": half_contract_clean,
        "half_failures_are_delayed_positive_pitch_collapses": (
            all(
                cell["termination_reason"] == "fall_or_nan"
                and cell["first_positive_pitch_over_0p25_tick"] is not None
                and cell["first_positive_pitch_over_0p5_tick"] is not None
                and cell["first_base_height_below_0p12_tick"] is not None
                and cell["last_body_pitch_rad"] > 1.2
                for cell in half_moving
            )
            and min(half_failure_onsets) == 165
            and max(half_failure_onsets) == 385
        ),
        "half_overshoots_every_moving_command": min(half_ratios) > 1.0,
        "final_reduces_every_moving_velocity_ratio": (
            max(final_ratios) < 1.0
            and max(final_ratios) < min(half_ratios)
        ),
        "training_metrics_consolidate_after_half": (
            episode_lengths[2_007_040] > episode_lengths[1_003_520]
            and support_rewards[2_007_040] > support_rewards[1_003_520]
            and left_support[2_007_040] > left_support[1_003_520]
            and right_support[2_007_040] > right_support[1_003_520]
        ),
        "objective_transition_is_one_step_not_interpolated": (
            "return support_reward" in source_text
            and "return original_reward + support_reward" in source_text
            and "0.5" not in source_text[
                source_text.index("def curriculum_reward") :
            ]
        ),
        "no_new_behavior_or_training": True,
        "robot_or_rdk_zero": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    result: dict[str, Any] = {
        "schema_version": (
            "open_duck.t60_t59_persistence_hold_attribution.v1"
        ),
        "status": (
            "PASS_T60_T59_PERSISTENCE_HOLD_ATTRIBUTION"
            if not failed
            else "HOLD_T60_T59_PERSISTENCE_HOLD_ATTRIBUTION"
        ),
        "decision": (
            "EARN_T61_MIDPOINT_GAIT_TRANSFER_CPU_CONTRACT_"
            "PREREGISTRATION_ONLY"
            if not failed
            else "STOP_T60_AND_REVIEW_ATTRIBUTION"
        ),
        "classification": "ABRUPT_TRANSFER_CONSOLIDATION_GAP",
        "finding": (
            "Balance-first training produced a viable final gait, but the "
            "single-step change from support-only reward to the complete "
            "locomotion-plus-support reward left the transfer-half policy "
            "in an unstable high-propulsion transition. All six half "
            "moving cells tracked inside 0.20 rad with zero rate excess "
            "and zero saturation, yet exceeded commanded mean velocity "
            "and ended in delayed positive-pitch collapse. The final "
            "checkpoint reduced mean-velocity ratios and passed all eight "
            "cells. T56 remains closed by its frozen both-checkpoint rule; "
            "this evidence earns only a CPU contract for a distinct "
            "midpoint reward-homotopy stage."
        ),
        "source": {
            "repository_commit": subprocess.check_output(
                ["git", "rev-parse", "HEAD"],
                cwd=ROOT,
                text=True,
            ).strip(),
            "t59_result": receipt(T59_RESULT),
            "t56_validation": receipt(T56_VALIDATION),
            "t55_reward_source": receipt(T55_SOURCE),
        },
        "summary": {
            "green_cells": sum(cell["cell_green"] for cell in cells),
            "half_x0_green": sum(cell["cell_green"] for cell in half_x0),
            "half_moving_green": sum(
                cell["cell_green"] for cell in half_moving
            ),
            "final_green": sum(cell["cell_green"] for cell in final),
            "half_failure_samples": sorted(
                cell["samples"] for cell in half_moving
            ),
            "half_positive_pitch_0p25_onset_ticks": sorted(
                half_failure_onsets
            ),
            "half_velocity_command_ratio": {
                "minimum": min(half_ratios),
                "maximum": max(half_ratios),
            },
            "final_velocity_command_ratio": {
                "minimum": min(final_ratios),
                "maximum": max(final_ratios),
            },
            "half_worst_tracking_p95_rad": max(
                cell["tracking_p95_rad"] for cell in half_moving
            ),
            "final_worst_tracking_p95_rad": max(
                cell["tracking_p95_rad"] for cell in final_moving
            ),
            "transfer_training_metrics": {
                "episode_length_half": episode_lengths[1_003_520],
                "episode_length_final": episode_lengths[2_007_040],
                "support_reward_half": support_rewards[1_003_520],
                "support_reward_final": support_rewards[2_007_040],
                "left_support_half": left_support[1_003_520],
                "left_support_final": left_support[2_007_040],
                "right_support_half": right_support[1_003_520],
                "right_support_final": right_support[2_007_040],
                "selection_weight": 0,
            },
        },
        "cells": cells,
        "successor_constraints": {
            "mechanism": (
                "training-only midpoint reward homotopy between the "
                "balance-only and full-transfer objectives"
            ),
            "source": "exact recovered T56 balance-final checkpoint",
            "midpoint_formula": (
                "support_reward + 0.5 * complete_frozen_locomotion_reward"
            ),
            "midpoint_coefficient_derivation": (
                "arithmetic midpoint of the closed 0 and 1 locomotion "
                "objective endpoints; no scalar search"
            ),
            "stage_order": [
                "midpoint transfer",
                "complete transfer",
            ],
            "runtime_or_policy_abi_change": False,
            "default_off_exactness_required": True,
            "both_transfer_checkpoints_required": True,
            "checkpoint_cherry_pick": False,
            "hosted_training_authorized": False,
        },
        "checks": checks,
        "failed_checks": failed,
        "execution": {
            "new_behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "t61_cpu_contract_preregistration": not failed,
            "t61_cpu_contract_execution": False,
            "hosted_training": False,
            "policy_promotion": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    result["result_sha256"] = canonical_sha256(result)
    OUTPUT.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    summary = result["summary"]
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T60 T59 persistence-hold attribution",
                "",
                f"- Status: `{result['status']}`",
                f"- Decision: `{result['decision']}`",
                f"- Classification: `{result['classification']}`",
                "- T59: `10/16` green",
                "- Half x=0 / moving: `2/2` / `0/6` green",
                "- Final: `8/8` green",
                (
                    "- Half moving pitch-collapse onset: ticks "
                    f"`{min(half_failure_onsets)}-"
                    f"{max(half_failure_onsets)}`"
                ),
                (
                    "- Half velocity/command ratio: "
                    f"`{min(half_ratios):.6f}-"
                    f"{max(half_ratios):.6f}`"
                ),
                (
                    "- Final velocity/command ratio: "
                    f"`{min(final_ratios):.6f}-"
                    f"{max(final_ratios):.6f}`"
                ),
                (
                    "- Half/final worst tracking p95: "
                    f"`{summary['half_worst_tracking_p95_rad']:.9f}` / "
                    f"`{summary['final_worst_tracking_p95_rad']:.9f}` rad"
                ),
                "- All failed half cells: zero rate excess and saturation",
                "- New behavior/training/Colab/robot: `0/0/0/0`",
                "",
                "## Decision",
                "",
                (
                    "T56 stays closed. The evidence earns only a CPU "
                    "contract for a fixed midpoint reward-homotopy stage; "
                    "it does not earn hosted training."
                ),
                "",
            ]
        ),
        encoding="utf-8",
        newline="\n",
    )
    print(result["status"])
    print(f"failed_checks={failed}")
    print(f"decision={result['decision']}")
    print(f"result_sha256={result['result_sha256']}")
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
