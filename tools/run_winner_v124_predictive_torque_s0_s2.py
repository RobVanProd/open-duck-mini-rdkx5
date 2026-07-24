#!/usr/bin/env python3
"""Run the preregistered V124 predictive-torque S0-S2 trace falsification."""

from __future__ import annotations

from collections import defaultdict
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any, Iterable

import mujoco
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

from actuator_bridge_model import (  # noqa: E402
    ActuatorBridgeModel,
    JOINT_NAMES,
    JointActuatorParams,
    params_from_fit,
)
from run_winner_v3_variable_configuration_behavior import (  # noqa: E402
    actuator_fit,
)


ANALYSIS = ROOT / "outputs/analysis"
PREREG = ANALYSIS / "winner_v124_predictive_torque_s0_s2_preregistration.json"
OUTPUT = ANALYSIS / "winner_v124_predictive_torque_s0_s2_result.json"
MARKDOWN = ANALYSIS / "WINNER_V124_PREDICTIVE_TORQUE_S0_S2_RESULT_20260724.md"
PREREG_SHA256 = (
    "61364c864ef3bf97d13df92a79645140a3918ecc8923f52810dd360f16b8042f"
)
AMENDMENT = ANALYSIS / "winner_v124_s0_ctrl_tolerance_amendment.json"
AMENDMENT_SHA256 = (
    "46e6c08864ba143b724975528c942f4cc822955a5334407a526580be197290b6"
)

PLANT_PREREG = (
    ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
)
TRANSFORM = ANALYSIS / "winner_v121_deployment_transform_contract.json"

HOME = np.asarray(
    [
        0.002,
        0.053,
        -0.630,
        1.368,
        -0.784,
        0.0,
        0.0,
        0.0,
        0.0,
        -0.003,
        -0.065,
        0.635,
        1.379,
        -0.796,
    ],
    dtype=np.float64,
)
PLANTS = ("P30_ALL_JOINT", "P31_34_PITCH_WITH_P30_NONPITCH")
CONTROL_DT_S = 0.02
DOF_VEL_SCALE = 0.05
TORQUE_LIMIT_NM = 1.91229675
NM_PER_A = 0.784532
STRICT_OVERCURRENT_TORQUE_NM = 2.0 * NM_PER_A
OBJECTIVE_SCALE = -307.48131091308585
POSITION_HALF_LSB_RAD = math.pi / 4096.0
VELOCITY_HALF_LSB_RAD_S = math.pi / 4095.0
GOAL_FULL_LSB_RAD = 2.0 * math.pi / 4096.0


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


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(item) for item in value]
    if isinstance(value, np.generic):
        return json_safe(value.item())
    if isinstance(value, float) and not math.isfinite(value):
        return "Infinity" if value > 0.0 else "-Infinity"
    return value


def load_trace(path: Path) -> dict[str, Any]:
    rows = [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line
    ]
    arrays = {
        key: np.asarray([row[key] for row in rows], dtype=np.float64)
        for key in (
            "sent_target_rad",
            "applied_target_rad",
            "actual_position_pre_rad",
            "actual_position_rad",
            "actuator_force_nm",
            "obs_state",
            "qpos",
            "qvel",
            "action",
        )
    }
    return {"path": path, "rows": rows, **arrays}


def plant_from_name(name: str) -> str:
    if "p31_34_pitch_with_p30_nonpitch" in name:
        return "P31_34_PITCH_WITH_P30_NONPITCH"
    if "p30_all_joint" in name:
        return "P30_ALL_JOINT"
    raise ValueError(f"cannot identify plant from {name}")


def checkpoint_from_name(name: str) -> str:
    if "_half_" in name:
        return "half"
    if "_final_" in name:
        return "final"
    raise ValueError(f"cannot identify checkpoint from {name}")


def command_from_name(name: str) -> float:
    marker = "_x"
    start = name.index(marker) + len(marker)
    end = name.index("_seed", start)
    return float(name[start:end])


def fit_params(
    plant_prereg: dict[str, Any],
) -> dict[str, list[JointActuatorParams]]:
    return {
        plant: params_from_fit(
            actuator_fit(plant_prereg, plant),
            include_gain_ratio=True,
        )
        for plant in PLANTS
    }


def replay_bridge(
    sent: np.ndarray,
    params: list[JointActuatorParams],
) -> np.ndarray:
    model = ActuatorBridgeModel(
        params,
        initial_target=HOME,
        home_target=HOME,
    )
    return np.asarray(
        [model.step(target, CONTROL_DT_S) for target in sent],
        dtype=np.float64,
    )


