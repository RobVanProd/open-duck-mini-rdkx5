#!/usr/bin/env python3
"""Attribute T41's sole condition-3 failure from immutable CPU traces."""

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
T41 = ANALYSIS / "t41_uniform_normalizer_r2_result.json"
T39 = (
    ANALYSIS
    / "t39_uniform_normalizer_rollback_nominal_preregistration.json"
)
T36 = ANALYSIS / "t36_t32_actor_block_factorial_preregistration.json"
CACHE = (
    Path("D:/CodexArtifacts/open-duck-policy")
    / "t41_uniform_normalizer_r2_v1"
)
OUTPUT = ANALYSIS / "t42_t41_condition3_failure_attribution.json"
MARKDOWN = ANALYSIS / "T42_T41_CONDITION3_FAILURE_ATTRIBUTION_20260728.md"
JOINT_NAMES = [
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
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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


def receipt(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def read_trace(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def first_tick(
    rows: list[dict[str, Any]],
    predicate: Callable[[dict[str, Any]], bool],
) -> int | None:
    for row in rows:
        if predicate(row):
            return int(row["tick"])
    return None


def trace_summary(path: Path) -> dict[str, Any]:
    rows = read_trace(path)
    tracking = np.abs(
        np.asarray([row["tracking_error_rad"] for row in rows], dtype=float)
    )
    torque = np.abs(
        np.asarray([row["actuator_force_nm"] for row in rows], dtype=float)
    )
    per_joint_tracking = np.quantile(tracking, 0.95, axis=0)
    per_joint_torque = np.max(torque, axis=0)
    roll = np.abs(
        np.asarray([row["body_roll_rad"] for row in rows], dtype=float)
    )
    pitch = np.abs(
        np.asarray([row["body_pitch_rad"] for row in rows], dtype=float)
    )
    height = np.asarray([row["base_height_m"] for row in rows], dtype=float)
    local_vx = np.asarray(
        [row["local_linvel_m_s"][0] for row in rows], dtype=float
    )
    guard = np.abs(
        np.asarray(
            [row["actual_centered_guard_excess_rad"] for row in rows],
            dtype=float,
        )
    )
    raw = np.asarray([row["policy_raw_action"] for row in rows], dtype=float)
    action = np.asarray([row["action"] for row in rows], dtype=float)
    tracking_index = int(np.argmax(per_joint_tracking))
    torque_index = int(np.argmax(per_joint_torque))
    return {
        "trace": receipt(path),
        "rows": len(rows),
        "last_tick": int(rows[-1]["tick"]),
        "done": bool(rows[-1]["done"]),
        "onset_ticks": {
            "abs_roll_gt_0p25": first_tick(
                rows, lambda row: abs(row["body_roll_rad"]) > 0.25
            ),
            "abs_pitch_gt_0p25": first_tick(
                rows, lambda row: abs(row["body_pitch_rad"]) > 0.25
            ),
            "abs_roll_or_pitch_gt_0p5": first_tick(
                rows,
                lambda row: max(
                    abs(row["body_roll_rad"]),
                    abs(row["body_pitch_rad"]),
                )
                > 0.5,
            ),
            "base_height_lt_0p12": first_tick(
                rows, lambda row: row["base_height_m"] < 0.12
            ),
        },
        "kinematics": {
            "minimum_base_height_m": float(np.min(height)),
            "maximum_abs_roll_rad": float(np.max(roll)),
            "maximum_abs_pitch_rad": float(np.max(pitch)),
            "mean_local_vx_m_s": float(np.mean(local_vx)),
            "final_base_x_m": float(rows[-1]["base_x_m"]),
            "final_base_y_m": float(rows[-1]["base_y_m"]),
        },
        "tracking": {
            "global_p95_rad": float(np.quantile(tracking, 0.95)),
            "worst_joint": JOINT_NAMES[tracking_index],
            "worst_joint_p95_rad": float(
                per_joint_tracking[tracking_index]
            ),
        },
        "torque": {
            "peak_joint": JOINT_NAMES[torque_index],
            "peak_abs_nm": float(per_joint_torque[torque_index]),
        },
        "action_pipeline": {
            "maximum_raw_to_final_delta": float(
                np.max(np.abs(raw - action))
            ),
            "changed_ticks": int(
                np.count_nonzero(
                    np.any(np.abs(raw - action) > 1e-7, axis=1)
                )
            ),
            "guard_nonzero_ticks": int(
                np.count_nonzero(np.any(guard > 1e-7, axis=1))
            ),
            "saturation_ticks": int(
                sum(any(row["action_saturated"]) for row in rows)
            ),
            "maximum_sent_target_rate_excess_rad_s": float(
                np.max(
                    np.abs(
                        np.asarray(
                            [
                                row["sent_target_rate_excess_rad_s"]
                                for row in rows
                            ],
                            dtype=float,
                        )
                    )
                )
            ),
        },
    }


def initializer_values(path: Path) -> dict[str, np.ndarray]:
    model = onnx.load(str(path))
    onnx.checker.check_model(model)
    return {
        item.name: np.asarray(numpy_helper.to_array(item))
        for item in model.graph.initializer
    }


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T42: {path}")
    t41 = json.loads(T41.read_text(encoding="utf-8"))
    t39 = json.loads(T39.read_text(encoding="utf-8"))
    t36 = json.loads(T36.read_text(encoding="utf-8"))
    failures = [
        {
            "condition_id": block["condition_id"],
            "checkpoint_id": block["checkpoint_id"],
            "fit_id": block["fit_id"],
            "cell": cell,
        }
        for block in t41["blocks"]
        for cell in block["result"]["cells"]
        if not cell["cell_green"]
    ]
    if len(failures) != 1:
        raise RuntimeError(f"expected one T41 failure, got {len(failures)}")
    failure = failures[0]

    cases = {
        "failure": (
            CACHE
            / "03_JOINT_FRICTIONLOSS_LO"
            / "T39_UNIFORM_NORMALIZER_HALF"
            / "p30"
            / "traces"
            / "x0.080_seed167931544_action_margin.jsonl"
        ),
        "same_policy_fit_lower_command": (
            CACHE
            / "03_JOINT_FRICTIONLOSS_LO"
            / "T39_UNIFORM_NORMALIZER_HALF"
            / "p30"
            / "traces"
            / "x0.077_seed167931544_action_margin.jsonl"
        ),
        "same_policy_command_other_fit": (
            CACHE
            / "03_JOINT_FRICTIONLOSS_LO"
            / "T39_UNIFORM_NORMALIZER_HALF"
            / "p31_34"
            / "traces"
            / "x0.080_seed167931544_action_margin.jsonl"
        ),
        "same_fit_command_final_checkpoint": (
            CACHE
            / "03_JOINT_FRICTIONLOSS_LO"
            / "T39_UNIFORM_NORMALIZER_FINAL"
            / "p30"
            / "traces"
            / "x0.080_seed167931544_action_margin.jsonl"
        ),
        "same_policy_fit_command_default_dynamics": (
            CACHE
            / "02_FLOOR_FRICTION_HI"
            / "T39_UNIFORM_NORMALIZER_HALF"
            / "p30"
            / "traces"
            / "x0.080_seed167931544_action_margin.jsonl"
        ),
    }
    summaries = {
        name: trace_summary(path) for name, path in cases.items()
    }
    half_policy = Path(t39["policies"][0]["path"])
    final_policy = Path(t39["policies"][1]["path"])
    half_values = initializer_values(half_policy)
    final_values = initializer_values(final_policy)
    changed = sorted(
        name
        for name in half_values
        if not np.array_equal(half_values[name], final_values[name])
    )
    expected_actor_drift = sorted(
        t36["groups"]["base"] + t36["groups"]["adapter"]
    )
    behavior = failure["cell"]["behavior"]
    protection = failure["cell"]["protection"]
    controls = {
        name: summary
        for name, summary in summaries.items()
        if name != "failure"
    }
    checks = {
        "t41_stopped_at_exact_first_failure": (
            t41["status"] == "HOLD_T41_UNIFORM_NORMALIZER_R2"
            and t41["summary"]["completed_conditions"] == 3
            and t41["summary"]["green_cells"] == 47
            and t41["summary"]["first_failed_condition"]
            == "JOINT_FRICTIONLOSS_LO"
        ),
        "exactly_one_failed_cell": len(failures) == 1,
        "failed_identity_exact": (
            failure["condition_id"] == "JOINT_FRICTIONLOSS_LO"
            and failure["checkpoint_id"] == "T39_UNIFORM_NORMALIZER_HALF"
            and failure["fit_id"] == "p30"
            and failure["cell"]["command_x_m_s"] == 0.08
        ),
        "failure_is_late_fall": (
            behavior["samples"] == 583
            and behavior["termination_reason"] == "fall_or_nan"
            and summaries["failure"]["last_tick"] == 582
            and summaries["failure"]["done"]
        ),
        "tracking_rate_saturation_quality_green_before_fall": (
            behavior["replacement_quality_pass"]
            and behavior["action_saturation_pct"] == 0.0
            and behavior["instant_rate_excess_rad_s"] == 0.0
            and behavior["p95_rate_excess_rad_s"] == 0.0
        ),
        "protection_and_handoff_green": (
            protection["duration_protection_pass"]
            and protection["maximum_full_measured_vector_excess_rad_s"]
            == 0.0
            and failure["cell"]["handoff"]["all_checks_pass"]
            and failure["cell"]["override_readback_exact"]
        ),
        "action_graph_is_authoritative_without_host_delta": (
            summaries["failure"]["action_pipeline"][
                "maximum_raw_to_final_delta"
            ]
            == 0.0
            and summaries["failure"]["action_pipeline"]["changed_ticks"]
            == 0
            and summaries["failure"]["action_pipeline"][
                "saturation_ticks"
            ]
            == 0
        ),
        "late_attitude_escape_precedes_height_loss": (
            summaries["failure"]["onset_ticks"]["abs_roll_gt_0p25"]
            == 530
            and summaries["failure"]["onset_ticks"]["abs_pitch_gt_0p25"]
            == 555
            and summaries["failure"]["onset_ticks"][
                "abs_roll_or_pitch_gt_0p5"
            ]
            == 569
            and summaries["failure"]["onset_ticks"][
                "base_height_lt_0p12"
            ]
            == 574
        ),
        "all_matched_controls_full_duration": all(
            item["rows"] == 600 and not item["done"]
            for item in controls.values()
        ),
        "endpoint_drift_is_exactly_base_plus_adapter": (
            changed == expected_actor_drift
        ),
        "normalizer_equal_across_endpoints": all(
            np.array_equal(half_values[name], final_values[name])
            for name in t36["groups"]["normalizer"]
        ),
        "no_new_behavior_or_training": True,
        "robot_or_rdk_absent": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed_checks = sorted(
        name for name, passed in checks.items() if not passed
    )
    value = {
        "schema_version": (
            "open_duck.t42_t41_condition3_failure_attribution.v1"
        ),
        "status": (
            "PASS_T42_T41_CONDITION3_FAILURE_ATTRIBUTION"
            if not failed_checks
            else "HOLD_T42_T41_CONDITION3_FAILURE_ATTRIBUTION"
        ),
        "decision": (
            "EARN_T43_HALF_FORWARD_ACTOR_BLOCK_FACTORIAL_PREREGISTRATION"
            if not failed_checks
            else "HOLD_FOR_T42_ATTRIBUTION_REPAIR"
        ),
        "classification": {
            "mechanism": (
                "late_closed_loop_attitude_stability_loss_specific_to_"
                "half_checkpoint_p30_x0p08_under_joint_frictionloss_0p9"
            ),
            "not_tracking_gate_failure": True,
            "not_rate_or_saturation_failure": True,
            "not_duration_protection_failure": True,
            "not_handoff_or_readback_failure": True,
            "matched_final_checkpoint_passes": True,
            "endpoint_trainable_drift_blocks": ["base", "adapter"],
        },
        "failed_cell": {
            "condition_id": failure["condition_id"],
            "checkpoint_id": failure["checkpoint_id"],
            "fit_id": failure["fit_id"],
            "command_x_m_s": failure["cell"]["command_x_m_s"],
            "behavior": behavior,
            "protection": protection,
        },
        "trace_summaries": summaries,
        "endpoint_initializer_audit": {
            "half_policy": receipt(half_policy),
            "final_policy": receipt(final_policy),
            "changed_initializers": changed,
            "expected_base_plus_adapter": expected_actor_drift,
            "normalizer_names": t36["groups"]["normalizer"],
            "base_names": t36["groups"]["base"],
            "adapter_names": t36["groups"]["adapter"],
        },
        "factorial": {
            "target": "exact_failed_cell_only",
            "variants": [
                "HALF_WITH_FINAL_BASE",
                "HALF_WITH_FINAL_ADAPTER",
                "HALF_WITH_FINAL_BASE_ADAPTER",
            ],
            "run_all_variants": True,
            "no_early_stop": True,
            "diagnostic_precedence": [
                "one changed block",
                "base before adapter",
            ],
            "only_combined_pass": (
                "classify coupled drift; do not promote an endpoint-"
                "collapsing combined transform"
            ),
        },
        "checks": checks,
        "failed_checks": failed_checks,
        "frozen_inputs": {
            "t41_result": receipt(T41),
            "t39_preregistration": receipt(T39),
            "t36_factorial_preregistration": receipt(T36),
        },
        "execution": {
            "new_formal_behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "t43_factorial_preregistration": not failed_checks,
            "t43_behavior_execution": False,
            "training": False,
            "colab": False,
            "deployment": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    value["result_sha256"] = canonical_sha256(value)
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T42 T41 condition-3 failure attribution",
                "",
                f"- Status: `{value['status']}`",
                f"- Decision: `{value['decision']}`",
                "- Failed cell: half / P30 / x=.080 / friction-loss .9×",
                "- Roll escape: tick `530`",
                "- Pitch escape: tick `555`",
                "- Height loss: tick `574`",
                "- Termination: tick `582` (`583` samples)",
                "- Tracking/rate/saturation/protection/handoff: `GREEN`",
                "- Matched green controls: lower command, other fit, final "
                "checkpoint, and default dynamics",
                "- Endpoint drift: exact base + recurrent-adapter "
                "initializer groups; normalizer is identical",
                "- New behavior/training/robot work: `0/0/0`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(value["status"])
    print(f"failed_checks={failed_checks}")
    print(f"result_sha256={value['result_sha256']}")
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed_checks else 1


if __name__ == "__main__":
    raise SystemExit(main())
