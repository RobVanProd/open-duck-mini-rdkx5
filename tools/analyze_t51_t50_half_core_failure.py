#!/usr/bin/env python3
"""Attribute T50's failure and select the sole remaining causal variant."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
T50_RESULT = ANALYSIS / "t50_uniform_half_core_qualification_result.json"
T49_RESULT = ANALYSIS / "t49_missing_combined_adapter_control_result.json"
OUTPUT = ANALYSIS / "t51_t50_half_core_failure_attribution.json"
MARKDOWN = (
    ANALYSIS / "T51_T50_HALF_CORE_FAILURE_ATTRIBUTION_20260728.md"
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


def rows(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def first_tick(
    values: list[dict[str, Any]],
    predicate: Callable[[dict[str, Any]], bool],
) -> int | None:
    return next(
        (int(row["tick"]) for row in values if predicate(row)),
        None,
    )


def trace_summary(path: Path) -> dict[str, Any]:
    values = rows(path)
    return {
        **receipt(path),
        "rows": len(values),
        "last_tick": int(values[-1]["tick"]),
        "ticks_contiguous_from_zero": (
            [int(row["tick"]) for row in values]
            == list(range(len(values)))
        ),
        "first_abs_pitch_over_0p25_tick": first_tick(
            values,
            lambda row: abs(float(row["body_pitch_rad"])) > 0.25,
        ),
        "first_abs_pitch_over_0p5_tick": first_tick(
            values,
            lambda row: abs(float(row["body_pitch_rad"])) > 0.5,
        ),
        "first_base_height_below_0p12_tick": first_tick(
            values, lambda row: float(row["base_height_m"]) < 0.12
        ),
        "first_no_foot_contact_tick": first_tick(
            values, lambda row: not any(row["foot_contacts"])
        ),
        "last_body_roll_rad": float(values[-1]["body_roll_rad"]),
        "last_body_pitch_rad": float(values[-1]["body_pitch_rad"]),
        "last_base_height_m": float(values[-1]["base_height_m"]),
    }


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T51 output: {path}")
    t50 = json.loads(T50_RESULT.read_text(encoding="utf-8"))
    t49 = json.loads(T49_RESULT.read_text(encoding="utf-8"))
    failed_cells = [
        cell
        for block in t50["blocks"]
        for cell in block["result"]["cells"]
        if not cell["cell_green"]
    ]
    failure = failed_cells[0]
    failure_path = Path(failure["protection"]["path"])
    controls = [
        cell
        for block in t50["blocks"]
        for cell in block["result"]["cells"]
        if cell is not failure
    ]
    head_cell = next(
        cell
        for cell in t49["cells"]
        if cell["variant_id"] == "FINAL_WITH_HALF_HEAD"
    )
    core_cell = next(
        cell
        for cell in t49["cells"]
        if cell["variant_id"] == "FINAL_WITH_HALF_CORE"
    )
    combined_cell = next(
        cell
        for cell in t49["cells"]
        if cell["variant_id"] == "FINAL_WITH_HALF_CORE_HEAD"
    )
    failure_trace = trace_summary(failure_path)
    checks = {
        "t50_stopped_at_first_condition": (
            t50["status"] == "HOLD_T50_UNIFORM_HALF_CORE_QUALIFICATION"
            and t50["decision"] == "CLOSE_T50_UNIFORM_HALF_CORE_TRANSFORM"
            and t50["summary"]["completed_conditions"] == 1
            and t50["summary"]["first_failed_condition"]
            == "FLOOR_FRICTION_LO"
        ),
        "exactly_one_failed_cell": len(failed_cells) == 1,
        "failure_identity_exact": (
            failure["command_x_m_s"] == 0.077
            and failure["behavior"]["samples"] == 163
            and failure["behavior"]["termination_reason"] == "fall_or_nan"
        ),
        "failure_contract_and_non_duration_quality_green": (
            failure["behavior"]["replacement_quality_pass"]
            and failure["handoff"]["all_checks_pass"]
            and failure["override_readback_exact"]
            and failure["protection"]["duration_protection_pass"]
            and failure["behavior"]["instant_rate_excess_rad_s"] == 0.0
            and failure["behavior"]["p95_rate_excess_rad_s"] == 0.0
            and failure["behavior"]["action_saturation_pct"] == 0.0
        ),
        "other_fifteen_cells_green": (
            len(controls) == 15
            and all(cell["cell_green"] for cell in controls)
        ),
        "early_forward_pitch_collapse_exact": (
            failure_trace["first_abs_pitch_over_0p25_tick"] == 136
            and failure_trace["first_abs_pitch_over_0p5_tick"] == 149
            and failure_trace["first_base_height_below_0p12_tick"] == 155
            and failure_trace["last_tick"] == 162
        ),
        "completed_factorial_both_one_group_variants_green": (
            t49["status"]
            == "PASS_T49_COMPLETED_ADAPTER_ONE_SUBBLOCK_CAUSE"
            and core_cell["cell_green"]
            and head_cell["cell_green"]
        ),
        "core_was_selected_and_is_now_closed": (
            t49["summary"]["selected_mechanism_variant_diagnostic"]
            == "FINAL_WITH_HALF_CORE"
            and t49["summary"]["selected_half_groups"] == ["core"]
        ),
        "head_is_only_remaining_nonduplicating_variant": (
            not head_cell["semantically_equals_half_endpoint"]
            and combined_cell["semantically_equals_half_endpoint"]
        ),
        "head_policy_asset_exact": (
            sha256(Path(head_cell["policy"]["path"]))
            == head_cell["policy"]["sha256"]
        ),
        "no_new_behavior_or_training": True,
        "robot_or_rdk_zero": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    result: dict[str, Any] = {
        "schema_version": (
            "open_duck.t51_t50_half_core_failure_attribution.v1"
        ),
        "status": (
            "PASS_T51_T50_HALF_CORE_FAILURE_ATTRIBUTION"
            if not failed
            else "HOLD_T51_T50_HALF_CORE_FAILURE_ATTRIBUTION"
        ),
        "decision": (
            "EARN_T52_FINAL_WITH_HALF_HEAD_UNIFORM_TRANSFORM_"
            "QUALIFICATION_PREREGISTRATION"
            if not failed
            else "STOP_T51_AND_REVIEW_ATTRIBUTION"
        ),
        "finding": (
            "The selected half-core transform repairs T46's condition-4 "
            "cell but creates one early final/P31-34/x=.077 collapse in "
            "condition 1. The completed causal factorial leaves exactly "
            "one nonduplicating, independently sufficient alternative: "
            "the half output head. It earns one full conditions 1-4 "
            "qualification, not policy promotion."
        ),
        "failure": {
            "condition_id": "FLOOR_FRICTION_LO",
            "checkpoint_id": "T50_UNIFORM_HALF_CORE_FINAL",
            "fit_id": "p31_34",
            "command_x_m_s": 0.077,
            "cell": failure,
            "trace": failure_trace,
        },
        "causal_successor": {
            "variant_id": head_cell["variant_id"],
            "half_groups": head_cell["half_groups"],
            "policy": head_cell["policy"],
            "original_failed_cell_green": head_cell["cell_green"],
            "original_failed_cell_samples": head_cell["behavior"]["samples"],
            "only_remaining_nonduplicating_one_group_variant": True,
        },
        "closed_variants": {
            "selected_core": {
                "variant_id": core_cell["variant_id"],
                "reason": "failed T50 qualification",
            },
            "combined": {
                "variant_id": combined_cell["variant_id"],
                "reason": "duplicates half endpoint",
            },
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
            "half_head_qualification_preregistration": not failed,
            "qualification_execution": False,
            "policy_promotion": False,
            "training": False,
            "colab": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    result["result_sha256"] = canonical_sha256(result)
    OUTPUT.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T51 T50 half-core failure attribution",
                "",
                f"- Status: `{result['status']}`",
                f"- Decision: `{result['decision']}`",
                "- Failure: condition 1 / final / P31-34 / x=.077",
                "- Duration: 163 rows; last tick 162",
                "- Forward pitch >.25/.5: ticks 136/149",
                "- Base height <.12: tick 155",
                "- Other condition-1 cells: `15/15` green",
                "- Sole remaining nonduplicating cause: half output head",
                "- New behavior/training/Colab/robot: `0/0/0/0`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(result["status"])
    print(f"failed_checks={failed}")
    print(f"decision={result['decision']}")
    print(f"result_sha256={result['result_sha256']}")
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