def longest_true_run(values: np.ndarray) -> int:
    longest = 0
    current = 0
    for value in values:
        if bool(value):
            current += 1
            longest = max(longest, current)
        else:
            current = 0
    return longest


def force_state_positions(
    trace: dict[str, Any],
    qpos_indices: np.ndarray,
    qvel_indices: np.ndarray,
    sim_dt_s: float,
) -> np.ndarray:
    return (
        trace["qpos"][:, qpos_indices]
        - sim_dt_s * trace["qvel"][:, qvel_indices]
    )


def bridge_target_interval(
    *,
    previous_applied: float,
    home: float,
    param: JointActuatorParams,
    safe_low: float,
    safe_high: float,
) -> tuple[float, float]:
    beta = (
        1.0 - math.exp(-CONTROL_DT_S / param.tau_s)
        if param.tau_s > 0.0
        else 1.0
    )
    slope = beta * param.gain_ratio
    if slope <= 0.0:
        raise ValueError("predictive interval requires a positive bridge slope")
    intercept = (
        previous_applied
        + beta
        * (
            home * (1.0 - param.gain_ratio)
            - previous_applied
        )
    )
    max_step = param.velocity_limit_rad_s * CONTROL_DT_S
    low_cap = (
        previous_applied - max_step
        if math.isfinite(max_step)
        else -math.inf
    )
    high_cap = (
        previous_applied + max_step
        if math.isfinite(max_step)
        else math.inf
    )
    if high_cap < safe_low or low_cap > safe_high:
        return math.inf, -math.inf
    lower = (
        -math.inf
        if low_cap >= safe_low
        else (safe_low - intercept) / slope
    )
    upper = (
        math.inf
        if high_cap <= safe_high
        else (safe_high - intercept) / slope
    )
    return lower, upper


def structural_target_interval(
    row: dict[str, Any],
    joint_index: int,
    target_delta: np.ndarray,
    g3_margin_rad: float,
) -> tuple[float, float]:
    previous_action = np.asarray(
        row["policy_state_input"]["previous_action"][0],
        dtype=np.float64,
    )
    previous_target = HOME + 0.25 * previous_action
    observed_position = HOME + np.asarray(
        row["obs_state"][13:27],
        dtype=np.float64,
    )
    low = max(
        HOME[joint_index] - 0.25,
        previous_target[joint_index] - target_delta[joint_index],
        observed_position[joint_index] - g3_margin_rad,
    )
    high = min(
        HOME[joint_index] + 0.25,
        previous_target[joint_index] + target_delta[joint_index],
        observed_position[joint_index] + g3_margin_rad,
    )
    return low, high


def predictor(
    trace: dict[str, Any],
    decision_tick: int,
    delay_ticks: int,
    joint_index: int,
    sim_dt_s: float,
) -> tuple[float, float]:
    q_pre = float(trace["actual_position_pre_rad"][decision_tick, joint_index])
    qdot_pre = float(
        trace["obs_state"][decision_tick, 27 + joint_index] / DOF_VEL_SCALE
    )
    horizon_s = (delay_ticks + 1) * CONTROL_DT_S - sim_dt_s
    return q_pre + horizon_s * qdot_pre, horizon_s


def robust_interval_at_decision(
    *,
    trace: dict[str, Any],
    dual_applied: dict[str, np.ndarray],
    params: dict[str, list[JointActuatorParams]],
    force_q: np.ndarray,
    decision_tick: int,
    joint_index: int,
    half_width_rad: float,
    use_prediction: bool,
    sim_dt_s: float,
) -> tuple[float, float, list[dict[str, Any]]]:
    low = -math.inf
    high = math.inf
    details = []
    for plant in PLANTS:
        param = params[plant][joint_index]
        event_tick = decision_tick + param.delay_ticks
        if event_tick >= len(trace["rows"]):
            return math.inf, -math.inf, []
        previous_applied = (
            HOME[joint_index]
            if event_tick == 0
            else float(dual_applied[plant][event_tick - 1, joint_index])
        )
        if use_prediction:
            center, horizon_s = predictor(
                trace,
                decision_tick,
                param.delay_ticks,
                joint_index,
                sim_dt_s,
            )
        else:
            center = float(force_q[event_tick, joint_index])
            horizon_s = (param.delay_ticks + 1) * CONTROL_DT_S - sim_dt_s
        fit_low, fit_high = bridge_target_interval(
            previous_applied=previous_applied,
            home=float(HOME[joint_index]),
            param=param,
            safe_low=center - half_width_rad,
            safe_high=center + half_width_rad,
        )
        low = max(low, fit_low)
        high = min(high, fit_high)
        details.append(
            {
                "plant": plant,
                "delay_ticks": param.delay_ticks,
                "event_tick": event_tick,
                "center_rad": center,
                "horizon_s": horizon_s,
                "fit_interval_rad": [fit_low, fit_high],
            }
        )
    return low, high, details


