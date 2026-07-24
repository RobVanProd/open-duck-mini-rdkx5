#!/usr/bin/env python3
"""Run the preregistered V125 second-order predictive-box trace census."""

from __future__ import annotations

from collections import Counter, defaultdict
import argparse
import json
import math
from pathlib import Path
import sys
from typing import Any

import mujoco
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

import run_winner_v124_predictive_torque_s0_s2 as v124  # noqa: E402


ANALYSIS = ROOT / "outputs/analysis"
PREREG = ANALYSIS / "winner_v125_second_order_predictor_preregistration.json"
PREREG_SHA256 = (
    "c3218e1c7b86e7d7131f90d563aff0573b2f092db7f18b538fbaef7b34f13b1f"
)
V124_PREREG = (
    ANALYSIS / "winner_v124_predictive_torque_s0_s2_preregistration.json"
)
V124_COMPACT = (
    ANALYSIS / "winner_v124_predictive_torque_s0_s2_compact_result.json"
)
OUTPUT = ANALYSIS / "winner_v125_second_order_predictor_result.json"
MARKDOWN = ANALYSIS / "WINNER_V125_SECOND_ORDER_PREDICTOR_RESULT_20260724.md"


def predictor(
    trace: dict[str, Any],
    decision_tick: int,
    delay_ticks: int,
    joint_index: int,
    sim_dt_s: float,
) -> tuple[float, float]:
    q_pre = float(trace["actual_position_pre_rad"][decision_tick, joint_index])
    qdot = float(
        trace["obs_state"][decision_tick, 27 + joint_index]
        / v124.DOF_VEL_SCALE
    )
    if decision_tick == 0:
        qddot = 0.0
    else:
        previous_qdot = float(
            trace["obs_state"][decision_tick - 1, 27 + joint_index]
            / v124.DOF_VEL_SCALE
        )
        qddot = (qdot - previous_qdot) / v124.CONTROL_DT_S
    horizon_s = (
        (delay_ticks + 1) * v124.CONTROL_DT_S - sim_dt_s
    )
    return (
        q_pre + horizon_s * qdot + 0.5 * horizon_s**2 * qddot,
        horizon_s,
    )


def robust_interval(
    *,
    trace: dict[str, Any],
    dual_applied: dict[str, np.ndarray],
    params: dict[str, list[v124.JointActuatorParams]],
    decision_tick: int,
    joint_index: int,
    half_width_rad: float,
    sim_dt_s: float,
) -> tuple[float, float]:
    low = -math.inf
    high = math.inf
    for plant in v124.PLANTS:
        param = params[plant][joint_index]
        event_tick = decision_tick + param.delay_ticks
        if event_tick >= len(trace["rows"]):
            return math.inf, -math.inf
        previous_applied = (
            v124.HOME[joint_index]
            if event_tick == 0
            else float(dual_applied[plant][event_tick - 1, joint_index])
        )
        center, _ = predictor(
            trace,
            decision_tick,
            param.delay_ticks,
            joint_index,
            sim_dt_s,
        )
        fit_low, fit_high = v124.bridge_target_interval(
            previous_applied=previous_applied,
            home=float(v124.HOME[joint_index]),
            param=param,
            safe_low=center - half_width_rad,
            safe_high=center + half_width_rad,
        )
        low = max(low, fit_low)
        high = min(high, fit_high)
    return low, high


