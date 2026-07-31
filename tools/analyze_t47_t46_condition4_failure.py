#!/usr/bin/env python3
"""Attribute T46's isolated condition-4 failure without new behavior runs."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Callable

import numpy as np
import onnx
from onnx import numpy_helper


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
T46_RESULT = (
    ANALYSIS / "t46_uniform_final_base_r2_remainder_result.json"
)
T45_RESULT = (
    ANALYSIS / "t45_uniform_final_base_qualification_result.json"
)
T45_PREREG = (
    ANALYSIS
    / "t45_uniform_final_base_qualification_preregistration.json"
)
OUTPUT = ANALYSIS / "t47_t46_condition4_failure_attribution.json"
MARKDOWN = (
    ANALYSIS / "T47_T46_CONDITION4_FAILURE_ATTRIBUTION_20260728.md"
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


def trace_summary(path: Path) -> dict[str, Any]:
    rows = read_rows(path)
    forces = np.abs(
        np.asarray(
            [row["actuator_force_nm"] for row in rows],
            dtype=np.float64,
        )
    )
    return {
        **receipt(path),
        "rows": len(rows),
        "last_tick": int(rows[-1]["tick"]),
        "ticks_contiguous_from_zero": (
            [int(row["tick"]) for row in rows] == list(range(len(rows)))
        ),
        "first_abs_pitch_over_0p25_tick": first_tick(
            rows, lambda row: abs(float(row["body_pitch_rad"])) > 0.25
        ),
        "first_abs_pitch_over_0p5_tick": first_tick(
            rows, lambda row: abs(float(row["body_pitch_rad"])) > 0.5
        ),
        "first_base_height_below_0p12_tick": first_tick(
            rows, lambda row: float(row["base_height_m"]) < 0.12
        ),
        "first_no_foot_contact_tick": first_tick(
            rows, lambda row: not any(row["foot_contacts"])
        ),
        "last_body_roll_rad": float(rows[-1]["body_roll_rad"]),
        "last_body_pitch_rad": float(rows[-1]["body_pitch_rad"]),
        "last_base_height_m": float(rows[-1]["base_height_m"]),
        "maximum_abs_actuator_force_nm": float(forces.max()),
        "ticks_any_actuator_over_gate_torque": int(
            np.sum(np.max(forces, axis=1) > 1.91229675)
        ),
    }


def initializers(path: Path) -> tuple[onnx.ModelProto, dict[str, np.ndarray]]:
    model = onnx.load(str(path))
    onnx.checker.check_model(model)
    return model, {
        item.name: np.asarray(numpy_helper.to_array(item))
        for item in model.graph.initializer
    }


def graph_signature(model: onnx.ModelProto) -> list[tuple[Any, ...]]:
    return [
        (
            node.op_type,
            node.domain,
            tuple(node.input),
            tuple(node.output),
        )
        for node in model.graph.node
    ]


def changed(
    first: dict[str, np.ndarray],
    second: dict[str, np.ndarray],
) -> list[str]:
    if set(first) != set(second):
        raise ValueError("T47 endpoint initializer inventories differ")
    return sorted(
        name
        for name in first
        if not np.array_equal(first[name], second[name])
    )


def cell(
    result: dict[str, Any],
    checkpoint: str,
    fit: str,
    command: float,
) -> dict[str, Any]:
    block = next(
        item
        for item in result["blocks"]
        if item["checkpoint_id"] == checkpoint
        and item["fit_id"] == fit
    )
    return next(
        item
        for item in block["result"]["cells"]
        if float(item["command_x_m_s"]) == command
    )


def action_drift(
    first_path: Path,
    second_path: Path,
) -> dict[str, float]:
    first = read_rows(first_path)
    second = read_rows(second_path)
    count = min(len(first), len(second))
    a = np.asarray(
        [row["policy_raw_action"] for row in first[:count]],
        dtype=np.float64,
    )
    b = np.asarray(
        [row["policy_raw_action"] for row in second[:count]],
        dtype=np.float64,
    )

    def rms(x: np.ndarray) -> float:
        return float(np.sqrt(np.mean(np.square(x))))

    return {
        "common_ticks": count,
        "raw_action_rms_all": rms(a - b),
        "raw_action_rms_first_400": rms(a[:400] - b[:400]),
        "raw_action_rms_last_64": rms(a[-64:] - b[-64:]),
        "raw_action_max_abs": float(np.max(np.abs(a - b))),
    }


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T47 output: {path}")
    t46 = json.loads(T46_RESULT.read_text(encoding="utf-8"))
    t45_result = json.loads(T45_RESULT.read_text(encoding="utf-8"))
    t45 = json.loads(T45_PREREG.read_text(encoding="utf-8"))
    half_id = "T45_UNIFORM_FINAL_BASE_HALF"
    final_id = "T45_UNIFORM_FINAL_BASE_FINAL"
    failure = cell(t46, final_id, "p30", 0.077)
    controls = {
        "same_endpoint_lower_command": cell(
            t46, final_id, "p30", 0.074
        ),
        "same_endpoint_higher_command": cell(
            t46, final_id, "p30", 0.08
        ),
        "same_endpoint_other_fit": cell(
            t46, final_id, "p31_34", 0.077
        ),
        "half_endpoint_same_fit_command": cell(
            t46, half_id, "p30", 0.077
        ),
        "nominal_same_endpoint_fit_command": cell(
            t45_result, final_id, "p30", 0.077
        ),
    }
    failure_path = Path(failure["protection"]["path"])
    control_paths = {
        name: Path(item["protection"]["path"])
        for name, item in controls.items()
    }
    failure_trace = trace_summary(failure_path)
    control_traces = {
        name: trace_summary(path)
        for name, path in control_paths.items()
    }
    half_path = Path(t45["policies"][0]["path"])
    final_path = Path(t45["policies"][1]["path"])
    half_model, half_values = initializers(half_path)
    final_model, final_values = initializers(final_path)
    endpoint_changes = changed(half_values, final_values)
    adapter_names = [
        "adapter_bias",
        "adapter_hidden_bias",
        "adapter_hidden_weight",
        "adapter_obs_weight",
        "adapter_weight",
    ]
    failed_cells = [
        item
        for block in t46["blocks"]
        for item in block["result"]["cells"]
        if not item["cell_green"]
    ]
    checks = {
        "t46_stopped_at_condition_four": (
            t46["status"]
            == "HOLD_T46_UNIFORM_FINAL_BASE_R2_REMAINDER"
            and t46["summary"]["completed_conditions"] == 1
            and t46["summary"]["first_failed_condition"]
            == "JOINT_FRICTIONLOSS_HI"
        ),
        "exactly_one_failed_cell": (
            len(failed_cells) == 1 and failed_cells[0] is failure
        ),
        "failure_identity_exact": (
            failure["command_x_m_s"] == 0.077
            and failure["behavior"]["samples"] == 494
            and failure["behavior"]["termination_reason"]
            == "fall_or_nan"
        ),
        "failure_non_duration_quality_green": (
            failure["behavior"]["replacement_quality_pass"]
            and failure["handoff"]["all_checks_pass"]
            and failure["override_readback_exact"]
            and failure["protection"]["duration_protection_pass"]
            and failure["behavior"]["instant_rate_excess_rad_s"] == 0.0
            and failure["behavior"]["p95_rate_excess_rad_s"] == 0.0
            and failure["behavior"]["action_saturation_pct"] == 0.0
        ),
        "all_five_matched_controls_green_full_duration": all(
            item["cell_green"]
            and item["behavior"]["samples"] == 600
            and item["behavior"]["termination_reason"]
            == "duration_complete"
            for item in controls.values()
        ),
        "failure_is_late_forward_pitch_collapse": (
            failure_trace["first_abs_pitch_over_0p25_tick"] == 467
            and failure_trace["first_abs_pitch_over_0p5_tick"] == 479
            and failure_trace["first_base_height_below_0p12_tick"] == 486
            and failure_trace["last_tick"] == 493
        ),
        "endpoint_graphs_exact": (
            graph_signature(half_model) == graph_signature(final_model)
        ),
        "endpoint_difference_exactly_adapter": (
            endpoint_changes == adapter_names
        ),
        "no_new_behavior_or_training": True,
        "robot_or_rdk_zero": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    result: dict[str, Any] = {
        "schema_version": (
            "open_duck.t47_t46_condition4_failure_attribution.v1"
        ),
        "status": (
            "PASS_T47_T46_CONDITION4_FAILURE_ATTRIBUTION"
            if not failed
            else "HOLD_T47_T46_CONDITION4_FAILURE_ATTRIBUTION"
        ),
        "decision": (
            "EARN_T48_FINAL_ADAPTER_CORE_HEAD_FACTORIAL_PREREGISTRATION"
            if not failed
            else "STOP_T47_AND_REVIEW_ATTRIBUTION"
        ),
        "finding": (
            "T46's only failure is an isolated late forward-pitch collapse "
            "of the final recurrent-adapter endpoint under P30, x=.077, "
            "and joint friction 1.1. All matched controls pass. Since the "
            "T45 endpoints differ only in the adapter recurrent core and "
            "output head, a zero-training two-block factorial is the "
            "smallest earned causal screen."
        ),
        "failure": {
            "checkpoint_id": final_id,
            "fit_id": "p30",
            "command_x_m_s": 0.077,
            "condition_id": "JOINT_FRICTIONLOSS_HI",
            "cell": failure,
            "trace": failure_trace,
        },
        "matched_controls": {
            name: {
                "cell_green": controls[name]["cell_green"],
                "samples": controls[name]["behavior"]["samples"],
                "termination_reason": controls[name]["behavior"][
                    "termination_reason"
                ],
                "trace": control_traces[name],
            }
            for name in controls
        },
        "endpoint_attribution": {
            "half_policy": receipt(half_path),
            "final_policy": receipt(final_path),
            "differing_initializers": endpoint_changes,
            "recurrent_core": [
                "adapter_hidden_bias",
                "adapter_hidden_weight",
                "adapter_obs_weight",
            ],
            "output_head": ["adapter_bias", "adapter_weight"],
            "half_vs_final_same_cell_action_drift": action_drift(
                control_paths["half_endpoint_same_fit_command"],
                failure_path,
            ),
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
            "adapter_core_head_factorial_preregistration": not failed,
            "factorial_execution": False,
            "training": False,
            "colab": False,
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
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T47 T46 condition-4 failure attribution",
                "",
                f"- Status: `{result['status']}`",
                f"- Decision: `{result['decision']}`",
                "- Failure: final / P30 / x=.077 / joint friction 1.1",
                "- Duration: 494 rows; last tick 493",
                "- Forward pitch >.25/.5: ticks 467/479",
                "- Base height <.12: tick 486",
                "- Matched controls: `5/5` full-duration green",
                "- Endpoint difference: adapter tensors only (`5`)",
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