def base_scaled_reward_sum(row: dict[str, Any]) -> float:
    terms = row["reward_terms"]
    return sum(
        float(value)
        for key, value in terms.items()
        if key.startswith("reward/")
    ) - sum(
        float(value)
        for key, value in terms.items()
        if key.startswith("cost/")
    )


def percentile(values: Iterable[float], value: float) -> float:
    data = np.asarray(list(values), dtype=np.float64)
    return float(np.percentile(data, value)) if data.size else 0.0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    args = parser.parse_args()
    del args
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V124 result: {path}")

    prereg = read_json(PREREG)
    if (
        sha256(PREREG) != PREREG_SHA256
        or prereg.get("status")
        != "PREREGISTERED_WINNER_V124_PREDICTIVE_TORQUE_S0_S2"
        or prereg.get("failed_checks") != []
        or not prereg.get("authority", {}).get(
            "s0_s2_read_only_analysis_authorized"
        )
    ):
        raise ValueError("V124 S0-S2 preregistration is not exact and passing")
    amendment = read_json(AMENDMENT)
    if (
        sha256(AMENDMENT) != AMENDMENT_SHA256
        or amendment.get("status")
        != "PREREGISTERED_WINNER_V124_S0_CTRL_TOLERANCE_AMENDMENT"
        or amendment.get("failed_checks") != []
        or not amendment.get("authority", {}).get(
            "one_exact_s0_s2_rerun_authorized"
        )
    ):
        raise ValueError("V124 S0 ctrl-tolerance amendment is not exact")
    ctrl_applied_tolerance = float(
        amendment["correction"]["ctrl_applied_tolerance_rad"]
    )

    for name, expected in prereg["input_hashes"].items():
        source = {
            "v121_result": ANALYSIS / "winner_v121_nominal_behavior_result.json",
            "v123_result": ANALYSIS / "winner_v123_nominal_behavior_result.json",
            "v123_attribution": (
                ANALYSIS / "winner_v123_episode_peak_failure_attribution.json"
            ),
            "v121_diagnosis": (
                ANALYSIS / "winner_v121_peak_objective_diagnosis.json"
            ),
            "v121_transform": TRANSFORM,
            "plant_preregistration": PLANT_PREREG,
            "v122_hosted_preregistration": (
                ANALYSIS / "winner_v122_hosted_preregistration.json"
            ),
            "episode_peak_patch": (
                ROOT / "patches/winner_v122_episode_peak_torque_increment.patch"
            ),
            "closed_loop_evaluator": ROOT / "tools/closed_loop_sim_eval.py",
            "bridge_model": ROOT / "tools/actuator_bridge_model.py",
        }[name]
        if sha256(source) != expected:
            raise ValueError(f"frozen source changed: {name}")
    for name, expected in prereg["external_source_hashes"].items():
        if sha256(Path(prereg["external_source_paths"][name])) != expected:
            raise ValueError(f"frozen external source changed: {name}")

    trace_sets: dict[str, list[dict[str, Any]]] = {}
    for label in ("v121", "v123"):
        manifest = prereg["trace_inputs"][label]
        run_root = Path(prereg["trace_inputs"][f"{label}_run_root"])
        current = []
        loaded = []
        for item in manifest:
            path = run_root / "traces" / item["filename"]
            if sha256(path) != item["sha256"]:
                raise ValueError(f"frozen trace changed: {path}")
            current.append(item)
            loaded.append(load_trace(path))
        if canonical_sha256(current) != prereg["trace_inputs"][
            f"{label}_manifest_sha256"
        ]:
            raise ValueError(f"{label} trace manifest changed")
        trace_sets[label] = loaded

    plant_prereg = read_json(PLANT_PREREG)
    params = fit_params(plant_prereg)
    transform = read_json(TRANSFORM)["transform"]
    target_delta = np.asarray(
        transform["exact_train_target_delta_rad"],
        dtype=np.float64,
    )
    g3_margin = float(transform["g3_margin_rad"])

    scene = Path(prereg["external_source_paths"]["scene"])
    model = mujoco.MjModel.from_xml_path(str(scene))
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
    kp = np.asarray(model.actuator_gainprm[:, 0], dtype=np.float64)
    kv = -np.asarray(model.actuator_biasprm[:, 2], dtype=np.float64)
    force_range = np.asarray(model.actuator_forcerange, dtype=np.float64)
    sim_dt_s = float(model.opt.timestep)

    s0_rows = []
    bridge_errors = []
    torque_errors = []
    ctrl_errors = []
    current_errors = []
    trace_cache: dict[str, dict[str, Any]] = {}
    for label, traces in trace_sets.items():
        run_root = Path(prereg["trace_inputs"][f"{label}_run_root"])
        for trace in traces:
            name = trace["path"].name
            trace_cache[f"{label}:{name}"] = trace
            plant = plant_from_name(name)
            bridge = replay_bridge(trace["sent_target_rad"], params[plant])
            bridge_error = float(
                np.max(np.abs(bridge - trace["applied_target_rad"]))
            )
            force_q = force_state_positions(
                trace,
                qpos_indices,
                qvel_indices,
                sim_dt_s,
            )
            reconstructed_force = np.clip(
                kp
                * (trace["applied_target_rad"] - force_q)
                - kv * trace["qvel"][:, qvel_indices],
                force_range[:, 0],
                force_range[:, 1],
            )
            torque_error = float(
                np.max(
                    np.abs(reconstructed_force - trace["actuator_force_nm"])
                )
            )
            ctrl_error = float(
                np.max(
                    np.abs(
                        np.asarray(
                            [row["ctrl"] for row in trace["rows"]],
                            dtype=np.float64,
                        )
                        - trace["applied_target_rad"]
                    )
                )
            )
            cell = read_json(run_root / "cells" / f"{Path(name).stem}.json")
            reported = np.asarray(
                cell["prospective_current_gate"]["peak_current_a_by_joint"],
                dtype=np.float64,
            )
            reconstructed_current = (
                np.max(np.abs(trace["actuator_force_nm"]), axis=0) / NM_PER_A
            )
            current_error = float(
                np.max(np.abs(reported - reconstructed_current))
            )
            bridge_errors.append(bridge_error)
            torque_errors.append(torque_error)
            ctrl_errors.append(ctrl_error)
            current_errors.append(current_error)
            s0_rows.append(
                {
                    "population": label,
                    "filename": name,
                    "plant": plant,
                    "bridge_max_abs_error_rad": bridge_error,
                    "torque_max_abs_error_nm": torque_error,
                    "ctrl_applied_max_abs_error_rad": ctrl_error,
                    "reported_current_max_abs_error_a": current_error,
                }
            )
    s0_checks = {
        "model_has_14_actuators": model.nu == 14,
        "kp_exact_17p11": bool(np.all(kp == 17.11)),
        "kv_exact_zero": bool(np.all(kv == 0.0)),
        "forcerange_exact_3p23": bool(
            np.all(force_range[:, 0] == -3.23)
            and np.all(force_range[:, 1] == 3.23)
        ),
        "sim_dt_exact_0p002": sim_dt_s == 0.002,
        "bridge_trace_closure": max(bridge_errors) <= 6.0e-8,
        "torque_trace_closure": max(torque_errors) <= 5.0e-6,
        "ctrl_equals_applied_target": (
            max(ctrl_errors) <= ctrl_applied_tolerance
        ),
        "reported_current_closure": max(current_errors) <= 1.0e-12,
        "torque_gate_stricter_than_peak_current_gate": (
            TORQUE_LIMIT_NM < 2.5 * NM_PER_A
        ),
    }
    s0_pass = all(s0_checks.values())

    dual_cache: dict[str, dict[str, np.ndarray]] = {}
    force_q_cache: dict[str, np.ndarray] = {}
    for key, trace in trace_cache.items():
        dual_cache[key] = {
            plant: replay_bridge(trace["sent_target_rad"], params[plant])
            for plant in PLANTS
        }
        force_q_cache[key] = force_state_positions(
            trace,
            qpos_indices,
            qvel_indices,
            sim_dt_s,
        )

    event_rows: dict[str, list[dict[str, Any]]] = {"v121": [], "v123": []}
    event_prediction_errors: dict[str, list[float]] = defaultdict(list)
    for label in ("v121", "v123"):
        for trace in trace_sets[label]:
            name = trace["path"].name
            key = f"{label}:{name}"
            actual_plant = plant_from_name(name)
            force_q = force_q_cache[key]
            for event_tick, joint_index in np.argwhere(
                np.abs(trace["actuator_force_nm"]) > TORQUE_LIMIT_NM
            ):
                event_tick = int(event_tick)
                joint_index = int(joint_index)
                delay = params[actual_plant][joint_index].delay_ticks
                decision_tick = event_tick - delay
                committed = decision_tick < 0
                structural_low = math.inf
                structural_high = -math.inf
                box_low = math.inf
                box_high = -math.inf
                robust_details: list[dict[str, Any]] = []
                prediction_error = None
                if not committed:
                    structural_low, structural_high = structural_target_interval(
                        trace["rows"][decision_tick],
                        joint_index,
                        target_delta,
                        g3_margin,
                    )
                    box_low, box_high, robust_details = (
                        robust_interval_at_decision(
                            trace=trace,
                            dual_applied=dual_cache[key],
                            params=params,
                            force_q=force_q,
                            decision_tick=decision_tick,
                            joint_index=joint_index,
                            half_width_rad=TORQUE_LIMIT_NM / 17.11,
                            use_prediction=False,
                            sim_dt_s=sim_dt_s,
                        )
                    )
                    qhat, _ = predictor(
                        trace,
                        decision_tick,
                        delay,
                        joint_index,
                        sim_dt_s,
                    )
                    prediction_error = abs(
                        qhat - float(force_q[event_tick, joint_index])
                    )
                    event_prediction_errors[JOINT_NAMES[joint_index]].append(
                        prediction_error
                    )
                feasible_low = max(structural_low, box_low)
                feasible_high = min(structural_high, box_high)
                preventable = (
                    not committed and feasible_low <= feasible_high
                )
                event_rows[label].append(
                    {
                        "filename": name,
                        "checkpoint": checkpoint_from_name(name),
                        "plant": actual_plant,
                        "command_x_m_s": command_from_name(name),
                        "event_tick": event_tick,
                        "joint": JOINT_NAMES[joint_index],
                        "joint_index": joint_index,
                        "force_abs_nm": float(
                            abs(trace["actuator_force_nm"][event_tick, joint_index])
                        ),
                        "delay_ticks": delay,
                        "decision_tick": decision_tick,
                        "committed": committed,
                        "structural_interval_rad": [
                            structural_low,
                            structural_high,
                        ],
                        "robust_box_interval_rad": [box_low, box_high],
                        "feasible_interval_rad": [
                            feasible_low,
                            feasible_high,
                        ],
                        "locally_preventable": preventable,
                        "prediction_error_rad": prediction_error,
                        "fit_details": robust_details,
                    }
                )

    s1b_trace_rows = []
    direct_credit_events = 0
    zero_direct_credit_events = 0
    max_setting_ticks = 0
    intended_price = 0.0
    realized_price = 0.0
    reward_reconstruction_errors = []
    for trace in trace_sets["v123"]:
        previous_peak = 0.0
        trace_direct = 0
        trace_zero = 0
        trace_max_ticks = 0
        trace_realized = 0.0
        for tick, row in enumerate(trace["rows"]):
            abs_force = np.abs(trace["actuator_force_nm"][tick])
            excess_by_joint = np.maximum(abs_force - TORQUE_LIMIT_NM, 0.0)
            instantaneous = float(np.max(excess_by_joint))
            next_peak = max(previous_peak, instantaneous)
            increment = next_peak - previous_peak
            increment_rate = increment / CONTROL_DT_S
            if increment > 0.0:
                trace_max_ticks += 1
            for joint_index in np.flatnonzero(excess_by_joint > 0.0):
                direct = bool(
                    increment > 0.0
                    and excess_by_joint[joint_index] == instantaneous
                )
                if direct:
                    trace_direct += 1
                else:
                    trace_zero += 1
            base_sum = base_scaled_reward_sum(row)
            base_reward = float(np.clip(base_sum * CONTROL_DT_S, 0.0, 10000.0))
            reward_reconstruction_errors.append(
                abs(base_reward - float(row["reward"]))
            )
            with_objective = float(
                np.clip(
                    (
                        base_sum
                        + OBJECTIVE_SCALE * increment_rate
                    )
                    * CONTROL_DT_S,
                    0.0,
                    10000.0,
                )
            )
            trace_realized += base_reward - with_objective
            previous_peak = next_peak
        trace_intended = abs(OBJECTIVE_SCALE) * previous_peak
        direct_credit_events += trace_direct
        zero_direct_credit_events += trace_zero
        max_setting_ticks += trace_max_ticks
        intended_price += trace_intended
        realized_price += trace_realized
        s1b_trace_rows.append(
            {
                "filename": trace["path"].name,
                "direct_credit_events": trace_direct,
                "zero_direct_credit_events": trace_zero,
                "max_setting_ticks": trace_max_ticks,
                "final_peak_excess_nm": previous_peak,
                "intended_unclipped_price": trace_intended,
                "realized_clipped_reward_price": trace_realized,
            }
        )

    v121_preventable = sum(
        row["locally_preventable"] for row in event_rows["v121"]
    )
    v123_preventable = sum(
        row["locally_preventable"] for row in event_rows["v123"]
    )
    s1_checks = {
        "v121_event_count_exact_15": len(event_rows["v121"]) == 15,
        "v123_event_count_exact_184": len(event_rows["v123"]) == 184,
        "v121_no_committed_events": not any(
            row["committed"] for row in event_rows["v121"]
        ),
        "v121_all_events_locally_preventable": (
            v121_preventable == len(event_rows["v121"]) == 15
        ),
        "v123_at_least_95pct_locally_preventable": (
            v123_preventable / len(event_rows["v123"]) >= 0.95
        ),
        "s1b_reward_reconstruction": (
            max(reward_reconstruction_errors) <= 1.0e-6
        ),
        "s1b_event_accounting_exact": (
            direct_credit_events + zero_direct_credit_events == 184
        ),
        "s1b_integral_identity_positive": intended_price > 0.0,
    }
    s1_pass = all(s1_checks.values())

    prediction_population: dict[str, list[float]] = defaultdict(list)
    half_moving = [
        trace
        for trace in trace_sets["v121"]
        if checkpoint_from_name(trace["path"].name) == "half"
        and command_from_name(trace["path"].name) > 0.01
    ]
    for trace in half_moving:
        key = f"v121:{trace['path'].name}"
        force_q = force_q_cache[key]
        for plant in PLANTS:
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
                    prediction_population[JOINT_NAMES[joint_index]].append(
                        abs(qhat - force_q[event_tick, joint_index])
                    )

    reserve_rows = []
    half_widths = np.zeros(14, dtype=np.float64)
    for joint_index, joint in enumerate(JOINT_NAMES):
        p999 = percentile(prediction_population[joint], 99.9)
        event_max = max(event_prediction_errors[joint], default=0.0)
        maximum_horizon = max(
            (params[plant][joint_index].delay_ticks + 1) * CONTROL_DT_S
            - sim_dt_s
            for plant in PLANTS
        )
        measurement_goal_floor = (
            POSITION_HALF_LSB_RAD
            + maximum_horizon * VELOCITY_HALF_LSB_RAD_S
            + GOAL_FULL_LSB_RAD
        )
        reserve = max(p999, event_max) + measurement_goal_floor
        torque_reserve = 17.11 * reserve
        half_width = TORQUE_LIMIT_NM / 17.11 - reserve
        half_widths[joint_index] = half_width
        reserve_rows.append(
            {
                "joint": joint,
                "passing_prediction_error_p99p9_rad": p999,
                "v121_event_prediction_error_max_rad": event_max,
                "maximum_horizon_s": maximum_horizon,
                "measurement_and_goal_floor_rad": measurement_goal_floor,
                "prediction_reserve_rad": reserve,
                "torque_reserve_nm": torque_reserve,
                "torque_safe_half_width_rad": half_width,
                "positive_half_width": half_width > 0.0,
            }
        )

    empty_intersections = []
    projection_corrections = []
    projection_required = 0
    joint_tick_count = 0
    occupancy: dict[str, list[float]] = defaultdict(list)
    dwell_ticks: dict[str, int] = defaultdict(int)
    dwell_longest: dict[str, int] = defaultdict(int)
    max_delay = max(
        param.delay_ticks for fit in params.values() for param in fit
    )
    for trace in half_moving:
        key = f"v121:{trace['path'].name}"
        force_q = force_q_cache[key]
        applied = trace["applied_target_rad"]
        for joint_index, joint in enumerate(JOINT_NAMES):
            occupancy[joint].extend(
                np.abs(applied[:, joint_index] - force_q[:, joint_index]).tolist()
            )
            over = (
                np.abs(trace["actuator_force_nm"][:, joint_index])
                > STRICT_OVERCURRENT_TORQUE_NM
            )
            dwell_ticks[joint] += int(np.sum(over))
            dwell_longest[joint] = max(
                dwell_longest[joint],
                longest_true_run(over),
            )
        for decision_tick in range(len(trace["rows"]) - max_delay):
            for joint_index, joint in enumerate(JOINT_NAMES):
                joint_tick_count += 1
                structural_low, structural_high = structural_target_interval(
                    trace["rows"][decision_tick],
                    joint_index,
                    target_delta,
                    g3_margin,
                )
                box_low, box_high, details = robust_interval_at_decision(
                    trace=trace,
                    dual_applied=dual_cache[key],
                    params=params,
                    force_q=force_q,
                    decision_tick=decision_tick,
                    joint_index=joint_index,
                    half_width_rad=float(half_widths[joint_index]),
                    use_prediction=True,
                    sim_dt_s=sim_dt_s,
                )
                feasible_low = max(structural_low, box_low)
                feasible_high = min(structural_high, box_high)
                if feasible_low > feasible_high:
                    empty_intersections.append(
                        {
                            "filename": trace["path"].name,
                            "decision_tick": decision_tick,
                            "joint": joint,
                            "structural_interval_rad": [
                                structural_low,
                                structural_high,
                            ],
                            "robust_box_interval_rad": [box_low, box_high],
                            "fit_details": details,
                        }
                    )
                    continue
                desired = float(
                    trace["sent_target_rad"][decision_tick, joint_index]
                )
                projected = min(max(desired, feasible_low), feasible_high)
                correction = abs(projected - desired)
                projection_corrections.append(correction)
                if correction > 1.0e-12:
                    projection_required += 1

    occupancy_rows = [
        {
            "joint": joint,
            "applied_error_p95_rad": percentile(occupancy[joint], 95.0),
            "applied_error_p99p9_rad": percentile(occupancy[joint], 99.9),
            "applied_error_max_rad": max(occupancy[joint], default=0.0),
            "strict_over_2a_equivalent_ticks": dwell_ticks[joint],
            "strict_over_2a_equivalent_longest_run_ticks": dwell_longest[joint],
        }
        for joint in JOINT_NAMES
    ]
    s2_checks = {
        "six_v121_half_moving_cells_exact": len(half_moving) == 6,
        "positive_torque_safe_half_width_every_joint": bool(
            np.all(half_widths > 0.0)
        ),
        "zero_empty_robust_intersections": len(empty_intersections) == 0,
        "existing_dwell_at_most_99_ticks": (
            max(dwell_longest.values(), default=0) <= 99
        ),
    }
    s2_pass = all(s2_checks.values())

    all_pass = s0_pass and s1_pass and s2_pass
    value = {
        "schema_version": "winner_v124.predictive_torque_s0_s2_result.v1",
        "status": (
            "PASS_WINNER_V124_PREDICTIVE_TORQUE_S0_S2"
            if all_pass
            else "HOLD_WINNER_V124_PREDICTIVE_TORQUE_S0_S2"
        ),
        "preregistration_sha256": sha256(PREREG),
        "amendment_sha256": sha256(AMENDMENT),
        "s0": {
            "pass": s0_pass,
            "checks": s0_checks,
            "source_readback": {
                "actuators": int(model.nu),
                "kp_nm_per_rad": kp.tolist(),
                "kv_nm_s_per_rad": kv.tolist(),
                "forcerange_nm": force_range.tolist(),
                "sim_dt_s": sim_dt_s,
                "qpos_indices": qpos_indices.tolist(),
                "qvel_indices": qvel_indices.tolist(),
                "current_nm_per_a": NM_PER_A,
            },
            "summary": {
                "cells": len(s0_rows),
                "bridge_max_abs_error_rad": max(bridge_errors),
                "torque_max_abs_error_nm": max(torque_errors),
                "ctrl_applied_max_abs_error_rad": max(ctrl_errors),
                "reported_current_max_abs_error_a": max(current_errors),
                "torque_gate_equivalent_current_a": TORQUE_LIMIT_NM / NM_PER_A,
                "peak_current_gate_equivalent_torque_nm": 2.5 * NM_PER_A,
            },
            "rows": s0_rows,
        },
        "s1": {
            "pass": s1_pass,
            "checks": s1_checks,
            "summary": {
                "v121_events": len(event_rows["v121"]),
                "v121_locally_preventable": v121_preventable,
                "v121_committed": sum(
                    row["committed"] for row in event_rows["v121"]
                ),
                "v123_events": len(event_rows["v123"]),
                "v123_locally_preventable": v123_preventable,
                "v123_preventable_fraction": (
                    v123_preventable / len(event_rows["v123"])
                ),
            },
            "events": event_rows,
            "s1b": {
                "direct_credit_events": direct_credit_events,
                "zero_direct_credit_events": zero_direct_credit_events,
                "zero_direct_credit_fraction": (
                    zero_direct_credit_events
                    / (direct_credit_events + zero_direct_credit_events)
                ),
                "max_setting_ticks": max_setting_ticks,
                "intended_unclipped_price": intended_price,
                "realized_clipped_reward_price": realized_price,
                "realized_fraction": realized_price / intended_price,
                "fraction_removed_by_clipping": 1.0
                - realized_price / intended_price,
                "reward_reconstruction_max_abs_error": max(
                    reward_reconstruction_errors
                ),
                "rows": s1b_trace_rows,
            },
        },
        "s2": {
            "pass": s2_pass,
            "checks": s2_checks,
            "reserve_by_joint": reserve_rows,
            "summary": {
                "half_moving_cells": len(half_moving),
                "joint_ticks": joint_tick_count,
                "empty_intersections": len(empty_intersections),
                "projection_required_joint_ticks": projection_required,
                "projection_required_fraction": (
                    projection_required / joint_tick_count
                ),
                "projection_correction_p95_rad": percentile(
                    projection_corrections, 95.0
                ),
                "projection_correction_max_rad": max(
                    projection_corrections, default=0.0
                ),
                "worst_existing_strict_over_2a_run_ticks": max(
                    dwell_longest.values(), default=0
                ),
            },
            "occupancy_by_joint": occupancy_rows,
            "empty_intersections": empty_intersections,
        },
        "decision": {
            "status": (
                "AUTHORIZE_SEPARATE_V124_S3_UNIFORM_WRAPPER_PREREGISTRATION"
                if all_pass
                else "CLOSE_V124_PREDICTIVE_TORQUE_BOX_WITHOUT_ROLLOUT"
            ),
            "reason": (
                "S0 source/trace closure, S1 local preventability, and S2 "
                "reserve-aware feasibility all pass."
                if all_pass
                else "At least one preregistered S0-S2 falsifier failed."
            ),
        },
        "execution": {
            "training_steps": 0,
            "behavior_rollouts": 0,
            "colab_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "s3_preregistration_authorized": all_pass,
            "s3_behavior_screen_authorized": False,
            "hosted_training_authorized": False,
            "checkpoint_selection_authorized": False,
            "gate5_authorized": False,
            "rdkx5_or_robot": False,
            "robot_clearance": False,
            "torque_or_motion": False,
        },
    }
    value = json_safe(value)
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner-v124 predictive-torque S0-S2 result\n\n"
        f"Status: `{value['status']}`\n\n"
        f"S0 source/trace closure: `{s0_pass}`. "
        f"Torque reconstruction max error: "
        f"`{max(torque_errors):.9g}` N.m.\n\n"
        f"S1 V121 preventability: `{v121_preventable}/15`; "
        f"V123: `{v123_preventable}/184`.\n\n"
        f"S1b zero-direct-credit events: "
        f"`{zero_direct_credit_events}/184`; reward clipping removed "
        f"`{100.0 * (1.0 - realized_price / intended_price):.3f}%` of the "
        "counterfactual un-clipped objective price.\n\n"
        f"S2 positive reserve-aware boxes: "
        f"`{s2_checks['positive_torque_safe_half_width_every_joint']}`; "
        f"empty intersections: `{len(empty_intersections)}`.\n\n"
        f"Decision: `{value['decision']['status']}`.\n\n"
        "This result contains no behavior rollout or training and does not "
        "authorize Colab, Gate 5, RDK-X5, robot use, torque, or motion.\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": value["status"],
                "s0": s0_pass,
                "s1": value["s1"]["summary"],
                "s2": value["s2"]["summary"],
                "decision": value["decision"]["status"],
            }
        )
    )
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