def count_by(rows: list[dict[str, Any]], key: str) -> dict[str, int]:
    return dict(sorted(Counter(str(row[key]) for row in rows).items()))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    args = parser.parse_args()
    del args
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V125: {path}")
    prereg = v124.read_json(PREREG)
    if (
        v124.sha256(PREREG) != PREREG_SHA256
        or prereg.get("status")
        != "PREREGISTERED_WINNER_V125_SECOND_ORDER_PREDICTOR"
        or prereg.get("failed_checks") != []
        or not prereg.get("authority", {}).get(
            "v125_trace_analysis_authorized"
        )
    ):
        raise ValueError("V125 preregistration is not exact and passing")
    input_paths = {
        "v124_compact_result": V124_COMPACT,
        "v124_preregistration": V124_PREREG,
        "v124_amendment": (
            ANALYSIS / "winner_v124_s0_ctrl_tolerance_amendment.json"
        ),
        "v124_runner": (
            ROOT / "tools/run_winner_v124_predictive_torque_s0_s2.py"
        ),
        "bridge_model": ROOT / "tools/actuator_bridge_model.py",
        "v121_transform": v124.TRANSFORM,
        "plant_preregistration": v124.PLANT_PREREG,
    }
    if {
        name: v124.sha256(path) for name, path in input_paths.items()
    } != prereg["input_hashes"]:
        raise ValueError("V125 frozen inputs changed")

    v124_prereg = v124.read_json(V124_PREREG)
    trace_manifest = v124_prereg["trace_inputs"]["v121"]
    run_root = Path(v124_prereg["trace_inputs"]["v121_run_root"])
    traces = []
    for item in trace_manifest:
        path = run_root / "traces" / item["filename"]
        if v124.sha256(path) != item["sha256"]:
            raise ValueError(f"V121 trace changed: {path}")
        traces.append(v124.load_trace(path))
    plant_prereg = v124.read_json(v124.PLANT_PREREG)
    params = v124.fit_params(plant_prereg)
    transform = v124.read_json(v124.TRANSFORM)["transform"]
    target_delta = np.asarray(
        transform["exact_train_target_delta_rad"],
        dtype=np.float64,
    )
    g3_margin = float(transform["g3_margin_rad"])

    scene = Path(v124_prereg["external_source_paths"]["scene"])
    model = mujoco.MjModel.from_xml_path(str(scene))
    sim_dt_s = float(model.opt.timestep)
    qpos_indices = np.asarray(
        [
            model.jnt_qposadr[model.actuator_trnid[index, 0]]
            for index in range(model.nu)
        ],
        dtype=int,
    )
    qvel_indices = np.asarray(
        [
            model.jnt_dofadr[model.actuator_trnid[index, 0]]
            for index in range(model.nu)
        ],
        dtype=int,
    )

    half_moving = [
        trace
        for trace in traces
        if v124.checkpoint_from_name(trace["path"].name) == "half"
        and v124.command_from_name(trace["path"].name) > 0.01
    ]
    dual_cache = {
        trace["path"].name: {
            plant: v124.replay_bridge(
                trace["sent_target_rad"],
                params[plant],
            )
            for plant in v124.PLANTS
        }
        for trace in traces
    }
    force_q_cache = {
        trace["path"].name: v124.force_state_positions(
            trace,
            qpos_indices,
            qvel_indices,
            sim_dt_s,
        )
        for trace in traces
    }

    passing_errors: dict[str, list[float]] = defaultdict(list)
    for trace in half_moving:
        force_q = force_q_cache[trace["path"].name]
        for plant in v124.PLANTS:
            for joint_index, param in enumerate(params[plant]):
                for decision_tick in range(
                    len(trace["rows"]) - param.delay_ticks
                ):
                    event_tick = decision_tick + param.delay_ticks
                    qhat, _ = predictor(
                        trace,
                        decision_tick,
                        param.delay_ticks,
                        joint_index,
                        sim_dt_s,
                    )
                    passing_errors[v124.JOINT_NAMES[joint_index]].append(
                        abs(qhat - force_q[event_tick, joint_index])
                    )

    event_precursors = []
    event_error: dict[str, list[float]] = defaultdict(list)
    for trace in traces:
        actual_plant = v124.plant_from_name(trace["path"].name)
        force_q = force_q_cache[trace["path"].name]
        for event_tick, joint_index in np.argwhere(
            np.abs(trace["actuator_force_nm"]) > v124.TORQUE_LIMIT_NM
        ):
            event_tick = int(event_tick)
            joint_index = int(joint_index)
            delay = params[actual_plant][joint_index].delay_ticks
            decision_tick = event_tick - delay
            qhat, _ = predictor(
                trace,
                decision_tick,
                delay,
                joint_index,
                sim_dt_s,
            )
            error = abs(qhat - force_q[event_tick, joint_index])
            event_error[v124.JOINT_NAMES[joint_index]].append(error)
            event_precursors.append(
                {
                    "filename": trace["path"].name,
                    "event_tick": event_tick,
                    "decision_tick": decision_tick,
                    "joint": v124.JOINT_NAMES[joint_index],
                    "prediction_error_rad": error,
                }
            )

    prior = v124.read_json(V124_COMPACT)
    prior_reserve = {
        row["joint"]: row for row in prior["s2"]["reserve_by_joint"]
    }
    reserve_rows = []
    half_widths = np.zeros(14, dtype=np.float64)
    for joint_index, joint in enumerate(v124.JOINT_NAMES):
        p999 = v124.percentile(passing_errors[joint], 99.9)
        event_max = max(event_error[joint], default=0.0)
        maximum_horizon = max(
            (
                params[plant][joint_index].delay_ticks + 1
            )
            * v124.CONTROL_DT_S
            - sim_dt_s
            for plant in v124.PLANTS
        )
        floor = (
            v124.POSITION_HALF_LSB_RAD
            + maximum_horizon * v124.VELOCITY_HALF_LSB_RAD_S
            + v124.GOAL_FULL_LSB_RAD
        )
        reserve = max(p999, event_max) + floor
        half_width = v124.TORQUE_LIMIT_NM / 17.11 - reserve
        half_widths[joint_index] = half_width
        reserve_rows.append(
            {
                "joint": joint,
                "prediction_error_p99p9_rad": p999,
                "event_prediction_error_max_rad": event_max,
                "measurement_and_goal_floor_rad": floor,
                "prediction_reserve_rad": reserve,
                "torque_safe_half_width_rad": half_width,
                "positive_half_width": half_width > 0.0,
                "v124_constant_velocity_reserve_rad": prior_reserve[joint][
                    "prediction_reserve_rad"
                ],
                "reserve_delta_vs_v124_rad": (
                    reserve
                    - prior_reserve[joint]["prediction_reserve_rad"]
                ),
            }
        )

    event_failures = []
    for row in event_precursors:
        trace = next(
            item for item in traces if item["path"].name == row["filename"]
        )
        joint_index = v124.JOINT_NAMES.index(row["joint"])
        structural_low, structural_high = v124.structural_target_interval(
            trace["rows"][row["decision_tick"]],
            joint_index,
            target_delta,
            g3_margin,
        )
        box_low, box_high = robust_interval(
            trace=trace,
            dual_applied=dual_cache[row["filename"]],
            params=params,
            decision_tick=row["decision_tick"],
            joint_index=joint_index,
            half_width_rad=float(half_widths[joint_index]),
            sim_dt_s=sim_dt_s,
        )
        if max(structural_low, box_low) > min(structural_high, box_high):
            event_failures.append(
                {
                    **row,
                    "structural_interval_rad": [
                        structural_low,
                        structural_high,
                    ],
                    "robust_box_interval_rad": [box_low, box_high],
                }
            )

    empty = []
    corrections = []
    projection_required = 0
    joint_ticks = 0
    max_delay = max(
        param.delay_ticks for fit in params.values() for param in fit
    )
    dwell_longest: dict[str, int] = defaultdict(int)
    for trace in half_moving:
        for joint_index, joint in enumerate(v124.JOINT_NAMES):
            over = (
                np.abs(trace["actuator_force_nm"][:, joint_index])
                > v124.STRICT_OVERCURRENT_TORQUE_NM
            )
            dwell_longest[joint] = max(
                dwell_longest[joint],
                v124.longest_true_run(over),
            )
        for decision_tick in range(len(trace["rows"]) - max_delay):
            for joint_index, joint in enumerate(v124.JOINT_NAMES):
                joint_ticks += 1
                structural_low, structural_high = (
                    v124.structural_target_interval(
                        trace["rows"][decision_tick],
                        joint_index,
                        target_delta,
                        g3_margin,
                    )
                )
                box_low, box_high = robust_interval(
                    trace=trace,
                    dual_applied=dual_cache[trace["path"].name],
                    params=params,
                    decision_tick=decision_tick,
                    joint_index=joint_index,
                    half_width_rad=float(half_widths[joint_index]),
                    sim_dt_s=sim_dt_s,
                )
                feasible_low = max(structural_low, box_low)
                feasible_high = min(structural_high, box_high)
                if feasible_low > feasible_high:
                    empty.append(
                        {
                            "filename": trace["path"].name,
                            "decision_tick": decision_tick,
                            "joint": joint,
                            "structural_interval_rad": [
                                structural_low,
                                structural_high,
                            ],
                            "robust_box_interval_rad": [box_low, box_high],
                        }
                    )
                    continue
                desired = float(
                    trace["sent_target_rad"][decision_tick, joint_index]
                )
                projected = min(max(desired, feasible_low), feasible_high)
                correction = abs(projected - desired)
                corrections.append(correction)
                if correction > 1.0e-12:
                    projection_required += 1

    checks = {
        "six_half_moving_cells_exact": len(half_moving) == 6,
        "v121_event_precursors_exact_15": len(event_precursors) == 15,
        "positive_half_width_every_joint": bool(np.all(half_widths > 0.0)),
        "all_v121_event_precursors_feasible": len(event_failures) == 0,
        "zero_empty_passing_intersections": len(empty) == 0,
        "existing_dwell_at_most_99_ticks": (
            max(dwell_longest.values(), default=0) <= 99
        ),
    }
    passed = all(checks.values())
    value = {
        "schema_version": "winner_v125.second_order_predictor_result.v1",
        "status": (
            "PASS_WINNER_V125_SECOND_ORDER_PREDICTOR"
            if passed
            else "HOLD_WINNER_V125_SECOND_ORDER_PREDICTOR"
        ),
        "preregistration_sha256": v124.sha256(PREREG),
        "checks": checks,
        "reserve_by_joint": reserve_rows,
        "event_precursors": {
            "count": len(event_precursors),
            "infeasible_count": len(event_failures),
            "infeasible": v124.json_safe(event_failures),
        },
        "feasibility": {
            "joint_ticks": joint_ticks,
            "empty_intersections": len(empty),
            "empty_by_joint": count_by(empty, "joint"),
            "empty_sample_first_32": v124.json_safe(empty[:32]),
            "projection_required_joint_ticks": projection_required,
            "projection_required_fraction": projection_required / joint_ticks,
            "projection_correction_p95_rad": v124.percentile(
                corrections, 95.0
            ),
            "projection_correction_max_rad": max(corrections, default=0.0),
            "worst_existing_strict_over_2a_run_ticks": max(
                dwell_longest.values(), default=0
            ),
        },
        "comparison_to_v124": {
            "v124_empty_intersections": prior["s2"]["summary"][
                "empty_intersections"
            ],
            "v125_empty_intersections": len(empty),
            "selection_weight": 0,
        },
        "decision": {
            "status": (
                "AUTHORIZE_SEPARATE_V125_UNIFORM_WRAPPER_PREREGISTRATION"
                if passed
                else "CLOSE_LOW_ORDER_KINEMATIC_PREDICTIVE_BOX_FAMILY"
            ),
            "next_action": (
                "preregister one zero-credit uniform wrapper screen"
                if passed
                else "select a different mechanism class without predictor "
                "coefficient, smoothing, or Taylor-order search"
            ),
        },
        "execution": {
            "training_steps": 0,
            "behavior_rollouts": 0,
            "colab_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "wrapper_preregistration_authorized": passed,
            "behavior_screen_authorized": False,
            "hosted_training_authorized": False,
            "checkpoint_selection_authorized": False,
            "gate5_authorized": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    OUTPUT.write_text(
        json.dumps(
            v124.json_safe(value),
            allow_nan=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner-v125 second-order predictor result\n\n"
        f"Status: `{value['status']}`\n\n"
        f"Positive reserve-aware half-widths for every joint: "
        f"`{checks['positive_half_width_every_joint']}`.\n\n"
        f"V121 event precursors feasible: "
        f"`{len(event_precursors) - len(event_failures)}/15`.\n\n"
        f"Empty passing-cell joint-tick intersections: `{len(empty)}` "
        f"(V124 constant velocity: "
        f"`{prior['s2']['summary']['empty_intersections']}`).\n\n"
        f"Decision: `{value['decision']['status']}`.\n\n"
        "No behavior rollout, training, Colab, RDK-X5, robot, torque, or "
        "motion occurred or is authorized.\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": value["status"],
                "checks": checks,
                "empty_intersections": len(empty),
                "event_failures": len(event_failures),
                "decision": value["decision"]["status"],
            }
        )
    )
    print(f"sha256={v124.sha256(OUTPUT)}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
